# ============================================================
# AHEAD – INTEGRATED DATA QUALITY DASHBOARD (STREAMLIT APP)
# ============================================================

import os
from typing import Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# For dynamic map visualization
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: plotly not available. Map features will be limited.")

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
DQ_EXCEL_PATH = "dq_review_ken_level4.xlsx"
DQ_GEO_PATH = "dq_unit_with_outliers.parquet"

# ------------------------------------------------------------
# DATA LOADING
# ------------------------------------------------------------
@st.cache_data
def load_dq_data(excel_path: str) -> Tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    dq_indicator = pd.read_excel(excel_path, sheet_name="completeness_indicator")
    dq_unit = pd.read_excel(excel_path, sheet_name="completeness_unit")
    dq_duplicates = pd.read_excel(excel_path, sheet_name="duplicates")
    dq_outliers = pd.read_excel(excel_path, sheet_name="outliers")
    df_derived = pd.read_excel(excel_path, sheet_name="derived_indicators")
    return dq_indicator, dq_unit, dq_duplicates, dq_outliers, df_derived


@st.cache_data
def load_geo_data(geo_path: str) -> pd.DataFrame | None:
    if not os.path.exists(geo_path):
        return None
    return pd.read_parquet(geo_path)

# ------------------------------------------------------------
# GLOBAL KPIs
# ------------------------------------------------------------
def compute_global_kpis(dq_indicator: pd.DataFrame, dq_unit: pd.DataFrame) -> dict:
    if dq_indicator.empty or dq_unit.empty:
        return {
            "avg_pct_reported": 0.0,
            "median_pct_outliers": 0.0,
            "indicators_high_missing": 0,
            "units_low_reporting": 0,
        }

    return {
        "avg_pct_reported": dq_unit["pct_reported"].mean() * 100,
        "median_pct_outliers": dq_indicator["pct_outliers"].median(),
        "indicators_high_missing": (dq_indicator["pct_missing"] > 10).sum(),
        "units_low_reporting": (dq_unit["pct_reported"] < 0.80).sum(),
    }


def kpi_card(label: str, value: str):
    with st.container(border=True):
        st.markdown(f"**{label}**")
        st.markdown(f"### {value}")

# ------------------------------------------------------------
# DASHBOARD PAGES
# ------------------------------------------------------------
def indicators_page(dq_indicator: pd.DataFrame):
    st.subheader("Indicator-level Data Quality")

    indicator_types = sorted(dq_indicator["indicator_type"].dropna().unique())
    col1, col2 = st.columns(2)

    with col1:
        selected = st.multiselect(
            "Filter by indicator_type",
            indicator_types,
            default=indicator_types,
        )

    with col2:
        metric = st.selectbox(
            "Metric to rank by",
            ["pct_outliers", "pct_missing", "pct_negative"],
        )

    df = dq_indicator[dq_indicator["indicator_type"].isin(selected)].copy()

    agg_cols = ["pct_missing", "pct_negative", "pct_duplicates", "pct_outliers"]
    df_agg = (
        df.groupby("indicator_type")[agg_cols]
        .mean(numeric_only=True)
        .reset_index()
    )

    top_n = st.slider("Number of indicators to show", 5, 50, 20)
    df_top = df_agg.sort_values(metric, ascending=False).head(top_n).iloc[::-1]

    fig, ax = plt.subplots(figsize=(8, max(4, 0.3 * len(df_top))))
    ax.barh(df_top["indicator_type"], df_top[metric])
    ax.set_xlabel(f"{metric} (%)")
    ax.set_title("Worst-performing indicators")
    st.pyplot(fig)

    st.dataframe(df_agg.sort_values(metric, ascending=False))


