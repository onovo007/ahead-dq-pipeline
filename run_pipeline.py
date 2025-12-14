"""
run_pipeline.py

AHEAD Integrated Data Quality Pipeline - Standalone Script Version
Executes the complete DQ analysis workflow without requiring Jupyter notebook

Author: Dr. Amobi Onovo
UNICEF AHEAD Project
Last Updated: December 2024
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import geopandas as gpd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Try to import ahead_etl package
try:
    import ahead_etl as ah
except ImportError:
    print("WARNING: ahead_etl package not found. Some functionality may be limited.")
    ah = None


# ============================================================
# CONFIGURATION
# ============================================================

class PipelineConfig:
    """Configuration for the data quality pipeline"""
    
    def __init__(self):
        # Country settings
        self.COUNTRY_CONFIG = "kenya"
        self.COUNTRY_CODE = "KEN"
        self.UNIT_LEVEL = 4
        
        # Date filters (None = use full range)
        self.DATE_MIN = None  # e.g., "2018-01-01"
        self.DATE_MAX = None  # e.g., "2024-12-31"
        
        # File paths
        self.MAP_PATH = Path("Data_id_12_10_25.csv")
        self.DQ_EXCEL_PATH = f"dq_review_{self.COUNTRY_CODE.lower()}_level{self.UNIT_LEVEL}.xlsx"
        self.DQ_GEO_PATH = "dq_unit_with_outliers.parquet"
        
        # IQR multiplier for outlier detection
        self.IQR_MULTIPLIER = 1.5
        
    def validate(self):
        """Validate configuration and file existence"""
        if not self.MAP_PATH.exists():
            raise FileNotFoundError(f"Indicator mapping file not found: {self.MAP_PATH}")
        
        if "DB_CONN" not in os.environ:
            raise ValueError("DB_CONN not found in environment variables. Check .env file.")
        
        print("✓ Configuration validated successfully")


# ============================================================
# DATA LOADING
# ============================================================

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    print("✓ Environment variables loaded")


def create_db_engine():
    """Create SQLAlchemy database engine"""
    db_conn = os.environ["DB_CONN"]
    engine = create_engine(db_conn)
    print(f"✓ Database engine created")
    return engine


def load_indicator_mapping(map_path: Path) -> pd.DataFrame:
    """Load and standardize indicator mapping CSV"""
    print(f"\nLoading indicator mapping from: {map_path}")
    
    # Read CSV
    df_map = pd.read_csv(map_path)
    
    # Standardize column names
    df_map = df_map.rename(columns={
        "indicator_code/ data_id": "indicator_code",
        "data_elements/ indicator_type": "indicator_type"
    })
    
    # Select required columns
    required_cols = ["indicator_code", "indicator_name", "indicator_type"]
    df_map = df_map[required_cols].copy()
    
    print(f"✓ Loaded {len(df_map)} indicator mappings")
    print(f"  Sample: {df_map.head(3)['indicator_type'].tolist()}")
    
    return df_map


def load_raw_data(engine, config: PipelineConfig, df_map: pd.DataFrame) -> pd.DataFrame:
    """Load raw data from AHEAD database"""
    print(f"\nLoading data for {config.COUNTRY_CODE}, level {config.UNIT_LEVEL}...")
    
    # Build SQL query
    query = """
    SELECT
        country_code,
        country_name,
        unit_code,
        unit_name,
        unit_level,
        indicator_code,
        indicator_name,
        date,
        value
    FROM observation
    WHERE country_code = %(country_code)s
      AND unit_level = %(unit_level)s
    """
    
    params = {
        "country_code": config.COUNTRY_CODE,
        "unit_level": config.UNIT_LEVEL
    }
    
    # Add date filters if specified
    if config.DATE_MIN:
        query += " AND date >= %(date_min)s"
        params["date_min"] = config.DATE_MIN
    
    if config.DATE_MAX:
        query += " AND date <= %(date_max)s"
        params["date_max"] = config.DATE_MAX
    
    # Execute query
    df_raw = pd.read_sql(query, con=engine, params=params)
    
    # Rename 'value' to 'value_clean' to match pipeline expectations
    if 'value' in df_raw.columns:
        df_raw = df_raw.rename(columns={'value': 'value_clean'})
    
    print(f"✓ Loaded {len(df_raw):,} raw observations")
    
    # Join with indicator mapping
    df_raw = df_raw.merge(
        df_map[["indicator_code", "indicator_type"]],
        on="indicator_code",
        how="left"
    )
    
    # Report unmapped indicators
    n_unmapped = df_raw["indicator_type"].isna().sum()
    if n_unmapped > 0:
        print(f"⚠ Warning: {n_unmapped:,} observations without indicator_type mapping")
    
    return df_raw


# ============================================================
# DATA QUALITY CHECKS
# ============================================================

def flag_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Flag missing value_clean as True/False"""
    df = df.copy()
    df["flag_missing"] = df["value_clean"].isna()
    return df


