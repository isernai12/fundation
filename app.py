
import os
import logging
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from cloudinary_service import upload_image, delete_image

basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'foundation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception("Unhandled Exception occurred")
    from werkzeug.exceptions import HTTPException
    message = "Something went wrong. Please try again later."
    code = 500
    if isinstance(e, HTTPException):
        message = e.description
        code = e.code
    return render_template('error.html', message=message), code

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def safe_commit():
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Database error: {str(e)}")
        try:
            flash("Unable to save data. Please try again.", "error")
        except:
            pass
        return False

# ==========================================
# Core Models
# ==========================================
class SystemUser(UserMixin, db.Model):
    __tablename__ = 'system_users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Active')

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    
    # Office Use Only (Auto/Admin generated)
    member_id_str = db.Column(db.String(50), unique=True, nullable=True)
    member_type = db.Column(db.String(50))
    
    # Section 1: Personal Information
    full_name = db.Column(db.String(150), nullable=False)
    fathers_name = db.Column(db.String(150))
    mothers_name = db.Column(db.String(150))
    dob = db.Column(db.Date)
    fund_source_id = db.Column(db.Integer, db.ForeignKey('fund_sources.id'), nullable=True)
    blood_group = db.Column(db.String(10))
    marital_status = db.Column(db.String(20))
    
    # Section 2: Contact Information
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    whatsapp_number = db.Column(db.String(20))
    present_address = db.Column(db.Text)
    permanent_address = db.Column(db.Text)
    
    # Legacy field kept for safety
    address = db.Column(db.Text)
    
    # Section 3: Education & Profession
    education = db.Column(db.String(100))
    profession = db.Column(db.String(150), nullable=False)
    organization = db.Column(db.String(150))
    special_skills = db.Column(db.Text)
    
    # Section 4: Foundation Information
    foundation_source = db.Column(db.String(100))
    purpose_of_joining = db.Column(db.Text)
    activities_interested = db.Column(db.Text)
    
    # Section 5: Emergency Contact
    emergency_contact_name = db.Column(db.String(150))
    emergency_contact_relation = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    
    # Other & Photos
    nid = db.Column(db.String(50))
    
    # Cloudinary Images
    profile_photo_url = db.Column(db.String(255))
    profile_photo_public_id = db.Column(db.String(100))
    profile_photo_time = db.Column(db.DateTime)
    
    nid_front_url = db.Column(db.String(255))
    nid_front_public_id = db.Column(db.String(100))
    nid_front_time = db.Column(db.DateTime)
    
    nid_back_url = db.Column(db.String(255))
    nid_back_public_id = db.Column(db.String(100))
    nid_back_time = db.Column(db.DateTime)
    
    signature_url = db.Column(db.String(255))
    signature_public_id = db.Column(db.String(100))
    signature_time = db.Column(db.DateTime)
    
    join_date = db.Column(db.Date, default=date.today)
    monthly_contribution_amount = db.Column(db.Float, nullable=True, default=None)
    status = db.Column(db.String(20), default='Active') # Status for activity (Active/Inactive)
    remarks = db.Column(db.Text)
    
    funds = db.relationship('Fund', backref='donor', lazy=True)
    ledgers = db.relationship('MemberLedger', backref='member', lazy=True)
    contributions = db.relationship('MemberContribution', backref='member', lazy=True)

class FundSource(db.Model):
    __tablename__ = 'fund_sources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)
    balance = db.Column(db.Float, default=0.0)
    opening_balance = db.Column(db.Float, default=0.0)
    funds = db.relationship('Fund', backref='source', lazy=True)
    members = db.relationship('Member', backref='fund_source', lazy=True)
    ledgers = db.relationship('FundSourceLedger', backref='fund_source', lazy=True)
    contribution_payments = db.relationship('MemberContributionPayment', backref='fund_source', lazy=True)

class FundSourceLedger(db.Model):
    __tablename__ = 'fund_source_ledger'
    id = db.Column(db.Integer, primary_key=True)
    fund_source_id = db.Column(db.Integer, db.ForeignKey('fund_sources.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_type = db.Column(db.String(50))
    reference_number = db.Column(db.String(50))
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=True)
    description = db.Column(db.String(255))
    debit = db.Column(db.Float, default=0.0)
    credit = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, default=0.0)
    remarks = db.Column(db.Text)

def add_fund_source_ledger(fund_source_id, t_type, desc, debit=0.0, credit=0.0, member_id=None, ref="", remarks=""):
    fs = db.session.get(FundSource, fund_source_id)
    if not fs: return
    fs.balance = fs.balance + credit - debit
    entry = FundSourceLedger(
        fund_source_id=fund_source_id,
        transaction_type=t_type,
        description=desc,
        debit=debit,
        credit=credit,
        balance=fs.balance,
        member_id=member_id,
        reference_number=ref,
        remarks=remarks
    )
    db.session.add(entry)


class Fund(db.Model):
    __tablename__ = 'funds'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('fund_sources.id'), nullable=False)

# ==========================================
# Module 1: Assistance Models
# ==========================================
class Beneficiary(db.Model):
    __tablename__ = 'beneficiaries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    details = db.Column(db.Text)
    requests = db.relationship('AssistanceRequest', backref='beneficiary', lazy=True)

class AssistanceRequest(db.Model):
    __tablename__ = 'assistance_requests'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending') # Pending, Approved, Rejected, Paid
    date = db.Column(db.DateTime, default=datetime.utcnow)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiaries.id'), nullable=False)
    payments = db.relationship('AssistancePayment', backref='assistance', lazy=True)