def units_page(dq_unit: pd.DataFrame, dq_outliers: pd.DataFrame):
    st.subheader("Unit-level Reporting Completeness")

    levels = sorted(dq_unit["unit_level"].dropna().unique())
    level = st.selectbox("Unit level", levels)

    df = dq_unit[dq_unit["unit_level"] == level].copy()

    outliers = (
        dq_outliers.groupby("unit_code")["value_clean"]
        .size()
        .rename("n_outliers_unit")
    )
    df = df.merge(outliers, on="unit_code", how="left")
    df["n_outliers_unit"] = df["n_outliers_unit"].fillna(0).astype(int)
    df["pct_reported_pct"] = df["pct_reported"] * 100

    max_report = st.slider("Show units with completeness ≤ (%)", 0, 100, 80)
    df = df[df["pct_reported_pct"] <= max_report]

    fig, ax = plt.subplots(figsize=(8, max(4, 0.3 * len(df.head(30)))))
    ax.barh(df.head(30)["unit_name"], df.head(30)["pct_reported_pct"])
    ax.set_xlabel("Reporting completeness (%)")
    ax.set_title("Lowest reporting units")
    st.pyplot(fig)

    st.dataframe(df.sort_values("pct_reported_pct"))


def heatmap_page(dq_indicator: pd.DataFrame):
    st.subheader("DQ KPI Heatmap")

    metrics = ["pct_missing", "pct_negative", "pct_duplicates", "pct_outliers"]
    df = (
        dq_indicator.groupby("indicator_type")[metrics]
        .mean(numeric_only=True)
        .reset_index()
        .sort_values("pct_outliers", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(8, max(4, 0.3 * len(df))))
    im = ax.imshow(df[metrics], aspect="auto")
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["indicator_type"])
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(metrics, rotation=45)
    fig.colorbar(im, ax=ax)
    st.pyplot(fig)


