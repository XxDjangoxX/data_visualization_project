# -------------------------------
# 📦 Imports and Config
# -------------------------------
import streamlit as st
import pandas as pd
import joblib
import plotly.express as px

# Set Page Config
st.set_page_config(
    page_title="Job Search Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# 🚀 Load Data and Models
# -------------------------------
@st.cache_resource
def load_data():
    return pd.read_pickle('final_df.pkl')

# Load
try:
    df_final = load_data()
except Exception as e:
    st.error(f"Error loading files: {e}")
    st.stop()

# -------------------------------
# 🚀 Main App Layout
# -------------------------------
st.title("🚀 Job Search Assistant")
st.write("Find job postings based on your skills instantly!")

tab1, tab2 = st.tabs(["🔎 Job Search", "📊 Insights"])

# -------------------------------
# 🔎 Job Search Tab
# -------------------------------
with tab1:
    # --- Sidebar Toggle ---
    show_sidebar = st.checkbox("🔎 Show Advanced Filters")

    if show_sidebar:
        with st.sidebar:
            st.header("🔎 Filters")

            city_options = ["All"] + sorted(df_final['city'].dropna().unique().tolist())
            selected_city = st.selectbox("Select a City:", options=city_options)

            category_options = ["All"] + sorted(df_final['job_category'].dropna().unique().tolist())
            selected_category = st.selectbox("Select a Job Category:", options=category_options)
    else:
        selected_city = "All"
        selected_category = "All"

    skill_query = st.text_input(
        "Search by Skill:",
        placeholder="e.g., Python, SQL, Sales...",
        help="Type a skill to find matching jobs.",
        key="skill_query_box"
    )

    # Filter DataFrame
    filtered_df = df_final.copy()

    if selected_city != "All":
        filtered_df = filtered_df[filtered_df['city'] == selected_city]

    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['job_category'] == selected_category]

    if skill_query:
        filtered_df = filtered_df[filtered_df['skills_text_cleaned'].str.contains(skill_query, case=False, na=False)]

    # Display Results
    if not filtered_df.empty:
        st.success(f"✅ Found {len(filtered_df)} matching jobs! Showing top 20:")

        for _, row in filtered_df.head(20).iterrows():
            with st.container():
                position = row['position_name'] if pd.notna(row['position_name']) else "Unknown Position"
                city = row['city'] if pd.notna(row['city']) else "Not specified"
                state = row['state'] if pd.notna(row['state']) else ""
                category = row['job_category'] if pd.notna(row['job_category']) else "Not specified"
                url = row['url'] if pd.notna(row['url']) else "#"

                st.markdown(f"""
                    ### {position.strip('"')}
                    **City/State:** {city}, {state}  
                    **Job Category:** {category}  
                    [🔗 View Job Posting]({url})
                    """, unsafe_allow_html=True)
                st.markdown("---")
    else:
        st.warning("⚠️ No matching jobs found. Try another skill!")

    st.markdown("---")
    st.markdown("<h6 style='text-align: center; color: gray;'>Powered by 🤖 Machine Learning & 💻 NLP</h6>", unsafe_allow_html=True)

# -------------------------------
# 📊 Insights Tab
# -------------------------------
with tab2:
    st.header("📊 Job Market Insights")

    st.subheader("Top 10 Skills in Demand")
    try:
        all_skills = df_final['core_skills'].dropna().explode().str.lower()
        top_skills = all_skills.value_counts().head(10)

        fig = px.bar(
            top_skills,
            x=top_skills.values,
            y=top_skills.index,
            orientation='h',
            labels={'x': 'Number of Jobs', 'y': 'Skill'},
            title="Top 10 Skills by Job Postings",
            color_discrete_sequence=['#636EFA']
        )
        fig.update_layout(template='plotly_white', height=500, width=800)
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error plotting top skills: {e}")

    st.subheader("Top 10 Hiring Cities (excluding Unknown)")
    try:
        city_counts = df_final['city'].fillna('Unknown').str.strip()
        city_counts = city_counts.replace('', 'Unknown')
        city_counts = city_counts.str.title().value_counts()

        unknown_count = city_counts.get('Unknown', 0)
        city_counts_no_unknown = city_counts.drop('Unknown', errors='ignore')
        top_cities = city_counts_no_unknown.head(10)

        fig2 = px.bar(
            top_cities,
            x=top_cities.values,
            y=top_cities.index,
            orientation='h',
            labels={'x': 'Number of Jobs', 'y': 'City'},
            title="Top 10 Cities by Number of Job Postings",
            color_discrete_sequence=['#EF553B']
        )
        fig2.update_layout(template='plotly_white', height=500, width=800)
        st.plotly_chart(fig2)

        if unknown_count > 0:
            st.info(f"Note: {unknown_count} jobs had an Unknown city.")
    except Exception as e:
        st.error(f"Error plotting top cities: {e}")

    st.subheader("Salary Distribution by Career Level")
    try:
        df_final['salary_cleaned'] = pd.to_numeric(df_final['salary_cleaned'], errors='coerce')
        salary_df = df_final.dropna(subset=['salary_cleaned', 'career_level'])

        fig3 = px.box(
            salary_df,
            x='career_level',
            y='salary_cleaned',
            color='career_level',
            title='Salary Distribution across Career Levels',
            labels={'career_level': 'Career Level', 'salary_cleaned': 'Salary (USD)'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig3.update_layout(template='plotly_white', height=600, width=800)
        st.plotly_chart(fig3)
    except Exception as e:
        st.error(f"Error plotting salary distribution: {e}")

# -------------------------------
# 🚀 End of File
# -------------------------------
