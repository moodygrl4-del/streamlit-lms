import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta

# ==========================================
# FUNGSI DATABASE
# ==========================================
def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect("data/lms.db")

def get_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    data = c.fetchone()
    conn.close()
    return data

def add_task(username, tugas, file_path, deadline):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            tugas TEXT,
            file_path TEXT,
            deadline TEXT
        )
    """)
    conn.commit()
    c.execute(
        "INSERT INTO tasks (username, tugas, file_path, deadline) VALUES (?, ?, ?, ?)",
        (username, tugas, file_path, deadline)
    )
    conn.commit()
    conn.close()

def add_event(title, description, date):
    conn = get_connection()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, date TEXT)")
    conn.commit()
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
    c.execute("CREATE TABLE IF NOT EXISTS quizzes (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, opt1 TEXT, opt2 TEXT, opt3 TEXT, answer TEXT)")
    conn.commit()
    c.execute("SELECT * FROM quizzes")
    data = c.fetchall()
    conn.close()
    return data

def get_unread_notifications(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            task_id INTEGER,
            read_status INTEGER DEFAULT 0
        )
    """)
    conn.commit()

    # Ambil tugas baru dari admin yang belum dibaca oleh siswa
    c.execute("""
        SELECT t.id, t.tugas, t.deadline 
        FROM tasks t
        LEFT JOIN notifications n ON t.id = n.task_id AND n.username = ?
        WHERE t.username='admin' AND (n.read_status IS NULL OR n.read_status = 0)
        ORDER BY t.id DESC
    """, (username,))
    rows = c.fetchall()
    conn.close()
    return rows

def mark_notifications_as_read(username):
    conn = get_connection()
    c = conn.cursor()
    # Tandai semua tugas admin sebagai sudah dibaca
    c.execute("""
        INSERT INTO notifications (username, task_id, read_status)
        SELECT ?, id, 1 FROM tasks WHERE username='admin'
        AND id NOT IN (SELECT task_id FROM notifications WHERE username=?)
    """, (username, username))
    c.execute("UPDATE notifications SET read_status=1 WHERE username=?", (username,))
    conn.commit()
    conn.close()

# ==========================================
# STREAMLIT SETUP
# ==========================================
st.set_page_config(page_title="🎓 LMS Streamlit", layout="wide")
st.title("🎓 Learning Management System")
st.caption("By Kamu 🚀")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = get_user(username, password)
    if user:
        st.success(f"Selamat datang, {username}!")
        role = user[2]

        menu = ["Dashboard", "Kalender", "Kuis", "Riwayat Kuis", "Leaderboard"]
        choice = st.sidebar.selectbox("📂 Menu Navigasi", menu)

        # =====================================================
        # DASHBOARD ADMIN / GURU
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
                    st.subheader("🧾 Buat Tugas Baru")
                    tugas = st.text_input("Nama Tugas")
                    deadline = st.date_input("Deadline", datetime.now() + timedelta(days=7))
                    if st.button("Publikasikan Tugas"):
                        add_task("admin", tugas, "", str(deadline))
                        st.success(f"Tugas '{tugas}' berhasil dibuat dan akan muncul di notifikasi siswa!")

                with tab3:
                    st.subheader("📤 Pengumpulan Tugas Siswa")
                    conn = get_connection()
                    df = pd.read_sql_query("SELECT * FROM tasks WHERE username != 'admin'", conn)
                    conn.close()
                    if not df.empty:
                        st.dataframe(df)
                    else:
                        st.info("Belum ada tugas siswa.")

            # =====================================================
            # DASHBOARD SISWA
            # =====================================================
            elif role == "student":
                st.header("🎒 Dashboard Siswa")

                # 🔔 Notifikasi tugas baru
                new_tasks = get_unread_notifications(username)
                if new_tasks:
                    st.info("📢 Ada tugas baru dari guru!")
                    for t in new_tasks[:3]:
                        st.write(f"🧾 **{t[1]}** — Deadline: {t[2]}")
                    if st.button("Tandai semua sudah dibaca"):
                        mark_notifications_as_read(username)
                        st.success("Semua notifikasi telah ditandai dibaca.")
                        st.rerun()

                tab1, tab2, tab3 = st.tabs(["Materi", "Upload Tugas", "Progress"])

                with tab1:
                    st.subheader("📖 Materi Tersedia")
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
                    conn = get_connection()
                    df = pd.read_sql_query(f"SELECT * FROM tasks WHERE username='{username}'", conn)
                    conn.close()
                    if len(df) > 0:
                        st.dataframe(df)
                        st.progress(min(len(df) / 5, 1.0))
                    else:
                        st.info("Belum ada progress.")

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

            events = get_all_events()
            if not events.empty:
                st.dataframe(events, use_container_width=True)
            else:
                st.info("Belum ada kegiatan.")

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
                    st.info("Jawab semua pertanyaan:")
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
                        conn = get_connection()
                        c = conn.cursor()
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
                        c.execute("""
                            INSERT INTO quiz_results (student_name, score, total, date)
                            VALUES (?, ?, ?, ?)
                        """, (student_name, score, len(quizzes),
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        conn.close()
                        st.info("✅ Hasil kamu telah disimpan!")
                else:
                    st.warning("Belum ada kuis.")
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
                st.info("Masukkan nama kamu.")

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



