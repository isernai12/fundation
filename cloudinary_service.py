import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_file_size(file_stream):
    file_stream.seek(0, os.SEEK_END)
    size = file_stream.tell()
    file_stream.seek(0)
    return size <= MAX_FILE_SIZE

def upload_image(file_stream, folder_name):
    """
    Uploads an image to Cloudinary and returns a dict with details.
    """
    if not file_stream or not file_stream.filename:
        return None
        
    if not allowed_file(file_stream.filename):
        raise ValueError(f"Invalid file type. Allowed types are: {', '.join(ALLOWED_EXTENSIONS)}")
        
    if not check_file_size(file_stream):
        raise ValueError("File is too large. Maximum size is 5MB.")

    # Reset stream pointer
    file_stream.seek(0)
    
    try:
        response = cloudinary.uploader.upload(
            file_stream,
            folder=folder_name,
            resource_type="image",
            quality="auto",
            fetch_format="auto"
        )
        return {
            'public_id': response.get('public_id'),
            'secure_url': response.get('secure_url'),
            'upload_time': datetime.utcnow()
        }
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed: {str(e)}")

def delete_image(public_id):
    """
    Deletes an image from Cloudinary by its public ID.
    """
    if not public_id:
        return True
    try:
        response = cloudinary.uploader.destroy(public_id)
        return response.get('result') == 'ok'
    except Exception as e:
        return False
