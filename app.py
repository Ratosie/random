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
    df = pd.read_csv('cleaned_data.csv')
    
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
st.markdown('<div class="main-title">🏥 Hospital Health Dashboard</div>', unsafe_allow_html=True)
st.markdown("### Understanding healthcare through clear visual stories")

# Sidebar filters
st.sidebar.header("🎛️ Customize Your View")
st.sidebar.markdown("Adjust to see different healthcare stories")

year_filter = st.sidebar.selectbox(
    "Select Time Period",
    options=["All Years"] + sorted(df['date_of_admission'].dt.year.dropna().unique().tolist())
)

condition_filter = st.sidebar.selectbox(
    "Focus on Health Condition",
    options=["All Conditions"] + sorted(df['medical_condition'].unique().tolist())
)

age_range = st.sidebar.slider(
    "Age Range",
    min_value=int(df['age'].min()),
    max_value=int(df['age'].max()),
    value=(13, 89)
)

# Apply filters
filtered_df = df.copy()
if year_filter != "All Years":
    filtered_df = filtered_df[filtered_df['date_of_admission'].dt.year == year_filter]
if condition_filter != "All Conditions":
    filtered_df = filtered_df[filtered_df['medical_condition'] == condition_filter]
filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]

# Quick Stats
st.markdown("## 📊 Quick Health Snapshot")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Patients", f"{len(filtered_df):,}")

with col2:
    avg_stay = filtered_df['length_of_stay'].mean()
    delta_color = "normal" if avg_stay < 7 else "inverse"
    st.metric("Average Stay", f"{avg_stay:.1f} days", delta_color=delta_color)

with col3:
    avg_bill = filtered_df['billing_amount'].mean()
    delta_color = "normal" if avg_bill < 20000 else "inverse"
    st.metric("Average Cost", f"${avg_bill:,.0f}", delta_color=delta_color)

with col4:
    recovery_rate = (filtered_df['test_results'] == 'Normal').mean() * 100
    delta_color = "normal" if recovery_rate > 60 else "inverse"
    st.metric("Recovery Rate", f"{recovery_rate:.1f}%", delta_color=delta_color)

# 1. AGE DISTRIBUTION
st.markdown('<div class="section-title">👥 Patient Age Distribution</div>', unsafe_allow_html=True)

# Create age groups for better visualization
age_bins = [0, 18, 35, 50, 65, 100]
age_labels = ['Children (0-18)', 'Young Adults (19-35)', 'Adults (36-50)', 'Senior (51-65)', 'Elderly (65+)']
filtered_df['age_group'] = pd.cut(filtered_df['age'], bins=age_bins, labels=age_labels)

age_counts = filtered_df['age_group'].value_counts()

fig_age = px.bar(
    x=age_counts.index,
    y=age_counts.values,
    title="Patient Age Groups - Who Gets Healthcare?",
    labels={'x': 'Age Group', 'y': 'Number of Patients'},
    color=age_counts.index,
    color_discrete_sequence=['#3498DB', '#9B59B6', '#2ECC71', '#F39C12', '#E74C3C']
)
fig_age.update_layout(
    showlegend=True,
    legend_title="Age Groups"
)
st.plotly_chart(fig_age, use_container_width=True)

