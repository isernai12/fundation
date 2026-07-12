import re

with open('/workspaces/fundation/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace relationship in Member model
content = re.sub(
    r"contribution_ledgers = db\.relationship\('MemberContributionLedger', backref='member', lazy=True\)",
    "ledgers = db.relationship('MemberLedger', backref='member', lazy=True)",
    content
)

# Replace Model Definition
old_model = """class MemberContributionLedger(db.Model):
    __tablename__ = 'member_contribution_ledger'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    record_type = db.Column(db.String(20))
    amount = db.Column(db.Float, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))"""

new_model = """class MemberLedger(db.Model):
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
    db.session.add(entry)"""

content = content.replace(old_model, new_model)

# Update logic in generate_monthly_contributions
old_add_ledger_1 = """            last_ledger = MemberContributionLedger.query.filter_by(member_id=member.id).order_by(MemberContributionLedger.id.desc()).first()
            bal = last_ledger.balance + member.monthly_contribution_amount if last_ledger else member.monthly_contribution_amount
            ledger = MemberContributionLedger(member_id=member.id, record_type='Expected', amount=member.monthly_contribution_amount, balance=bal, description=f"Expected Contribution for {m}/{y}")
            db.session.add(ledger)"""

new_add_ledger_1 = """            add_ledger_entry(member.id, 'মাসিক অনুদান (বকেয়া)', f"{m}/{y} মাসের প্রত্যাশিত অনুদান", debit=member.monthly_contribution_amount)"""
content = content.replace(old_add_ledger_1, new_add_ledger_1)

# Update logic in add_contribution (manual)
old_add_ledger_2 = """        last_ledger = MemberContributionLedger.query.filter_by(member_id=member_id).order_by(MemberContributionLedger.id.desc()).first()
        bal = last_ledger.balance + amount if last_ledger else amount
        ledger = MemberContributionLedger(member_id=member_id, record_type='Expected', amount=amount, balance=bal, description=f"Manual Expected for {month}/{year}")
        db.session.add(ledger)"""

new_add_ledger_2 = """        add_ledger_entry(member_id, 'মাসিক অনুদান (বকেয়া)', f"{month}/{year} মাসের প্রত্যাশিত অনুদান", debit=amount)"""
content = content.replace(old_add_ledger_2, new_add_ledger_2)

# Update logic in collect_contribution
old_add_ledger_3 = """            last_ledger = MemberContributionLedger.query.filter_by(member_id=contrib.member_id).order_by(MemberContributionLedger.id.desc()).first()
            bal = last_ledger.balance - paid if last_ledger else -paid
            ledger = MemberContributionLedger(member_id=contrib.member_id, record_type='Payment', amount=paid, balance=bal, description=f"Payment for {contrib.month}/{contrib.year}")
            db.session.add(ledger)"""

new_add_ledger_3 = """            add_ledger_entry(contrib.member_id, 'মাসিক অনুদান', f"{contrib.month}/{contrib.year} মাসের অনুদান প্রদান", credit=paid, remarks=request.form.get('remarks', ''))"""
content = content.replace(old_add_ledger_3, new_add_ledger_3)

# Replace member_profile ledger loading
old_load_ledger = """        m.ledgers = MemberContributionLedger.query.filter_by(member_id=m.id).order_by(MemberContributionLedger.id.asc()).all()"""
new_load_ledger = """        m.ledgers = MemberLedger.query.filter_by(member_id=m.id).order_by(MemberLedger.date.asc()).all()"""
content = content.replace(old_load_ledger, new_load_ledger)

# Re-write member_ledger route
old_route = """def member_ledger():
    return render_template('member_ledger.html', members=Member.query.all())"""
new_route = """def member_ledger():
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
        
    return render_template('member_ledger.html', members=members, ledgers=ledgers, member=member, summary=summary)"""
content = content.replace(old_route, new_route)

# Now, we should also intercept Loan issuance and Assistance and inject add_ledger_entry if member_id is provided.
# Actually wait, the existing code doesn't set member_id on loans because we just added it to the DB schema!
# In issue_loan route, we need to save member_id.
# And same for assistance.

# issue_loan route
old_issue_loan = """        db.session.add(Loan(amount=amount, start_date=start_date, duration_months=duration, monthly_installment=installment, beneficiary_id=beneficiary_id))"""
new_issue_loan = """        member_id = request.form.get('member_id')
        new_loan = Loan(amount=amount, start_date=start_date, duration_months=duration, monthly_installment=installment, beneficiary_id=beneficiary_id, member_id=member_id)
        db.session.add(new_loan)
        db.session.flush()
        if member_id:
            add_ledger_entry(member_id, 'ঋণ প্রদান', 'নতুন ঋণ প্রদান', debit=amount)"""
content = content.replace(old_issue_loan, new_issue_loan)

# loan installment payment
old_loan_pay = """        db.session.add(LoanPayment(loan_installment_id=inst.id, amount=inst.amount))
        inst.status = 'Paid'"""
new_loan_pay = """        db.session.add(LoanPayment(loan_installment_id=inst.id, amount=inst.amount))
        inst.status = 'Paid'
        db.session.flush()
        if inst.loan.member_id:
            add_ledger_entry(inst.loan.member_id, 'ঋণ কিস্তি', f"কিস্তি নং {inst.installment_number} জমা", credit=inst.amount)"""
content = content.replace(old_loan_pay, new_loan_pay)

# assistance issue
old_assist = """        db.session.add(AssistanceRequest(amount=amount, beneficiary_id=beneficiary_id))"""
new_assist = """        member_id = request.form.get('member_id')
        db.session.add(AssistanceRequest(amount=amount, beneficiary_id=beneficiary_id, member_id=member_id))
        if member_id:
            add_ledger_entry(member_id, 'সহায়তা', 'সহায়তা প্রদান', debit=amount)"""
content = content.replace(old_assist, new_assist)

with open('/workspaces/fundation/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
