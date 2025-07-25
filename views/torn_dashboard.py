
'''
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("⚔️ Torn Faction Dashboard")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_excel('assets/RW_Factions.xlsx', sheet_name='RW_Factions')
    # Clean numerical columns
    df['networth'] = pd.to_numeric(df['networth'], errors='coerce')
    df['bss_public'] = pd.to_numeric(df['bss_public'], errors='coerce')
    df['elo'] = pd.to_numeric(df['elo'], errors='coerce')
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")

# Rank Selector
selected_rank = st.sidebar.multiselect(
    "Select Rank & Division:",
    options=df["Rank Name"].unique(),
    default=None
)

# Faction Selector (multi-select)
selected_factions = st.sidebar.multiselect(
    "Select Factions:",
    options=df["Faction Name"].unique(),
    default=None
)

# Player Name Search (supports partial matching)
player_search = st.sidebar.text_input("Search Players:")

# Number of Members Slider
min_members, max_members = st.sidebar.slider(
    "Number of Members Range:",
    min_value=int(df.groupby("Faction Name")["Member Name"].count().min()),
    max_value=int(df.groupby("Faction Name")["Member Name"].count().max()),
    value=(1, int(df.groupby("Faction Name")["Member Name"].count().max()))
)

# --- DYNAMIC FILTERING ---
filtered_df = df.copy()

# Apply Rank filter
if selected_rank:
    filtered_df = filtered_df[filtered_df["Rank Name"].isin(selected_rank)]

# Apply faction filter
if selected_factions:
    filtered_df = filtered_df[filtered_df["Faction Name"].isin(selected_factions)]   

# Apply player name filter
if player_search:
    filtered_df = filtered_df[filtered_df["Member Name"].str.contains(player_search, case=False, na=False)]

# Apply member count filter
faction_counts = filtered_df.groupby("Faction Name")["Member Name"].count()
valid_factions = faction_counts[
    (faction_counts >= min_members) & 
    (faction_counts <= max_members)
].index
filtered_df = filtered_df[filtered_df["Faction Name"].isin(valid_factions)]

# --- MAIN DASHBOARD LAYOUT ---
tab1, tab2, tab3 = st.tabs(["🏆 Overview", "📊 Stats", "🔍 Player Search"])

with tab1:
    # Key Metrics
    st.subheader("Faction Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Filtered Factions", filtered_df["Faction Name"].nunique())
    with col2:
        st.metric("Filtered Members", len(filtered_df))
    with col3:
        total_battlestats = filtered_df["bs_estimate"].sum()/1e9 # In billions
        st.metric("Total Battlestats",f"{total_battlestats:,.2f}B")    
    with col4:
        total_networth = filtered_df["networth"].sum()/1e9  # In billions
        st.metric("Total NetWorth", f"${total_networth:,.2f}B")

    # Scatterplot for factions
    st.subheader("Faction Comparison")
    
    # Prepare faction-level data with all requested metrics
    faction_stats = filtered_df.groupby("Faction Name").agg({
        'Member Name': 'count',
        'Rank Name': lambda x: str(x.mode()[0]) if not x.empty else '',
        'Division': lambda x: str(x.mode()[0]) if not x.empty else '',
        'attackswon': 'sum',
        'rankedwarhits': 'sum',
        'retals': 'sum',
        'elo': 'mean',
        'bs_estimate': 'sum',
        'bss_public': 'mean',
        'networth': 'sum',
        'xantaken': 'sum',
        'lsdtaken': 'sum',
        'statenhancersused': 'sum',
        'boostersused': 'sum',
        'refills': 'sum',
        'rankedwarringwins': 'sum',
        'useractivity': 'sum'
    }).reset_index()
    
    # Combine Rank Name and Division (now properly converted to strings)
    faction_stats['Rank & Division'] = faction_stats['Rank Name'] + ' ' + faction_stats['Division']
    
    fig = px.scatter(
        faction_stats,
        x="elo",
        y="Member Name",
        size="bss_public",
        color="Faction Name",
        hover_name="Faction Name",
        hover_data={"networth": ":$,.0f"},
        size_max=30,
        labels={
            "elo": "Average ELO Rating",
            "Member Name": "Number of Members",
            "bss_public": "BSS Public Score"
        },
        title="Faction Comparison: Size = BSS, X = Avg ELO, Y = Members"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # --- FACTION COMPARISON TABLE WITH CONDITIONAL FORMATTING ---
    st.subheader("Faction Performance Comparison")
    
    # Select reference faction
    reference_faction = st.selectbox(
        "Select Reference Faction for Comparison:",
        options=faction_stats["Faction Name"].unique()
    )
    
    # Get reference values
    ref_values = faction_stats[faction_stats["Faction Name"] == reference_faction].iloc[0]
    
    # Prepare comparison table with all requested columns
    comparison_cols = [
        'Faction Name', 
        'Member Name',
        'Rank & Division',
        'attackswon',
        'rankedwarhits',
        'retals',
        'elo',
        'bs_estimate',
        'bss_public',
        'networth',
        'xantaken',
        'lsdtaken',
        'statenhancersused',
        'boostersused',
        'refills',
        'rankedwarringwins',
        'useractivity'
    ]
    
    comparison_df = faction_stats[comparison_cols].copy()
    
    # Format values with thousand separators and no decimals
    def format_number(x):
        if pd.api.types.is_number(x):
            return f"{x:,.0f}"
        return x
    
    display_df = comparison_df.copy()
    for col in comparison_cols[3:]:  # Skip first 3 columns (name, members, rank/division)
        if pd.api.types.is_numeric_dtype(display_df[col]):
            display_df[col] = display_df[col].apply(format_number)
    
    # Function to apply conditional formatting
    def highlight_cells(row):
        styles = []
        for col in comparison_cols:
            if col in ['Faction Name', 'Rank & Division']:
                styles.append('')  # No styling for these columns
                continue
                
            # Get numeric values from original df (remove formatting if any)
            try:
                cell_val = float(comparison_df.loc[row.name, col])
                ref_val = float(ref_values[col])
            except:
                styles.append('')
                continue
            
            if cell_val > ref_val:
                styles.append('background-color: #ff7d7d')  # Red for higher
            elif cell_val < ref_val:
                styles.append('background-color: #90ee90')  # Green for lower
            else:
                styles.append('')
        return styles
    
    # Apply styling to the display dataframe
    styled_df = display_df.style.apply(highlight_cells, axis=1)
    
    # Display table with column configurations
    st.dataframe(
        styled_df,
        column_config={
            "Faction Name": "Faction",
            "Member Name": "Members",
            "Rank & Division": "Rank & Division",
            "attackswon": "Attacks Won",
            "rankedwarhits": "Ranked War Hits",
            "retals": "Retaliations",
            "elo": "Avg ELO",
            "bs_estimate": "BS Estimate",
            "bss_public": "Avg BSS Public",
            "networth": "Total Net Worth",
            "xantaken": "Xanax Taken",
            "lsdtaken": "LSD Taken",
            "statenhancersused": "Stat Enhancers",
            "boostersused": "Boosters Used",
            "refills": "Refills",
            "rankedwarringwins": "Ranked War Wins",
            "useractivity": "User Activity"
        },
        hide_index=True,
        use_container_width=True
    )

with tab2:
    st.subheader("Member Performance Dashboard")
    
    # Select KPIs to display
    kpi_cols = st.multiselect(
        "Select KPIs to display:",
        options=['attackswon', 'networth', 'elo', 'bss_public', 'respectforfaction', 'rankedwarhits'],
        default=['attackswon', 'networth', 'elo']
    )
    
    if kpi_cols:
        # Create bar charts for each selected KPI
        for kpi in kpi_cols:
            # Get top 10 members for this KPI
            top_members = filtered_df.nlargest(10, kpi)[['Member Name', 'Faction Name', kpi]]
            
            fig = px.bar(
                top_members,
                x='Member Name',
                y=kpi,
                color='Faction Name',
                title=f"Top 10 Members by {kpi.replace('_', ' ').title()}",
                labels={kpi: kpi.replace('_', ' ').title()}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Member table with data bars
        st.subheader("Member KPIs")
        
        # Format networth
        display_members = filtered_df.copy()
        display_members['networth'] = display_members['networth'].apply(lambda x: f"${x/1e6:,.1f}M" if pd.notnull(x) else 'N/A')
        
        # Create data bars for numeric columns
        def data_bars(column):
            n_bins = 100
            bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
            col_min = filtered_df[column].min()
            col_max = filtered_df[column].max()
            ranges = [((col_max - col_min) * i) + col_min for i in bounds]
            styles = []
            for value in filtered_df[column]:
                # Find position in bounds
                for i, bound in enumerate(bounds):
                    if value <= ranges[i]:
                        break
                # Color stops
                color = f"background: linear-gradient(90deg, #5fba7d {bound*100}%, transparent {bound*100}%);"
                styles.append(color)
            return styles
        
        # Apply data bars to numeric columns
        numeric_cols = [col for col in kpi_cols if col != 'networth']
        bar_styles = {}
        for col in numeric_cols:
            bar_styles[col] = data_bars(col)
        
        # Display member table
        st.dataframe(
            display_members[['Member Name', 'Faction Name', *kpi_cols]].style.apply(
                lambda x: bar_styles[x.name] if x.name in numeric_cols else ['']*len(x),
                subset=numeric_cols
            ),
            column_config={
                "Member Name": "Player",
                "attackswon": "Attacks Won",
                "networth": "Net Worth",
                "elo": "ELO Rating",
                "bss_public": "BSS Score",
                "respectforfaction": "Respect",
                "rankedwarhits": "Ranked Hits"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("Please select at least one KPI to display")

with tab3:
    # Player Search Results
    st.subheader("Player Details")
    
    # Sortable table with key columns
    st.dataframe(
        filtered_df[[
            "Member Name", 
            "Faction Name", 
            "Rank Level", 
            "attackswon", 
            "networth",
            "last_updated"
        ]].sort_values("networth", ascending=False),
        column_config={
            "networth": st.column_config.NumberColumn("Net Worth", format="$%.0f"),
            "attackswon": st.column_config.NumberColumn("Attacks Won", format="%,d"),
            "last_updated": "Last Updated"
        },
        hide_index=True,
        use_container_width=True
    )

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption(f"Data updated: {df['last_updated'].max()}")
'''

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("⚔️ Torn Faction Dashboard")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_excel('assets/RW_Factions.xlsx', sheet_name='RW_Factions')
    # Clean numerical columns
    df['networth'] = pd.to_numeric(df['networth'], errors='coerce')
    df['bss_public'] = pd.to_numeric(df['bss_public'], errors='coerce')
    df['elo'] = pd.to_numeric(df['elo'], errors='coerce')
    
    # Combine Rank Name and Division at the start
    df['Rank & Division'] = df['Rank Name'].astype(str) + ' ' + df['Division'].astype(str)
    
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")

