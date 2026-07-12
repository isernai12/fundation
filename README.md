# CivicFund OS

A secure, modern, light-mode Foundation & Organization Management System built with Python (Flask, SQLite, SQLAlchemy) and styled with Tailwind CSS.

## Project Structure
```text
/workspaces/fundation/
├── app.py                  # Main Flask application and session-based route controls
├── models.py               # SQLAlchemy SQLite schemas (Users, Members, Ledgers, Funds)
├── foundation.db           # Auto-created SQLite database (created on first run)
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Core layout containing responsive Sidebar & Lucide icons
│   ├── login.html          # Clean light-mode login screen
│   ├── dashboard.html      # Stats summary counters and recent operational listings
│   ├── members.html        # Member Directory view
│   ├── members_add.html    # Add Member registration form
│   ├── members_manage.html # Edit and Delete operations for members
│   ├── member_ledger.html  # Activity logs and membership fee/payment ledgers
│   ├── funds_add.html      # Donation/Grants entry page
│   ├── funds_manage.html   # Update category/donor details or delete donation entries
│   ├── fund_report.html    # allocation analytics and category distributions
│   └── fund_ledger.html    # General organization inflows/outflows cash ledger
└── README.md               # Setup and project usage documentation
```

## Running the Application
To run the server locally, perform the following command:
```bash
python3 app.py
```
Open [http://localhost:5000](http://localhost:5000) in your web browser.

### Credentials
- **Username**: `admin`
- **Password**: `admin123`
*Note: Seed data is automatically injected if the database doesn't exist.*