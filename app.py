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