# Rank & Division Selector (using the combined column)
selected_rank_division = st.sidebar.multiselect(
    "Select Rank & Division:",
    options=df["Rank & Division"].unique(),
    default=None
)

# Faction Selector (multi-select)
selected_factions = st.sidebar.multiselect(
    "Select Factions:",
    options=df["Faction Name"].unique(),
    default=None
)

# Player Name Search (supports partial matching)
player_search = st.sidebar.text_input("Search Players:")

# Number of Members Slider
min_members, max_members = st.sidebar.slider(
    "Number of Members Range:",
    min_value=int(df.groupby("Faction Name")["Member Name"].count().min()),
    max_value=int(df.groupby("Faction Name")["Member Name"].count().max()),
    value=(1, int(df.groupby("Faction Name")["Member Name"].count().max()))
)

# --- DYNAMIC FILTERING ---
filtered_df = df.copy()

# Apply Rank & Division filter
if selected_rank_division:
    filtered_df = filtered_df[filtered_df["Rank & Division"].isin(selected_rank_division)]

# Apply faction filter
if selected_factions:
    filtered_df = filtered_df[filtered_df["Faction Name"].isin(selected_factions)]   

# Apply player name filter
if player_search:
    filtered_df = filtered_df[filtered_df["Member Name"].str.contains(player_search, case=False, na=False)]

