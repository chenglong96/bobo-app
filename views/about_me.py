import streamlit as st


# --- HERO SECTION ---
col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
with col1:
    st.image("./assets/Hello.png", width=230)

with col2:
    st.title("Froggo", anchor=False)
    st.write(
        "Data Analyst, creating dashboards that helps data-driven decision-making."
    )


# --- EXPERIENCE & QUALIFICATIONS ---
st.write("\n")
st.subheader("Experience & Qualifications", anchor=False)
st.write(
    """
    - Years experience extracting actionable insights from data
    - Strong hands-on experience and knowledge in Python and Excel
    - Utilise automation to improves efficiency by streamlining processes 
    - Good understanding of statistical principles and their respective applications
    - Excellent team-player and displaying a strong sense of initiative on tasks
    """
)

# --- SKILLS ---
st.write("\n")
st.subheader("Hard Skills", anchor=False)
st.write(
    """
    - Programming: Python (Scikit-learn, Pandas, matlibplot), Javascript, SQL, VBA, DAX
    - Data Visualization: PowerBi, MS Excel, Plotly, Matlibplot
    - Modeling: Logistic regression, linear regression, decision trees, random forest
    - Databases: Postgres, MySQL
    """
)