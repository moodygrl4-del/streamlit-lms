import sqlite3

# Hubungkan ke database di folder "data"
conn = sqlite3.connect("data/lms.db")
c = conn.cursor()

# Tabel user
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    role TEXT,
    email TEXT
)
""")

# Tabel kegiatan / kalender
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

# Tabel progres belajar
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

print("✅ Database LMS berhasil dibuat.")