class AssistancePayment(db.Model):
    __tablename__ = 'assistance_payments'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    assistance_request_id = db.Column(db.Integer, db.ForeignKey('assistance_requests.id'), nullable=False)

# ==========================================
# Module 2: Loan Models
# ==========================================
class LoanBeneficiary(db.Model):
    __tablename__ = 'loan_beneficiaries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    details = db.Column(db.Text)
    loans = db.relationship('Loan', backref='beneficiary', lazy=True)

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    monthly_installment = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('loan_beneficiaries.id'), nullable=False)
    installments = db.relationship('LoanInstallment', backref='loan', lazy=True)
    
class LoanInstallment(db.Model):
    __tablename__ = 'loan_installments'
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    installment_number = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Unpaid')
    payment_date = db.Column(db.DateTime, nullable=True)
    collector = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text)
    payments = db.relationship('LoanPayment', backref='installment', lazy=True)

class LoanPayment(db.Model):
    __tablename__ = 'loan_payments'
    id = db.Column(db.Integer, primary_key=True)
    loan_installment_id = db.Column(db.Integer, db.ForeignKey('loan_installments.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

class LoanReport(db.Model):
    __tablename__ = 'loan_reports'
    id = db.Column(db.Integer, primary_key=True)
    date_generated = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text)

# ==========================================
# Module 3: Member Contributions
# ==========================================
class MemberContribution(db.Model):
    __tablename__ = 'member_contributions'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    expected_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Due')
    payments = db.relationship('MemberContributionPayment', backref='contribution', lazy=True)
    
class MemberContributionPayment(db.Model):
    __tablename__ = 'member_contribution_payments'
    id = db.Column(db.Integer, primary_key=True)
    contribution_id = db.Column(db.Integer, db.ForeignKey('member_contributions.id'), nullable=False)
    paid_amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))
    collector = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    fund_source_id = db.Column(db.Integer, db.ForeignKey('fund_sources.id'), nullable=True)

class MemberLedger(db.Model):
    __tablename__ = 'member_ledger'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_type = db.Column(db.String(50))
    description = db.Column(db.String(255))
    debit = db.Column(db.Float, default=0.0)
    credit = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, default=0.0)
    reference_number = db.Column(db.String(50))
    remarks = db.Column(db.Text)

def add_ledger_entry(member_id, t_type, desc, debit=0.0, credit=0.0, ref="", remarks="", date=None):
    last_entry = MemberLedger.query.filter_by(member_id=member_id).order_by(MemberLedger.id.desc()).first()
    bal = last_entry.balance if last_entry else 0.0
    bal = bal + credit - debit
    entry = MemberLedger(
        member_id=member_id,
        transaction_type=t_type,
        description=desc,
        debit=debit,
        credit=credit,
        balance=bal,
        reference_number=ref,
        remarks=remarks,
        date=date or datetime.utcnow()
    )
    db.session.add(entry)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(SystemUser, int(user_id))

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# ==========================================
# Authentication & Dashboard
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = SystemUser.query.filter_by(username=username, status='Active').first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    tot_assist = db.session.query(db.func.sum(AssistanceRequest.amount)).filter_by(status='Paid').scalar() or 0
    tot_assist_b = Beneficiary.query.count()
    pend_assist = AssistanceRequest.query.filter_by(status='Pending').count()
    
    tot_loan = db.session.query(db.func.sum(Loan.amount)).filter_by(status='Running').scalar() or 0
    run_loans = Loan.query.filter_by(status='Running').count()
    col_inst = db.session.query(db.func.sum(LoanPayment.amount)).scalar() or 0
    out_bal = tot_loan - col_inst if tot_loan > col_inst else 0
    
    generate_current_month_contributions()
    now = datetime.utcnow()
    m, y = now.month, now.year
    
    tot_members = Member.query.count()
    cur_contribs = MemberContribution.query.filter_by(month=m, year=y).all()
    mon_exp = sum(c.expected_amount for c in cur_contribs)
    mon_col = sum(sum(p.paid_amount for p in c.payments if p.payment_date.month == m and p.payment_date.year == y) for c in MemberContribution.query.all())
    
    all_exp = db.session.query(db.func.sum(MemberContribution.expected_amount)).scalar() or 0
    all_col = db.session.query(db.func.sum(MemberContributionPayment.paid_amount)).scalar() or 0
    out_due_contrib = all_exp - all_col
    
    fully_paid_users = 0
    due_users_cnt = 0
    for m_obj in Member.query.all():
        u_exp = db.session.query(db.func.sum(MemberContribution.expected_amount)).filter_by(member_id=m_obj.id).scalar() or 0
        u_col_list = MemberContribution.query.filter_by(member_id=m_obj.id).all()
        u_col = sum(sum(p.paid_amount for p in c.payments) for c in u_col_list)
        if u_exp > u_col:
            due_users_cnt += 1
        else:
            fully_paid_users += 1
            
    contrib_pct = round((all_col / all_exp * 100), 2) if all_exp > 0 else 0
    
    return render_template('dashboard.html', 
                           tot_assist=tot_assist, tot_assist_b=tot_assist_b, pend_assist=pend_assist,
                           tot_loan=tot_loan, run_loans=run_loans, col_inst=col_inst, out_bal=out_bal,
                           tot_members=tot_members, mon_exp=mon_exp, mon_col=mon_col, out_due_contrib=out_due_contrib,
                           fully_paid_users=fully_paid_users, due_users_cnt=due_users_cnt, contrib_pct=contrib_pct)



