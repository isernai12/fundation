import re
with open('templates/add_member.html', 'r') as f:
    content = f.read()

# Replace block title
content = content.replace('{% block header_title %}Add New Member{% endblock %}', '{% block header_title %}Edit Member: {{ member.full_name }}{% endblock %}')

# Function to add value attribute
def add_val(match):
    name = match.group(1)
    if name in ['declaration', 'photo_file', 'nid_front_file', 'nid_back_file', 'signature_file']:
        return match.group(0)
    return f'{match.group(0)[:-1]} value="{{{{ member.{name} or \'\' }}}}">'

# Add values to inputs
content = re.sub(r'<input[^>]*name="([^"]+)"[^>]*>', add_val, content)

# Replace form action
content = content.replace('<form method="POST"', '<form method="POST" action="{{ url_for(\'edit_member\', id=member.id) }}"')
content = content.replace('Submit Member', 'Update Member')

with open('templates/edit_member.html', 'w') as f:
    f.write(content)
