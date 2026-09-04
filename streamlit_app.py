import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Deadline Reminder & Subject Archive",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS untuk Tampilan UI/UX Modern
st.markdown("""
    <style>
    /* Styling Header Main */
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    
    /* Custom Card Dashboard */
    .dashboard-card {
        background-color: #FFFFFF;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    /* Badges Status */
    .badge-urgent {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-normal {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-safe {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Archive Folder Box */
    .archive-box {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 1px solid #BFDBFE;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar Navigasi
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2693/2693507.png", width=60)
    st.title("Menu Utama")
    page = st.radio("Navigasi", ["Dashboard", "Pengingat Deadline", "Arsip Mata Kuliah", "Pengaturan"])
    
    st.divider()
    st.caption("Status Sistem: **Online**")
    st.caption("Proyek Terhubung ke GitHub")

# 4. Dummy Data
if 'deadlines' not in st.session_state:
    st.session_state.deadlines = [
        {"Tugas": "Laporan Praktikum AI", "Matkul": "Kecerdasan Buatan", "Deadline": date(2026, 9, 6), "Status": "Urgent"},
        {"Tugas": "Desain Wireframe UI/UX", "Matkul": "Interaksi Manusia & Komputer", "Deadline": date(2026, 9, 12), "Status": "Normal"},
        {"Tugas": "Paper Etika Profesi", "Matkul": "Etika TI", "Deadline": date(2026, 9, 20), "Status": "Safe"}
    ]

# 5. Tampilan Halaman
if page == "Dashboard" or page == "Pengingat Deadline":
    st.markdown('<div class="main-title">Deadline Reminder & Subject Archive</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Kelola tenggat waktu tugas dan simpan materi perkuliahan dalam satu tempat.</div>', unsafe_allow_html=True)
    
    # Ringkasan Metrik
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Tugas Active", value=len(st.session_state.deadlines))
    with col2:
        st.metric(label="Mendesak (<3 Hari)", value=1, delta_color="inverse")
    with col3:
        st.metric(label="Arsip Mata Kuliah", value=6)
    with col4:
        st.metric(label="Selesai Minggu Ini", value=4)

    st.divider()

    # Layout 2 Kolom: List Deadline & Form Input
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("📋 Daftar Deadline Terdekat")
        
        for item in st.session_state.deadlines:
            days_left = (item["Deadline"] - date.today()).days
            badge_class = "badge-safe"
            if days_left <= 3:
                badge_class = "badge-urgent"
            elif days_left <= 7:
                badge_class = "badge-normal"

            st.markdown(f"""
            <div class="dashboard-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0; color: #0F172A;">{item['Tugas']}</h4>
                    <span class="{badge_class}">{days_left} Hari Lagi</span>
                </div>
                <p style="margin: 4px 0 0 0; color: #64748B; font-size: 0.9rem;">
                    📚 <b>{item['Matkul']}</b> | Tenggat: {item['Deadline'].strftime('%d %B %Y')}
                </p>
            </div>
            """, unsafe_allow_html=True)

    with right_col:
        st.subheader("➕ Tambah Deadline Baru")
        with st.form("add_deadline_form"):
            task_name = st.text_input("Nama Tugas / Proyek")
            subject_name = st.selectbox("Mata Kuliah", ["Kecerdasan Buatan", "Interaksi Manusia & Komputer", "Etika TI", "Pemrograman Web"])
            due_date = st.date_input("Tenggat Waktu", min_value=date.today())
            
            submit = st.form_submit_button("Simpan Reminder", use_container_width=True)
            if submit and task_name:
                st.session_state.deadlines.append({
                    "Tugas": task_name,
                    "Matkul": subject_name,
                    "Deadline": due_date,
                    "Status": "Normal"
                })
                st.success("Deadline berhasil ditambahkan!")
                st.rerun()

elif page == "Arsip Mata Kuliah":
    st.markdown('<div class="main-title">📚 Subject Archive</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Penyimpanan terorganisir untuk modul, catatatan, dan pustaka berkas perkuliahan.</div>', unsafe_allow_html=True)

    search = st.text_input("🔍 Cari arsip modul atau materi...", placeholder="Ketik nama mata kuliah...")
    
    col_a, col_b = st.columns(2)
    
    subjects = [
        {"code": "IF301", "name": "Kecerdasan Buatan", "files": 12, "updated": "2 hari lalu"},
        {"code": "IF302", "name": "Interaksi Manusia & Komputer", "files": 8, "updated": "Kemarin"},
        {"code": "IF303", "name": "Pemrograman Web Lanjut", "files": 15, "updated": "5 hari lalu"},
        {"code": "IF304", "name": "Basis Data Terdistribusi", "files": 6, "updated": "1 minggu lalu"}
    ]

    for index, sub in enumerate(subjects):
        target_col = col_a if index % 2 == 0 else col_b
        with target_col:
            st.markdown(f"""
            <div class="archive-box">
                <span style="font-size: 0.8rem; font-weight: 700; color: #2563EB;">{sub['code']}</span>
                <h3 style="margin: 0.2rem 0; color: #1E293B;">{sub['name']}</h3>
                <p style="color: #64748B; font-size: 0.85rem; margin-bottom: 0.8rem;">
                    📂 {sub['files']} Berkas Tersimpan • Diperbarui {sub['updated']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.button(f"Buka Folder {sub['code']}", key=sub['code'])

elif page == "Pengaturan":
    st.markdown('<div class="main-title">⚙️ Pengaturan Aplikasi</div>', unsafe_allow_html=True)
    st.toggle("Aktifkan Notifikasi Email", value=True)
    st.toggle("Mode Gelap (Dark Mode Override)", value=False)
