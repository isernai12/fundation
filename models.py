from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Active')
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    ledgers = db.relationship('UserLedger', backref='user', lazy=True, cascade='all, delete-orphan')
    funds = db.relationship('Fund', backref='user', lazy=True)

class UserLedger(db.Model):
    __tablename__ = 'user_ledgers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    activity_type = db.Column(db.String(50), nullable=False) 
    amount = db.Column(db.Float, default=0.0)
    description = db.Column(db.String(255))

class FundSource(db.Model):
    __tablename__ = 'fund_sources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # e.g. "Village X", "Org Y"
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    funds = db.relationship('Fund', backref='source', lazy=True)
    ledgers = db.relationship('FundLedger', backref='source', lazy=True)

class Fund(db.Model):
    __tablename__ = 'funds'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('fund_sources.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))
    
    ledgers = db.relationship('FundLedger', backref='fund', lazy=True, cascade='all, delete-orphan')

class FundLedger(db.Model):
    __tablename__ = 'fund_ledgers'
    id = db.Column(db.Integer, primary_key=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('funds.id'), nullable=True) # Linked to a specific fund income
    source_id = db.Column(db.Integer, db.ForeignKey('fund_sources.id'), nullable=True) # Used to trace expense/income to a category
    transaction_type = db.Column(db.String(20), nullable=False) # 'Income' or 'Expense'
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))
