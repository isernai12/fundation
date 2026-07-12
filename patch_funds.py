import re

with open('/workspaces/fundation/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Member model
content = re.sub(
    r"date_of_birth = db\.Column\(db\.Date\)",
    "date_of_birth = db.Column(db.Date)\n    fund_source_id = db.Column(db.Integer, db.ForeignKey('fund_sources.id'), nullable=True)",
    content
)

# 2. Update FundSource model & Add FundSourceLedger
old_fund_source = """class FundSource(db.Model):
    __tablename__ = 'fund_sources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)
    funds = db.relationship('Fund', backref='source', lazy=True)"""

new_fund_source = """class FundSource(db.Model):
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
"""

content = content.replace(old_fund_source, new_fund_source)

# 3. Update MemberContributionPayment
old_mcp = """    payment_method = db.Column(db.String(50))
    collector = db.Column(db.String(100))
    remarks = db.Column(db.Text)"""

new_mcp = """    payment_method = db.Column(db.String(50))
    collector = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    fund_source_id = db.Column(db.Integer, db.ForeignKey('fund_sources.id'), nullable=True)"""
content = content.replace(old_mcp, new_mcp)

with open('/workspaces/fundation/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Models patched.")