def map_page(dq_unit_geo: pd.DataFrame | None, dq_outliers: pd.DataFrame):
    """
    FIXED VERSION: Map now updates dynamically with indicator filters
    """
    st.subheader("Map – Unit-level Anomalies")

    if dq_unit_geo is None or dq_unit_geo.empty:
        st.info("Geo file not found. Run pipeline Section 9 to generate geographic data.")
        return

    # Get base data
    df = dq_unit_geo.copy()
    df["pct_reported_pct"] = df["pct_reported"] * 100

    # Indicator filter
    indicators = sorted(dq_outliers["indicator_type"].dropna().unique())
    
    st.markdown("### Filter Options")
    selected = st.multiselect(
        "Select indicator(s) to filter outliers (leave empty for all)",
        indicators,
        default=[],
    )

    # CRITICAL FIX: Filter outliers BEFORE counting
    if selected:
        out = dq_outliers[dq_outliers["indicator_type"].isin(selected)].copy()
        filter_status = f"Showing outliers for: {', '.join(selected)}"
    else:
        out = dq_outliers.copy()
        filter_status = "Showing all outliers"
    
    st.info(f"📍 {filter_status}")

    # Count filtered outliers per unit
    counts = out.groupby("unit_code").size().reset_index(name="n_outliers_filt")
    
    # Merge with geo data
    df = df.merge(counts, on="unit_code", how="left")
    df["n_outliers_filt"] = df["n_outliers_filt"].fillna(0).astype(int)

    # Create bubble size (square root scaling for better visualization)
    df["bubble_size"] = np.sqrt(df["n_outliers_filt"] + 1) * 5
    
    # Add hover text
    df["hover_text"] = (
        df["unit_name"] + 
        "<br>Completeness: " + df["pct_reported_pct"].round(1).astype(str) + "%" +
        "<br>Outliers: " + df["n_outliers_filt"].astype(str)
    )

    # ============================================================
    # PLOTLY INTERACTIVE MAP (RECOMMENDED)
    # ============================================================
    if PLOTLY_AVAILABLE:
        st.markdown("### Interactive Map")
        
        # Create plotly scatter map
        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            size="bubble_size",
            color="n_outliers_filt",
            hover_name="unit_name",
            hover_data={
                "pct_reported_pct": ":.1f",
                "n_outliers_filt": True,
                "bubble_size": False,
                "lat": False,
                "lon": False
            },
            color_continuous_scale="Reds",
            size_max=30,
            zoom=5.5,
            title=f"Outlier Distribution ({len(df[df['n_outliers_filt'] > 0])} units with outliers)"
        )
        
        fig.update_layout(
            mapbox_style="open-street-map",
            height=600,
            margin={"r": 0, "t": 50, "l": 0, "b": 0}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        # ============================================================
        # FALLBACK: SIMPLE STREAMLIT MAP (Less dynamic but works)
        # ============================================================
        st.markdown("### Map View")
        st.warning("Install plotly for interactive map: pip install plotly")
        
        # Prepare data for st.map
        df_map = df[["lat", "lon", "bubble_size"]].copy()
        df_map = df_map.rename(columns={"lat": "latitude", "lon": "longitude"})
        
        # Use st.map (note: this is less dynamic but works without plotly)
        st.map(df_map, size="bubble_size")

    # ============================================================
    # DATA TABLE (Always shown)
    # ============================================================
    st.markdown("### Detailed Unit Data")
    
    # Add summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Units", len(df))
    with col2:
        st.metric("Units with Outliers", len(df[df["n_outliers_filt"] > 0]))
    with col3:
        st.metric("Total Outliers", int(df["n_outliers_filt"].sum()))
    
    # Show sortable table
    df_display = df[["unit_name", "unit_level", "pct_reported_pct", "n_outliers_filt"]].copy()
    df_display = df_display.rename(columns={
        "unit_name": "Unit",
        "unit_level": "Level",
        "pct_reported_pct": "Completeness (%)",
        "n_outliers_filt": "Outliers"
    })
    
    st.dataframe(
        df_display.sort_values("Outliers", ascending=False),
        use_container_width=True,
        height=400
    )


def outliers_page(dq_outliers: pd.DataFrame):
    st.subheader("Outlier Records")
    
    # Add filters
    col1, col2 = st.columns(2)
    
    with col1:
        indicator_filter = st.multiselect(
            "Filter by indicator type",
            sorted(dq_outliers["indicator_type"].dropna().unique()),
            default=[]
        )
    
    with col2:
        min_zscore = st.slider(
            "Minimum |z-score|",
            0.0, 10.0, 0.0, 0.5
        )
    
    # Apply filters
    df = dq_outliers.copy()
    if indicator_filter:
        df = df[df["indicator_type"].isin(indicator_filter)]
    
    df = df[df["zscore"].abs() >= min_zscore]
    
    # Sort by absolute z-score
    df = df.sort_values("zscore", key=lambda s: s.abs(), ascending=False)
    
    st.info(f"Showing {len(df):,} outliers (from {len(dq_outliers):,} total)")
    
    st.dataframe(
        df,
        use_container_width=True,
        height=500
    )


def derived_page(df_derived: pd.DataFrame):
    st.subheader("Derived Percentage Indicators")

    pct_cols = [c for c in df_derived.columns if c.startswith("pct_")]
    
    if not pct_cols:
        st.warning("No derived indicators found in the dataset.")
        return
    
    indicator = st.selectbox("Indicator", pct_cols)

    levels = sorted(df_derived["unit_level"].dropna().unique())
    level = st.selectbox("Unit level", levels)

    mode = st.radio("View mode", ["Aggregate (median)", "Single unit"], horizontal=True)

    df = df_derived[df_derived["unit_level"] == level].copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    if mode == "Aggregate (median)":
        df_plot = df.groupby("date", as_index=False)[indicator].median()
        title_suffix = "(National Median)"
    else:
        units = sorted(df["unit_name"].dropna().unique())
        unit = st.selectbox("Unit", units)
        df_plot = df[df["unit_name"] == unit][["date", indicator]]
        title_suffix = f"({unit})"

    # Apply 3-month moving average
    df_plot[indicator] = df_plot[indicator].rolling(3, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_plot["date"], df_plot[indicator], linewidth=2, marker='o', markersize=3)
    ax.set_ylim(0, 100)  # Changed from (0, 1) to (0, 100)
    ax.set_ylabel("Percentage (%)")  # Changed from "Proportion (0–1)"
    ax.set_xlabel("Date")
    ax.set_title(f"{indicator} {title_suffix}")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    st.dataframe(df_plot, use_container_width=True)


def export_page(dq_indicator, dq_unit, dq_outliers, df_derived):
    st.subheader("Export Data Quality Tables")
    
    st.markdown("""
    Download individual DQ tables as CSV files for further analysis.
    """)
    
    def to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            "📊 Download Indicator DQ", 
            to_csv(dq_indicator), 
            "dq_indicator.csv",
            help="Indicator-level completeness and quality metrics"
        )
        st.download_button(
            "📍 Download Unit DQ", 
            to_csv(dq_unit), 
            "dq_unit.csv",
            help="Unit-level reporting completeness"
        )
    
    with col2:
        st.download_button(
            "⚠️ Download Outliers", 
            to_csv(dq_outliers), 
            "dq_outliers.csv",
            help="Flagged outlier records with z-scores"
        )
        st.download_button(
            "📈 Download Derived Indicators", 
            to_csv(df_derived), 
            "derived_indicators.csv",
            help="Computed percentage indicators"
        )

