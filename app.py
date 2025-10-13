import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

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

# Key Metrics
st.markdown("## 📊 Quick Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Patients", f"{len(filtered_df):,}")

with col2:
    avg_stay = filtered_df['length_of_stay'].mean()
    st.metric("Avg Hospital Stay", f"{avg_stay:.1f} days")

with col3:
    avg_bill = filtered_df['billing_amount'].mean()
    st.metric("Avg Medical Bill", f"${avg_bill:,.0f}")

with col4:
    recovery_rate = (filtered_df['test_results'] == 'Normal').mean() * 100
    st.metric("Positive Outcomes", f"{recovery_rate:.1f}%")

# Story 1: Patient Demographics
st.markdown("---")
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 👥 Patient Stories: Who Visits Our Hospital?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Age Distribution")
    st.bar_chart(filtered_df['age'].value_counts().sort_index())
    st.markdown("""
    **What this tells us:** 
    - Different age groups face different health challenges
    - Healthcare needs change throughout life
    """)

with col2:
    st.markdown("### Most Common Conditions")
    top_conditions = filtered_df['medical_condition'].value_counts().head(8)
    st.dataframe(top_conditions, use_container_width=True)
    st.markdown("""
    **What this tells us:**
    - Some conditions are more common than others
    - Early detection can make a big difference
    """)

st.markdown('</div>', unsafe_allow_html=True)

# Story 2: Hospital Experience
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 🏥 The Hospital Journey: What to Expect")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### How Patients Arrive")
    admission_counts = filtered_df['admission_type'].value_counts()
    st.dataframe(admission_counts, use_container_width=True)
    st.markdown("""
    **Understanding your visit:**
    - **Emergency**: Unexpected, urgent care needed
    - **Urgent**: Soon, but can wait a bit
    - **Elective**: Planned in advance
    """)

with col2:
    st.markdown("### Hospital Stay Duration")
    st.metric("Average Stay", f"{filtered_df['length_of_stay'].mean():.1f} days")
    st.metric("Shortest Stay", f"{filtered_df['length_of_stay'].min()} days")
    st.metric("Longest Stay", f"{filtered_df['length_of_stay'].max()} days")
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
    st.markdown("### Test Results")
    results = filtered_df['test_results'].value_counts()
    
    # Create a simple progress bar visualization
    for result, count in results.items():
        total = len(filtered_df)
        percentage = (count / total) * 100
        if result == 'Normal':
            color = '🟢'
        elif result == 'Abnormal':
            color = '🔴'
        else:
            color = '🟡'
        
        st.write(f"{color} **{result}**: {count} patients ({percentage:.1f}%)")
        st.progress(percentage/100)

with col2:
    st.markdown("### Common Treatments")
    top_meds = filtered_df['medication'].value_counts().head(6)
    for med, count in top_meds.items():
        st.write(f"💊 **{med}**: {count} patients")

st.markdown('</div>', unsafe_allow_html=True)

# Story 4: Financial Side
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 💰 Understanding Healthcare Costs")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Cost Distribution")
    st.metric("Average Bill", f"${filtered_df['billing_amount'].mean():,.0f}")
    st.metric("Lowest Bill", f"${filtered_df['billing_amount'].min():,.0f}")
    st.metric("Highest Bill", f"${filtered_df['billing_amount'].max():,.0f}")
    
    # Simple histogram using st.bar_chart
    cost_ranges = pd.cut(filtered_df['billing_amount'], bins=10)
    cost_dist = cost_ranges.value_counts().sort_index()
    st.bar_chart(cost_dist)

with col2:
    st.markdown("### Insurance Providers")
    insurance_counts = filtered_df['insurance_provider'].value_counts().head(6)
    st.dataframe(insurance_counts, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Monthly Trends
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 📅 Hospital Visits Through the Year")

# Monthly admissions trend
monthly_trend = filtered_df['date_of_admission'].dt.month.value_counts().sort_index()
st.line_chart(monthly_trend)

st.markdown("""
**Seasonal patterns:**
- Some months see more hospital visits than others
- Weather, holidays, and seasons can affect health
- Being prepared year-round is important
""")
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
### 💡 Helpful Information for Patients

**Remember:** 
- These are general patterns - every patient is unique
- Always consult with healthcare professionals for personal advice
- Early detection and regular check-ups are key to good health

*Data represents patient experiences to help you understand healthcare better.*
""")
