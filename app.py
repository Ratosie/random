import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Hospital Health Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv('healthcare_dataset_no_duplicates.csv')
    
    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Convert dates
    df['date_of_admission'] = pd.to_datetime(df['date_of_admission'], errors='coerce')
    df['discharge_date'] = pd.to_datetime(df['discharge_date'], errors='coerce')
    
    # Calculate length of stay
    df['length_of_stay'] = (df['discharge_date'] - df['date_of_admission']).dt.days
    
    # Clean billing amount
    df['billing_amount'] = df['billing_amount'].clip(lower=0)
    
    return df

df = load_data()

# Simple styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .section-title {
        font-size: 1.5rem;
        color: #2C3E50;
        margin: 2rem 0 1rem 0;
        border-bottom: 3px solid #3498DB;
        padding-bottom: 0.5rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">🏥 Dashboard Analisis Data Kesehatan</div>', unsafe_allow_html=True)
st.markdown("### Fokus: Tren Penyakit, Biaya Pengobatan, Perbandingan Demografis Pasien")

# Sidebar navigation
st.sidebar.header("🧭 Navigasi Analisis")
analysis_focus = st.sidebar.radio(
    "Pilih Fokus Analisis:",
    ["Tren Penyakit", "Biaya Pengobatan", "Perbandingan Demografis Pasien"]
)

# Global filters
st.sidebar.header("🎛️ Filter Data")
year_filter = st.sidebar.selectbox(
    "Periode Waktu",
    options=["Semua Tahun"] + sorted(df['date_of_admission'].dt.year.dropna().unique().tolist())
)

condition_filter = st.sidebar.selectbox(
    "Kondisi Kesehatan",
    options=["Semua Kondisi"] + sorted(df['medical_condition'].unique().tolist())
)

age_range = st.sidebar.slider(
    "Rentang Usia",
    min_value=int(df['age'].min()),
    max_value=int(df['age'].max()),
    value=(13, 89)
)

# Apply filters
filtered_df = df.copy()
if year_filter != "Semua Tahun":
    filtered_df = filtered_df[filtered_df['date_of_admission'].dt.year == year_filter]
if condition_filter != "Semua Kondisi":
    filtered_df = filtered_df[filtered_df['medical_condition'] == condition_filter]
filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]

# Quick Stats
st.markdown("## 📊 Ringkasan Cepat")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Pasien", f"{len(filtered_df):,}")

with col2:
    avg_stay = filtered_df['length_of_stay'].mean()
    delta_color = "normal" if avg_stay < 7 else "inverse"
    st.metric("Rata-rata Rawat", f"{avg_stay:.1f} hari", delta_color=delta_color)

with col3:
    avg_bill = filtered_df['billing_amount'].mean()
    delta_color = "normal" if avg_bill < 20000 else "inverse"
    st.metric("Rata-rata Biaya", f"${avg_bill:,.0f}", delta_color=delta_color)

with col4:
    recovery_rate = (filtered_df['test_results'] == 'Normal').mean() * 100
    delta_color = "normal" if recovery_rate > 60 else "inverse"
    st.metric("Tingkat Pemulihan", f"{recovery_rate:.1f}%", delta_color=delta_color)

