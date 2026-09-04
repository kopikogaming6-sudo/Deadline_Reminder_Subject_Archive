import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Konfigurasi Halaman & Tema
st.set_page_config(
    page_title="Modern Analytics Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS untuk UI/UX Interaktif & Modern
st.markdown("""
<style>
    /* Gradient Header & Font Custom */
    .hero-title {
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        color: #64748B;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    /* Card Container Styling */
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        color: #0F172A;
        font-size: 1.8rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar Navigation & Branding
with st.sidebar:
    st.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=50)
    st.title("Control Panel")
    st.caption("Versi 1.0.0")
    
    st.divider()
    
    menu = st.radio(
        "Navigasi",
        ["Dashboard", "Analisis Data", "Pengaturan"],
        index=0
    )
    
    st.divider()
    filter_date = st.date_input("Rentang Waktu", [])
    status_filter = st.multiselect("Status", ["Aktif", "Pending", "Selesai"], default=["Aktif"])

# 4. Content Area berdasarkan Menu
if menu == "Dashboard":
    # Hero Section
    st.markdown('<p class="hero-title">Overview Performa</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Pantau metrik utama dan tren lalu lintas secara real-time.</p>', unsafe_allow_html=True)
    
    # Grid Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Total Pengguna</div>
            <div class="metric-value">12,450</div>
            <span style="color: #10B981; font-size: 0.85rem;">▲ 12% dari bulan lalu</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Pendapatan</div>
            <div class="metric-value">Rp 84.2M</div>
            <span style="color: #10B981; font-size: 0.85rem;">▲ 8% dari target</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Konversi</div>
            <div class="metric-value">3.42%</div>
            <span style="color: #EF4444; font-size: 0.85rem;">▼ 0.5% minggu ini</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Tiket Aktif</div>
            <div class="metric-value">18</div>
            <span style="color: #64748B; font-size: 0.85rem;">Perlu penanganan</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabbed Layout untuk Visualisasi
    tab1, tab2 = st.tabs(["📊 Tren Penjualan", "📋 Data Transaksi"])
    
    # Generate Dummy Data
    dates = pd.date_range(start="2026-01-01", periods=30)
    df_chart = pd.DataFrame({
        "Tanggal": dates,
        "Penjualan": np.random.randint(100, 500, size=30),
        "Pengunjung": np.random.randint(1000, 3000, size=30)
    })
    
    with tab1:
        fig = px.area(
            df_chart, 
            x="Tanggal", 
            y=["Penjualan", "Pengunjung"],
            title="Lalu Lintas & Transaksi Harian",
            color_discrete_sequence=["#4F46E5", "#06B6D4"]
        )
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.dataframe(
            df_chart,
            use_container_width=True,
            hide_index=True
        )

elif menu == "Analisis Data":
    st.subheader("Analisis Detail")
    st.info("Pilih variabel di panel samping untuk memfilter data.")

elif menu == "Pengaturan":
    st.subheader("Pengaturan Profil")
    with st.form("settings_form"):
        st.text_input("Nama Lengkap", value="Admin User")
        st.text_input("Email", value="admin@example.com")
        st.toggle("Notifikasi Email", value=True)
        submitted = st.form_submit_button("Simpan Perubahan")
        if submitted:
            st.success("Pengaturan berhasil disimpan!")