def flag_negative_values(df: pd.DataFrame) -> pd.DataFrame:
    """Flag and replace negative values with NaN"""
    df = df.copy()
    df["flag_negative"] = (df["value_clean"] < 0) & df["value_clean"].notna()
    df.loc[df["flag_negative"], "value_clean"] = np.nan
    return df


def remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Remove duplicates, keeping most recent record"""
    df = df.copy()
    
    # Identify duplicates
    subset = ["country_code", "unit_code", "indicator_code", "date"]
    df["flag_duplicate"] = df.duplicated(subset=subset, keep="last")
    
    # Extract duplicate records for reporting
    df_duplicates = df[df["flag_duplicate"]].copy()
    
    # Remove duplicates
    df_clean = df[~df["flag_duplicate"]].copy()
    
    print(f"✓ Removed {len(df_duplicates):,} duplicate records")
    
    return df_clean, df_duplicates


def flag_outliers_iqr(df: pd.DataFrame, iqr_multiplier: float = 1.5) -> pd.DataFrame:
    """Flag outliers using IQR method within each indicator_type"""
    df = df.copy()
    df["flag_outlier"] = False
    df["outlier_threshold_lo"] = np.nan
    df["outlier_threshold_hi"] = np.nan
    
    # Group by indicator_type
    for indicator_type, group in df.groupby("indicator_type"):
        if group["value_clean"].notna().sum() < 5:
            continue  # Skip if too few values
        
        # Calculate IQR bounds
        Q1 = group["value_clean"].quantile(0.25)
        Q3 = group["value_clean"].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - iqr_multiplier * IQR
        upper_bound = Q3 + iqr_multiplier * IQR
        
        # Store thresholds for this indicator_type
        df.loc[group.index, "outlier_threshold_lo"] = lower_bound
        df.loc[group.index, "outlier_threshold_hi"] = upper_bound
        
        # Flag outliers
        outlier_mask = (
            (group["value_clean"] < lower_bound) | 
            (group["value_clean"] > upper_bound)
        ) & group["value_clean"].notna()
        
        df.loc[group.index[outlier_mask], "flag_outlier"] = True
    
    n_outliers = df["flag_outlier"].sum()
    print(f"✓ Flagged {n_outliers:,} outliers using IQR method")
    
    return df


def compute_zscore(df: pd.DataFrame) -> pd.DataFrame:
    """Compute z-scores for outlier analysis"""
    df = df.copy()
    
    # Calculate z-score within each indicator_type
    df["zscore"] = np.nan
    
    for indicator_type, group in df.groupby("indicator_type"):
        if group["value_clean"].notna().sum() < 3:
            continue
        
        mean_val = group["value_clean"].mean()
        std_val = group["value_clean"].std()
        
        if std_val > 0:
            zscores = (group["value_clean"] - mean_val) / std_val
            df.loc[group.index, "zscore"] = zscores
    
    return df


# ============================================================
# DATA QUALITY SUMMARY TABLES
# ============================================================

def compute_indicator_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute indicator-level DQ summary"""
    print("\nComputing indicator-level summary...")
    
    summary = df.groupby(["indicator_type", "indicator_code", "indicator_name"]).agg(
        n_obs=("value_clean", "size"),
        n_missing=("flag_missing", "sum"),
        n_negative=("flag_negative", "sum"),
        n_duplicates=("flag_duplicate", lambda x: 0),  # Already removed
        n_outliers=("flag_outlier", "sum"),
    ).reset_index()
    
    # Calculate percentages (store as decimals for Excel formatting)
    summary["pct_missing"] = summary["n_missing"] / summary["n_obs"]
    summary["pct_negative"] = summary["n_negative"] / summary["n_obs"]
    summary["pct_duplicates"] = 0.0  # Already removed
    summary["pct_outliers"] = summary["n_outliers"] / summary["n_obs"]
    
    print(f"✓ Generated summary for {len(summary)} indicators")
    
    return summary


