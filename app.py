import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Hospital Health Insights",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_data.csv')
    
    # Clean column names and handle data issues
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Convert dates
    df['date_of_admission'] = pd.to_datetime(df['date_of_admission'], errors='coerce')
    df['discharge_date'] = pd.to_datetime(df['discharge_date'], errors='coerce')
    
    # Calculate length of stay
    df['length_of_stay'] = (df['discharge_date'] - df['date_of_admission']).dt.days
    
    # Clean billing amount (remove negative values)
    df['billing_amount'] = df['billing_amount'].clip(lower=0)
    
    return df

df = load_data()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .story-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🏥 Hospital Health Insights</h1>', unsafe_allow_html=True)
st.markdown("### Understanding healthcare through patient stories")

# Sidebar filters
st.sidebar.header("🔍 Filter the View")
st.sidebar.markdown("Adjust these filters to explore different perspectives")

year_filter = st.sidebar.selectbox(
    "Select Year",
    options=["All Years"] + sorted(df['date_of_admission'].dt.year.dropna().unique().tolist())
)

condition_filter = st.sidebar.selectbox(
    "Medical Condition",
    options=["All Conditions"] + sorted(df['medical_condition'].unique().tolist())
)

age_range = st.sidebar.slider(
    "Age Range",
    min_value=int(df['age'].min()),
    max_value=int(df['age'].max()),
    value=(20, 80)
)

# Apply filters
filtered_df = df.copy()
if year_filter != "All Years":
    filtered_df = filtered_df[filtered_df['date_of_admission'].dt.year == year_filter]
if condition_filter != "All Conditions":
    filtered_df = filtered_df[filtered_df['medical_condition'] == condition_filter]
filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]

# Key Metrics Row
st.markdown("## 📊 Quick Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Patients", 
        f"{len(filtered_df):,}",
        help="Number of patients in current view"
    )

with col2:
    avg_stay = filtered_df['length_of_stay'].mean()
    st.metric(
        "Avg Hospital Stay", 
        f"{avg_stay:.1f} days",
        help="Average time patients spend in hospital"
    )

with col3:
    avg_bill = filtered_df['billing_amount'].mean()
    st.metric(
        "Avg Medical Bill", 
        f"${avg_bill:,.0f}",
        help="Average cost per hospital visit"
    )

with col4:
    recovery_rate = (filtered_df['test_results'] == 'Normal').mean() * 100
    st.metric(
        "Positive Outcomes", 
        f"{recovery_rate:.1f}%",
        help="Percentage of patients with normal test results"
    )

# Main Visualizations - Story-based approach
st.markdown("---")

# Story 1: Who comes to the hospital?
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 👥 Patient Stories: Who Visits Our Hospital?")

col1, col2 = st.columns(2)

with col1:
    # Age distribution with story context
    fig_age = px.histogram(
        filtered_df, 
        x='age', 
        nbins=20,
        title="Patient Ages: From Young Adults to Seniors",
        labels={'age': 'Age', 'count': 'Number of Patients'}
    )
    fig_age.update_layout(
        showlegend=False,
        xaxis_title="Age",
        yaxis_title="Number of Patients"
    )
    st.plotly_chart(fig_age, use_container_width=True)
    
    st.markdown("""
    **What this tells us:** 
    - Different age groups face different health challenges
    - Healthcare needs change throughout life
    """)

with col2:
    # Medical conditions by age group
    condition_counts = filtered_df['medical_condition'].value_counts().head(8)
    fig_conditions = px.bar(
        x=condition_counts.values,
        y=condition_counts.index,
        orientation='h',
        title="Most Common Health Conditions",
        labels={'x': 'Number of Patients', 'y': 'Medical Condition'}
    )
    fig_conditions.update_layout(showlegend=False)
    st.plotly_chart(fig_conditions, use_container_width=True)
    
    st.markdown("""
    **What this tells us:**
    - Some conditions are more common than others
    - Early detection can make a big difference
    """)
st.markdown('</div>', unsafe_allow_html=True)

