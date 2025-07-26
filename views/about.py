import streamlit as st


# --- HERO SECTION ---
col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
with col1:
    st.image("./assets/Hello.png", width=230)

with col2:
    st.title("Froggo", anchor=False)
    st.write(
        "Hi everyone, this is just a prototype dashboard website on Torn Rank War factions and give some insights on them"
    )


st.write("\n")
st.subheader("Torn Dashboard", anchor=False)
st.write(
    """
        - Torn Dashboard is to show the list of Factions in rank war and their rank and all their informations
        - There are 2 Tabs to it. one being the overview of the factions, and the other shows the stats on a member level
        - on the Sidebar, there are filters that can be toggle or selected around to focus on what to view
    """
)

st.write("\n")
st.subheader("Torn Dashboard 2", anchor=False)
st.write(
    """
        - Torn Dashboard 2 is mainly just a tornado chart and the toggling of 2 factions to compare between them.
    """
)


st.write("\n")
st.subheader("Machine Learning", anchor=False)
st.write(
    """
    - This is just a demonstration of how using the different KPIs in the personal stats to derive out the Predicted Battlestats of the players
    - Still working in progress so its empty for now
    """
)