def compute_unit_summary(df: pd.DataFrame, df_map: pd.DataFrame) -> pd.DataFrame:
    """Compute unit-level reporting completeness"""
    print("\nComputing unit-level summary...")
    
    # Get unique indicators
    n_indicators = df_map["indicator_type"].nunique()
    
    # Count indicators reported per unit
    unit_reporting = df.groupby(
        ["country_code", "unit_code", "unit_name", "unit_level"]
    ).agg(
        n_indicators_reported=("indicator_type", "nunique")
    ).reset_index()
    
    # Calculate completeness
    unit_reporting["n_indicators_missing"] = n_indicators - unit_reporting["n_indicators_reported"]
    unit_reporting["pct_reported"] = unit_reporting["n_indicators_reported"] / n_indicators
    
    # Add duplicate count (0 after cleaning)
    unit_reporting["n_duplicates"] = 0
    
    print(f"✓ Generated summary for {len(unit_reporting)} units")
    
    return unit_reporting


def extract_outlier_records(df: pd.DataFrame) -> pd.DataFrame:
    """Extract flagged outlier records for review"""
    print("\nExtracting outlier records...")
    
    df_outliers = df[df["flag_outlier"]].copy()
    
    # Select relevant columns (including thresholds for transparency)
    outlier_cols = [
        "country_code", "unit_code", "unit_name", "unit_level",
        "indicator_code", "indicator_name", "indicator_type",
        "date", "value_clean", "zscore",
        "outlier_threshold_lo", "outlier_threshold_hi"
    ]
    
    df_outliers = df_outliers[outlier_cols].copy()
    
    print(f"✓ Extracted {len(df_outliers):,} outlier records")
    
    return df_outliers


# ============================================================
# DERIVED INDICATORS
# ============================================================

