import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta

# ==========================================
# FUNGSI DATABASE
# ==========================================
def get_user(username, password):
    conn = sqlite3.connect("data/users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    data = c.fetchone()
    conn.close()
    return data

def add_task(username, tugas, file_path, deadline):
    conn = sqlite3.connect("data/users.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (username, tugas, file_path, deadline) VALUES (?, ?, ?, ?)",
        (username, tugas, file_path, deadline)
    )
    conn.commit()
    conn.close()

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

def get_quizzes():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM quizzes")
    data = c.fetchall()
    conn.close()
    return data


# ==========================================
# KONFIGURASI STREAMLIT
# ==========================================
st.set_page_config(page_title="🎓 LMS Streamlit", layout="wide")
st.title("🎓 Learning Management System")
st.caption("By Kamu 🚀")

# ==========================================
# LOGIN FORM
# ==========================================
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = get_user(username, password)
    if user:
        st.success(f"Selamat datang, {username}!")
        role = user[2]

        # Sidebar Navigasi
        menu = ["Dashboard", "Kalender", "Kuis", "Riwayat Kuis", "Leaderboard"]
        choice = st.sidebar.selectbox("📂 Menu Navigasi", menu)

        # =====================================================
        # DASHBOARD
        # =====================================================
        if choice == "Dashboard":
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
                    if st.button("Publikasikan Tugas"):
                        add_task("admin", tugas, "", str(deadline))
                        st.success(f"Tugas '{tugas}' berhasil dibuat! Deadline: {deadline}")

                with tab3:
                    st.subheader("📤 Pengumpulan Tugas Siswa")
                    conn = sqlite3.connect("data/users.db")
                    df = pd.read_sql_query("SELECT * FROM tasks WHERE username != 'admin'", conn)
                    conn.close()
                    if not df.empty:
                        st.dataframe(df)
                    else:
                        st.info("Belum ada tugas yang dikumpulkan siswa.")

            elif role == "student":
                st.header("🎒 Dashboard Siswa")
                tab1, tab2, tab3 = st.tabs(["Materi", "Upload Tugas", "Progress"])

                with tab1:
                    st.subheader("📖 Materi Tersedia")
                    files = os.listdir("data/materials") if os.path.exists("data/materials") else []
                    if files:
                        for f in files:
                            st.download_button("📥 Unduh " + f, open(f"data/materials/" + f, "rb"), f)
                    else:
                        st.info("Belum ada materi diunggah.")

                with tab2:
                    st.subheader("📌 Upload Tugas")
                    tugas = st.text_input("Nama Tugas")
                    file = st.file_uploader("Upload File (PDF/DOCX)")
                    if st.button("Kirim Tugas"):
                        if file and tugas:
                            os.makedirs("data", exist_ok=True)
                            file_path = f"data/{username}_{file.name}"
                            with open(file_path, "wb") as f:
                                f.write(file.getbuffer())
                            add_task(username, tugas, file_path, str(datetime.now()))
                            st.success("Tugas berhasil dikirim!")
                        else:
                            st.error("Lengkapi tugas dan file.")

                with tab3:
                    st.subheader("📊 Progress Belajar")
                    conn = sqlite3.connect("data/users.db")
                    df = pd.read_sql_query(f"SELECT * FROM tasks WHERE username='{username}'", conn)
                    conn.close()
                    if len(df) > 0:
                        st.dataframe(df)
                        st.progress(min(len(df) / 5, 1.0))
                    else:
                        st.info("Belum ada progress untuk ditampilkan.")

        # =====================================================
        # KALENDER
        # =====================================================
        elif choice == "Kalender":
            st.header("📅 Kalender Kegiatan")
            with st.form("add_event_form"):
                title = st.text_input("Judul Kegiatan")
                description = st.text_area("Deskripsi")
                date = st.date_input("Tanggal Kegiatan")
                submitted = st.form_submit_button("Tambah")
                if submitted:
                    add_event(title, description, str(date))
                    st.success(f"Kegiatan '{title}' berhasil ditambahkan!")
            st.divider()
            events = get_all_events()
            if not events.empty:
                st.dataframe(events, use_container_width=True)
            else:
                st.info("Belum ada kegiatan yang tercatat.")

        # =====================================================
        # KUIS
        # =====================================================
        elif choice == "Kuis":
            st.header("🧠 Kuis Interaktif")
            student_name = st.text_input("Masukkan nama kamu:")
            if student_name:
                quizzes = get_quizzes()
                score = 0
                if quizzes:
                    st.info("Jawab semua pertanyaan di bawah:")
                    answers = {}
                    for q in quizzes:
                        st.subheader(q[1])
                        answer = st.radio("Pilih jawaban:", [q[2], q[3], q[4]], key=q[0])
                        answers[q[0]] = answer

                    if st.button("Kirim Jawaban"):
                        for q in quizzes:
                            if answers[q[0]] == q[5]:
                                score += 1

                        st.success(f"Skor kamu: {score}/{len(quizzes)}")

                        # Simpan hasil kuis
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute("""
                            INSERT INTO quiz_results (student_name, score, total, date)
                            VALUES (?, ?, ?, ?)
                        """, (student_name, score, len(quizzes),
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        conn.close()
                        st.info("✅ Hasil kamu telah disimpan!")
                else:
                    st.warning("Belum ada kuis tersedia.")
            else:
                st.warning("Masukkan nama dulu sebelum mulai kuis!")

        # =====================================================
        # RIWAYAT KUIS
        # =====================================================
        elif choice == "Riwayat Kuis":
            st.header("📜 Riwayat Kuis")
            student_name = st.text_input("Masukkan nama kamu:")
            if student_name:
                conn = get_connection()
                c = conn.cursor()
                c.execute("SELECT date, score, total FROM quiz_results WHERE student_name = ?", (student_name,))
                rows = c.fetchall()
                conn.close()
                if rows:
                    for r in rows:
                        st.write(f"🕓 {r[0]} — Skor: {r[1]}/{r[2]}")
                else:
                    st.warning("Belum ada hasil kuis kamu.")
            else:
                st.info("Masukkan nama kamu untuk melihat riwayat.")

        # =====================================================
        # LEADERBOARD
        # =====================================================
        elif choice == "Leaderboard":
            st.header("🏆 Leaderboard")
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT student_name, AVG(score*1.0/total)*100 AS avg_score
                FROM quiz_results
                GROUP BY student_name
                ORDER BY avg_score DESC LIMIT 10
            """)
            rows = c.fetchall()
            conn.close()
            if rows:
                for i, r in enumerate(rows, start=1):
                    st.write(f"**{i}. {r[0]}** — Rata-rata: {r[1]:.2f}%")
            else:
                st.warning("Belum ada data leaderboard.")

    else:
        st.error("Username atau password salah.")