# Apply member count filter
faction_counts = filtered_df.groupby("Faction Name")["Member Name"].count()
valid_factions = faction_counts[
    (faction_counts >= min_members) & 
    (faction_counts <= max_members)
].index
filtered_df = filtered_df[filtered_df["Faction Name"].isin(valid_factions)]

# --- MAIN DASHBOARD LAYOUT ---
tab1, tab2, tab3 = st.tabs(["🏆 Overview", "📊 Stats", "🔍 Player Search"])

with tab1:
    # Key Metrics
    st.subheader("Faction Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Filtered Factions", filtered_df["Faction Name"].nunique())
    with col2:
        st.metric("Filtered Members", len(filtered_df))
    with col3:
        total_battlestats = filtered_df["bs_estimate"].sum()/1e9 # In billions
        st.metric("Total Battlestats",f"{total_battlestats:,.2f}B")    
    with col4:
        total_networth = filtered_df["networth"].sum()/1e9  # In billions
        st.metric("Total NetWorth", f"${total_networth:,.2f}B")

    # Scatterplot for factions
    st.subheader("Faction Comparison")
    
    # Prepare faction-level data with all requested metrics
    faction_stats = filtered_df.groupby("Faction Name").agg({
        'Member Name': 'count',
        'Rank & Division': lambda x: str(x.mode()[0]) if not x.empty else '',
        'attackswon': 'sum',
        'rankedwarhits': 'sum',
        'retals': 'sum',
        'elo': 'mean',
        'bs_estimate': 'sum',
        'bss_public': 'mean',
        'networth': 'sum',
        'xantaken': 'sum',
        'lsdtaken': 'sum',
        'statenhancersused': 'sum',
        'boostersused': 'sum',
        'refills': 'sum',
        'rankedwarringwins': 'sum',
        'useractivity': 'sum'
    }).reset_index()
    
    fig = px.scatter(
        faction_stats,
        x="elo",
        y="Member Name",
        size="bss_public",
        color="Faction Name",
        hover_name="Faction Name",
        hover_data={"networth": ":$,.0f"},
        size_max=30,
        labels={
            "elo": "Average ELO Rating",
            "Member Name": "Number of Members",
            "bss_public": "BSS Public Score"
        },
        title="Faction Comparison: Size = BSS, X = Avg ELO, Y = Members"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # --- FACTION COMPARISON TABLE WITH CONDITIONAL FORMATTING ---
    st.subheader("Faction Performance Comparison")
    
    # Select reference faction
    reference_faction = st.selectbox(
        "Select Reference Faction for Comparison:",
        options=faction_stats["Faction Name"].unique()
    )
    
    # Get reference values
    ref_values = faction_stats[faction_stats["Faction Name"] == reference_faction].iloc[0]
    
    # Prepare comparison table with all requested columns
    comparison_cols = [
        'Faction Name', 
        'Member Name',
        'Rank & Division',
        'attackswon',
        'rankedwarhits',
        'retals',
        'elo',
        'bs_estimate',
        'bss_public',
        'networth',
        'xantaken',
        'lsdtaken',
        'statenhancersused',
        'boostersused',
        'refills',
        'rankedwarringwins',
        'useractivity'
    ]
    
    comparison_df = faction_stats[comparison_cols].copy()
    
    # Format values with thousand separators and no decimals
    def format_number(x):
        if pd.api.types.is_number(x):
            return f"{x:,.0f}"
        return x
    
    display_df = comparison_df.copy()
    for col in comparison_cols[3:]:  # Skip first 3 columns (name, members, rank/division)
        if pd.api.types.is_numeric_dtype(display_df[col]):
            display_df[col] = display_df[col].apply(format_number)
    
    # Function to apply conditional formatting
    def highlight_cells(row):
        styles = []
        for col in comparison_cols:
            if col in ['Faction Name', 'Rank & Division']:
                styles.append('')  # No styling for these columns
                continue
                
            # Get numeric values from original df (remove formatting if any)
            try:
                cell_val = float(comparison_df.loc[row.name, col])
                ref_val = float(ref_values[col])
            except:
                styles.append('')
                continue
            
            if cell_val > ref_val:
                styles.append('background-color: #ff7d7d')  # Red for higher
            elif cell_val < ref_val:
                styles.append('background-color: #90ee90')  # Green for lower
            else:
                styles.append('')
        return styles
    
    # Apply styling to the display dataframe
    styled_df = display_df.style.apply(highlight_cells, axis=1)
    
    # Display table with column configurations
    st.dataframe(
        styled_df,
        column_config={
            "Faction Name": "Faction",
            "Member Name": "Members",
            "Rank & Division": "Rank & Division",
            "attackswon": "Attacks Won",
            "rankedwarhits": "Ranked War Hits",
            "retals": "Retaliations",
            "elo": "Avg ELO",
            "bs_estimate": "BS Estimate",
            "bss_public": "Avg BSS Public",
            "networth": "Total Net Worth",
            "xantaken": "Xanax Taken",
            "lsdtaken": "LSD Taken",
            "statenhancersused": "Stat Enhancers",
            "boostersused": "Boosters Used",
            "refills": "Refills",
            "rankedwarringwins": "Ranked War Wins",
            "useractivity": "User Activity"
        },
        hide_index=True,
        use_container_width=True
    )

with tab2:
    st.subheader("Member Performance Dashboard")
    
    # Select KPIs to display
    kpi_cols = st.multiselect(
        "Select KPIs to display:",
        options=['attackswon', 'networth', 'elo', 'bss_public', 'respectforfaction', 'rankedwarhits'],
        default=['attackswon', 'networth', 'elo']
    )
    
    if kpi_cols:
        # Create bar charts for each selected KPI
        for kpi in kpi_cols:
            # Get top 10 members for this KPI
            top_members = filtered_df.nlargest(10, kpi)[['Member Name', 'Faction Name', 'Rank & Division', kpi]]
            
            fig = px.bar(
                top_members,
                x='Member Name',
                y=kpi,
                color='Faction Name',
                title=f"Top 10 Members by {kpi.replace('_', ' ').title()}",
                labels={kpi: kpi.replace('_', ' ').title()},
                hover_data=['Rank & Division']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Member table with data bars
        st.subheader("Member KPIs")
        
        # Format networth
        display_members = filtered_df.copy()
        display_members['networth'] = display_members['networth'].apply(lambda x: f"${x/1e6:,.1f}M" if pd.notnull(x) else 'N/A')
        
        # Create data bars for numeric columns
        def data_bars(column):
            n_bins = 100
            bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
            col_min = filtered_df[column].min()
            col_max = filtered_df[column].max()
            ranges = [((col_max - col_min) * i) + col_min for i in bounds]
            styles = []
            for value in filtered_df[column]:
                # Find position in bounds
                for i, bound in enumerate(bounds):
                    if value <= ranges[i]:
                        break
                # Color stops
                color = f"background: linear-gradient(90deg, #5fba7d {bound*100}%, transparent {bound*100}%);"
                styles.append(color)
            return styles
        
        # Apply data bars to numeric columns
        numeric_cols = [col for col in kpi_cols if col != 'networth']
        bar_styles = {}
        for col in numeric_cols:
            bar_styles[col] = data_bars(col)
        
        # Display member table
        st.dataframe(
            display_members[['Member Name', 'Faction Name', 'Rank & Division', *kpi_cols]].style.apply(
                lambda x: bar_styles[x.name] if x.name in numeric_cols else ['']*len(x),
                subset=numeric_cols
            ),
            column_config={
                "Member Name": "Player",
                "Faction Name": "Faction",
                "Rank & Division": "Rank & Division",
                "attackswon": "Attacks Won",
                "networth": "Net Worth",
                "elo": "ELO Rating",
                "bss_public": "BSS Score",
                "respectforfaction": "Respect",
                "rankedwarhits": "Ranked Hits"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("Please select at least one KPI to display")

with tab3:
    # Player Search Results
    st.subheader("Player Details")
    
    # Sortable table with key columns
    st.dataframe(
        filtered_df[[
            "Member Name", 
            "Faction Name", 
            "Rank & Division",
            "Rank Level", 
            "attackswon", 
            "networth",
            "last_updated"
        ]].sort_values("networth", ascending=False),
        column_config={
            "networth": st.column_config.NumberColumn("Net Worth", format="$%.0f"),
            "attackswon": st.column_config.NumberColumn("Attacks Won", format="%,d"),
            "last_updated": "Last Updated"
        },
        hide_index=True,
        use_container_width=True
    )

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption(f"Data updated: {df['last_updated'].max()}")