def compute_derived_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute percentage-based derived indicators"""
    print("\nComputing derived indicators...")
    
    # Define derived indicator formulas (expanded list)
    derived_formulas = {
        # ANC coverage
        "pct_anc4": ("anc4", "anc1"),
        "pct_anc8": ("anc8", "anc1"),
        
        # Vaccination coverage
        "pct_penta3": ("penta3", "penta1"),
        "pct_measles2": ("measles2", "measles1"),
        "pct_bcg": ("bcg", "delivery"),
        
        # Delivery indicators
        "pct_skilled_del": ("skilled_del", "delivery"),
        "pct_csection": ("csection", "delivery"),
        "pct_deliveries_assisted_vag": ("deliveries_assisted_vag", "delivery"),
        "pct_deliveries_breach": ("deliveries_breach", "delivery"),
        
        # Family planning
        "pct_fp_new": ("fp_new", "anc1"),
        
        # Testing coverage
        "pct_syphilis_testing_anc": ("anc_hbv_test", "anc1"),
        "pct_hiv_testing_anc": ("anc_hiv_test", "anc1"),
        "pct_hiv_testing_pnc": ("HIV testing at PNC", "anc1"),
        "pct_hiv_testing_ld": ("HIV testing at L&D", "delivery"),
    }
    
    # Pivot to wide format
    df_wide = df.pivot_table(
        index=["country_code", "unit_code", "unit_name", "unit_level", "date"],
        columns="indicator_type",
        values="value_clean",
        aggfunc="first"
    ).reset_index()
    
    # Compute derived indicators
    indicators_computed = 0
    for derived_name, (numerator, denominator) in derived_formulas.items():
        if numerator in df_wide.columns and denominator in df_wide.columns:
            # Calculate as decimal (0-1) for Excel percentage formatting
            df_wide[derived_name] = (
                df_wide[numerator] / df_wide[denominator].replace(0, np.nan)
            )
            
            # Cap at 100% (1.0 in decimal form)
            df_wide[derived_name] = df_wide[derived_name].clip(upper=1.0)
            indicators_computed += 1
    
    print(f"✓ Computed {indicators_computed} derived indicators (from {len(derived_formulas)} formulas)")
    
    return df_wide


# ============================================================
# GEO DATA FOR MAPPING
# ============================================================

def load_unit_geometry(engine, config: PipelineConfig) -> pd.DataFrame:
    """Load unit geometry from database"""
    print("\nLoading unit geometry...")
    
    query = """
    SELECT DISTINCT
        country_code,
        unit_code,
        unit_name,
        unit_level,
        unit_geometry
    FROM observation
    WHERE country_code = %(country_code)s
      AND unit_level = %(unit_level)s
      AND unit_geometry IS NOT NULL
    """
    
    df_geo = pd.read_sql(
        query,
        con=engine,
        params={
            "country_code": config.COUNTRY_CODE,
            "unit_level": config.UNIT_LEVEL
        }
    )
    
    print(f"✓ Loaded geometry for {len(df_geo)} units")
    
    return df_geo


def compute_centroids(df_geo: pd.DataFrame) -> pd.DataFrame:
    """Compute lat/lon centroids from WKT geometry"""
    print("Computing centroids...")
    
    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df_geo,
        geometry=gpd.GeoSeries.from_wkt(df_geo["unit_geometry"]),
        crs="EPSG:4326"
    )
    
    # Extract centroids
    gdf["lon"] = gdf.geometry.centroid.x
    gdf["lat"] = gdf.geometry.centroid.y
    
    # Convert back to regular DataFrame
    df_coords = gdf[["country_code", "unit_code", "unit_name", "unit_level", "lat", "lon"]].copy()
    df_coords = df_coords.dropna(subset=["lat", "lon"])
    
    print(f"✓ Computed centroids for {len(df_coords)} units")
    
    return df_coords


def create_geo_dq_file(
    dq_unit: pd.DataFrame,
    df_outliers: pd.DataFrame,
    df_coords: pd.DataFrame,
    output_path: str
):
    """Create geo-enabled DQ file for Streamlit map"""
    print("\nCreating geo-enabled DQ file...")
    
    # Count outliers per unit
    outlier_counts = (
        df_outliers.groupby("unit_code")
        .size()
        .rename("n_outliers_unit")
        .reset_index()
    )
    
    # Merge: dq_unit + outlier counts + coordinates
    df_geo_dq = dq_unit.merge(
        outlier_counts,
        on="unit_code",
        how="left"
    ).merge(
        df_coords[["unit_code", "lat", "lon"]],
        on="unit_code",
        how="left"
    )
    
    # Fill missing outlier counts
    df_geo_dq["n_outliers_unit"] = df_geo_dq["n_outliers_unit"].fillna(0).astype(int)
    
    # Drop units without coordinates
    df_geo_dq = df_geo_dq.dropna(subset=["lat", "lon"])
    
    # Save as parquet
    df_geo_dq.to_parquet(output_path, index=False)
    
    print(f"✓ Saved geo DQ file: {output_path}")
    print(f"  {len(df_geo_dq)} units with coordinates")


# ============================================================
# EXCEL EXPORT
# ============================================================

def export_excel_workbook(
    dq_indicator: pd.DataFrame,
    dq_unit: pd.DataFrame,
    df_duplicates: pd.DataFrame,
    df_outliers: pd.DataFrame,
    df_derived: pd.DataFrame,
    output_path: str
):
    """Export formatted Excel workbook with all DQ tables"""
    print(f"\nExporting Excel workbook: {output_path}")
    
    # Create Excel writer with XlsxWriter engine
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        workbook = writer.book
        
        # Define formats
        header_fmt = workbook.add_format({
            "bold": True,
            "bg_color": "#4472C4",
            "font_color": "white",
            "border": 1
        })
        
        percent_fmt = workbook.add_format({"num_format": "0.00%"})
        
        # Write each sheet
        sheets = {
            "completeness_indicator": dq_indicator,
            "completeness_unit": dq_unit,
            "duplicates": df_duplicates,
            "outliers": df_outliers,
            "derived_indicators": df_derived
        }
        
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            
            # Format header
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_fmt)
            
            # Auto-width columns
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet.set_column(i, i, min(max_len, 40))
            
            # Freeze header
            worksheet.freeze_panes(1, 0)
            
            # Format percentage columns
            pct_cols = [i for i, c in enumerate(df.columns) if c.startswith("pct_")]
            for col_idx in pct_cols:
                worksheet.set_column(col_idx, col_idx, 12, percent_fmt)
    
    print(f"✓ Excel workbook exported successfully")
    print(f"  Sheets: {list(sheets.keys())}")


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    """Execute the complete data quality pipeline"""
    
    print("="*60)
    print("AHEAD INTEGRATED DATA QUALITY PIPELINE")
    print("="*60)
    print()
    
    try:
        # 1. Setup
        print("STEP 1: Configuration & Setup")
        print("-" * 60)
        load_environment()  # CRITICAL FIX: Load .env BEFORE config validation
        config = PipelineConfig()
        config.validate()
        engine = create_db_engine()
        
        # 2. Load Data
        print("\n" + "="*60)
        print("STEP 2: Data Loading")
        print("-" * 60)
        df_map = load_indicator_mapping(config.MAP_PATH)
        df_raw = load_raw_data(engine, config, df_map)
        
        # 3. Quality Checks
        print("\n" + "="*60)
        print("STEP 3: Data Quality Checks")
        print("-" * 60)
        df = flag_missing_values(df_raw)
        df = flag_negative_values(df)
        df, df_duplicates = remove_duplicates(df)
        df = flag_outliers_iqr(df, config.IQR_MULTIPLIER)
        df = compute_zscore(df)
        
        # 4. DQ Summaries
        print("\n" + "="*60)
        print("STEP 4: Summary Tables")
        print("-" * 60)
        dq_indicator = compute_indicator_summary(df)
        dq_unit = compute_unit_summary(df, df_map)
        df_outliers = extract_outlier_records(df)
        
        # 5. Derived Indicators
        print("\n" + "="*60)
        print("STEP 5: Derived Indicators")
        print("-" * 60)
        df_derived = compute_derived_indicators(df)
        
        # 6. Geo Data
        print("\n" + "="*60)
        print("STEP 6: Geographic Data")
        print("-" * 60)
        try:
            df_geo = load_unit_geometry(engine, config)
            df_coords = compute_centroids(df_geo)
            create_geo_dq_file(dq_unit, df_outliers, df_coords, config.DQ_GEO_PATH)
        except Exception as e:
            print(f"⚠ Warning: Could not create geo file: {e}")
            print("  Continuing without geographic data...")
        
        # 7. Export
        print("\n" + "="*60)
        print("STEP 7: Export Outputs")
        print("-" * 60)
        export_excel_workbook(
            dq_indicator,
            dq_unit,
            df_duplicates,
            df_outliers,
            df_derived,
            config.DQ_EXCEL_PATH
        )
        
        # Success
        print("\n" + "="*60)
        print("✓ PIPELINE COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"\nOutputs generated:")
        print(f"  1. {config.DQ_EXCEL_PATH}")
        if Path(config.DQ_GEO_PATH).exists():
            print(f"  2. {config.DQ_GEO_PATH}")
        print(f"\nNext steps:")
        print(f"  1. Review Excel workbook for DQ issues")
        print(f"  2. Launch Streamlit dashboard: streamlit run dq_dashboard_app.py")
        print()
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ PIPELINE FAILED")
        print("="*60)
        print(f"\nError: {e}")
        print(f"\nFull traceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
