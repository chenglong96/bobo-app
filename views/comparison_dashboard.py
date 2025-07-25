'''
import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.title("⚔️ Tornado Faction Comparison")

# --- LOAD AND PREPARE DATA ---
@st.cache_data
def load_data():
    df = pd.read_excel('assets/RW_Factions.xlsx', sheet_name='RW_Factions')
    
    # Drop unnecessary columns
    drop_cols = ['Rank Position', 'Member Name', 'Member ID', 'bs_estimate_human', 
                'last_updated','attackslost', 'attacksdraw','revives',
                'nerverefills', 'tokenrefills', 'overdosed']
    df = df.drop(columns=drop_cols, errors='ignore')
    
    # Grouping and aggregation
    group_cols = ['Faction ID', 'Faction Name', 'Tag', 'Rank Level', 'Rank Name', 'Division']
    df['Number of Members'] = 1
    
    grouped = df.groupby(group_cols, as_index=False).agg({
        'Number of Members': 'sum',
        'attackswon': 'sum',
        'attacksassisted': 'sum',
        'elo': 'mean',
        'retals': 'sum',
        'respectforfaction': 'sum',
        'rankedwarhits': 'sum',
        'booksread': 'sum',
        'boostersused': 'sum',
        'consumablesused': 'sum',
        'candyused': 'sum',
        'alcoholused': 'sum',
        'energydrinkused': 'sum',
        'statenhancersused': 'sum',
        'lsdtaken': 'sum',
        'xantaken': 'sum',
        'useractivity': 'sum',
        'rankedwarringwins': 'sum',
        'daysbeendonator': 'sum',
        'refills': 'sum',
        'rehabcost': 'sum',
        'networth': 'sum',
        'awards': 'sum',
        'bs_estimate': 'sum',
        'bss_public': 'mean'
    })
    
    return grouped

df = load_data()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Comparison Settings")

# Get sorted list of factions for dropdowns
factions = sorted(df['Faction Name'].unique())

col1, col2 = st.sidebar.columns(2)
with col1:
    left_faction = st.selectbox(
        "Left Faction",
        options=factions,
        index=0
    )
with col2:
    right_faction = st.selectbox(
        "Right Faction",
        options=factions,
        index=1 if len(factions) > 1 else 0
    )

# Select metrics to compare
metrics = [
    'Number of Members', 'attackswon', 'respectforfaction', 
    'networth', 'rankedwarhits', 'energydrinkused',
    'boostersused', 'lsdtaken', 'xantaken', 'booksread'
]

selected_metric = st.sidebar.selectbox(
    "Select Metric to Compare",
    options=metrics,
    index=0
)

# --- MAIN DASHBOARD ---
# Get data for selected factions
left_data = df[df['Faction Name'] == left_faction].iloc[0]
right_data = df[df['Faction Name'] == right_faction].iloc[0]

# Create comparison dataframe
comparison = pd.DataFrame({
    'Metric': [selected_metric, selected_metric],
    'Value': [left_data[selected_metric], right_data[selected_metric]],
    'Faction': [left_faction, right_faction]
})

# Create tornado chart
fig = px.bar(
    comparison,
    x='Value',
    y='Metric',
    color='Faction',
    orientation='h',
    barmode='group',
    title=f"{left_faction} vs {right_faction} - {selected_metric} Comparison",
    labels={'Value': selected_metric},
    height=400
)

# Customize layout
fig.update_layout(
    yaxis={'visible': False, 'showticklabels': False},
    hovermode='y unified',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

# Display the chart
st.plotly_chart(fig, use_container_width=True)

# --- METRIC COMPARISON TABLE ---
st.subheader("Detailed Comparison")

# Select metrics to show in table
table_metrics = [
    'Number of Members', 'attackswon', 'respectforfaction',
    'networth', 'rankedwarhits', 'energydrinkused',
    'boostersused', 'lsdtaken', 'xantaken', 'booksread'
]

# Create comparison table
comparison_table = pd.DataFrame({
    'Metric': table_metrics,
    left_faction: [left_data[m] for m in table_metrics],
    right_faction: [right_data[m] for m in table_metrics]
})

# Format numeric values
def format_numbers(x):
    if isinstance(x, (int, float)):
        if abs(x) >= 1e6:
            return f"{x/1e6:,.1f}M"
        elif abs(x) >= 1e3:
            return f"{x/1e3:,.0f}K"
        return f"{x:,.0f}"
    return x

comparison_table = comparison_table.applymap(format_numbers)

# Display table
st.dataframe(
    comparison_table,
    column_config={
        "Metric": st.column_config.TextColumn("Metric"),
        left_faction: st.column_config.TextColumn(left_faction),
        right_faction: st.column_config.TextColumn(right_faction)
    },
    hide_index=True,
    use_container_width=True
)

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("Faction data aggregated from member statistics")

'''

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("⚔️ Tornado Faction Comparison")

