import sqlite3

conn = sqlite3.connect('instance/foundation.db')
c = conn.cursor()

# Create member_ledger table
c.execute("DROP TABLE IF EXISTS member_contribution_ledger;")
c.execute("""
CREATE TABLE IF NOT EXISTS member_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    transaction_type VARCHAR(50),
    description VARCHAR(255),
    debit FLOAT DEFAULT 0.0,
    credit FLOAT DEFAULT 0.0,
    balance FLOAT DEFAULT 0.0,
    reference_number VARCHAR(50),
    remarks TEXT,
    FOREIGN KEY(member_id) REFERENCES members(id)
);
""")

# Convert Loans and Assistance to use member_id instead of beneficiary_id
try:
    c.execute("ALTER TABLE loans ADD COLUMN member_id INTEGER REFERENCES members(id);")
except:
    pass

try:
    c.execute("ALTER TABLE assistance_requests ADD COLUMN member_id INTEGER REFERENCES members(id);")
except:
    pass

conn.commit()
conn.close()
print("Migration done.")