# ------------------------------------------------------------
# MAIN APP
# ------------------------------------------------------------
def main():
    st.set_page_config("AHEAD Data Quality Dashboard", layout="wide")
    st.title("AHEAD – Integrated Data Quality Dashboard")

    # Check for required files
    if not os.path.exists(DQ_EXCEL_PATH):
        st.error(f"❌ Required file not found: {DQ_EXCEL_PATH}")
        st.info("Please run the data quality pipeline first to generate required files.")
        st.stop()

    # Load data
    try:
        dq_indicator, dq_unit, dq_duplicates, dq_outliers, df_derived = load_dq_data(DQ_EXCEL_PATH)
        dq_unit_geo = load_geo_data(DQ_GEO_PATH)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    tabs = [
        "🏠 Overview",
        "📊 Indicators", 
        "🏥 Units", 
        "🔥 DQ Heatmap",
        "🗺️ Map", 
        "⚠️ Outliers", 
        "📈 Derived Indicators", 
        "💾 Export"
    ]

    tab = st.sidebar.radio("Select View", tabs)

    # Display global KPIs in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Global KPIs")
    kpi = compute_global_kpis(dq_indicator, dq_unit)
    
    st.sidebar.metric("Avg Completeness", f"{kpi['avg_pct_reported']:.1f}%")
    st.sidebar.metric("Median % Outliers", f"{kpi['median_pct_outliers']:.2f}%")
    st.sidebar.metric("High Missing (>10%)", kpi["indicators_high_missing"])
    st.sidebar.metric("Low Reporting (<80%)", kpi["units_low_reporting"])

    # Route to appropriate page
    if tab == "🏠 Overview":
        st.markdown("""
        ### Welcome to the AHEAD Data Quality Dashboard
        
        This dashboard provides comprehensive data quality analytics for health and HIV programs.
        
        **Navigation Guide:**
        - 📊 **Indicators**: Analyze indicator-level quality metrics
        - 🏥 **Units**: Review facility reporting completeness
        - 🔥 **DQ Heatmap**: Visual comparison across indicators
        - 🗺️ **Map**: Geographic distribution of anomalies
        - ⚠️ **Outliers**: Detailed outlier records for verification
        - 📈 **Derived Indicators**: Cleaned percentage indicators
        - 💾 **Export**: Download analysis tables
        
        **Quick Stats:**
        """)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            kpi_card("Indicators Monitored", str(len(dq_indicator)))
        with col2:
            kpi_card("Reporting Units", str(len(dq_unit)))
        with col3:
            kpi_card("Outliers Flagged", f"{len(dq_outliers):,}")
        with col4:
            kpi_card("Duplicates Removed", f"{len(dq_duplicates):,}")
            
    elif tab == "📊 Indicators":
        indicators_page(dq_indicator)
    elif tab == "🏥 Units":
        units_page(dq_unit, dq_outliers)
    elif tab == "🔥 DQ Heatmap":
        heatmap_page(dq_indicator)
    elif tab == "🗺️ Map":
        map_page(dq_unit_geo, dq_outliers)
    elif tab == "⚠️ Outliers":
        outliers_page(dq_outliers)
    elif tab == "📈 Derived Indicators":
        derived_page(df_derived)
    elif tab == "💾 Export":
        export_page(dq_indicator, dq_unit, dq_outliers, df_derived)


if __name__ == "__main__":
    main()
