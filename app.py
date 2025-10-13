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
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
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
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Patients", f"{len(filtered_df):,}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    avg_stay = filtered_df['length_of_stay'].mean()
    st.metric("Avg Hospital Stay", f"{avg_stay:.1f} days")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    avg_bill = filtered_df['billing_amount'].mean()
    st.metric("Avg Medical Bill", f"${avg_bill:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    recovery_rate = (filtered_df['test_results'] == 'Normal').mean() * 100
    st.metric("Positive Outcomes", f"{recovery_rate:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)

# Story 1: Patient Demographics
st.markdown("---")
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 👥 Patient Stories: Who Visits Our Hospital?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Age Distribution")
    
    # Create age groups for better visualization
    age_bins = [0, 18, 30, 45, 60, 75, 100]
    age_labels = ['0-18', '19-30', '31-45', '46-60', '61-75', '75+']
    filtered_df['age_group'] = pd.cut(filtered_df['age'], bins=age_bins, labels=age_labels)
    
    age_counts = filtered_df['age_group'].value_counts().sort_index()
    
    # Display age distribution as text with emojis
    for age_group, count in age_counts.items():
        percentage = (count / len(filtered_df)) * 100
        if age_group in ['0-18', '19-30']:
            emoji = "👦"
        elif age_group in ['31-45', '46-60']:
            emoji = "👨"
        else:
            emoji = "👴"
        
        st.write(f"{emoji} **{age_group}**: {count} patients ({percentage:.1f}%)")
        st.progress(percentage/100)

with col2:
    st.markdown("### Most Common Conditions")
    top_conditions = filtered_df['medical_condition'].value_counts().head(10)
    
    for condition, count in top_conditions.items():
        percentage = (count / len(filtered_df)) * 100
        st.write(f"🩺 **{condition}**: {count} patients ({percentage:.1f}%)")
        st.progress(percentage/100)

st.markdown('</div>', unsafe_allow_html=True)

# Story 2: Hospital Experience
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 🏥 The Hospital Journey: What to Expect")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### How Patients Arrive")
    admission_counts = filtered_df['admission_type'].value_counts()
    
    for admission_type, count in admission_counts.items():
        percentage = (count / len(filtered_df)) * 100
        if admission_type == 'Emergency':
            emoji = "🚨"
        elif admission_type == 'Urgent':
            emoji = "⚠️"
        else:
            emoji = "📅"
        
        st.write(f"{emoji} **{admission_type}**: {count} patients ({percentage:.1f}%)")
        st.progress(percentage/100)

with col2:
    st.markdown("### Hospital Stay Duration")
    
    # Calculate stay statistics
    avg_stay = filtered_df['length_of_stay'].mean()
    min_stay = filtered_df['length_of_stay'].min()
    max_stay = filtered_df['length_of_stay'].max()
    
    col2a, col2b, col2c = st.columns(3)
    with col2a:
        st.metric("Average Stay", f"{avg_stay:.1f} days")
    with col2b:
        st.metric("Shortest Stay", f"{min_stay} days")
    with col2c:
        st.metric("Longest Stay", f"{max_stay} days")
    
    # Show stay distribution in categories
    stay_bins = [0, 1, 3, 7, 14, 30, 1000]
    stay_labels = ['1 day', '2-3 days', '4-7 days', '1-2 weeks', '2-4 weeks', '1 month+']
    filtered_df['stay_category'] = pd.cut(filtered_df['length_of_stay'], bins=stay_bins, labels=stay_labels)
    
    stay_counts = filtered_df['stay_category'].value_counts().sort_index()
    
    for stay_cat, count in stay_counts.items():
        if count > 0:  # Only show categories that have patients
            percentage = (count / len(filtered_df)) * 100
            st.write(f"⏱️ **{stay_cat}**: {count} patients ({percentage:.1f}%)")
            st.progress(percentage/100)

st.markdown('</div>', unsafe_allow_html=True)

# Story 3: Recovery and Outcomes
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 💪 Recovery Stories: Patient Outcomes")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Test Results")
    results = filtered_df['test_results'].value_counts()
    
    for result, count in results.items():
        total = len(filtered_df)
        percentage = (count / total) * 100
        if result == 'Normal':
            emoji = "✅"
            color = "green"
        elif result == 'Abnormal':
            emoji = "⚠️"
            color = "orange"
        else:
            emoji = "❓"
            color = "gray"
        
        st.write(f"{emoji} **{result}**: {count} patients ({percentage:.1f}%)")
        st.progress(percentage/100)

