import os

templates_dir = '/workspaces/fundation/templates'

files = {
    'login.html': """{% extends 'base.html' %}
{% block header_title %}Login{% endblock %}
{% block content %}
<div class="max-w-md mx-auto mt-20 bg-white p-8 rounded-xl shadow-md border border-gray-100">
    <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 text-primary mb-4">
            <i data-lucide="building-2" class="w-8 h-8"></i>
        </div>
        <h2 class="text-2xl font-bold text-gray-800">Welcome Back</h2>
        <p class="text-sm text-gray-500 mt-1">Sign in to your account to continue</p>
    </div>
    
    <form method="POST" action="{{ url_for('login') }}" class="space-y-5">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i data-lucide="user" class="w-5 h-5 text-gray-400"></i>
                </div>
                <input type="text" name="username" required class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all" placeholder="Enter your username">
            </div>
        </div>
        
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i data-lucide="lock" class="w-5 h-5 text-gray-400"></i>
                </div>
                <input type="password" name="password" required class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all" placeholder="••••••••">
            </div>
        </div>
        
        <button type="submit" class="w-full bg-primary text-white font-medium py-2.5 rounded-lg hover:bg-blue-700 transition-colors shadow-sm">
            Sign In
        </button>
    </form>
</div>
{% endblock %}""",

    'dashboard.html': """{% extends 'base.html' %}
{% block header_title %}Dashboard Overview{% endblock %}
{% block content %}
<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
    
    <!-- Total Funds -->
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
        <div class="w-14 h-14 rounded-full bg-green-50 flex items-center justify-center mr-4 text-green-600">
            <i data-lucide="piggy-bank" class="w-7 h-7"></i>
        </div>
        <div>
            <p class="text-sm font-medium text-gray-500">Total Funds Collected</p>
            <h3 class="text-2xl font-bold text-gray-800">${{ "%.2f"|format(total_funds) }}</h3>
        </div>
    </div>

    <!-- Total Loans Issued -->
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
        <div class="w-14 h-14 rounded-full bg-blue-50 flex items-center justify-center mr-4 text-blue-600">
            <i data-lucide="coins" class="w-7 h-7"></i>
        </div>
        <div>
            <p class="text-sm font-medium text-gray-500">Total Loans Issued</p>
            <h3 class="text-2xl font-bold text-gray-800">${{ "%.2f"|format(total_loans) }}</h3>
        </div>
    </div>

    <!-- Total Grants -->
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
        <div class="w-14 h-14 rounded-full bg-purple-50 flex items-center justify-center mr-4 text-purple-600">
            <i data-lucide="gift" class="w-7 h-7"></i>
        </div>
        <div>
            <p class="text-sm font-medium text-gray-500">Total Grants Given</p>
            <h3 class="text-2xl font-bold text-gray-800">${{ "%.2f"|format(total_grants) }}</h3>
        </div>
    </div>

    <!-- Total Recovered -->
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
        <div class="w-14 h-14 rounded-full bg-orange-50 flex items-center justify-center mr-4 text-orange-600">
            <i data-lucide="refresh-cw" class="w-7 h-7"></i>
        </div>
        <div>
            <p class="text-sm font-medium text-gray-500">Loan Amount Recovered</p>
            <h3 class="text-2xl font-bold text-gray-800">${{ "%.2f"|format(total_recovered) }}</h3>
        </div>
    </div>

</div>

<div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
    <h2 class="text-lg font-bold text-gray-800 mb-4">Welcome to Foundation Management System</h2>
    <p class="text-gray-600">Use the sidebar to navigate through the modules. You can manage users, track funds, and issue assistances (loans and grants).</p>
</div>
{% endblock %}""",

    'add_user.html': """{% extends 'base.html' %}
{% block header_title %}Add New User{% endblock %}
{% block content %}
<div class="max-w-2xl bg-white p-8 rounded-xl shadow-sm border border-gray-100">
    <h2 class="text-xl font-bold text-gray-800 mb-6">User Details</h2>
    <form method="POST" action="{{ url_for('add_user') }}" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input type="text" name="name" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select name="role" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
                    <option value="Member">Member</option>
                    <option value="Admin">Admin</option>
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <input type="text" name="username" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input type="password" name="password" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
            </div>
        </div>
        <div class="flex justify-end pt-4">
            <button type="submit" class="bg-primary text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm">Add User</button>
        </div>
    </form>
</div>
{% endblock %}""",

    'manage_users.html': """{% extends 'base.html' %}
{% block header_title %}Manage Users{% endblock %}
{% block content %}
<div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-gray-50 border-b border-gray-200">
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Name</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Username</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Role</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                {% for user in users %}
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4 text-sm text-gray-600">#{{ user.id }}</td>
                    <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ user.name }}</td>
                    <td class="px-6 py-4 text-sm text-gray-600">{{ user.username }}</td>
                    <td class="px-6 py-4 text-sm">
                        <span class="px-2.5 py-1 rounded-full text-xs font-medium {% if user.role == 'Admin' %}bg-purple-100 text-purple-700{% else %}bg-blue-100 text-blue-700{% endif %}">
                            {{ user.role }}
                        </span>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}""",

    'user_ledger.html': """{% extends 'base.html' %}
{% block header_title %}User Ledger{% endblock %}
{% block content %}
<div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
    <p class="text-gray-600 mb-6">Detailed ledger for each user (donations made).</p>
    
    <div class="space-y-6">
        {% for user in users %}
        <div class="border border-gray-200 rounded-lg p-5">
            <h3 class="text-lg font-bold text-gray-800 mb-3"><i data-lucide="user" class="inline w-5 h-5 mr-2"></i>{{ user.name }} ({{ user.username }})</h3>
            {% if user.funds %}
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm">
                    <thead>
                        <tr class="bg-gray-50">
                            <th class="px-4 py-2 font-medium text-gray-600">Date</th>
                            <th class="px-4 py-2 font-medium text-gray-600">Source</th>
                            <th class="px-4 py-2 font-medium text-gray-600">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for fund in user.funds %}
                        <tr class="border-t border-gray-100">
                            <td class="px-4 py-2 text-gray-600">{{ fund.date.strftime('%Y-%m-%d %H:%M') }}</td>
                            <td class="px-4 py-2 text-gray-600">{{ fund.source.name }}</td>
                            <td class="px-4 py-2 font-medium text-green-600">${{ "%.2f"|format(fund.amount) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <p class="text-sm text-gray-500 italic">No funds contributed yet.</p>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}""",

    'add_source.html': """{% extends 'base.html' %}
{% block header_title %}Add Fund Source{% endblock %}
{% block content %}
<div class="max-w-2xl bg-white p-8 rounded-xl shadow-sm border border-gray-100">
    <form method="POST" action="{{ url_for('add_source') }}" class="space-y-6">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Source Name</label>
            <input type="text" name="name" placeholder="e.g., Village X, Organization Y" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description (Optional)</label>
            <textarea name="description" rows="3" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none"></textarea>
        </div>
        <div class="flex justify-end pt-4">
            <button type="submit" class="bg-primary text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm">Add Source</button>
        </div>
    </form>
</div>
{% endblock %}""",

    'manage_sources.html': """{% extends 'base.html' %}
{% block header_title %}Manage Fund Sources{% endblock %}
{% block content %}
<div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-gray-50 border-b border-gray-200">
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Source Name</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Description</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                {% for source in sources %}
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4 text-sm text-gray-600">#{{ source.id }}</td>
                    <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ source.name }}</td>
                    <td class="px-6 py-4 text-sm text-gray-600">{{ source.description }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}""",

    'source_report.html': """{% extends 'base.html' %}
{% block header_title %}Fund Source Report{% endblock %}
{% block content %}
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    {% for source in sources %}
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div class="flex justify-between items-start mb-4">
            <div>
                <h3 class="text-lg font-bold text-gray-800">{{ source.name }}</h3>
                <p class="text-sm text-gray-500">{{ source.description }}</p>
            </div>
            <div class="bg-blue-50 text-primary p-2 rounded-lg">
                <i data-lucide="map-pin" class="w-5 h-5"></i>
            </div>
        </div>
        <div class="mt-4 pt-4 border-t border-gray-100">
            {% set total = namespace(value=0) %}
            {% for fund in source.funds %}
                {% set total.value = total.value + fund.amount %}
            {% endfor %}
            <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Total Funds Received:</span>
                <span class="text-xl font-bold text-green-600">${{ "%.2f"|format(total.value) }}</span>
            </div>
            <div class="flex justify-between items-center mt-2">
                <span class="text-sm text-gray-600">Total Contributions:</span>
                <span class="text-sm font-medium text-gray-800">{{ source.funds|length }}</span>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}""",

    'source_ledger.html': """{% extends 'base.html' %}
{% block header_title %}Source Ledger{% endblock %}
{% block content %}
<div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-8">
    {% for source in sources %}
    <div>
        <h3 class="text-lg font-bold text-gray-800 mb-4 border-b pb-2"><i data-lucide="map" class="inline w-5 h-5 mr-2"></i>{{ source.name }} Ledger</h3>
        {% if source.funds %}
        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
                <thead>
                    <tr class="bg-gray-50">
                        <th class="px-4 py-2 font-medium text-gray-600">Date</th>
                        <th class="px-4 py-2 font-medium text-gray-600">Donor User</th>
                        <th class="px-4 py-2 font-medium text-gray-600">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {% for fund in source.funds %}
                    <tr class="border-t border-gray-100">
                        <td class="px-4 py-2 text-gray-600">{{ fund.date.strftime('%Y-%m-%d %H:%M') }}</td>
                        <td class="px-4 py-2 text-gray-600">{{ fund.donor.name }}</td>
                        <td class="px-4 py-2 font-medium text-green-600">${{ "%.2f"|format(fund.amount) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <p class="text-sm text-gray-500 italic">No funds received from this source.</p>
        {% endif %}
    </div>
    {% endfor %}
</div>
{% endblock %}""",

    'add_fund.html': """{% extends 'base.html' %}
{% block header_title %}Add New Fund (Inflow){% endblock %}
{% block content %}
<div class="max-w-2xl bg-white p-8 rounded-xl shadow-sm border border-gray-100">
    <form method="POST" action="{{ url_for('add_fund') }}" class="space-y-6">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Donor User</label>
            <select name="user_id" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
                <option value="">-- Select User --</option>
                {% for user in users %}
                <option value="{{ user.id }}">{{ user.name }} (@{{ user.username }})</option>
                {% endfor %}
            </select>
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Fund Source</label>
            <select name="source_id" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
                <option value="">-- Select Source --</option>
                {% for source in sources %}
                <option value="{{ source.id }}">{{ source.name }}</option>
                {% endfor %}
            </select>
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Amount ($)</label>
            <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span class="text-gray-500">$</span>
                </div>
                <input type="number" step="0.01" name="amount" required class="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
            </div>
        </div>
        <div class="flex justify-end pt-4">
            <button type="submit" class="bg-primary text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm">Record Fund</button>
        </div>
    </form>
</div>
{% endblock %}""",

    'manage_funds.html': """{% extends 'base.html' %}
{% block header_title %}Manage Funds{% endblock %}
{% block content %}
<div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-gray-50 border-b border-gray-200">
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Date</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Donor</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Source</th>
                    <th class="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Amount</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                {% for fund in funds %}
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4 text-sm text-gray-600">{{ fund.date.strftime('%Y-%m-%d %H:%M') }}</td>
                    <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ fund.donor.name }}</td>
                    <td class="px-6 py-4 text-sm text-gray-600">
                        <span class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">{{ fund.source.name }}</span>
                    </td>
                    <td class="px-6 py-4 text-sm font-bold text-green-600 text-right">${{ "%.2f"|format(fund.amount) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}""",

    'fund_report.html': """{% extends 'base.html' %}
{% block header_title %}Fund Report{% endblock %}
{% block content %}
<div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
    <h3 class="text-lg font-bold text-gray-800 mb-4">Overall Fund Summary</h3>
    {% set total = namespace(value=0) %}
    {% for fund in funds %}
        {% set total.value = total.value + fund.amount %}
    {% endfor %}
    
    <div class="p-6 bg-green-50 rounded-xl border border-green-100 inline-block mb-6">
        <p class="text-sm text-green-800 font-medium mb-1">Total Inflow Amount</p>
        <p class="text-3xl font-bold text-green-700">${{ "%.2f"|format(total.value) }}</p>
    </div>

    <p class="text-gray-600 text-sm">Detailed report can be exported from the ledger.</p>
</div>
{% endblock %}""",

    'fund_ledger.html': """{% extends 'base.html' %}
{% block header_title %}Fund Ledger (Master){% endblock %}
{% block content %}
<div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="p-4 bg-gray-50 border-b border-gray-100 flex justify-between items-center">
        <h3 class="font-medium text-gray-700">Master Record of All Inflows</h3>
        <button class="text-sm bg-white border border-gray-300 px-3 py-1.5 rounded text-gray-700 hover:bg-gray-50 flex items-center">
            <i data-lucide="download" class="w-4 h-4 mr-1"></i> Export
        </button>
    </div>
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-gray-50 border-b border-gray-200">
                    <th class="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Tx ID</th>
                    <th class="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Date</th>
                    <th class="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Donor</th>
                    <th class="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Source</th>
                    <th class="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Credit (+)</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                {% for fund in funds %}
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-3 text-sm text-gray-500">TX-{{ "%05d"|format(fund.id) }}</td>
                    <td class="px-6 py-3 text-sm text-gray-600">{{ fund.date.strftime('%Y-%m-%d %H:%M:%S') }}</td>
                    <td class="px-6 py-3 text-sm font-medium text-gray-900">{{ fund.donor.name }}</td>
                    <td class="px-6 py-3 text-sm text-gray-600">{{ fund.source.name }}</td>
                    <td class="px-6 py-3 text-sm font-bold text-green-600 text-right">${{ "%.2f"|format(fund.amount) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}""",

    'add_beneficiary.html': """{% extends 'base.html' %}
{% block header_title %}Add Beneficiary{% endblock %}
{% block content %}
<div class="max-w-2xl bg-white p-8 rounded-xl shadow-sm border border-gray-100">
    <form method="POST" action="{{ url_for('add_beneficiary') }}" class="space-y-6">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Beneficiary Name</label>
            <input type="text" name="name" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Contact Details & Address</label>
            <textarea name="details" rows="3" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none"></textarea>
        </div>
        <div class="flex justify-end pt-4">
            <button type="submit" class="bg-primary text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm">Register Beneficiary</button>
        </div>
    </form>
</div>
{% endblock %}""",

    'issue_assistance.html': """{% extends 'base.html' %}
{% block header_title %}Issue Assistance{% endblock %}
{% block content %}
<div class="max-w-2xl bg-white p-8 rounded-xl shadow-sm border border-gray-100">
    <form method="POST" action="{{ url_for('issue_assistance') }}" class="space-y-6">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Beneficiary</label>
            <select name="beneficiary_id" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
                <option value="">-- Select Beneficiary --</option>
                {% for b in beneficiaries %}
                <option value="{{ b.id }}">{{ b.name }}</option>
                {% endfor %}
            </select>
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Assistance Type</label>
            <select name="assistance_type" id="type-select" onchange="toggleInstallment()" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
                <option value="Loan">Interest-Free Loan</option>
                <option value="Grant">One-Time Grant</option>
            </select>
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Amount ($)</label>
            <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span class="text-gray-500">$</span>
                </div>
                <input type="number" step="0.01" name="amount" required class="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
            </div>
        </div>
        <div id="installments-div">
            <label class="block text-sm font-medium text-gray-700 mb-1">Number of Installments (For Loan)</label>
            <input type="number" name="installments_count" min="1" value="1" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
        </div>
        <div class="flex justify-end pt-4">
            <button type="submit" class="bg-primary text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm">Issue Assistance</button>
        </div>
    </form>
</div>
<script>
    function toggleInstallment() {
        const type = document.getElementById('type-select').value;
        const div = document.getElementById('installments-div');
        if (type === 'Grant') {
            div.style.display = 'none';
        } else {
            div.style.display = 'block';
        }
    }
</script>
{% endblock %}""",

    'collect_installment.html': """{% extends 'base.html' %}
{% block header_title %}Collect Installment{% endblock %}
{% block content %}
<div class="max-w-2xl bg-white p-8 rounded-xl shadow-sm border border-gray-100">
    <form method="POST" action="{{ url_for('collect_installment') }}" class="space-y-6">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Select Active Loan</label>
            <select name="record_id" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
                <option value="">-- Select Loan Record --</option>
                {% for loan in active_loans %}
                <option value="{{ loan.id }}">{{ loan.beneficiary.name }} - Loan ${{ "%.2f"|format(loan.total_amount) }} (Paid: ${{ "%.2f"|format(loan.amount_paid) }})</option>
                {% endfor %}
            </select>
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Collection Amount ($)</label>
            <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span class="text-gray-500">$</span>
                </div>
                <input type="number" step="0.01" name="amount" required class="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none">
            </div>
        </div>
        <div class="flex justify-end pt-4">
            <button type="submit" class="bg-primary text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm">Record Payment</button>
        </div>
    </form>
</div>
{% endblock %}""",

    'assistance_report.html': """{% extends 'base.html' %}
{% block header_title %}Assistance & Loan Report{% endblock %}
{% block content %}
<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <p class="text-sm font-medium text-gray-500">Total Grants Issued</p>
        <h3 class="text-2xl font-bold text-purple-600 mt-2">${{ "%.2f"|format(total_grants) }}</h3>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <p class="text-sm font-medium text-gray-500">Total Loans Issued</p>
        <h3 class="text-2xl font-bold text-blue-600 mt-2">${{ "%.2f"|format(total_loans) }}</h3>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <p class="text-sm font-medium text-gray-500">Loans Recovered</p>
        <h3 class="text-2xl font-bold text-green-600 mt-2">${{ "%.2f"|format(total_recovered) }}</h3>
    </div>
</div>

<div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="p-4 border-b border-gray-100 bg-gray-50">
        <h3 class="font-medium text-gray-700">All Assistance Records</h3>
    </div>
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-gray-50 border-b border-gray-200">
                    <th class="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Date</th>
                    <th class="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Beneficiary</th>
                    <th class="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Type</th>
                    <th class="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Amount</th>
                    <th class="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Paid</th>
                    <th class="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                {% for r in records %}
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4 text-sm text-gray-600">{{ r.date.strftime('%Y-%m-%d') }}</td>
                    <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ r.beneficiary.name }}</td>
                    <td class="px-6 py-4 text-sm">
                        {% if r.assistance_type == 'Loan' %}
                        <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">Loan</span>
                        {% else %}
                        <span class="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">Grant</span>
                        {% endif %}
                    </td>
                    <td class="px-6 py-4 text-sm font-bold text-gray-700">${{ "%.2f"|format(r.total_amount) }}</td>
                    <td class="px-6 py-4 text-sm text-green-600 font-medium">
                        {% if r.assistance_type == 'Loan' %}
                        ${{ "%.2f"|format(r.amount_paid) }}
                        {% else %}
                        -
                        {% endif %}
                    </td>
                    <td class="px-6 py-4 text-sm">
                        {% if r.status == 'Active' %}
                        <span class="px-2.5 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-medium">Active</span>
                        {% elif r.status == 'Completed' %}
                        <span class="px-2.5 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">Completed</span>
                        {% else %}
                        <span class="px-2.5 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">Granted</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}"""
}

for filename, content in files.items():
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'w') as f:
        f.write(content)

print("All templates generated successfully.")
