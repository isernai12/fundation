import re

with open('/workspaces/fundation/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update add_member
old_add_member = """            special_skills=request.form.get('special_skills'),
            foundation_source=request.form.get('foundation_source'),"""
new_add_member = """            special_skills=request.form.get('special_skills'),
            foundation_source=request.form.get('foundation_source'),
            fund_source_id=request.form.get('fund_source_id'),"""
content = content.replace(old_add_member, new_add_member)

# Pass fund_sources to add_member.html
old_add_render = "return render_template('add_member.html')"
new_add_render = "return render_template('add_member.html', fund_sources=FundSource.query.all())"
content = content.replace(old_add_render, new_add_render)

# 2. Update edit_member
old_edit_member = """        member.organization = request.form.get('organization')
        member.special_skills = request.form.get('special_skills')
        member.foundation_source = request.form.get('foundation_source')"""
new_edit_member = """        member.organization = request.form.get('organization')
        member.special_skills = request.form.get('special_skills')
        member.foundation_source = request.form.get('foundation_source')
        member.fund_source_id = request.form.get('fund_source_id')"""
content = content.replace(old_edit_member, new_edit_member)

old_edit_render = "return render_template('edit_member.html', member=member)"
new_edit_render = "return render_template('edit_member.html', member=member, fund_sources=FundSource.query.all())"
content = content.replace(old_edit_render, new_edit_render)

# 3. Update collect_contribution
old_collect = """        contrib = db.session.get(MemberContribution, contrib_id)
        if contrib:
            pay = MemberContributionPayment(contribution_id=contrib.id, paid_amount=paid, payment_method=pmethod, collector=current_user.full_name, remarks=remarks)
            db.session.add(pay)
            
            total_paid = sum(p.paid_amount for p in contrib.payments) + paid
            if total_paid >= contrib.expected_amount:
                contrib.status = 'Paid'
            else:
                contrib.status = 'Partial'
                
            add_ledger_entry(contrib.member_id, 'মাসিক অনুদান', f"{contrib.month}/{contrib.year} মাসের অনুদান প্রদান", credit=paid, remarks=request.form.get('remarks', ''))"""

new_collect = """        fund_source_id = request.form.get('fund_source_id')
        contrib = db.session.get(MemberContribution, contrib_id)
        if contrib:
            pay = MemberContributionPayment(contribution_id=contrib.id, paid_amount=paid, payment_method=pmethod, collector=current_user.full_name, remarks=remarks, fund_source_id=fund_source_id)
            db.session.add(pay)
            
            total_paid = sum(p.paid_amount for p in contrib.payments) + paid
            if total_paid >= contrib.expected_amount:
                contrib.status = 'Paid'
            else:
                contrib.status = 'Partial'
                
            add_ledger_entry(contrib.member_id, 'মাসিক অনুদান', f"{contrib.month}/{contrib.year} মাসের অনুদান প্রদান", credit=paid, remarks=request.form.get('remarks', ''))
            if fund_source_id:
                add_fund_source_ledger(fund_source_id, 'মাসিক অনুদান', f"{contrib.member.full_name} এর {contrib.month}/{contrib.year} অনুদান", credit=paid, member_id=contrib.member_id, remarks=remarks)"""
content = content.replace(old_collect, new_collect)

old_collect_render = "return render_template('contribution_collect.html', dues=dues, first_time=first_time)"
new_collect_render = "return render_template('contribution_collect.html', dues=dues, first_time=first_time, fund_sources=FundSource.query.all())"
content = content.replace(old_collect_render, new_collect_render)

# 4. Add Edit Contribution Route (To edit payments and update fund source ledger automatically)
edit_payment_route = """
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
"""
if "/contributions/payment/edit/" not in content:
    content += edit_payment_route

# 5. Add Fund Transfer Route
transfer_route = """
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
"""
if "/sources/transfer" not in content:
    content += transfer_route

# 6. Replace Manage Sources with Dashboard
old_manage_sources = """@app.route('/sources')
@login_required
def manage_sources(): return render_template('manage_sources.html', sources=FundSource.query.all())"""

new_dashboard = """@app.route('/sources')
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
"""
content = content.replace(old_manage_sources, new_dashboard)

with open('/workspaces/fundation/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Routes patched successfully.")
