import re

with open('/workspaces/fundation/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

bulk_update_route = """
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
"""

if "/sources/assign-default" not in content:
    content = content.replace("def transfer_fund():", bulk_update_route + "\n\n@app.route('/sources/transfer', methods=['GET', 'POST'])\n@login_required\ndef transfer_fund():")

with open('/workspaces/fundation/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Bulk update route patched in app.py.")
