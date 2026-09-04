import streamlit as st
import pandas as pd
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai

# Import Pustaka Google Drive API
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials
import io

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Deadline Reminder & Subject Archive",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS untuk UI/UX Modern
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
        margin-bottom: 0.5rem;
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
    .archive-box {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 1px solid #BFDBFE;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Inisialisasi Koneksi Google Sheets & Drive
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    conn = None

def upload_to_drive(uploaded_file):
    """Fungsi mengunggah berkas hasil pengerjaan ke Google Drive"""
    try:
        secrets_gsheets = st.secrets.get("connections", {}).get("gsheets", {})
        if not secrets_gsheets:
            return None

        creds_dict = {
            "type": secrets_gsheets.get("type"),
            "project_id": secrets_gsheets.get("project_id"),
            "private_key_id": secrets_gsheets.get("private_key_id"),
            "private_key": secrets_gsheets.get("private_key").replace("\\n", "\n") if secrets_gsheets.get("private_key") else None,
            "client_email": secrets_gsheets.get("client_email"),
            "client_id": secrets_gsheets.get("client_id"),
            "auth_uri": secrets_gsheets.get("auth_uri"),
            "token_uri": secrets_gsheets.get("token_uri"),
            "auth_provider_x509_cert_url": secrets_gsheets.get("auth_provider_x509_cert_url"),
            "client_x509_cert_url": secrets_gsheets.get("client_x509_cert_url"),
        }

        scopes = ["https://www.googleapis.com/auth/drive.file"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {'name': f"[SELESAI]_{uploaded_file.name}"}
        
        # Masukkan file ke folder spesifik jika ID tersedia di Secrets
        folder_id = st.secrets.get("DRIVE_FOLDER_ID")
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), mimetype=uploaded_file.type, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

        # Atur akses file agar publik dengan link
        service.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()

        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Gagal mengunggah file ke Google Drive: {e}")
        return None

def load_data():
    """Fungsi mengambil data dari Google Sheets"""
    if conn is not None:
        try:
            df = conn.read(worksheet="Sheet1", ttl=0)
            if not df.empty and "Tugas" in df.columns:
                df["Deadline"] = pd.to_datetime(df["Deadline"]).dt.date
                return df
        except Exception:
            pass
    
    # Session state cadangan jika mode lokal
    if "local_deadlines" not in st.session_state:
        st.session_state.local_deadlines = pd.DataFrame([
            {"Tugas": "Laporan Praktikum AI", "Matkul": "Kecerdasan Buatan", "Deadline": date(2026, 9, 6)},
            {"Tugas": "Desain Wireframe UI/UX", "Matkul": "Interaksi Manusia & Komputer", "Deadline": date(2026, 9, 12)}
        ])
    return st.session_state.local_deadlines

df_deadlines = load_data()

# Setup AI Gemini
gemini_key = st.secrets.get("GEMINI_API_KEY")
if gemini_key:
    genai.configure(api_key=gemini_key)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    gemini_model = None

# Chat Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya **Academic Co-pilot**. Ada yang bisa dibantu terkait deadline tugas atau materi kuliahmu?"}
    ]

# 4. Sidebar Navigasi
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2693/2693507.png", width=60)
    st.title("Menu Utama")
    page = st.radio("Navigasi", ["Dashboard & Deadline", "Arsip Mata Kuliah", "🤖 AI Co-pilot", "Pengaturan"])
    
    st.divider()
    if conn:
        st.success("🟢 Google Sheets Terhubung", icon="📊")
    else:
        st.info("🟡 Mode Lokal (GSheets Belum Set)", icon="💾")
        
    if gemini_model:
        st.success("🤖 Gemini AI Connected", icon="✅")
    else:
        st.warning("⚠️ Gemini API Belum Set", icon="🔑")

# 5. Routing Tampilan Halaman

