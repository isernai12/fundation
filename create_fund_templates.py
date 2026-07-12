import os

def write_file(filename, content):
    with open(f'/workspaces/fundation/templates/{filename}', 'w', encoding='utf-8') as f:
        f.write(content.strip())

# 1. fund_sources_dashboard.html
dashboard = """
{% extends 'base.html' %}
{% block header_title %}তহবিল ড্যাশবোর্ড (Fund Sources Dashboard){% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto space-y-6">
    <div class="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <h2 class="text-lg font-bold text-gray-800">তহবিলসমূহ</h2>
        <div class="flex gap-2">
            <a href="{{ url_for('transfer_fund') }}" class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">তহবিল ট্রান্সফার</a>
            <a href="{{ url_for('add_source') }}" class="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-blue-700">নতুন তহবিল যোগ করুন</a>
        </div>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for s in sources %}
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col relative">
            <h3 class="text-xl font-bold text-gray-800 mb-1">{{ s.name }}</h3>
            <p class="text-sm text-gray-500 mb-4 line-clamp-2">{{ s.description or 'কোনো বিবরণ নেই' }}</p>
            
            <div class="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-100">
                <div class="flex justify-between items-center mb-1">
                    <span class="text-sm font-semibold text-gray-600">বর্তমান ব্যালেন্স:</span>
                    <span class="text-xl font-bold text-primary">৳ {{ "{:,.2f}".format(s.balance) }}</span>
                </div>
                <div class="flex justify-between items-center text-xs text-gray-500">
                    <span>প্রারম্ভিক ব্যালেন্স:</span>
                    <span>৳ {{ "{:,.2f}".format(s.opening_balance) }}</span>
                </div>
            </div>
            
            <div class="space-y-2 mb-6">
                <div class="flex justify-between text-sm">
                    <span class="text-gray-600">মোট সদস্য:</span>
                    <span class="font-medium text-gray-800">{{ s.total_members }} জন</span>
                </div>
                <div class="flex justify-between text-sm">
                    <span class="text-gray-600">মাসিক অনুদান:</span>
                    <span class="font-medium text-green-600">৳ {{ "{:,.2f}".format(s.total_contributions) }}</span>
                </div>
                <div class="flex justify-between text-sm">
                    <span class="text-gray-600">বহিরাগত অনুদান:</span>
                    <span class="font-medium text-blue-600">৳ {{ "{:,.2f}".format(s.total_external) }}</span>
                </div>
                <div class="flex justify-between text-sm">
                    <span class="text-gray-600">মোট খরচ/সহায়তা:</span>
                    <span class="font-medium text-red-600">৳ {{ "{:,.2f}".format(s.total_expenses) }}</span>
                </div>
                <div class="flex justify-between text-sm text-gray-400 mt-2 border-t pt-2">
                    <span>শেষ লেনদেন:</span>
                    <span>{{ s.last_transaction.strftime('%Y-%m-%d %H:%M') if s.last_transaction else 'নেই' }}</span>
                </div>
            </div>
            
            <div class="mt-auto pt-4 border-t border-gray-100 flex justify-between gap-2">
                <a href="{{ url_for('fund_source_ledger', id=s.id) }}" class="flex-1 text-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200">লেজার দেখুন</a>
                <!-- Optional Edit button if available -->
            </div>
        </div>
        {% else %}
        <div class="col-span-full bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center text-gray-500">
            <p class="text-lg">কোনো তহবিল পাওয়া যায়নি।</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""
write_file('fund_sources_dashboard.html', dashboard)

# 2. fund_source_ledger.html
ledger = """
{% extends 'base.html' %}
{% block header_title %}{{ source.name }} - লেজার{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto space-y-6">
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        
        <div class="p-4 border-b border-gray-100 flex flex-col md:flex-row justify-between items-center gap-4 bg-gray-50">
            <div>
                <h3 class="font-bold text-gray-800">{{ source.name }} এর লেজার</h3>
                <p class="text-sm text-gray-500">বর্তমান ব্যালেন্স: ৳ {{ "{:,.2f}".format(source.balance) }}</p>
            </div>
            <div class="flex gap-2">
                <button onclick="window.print()" class="px-3 py-1.5 bg-white border border-gray-200 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 shadow-sm flex items-center">
                    প্রিন্ট লেজার
                </button>
                <button onclick="exportTableToCSV('fund_ledger_{{ source.id }}.csv')" class="px-3 py-1.5 bg-white border border-green-200 text-green-600 rounded-md text-sm font-medium hover:bg-green-50 shadow-sm flex items-center">
                    Excel এক্সপোর্ট
                </button>
            </div>
        </div>
        
        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-gray-600" id="ledgerTable">
                <thead class="bg-gray-50 text-gray-700 text-xs uppercase font-semibold border-b">
                    <tr>
                        <th class="px-4 py-3">তারিখ</th>
                        <th class="px-4 py-3">রেফারেন্স</th>
                        <th class="px-4 py-3">লেনদেনের ধরন</th>
                        <th class="px-4 py-3">সদস্য / বিবরণ</th>
                        <th class="px-4 py-3 text-right">ডেবিট (খরচ) ৳</th>
                        <th class="px-4 py-3 text-right">ক্রেডিট (জমা) ৳</th>
                        <th class="px-4 py-3 text-right">ব্যালেন্স (৳)</th>
                        <th class="px-4 py-3">মন্তব্য</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                    <!-- Opening Balance Row -->
                    <tr class="bg-blue-50">
                        <td class="px-4 py-3 whitespace-nowrap">-</td>
                        <td class="px-4 py-3">-</td>
                        <td class="px-4 py-3 font-medium">প্রারম্ভিক ব্যালেন্স</td>
                        <td class="px-4 py-3">-</td>
                        <td class="px-4 py-3 text-right">-</td>
                        <td class="px-4 py-3 text-right font-medium text-green-600">{{ "{:,.2f}".format(source.opening_balance) }}</td>
                        <td class="px-4 py-3 text-right font-bold text-gray-800">{{ "{:,.2f}".format(source.opening_balance) }}</td>
                        <td class="px-4 py-3 text-xs text-gray-500"></td>
                    </tr>
                    
                    {% for l in ledgers %}
                    <tr class="hover:bg-gray-50 transition-colors">
                        <td class="px-4 py-3 whitespace-nowrap">{{ l.date.strftime('%Y-%m-%d %H:%M') }}</td>
                        <td class="px-4 py-3 text-xs text-gray-500">{{ l.reference_number or '-' }}</td>
                        <td class="px-4 py-3"><span class="px-2 py-1 bg-gray-100 text-gray-600 rounded-md text-xs font-medium">{{ l.transaction_type }}</span></td>
                        <td class="px-4 py-3">
                            {% if l.member_id %}
                            <a href="{{ url_for('member_view', id=l.member_id) }}" class="text-primary hover:underline font-medium">সদস্য #{{ l.member_id }}</a><br>
                            {% endif %}
                            <span class="text-xs text-gray-500">{{ l.description }}</span>
                        </td>
                        <td class="px-4 py-3 text-right {% if l.debit > 0 %}text-red-600 font-medium{% endif %}">{{ "{:,.2f}".format(l.debit) if l.debit else '-' }}</td>
                        <td class="px-4 py-3 text-right {% if l.credit > 0 %}text-green-600 font-medium{% endif %}">{{ "{:,.2f}".format(l.credit) if l.credit else '-' }}</td>
                        <td class="px-4 py-3 text-right font-bold text-gray-800">{{ "{:,.2f}".format(l.balance) }}</td>
                        <td class="px-4 py-3 text-xs text-gray-500">{{ l.remarks or '-' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
function exportTableToCSV(filename) {
    var csv = [];
    var rows = document.querySelectorAll("table#ledgerTable tr");
    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll("td, th");
        for (var j = 0; j < cols.length; j++) row.push('"' + cols[j].innerText.replace(/"/g, '""') + '"');
        csv.push(row.join(","));        
    }
    var csvFile = new Blob([csv.join("\\n")], {type: "text/csv"});
    var downloadLink = document.createElement("a");
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = "none";
    document.body.appendChild(downloadLink);
    downloadLink.click();
}
</script>
{% endblock %}
"""
write_file('fund_source_ledger.html', ledger)

# 3. transfer_fund.html
transfer = """
{% extends 'base.html' %}
{% block header_title %}তহবিল ট্রান্সফার{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto bg-white rounded-xl shadow-sm border border-gray-100 p-8">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">এক তহবিল থেকে অন্য তহবিলে টাকা স্থানান্তর</h2>
    
    <form method="POST" class="space-y-6">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">প্রেরক তহবিল (From Fund) <span class="text-red-500">*</span></label>
            <select name="from_fund_id" required class="w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary no-bn">
                <option value="">তহবিল নির্বাচন করুন</option>
                {% for fs in fund_sources %}
                <option value="{{ fs.id }}">{{ fs.name }} (ব্যালেন্স: ৳ {{ "{:,.2f}".format(fs.balance) }})</option>
                {% endfor %}
            </select>
        </div>
        
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">প্রাপক তহবিল (To Fund) <span class="text-red-500">*</span></label>
            <select name="to_fund_id" required class="w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary no-bn">
                <option value="">তহবিল নির্বাচন করুন</option>
                {% for fs in fund_sources %}
                <option value="{{ fs.id }}">{{ fs.name }} (ব্যালেন্স: ৳ {{ "{:,.2f}".format(fs.balance) }})</option>
                {% endfor %}
            </select>
        </div>
        
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">পরিমাণ (Amount ৳) <span class="text-red-500">*</span></label>
            <input type="number" name="amount" step="0.01" min="1" required class="w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary no-bn">
        </div>
        
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">মন্তব্য (Remarks)</label>
            <textarea name="remarks" rows="2" class="w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary"></textarea>
        </div>
        
        <div class="pt-4 flex gap-4">
            <button type="submit" class="flex-1 bg-primary text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-blue-700 transition-colors">ট্রান্সফার করুন</button>
            <a href="{{ url_for('fund_sources_dashboard') }}" class="flex-1 bg-gray-100 text-gray-700 rounded-lg px-4 py-2 text-sm font-medium hover:bg-gray-200 transition-colors text-center flex items-center justify-center">বাতিল</a>
        </div>
    </form>
</div>
{% endblock %}
"""
write_file('transfer_fund.html', transfer)

# 4. edit_contribution_payment.html
edit_payment = """
{% extends 'base.html' %}
{% block header_title %}অনুদান পেমেন্ট সম্পাদনা{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto bg-white rounded-xl shadow-sm border border-gray-100 p-8">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">পেমেন্ট সংশোধন করুন</h2>
    
    <div class="bg-gray-50 rounded-lg p-4 mb-6 border border-gray-200">
        <p class="text-sm text-gray-600"><strong>সদস্য:</strong> {{ pay.contribution.member.full_name }}</p>
        <p class="text-sm text-gray-600"><strong>মাস/বছর:</strong> {{ pay.contribution.month }}/{{ pay.contribution.year }}</p>
    </div>
    
    <form method="POST" class="space-y-6">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">জমা টাকার পরিমাণ <span class="text-red-500">*</span></label>
            <input type="number" name="paid_amount" step="0.01" value="{{ pay.paid_amount }}" required class="w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary no-bn">
        </div>
        
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">তহবিল (Fund Source) <span class="text-red-500">*</span></label>
            <select name="fund_source_id" required class="w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary no-bn">
                <option value="">তহবিল নির্বাচন করুন</option>
                {% for fs in fund_sources %}
                <option value="{{ fs.id }}" {% if pay.fund_source_id == fs.id %}selected{% endif %}>{{ fs.name }}</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="pt-4 flex gap-4">
            <button type="submit" class="flex-1 bg-primary text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-blue-700 transition-colors">হালনাগাদ করুন</button>
            <a href="{{ url_for('contrib_history') }}" class="flex-1 bg-gray-100 text-gray-700 rounded-lg px-4 py-2 text-sm font-medium hover:bg-gray-200 transition-colors text-center flex items-center justify-center">বাতিল</a>
        </div>
    </form>
</div>
{% endblock %}
"""
write_file('edit_contribution_payment.html', edit_payment)

print("Templates created successfully.")
