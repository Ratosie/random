# ============================================================
# Dashboard Interaktif Visualisasi Data Kesehatan
# Dibangun dengan Streamlit
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# Konfigurasi Halaman
# ------------------------------------------------------------
st.set_page_config(
    page_title="Healthcare Data Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# Header Dashboard
# ------------------------------------------------------------
st.title("💊 Healthcare Data Visualization Dashboard")
st.markdown("""
Dashboard ini menyajikan visualisasi interaktif dari dataset *Healthcare*.
Terdapat tiga fokus utama analisis:
1. **Tren Penyakit**
2. **Biaya Pengobatan**
3. **Perbandingan Demografis Pasien**
""")

# ------------------------------------------------------------
# Load Dataset
# ------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("healthcare_dataset_no_duplicates.csv")
    # Pastikan kolom tanggal dikenali sebagai datetime
    if 'Date of Admission' in df.columns:
        df['Date of Admission'] = pd.to_datetime(df['Date of Admission'], errors='coerce')
    return df

df = load_data()

# Sidebar Navigasi
st.sidebar.title("🧭 Navigasi Dashboard")
page = st.sidebar.radio(
    "Pilih Halaman Analisis:",
    ["Tren Penyakit", "Biaya Pengobatan", "Perbandingan Demografis Pasien"]
)

# ------------------------------------------------------------
# 1️⃣ TREN PENYAKIT
# ------------------------------------------------------------
if page == "Tren Penyakit":
    st.header("📈 Analisis Tren Penyakit")

    st.markdown("""
    Analisis ini menunjukkan pola kemunculan penyakit berdasarkan waktu dan tipe penerimaan pasien.
    Gunakan filter di bawah untuk menyesuaikan tampilan data.
    """)

    # Filter interaktif
    diseases = df['Medical Condition'].dropna().unique()
    selected_disease = st.multiselect("Pilih Jenis Penyakit:", diseases, default=diseases[:3])

    filtered_df = df[df['Medical Condition'].isin(selected_disease)]

    # --- Line Chart: Tren waktu masuk pasien per penyakit ---
    st.subheader("📆 Tren Jumlah Pasien Berdasarkan Waktu Masuk (Line Chart)")
    trend_df = (
        filtered_df.groupby([pd.Grouper(key='Date of Admission', freq='M'), 'Medical Condition'])
        .size()
        .reset_index(name='Jumlah Pasien')
    )

    fig_line = px.line(
        trend_df,
        x='Date of Admission',
        y='Jumlah Pasien',
        color='Medical Condition',
        markers=True,
        title="Tren Jumlah Pasien per Penyakit dari Waktu ke Waktu"
    )
    fig_line.update_layout(xaxis_title="Tanggal Masuk", yaxis_title="Jumlah Pasien")
    st.plotly_chart(fig_line, use_container_width=True)

    # --- Bar Chart: Distribusi penyakit & tipe penerimaan ---
    st.subheader("🏥 Distribusi Penyakit dan Tipe Penerimaan Pasien (Bar Chart)")
    bar_df = (
        filtered_df.groupby(['Medical Condition', 'Admission Type'])
        .size()
        .reset_index(name='Jumlah Pasien')
    )

    fig_bar = px.bar(
        bar_df,
        x='Medical Condition',
        y='Jumlah Pasien',
        color='Admission Type',
        barmode='group',
        title="Distribusi Pasien Berdasarkan Jenis Penyakit dan Tipe Penerimaan"
    )
    fig_bar.update_layout(xaxis_title="Jenis Penyakit", yaxis_title="Jumlah Pasien")
    st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------------------------------------------
# 2️⃣ BIAYA PENGOBATAN
# ------------------------------------------------------------
elif page == "Biaya Pengobatan":
    st.header("💰 Analisis Biaya Pengobatan")

    st.markdown("""
    Analisis ini bertujuan untuk memahami variasi biaya pengobatan berdasarkan penyakit, rumah sakit, dokter, dan penyedia asuransi.
    """)

    # --- Boxplot: Distribusi biaya per penyakit ---
    st.subheader("📊 Distribusi Biaya Pengobatan per Jenis Penyakit (Boxplot)")
    fig_box = px.box(
        df,
        x='Medical Condition',
        y='Billing Amount',
        color='Medical Condition',
        title="Distribusi Biaya Pengobatan Berdasarkan Jenis Penyakit",
        points="outliers"
    )
    fig_box.update_layout(xaxis_title="Jenis Penyakit", yaxis_title="Biaya Pengobatan")
    st.plotly_chart(fig_box, use_container_width=True)

    # --- Bar Chart: Rata-rata biaya per rumah sakit ---
    st.subheader("🏥 Rata-rata Biaya Pengobatan per Rumah Sakit (Bar Chart)")
    avg_cost = df.groupby('Hospital')['Billing Amount'].mean().sort_values(ascending=False).reset_index()
    fig_hosp = px.bar(
        avg_cost,
        x='Hospital',
        y='Billing Amount',
        title="Rata-rata Biaya Pengobatan per Rumah Sakit",
        color='Billing Amount',
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_hosp, use_container_width=True)

    # --- Pie Chart: Distribusi Asuransi ---
    st.subheader("🧾 Proporsi Pasien Berdasarkan Penyedia Asuransi (Pie Chart)")
    insurance_df = df['Insurance Provider'].value_counts().reset_index()
    insurance_df.columns = ['Insurance Provider', 'Jumlah Pasien']
    fig_pie = px.pie(
        insurance_df,
        names='Insurance Provider',
        values='Jumlah Pasien',
        title="Proporsi Pasien Berdasarkan Penyedia Asuransi",
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ------------------------------------------------------------
# 3️⃣ PERBANDINGAN DEMOGRAFIS PASIEN
# ------------------------------------------------------------
elif page == "Perbandingan Demografis Pasien":
    st.header("👥 Analisis Perbandingan Demografis Pasien")

    st.markdown("""
    Analisis ini menampilkan distribusi pasien berdasarkan usia, jenis kelamin, golongan darah, dan rumah sakit.
    """)

    # --- Histogram: Distribusi umur ---
    st.subheader("🎂 Distribusi Usia Pasien (Histogram)")
    fig_hist = px.histogram(
        df,
        x='Age',
        nbins=20,
        color_discrete_sequence=['#5DADE2'],
        title="Distribusi Umur Pasien"
    )
    fig_hist.update_layout(xaxis_title="Usia", yaxis_title="Jumlah Pasien")
    st.plotly_chart(fig_hist, use_container_width=True)

    # --- Pie Chart: Jenis Kelamin ---
    st.subheader("⚧ Proporsi Jenis Kelamin Pasien (Pie Chart)")
    gender_df = df['Gender'].value_counts().reset_index()
    gender_df.columns = ['Gender', 'Jumlah']
    fig_gender = px.pie(
        gender_df,
        names='Gender',
        values='Jumlah',
        title="Proporsi Pasien Berdasarkan Jenis Kelamin",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_gender, use_container_width=True)

    # --- Stacked Bar: Jenis Kelamin per Rumah Sakit ---
    st.subheader("🏥 Jumlah Pasien Berdasarkan Jenis Kelamin per Rumah Sakit (Stacked Bar Chart)")
    gender_hosp_df = (
        df.groupby(['Hospital', 'Gender'])
        .size()
        .reset_index(name='Jumlah Pasien')
    )
    fig_stack = px.bar(
        gender_hosp_df,
        x='Hospital',
        y='Jumlah Pasien',
        color='Gender',
        title="Distribusi Pasien Berdasarkan Jenis Kelamin dan Rumah Sakit",
        barmode='stack'
    )
    fig_stack.update_layout(xaxis_title="Rumah Sakit", yaxis_title="Jumlah Pasien")
    st.plotly_chart(fig_stack, use_container_width=True)

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------
st.markdown("---")
st.markdown("🩺 **Dashboard ini dibuat menggunakan Streamlit dan Plotly Express** — Menyajikan data kesehatan secara interaktif dan informatif.")