# 2. GENDER DISTRIBUTION
st.markdown('<div class="section-title">🚻 Patient Gender Distribution</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    gender_counts = filtered_df['gender'].value_counts()
    fig_gender = px.pie(
        values=gender_counts.values,
        names=gender_counts.index,
        title="Patient Gender Split",
        color_discrete_sequence=['#FF6B9D', '#4A90E2'],
        hover_data=[gender_counts.values],
        labels={'value': 'Patients'}
    )
    fig_gender.update_traces(
        textinfo='percent+label',
        hovertemplate="<b>%{label}</b><br>Patients: %{value}<br>Percentage: %{percent}"
    )
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    # Gender by condition - CHANGED: Two bars per condition (one for each gender)
    gender_condition = filtered_df.groupby(['medical_condition', 'gender']).size().reset_index(name='count')
    top_conditions_gender = gender_condition.groupby('medical_condition')['count'].sum().nlargest(5).index
    gender_condition_top = gender_condition[gender_condition['medical_condition'].isin(top_conditions_gender)]
    
    fig_gender_condition = px.bar(
        gender_condition_top,
        x='medical_condition',
        y='count',
        color='gender',
        title="Top Conditions by Gender",
        labels={'count': 'Number of Patients', 'medical_condition': 'Health Condition'},
        color_discrete_sequence=['#FF6B9D', '#4A90E2'],
        barmode='group'  # This creates grouped bars (two bars per condition)
    )
    fig_gender_condition.update_layout(showlegend=True, legend_title="Gender")
    st.plotly_chart(fig_gender_condition, use_container_width=True)

# 3. HEALTH CONDITIONS
st.markdown('<div class="section-title">🩺 Most Common Health Conditions</div>', unsafe_allow_html=True)

top_conditions = filtered_df['medical_condition'].value_counts().head(10)

fig_conditions = px.bar(
    x=top_conditions.values,
    y=top_conditions.index,
    orientation='h',
    title="Top 10 Health Conditions Treated",
    labels={'x': 'Number of Patients', 'y': 'Health Condition'},
    color=top_conditions.values,
    color_continuous_scale='Viridis'
)
fig_conditions.update_layout(
    showlegend=False,
    coloraxis_colorbar=dict(title="Patients")
)
st.plotly_chart(fig_conditions, use_container_width=True)

# 4. HOSPITAL VISIT TYPES
st.markdown('<div class="section-title">🏥 Hospital Visit Patterns</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    admission_counts = filtered_df['admission_type'].value_counts()
    fig_admission = px.pie(
        values=admission_counts.values,
        names=admission_counts.index,
        title="Types of Hospital Visits",
        color_discrete_sequence=['#2ECC71', '#F39C12', '#E74C3C'],
        hover_data=[admission_counts.values],
        labels={'value': 'Patients'}
    )
    fig_admission.update_traces(
        textinfo='percent+label',
        hovertemplate="<b>%{label}</b><br>Patients: %{value}<br>Percentage: %{percent}"
    )
    st.plotly_chart(fig_admission, use_container_width=True)

with col2:
    # Length of stay distribution
    fig_stay = px.box(
        filtered_df, 
        y='length_of_stay',
        title="Hospital Stay Duration",
        labels={'length_of_stay': 'Days in Hospital'},
        color_discrete_sequence=['#3498DB']
    )
    fig_stay.update_layout(showlegend=False)
    st.plotly_chart(fig_stay, use_container_width=True)

# 5. TREATMENT OUTCOMES
st.markdown('<div class="section-title">💪 Treatment Results & Recovery</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    results = filtered_df['test_results'].value_counts()
    fig_results = px.pie(
        values=results.values,
        names=results.index,
        title="Patient Test Results",
        color_discrete_sequence=['#E74C3C', '#2ECC71', '#F39C12'],
        hover_data=[results.values],
        labels={'value': 'Patients'}
    )
    fig_results.update_traces(
        textinfo='percent+label',
        hovertemplate="<b>%{label}</b><br>Patients: %{value}<br>Percentage: %{percent}"
    )
    st.plotly_chart(fig_results, use_container_width=True)

with col2:
    top_meds = filtered_df['medication'].value_counts().head(8)
    fig_meds = px.bar(
        x=top_meds.index,
        y=top_meds.values,
        title="Most Common Medications",
        labels={'x': 'Medication', 'y': 'Patients Treated'},
        color=top_meds.values,
        color_continuous_scale='Blues'
    )
    fig_meds.update_layout(
        showlegend=False,
        coloraxis_colorbar=dict(title="Patients")
    )
    st.plotly_chart(fig_meds, use_container_width=True)

# 6. HEALTHCARE COSTS
st.markdown('<div class="section-title">💰 Healthcare Costs Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fig_cost = px.histogram(
        filtered_df,
        x='billing_amount',
        nbins=20,
        title="Medical Bill Distribution",
        labels={'billing_amount': 'Medical Bill Amount ($)', 'count': 'Number of Patients'},
        color_discrete_sequence=['#E67E22']
    )
    fig_cost.update_layout(showlegend=False)
    st.plotly_chart(fig_cost, use_container_width=True)

with col2:
    insurance_counts = filtered_df['insurance_provider'].value_counts().head(6)
    fig_insurance = px.pie(
        values=insurance_counts.values,
        names=insurance_counts.index,
        title="Insurance Provider Coverage",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hover_data=[insurance_counts.values],
        labels={'value': 'Patients'}
    )
    fig_insurance.update_traces(
        textinfo='percent+label',
        hovertemplate="<b>%{label}</b><br>Patients: %{value}<br>Percentage: %{percent}"
    )
    st.plotly_chart(fig_insurance, use_container_width=True)

# 7. SEASONAL TRENDS
st.markdown('<div class="section-title">📅 Hospital Visits Throughout the Year</div>', unsafe_allow_html=True)

monthly_trend = filtered_df['date_of_admission'].dt.month.value_counts().sort_index()
all_months = pd.Series(range(1, 13), index=range(1, 13))
monthly_trend_complete = all_months.map(monthly_trend).fillna(0)

month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

fig_trend = px.line(
    x=month_names,
    y=monthly_trend_complete.values,
    title="Monthly Hospital Visit Patterns",
    labels={'x': 'Month', 'y': 'Number of Patients'},
    markers=True
)
fig_trend.update_traces(
    line=dict(width=3, color='#3498DB'),
    marker=dict(size=8, color='#E74C3C')
)
fig_trend.update_layout(showlegend=False)
st.plotly_chart(fig_trend, use_container_width=True)

# 8. RECOVERY RATES BY CONDITION
st.markdown('<div class="section-title">📈 Recovery Success by Health Condition</div>', unsafe_allow_html=True)

recovery_by_condition = filtered_df.groupby('medical_condition')['test_results'].apply(
    lambda x: (x == 'Normal').mean() * 100
).sort_values(ascending=False).head(12)

fig_recovery = px.bar(
    x=recovery_by_condition.index,
    y=recovery_by_condition.values,
    title="Recovery Rates for Different Health Conditions",
    labels={'x': 'Health Condition', 'y': 'Recovery Rate (%)'},
    color=recovery_by_condition.values,
    color_continuous_scale='RdYlGn'
)
fig_recovery.update_layout(
    showlegend=False,
    coloraxis_colorbar=dict(title="Recovery %")
)
st.plotly_chart(fig_recovery, use_container_width=True)

# 9. BLOOD TYPE DISTRIBUTION
st.markdown('<div class="section-title">🩸 Patient Blood Types</div>', unsafe_allow_html=True)

blood_counts = filtered_df['blood_type'].value_counts()
fig_blood = px.bar(
    x=blood_counts.index,
    y=blood_counts.values,
    title="Blood Type Distribution Among Patients",
    labels={'x': 'Blood Type', 'y': 'Number of Patients'},
    color=blood_counts.index,
    color_discrete_sequence=px.colors.qualitative.Bold
)
fig_blood.update_layout(showlegend=True, legend_title="Blood Type")
st.plotly_chart(fig_blood, use_container_width=True)

# 10. CONDITION & COST RELATIONSHIP
st.markdown('<div class="section-title">🔍 Condition Severity vs Treatment Cost</div>', unsafe_allow_html=True)

condition_costs = filtered_df.groupby('medical_condition').agg({
    'billing_amount': 'mean',
    'length_of_stay': 'mean',
    'test_results': lambda x: (x == 'Normal').mean() * 100
}).round(2).reset_index()
condition_costs.columns = ['Condition', 'Avg_Cost', 'Avg_Stay', 'Recovery_Rate']

# Take top 8 conditions by frequency
top_conditions_list = filtered_df['medical_condition'].value_counts().head(8).index
condition_costs_top = condition_costs[condition_costs['Condition'].isin(top_conditions_list)]

fig_condition_cost = px.scatter(
    condition_costs_top,
    x='Avg_Cost',
    y='Recovery_Rate',
    size='Avg_Stay',
    color='Condition',
    title="Treatment Cost vs Recovery Rate",
    labels={
        'Avg_Cost': 'Average Treatment Cost ($)',
        'Recovery_Rate': 'Recovery Rate (%)',
        'Avg_Stay': 'Average Stay (days)',
        'Condition': 'Health Condition'
    },
    hover_data=['Condition', 'Avg_Cost', 'Recovery_Rate', 'Avg_Stay']
)
fig_condition_cost.update_layout(showlegend=True, legend_title="Health Condition")
st.plotly_chart(fig_condition_cost, use_container_width=True)

# Key Insights
st.markdown("---")
st.markdown("## 💡 Key Insights at a Glance")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"**Most Common Condition**\n\n{filtered_df['medical_condition'].value_counts().index[0]}")

with col2:
    st.success(f"**Best Recovery Rate**\n\n{recovery_by_condition.index[0]} ({recovery_by_condition.iloc[0]:.0f}%)")

with col3:
    busiest_month = monthly_trend.idxmax()
    month_name = month_names[busiest_month-1]
    st.warning(f"**Busiest Month**\n\n{month_name}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📊 Chart Guide
- **Hover** over charts for details
- **Click** legend items to filter
- **Colors** show different categories
- **Size** often shows importance
""")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7F8C8D;">
    <p><strong>Interactive Healthcare Dashboard</strong> - Hover over charts for detailed information</p>
    <p>Each chart tells a different part of the healthcare story</p>
</div>
""", unsafe_allow_html=True)


