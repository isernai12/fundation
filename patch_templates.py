import re

# 1. Update add_member.html
with open('/workspaces/fundation/templates/add_member.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_field = """<div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">ডিফল্ট তহবিল (Default Fund Source) <span class="text-red-500">*</span></label>
                    <select name="fund_source_id" required class="w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary no-bn">
                        <option value="">তহবিল নির্বাচন করুন</option>
                        {% for fs in fund_sources %}
                        <option value="{{ fs.id }}">{{ fs.name }}</option>
                        {% endfor %}
                    </select>
                </div>
"""
if "name=\"fund_source_id\"" not in content:
    content = content.replace('<div class="grid grid-cols-1 gap-6">', '<div class="grid grid-cols-1 gap-6">\n                ' + new_field, 1)

with open('/workspaces/fundation/templates/add_member.html', 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Update edit_member.html
with open('/workspaces/fundation/templates/edit_member.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_field_edit = """<div class="col-span-1 md:col-span-2">
                    <label class="block text-sm font-medium text-gray-700 mb-1">ডিফল্ট তহবিল (Default Fund Source) <span class="text-red-500">*</span></label>
                    <select name="fund_source_id" required class="w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary no-bn">
                        <option value="">তহবিল নির্বাচন করুন</option>
                        {% for fs in fund_sources %}
                        <option value="{{ fs.id }}" {% if member.fund_source_id == fs.id %}selected{% endif %}>{{ fs.name }}</option>
                        {% endfor %}
                    </select>
                </div>
"""
if "name=\"fund_source_id\"" not in content:
    content = content.replace('<div class="grid grid-cols-1 md:grid-cols-2 gap-6">', '<div class="grid grid-cols-1 md:grid-cols-2 gap-6">\n                ' + new_field_edit, 1)

with open('/workspaces/fundation/templates/edit_member.html', 'w', encoding='utf-8') as f:
    f.write(content)

# 3. Update contribution_collect.html
with open('/workspaces/fundation/templates/contribution_collect.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_field_collect = """<div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">তহবিল (Fund Source) <span class="text-red-500">*</span></label>
                                <select name="fund_source_id" required class="w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary no-bn">
                                    {% for fs in fund_sources %}
                                    <option value="{{ fs.id }}" {% if d.member.fund_source_id == fs.id %}selected{% endif %}>{{ fs.name }}</option>
                                    {% endfor %}
                                </select>
                            </div>
"""
# Find where payment method is and insert before it
if "name=\"fund_source_id\"" not in content:
    content = content.replace('<div>\n                                <label class="block text-sm font-medium text-gray-700 mb-1">প্রদানের মাধ্যম', new_field_collect + '                            <div>\n                                <label class="block text-sm font-medium text-gray-700 mb-1">প্রদানের মাধ্যম')

with open('/workspaces/fundation/templates/contribution_collect.html', 'w', encoding='utf-8') as f:
    f.write(content)

# 4. Update member_profile.html to show Default Fund Source
with open('/workspaces/fundation/templates/member_profile.html', 'r', encoding='utf-8') as f:
    content = f.read()

profile_fund_source = """<div class="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                <div>
                    <span class="block text-xs text-gray-500">ডিফল্ট তহবিল</span>
                    <span class="font-medium text-gray-800">{{ member.fund_source.name if member.fund_source else 'নির্ধারিত নয়' }}</span>
                </div>
            </div>"""

if "ডিফল্ট তহবিল" not in content:
    content = content.replace('<!-- Right Side -->', profile_fund_source + '\n\n            <!-- Right Side -->')

with open('/workspaces/fundation/templates/member_profile.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Templates patched.")
