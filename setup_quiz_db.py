import sqlite3

# Koneksi ke database
conn = sqlite3.connect("data/lms.db")
c = conn.cursor()

# Buat tabel kuis jika belum ada
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

# Contoh data kuis (hapus atau ubah nanti)
sample_quizzes = [
    ("Apa ibu kota Indonesia?", "Bandung", "Jakarta", "Surabaya", "Jakarta"),
    ("Hasil dari 5 + 3 adalah?", "6", "8", "10", "8"),
    ("Bahasa pemrograman untuk Streamlit?", "Python", "Java", "C++", "Python")
]

c.executemany("INSERT INTO quizzes (question, option_a, option_b, option_c, answer) VALUES (?, ?, ?, ?, ?)", sample_quizzes)
conn.commit()
conn.close()

print("✅ Tabel kuis berhasil dibuat dan data contoh ditambahkan.")
