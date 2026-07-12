import sqlite3

conn = sqlite3.connect('instance/foundation.db')
c = conn.cursor()

try:
    c.execute("ALTER TABLE fund_sources ADD COLUMN balance FLOAT DEFAULT 0.0;")
    c.execute("ALTER TABLE fund_sources ADD COLUMN opening_balance FLOAT DEFAULT 0.0;")
except Exception as e:
    print(e)

try:
    c.execute("ALTER TABLE members ADD COLUMN fund_source_id INTEGER REFERENCES fund_sources(id);")
except Exception as e:
    print(e)

try:
    c.execute("ALTER TABLE member_contribution_payments ADD COLUMN fund_source_id INTEGER REFERENCES fund_sources(id);")
except Exception as e:
    print(e)

c.execute("""
CREATE TABLE IF NOT EXISTS fund_source_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_source_id INTEGER NOT NULL REFERENCES fund_sources(id),
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    transaction_type VARCHAR(50),
    reference_number VARCHAR(50),
    member_id INTEGER REFERENCES members(id),
    description VARCHAR(255),
    debit FLOAT DEFAULT 0.0,
    credit FLOAT DEFAULT 0.0,
    balance FLOAT DEFAULT 0.0,
    remarks TEXT
);
""")

conn.commit()
conn.close()
print("Migration completed.")
