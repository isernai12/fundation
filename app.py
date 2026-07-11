import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Admin, Member, MemberLedger, Fund, FundLedger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///foundation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

def init_db():
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Admin.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    member_count = Member.query.count()
    total_funds = db.session.query(db.func.sum(Fund.total_amount)).scalar() or 0.0
    recent_members = Member.query.order_by(Member.join_date.desc()).limit(5).all()
    return render_template('dashboard.html', member_count=member_count, total_funds=total_funds, recent_members=recent_members)

# --- User/Membership Management ---
@app.route('/users')
@login_required
def users_list():
    users = Member.query.all()
    return render_template('users/list.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def users_add():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        new_member = Member(name=name, email=email, phone=phone)
        db.session.add(new_member)
        db.session.commit()
        flash('User added successfully!')
        return redirect(url_for('users_list'))
    return render_template('users/add.html')

@app.route('/users/manage', methods=['GET', 'POST'])
@login_required
def users_manage():
    users = Member.query.all()
    return render_template('users/manage.html', users=users)

@app.route('/users/ledger')
@login_required
def users_ledger():
    ledgers = MemberLedger.query.order_by(MemberLedger.date.desc()).all()
    return render_template('users/ledger.html', ledgers=ledgers)

# --- Fund Management ---
@app.route('/funds/add', methods=['GET', 'POST'])
@login_required
def funds_add():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        amount = float(request.form.get('amount', 0))
        new_fund = Fund(name=name, description=description, total_amount=amount)
        db.session.add(new_fund)
        db.session.commit()
        
        if amount > 0:
            ledger = FundLedger(fund_id=new_fund.id, transaction_type='IN', amount=amount, description='Initial deposit')
            db.session.add(ledger)
            db.session.commit()

        flash('Fund added successfully!')
        return redirect(url_for('funds_manage'))
    return render_template('funds/add.html')

@app.route('/funds/manage')
@login_required
def funds_manage():
    funds = Fund.query.all()
    return render_template('funds/manage.html', funds=funds)

@app.route('/funds/report')
@login_required
def funds_report():
    funds = Fund.query.all()
    return render_template('funds/report.html', funds=funds)

@app.route('/funds/ledger')
@login_required
def funds_ledger():
    ledgers = FundLedger.query.order_by(FundLedger.date.desc()).all()
    return render_template('funds/ledger.html', ledgers=ledgers)

if __name__ == '__main__':
    if not os.path.exists('foundation.db'):
        init_db()
    app.run(debug=True, port=5000, host='0.0.0.0')