# Story 2: The Hospital Experience
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 🏥 The Hospital Journey: What to Expect")

col1, col2 = st.columns(2)

with col1:
    # Admission types - emergency vs planned
    admission_counts = filtered_df['admission_type'].value_counts()
    fig_admission = px.pie(
        values=admission_counts.values,
        names=admission_counts.index,
        title="How Patients Arrive: Emergency vs Planned Visits",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_admission, use_container_width=True)
    
    st.markdown("""
    **Understanding your visit:**
    - **Emergency**: Unexpected, urgent care needed
    - **Urgent**: Soon, but can wait a bit
    - **Elective**: Planned in advance
    """)

with col2:
    # Length of stay distribution
    fig_stay = px.box(
        filtered_df, 
        y='length_of_stay',
        title="Typical Hospital Stay Duration",
        labels={'length_of_stay': 'Days in Hospital'}
    )
    fig_stay.update_layout(showlegend=False)
    st.plotly_chart(fig_stay, use_container_width=True)
    
    st.markdown("""
    **Hospital stay facts:**
    - Most stays are relatively short
    - Recovery times vary by condition
    - Every patient's journey is unique
    """)
st.markdown('</div>', unsafe_allow_html=True)

# Story 3: Recovery and Outcomes
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 💪 Recovery Stories: Patient Outcomes")

col1, col2 = st.columns(2)

with col1:
    # Test results - the recovery story
    results = filtered_df['test_results'].value_counts()
    fig_results = px.bar(
        x=results.index,
        y=results.values,
        title="Patient Test Results: The Road to Recovery",
        labels={'x': 'Test Result', 'y': 'Number of Patients'},
        color=results.index,
        color_discrete_map={
            'Normal': '#2ecc71',
            'Abnormal': '#e74c3c', 
            'Inconclusive': '#f39c12'
        }
    )
    st.plotly_chart(fig_results, use_container_width=True)
    
    st.markdown("""
    **Understanding your results:**
    - **Normal**: Great news! Treatment is working
    - **Abnormal**: Needs more attention
    - **Inconclusive**: More tests may be needed
    """)

with col2:
    # Common medications
    top_meds = filtered_df['medication'].value_counts().head(8)
    fig_meds = px.bar(
        x=top_meds.values,
        y=top_meds.index,
        orientation='h',
        title="Most Common Treatments",
        labels={'x': 'Number of Patients', 'y': 'Medication'}
    )
    st.plotly_chart(fig_meds, use_container_width=True)
    
    st.markdown("""
    **Treatment insights:**
    - Different conditions need different approaches
    - Medications help manage symptoms
    - Always follow doctor's instructions
    """)
st.markdown('</div>', unsafe_allow_html=True)

# Story 4: The Financial Side
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 💰 Understanding Healthcare Costs")

col1, col2 = st.columns(2)

with col1:
    # Cost distribution
    fig_cost = px.histogram(
        filtered_df,
        x='billing_amount',
        nbins=20,
        title="Healthcare Costs: What to Expect",
        labels={'billing_amount': 'Medical Bill Amount', 'count': 'Number of Patients'}
    )
    fig_cost.update_layout(showlegend=False)
    st.plotly_chart(fig_cost, use_container_width=True)
    
    st.markdown("""
    **Cost insights:**
    - Healthcare costs vary widely
    - Insurance helps manage expenses
    - Planning ahead can reduce stress
    """)

with col2:
    # Insurance coverage
    insurance_counts = filtered_df['insurance_provider'].value_counts().head(6)
    fig_insurance = px.pie(
        values=insurance_counts.values,
        names=insurance_counts.index,
        title="How Patients Pay for Care",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_insurance, use_container_width=True)
    
    st.markdown("""
    **Insurance facts:**
    - Different providers offer various plans
    - Coverage affects out-of-pocket costs
    - Always verify your benefits
    """)
st.markdown('</div>', unsafe_allow_html=True)

# Monthly Trends Story - FIXED VERSION
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 📅 Hospital Visits Through the Year")

