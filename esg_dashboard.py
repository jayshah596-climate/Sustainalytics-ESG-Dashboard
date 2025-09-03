import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datasets import load_dataset

# ---------------------------
# Load dataset
# ---------------------------
@st.cache_data
def load_data():
    dataset = load_dataset(
        "nlp-esg-scoring/spx-sustainalytics-esg-scores", split="train"
    )
    return pd.DataFrame(dataset)

df = load_data()

st.set_page_config(page_title="SPX ESG Dashboard", layout="wide")
st.title("Sustainalytics ESG Dashboard 📊")

# ---------------------------
# Sidebar filters
# ---------------------------
st.sidebar.header("Filters")
unique_companies = df['Company'].unique()
selected_companies = st.sidebar.multiselect("Select Company(s):", unique_companies)

unique_peers = df['Peer_group_root'].unique()
selected_peers = st.sidebar.multiselect("Select Peer Group(s):", unique_peers)

unique_regions = df['Region'].unique()
selected_regions = st.sidebar.multiselect("Select Region(s):", unique_regions)

unique_countries = df['Country'].unique()
selected_countries = st.sidebar.multiselect("Select Country(s):", unique_countries)

# ---------------------------
# Only filter if the user has selected something
# ---------------------------
filtered_df = pd.DataFrame()  # start empty

if selected_companies or selected_peers or selected_regions or selected_countries:
    filtered_df = df.copy()
    if selected_companies:
        filtered_df = filtered_df[filtered_df['Company'].isin(selected_companies)]
    if selected_peers:
        filtered_df = filtered_df[filtered_df['Peer_group_root'].isin(selected_peers)]
    if selected_regions:
        filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]
    if selected_countries:
        filtered_df = filtered_df[filtered_df['Country'].isin(selected_countries)]

# ---------------------------
# Only render dashboard after selection
# ---------------------------
if filtered_df.empty:
    st.info("Please select at least one filter from the sidebar to view the data.")
else:
    # Metrics
    st.subheader("Overview Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Companies", filtered_df['Company'].nunique())
    col2.metric("Average ESG Score", round(filtered_df['total_esg_score'].mean(), 2))
    col3.metric("Average Governance Score", round(filtered_df['governance_score'].mean(), 2))

    # ESG Score Distribution
    st.subheader("Total ESG Score Distribution")
    fig_esg_dist = px.histogram(filtered_df, x="total_esg_score", nbins=20)
    st.plotly_chart(fig_esg_dist, use_container_width=True)

    # ESG Scores per Company
    st.subheader("Total ESG Scores per Company")
    fig_esg_company = px.bar(
        filtered_df.sort_values("total_esg_score", ascending=False),
        x="Company",
        y="total_esg_score",
        text="total_esg_score",
    )
    fig_esg_company.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_esg_company, use_container_width=True)

    # ESG Score vs Governance Score
    st.subheader("ESG Score vs Governance Score")
    fig_scatter = px.scatter(
        filtered_df,
        x="total_esg_score",
        y="governance_score",
        size="total_esg_score",
        hover_data=["Company", "Ticker"],
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # ESG Gauge per Company
    st.subheader("ESG Gauge per Company")
    for company in filtered_df['Company'].unique():
        esg_val = filtered_df.loc[filtered_df['Company'] == company, 'total_esg_score'].values[0]
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=esg_val,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"{company} ESG Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': 'red'},
                    {'range': [40, 70], 'color': 'yellow'},
                    {'range': [70, 100], 'color': 'green'}
                ]
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Filtered data sample
    st.markdown("---")
    st.subheader("Filtered Data Sample")
    st.dataframe(filtered_df.head(50))
    csv = filtered_df.to_csv(index=False).encode('utf-8')