# In scripts/setup_db.py
PATTERNS_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS patterns (
    pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
    features BLOB NOT NULL,
    profitability REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""
