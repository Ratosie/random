import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Dashboard Analisis Kesehatan Rumah Sakit",
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

# Professional styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .section-title {
        font-size: 1.5rem;
        color: #2C3E50;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #3498DB;
        padding-bottom: 0.5rem;
        font-weight: 600;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498DB;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">Dashboard Analisis Kesehatan Rumah Sakit</div>', unsafe_allow_html=True)
st.markdown("### Fokus: Tren Penyakit, Biaya Pengobatan, Demografi Pasien")

# Sidebar navigation
st.sidebar.header("Navigasi")
analysis_focus = st.sidebar.radio(
    "Pilih Fokus Analisis:",
    ["Tren Penyakit", "Biaya Pengobatan", "Demografi Pasien"]
)

# Global filters
st.sidebar.header("Filter Data")
year_filter = st.sidebar.selectbox(
    "Periode Waktu",
    options=["Semua Tahun"] + sorted(df['date_of_admission'].dt.year.dropna().unique().tolist())
)

condition_filter = st.sidebar.selectbox(
    "Kondisi Medis",
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
st.markdown("## Summary")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Pasien", f"{len(filtered_df):,}")

with col2:
    avg_stay = filtered_df['length_of_stay'].mean()
    st.metric("Rata-rata Masa Rawat", f"{avg_stay:.1f} hari")

with col3:
    avg_bill = filtered_df['billing_amount'].mean()
    st.metric("Rata-rata Biaya", f"${avg_bill:,.0f}")

with col4:
    recovery_rate = (filtered_df['test_results'] == 'Normal').mean() * 100
    st.metric("Tingkat Pemulihan", f"{recovery_rate:.1f}%")

# ============================================================
# 1️⃣ TREN PENYAKIT
# ============================================================
if analysis_focus == "Tren Penyakit":
    st.markdown('<div class="section-title">Analisis Tren Penyakit</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Line Chart: Disease trends over time
        st.subheader("Tren Penyakit Berdasarkan Waktu")
        
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
                title="Tren Jumlah Pasien per Kondisi Medis",
                markers=True
            )
            fig_trend.update_layout(
                xaxis_title="Bulan",
                yaxis_title="Jumlah Pasien",
                showlegend=True
            )
            st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        # Top conditions - simple version
        st.subheader("Kondisi Medis Paling Umum")
        top_conditions = filtered_df['medical_condition'].value_counts().head(10)
        
        fig_top_conditions = px.bar(
            x=top_conditions.values,
            y=top_conditions.index,
            orientation='h',
            title="Distribusi Kondisi Medis",
            labels={'x': 'Jumlah Pasien', 'y': ''},
            color=top_conditions.values,
            color_continuous_scale='Blues'
        )
        
        fig_top_conditions.update_layout(
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig_top_conditions, use_container_width=True)
        
        # Optional: Show summary statistics
        st.caption(f"Total {len(filtered_df)} pasien • {top_conditions.index[0]} paling umum ({top_conditions.iloc[0]} pasien)")
    
    # Seasonal patterns
    st.subheader("Pola Kunjungan Rumah Sakit Musiman")
    monthly_visits = filtered_df['date_of_admission'].dt.month.value_counts().sort_index()
    
    # Ensure all months are represented
    all_months = pd.Series(range(1, 13), index=range(1, 13))
    monthly_visits_complete = all_months.map(monthly_visits).fillna(0)
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 
                   'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
    
    fig_seasonal = px.bar(
        x=month_names,
        y=monthly_visits_complete.values,
        title="Kunjungan Rumah Sakit per Bulan",
        labels={'x': 'Bulan', 'y': 'Jumlah Pasien'},
        color=monthly_visits_complete.values,
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_seasonal, use_container_width=True)
    
    # Admission types by condition
    st.subheader("Tipe Penerimaan per Kondisi Medis")
    admission_condition = filtered_df.groupby(['medical_condition', 'admission_type']).size().reset_index(name='jumlah')

    fig_admission = px.bar(
        admission_condition,
        x='medical_condition',
        y='jumlah',
        color='admission_type',
        title="Distribusi Tipe Penerimaan per Kondisi Medis",
        barmode='group',
        color_discrete_map={
            'Emergency': '#DC2626',
            'Urgent': '#EA580C', 
            'Elective': '#16A34A'
        }
    )
    
    fig_admission.update_layout(xaxis_title="Kondisi Medis", yaxis_title="Jumlah Pasien")
    st.plotly_chart(fig_admission, use_container_width=True)

# ============================================================
# 2️⃣ BIAYA PENGOBATAN
# ============================================================
elif analysis_focus == "Biaya Pengobatan":
    st.markdown('<div class="section-title">Analisis Biaya Pengobatan</div>', unsafe_allow_html=True)
    
    # Average cost by hospital
    st.subheader("Rata-rata Biaya per Rumah Sakit")
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
    
    fig_hospital_cost.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig_hospital_cost.update_yaxes(autorange="reversed")
    
    st.plotly_chart(fig_hospital_cost, use_container_width=True)
    
    # Insurance and costs
    st.subheader("Analisis Biaya Berdasarkan Asuransi")
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
            color=insurance_costs.index,  # Add this line to enable color mapping
            color_discrete_map={
                'Cigna': "#75B0EB",
                'Medicare': "#2F5FE3", 
                'UnitedHealthCare': "#EDC0D0",
                'Blue Cross': "#E20B0B",
                'Aetna': "#7BD894",
            }
        )
        fig_insurance_cost.update_layout(showlegend=False)  # Hide legend since colors are self-explanatory
        st.plotly_chart(fig_insurance_cost, use_container_width=True)
    
    # Cost vs Recovery analysis
    st.subheader("Analisis Hubungan Biaya dengan Tingkat Pemulihan")
    condition_analysis = filtered_df.groupby('medical_condition').agg({
        'billing_amount': 'mean',
        'test_results': lambda x: (x == 'Normal').mean() * 100,
        'length_of_stay': 'mean'
    }).round(2).reset_index()
    
    condition_analysis.columns = ['Kondisi_Medis', 'Biaya_Rata', 'Tingkat_Pemulihan', 'Masa_Rawat_Rata']
    
    fig_cost_recovery = px.scatter(
        condition_analysis,
        x='Biaya_Rata',
        y='Tingkat_Pemulihan',
        size='Masa_Rawat_Rata',
        color='Kondisi_Medis',
        title="Hubungan Biaya Pengobatan dengan Tingkat Pemulihan",
        labels={
            'Biaya_Rata': 'Rata-rata Biaya ($)',
            'Tingkat_Pemulihan': 'Tingkat Pemulihan (%)',
            'Masa_Rawat_Rata': 'Rata-rata Masa Rawat (hari)'
        },
        hover_data=['Kondisi_Medis', 'Biaya_Rata', 'Tingkat_Pemulihan', 'Masa_Rawat_Rata']
    )
    st.plotly_chart(fig_cost_recovery, use_container_width=True)