# --- LOAD AND PREPARE DATA ---
@st.cache_data
def load_data():
    df = pd.read_excel('assets/RW_Factions.xlsx', sheet_name='RW_Factions')
    
    # Drop unnecessary columns
    drop_cols = ['Rank Position', 'Member Name', 'Member ID', 'bs_estimate_human', 
                'last_updated','attackslost', 'attacksdraw','revives',
                'nerverefills', 'tokenrefills', 'overdosed']
    df = df.drop(columns=drop_cols, errors='ignore')
    
    # Grouping and aggregation
    group_cols = ['Faction ID', 'Faction Name', 'Tag', 'Rank Level', 'Rank Name', 'Division']
    df['Number of Members'] = 1
    
    grouped = df.groupby(group_cols, as_index=False).agg({
        'Number of Members': 'sum',
        'attackswon': 'sum',
        'attacksassisted': 'sum',
        'elo': 'mean',
        'retals': 'sum',
        'respectforfaction': 'sum',
        'rankedwarhits': 'sum',
        'booksread': 'sum',
        'boostersused': 'sum',
        'consumablesused': 'sum',
        'candyused': 'sum',
        'alcoholused': 'sum',
        'energydrinkused': 'sum',
        'statenhancersused': 'sum',
        'lsdtaken': 'sum',
        'xantaken': 'sum',
        'useractivity': 'sum',
        'rankedwarringwins': 'sum',
        'daysbeendonator': 'sum',
        'refills': 'sum',
        'rehabcost': 'sum',
        'networth': 'sum',
        'awards': 'sum',
        'bs_estimate': 'sum',
        'bss_public': 'mean'
    })
    
    return grouped

df = load_data()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Comparison Settings")

# Get sorted list of factions for dropdowns
factions = sorted(df['Faction Name'].unique())

col1, col2 = st.sidebar.columns(2)
with col1:
    left_faction = st.selectbox(
        "Left Faction",
        options=factions,
        index=0
    )
with col2:
    right_faction = st.selectbox(
        "Right Faction",
        options=factions,
        index=1 if len(factions) > 1 else 0
    )

# --- MAIN DASHBOARD ---
# Get data for selected factions
left_data = df[df['Faction Name'] == left_faction].iloc[0]
right_data = df[df['Faction Name'] == right_faction].iloc[0]

# Define metrics to compare (matching your reference image)
metrics = [
    'Number of Members', 'attackswon', 'respectforfaction',
    'networth', 'rankedwarhits', 'energydrinkused',
    'boostersused', 'lsdtaken', 'xantaken', 'booksread',
    'statenhancersused', 'alcoholused', 'candyused',
    'daysbeendonator', 'awards'
]

# Format values with appropriate units
def format_value(val, metric):
    if metric == 'networth':
        return f"${val/1e9:,.1f}B" if val >= 1e9 else f"${val/1e6:,.1f}M"
    elif val >= 1e6:
        return f"{val/1e6:,.1f}M"
    elif val >= 1e3:
        return f"{val/1e3:,.0f}K"
    return f"{val:,.0f}"

# Create PERCENTAGE-BASED tornado chart
fig = go.Figure()

# Calculate percentages (normalized to the maximum value for each metric)
max_values = [max(abs(left_data[m]), abs(right_data[m])) for m in metrics]
total_values = [abs(left_data[m]) + abs(right_data[m]) for m in metrics]
percentages_left = [-100 * left_data[m] / (total if total != 0 else 1) for m, total in zip(metrics, total_values)]
percentages_right = [100 * right_data[m] / (total if total != 0 else 1) for m, total in zip(metrics, total_values)]

# Add left faction bars (negative percentages)
fig.add_trace(go.Bar(
    y=metrics,
    x=percentages_left,
    name=left_faction,
    orientation='h',
    marker_color='#1f77b4',
    text=[format_value(left_data[m], m) for m in metrics],
    textposition='outside',
    textfont=dict(size=10),
    width=0.6
))

# Add right faction bars (positive percentages)
fig.add_trace(go.Bar(
    y=metrics,
    x=percentages_right,
    name=right_faction,
    orientation='h',
    marker_color='#ff7f0e',
    text=[format_value(right_data[m], m) for m in metrics],
    textposition='outside',
    textfont=dict(size=10),
    width=0.6
))

# Update layout for percentage tornado effect
fig.update_layout(
    title=f"<b>{left_faction} vs {right_faction}</b> - Percentage Comparison",
    barmode='relative',
    height=max(600, 35 * len(metrics)),
    margin=dict(l=220, r=50, b=100, t=80, pad=10),
    xaxis=dict(
        title='Percentage of Maximum Value',
        tickvals=[-100, -75, -50, -25, 0, 25, 50, 75, 100],
        ticktext=['100%', '75%', '50%', '25%', '0', '25%', '50%', '75%', '100%'],
        range=[-105, 105],
        showgrid=True,
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='black'
    ),
    yaxis=dict(
        autorange='reversed',
        automargin=True,
        tickfont=dict(size=11),
        title=None
    ),
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    bargap=0.4
)

# Display the percentage-based chart
st.plotly_chart(fig, use_container_width=True)

# --- METRIC COMPARISON TABLE ---
st.subheader("Detailed Metrics Comparison")

# Create comparison table
comparison_table = pd.DataFrame({
    'Metric': metrics,
    left_faction: [format_value(left_data[m], m) for m in metrics],
    right_faction: [format_value(right_data[m], m) for m in metrics]
})

# Simplified styling approach
def style_table():
    # Create a style dictionary
    styles = []
    styles.append({
        'selector': 'th.col_heading',
        'props': [('background-color', '#1f77b4'), ('color', 'white')]
    })
    styles.append({
        'selector': f'th.col_heading.level0.col1',
        'props': [('background-color', '#1f77b4'), ('color', 'white')]
    })
    styles.append({
        'selector': f'th.col_heading.level0.col2',
        'props': [('background-color', '#ff7f0e'), ('color', 'white')]
    })
    return styles

# Apply styling
styled_table = comparison_table.style.set_table_styles(style_table())

# Display table
st.dataframe(
    styled_table,
    column_config={
        "Metric": st.column_config.TextColumn("Metric", width="medium"),
        left_faction: st.column_config.TextColumn(left_faction, width="small"),
        right_faction: st.column_config.TextColumn(right_faction, width="small")
    },
    hide_index=True,
    use_container_width=True
)

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("Faction data aggregated from member statistics")


