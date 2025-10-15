import sqlite3
import os

os.makedirs("data", exist_ok=True)
conn = sqlite3.connect("data/lms.db")
c = conn.cursor()

# Tabel user
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

# Tabel kalender / kegiatan
c.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    date TEXT
)
""")

# Tabel kuis
c.execute("""
CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    answer TEXT
)
""")

# Tabel hasil kuis
c.execute("""
CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    score INTEGER,
    total INTEGER,
    date TEXT
)
""")

# Tabel tugas
c.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    tugas TEXT,
    file_path TEXT,
    deadline TEXT
)
""")

# Tabel progres
c.execute("""
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    course_name TEXT,
    progress INTEGER
)
""")

conn.commit()
conn.close()
print("✅ Database LMS final berhasil dibuat di 'data/lms.db'")