# ==========================================
# Organization Members
# ==========================================
@app.route('/members')
@login_required
def members():
    return render_template('manage_members.html', members=Member.query.order_by(Member.id.desc()).all())

@app.route('/member/view/<int:id>')
@login_required
def member_profile(id):
    member = db.session.get(Member, id)
    if not member:
        flash('সদস্য খুঁজে পাওয়া যায়নি', 'error')
        return redirect(url_for('members'))
        
    # Get all loans, assistance, contributions for timelines and summaries
    contributions = MemberContribution.query.filter_by(member_id=id).all()
    
    # Calculate Summaries
    total_expected = sum(c.expected_amount for c in contributions)
    total_paid = sum(sum(p.paid_amount for p in c.payments) for c in contributions)
    
    # We might need to construct a timeline from logs, but for now we'll combine created_at, payments etc.
    timeline = []
    if member.join_date:
        timeline.append({'date': member.join_date, 'event': 'সদস্য তৈরি হয়েছে', 'details': f'{member.profession} পেশায় যুক্ত হয়েছেন'})
    for c in contributions:
        for p in c.payments:
            p_date = p.payment_date.date() if hasattr(p.payment_date, 'date') else p.payment_date
            timeline.append({'date': p_date, 'event': 'অনুদান সংগ্রহ হয়েছে', 'details': f'Amount: {p.paid_amount}'})
            
    # Sort timeline
    timeline.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('member_profile.html', member=member, total_expected=total_expected, total_paid=total_paid, timeline=timeline)

