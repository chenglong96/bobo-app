import streamlit as st

# --- PAGE SETUP ---
about_page = st.Page(
    page="views/about.py",
    title="About this page",
    icon=":material/account_circle:",
    default=True,
)
project_1_page = st.Page(
    page="views/torn_dashboard.py",
    title="Torn Dashboard",
    icon=":material/bar_chart:",
)
project_2_page = st.Page(
    page="views/comparison_dashboard.py",
    title="Torn Dashboard 2",
    icon=":material/bar_chart:", 
)
project_3_page = st.Page(
    page="views/machinelearning_stats_predictor.py",
    title="Machine Learning",
    icon=":material/bar_chart:", 
)


# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
#pg = st.navigation(pages = [about_page, project_1_page, project_2_page, project_3_page])

# --- NAVIGATION SETUP [WITH SECTIONS] ---
pg = st.navigation(
    {
        "Info":[about_page],
        "Projects": [project_1_page,project_2_page,project_3_page]
    }
)
# --- SHARED ON ALL PAGES ---
st.logo("assets/Ducky.png")
st.sidebar.text("Made for fun by Maple ")


# --- RUN NAVIGATION ---
pg.run()