# ============================================================
# 3️⃣ DEMOGRAFI PASIEN
# ============================================================
elif analysis_focus == "Demografi Pasien":
    st.markdown('<div class="section-title">Analisis Demografi Pasien</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Age distribution
        st.subheader("Distribusi Usia Pasien")
        
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
        st.subheader("Distribusi Jenis Kelamin")
        gender_counts = filtered_df['gender'].value_counts()
        
        fig_gender = px.pie(
            values=gender_counts.values,
            names=gender_counts.index,
            title="Proporsi Jenis Kelamin Pasien",
            color_discrete_sequence=['#4A90E2', '#FF6B9D']
        )
        fig_gender.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_gender, use_container_width=True)
    
    # Gender by condition
    st.subheader("Kondisi Medis berdasarkan Jenis Kelamin")
    gender_condition = filtered_df.groupby(['medical_condition', 'gender']).size().reset_index(name='jumlah')
    top_conditions = gender_condition.groupby('medical_condition')['jumlah'].sum().nlargest(6).index
    gender_condition_top = gender_condition[gender_condition['medical_condition'].isin(top_conditions)]
    
    fig_gender_condition = px.bar(
        gender_condition_top,
        x='medical_condition',
        y='jumlah',
        color='gender',
        title="6 Kondisi Medis Terbanyak berdasarkan Jenis Kelamin",
        labels={'jumlah': 'Jumlah Pasien', 'medical_condition': 'Kondisi Medis'},
        color_discrete_sequence=['#FF6B9D', '#4A90E2'],
        barmode='group'
    )
    st.plotly_chart(fig_gender_condition, use_container_width=True)
    
    # Blood type distribution
    st.subheader("Distribusi Golongan Darah")
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
    
    # Hospital demographics
    st.subheader("Distribusi Pasien per Rumah Sakit")
    
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
        title=f"8 Rumah Sakit dengan Volume Pasien Tertinggi ({percentage_of_total:.1f}% dari {total_patients:,} total pasien)",
        labels={'jumlah': 'Jumlah Pasien', 'hospital': 'Rumah Sakit'},
        color_discrete_sequence=['#FF6B9D', '#4A90E2'],
        barmode='group'
    )
    
    # Add subtitle with context
    st.caption(f"Menampilkan 8 rumah sakit teratas dari total {total_hospitals} rumah sakit")
    st.plotly_chart(fig_hospital_demo, use_container_width=True)
""")