with col2:
    st.markdown("### Common Treatments")
    top_meds = filtered_df['medication'].value_counts().head(8)
    
    for med, count in top_meds.items():
        percentage = (count / len(filtered_df)) * 100
        st.write(f"💊 **{med}**: {count} patients ({percentage:.1f}%)")
        st.progress(percentage/100)

st.markdown('</div>', unsafe_allow_html=True)

# Story 4: Financial Side
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 💰 Understanding Healthcare Costs")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Cost Distribution")
    
    # Calculate cost statistics
    avg_cost = filtered_df['billing_amount'].mean()
    min_cost = filtered_df['billing_amount'].min()
    max_cost = filtered_df['billing_amount'].max()
    
    col1a, col1b, col1c = st.columns(3)
    with col1a:
        st.metric("Average Bill", f"${avg_cost:,.0f}")
    with col1b:
        st.metric("Lowest Bill", f"${min_cost:,.0f}")
    with col1c:
        st.metric("Highest Bill", f"${max_cost:,.0f}")
    
    # Show cost distribution in ranges
    cost_bins = [0, 5000, 10000, 20000, 30000, 50000, 1000000]
    cost_labels = ['<$5K', '$5-10K', '$10-20K', '$20-30K', '$30-50K', '$50K+']
    filtered_df['cost_range'] = pd.cut(filtered_df['billing_amount'], bins=cost_bins, labels=cost_labels)
    
    cost_counts = filtered_df['cost_range'].value_counts().sort_index()
    
    for cost_range, count in cost_counts.items():
        if count > 0:
            percentage = (count / len(filtered_df)) * 100
            st.write(f"💰 **{cost_range}**: {count} patients ({percentage:.1f}%)")
            st.progress(percentage/100)

with col2:
    st.markdown("### Insurance Providers")
    insurance_counts = filtered_df['insurance_provider'].value_counts().head(8)
    
    for insurance, count in insurance_counts.items():
        percentage = (count / len(filtered_df)) * 100
        st.write(f"🏢 **{insurance}**: {count} patients ({percentage:.1f}%)")
        st.progress(percentage/100)

st.markdown('</div>', unsafe_allow_html=True)

# Monthly Trends
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 📅 Hospital Visits Through the Year")

# Monthly admissions trend
monthly_trend = filtered_df['date_of_admission'].dt.month.value_counts().sort_index()

# Ensure we have all 12 months
all_months = list(range(1, 13))
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Create a simple text-based monthly view
st.markdown("### Monthly Patient Visits")

for month_num, month_name in zip(all_months, month_names):
    count = monthly_trend.get(month_num, 0)
    max_count = monthly_trend.max() if len(monthly_trend) > 0 else 1
    bar_length = int((count / max_count) * 20)  # Scale to 20 characters
    
    if count > 0:
        percentage = (count / len(filtered_df)) * 100
        bar = "█" * bar_length
        st.write(f"**{month_name}**: {bar} {count} patients ({percentage:.1f}%)")
    else:
        st.write(f"**{month_name}**: (no patients)")

st.markdown("""
**Seasonal patterns:**
- Some months see more hospital visits than others
- Weather, holidays, and seasons can affect health
- Being prepared year-round is important
""")
st.markdown('</div>', unsafe_allow_html=True)

# Additional Insights
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown("## 🌟 Quick Health Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Gender Distribution")
    gender_counts = filtered_df['gender'].value_counts()
    for gender, count in gender_counts.items():
        percentage = (count / len(filtered_df)) * 100
        st.write(f"👤 **{gender}**: {count} ({percentage:.1f}%)")

with col2:
    st.markdown("### Blood Types")
    blood_counts = filtered_df['blood_type'].value_counts().head(6)
    for blood_type, count in blood_counts.items():
        percentage = (count / len(filtered_df)) * 100
        st.write(f"🩸 **{blood_type}**: {count} ({percentage:.1f}%)")

with col3:
    st.markdown("### Room Usage")
    room_counts = filtered_df['room_number'].value_counts().head(5)
    st.write("Most used rooms:")
    for room, count in room_counts.items():
        st.write(f"🚪 **Room {room}**: {count} patients")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
### 💡 Helpful Information for Patients

**Remember:** 
- These are general patterns - every patient is unique
- Always consult with healthcare professionals for personal advice
- Early detection and regular check-ups are key to good health
- Your healthcare team is here to support your journey to wellness

*Data represents patient experiences to help you understand healthcare better.*
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