# Create complete monthly data (ensure all 12 months)
monthly_trend = filtered_df['date_of_admission'].dt.month.value_counts().sort_index()

# Ensure we have all 12 months
all_months = pd.Series(range(1, 13), index=range(1, 13))
monthly_trend_complete = all_months.map(monthly_trend).fillna(0)

month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

fig_trend = px.line(
    x=month_names,
    y=monthly_trend_complete.values,
    title="When Do People Need Hospital Care?",
    labels={'x': 'Month', 'y': 'Number of Admissions'},
    markers=True
)
fig_trend.update_traces(line=dict(width=4), marker=dict(size=8))
fig_trend.update_layout(
    xaxis_title="Month",
    yaxis_title="Number of Hospital Visits"
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("""
**Seasonal patterns:**
- Some months see more hospital visits than others
- Weather, holidays, and seasons can affect health
- Being prepared year-round is important
""")
st.markdown('</div>', unsafe_allow_html=True)

# Additional Story: Gender and Blood Type
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 👨‍👩‍👧‍👦 More About Our Patients")

col1, col2 = st.columns(2)

with col1:
    # Gender distribution
    gender_counts = filtered_df['gender'].value_counts()
    fig_gender = px.pie(
        values=gender_counts.values,
        names=gender_counts.index,
        title="Patient Gender Distribution",
        color_discrete_sequence=['#FF9999', '#66B2FF']
    )
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    # Blood type distribution
    blood_counts = filtered_df['blood_type'].value_counts()
    fig_blood = px.bar(
        x=blood_counts.index,
        y=blood_counts.values,
        title="Patient Blood Types",
        labels={'x': 'Blood Type', 'y': 'Number of Patients'},
        color=blood_counts.index
    )
    st.plotly_chart(fig_blood, use_container_width=True)

st.markdown("""
**Health diversity:**
- Different genders may have different health needs
- Blood types are important for medical treatments
- Everyone's health journey is unique
""")
st.markdown('</div>', unsafe_allow_html=True)

# Success Stories Section
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 🌟 Health Success Stories")

col1, col2, col3 = st.columns(3)

with col1:
    # Quick recovery stories
    quick_recovery = filtered_df[filtered_df['length_of_stay'] <= 3].shape[0]
    st.metric("Quick Recoveries", f"{quick_recovery:,}", "Short hospital stays")

with col2:
    # Normal test results
    normal_tests = (filtered_df['test_results'] == 'Normal').sum()
    st.metric("Positive Outcomes", f"{normal_tests:,}", "Good test results")

with col3:
    # Planned visits (less stressful)
    planned_visits = (filtered_df['admission_type'] == 'Elective').sum()
    st.metric("Planned Visits", f"{planned_visits:,}", "Scheduled care")

st.markdown("""
**Celebrating health wins:**
- Many patients have short, successful hospital stays
- Positive outcomes are common
- Planning ahead leads to better experiences
""")
st.markdown('</div>', unsafe_allow_html=True)

# Footer with helpful information
st.markdown("---")
st.markdown("""
### 💡 Helpful Information for Patients

**Remember:** 
- These are general patterns - every patient is unique
- Always consult with healthcare professionals for personal advice
- Early detection and regular check-ups are key to good health
- Your healthcare team is here to support your journey to wellness

*Data represents real patient experiences to help you understand healthcare better.*
""")

# Data source and disclaimer
st.sidebar.markdown("---")
st.sidebar.markdown("""
**About This Dashboard**
This shows general healthcare patterns to help you understand:
- Common health conditions
- Typical hospital experiences  
- Recovery journeys
- Healthcare costs

*For personal medical advice, please consult your doctor.*
""")

# Add some sample patient stories in the sidebar for extra engagement
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Patient Story Examples")
st.sidebar.markdown("""
**Maria, 45**
- Condition: Hypertension  
- Stay: 2 days
- Outcome: Normal results
- *"Regular check-ups helped catch it early"*

**James, 68**
- Condition: Arthritis
- Stay: 5 days  
- Outcome: Improved mobility
- *"Physical therapy made a big difference"*
""")