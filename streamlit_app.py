import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. Konfigurasi Halaman Web
st.set_page_config(
    page_title="Deadline Reminder System",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS untuk UI/UX Modern (Berdasarkan Desain Pertama)
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .dashboard-card {
        background-color: #FFFFFF;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    .badge-urgent {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-normal {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-safe {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Inisialisasi Session State (Tempat Penyimpanan Data Input Pengguna)
if 'deadlines' not in st.session_state:
    # Contoh data awal (bisa diisi atau dikosongkan [])
    st.session_state.deadlines = [
        {"Tugas": "Laporan Praktikum AI", "Matkul": "Kecerdasan Buatan", "Deadline": date(2026, 9, 6)},
        {"Tugas": "Desain Wireframe UI/UX", "Matkul": "Interaksi Manusia & Komputer", "Deadline": date(2026, 9, 12)}
    ]

# 4. Sidebar Navigasi
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2693/2693507.png", width=60)
    st.title("Menu Utama")
    menu = st.radio("Pilih Halaman", ["Kelola Deadline", "Tabel Rekapitulasi"])
    st.divider()
    st.caption("Aplikasi Input & Pengingat Deadline")

# 5. Tampilan Utama

if menu == "Kelola Deadline":
    st.markdown('<div class="main-title">Deadline Reminder System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Masukkan tugas baru Anda dan pantau tenggat waktunya secara langsung.</div>', unsafe_allow_html=True)

    # Membagi Layar Menjadi 2 Kolom (Kiri: Form Input, Kanan: Daftar Tugas)
    col_input, col_display = st.columns([1, 1.4])

    # === A. FORM INPUT USER ===
    with col_input:
        st.subheader("➕ Tambah Tugas Baru")
        
        # Form input dengan parameter clear_on_submit=True agar form otomatis bersih setelah dikirim
        with st.form(key="form_input_deadline", clear_on_submit=True):
            
            # 1. Input Nama Tugas
            nama_tugas = st.text_input(
                "Nama Tugas / Proyek",
                placeholder="Contoh: Makalah Etika Profesi"
            )
            
            # 2. Input Nama Mata Kuliah
            nama_matkul = st.text_input(
                "Nama Mata Kuliah",
                placeholder="Contoh: Pemrograman Web"
            )
            
            # 3. Input Tanggal Deadline
            tanggal_deadline = st.date_input(
                "Tanggal Deadline",
                value=date.today(),
                min_value=date.today()
            )
            
            # Tombol Simpan
            submit_btn = st.form_submit_button(label="📌 Simpan Deadline", use_container_width=True)

            # Validasi dan Logika Penyimpanan Data
            if submit_btn:
                if not nama_tugas.strip():
                    st.error("⚠️ Nama Tugas wajib diisi!")
                elif not nama_matkul.strip():
                    st.error("⚠️ Nama Mata Kuliah wajib diisi!")
                else:
                    # Menambahkan data baru ke session state
                    st.session_state.deadlines.append({
                        "Tugas": nama_tugas,
                        "Matkul": nama_matkul,
                        "Deadline": tanggal_deadline
                    })
                    st.success(f"✅ Tugas '{nama_tugas}' berhasil disimpan!")
                    st.rerun()

    # === B. TAMPILAN CARD DEADLINE ===
    with col_display:
        st.subheader("📋 Daftar Deadline Aktif")
        
        if len(st.session_state.deadlines) == 0:
            st.info("Belum ada deadline yang ditambahkan. Gunakan formulir di sebelah kiri untuk menambah tugas.")
        else:
            # Mengurutkan daftar tugas berdasarkan tanggal deadline terdekat
            sorted_deadlines = sorted(st.session_state.deadlines, key=lambda x: x["Deadline"])
            
            for index, item in enumerate(sorted_deadlines):
                # Hitung sisa hari
                sisa_hari = (item["Deadline"] - date.today()).days
                
                # Menentukan badge warna status berdasarkan selisih hari
                if sisa_hari <= 3:
                    badge_class = "badge-urgent"
                    status_label = "Mendesak"
                elif sisa_hari <= 7:
                    badge_class = "badge-normal"
                    status_label = "Segera"
                else:
                    badge_class = "badge-safe"
                    status_label = "Aman"

                # Render Kartu Tampilan Custom
                st.markdown(f"""
                <div class="dashboard-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #0F172A;">{item['Tugas']}</h4>
                        <span class="{badge_class}">{sisa_hari} Hari Lagi ({status_label})</span>
                    </div>
                    <p style="margin: 6px 0 0 0; color: #64748B; font-size: 0.9rem;">
                        📚 <b>{item['Matkul']}</b> | Tenggat: {item['Deadline'].strftime('%d %B %Y')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Tombol Selesai untuk Menghapus Tugas
                if st.button(f"✔️ Tandai Selesai ({item['Tugas']})", key=f"btn_{index}"):
                    st.session_state.deadlines.remove(item)
                    st.success(f"Tugas '{item['Tugas']}' selesai!")
                    st.rerun()

elif menu == "Tabel Rekapitulasi":
    st.markdown('<div class="main-title">📊 Tabel Rekapitulasi</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Ringkasan seluruh tugas dalam bentuk tabel interaktif.</div>', unsafe_allow_html=True)

    if len(st.session_state.deadlines) > 0:
        df = pd.DataFrame(st.session_state.deadlines)
        df["Deadline"] = df["Deadline"].apply(lambda x: x.strftime('%d %B %Y'))
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Tidak ada data untuk ditampilkan.")