# ============================================================
# 1️⃣ TREN PENYAKIT
# ============================================================
if analysis_focus == "Tren Penyakit":
    st.markdown('<div class="section-title">📈 Analisis Tren Penyakit</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Line Chart: Tren penyakit dari waktu ke waktu
        st.subheader("📆 Tren Penyakit dari Waktu ke Waktu")
        
        # Prepare data for monthly trends
        monthly_trend = filtered_df.groupby([
            pd.Grouper(key='date_of_admission', freq='M'),
            'medical_condition'
        ]).size().reset_index(name='jumlah_pasien')
        
        if not monthly_trend.empty:
            fig_trend = px.line(
                monthly_trend,
                x='date_of_admission',
                y='jumlah_pasien',
                color='medical_condition',
                title="Tren Jumlah Pasien per Penyakit",
                markers=True
            )
            fig_trend.update_layout(
                xaxis_title="Bulan",
                yaxis_title="Jumlah Pasien",
                showlegend=True
            )
            st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        # Top conditions
        st.subheader("🩺 Penyakit Paling Umum")
        top_conditions = filtered_df['medical_condition'].value_counts().head(10)
        
        for condition, count in top_conditions.items():
            percentage = (count / len(filtered_df)) * 100
            st.write(f"**{condition}**")
            st.write(f"{count} pasien ({percentage:.1f}%)")
            st.progress(percentage/100)
    
    # Seasonal patterns
    st.subheader("📅 Pola Musiman Kunjungan Rumah Sakit")
    monthly_visits = filtered_df['date_of_admission'].dt.month.value_counts().sort_index()
    
    # Ensure all months are represented
    all_months = pd.Series(range(1, 13), index=range(1, 13))
    monthly_visits_complete = all_months.map(monthly_visits).fillna(0)
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    fig_seasonal = px.bar(
        x=month_names,
        y=monthly_visits_complete.values,
        title="Kunjungan Rumah Sakit per Bulan",
        labels={'x': 'Bulan', 'y': 'Jumlah Pasien'},
        color=monthly_visits_complete.values,
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_seasonal, use_container_width=True)
    
    # Admission types by condition - CHANGED TO GROUPED BAR
    st.subheader("🏥 Tipe Penerimaan per Penyakit")
    admission_condition = filtered_df.groupby(['medical_condition', 'admission_type']).size().reset_index(name='jumlah')
    
    fig_admission = px.bar(
        admission_condition,
        x='medical_condition',
        y='jumlah',
        color='admission_type',
        title="Distribusi Tipe Penerimaan per Penyakit",
        barmode='group'  # Changed from 'stack' to 'group'
    )
    fig_admission.update_layout(xaxis_title="Penyakit", yaxis_title="Jumlah Pasien")
    st.plotly_chart(fig_admission, use_container_width=True)

# ============================================================
# 2️⃣ BIAYA PENGOBATAN
# ============================================================
elif analysis_focus == "Biaya Pengobatan":
    st.markdown('<div class="section-title">💰 Analisis Biaya Pengobatan</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost distribution by condition
        st.subheader("📊 Distribusi Biaya per Penyakit")
        fig_cost_box = px.box(
            filtered_df,
            x='medical_condition',
            y='billing_amount',
            color='medical_condition',
            title="Distribusi Biaya Pengobatan per Penyakit"
        )
        fig_cost_box.update_layout(showlegend=False, xaxis_title="Penyakit", yaxis_title="Biaya ($)")
        st.plotly_chart(fig_cost_box, use_container_width=True)
    
    with col2:
        # Average cost by hospital
        st.subheader("🏥 Rata-rata Biaya per Rumah Sakit")
        hospital_costs = filtered_df.groupby('hospital')['billing_amount'].mean().sort_values(ascending=False).head(10)
        
        fig_hospital_cost = px.bar(
            x=hospital_costs.values,
            y=hospital_costs.index,
            orientation='h',
            title="10 Rumah Sakit dengan Biaya Tertinggi",
            labels={'x': 'Rata-rata Biaya ($)', 'y': 'Rumah Sakit'},
            color=hospital_costs.values,
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_hospital_cost, use_container_width=True)
    
    # Insurance and costs
    st.subheader("🧾 Biaya berdasarkan Asuransi")
    col1, col2 = st.columns(2)
    
    with col1:
        # Insurance distribution
        insurance_counts = filtered_df['insurance_provider'].value_counts().head(8)
        fig_insurance = px.pie(
            values=insurance_counts.values,
            names=insurance_counts.index,
            title="Distribusi Provider Asuransi"
        )
        st.plotly_chart(fig_insurance, use_container_width=True)
    
    with col2:
        # Cost by insurance
        insurance_costs = filtered_df.groupby('insurance_provider')['billing_amount'].mean().sort_values(ascending=False).head(8)
        fig_insurance_cost = px.bar(
            x=insurance_costs.index,
            y=insurance_costs.values,
            title="Rata-rata Biaya per Provider Asuransi",
            labels={'x': 'Provider Asuransi', 'y': 'Rata-rata Biaya ($)'},
            color=insurance_costs.values,
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_insurance_cost, use_container_width=True)
    
    # Cost vs Recovery analysis
    st.subheader("🔍 Hubungan Biaya dengan Tingkat Pemulihan")
    condition_analysis = filtered_df.groupby('medical_condition').agg({
        'billing_amount': 'mean',
        'test_results': lambda x: (x == 'Normal').mean() * 100,
        'length_of_stay': 'mean'
    }).round(2).reset_index()
    
    condition_analysis.columns = ['Penyakit', 'Biaya_Rata', 'Tingkat_Pemulihan', 'Rawat_Rata']
    
    fig_cost_recovery = px.scatter(
        condition_analysis,
        x='Biaya_Rata',
        y='Tingkat_Pemulihan',
        size='Rawat_Rata',
        color='Penyakit',
        title="Hubungan Biaya Pengobatan dengan Tingkat Pemulihan",
        labels={
            'Biaya_Rata': 'Rata-rata Biaya ($)',
            'Tingkat_Pemulihan': 'Tingkat Pemulihan (%)',
            'Rawat_Rata': 'Lama Rawat (hari)'
        },
        hover_data=['Penyakit', 'Biaya_Rata', 'Tingkat_Pemulihan', 'Rawat_Rata']
    )
    st.plotly_chart(fig_cost_recovery, use_container_width=True)

# ============================================================
# 3️⃣ PERBANDINGAN DEMOGRAFIS PASIEN
# ============================================================
elif analysis_focus == "Perbandingan Demografis Pasien":
    st.markdown('<div class="section-title">👥 Analisis Demografis Pasien</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Age distribution
        st.subheader("🎂 Distribusi Usia Pasien")
        
        # Create age groups
        age_bins = [0, 18, 35, 50, 65, 100]
        age_labels = ['Anak (0-18)', 'Dewasa Muda (19-35)', 'Dewasa (36-50)', 'Lansia (51-65)', 'Manula (65+)']
        filtered_df['kelompok_usia'] = pd.cut(filtered_df['age'], bins=age_bins, labels=age_labels)
        
        age_counts = filtered_df['kelompok_usia'].value_counts()
        
        fig_age = px.bar(
            x=age_counts.index,
            y=age_counts.values,
            title="Distribusi Pasien berdasarkan Kelompok Usia",
            labels={'x': 'Kelompok Usia', 'y': 'Jumlah Pasien'},
            color=age_counts.index,
            color_discrete_sequence=['#3498DB', '#9B59B6', '#2ECC71', '#F39C12', '#E74C3C']
        )
        fig_age.update_layout(showlegend=False)
        st.plotly_chart(fig_age, use_container_width=True)
    
    with col2:
        # Gender distribution
        st.subheader("⚧ Distribusi Jenis Kelamin")
        gender_counts = filtered_df['gender'].value_counts()
        
        fig_gender = px.pie(
            values=gender_counts.values,
            names=gender_counts.index,
            title="Proporsi Jenis Kelamin Pasien",
            color_discrete_sequence=['#4A90E2', '#FF6B9D']
        )
        fig_gender.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_gender, use_container_width=True)
    
    # Gender by condition - CHANGED TO GROUPED BAR
    st.subheader("🩺 Penyakit berdasarkan Jenis Kelamin")
    gender_condition = filtered_df.groupby(['medical_condition', 'gender']).size().reset_index(name='jumlah')
    top_conditions = gender_condition.groupby('medical_condition')['jumlah'].sum().nlargest(6).index
    gender_condition_top = gender_condition[gender_condition['medical_condition'].isin(top_conditions)]
    
    fig_gender_condition = px.bar(
        gender_condition_top,
        x='medical_condition',
        y='jumlah',
        color='gender',
        title="6 Penyakit Terbanyak berdasarkan Jenis Kelamin",
        labels={'jumlah': 'Jumlah Pasien', 'medical_condition': 'Penyakit'},
        color_discrete_sequence=['#FF6B9D', '#4A90E2'],
        barmode='group'  # Changed from 'group' to 'group' (already was grouped, but keeping for consistency)
    )
    st.plotly_chart(fig_gender_condition, use_container_width=True)
    
    # Blood type distribution
    st.subheader("🩸 Distribusi Golongan Darah")
    blood_counts = filtered_df['blood_type'].value_counts()
    
    fig_blood = px.bar(
        x=blood_counts.index,
        y=blood_counts.values,
        title="Distribusi Golongan Darah Pasien",
        labels={'x': 'Golongan Darah', 'y': 'Jumlah Pasien'},
        color=blood_counts.index,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_blood.update_layout(showlegend=False)
    st.plotly_chart(fig_blood, use_container_width=True)
    
    # Hospital demographics - CHANGED TO GROUPED BAR
    st.subheader("🏥 Distribusi Pasien per Rumah Sakit")
    
    total_hospitals = filtered_df['hospital'].nunique()
    total_patients = len(filtered_df)
    
    hospital_demo = filtered_df.groupby(['hospital', 'gender']).size().reset_index(name='jumlah')
    top_hospitals = hospital_demo.groupby('hospital')['jumlah'].sum().nlargest(8).index
    hospital_demo_top = hospital_demo[hospital_demo['hospital'].isin(top_hospitals)]
    
    top_hospitals_total_patients = hospital_demo_top['jumlah'].sum()
    percentage_of_total = (top_hospitals_total_patients / total_patients) * 100
    
    fig_hospital_demo = px.bar(
        hospital_demo_top,
        x='hospital',
        y='jumlah',
        color='gender',
        title=f"8 Rumah Sakit dengan Pasien Terbanyak ({percentage_of_total:.1f}% dari {total_patients:,} total pasien)",
        labels={'jumlah': 'Jumlah Pasien', 'hospital': 'Rumah Sakit'},
        color_discrete_sequence=['#FF6B9D', '#4A90E2'],
        barmode='group'
    )
    
    # Add subtitle with context
    st.caption(f"Menampilkan 8 rumah sakit teratas dari total {total_hospitals} rumah sakit")
    st.plotly_chart(fig_hospital_demo, use_container_width=True)

    
# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7F8C8D;">
    <p><strong>Dashboard Analisis Kesehatan</strong> - Fokus: Tren Penyakit, Biaya Pengobatan, Perbandingan Demografis Pasien</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📊 Panduan Dashboard
- **Tren Penyakit**: Pola waktu dan musiman
- **Biaya Pengobatan**: Analisis biaya dan asuransi  
- **Demografi Pasien**: Usia, gender, golongan darah
""")
