import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta

# === DATABASE CONNECTION ===
DB_PATH = "data/users.db"

def get_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    data = c.fetchone()
    conn.close()
    return data

def add_task(username, tugas, file_path, deadline):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO tasks (username, tugas, file_path, deadline) VALUES (?, ?, ?, ?)", 
              (username, tugas, file_path, deadline))
    conn.commit()
    conn.close()

# === PAGE CONFIG ===
st.set_page_config(page_title="🎓 LMS Streamlit", layout="wide")
st.title("🎓 Learning Management System (Streamlit)")
st.caption("By Kamu 🚀")

# === LOGIN FORM ===
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = get_user(username, password)
    if user:
        st.success(f"Selamat datang, {username}!")
        role = user[2]

        # ============ ADMIN DASHBOARD ============
        if role == "admin":
            st.header("📚 Dashboard Guru/Admin")

            tab1, tab2, tab3 = st.tabs(["Upload Materi", "Kelola Tugas", "Lihat Pengumpulan"])

            with tab1:
                st.subheader("📘 Upload Materi")
                materi = st.text_input("Judul Materi")
                file = st.file_uploader("Upload File (PDF/DOCX/VIDEO)")
                if st.button("Upload Materi"):
                    if file and materi:
                        os.makedirs("data/materials", exist_ok=True)
                        with open(f"data/materials/{file.name}", "wb") as f:
                            f.write(file.getbuffer())
                        st.success(f"Materi '{materi}' berhasil diupload!")
                    else:
                        st.error("Lengkapi judul dan file materi.")

            with tab2:
                st.subheader("🧾 Buat Tugas")
                tugas = st.text_input("Nama Tugas")
                deadline = st.date_input("Deadline", datetime.now() + timedelta(days=7))
                file = st.file_uploader("File Pendukung (opsional)")
                if st.button("Publikasikan Tugas"):
                    add_task("admin", tugas, file.name if file else "", str(deadline))
                    st.success(f"Tugas '{tugas}' berhasil dibuat. Deadline: {deadline}")

            with tab3:
                st.subheader("📤 Pengumpulan Tugas Siswa")
                conn = sqlite3.connect(DB_PATH)
                df = pd.read_sql_query("SELECT * FROM tasks WHERE username != 'admin'", conn)
                st.dataframe(df)
                conn.close()

        # ============ STUDENT DASHBOARD ============
        elif role == "student":
            st.header("🎒 Dashboard Siswa")

            tab1, tab2, tab3 = st.tabs(["Materi", "Tugas", "Progress"])

            with tab1:
                st.subheader("📖 Materi yang Tersedia")
                files = os.listdir("data/materials") if os.path.exists("data/materials") else []
                if files:
                    for f in files:
                        st.download_button("📥 Unduh " + f, open(f"data/materials/" + f, "rb"), f)
                else:
                    st.info("Belum ada materi.")

            with tab2:
                st.subheader("📌 Upload Tugas")
                tugas = st.text_input("Nama Tugas")
                file = st.file_uploader("Upload File (PDF/DOCX)")
                if st.button("Kirim Tugas"):
                    if file and tugas:
                        file_path = f"data/{username}_{file.name}"
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                        add_task(username, tugas, file_path, str(datetime.now()))
                        st.success("Tugas berhasil dikirim!")
                    else:
                        st.error("Lengkapi tugas dan file terlebih dahulu.")

            with tab3:
                st.subheader("📊 Progress Belajar")
                conn = sqlite3.connect(DB_PATH)
                df = pd.read_sql_query(f"SELECT * FROM tasks WHERE username='{username}'", conn)
                conn.close()
                if len(df) > 0:
                    st.dataframe(df)
                    st.progress(min(len(df) / 5, 1.0))
                else:
                    st.info("Belum ada progress untuk ditampilkan.")
    else:
        st.error("Username atau password salah.")
import streamlit as st
import sqlite3
import pandas as pd

# ------------------------------
# Fungsi database
# ------------------------------
def get_connection():
    return sqlite3.connect("data/lms.db")

def add_event(title, description, date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO events (title, description, date) VALUES (?, ?, ?)", (title, description, date))
    conn.commit()
    conn.close()

def get_all_events():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM events ORDER BY date ASC", conn)
    conn.close()
    return df

# ------------------------------
# Halaman kalender
# ------------------------------
def kalender_page():
    st.title("📅 Kalender Kegiatan")

    st.subheader("Tambah Kegiatan Baru")
    with st.form("add_event_form"):
        title = st.text_input("Judul Kegiatan")
        description = st.text_area("Deskripsi")
        date = st.date_input("Tanggal Kegiatan")
        submitted = st.form_submit_button("Tambah")

        if submitted:
            add_event(title, description, str(date))
            st.success(f"Kegiatan '{title}' berhasil ditambahkan!")

    st.divider()

    st.subheader("Daftar Semua Kegiatan")
    events = get_all_events()
    if not events.empty:
        st.dataframe(events, use_container_width=True)
    else:
        st.info("Belum ada kegiatan yang tercatat.")

# ------------------------------
# Navigasi sederhana
# ------------------------------
menu = st.sidebar.radio(
    "Navigasi",
    ["Beranda", "Kalender"]
)

if menu == "Beranda":
    st.title("🎓 Learning Management System")
    st.write("Selamat datang di LMS berbasis Streamlit!")
elif menu == "Kalender":
    kalender_page()
import sqlite3
import streamlit as st

# Fungsi ambil data kuis
def get_quizzes():
    conn = sqlite3.connect("data/lms.db")
    c = conn.cursor()
    c.execute("SELECT * FROM quizzes")
    data = c.fetchall()
    conn.close()
    return data

# Di bagian menu navigasi:
menu = ["Dashboard", "Kalender", "Kuis"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Kuis":
    st.header("🧠 Kuis Interaktif")

    quizzes = get_quizzes()
    score = 0

    if quizzes:
        for q in quizzes:
            st.subheader(q[1])
            answer = st.radio("Pilih jawaban:", [q[2], q[3], q[4]], key=q[0])
            if st.button(f"Periksa Jawaban {q[0]}"):
                if answer == q[5]:
                    st.success("Benar ✅")
                    score += 1
                else:
                    st.error(f"Salah ❌ Jawaban benar: {q[5]}")

        st.info(f"Skor akhir kamu: {score}/{len(quizzes)}")
    else:
        st.warning("Belum ada kuis tersedia.")
