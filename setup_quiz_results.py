import sqlite3

conn = sqlite3.connect("data/lms.db")
c = conn.cursor()

# Buat tabel hasil kuis
c.execute("""
CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    score INTEGER,
    total INTEGER,
    date TEXT
)
""")

conn.commit()
conn.close()

print("✅ Tabel hasil kuis berhasil dibuat.")