@app.route('/members/add', methods=['GET', 'POST'])
@login_required
def add_member():
    if request.method == 'POST':
        dob_str = request.form.get('dob')
        join_str = request.form.get('join_date')
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        join_date = datetime.strptime(join_str, '%Y-%m-%d').date() if join_str else date.today()
        
        # Parse activities checkboxes
        activities = request.form.getlist('activities')
        activities_str = ",".join(activities) if activities else ""
        
        prof = request.form.get('profession')
        if prof == 'Other':
            prof = request.form.get('profession_other')
            
        uploaded_ids = []
        try:
            profile_data = upload_image(request.files.get('photo_file'), 'members/profile')
            if profile_data: uploaded_ids.append(profile_data['public_id'])
            
            nid_front_data = upload_image(request.files.get('nid_front_file'), 'members/nid/front')
            if nid_front_data: uploaded_ids.append(nid_front_data['public_id'])
            
            nid_back_data = upload_image(request.files.get('nid_back_file'), 'members/nid/back')
            if nid_back_data: uploaded_ids.append(nid_back_data['public_id'])
            
            signature_data = upload_image(request.files.get('signature_file'), 'members/signature')
            if signature_data: uploaded_ids.append(signature_data['public_id'])
            
        except Exception as e:
            for pid in uploaded_ids:
                delete_image(pid)
            flash(f'Image upload failed: {str(e)}', 'error')
            return redirect(url_for('add_member'))
            
        m = Member(
            full_name=request.form.get('full_name'),
            fathers_name=request.form.get('fathers_name'),
            mothers_name=request.form.get('mothers_name'),
            dob=dob,
            blood_group=request.form.get('blood_group'),
            marital_status=request.form.get('marital_status'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            whatsapp_number=request.form.get('whatsapp_number'),
            present_address=request.form.get('present_address'),
            permanent_address=request.form.get('permanent_address'),
            address=request.form.get('present_address'), # fallback
            education=request.form.get('education'),
            profession=prof,
            organization=request.form.get('organization'),
            special_skills=request.form.get('special_skills'),
            foundation_source=request.form.get('foundation_source'),
            fund_source_id=request.form.get('fund_source_id'),
            purpose_of_joining=request.form.get('purpose_of_joining'),
            activities_interested=activities_str,
            emergency_contact_name=request.form.get('emergency_contact_name'),
            emergency_contact_relation=request.form.get('emergency_contact_relation'),
            emergency_contact_phone=request.form.get('emergency_contact_phone'),
            nid=request.form.get('nid'),
            join_date=join_date,
            monthly_contribution_amount=None,
            status='Active',
            remarks=request.form.get('remarks'),
            profile_photo_url=profile_data['secure_url'] if profile_data else None,
            profile_photo_public_id=profile_data['public_id'] if profile_data else None,
            profile_photo_time=profile_data['upload_time'] if profile_data else None,
            nid_front_url=nid_front_data['secure_url'] if nid_front_data else None,
            nid_front_public_id=nid_front_data['public_id'] if nid_front_data else None,
            nid_front_time=nid_front_data['upload_time'] if nid_front_data else None,
            nid_back_url=nid_back_data['secure_url'] if nid_back_data else None,
            nid_back_public_id=nid_back_data['public_id'] if nid_back_data else None,
            nid_back_time=nid_back_data['upload_time'] if nid_back_data else None,
            signature_url=signature_data['secure_url'] if signature_data else None,
            signature_public_id=signature_data['public_id'] if signature_data else None,
            signature_time=signature_data['upload_time'] if signature_data else None
        )
        db.session.add(m)
        if safe_commit():
            # Generate Member ID after we have the primary key id
            m.member_id_str = f"MEM-{m.id:04d}"
            safe_commit()
            
            flash('সদস্য সফলভাবে যোগ করা হয়েছে।', 'success')
            return redirect(url_for('members'))
    return render_template('add_member.html', fund_sources=FundSource.query.all())

@app.route('/members/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_member(id):
    member = db.session.get(Member, id)
    if not member:
        flash('সদস্য খুঁজে পাওয়া যায়নি', 'error')
        return redirect(url_for('members'))
        
    if request.method == 'POST':
        dob_str = request.form.get('dob')
        join_str = request.form.get('join_date')
        member.dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        if join_str: member.join_date = datetime.strptime(join_str, '%Y-%m-%d').date()
        
        activities = request.form.getlist('activities')
        member.activities_interested = ",".join(activities) if activities else ""
        
        prof = request.form.get('profession')
        member.profession = request.form.get('profession_other') if prof == 'Other' else prof
            
        member.full_name = request.form.get('full_name')
        member.fathers_name = request.form.get('fathers_name')
        member.mothers_name = request.form.get('mothers_name')
        member.blood_group = request.form.get('blood_group')
        member.marital_status = request.form.get('marital_status')
        member.phone = request.form.get('phone')
        member.email = request.form.get('email')
        member.whatsapp_number = request.form.get('whatsapp_number')
        member.present_address = request.form.get('present_address')
        member.permanent_address = request.form.get('permanent_address')
        member.address = request.form.get('present_address')
        member.education = request.form.get('education')
        member.organization = request.form.get('organization')
        member.special_skills = request.form.get('special_skills')
        member.foundation_source = request.form.get('foundation_source')
        member.fund_source_id = request.form.get('fund_source_id')
        member.purpose_of_joining = request.form.get('purpose_of_joining')
        member.emergency_contact_name = request.form.get('emergency_contact_name')
        member.emergency_contact_relation = request.form.get('emergency_contact_relation')
        member.emergency_contact_phone = request.form.get('emergency_contact_phone')
        member.nid = request.form.get('nid')
        member.remarks = request.form.get('remarks')
        
        status = request.form.get('status')
        if status in ['Active', 'Inactive']:
            member.status = status
        
        try:
            # Profile Photo
            if request.form.get('delete_profile_photo'):
                if member.profile_photo_public_id: delete_image(member.profile_photo_public_id)
                member.profile_photo_url, member.profile_photo_public_id, member.profile_photo_time = None, None, None
            elif request.files.get('photo_file') and request.files.get('photo_file').filename:
                if member.profile_photo_public_id: delete_image(member.profile_photo_public_id)
                data = upload_image(request.files.get('photo_file'), 'members/profile')
                if data: member.profile_photo_url, member.profile_photo_public_id, member.profile_photo_time = data['secure_url'], data['public_id'], data['upload_time']
                    
            # NID Front
            if request.form.get('delete_nid_front'):
                if member.nid_front_public_id: delete_image(member.nid_front_public_id)
                member.nid_front_url, member.nid_front_public_id, member.nid_front_time = None, None, None
            elif request.files.get('nid_front_file') and request.files.get('nid_front_file').filename:
                if member.nid_front_public_id: delete_image(member.nid_front_public_id)
                data = upload_image(request.files.get('nid_front_file'), 'members/nid/front')
                if data: member.nid_front_url, member.nid_front_public_id, member.nid_front_time = data['secure_url'], data['public_id'], data['upload_time']

            # NID Back
            if request.form.get('delete_nid_back'):
                if member.nid_back_public_id: delete_image(member.nid_back_public_id)
                member.nid_back_url, member.nid_back_public_id, member.nid_back_time = None, None, None
            elif request.files.get('nid_back_file') and request.files.get('nid_back_file').filename:
                if member.nid_back_public_id: delete_image(member.nid_back_public_id)
                data = upload_image(request.files.get('nid_back_file'), 'members/nid/back')
                if data: member.nid_back_url, member.nid_back_public_id, member.nid_back_time = data['secure_url'], data['public_id'], data['upload_time']

            # Signature
            if request.form.get('delete_signature'):
                if member.signature_public_id: delete_image(member.signature_public_id)
                member.signature_url, member.signature_public_id, member.signature_time = None, None, None
            elif request.files.get('signature_file') and request.files.get('signature_file').filename:
                if member.signature_public_id: delete_image(member.signature_public_id)
                data = upload_image(request.files.get('signature_file'), 'members/signature')
                if data: member.signature_url, member.signature_public_id, member.signature_time = data['secure_url'], data['public_id'], data['upload_time']
        except Exception as e:
            flash(f'Image upload failed: {str(e)}', 'error')
            
        if safe_commit():
            flash('Member information updated successfully.', 'success')
            return redirect(url_for('member_profile', id=member.id))
            
    return render_template('edit_member.html', member=member, fund_sources=FundSource.query.all())

@app.route('/members/delete/<int:id>', methods=['POST'])
@login_required
def delete_member(id):
    member = db.session.get(Member, id)
    if not member:
        flash('Member not found.', 'error')
        return redirect(url_for('members'))
        
    images_to_delete = [
        member.profile_photo_public_id,
        member.nid_front_public_id,
        member.nid_back_public_id,
        member.signature_public_id
    ]
    for pid in images_to_delete:
        if pid:
            delete_image(pid)
            
    db.session.delete(member)
    if safe_commit():
        flash('Member and associated images deleted successfully.', 'success')
    return redirect(url_for('members'))

@app.route('/members/ledger')
@login_required
def member_ledger():
    members = Member.query.all()
    selected_member_id = request.args.get('member_id', type=int)
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    t_type = request.args.get('transaction_type')
    month = request.args.get('month')
    year = request.args.get('year')
    
    ledgers = []
    member = None
    summary = {}
    
    if selected_member_id:
        member = db.session.get(Member, selected_member_id)
        query = MemberLedger.query.filter_by(member_id=selected_member_id)
        
        if start_date: query = query.filter(MemberLedger.date >= start_date)
        if end_date: query = query.filter(MemberLedger.date <= end_date + ' 23:59:59')
        if t_type: query = query.filter(MemberLedger.transaction_type == t_type)
        if year:
            query = query.filter(db.extract('year', MemberLedger.date) == int(year))
            if month:
                query = query.filter(db.extract('month', MemberLedger.date) == int(month))
                
        ledgers = query.order_by(MemberLedger.date.asc()).all()
        
        # Summaries
        all_ledgers = MemberLedger.query.filter_by(member_id=selected_member_id).all()
        summary = {
            'total_contribution': sum(l.credit for l in all_ledgers if 'অনুদান' in l.transaction_type and 'বকেয়া' not in l.transaction_type),
            'total_loan_received': sum(l.debit for l in all_ledgers if 'ঋণ প্রদান' in l.transaction_type),
            'total_loan_paid': sum(l.credit for l in all_ledgers if 'ঋণ কিস্তি' in l.transaction_type),
            'outstanding_loan': sum(l.debit for l in all_ledgers if 'ঋণ প্রদান' in l.transaction_type) - sum(l.credit for l in all_ledgers if 'ঋণ কিস্তি' in l.transaction_type),
            'total_assistance': sum(l.debit for l in all_ledgers if 'সহায়তা' in l.transaction_type),
            'current_balance': all_ledgers[-1].balance if all_ledgers else 0.0
        }
        
    return render_template('member_ledger.html', members=members, ledgers=ledgers, member=member, summary=summary)

# ==========================================
# Funds
# ==========================================
@app.route('/sources')
@login_required
def fund_sources_dashboard():
    sources = FundSource.query.all()
    for s in sources:
        s.total_members = Member.query.filter_by(fund_source_id=s.id).count()
        ledgers = FundSourceLedger.query.filter_by(fund_source_id=s.id).all()
        s.total_contributions = sum(l.credit for l in ledgers if l.transaction_type == 'মাসিক অনুদান')
        s.total_external = sum(l.credit for l in ledgers if l.transaction_type == 'বহিরাগত অনুদান')
        s.total_expenses = sum(l.debit for l in ledgers if l.transaction_type in ('খরচ', 'সহায়তা'))
        s.last_transaction = ledgers[-1].date if ledgers else None
    return render_template('fund_sources_dashboard.html', sources=sources)
    
@app.route('/sources/ledger/<int:id>')
@login_required
def fund_source_ledger(id):
    source = db.session.get(FundSource, id)
    ledgers = FundSourceLedger.query.filter_by(fund_source_id=id).order_by(FundSourceLedger.date.asc()).all()
    return render_template('fund_source_ledger.html', source=source, ledgers=ledgers)

@app.route('/sources/add', methods=['GET', 'POST'])
@login_required
def add_source():
    if request.method == 'POST':
        if not FundSource.query.filter_by(name=request.form.get('name')).first():
            db.session.add(FundSource(name=request.form.get('name'), description=request.form.get('description')))
            if safe_commit():
                return redirect(url_for('manage_sources'))
    return render_template('add_source.html')
@app.route('/sources/report')
@login_required
def source_report(): return render_template('source_report.html', sources=FundSource.query.all())
@app.route('/sources/ledger')
@login_required
def source_ledger(): return render_template('source_ledger.html', sources=FundSource.query.all())

@app.route('/funds')
@login_required
def manage_funds(): return render_template('manage_funds.html', funds=Fund.query.order_by(Fund.date.desc()).all())
@app.route('/funds/add', methods=['GET', 'POST'])
@login_required
def add_fund():
    if request.method == 'POST':
        db.session.add(Fund(amount=float(request.form.get('amount')), member_id=request.form.get('member_id'), source_id=request.form.get('source_id')))
        if safe_commit():
            return redirect(url_for('manage_funds'))
    return render_template('add_fund.html', members=Member.query.all(), sources=FundSource.query.all())
@app.route('/funds/report')
@login_required
def fund_report(): return render_template('fund_report.html', funds=Fund.query.order_by(Fund.date.desc()).all())
@app.route('/funds/ledger')
@login_required
def fund_ledger(): return render_template('fund_ledger.html', funds=Fund.query.order_by(Fund.date.desc()).all())

# ==========================================
# Module 1: Assistance Routes
# ==========================================
@app.route('/assistance/beneficiary/add', methods=['GET', 'POST'])
@login_required
def add_assist_beneficiary():
    if request.method == 'POST':
        db.session.add(Beneficiary(name=request.form.get('name'), details=request.form.get('details')))
        if safe_commit():
            flash('Beneficiary added successfully.', 'success')
            return redirect(url_for('issue_assistance'))
    return render_template('assistance_add_beneficiary.html')

@app.route('/assistance/issue', methods=['GET', 'POST'])
@login_required
def issue_assistance():
    if request.method == 'POST':
        req = AssistanceRequest(amount=float(request.form.get('amount')), beneficiary_id=request.form.get('beneficiary_id'), status='Approved')
        db.session.add(req)
        if safe_commit():
            pay = AssistancePayment(amount=req.amount, assistance_request_id=req.id)
            db.session.add(pay)
            req.status = 'Paid'
            if safe_commit():
                flash('Assistance Issued and Paid successfully.', 'success')
                return redirect(url_for('assistance_report'))
    return render_template('issue_assistance.html', beneficiaries=Beneficiary.query.all())

@app.route('/assistance/report')
@login_required
def assistance_report():
    requests = AssistanceRequest.query.all()
    return render_template('assistance_report.html', requests=requests)

# ==========================================
# Module 2: Loan Routes
# ==========================================
@app.route('/loan/beneficiary/add', methods=['GET', 'POST'])
@login_required
def add_loan_beneficiary():
    if request.method == 'POST':
        db.session.add(LoanBeneficiary(name=request.form.get('name'), details=request.form.get('details')))
        if safe_commit():
            flash('Loan Beneficiary added successfully.', 'success')
            return redirect(url_for('issue_loan'))
    return render_template('loan_beneficiary.html')

@app.route('/loan/issue', methods=['GET', 'POST'])
@login_required
def issue_loan():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        dur = int(request.form.get('duration_months'))
        sdate_str = request.form.get('start_date')
        sdate = datetime.strptime(sdate_str, '%Y-%m-%d').date()
        
        monthly = round(amount / dur, 2)
        loan = Loan(amount=amount, start_date=sdate, duration_months=dur, monthly_installment=monthly, status='Running', beneficiary_id=request.form.get('beneficiary_id'))
        db.session.add(loan)
        if safe_commit():
            for i in range(1, dur + 1):
                due = sdate + relativedelta(months=i)
                inst = LoanInstallment(loan_id=loan.id, installment_number=i, due_date=due, amount=monthly)
                db.session.add(inst)
            if safe_commit():
                flash('Loan issued and installments generated.', 'success')
                return redirect(url_for('loan_report'))
    return render_template('issue_loan.html', beneficiaries=LoanBeneficiary.query.all())

@app.route('/loan/collect', methods=['GET', 'POST'])
@login_required
def collect_installment():
    if request.method == 'POST':
        inst = db.session.get(LoanInstallment, request.form.get('installment_id'))
        amt = float(request.form.get('amount'))
        
        pay = LoanPayment(loan_installment_id=inst.id, amount=amt)
        db.session.add(pay)
        
        total_paid = sum(p.amount for p in inst.payments) + amt
        if total_paid >= inst.amount:
            inst.status = 'Paid'
        else:
            inst.status = 'Partial'
        inst.payment_date = datetime.utcnow()
        if safe_commit():
            loan = inst.loan
            all_paid = all(i.status == 'Paid' for i in loan.installments)
            if all_paid:
                loan.status = 'Completed'
                safe_commit()
            flash('Installment collected.', 'success')
            return redirect(url_for('collect_installment'))
        
    running_loans = Loan.query.filter_by(status='Running').all()
    unpaid = []
    for l in running_loans:
        unpaid.extend([i for i in l.installments if i.status in ('Unpaid', 'Partial')])
    return render_template('collect_installment.html', installments=unpaid)

@app.route('/loan/history')
@login_required
def loan_history():
    loans = Loan.query.all()
    return render_template('loan_history.html', loans=loans)

@app.route('/loan/<int:loan_id>')
@login_required
def loan_details(loan_id):
    loan = db.session.get(Loan, loan_id)
    return render_template('loan_details.html', loan=loan)

@app.route('/loan/report')
@login_required
def loan_report():
    loans = Loan.query.all()
    return render_template('loan_report.html', loans=loans)

# ==========================================
# Member Contributions Routes
# ==========================================

def generate_current_month_contributions():
    now = datetime.utcnow()
    m = now.month
    y = now.year
    
    members = Member.query.filter(Member.status == 'Active', Member.monthly_contribution_amount.isnot(None)).all()
    for member in members:
        contrib = MemberContribution.query.filter_by(member_id=member.id, month=m, year=y).first()
        if not contrib:
            contrib = MemberContribution(member_id=member.id, month=m, year=y, expected_amount=member.monthly_contribution_amount)
            db.session.add(contrib)
            
            add_ledger_entry(member.id, 'মাসিক অনুদান (বকেয়া)', f"{m}/{y} মাসের প্রত্যাশিত অনুদান", debit=member.monthly_contribution_amount)
            safe_commit()

@app.route('/contributions/settings', methods=['GET', 'POST'])
@login_required
def contrib_settings():
    if request.method == 'POST':
        member_id = request.form.get('member_id')
        amount = request.form.get('monthly_amount')
        member = db.session.get(Member, member_id)
        if member:
            member.monthly_contribution_amount = float(amount)
            if safe_commit():
                flash("Setting updated.", "success")
        return redirect(url_for('contrib_settings'))
    return render_template('contribution_settings.html', members=Member.query.all())

@app.route('/contributions/manage')
@login_required
def contrib_manage():
    contribs = MemberContribution.query.order_by(MemberContribution.year.desc(), MemberContribution.month.desc()).all()
    return render_template('contribution_manage.html', contribs=contribs)

@app.route('/contributions/add', methods=['GET', 'POST'])
@login_required
def contrib_add():
    if request.method == 'POST':
        member_id = request.form.get('member_id')
        month = int(request.form.get('month'))
        year = int(request.form.get('year'))
        amount = float(request.form.get('expected_amount'))
        
        contrib = MemberContribution(member_id=member_id, month=month, year=year, expected_amount=amount)
        db.session.add(contrib)
        
        add_ledger_entry(member_id, 'মাসিক অনুদান (বকেয়া)', f"{month}/{year} মাসের প্রত্যাশিত অনুদান", debit=amount)
        
        if safe_commit():
            flash("Contribution created.", "success")
        return redirect(url_for('contrib_manage'))
    return render_template('contribution_add.html', members=Member.query.all())

@app.route('/contributions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def contrib_edit(id):
    contrib = db.session.get(MemberContribution, id)
    if request.method == 'POST':
        contrib.expected_amount = float(request.form.get('expected_amount'))
        if safe_commit():
            flash("Contribution updated.", "success")
        return redirect(url_for('contrib_manage'))
    return render_template('contribution_edit.html', contrib=contrib)

@app.route('/contributions/delete/<int:id>', methods=['POST'])
@login_required
def contrib_delete(id):
    contrib = db.session.get(MemberContribution, id)
    for p in contrib.payments:
        db.session.delete(p)
    db.session.delete(contrib)
    if safe_commit():
        flash("Contribution deleted.", "success")
    return redirect(url_for('contrib_manage'))

@app.route('/contributions/collect', methods=['GET', 'POST'])
@login_required
def contrib_collect():
    generate_current_month_contributions()
    if request.method == 'POST':
        if request.form.get('is_first_time'):
            m_id = request.form.get('new_member_id')
            amt = float(request.form.get('new_monthly_amount', 100))
            member = db.session.get(Member, m_id)
            if member:
                member.monthly_contribution_amount = amt
                if safe_commit():
                    generate_current_month_contributions()
                    flash('Default monthly contribution set. You can now collect the due.', 'success')
            return redirect(url_for('contrib_collect'))
            
        contrib_id = request.form.get('contribution_id')
        paid = float(request.form.get('paid_amount'))
        pmethod = request.form.get('payment_method')
        remarks = request.form.get('remarks')
        
        fund_source_id = request.form.get('fund_source_id')
        contrib = db.session.get(MemberContribution, contrib_id)
        if contrib:
            try:
                member_obj = db.session.get(Member, contrib.member_id)
                member_name = member_obj.full_name if member_obj else "Unknown"
                
                pay = MemberContributionPayment(contribution_id=contrib.id, paid_amount=paid, payment_method=pmethod, collector=current_user.full_name, remarks=remarks, fund_source_id=fund_source_id)
                db.session.add(pay)
                
                total_paid = sum(p.paid_amount for p in contrib.payments) + paid
                if total_paid >= contrib.expected_amount:
                    contrib.status = 'Paid'
                else:
                    contrib.status = 'Partial'
                    
                add_ledger_entry(contrib.member_id, 'মাসিক অনুদান', f"{contrib.month}/{contrib.year} মাসের অনুদান প্রদান", credit=paid, remarks=request.form.get('remarks', ''))
                if fund_source_id:
                    add_fund_source_ledger(fund_source_id, 'মাসিক অনুদান', f"{member_name} এর {contrib.month}/{contrib.year} অনুদান", credit=paid, member_id=contrib.member_id, remarks=remarks)
                
                if safe_commit():
                    flash('Contribution collected successfully', 'success')
                    return redirect(url_for('contrib_history'))
            except Exception as e:
                db.session.rollback()
                import traceback
                logging.error(f"Error collecting contribution: {str(e)}\n{traceback.format_exc()}")
                flash('Something went wrong while collecting the contribution. Please try again.', 'error')
            
    dues = MemberContribution.query.filter(MemberContribution.status.in_(['Due', 'Partial'])).all()
    for d in dues:
        d.total_paid = sum(p.paid_amount for p in d.payments)
        d.remaining = d.expected_amount - d.total_paid
        d.member = db.session.get(Member, d.member_id)
        
    first_time = Member.query.filter(Member.status == 'Active', Member.monthly_contribution_amount.is_(None)).all()
        
    return render_template('contribution_collect.html', dues=dues, first_time=first_time, fund_sources=FundSource.query.all())

@app.route('/contributions/history')
@login_required
def contrib_history():
    payments = MemberContributionPayment.query.order_by(MemberContributionPayment.payment_date.desc()).all()
    return render_template('contribution_history.html', payments=payments)

@app.route('/contributions/due')
@login_required
def contrib_due():
    generate_current_month_contributions()
    members = Member.query.all()
    due_users = []
    for m in members:
        tot_exp = db.session.query(db.func.sum(MemberContribution.expected_amount)).filter_by(member_id=m.id).scalar() or 0
        contribs = MemberContribution.query.filter_by(member_id=m.id).all()
        tot_paid = sum(sum(p.paid_amount for p in c.payments) for c in contribs)
        bal = tot_exp - tot_paid
        if bal > 0:
            due_users.append({'member': m, 'total_due': bal, 'total_paid': tot_paid})
            
    return render_template('contribution_due.html', due_users=due_users)

@app.route('/contributions/ledger')
@login_required
def contrib_ledger():
    members = Member.query.all()
    for m in members:
        m.ledgers = MemberLedger.query.filter_by(member_id=m.id).order_by(MemberLedger.date.asc()).all()
    return render_template('contribution_ledger.html', members=members)

@app.route('/contributions/report')
@login_required
def contrib_report():
    generate_current_month_contributions()
    
    tot_members = Member.query.count()
    now = datetime.utcnow()
    m, y = now.month, now.year
    
    cur_contribs = MemberContribution.query.filter_by(month=m, year=y).all()
    mon_exp = sum(c.expected_amount for c in cur_contribs)
    mon_col = sum(sum(p.paid_amount for p in c.payments if p.payment_date.month == m and p.payment_date.year == y) for c in MemberContribution.query.all())
    
    all_exp = db.session.query(db.func.sum(MemberContribution.expected_amount)).scalar() or 0
    all_col = db.session.query(db.func.sum(MemberContributionPayment.paid_amount)).scalar() or 0
    out_due = all_exp - all_col
    
    fully_paid_users = 0
    due_users = 0
    for m_obj in Member.query.all():
        u_exp = db.session.query(db.func.sum(MemberContribution.expected_amount)).filter_by(member_id=m_obj.id).scalar() or 0
        u_col_list = MemberContribution.query.filter_by(member_id=m_obj.id).all()
        u_col = sum(sum(p.paid_amount for p in c.payments) for c in u_col_list)
        if u_exp > u_col:
            due_users += 1
        else:
            fully_paid_users += 1
            
    pct = (all_col / all_exp * 100) if all_exp > 0 else 0
    
    return render_template('contribution_report.html', 
        tot_members=tot_members, mon_exp=mon_exp, mon_col=mon_col,
        out_due=out_due, fully_paid_users=fully_paid_users, due_users=due_users, pct=pct)

def init_db():
    with app.app_context():
        db.create_all()
        if not SystemUser.query.filter_by(username='admin').first():
            db.session.add(SystemUser(username='admin', password_hash=generate_password_hash('admin123'), full_name='Administrator', status='Active'))
            safe_commit()


@app.route('/contributions/payment/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_contribution_payment(id):
    pay = db.session.get(MemberContributionPayment, id)
    if not pay:
        flash('Payment not found', 'error')
        return redirect(url_for('contrib_history'))
        
    if request.method == 'POST':
        new_amount = float(request.form.get('paid_amount'))
        new_fund_source_id = request.form.get('fund_source_id', type=int)
        
        old_amount = pay.paid_amount
        old_fund_source_id = pay.fund_source_id
        
        pay.paid_amount = new_amount
        pay.fund_source_id = new_fund_source_id
        
        # Adjust old fund source
        if old_fund_source_id:
            add_fund_source_ledger(old_fund_source_id, 'অনুদান সংশোধন (বিয়োগ)', f"Payment {pay.id} Edit Subtraction", debit=old_amount, member_id=pay.contribution.member_id)
            
        # Add to new fund source
        if new_fund_source_id:
            add_fund_source_ledger(new_fund_source_id, 'অনুদান সংশোধন (যোগ)', f"Payment {pay.id} Edit Addition", credit=new_amount, member_id=pay.contribution.member_id)
            
        # Update MemberLedger by injecting a manual adjustment to balance things out
        diff = new_amount - old_amount
        if diff != 0:
            if diff > 0:
                add_ledger_entry(pay.contribution.member_id, 'ম্যানুয়াল', f"Payment {pay.id} Edited", credit=diff)
            else:
                add_ledger_entry(pay.contribution.member_id, 'ম্যানুয়াল', f"Payment {pay.id} Edited", debit=abs(diff))
                
        if safe_commit():
            flash("Contribution payment updated.", "success")
        return redirect(url_for('contrib_history'))
        
    fund_sources = FundSource.query.all()
    return render_template('edit_contribution_payment.html', pay=pay, fund_sources=fund_sources)

@app.route('/sources/assign-default', methods=['GET', 'POST'])
@login_required
def assign_default_fund_source():
    if request.method == 'POST':
        # the form will have field names like fund_source_for_MEMBERID
        updated_count = 0
        for key, val in request.form.items():
            if key.startswith('fund_source_for_') and val:
                try:
                    member_id = int(key.replace('fund_source_for_', ''))
                    member = db.session.get(Member, member_id)
                    if member:
                        member.fund_source_id = int(val)
                        updated_count += 1
                except:
                    pass
        if updated_count > 0:
            if safe_commit():
                flash(f"{updated_count} জন সদস্যের ডিফল্ট ফান্ড সোর্স আপডেট করা হয়েছে।", "success")
        return redirect(url_for('assign_default_fund_source'))
        
    members_without_fund = Member.query.filter((Member.fund_source_id == None) | (Member.fund_source_id == '')).all()
    fund_sources = FundSource.query.all()
    return render_template('assign_default_fund_source.html', members=members_without_fund, fund_sources=fund_sources)


@app.route('/sources/transfer', methods=['GET', 'POST'])
@login_required
def transfer_fund():
    if request.method == 'POST':
        from_id = request.form.get('from_fund_id', type=int)
        to_id = request.form.get('to_fund_id', type=int)
        amount = float(request.form.get('amount'))
        remarks = request.form.get('remarks')
        
        if from_id == to_id:
            flash("একই তহবিলে ট্রান্সফার করা যাবে না।", "error")
            return redirect(url_for('transfer_fund'))
            
        add_fund_source_ledger(from_id, 'ট্রান্সফার (প্রদান)', f"তহবিল স্থানান্তর", debit=amount, remarks=remarks)
        add_fund_source_ledger(to_id, 'ট্রান্সফার (গ্রহণ)', f"তহবিল গ্রহণ", credit=amount, remarks=remarks)
        
        if safe_commit():
            flash("তহবিল সফলভাবে ট্রান্সফার হয়েছে।", "success")
            return redirect(url_for('fund_sources_dashboard'))
            
    fund_sources = FundSource.query.all()
    return render_template('transfer_fund.html', fund_sources=fund_sources)

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=8080)