# --- HALAMAN 1: DASHBOARD & DEADLINE REMINDER ---
if page == "Dashboard & Deadline":
    st.markdown('<div class="main-title">Deadline Reminder & Subject Archive</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Kelola tenggat waktu tugas secara terpusat dengan penyimpanan Google Sheets.</div>', unsafe_allow_html=True)

    # Hitung Statistik
    total_tugas = len(df_deadlines)
    urgent_count = 0
    if not df_deadlines.empty:
        urgent_count = sum((df_deadlines["Deadline"] - date.today()).apply(lambda x: x.days <= 3))

    # Ringkasan Metrik
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Tugas Aktif", value=total_tugas)
    with col2:
        st.metric(label="Mendesak (<3 Hari)", value=urgent_count, delta_color="inverse")
    with col3:
        st.metric(label="Arsip Mata Kuliah", value=4)
    with col4:
        st.metric(label="Status Database", value="Google Sheets" if conn else "Lokal")

    st.divider()

    col_input, col_display = st.columns([1, 1.4])

    # Form Input Tugas Baru (Bersih tanpa upload file)
    with col_input:
        st.subheader("➕ Tambah Deadline Baru")
        with st.form(key="form_add_task", clear_on_submit=True):
            nama_tugas = st.text_input("Nama Tugas / Proyek", placeholder="Contoh: Laporan Keamanan Siber")
            nama_matkul = st.text_input("Nama Mata Kuliah", placeholder="Contoh: Keamanan Informasi")
            tanggal_deadline = st.date_input("Tanggal Deadline", value=date.today(), min_value=date.today())
            
            submit_btn = st.form_submit_button(label="📌 Simpan Tugas", use_container_width=True)

            if submit_btn:
                if not nama_tugas.strip() or not nama_matkul.strip():
                    st.error("⚠️ Nama tugas dan mata kuliah wajib diisi!")
                else:
                    new_row = pd.DataFrame([{"Tugas": nama_tugas, "Matkul": nama_matkul, "Deadline": tanggal_deadline}])
                    
                    if conn:
                        updated_df = pd.concat([df_deadlines, new_row], ignore_index=True)
                        updated_df["Deadline"] = updated_df["Deadline"].astype(str)
                        conn.update(worksheet="Sheet1", data=updated_df)
                    else:
                        st.session_state.local_deadlines = pd.concat([st.session_state.local_deadlines, new_row], ignore_index=True)
                        
                    st.success(f"✅ Tugas '{nama_tugas}' berhasil disimpan!")
                    st.rerun()

    # Daftar Kartu Deadline + Fitur Upload Hasil Pekerjaan
    with col_display:
        st.subheader("📋 Daftar Deadline Terdekat")
        if df_deadlines.empty:
            st.info("Belum ada tugas tersimpan.")
        else:
            sorted_df = df_deadlines.sort_values(by="Deadline").reset_index(drop=True)
            for index, row in sorted_df.iterrows():
                sisa_hari = (row["Deadline"] - date.today()).days
                
                badge_class = "badge-safe"
                status_label = "Aman"
                if sisa_hari <= 3:
                    badge_class = "badge-urgent"
                    status_label = "Mendesak"
                elif sisa_hari <= 7:
                    badge_class = "badge-normal"
                    status_label = "Segera"

                # Tampilan Kartu Tugas
                st.markdown(f"""
                <div class="dashboard-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #0F172A;">{row['Tugas']}</h4>
                        <span class="{badge_class}">{sisa_hari} Hari Lagi ({status_label})</span>
                    </div>
                    <p style="margin: 6px 0 0 0; color: #64748B; font-size: 0.9rem;">
                        📚 <b>{row['Matkul']}</b> | Tenggat: {row['Deadline'].strftime('%d %B %Y')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Popover Form Pengumpulan Hasil Tugas
                with st.popover(f"✔️ Selesaikan Task '{row['Tugas']}'", use_container_width=True):
                    st.markdown("#### 📤 Pengumpulan Hasil Tugas")
                    st.write("Upload file pengerjaan tugas kamu (PDF, DOCX, ZIP, Gambar) untuk menandai tugas ini selesai:")
                    
                    uploaded_hasil = st.file_uploader(
                        "Pilih Berkas Hasil Tugas", 
                        type=["pdf", "docx", "png", "jpg", "zip", "rar", "pptx"], 
                        key=f"file_{index}"
                    )
                    
                    if st.button("🚀 Kirim & Mark as Done", key=f"btn_finish_{index}", type="primary"):
                        if uploaded_hasil is None:
                            st.warning("⚠️ Harap upload file hasil tugas terlebih dahulu!")
                        else:
                            with st.spinner("Mengunggah hasil tugas ke Google Drive..."):
                                drive_link = upload_to_drive(uploaded_hasil)
                            
                            # Hapus tugas dari daftar tugas aktif di Google Sheets
                            updated_df = sorted_df.drop(index).reset_index(drop=True)
                            if conn:
                                updated_df["Deadline"] = updated_df["Deadline"].astype(str)
                                conn.update(worksheet="Sheet1", data=updated_df)
                            else:
                                st.session_state.local_deadlines = updated_df
                            
                            st.success(f"🎉 Selamat! Tugas '{row['Tugas']}' selesai dan berkas berhasil disimpan di Google Drive!")
                            st.rerun()

# --- HALAMAN 2: ARSIP MATA KULIAH ---
elif page == "Arsip Mata Kuliah":
    st.markdown('<div class="main-title">📚 Subject Archive</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Penyimpanan modul, catatan, dan berkas kuliah terorganisir.</div>', unsafe_allow_html=True)

    st.text_input("🔍 Cari arsip modul atau materi...", placeholder="Ketik nama mata kuliah...")
    
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

# --- HALAMAN 3: AI CO-PILOT ---
elif page == "🤖 AI Co-pilot":
    st.markdown('<div class="main-title">🤖 Academic AI Co-pilot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">AI membaca data tugas dari Google Sheets untuk memberikan saran prioritas belajar.</div>', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Tanyakan sesuatu (Contoh: 'Buatkan jadwal belajar untuk tugas mendesakku')"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if gemini_model:
                if not df_deadlines.empty:
                    context_list = [f"- {r['Tugas']} (Matkul: {r['Matkul']}, Deadline: {r['Deadline']})" for _, r in df_deadlines.iterrows()]
                    context_str = "\n".join(context_list)
                else:
                    context_str = "Tidak ada tugas aktif saat ini."

                full_prompt = f"""
                Kamu adalah Academic Co-pilot untuk mahasiswa.
                Daftar tugas aktif mahasiswa saat ini yang diambil dari database:
                {context_str}

                Pertanyaan Pengguna: {prompt}
                Jawab dengan ringkas, membantu, terstruktur, dan gunakan penanda bold jika perlu.
                """
                
                try:
                    response = gemini_model.generate_content(full_prompt)
                    ai_reply = response.text
                except Exception as e:
                    ai_reply = f"Gagal menghubungkan ke AI: {str(e)}"
            else:
                ai_reply = "API Key Gemini belum dikonfigurasi pada `secrets.toml`."

            st.markdown(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

# --- HALAMAN 4: PENGATURAN ---
elif page == "Pengaturan":
    st.markdown('<div class="main-title">⚙️ Pengaturan Aplikasi</div>', unsafe_allow_html=True)
    st.toggle("Aktifkan Notifikasi Email", value=True)
    st.toggle("Auto-sync ke Google Sheets", value=True)
