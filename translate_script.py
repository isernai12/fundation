import os
import glob
import re

replacements = {
    "Dashboard": "ড্যাশবোর্ড",
    "Organization Members": "সদস্য ব্যবস্থাপনা",
    "Add Member": "নতুন সদস্য যোগ করুন",
    "Manage Members": "সদস্য তালিকা",
    "Member Profile": "সদস্যের প্রোফাইল",
    "Edit Member": "সদস্যের তথ্য সম্পাদনা",
    "Delete Member": "সদস্য মুছে ফেলুন",
    "Save": "সংরক্ষণ করুন",
    "Cancel": "বাতিল",
    "Search": "অনুসন্ধান",
    "Filter": "ফিল্টার",
    "Phone Number": "মোবাইল নম্বর",
    "Mobile Number": "মোবাইল নম্বর",
    "WhatsApp Number": "হোয়াটসঅ্যাপ নম্বর",
    "Email Address": "ইমেইল ঠিকানা",
    "Present Address": "বর্তমান ঠিকানা",
    "Permanent Address": "স্থায়ী ঠিকানা",
    "Date of Birth": "জন্ম তারিখ",
    "Blood Group": "রক্তের গ্রুপ",
    "Profession": "পেশা",
    "Emergency Contact": "জরুরি যোগাযোগ",
    "Foundation Information": "ফাউন্ডেশন সম্পর্কিত তথ্য",
    "Purpose of Joining": "সদস্য হওয়ার উদ্দেশ্য",
    "Collect Contribution": "অনুদান সংগ্রহ",
    "Contribution History": "অনুদানের ইতিহাস",
    "Contribution Ledger": "অনুদান লেজার",
    "Contribution Report": "অনুদান রিপোর্ট",
    "Contributions": "অনুদান",
    "Fund Sources": "তহবিলের উৎস",
    "Fund Management": "তহবিল ব্যবস্থাপনা",
    "Assistance": "সহায়তা",
    "Loans": "ঋণ",
    "Loan": "ঋণ",
    "Print Profile": "প্রোফাইল প্রিন্ট",
    "Print": "প্রিন্ট",
    "Download PDF": "PDF ডাউনলোড",
    "Financial Summary": "আর্থিক সারসংক্ষেপ",
    "Activity Timeline": "কার্যক্রমের সময়রেখা",
    "Active": "সক্রিয়",
    "Inactive": "নিষ্ক্রিয়",
    "Joined Date": "যোগদানের তারিখ",
    "Join Date": "যোগদানের তারিখ",
    "Joined": "যোগদান করেছেন",
    "Status": "অবস্থা",
    "Full Name": "পূর্ণ নাম",
    "Father's Name": "পিতার নাম",
    "Mother's Name": "মাতার নাম",
    "Marital Status": "বৈবাহিক অবস্থা",
    "Single": "অবিবাহিত",
    "Married": "বিবাহিত",
    "Highest Education": "সর্বোচ্চ শিক্ষা",
    "Organization / Workplace": "প্রতিষ্ঠান / কর্মস্থল",
    "Special Skills": "বিশেষ দক্ষতা",
    "National ID": "জাতীয় পরিচয়পত্র",
    "NID Front": "জাতীয় পরিচয়পত্রের সামনের অংশ",
    "NID Back": "জাতীয় পরিচয়পত্রের পেছনের অংশ",
    "Signature Image": "স্বাক্ষরের ছবি",
    "Signature": "স্বাক্ষর",
    "Profile Photo": "প্রোফাইল ছবি",
    "Upload New Photo": "নতুন ছবি আপলোড করুন",
    "Delete Current Photo": "বর্তমান ছবি মুছে ফেলুন",
    "View Image": "ছবি দেখুন",
    "Change Photo": "ছবি পরিবর্তন করুন",
    "Next": "পরবর্তী",
    "Previous": "পূর্ববর্তী",
    "Submit Member": "সদস্য সংরক্ষণ করুন",
    "Update Member": "সদস্য আপডেট করুন",
    "Personal Information": "ব্যক্তিগত তথ্য",
    "Contact Information": "যোগাযোগের তথ্য",
    "Education & Profession": "শিক্ষা ও পেশা",
    "Uploaded Documents": "আপলোডকৃত নথিপত্র",
    "History Records:": "ইতিহাস রেকর্ড:",
    "Total Contributions": "মোট অনুদান",
    "Pending Dues": "বকেয়া",
    "Select Blood Group": "রক্তের গ্রুপ নির্বাচন করুন",
    "Select Marital Status": "বৈবাহিক অবস্থা নির্বাচন করুন",
    "Select Education": "শিক্ষা নির্বাচন করুন",
    "Select Profession": "পেশা নির্বাচন করুন",
    "Service": "চাকরি",
    "Business": "ব্যবসা",
    "Teacher": "শিক্ষক",
    "Student": "শিক্ষার্থী",
    "Freelancer": "ফ্রিল্যান্সার",
    "Farmer": "কৃষক",
    "Doctor": "ডাক্তার",
    "Engineer": "প্রকৌশলী",
    "Lawyer": "আইনজীবী",
    "Housewife": "গৃহিণী",
    "Other": "অন্যান্য",
    "Name": "নাম",
    "Relationship": "সম্পর্ক",
    "Source of Information": "তথ্যসূত্র",
    "Interested Activities": "আগ্রহী কার্যক্রম",
    "Delete File": "নথি মুছে ফেলুন",
    "No File": "কোনো নথি নেই",
    "No Photo": "কোনো ছবি নেই",
    "No Image": "কোনো ছবি নেই",
    "No Signature": "কোনো স্বাক্ষর নেই",
    "No activities found.": "কোনো কার্যক্রম পাওয়া যায়নি।",
    "Log Out": "লগ আউট",
    "Logout": "লগ আউট",
    "Sign Out": "সাইন আউট",
    "Settings": "সেটিংস",
    "Profile": "প্রোফাইল",
    "Total Members": "মোট সদস্য",
    "Total Funds": "মোট তহবিল",
    "Recent Members": "সাম্প্রতিক সদস্য",
    "View All": "সবগুলো দেখুন",
    "Quick Links": "গুরুত্বপূর্ণ লিংক",
    "Welcome": "স্বাগতম",
    "Optional": "ঐচ্ছিক",
    "Required": "প্রয়োজনীয়",
    "Actions": "পদক্ষেপ",
    "View": "দেখুন",
    "Edit": "সম্পাদনা",
    "Delete": "মুছে ফেলুন",
    "Are you sure you want to delete this member?": "আপনি কি নিশ্চিত যে আপনি এই সদস্যকে মুছে ফেলতে চান?",
    "Confirm Delete": "মুছে ফেলা নিশ্চিত করুন",
    "Search Members...": "সদস্য অনুসন্ধান করুন...",
    "All Professions": "সব পেশা",
    "Member ID": "সদস্য আইডি",
    "Clear Filters": "ফিল্টার মুছুন",
    "Clear": "পরিষ্কার",
    "Member Info": "সদস্যের তথ্য",
    "Contact": "যোগাযোগ",
    "Activities": "কার্যক্রম",
    "Amount": "পরিমাণ",
    "Member Created": "সদস্য তৈরি হয়েছে",
    "Contribution Collected": "অনুদান সংগ্রহ হয়েছে",
    "System": "সিস্টেম",
    "Users": "ব্যবহারকারী",
    "System Users": "সিস্টেম ব্যবহারকারী"
}

sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)

def translate_text(match):
    text = match.group(1)
    for eng, ben in sorted_replacements:
        text = text.replace(eng, ben)
    return '>' + text + '<'

def translate_attr(attr):
    def repl(match):
        text = match.group(1)
        for eng, ben in sorted_replacements:
            text = text.replace(eng, ben)
        return f'{attr}="' + text + '"'
    return repl

for filepath in glob.glob('/workspaces/fundation/templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = re.sub(r'>([^<]+)<', translate_text, content)
    for attr in ["placeholder", "value", "title", "label"]:
        content = re.sub(rf'{attr}="([^"]+)"', translate_attr(attr), content)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Update app.py
app_py = '/workspaces/fundation/app.py'
with open(app_py, 'r', encoding='utf-8') as f:
    app_content = f.read()

app_replacements = {
    "Member not found": "সদস্য খুঁজে পাওয়া যায়নি",
    "Member added successfully.": "সদস্য সফলভাবে যোগ করা হয়েছে।",
    "Member updated successfully.": "সদস্যের তথ্য সফলভাবে আপডেট করা হয়েছে।",
    "Member deleted successfully.": "সদস্য সফলভাবে মুছে ফেলা হয়েছে।",
    "Invalid member data": "অকার্যকর সদস্য তথ্য",
    "Member Created": "সদস্য তৈরি হয়েছে",
    "Contribution Collected": "অনুদান সংগ্রহ হয়েছে",
    "Joined as": "পেশায় যুক্ত হয়েছেন"
}

for eng, ben in app_replacements.items():
    app_content = app_content.replace(f"'{eng}'", f"'{ben}'")
    app_content = app_content.replace(f'"{eng}"', f'"{ben}"')
    
app_content = app_content.replace("f'Joined as {member.profession}'", "f'{member.profession} পেশায় যুক্ত হয়েছেন'")

with open(app_py, 'w', encoding='utf-8') as f:
    f.write(app_content)
