# streamlit_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Winter Weather Dashboard", layout="wide")

# --- Load preprocessed data ---
pbw = pd.read_csv('pbw_processed.csv', parse_dates=['DATE'])
winter_prcp = pd.read_csv('winter_prcp.csv')
monthly_summary = pd.read_csv('monthly_summary.csv')
winter_extremes = pd.read_csv('winter_extremes.csv')
cold_days = pd.read_csv('cold_days.csv')

# --- Sidebar Controls ---
st.sidebar.header("Filters & Options")

# Year range filter
year_min = int(winter_prcp['WINTER_YEAR'].min())
year_max = int(winter_prcp['WINTER_YEAR'].max())
years = st.sidebar.slider(
    "Select Winter Year Range",
    year_min, year_max,
    (year_min, year_max)
)

# Metric selection for winter-level plots
winter_metrics = st.sidebar.multiselect(
    "Select Winter Metric(s)",
    options=['snowy_days', 'rainy_days', 'no_rain_nor_snow_days', 'days_below_zero', 'sum_prcp_no_snow'],
    default=['snowy_days', 'days_below_zero']
)

# Month selection for monthly plots
month_selected = st.sidebar.slider("Select Month for Monthly Metrics", 1, 12, 1)

# Timeline metrics for first/last snow or freeze
timeline_metrics = st.sidebar.multiselect(
    "Select Timeline Metrics",
    options=['first_snow', 'last_snow', 'first_freeze', 'last_freeze'],
    default=['first_snow', 'last_snow']
)

# Rolling average toggle
rolling_window = st.sidebar.slider("Rolling average window (years)", 1, 10, 5)

# --- Main Dashboard Tabs ---
tabs = st.tabs([
    "Winter Overview",
    "Winter Extremes & Cold",
    "Snow & Precipitation Events",
    "Holiday Snow",
    "First/Last Snow & Freeze",
    "Monthly Comparison",
    "Trend Analysis"
])

# --- Tab 1: Winter Overview (Q1) ---
with tabs[0]:
    st.header("Winter Overview: TMAX, TMIN, SNWD, PRCP")
    winter_filtered = pbw[(pbw['WINTER_YEAR'] >= years[0]) & (pbw['WINTER_YEAR'] <= years[1])]
    fig = px.line(
        winter_filtered,
        x='DATE',
        y=['TMAX', 'TMIN', 'SNWD', 'PRCP'],
        labels={'value': 'Measurement', 'variable': 'Metric'},
        title='Daily Temperature, Snow Depth, and Precipitation'
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Winter Extremes & Cold (Q2 & Q3) ---
with tabs[1]:
    st.header("Winter Extremes & Cold")
    winter_filtered = winter_prcp[(winter_prcp['WINTER_YEAR'] >= years[0]) & (winter_prcp['WINTER_YEAR'] <= years[1])]
    fig = go.Figure()
    for metric in winter_metrics:
        fig.add_trace(go.Scatter(
            x=winter_filtered['WINTER_YEAR'],
            y=winter_filtered[metric],
            mode='lines+markers',
            name=metric
        ))
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 3: Snow & Precipitation Events (Q4 & Q5 & Q6) ---
with tabs[2]:
    st.header("Snow Streaks & Precipitation Events")
    fig = go.Figure()
    for metric in ['max_snow_streak', 'max_cold_streak', 'sum_prcp_no_snow']:
        if metric in winter_filtered.columns:
            fig.add_trace(go.Scatter(
                x=winter_filtered['WINTER_YEAR'],
                y=winter_filtered[metric],
                mode='lines+markers',
                name=metric
            ))
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 4: Holiday Snow (Q7) ---
with tabs[3]:
    st.header("Snow During Holiday Season (Dec 23–Jan 1)")
    holiday_filtered = winter_prcp[(winter_prcp['WINTER_YEAR'] >= years[0]) & (winter_prcp['WINTER_YEAR'] <= years[1])]
    fig = px.bar(
        holiday_filtered,
        x='WINTER_YEAR',
        y='snowy_holidays',
        labels={'snowy_holidays': 'Snowy Holiday Days'},
        title='Snowy Days During Holidays'
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 5: First/Last Snow & Freeze (Q8) ---
with tabs[4]:
    st.header("First and Last Snow / Freeze")
    extremes_filtered = winter_extremes[(winter_extremes['WINTER_YEAR'] >= years[0]) & (winter_extremes['WINTER_YEAR'] <= years[1])]
    fig = go.Figure()
    for metric in timeline_metrics:
        fig.add_trace(go.Scatter(
            x=extremes_filtered['WINTER_YEAR'],
            y=extremes_filtered[metric],
            mode='markers+lines',
            name=metric
        ))
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 6: Monthly Comparison (Q9) ---
with tabs[5]:
    st.header(f"Monthly Metrics for Month {month_selected}")
    monthly_filtered = monthly_summary[monthly_summary['MONTH'] == month_selected]
    monthly_long = monthly_filtered.melt(
        id_vars=['YEAR', 'MONTH'],
        value_vars=['snowy_days', 'rainy_days', 'dry_days', 'sum_PRCP', 'mean_SNWD'],
        var_name='Metric',
        value_name='Value'
    )
    fig = px.line(
        monthly_long,
        x='YEAR',
        y='Value',
        color='Metric',
        markers=True,
        title=f"Monthly Metrics Over Years"
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 7: Trend Analysis (Q10) ---
with tabs[6]:
    st.header("Trend Analysis")
    trend_filtered = winter_prcp[(winter_prcp['WINTER_YEAR'] >= years[0]) & (winter_prcp['WINTER_YEAR'] <= years[1])]
    fig = go.Figure()
    for metric in winter_metrics:
        # Optional rolling average
        rolling_series = trend_filtered[metric].rolling(window=rolling_window, center=True).mean()
        fig.add_trace(go.Scatter(
            x=trend_filtered['WINTER_YEAR'],
            y=rolling_series,
            mode='lines',
            name=f"{metric} ({rolling_window}-yr rolling)"
        ))
    st.plotly_chart(fig, use_container_width=True)
