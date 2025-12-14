# AHEAD – Integrated Data Quality Analytics & Dashboard

**Country-Focused Data Quality Assessment for Health & HIV Programs**

This repository provides a complete, reproducible data quality analytics package developed under the UNICEF AHEAD Project. It supports country teams and analysts to assess, interpret, and act on data quality issues using standardized metrics, automated pipelines, and an interactive Streamlit dashboard.

The package is designed for both analyst-driven exploration and country-level automation, ensuring transparency, trust, and operational usability.

---

## 🚀 Quick Start (5 Minutes to First Run)

**Fastest path from zero to running pipeline:**

```bash
# 1. Clone and navigate
git clone <repository-url>
cd ahead-integrated-analytics

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Mac/Linux/Git Bash
# OR: .venv\Scripts\activate  # Windows CMD

# 3. Install packages
pip install -r requirements.txt

# 4. Create .env file (replace with your credentials)
echo 'DB_CONN=postgresql+psycopg2://user:pass@host:5432/db' > .env

# 5. Test connection
python -c "from dotenv import load_dotenv; import os; from sqlalchemy import create_engine; load_dotenv(); create_engine(os.environ['DB_CONN']).connect(); print('✓ Connected')"

# 6. Run pipeline
python run_pipeline.py

# 7. Launch dashboard
streamlit run dq_dashboard_app.py
```

**⚠️ CRITICAL:** If you have special characters in your password (like `@`, `#`, `%`), you MUST encode them:
- `@` → `%40`
- `#` → `%23`  
- `%` → `%25`

**Example:** Password `MyP@ss#123` becomes `MyP%40ss%23123`

---

## Overview

This package delivers:

- **Automated data quality assessment** (completeness, missingness, outliers, negative values)
- **Country-ready Excel Data Quality Workbook** for offline review
- **Geo-enabled Streamlit dashboard** for interactive exploration
- **Dual execution modes**: Notebook (interactive) and Script (automated)

---

## Key Outputs

Running the pipeline produces:

1. **`dq_review_<country>_level<N>.xlsx`**  
   → Excel data quality workbook with multiple sheets:
   - Indicator-level completeness
   - Unit-level completeness
   - Duplicates summary
   - Outliers flagged
   - Derived indicators

2. **`dq_unit_with_outliers.parquet`**  
   → Unit-level geo dataset with lat/lon for Streamlit map visualization

---

## Repository Structure

```
ahead-integrated-analytics/
│
├── integrated_pipeline.ipynb      # Main analysis notebook
├── run_pipeline.py                 # Automated script version
├── dq_dashboard_app.py            # Streamlit dashboard
├── Data_id_12_10_25.csv           # Indicator mapping file
├── config.yaml                     # DHIS2 configuration
├── .env                            # Database credentials (not in repo)
├── README.md                       # This file
└── requirements.txt                # Python dependencies
```

**Note:** Actual file organization may vary based on deployment needs.

---

## Prerequisites

### Required
- Python 3.12+
- PostgreSQL database access (AHEAD DB)
- Git
- Internet access (for dependency installation)

### Recommended
- Virtual environment (venv or conda)
- Git Bash (Windows users)
- VS Code or Jupyter Lab

---

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/<your-org>/ahead-integrated-analytics.git
cd ahead-integrated-analytics
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 🪟 **Windows-Specific Installation**

**If you encounter installation issues on Windows:**

```bash
# Install psycopg2-binary explicitly (instead of psycopg)
pip install psycopg2-binary

# If geopandas fails, install dependencies first
pip install numpy pandas shapely pyproj
pip install geopandas

# Then install remaining requirements
pip install -r requirements.txt
```

**Common Windows issues:**
- **`ModuleNotFoundError: No module named 'psycopg'`**  
  → Solution: `pip install psycopg2-binary`
  
- **`ImportError: no pq wrapper available`**  
  → Solution: Use `psycopg2` in .env, not `psycopg`
  
- **`error: Microsoft Visual C++ 14.0 or greater is required`**  
  → Solution: Install packages with `--only-binary` flag or use conda

#### ✅ **Verify Installation**

```bash
# Check all critical packages installed
pip list | grep -E "pandas|sqlalchemy|geopandas|streamlit|plotly|psycopg2"
```

**Expected output:**
```
geopandas         0.14.x
pandas            2.1.x
plotly            5.x.x
psycopg2-binary   2.9.x
sqlalchemy        2.0.x
streamlit         1.x.x
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_CONN=postgresql+psycopg2://user:password@host:5432/ahead_db
```

#### ⚠️ **CRITICAL: Database Connection Format**

**Use `psycopg2` (not `psycopg`):**
```env
# ✓ CORRECT (psycopg2)
DB_CONN=postgresql+psycopg2://username:password@host:5432/database

# ✗ WRONG (psycopg - has Windows installation issues)
DB_CONN=postgresql+psycopg://username:password@host:5432/database
```

**Reason:** `psycopg` (version 3) requires additional C libraries that cause installation issues on Windows. `psycopg2-binary` is much simpler and cross-platform compatible.

#### 🔐 **Password Special Character Encoding**

If your password contains special characters, they **MUST** be URL-encoded:

| Character | Encode As | Example |
|-----------|-----------|---------|
| `@` | `%40` | `p@ss` → `p%40ss` |
| `#` | `%23` | `pass#123` → `pass%23123` |
| `%` | `%25` | `pass%word` → `pass%25word` |
| `/` | `%2F` | `pass/word` → `pass%2Fword` |
| `?` | `%3F` | `pass?123` → `pass%3F123` |

**Example:**
```env
# Original password: MyP@ss#123%
# Encoded password:  MyP%40ss%23123%25

DB_CONN=postgresql+psycopg2://user:MyP%40ss%23123%25@host:5432/db
```

#### 📝 **Format Rules - CRITICAL!**

```env
# ✓ CORRECT - No quotes, no spaces around =
DB_CONN=postgresql+psycopg2://user:pass@host:5432/db

# ✗ WRONG - Has quotes (Python will read them as part of value)
DB_CONN="postgresql+psycopg2://user:pass@host:5432/db"

# ✗ WRONG - Has spaces around =
DB_CONN = postgresql+psycopg2://user:pass@host:5432/db
```

#### ✅ **Test Your Connection**

**Before running the pipeline, test your database connection:**

```bash
python -c "from dotenv import load_dotenv; import os; from sqlalchemy import create_engine; load_dotenv(); create_engine(os.environ['DB_CONN']).connect(); print('✓ Database connected successfully')"
```

**Expected output:**
```
✓ Database connected successfully
```

**If it fails:**
- Check password encoding (special characters?)
- Verify hostname and port
- Confirm VPN connection (if required)
- Check firewall settings

**Important:** Never commit the `.env` file to version control!

### 5. Configure Country Settings

Edit `config.yaml` for your country's DHIS2 instance:

```yaml
kenya:
  iso: "ken"
  username: "your_username"
  password: "your_password"
  url: "https://hiskenya.org/api/"
  ou: "LEVEL-5"
  dxs: []
  timeout: 300
```

---

## How to Run the Pipeline

### Option 1: Notebook (Recommended for Analysts)

**Best for:** Analysts, validation workshops, exploratory analysis

1. Open `integrated_pipeline.ipynb` in Jupyter Lab or VS Code
2. Configure parameters in Section 0:
   ```python
   COUNTRY_CONFIG = "kenya"
   COUNTRY_CODE = "KEN"
   UNIT_LEVEL = 4
   DATE_MIN = None  # or "2018-01-01"
   DATE_MAX = None  # or "2024-12-31"
   ```
3. Run all cells sequentially (Ctrl+Shift+Enter)
4. Review outputs as they generate

**Advantages:**
- Step-by-step execution with intermediate results
- Easy debugging and data exploration
- Visual feedback at each stage

---

### Option 2: Script (Recommended for Automation)

**Best for:** Routine monitoring, country IT deployment, scheduled runs

**IMPORTANT:** Before using the script version, ensure you have:
- Completed notebook run at least once
- Verified all paths and configurations
- Tested database connectivity

#### Running the Script

```bash
python run_pipeline.py
```

This produces the same outputs as the notebook:
- `dq_review_<country>_level<N>.xlsx`
- `dq_unit_with_outliers.parquet`

#### Script Workflow

The script executes these steps automatically:
1. Load data from AHEAD database
2. Apply indicator mapping
3. Run quality checks (completeness, outliers, duplicates)
4. Compute derived indicators
5. Export formatted Excel workbook
6. Generate geo-enabled parquet file

**Note:** Monitor the console for progress messages and any errors.

---

## Data Quality Metrics Explained

### 1. Reporting Completeness

**Definition:** Proportion of expected records actually reported.

**Formula:**
```
Completeness (%) = (Reported Records / Expected Records) × 100
```

**Expected records** = Indicators × Units × Time periods

**Interpretation:**
- ≥ 90% → Strong reporting
- 80–89% → Moderate concern
- < 80% → High priority for follow-up

---

### 2. Missing Values

**Definition:** Expected records with no submitted value.

**Formula:**
```
Missing (%) = (Missing Records / Expected Records) × 100
```

**Key distinction:**
- Missing = Expected but not reported
- Incomplete = Reported but invalid/blank

---

### 3. Outliers

**Definition:** Values deviating significantly from expected patterns.

**Detection Method:**
- Z-score based (typically |z| > 3)
- Compared within unit over time
- Compared across peer units

**CRITICAL:** Outliers are **flagged, not removed**. They require:
1. Verification with program staff
2. Root cause analysis
3. Correction if confirmed as errors
4. Documentation if legitimate

**Common causes:**
- Data entry errors (extra zeros, decimal mistakes)
- Reporting backlogs (catch-up submissions)
- Special campaigns or outbreaks
- System migrations

---

### 4. Negative Values

**Definition:** Logically impossible negative counts.

**Interpretation:**
- Almost always indicates data quality errors
- Common sources:
  - Manual calculation errors
  - System aggregation bugs
  - Incorrect formulas

**Action required:** Immediate correction at source system.

---

### 5. Duplicates

**Definition:** Multiple records for same unit-indicator-date combination.

**Common causes:**
- Double submissions
- System syncing issues
- Data migration artifacts

**Handling:** Pipeline keeps the most recent record.

---

## Using the Streamlit Dashboard

### Prerequisites

Ensure these files exist before launching:
- `dq_dashboard_app.py`
- `dq_review_<country>_level<N>.xlsx`
- `dq_unit_with_outliers.parquet`

### Launching the Dashboard

```bash
# From project root directory
streamlit run dq_dashboard_app.py
```

The dashboard will open automatically at: `http://localhost:8501`

**Troubleshooting:**
- If port 8501 is busy: `streamlit run dq_dashboard_app.py --server.port 8502`
- If browser doesn't open: Manually navigate to the URL shown in terminal

---

### Dashboard Tabs Guide

| Tab | Purpose | Key Features |
|-----|---------|--------------|
| **Indicators** | Indicator-level DQ metrics | Filter by type, rank by metric, identify worst performers |
| **Units** | Unit-level completeness | Filter by admin level, identify low-reporting facilities |
| **DQ Heatmap** | Multi-metric comparison | Visual comparison across all indicators |
| **Map** | Identify Geographic anomalies | Proportional symbol (bubble) map showing outlier distribution by location |
| **Outliers** | Record-level review | Detailed outlier list with z-scores for verification |
| **Derived Indicators** | Cleaned trend analysis | Time series of percentage-based indicators |
| **Export** | Download outputs | CSV exports of all Data Quality tables |

---

### Dashboard Navigation Tips

1. **Start with Global KPIs** (top of page)
   - Get overall health snapshot
   - Identify priority areas

2. **Drill down systematically:**
   - Indicators tab → Identify problematic indicators
   - Units tab → Find facilities needing support
   - Map tab → Geographic patterns
   - Outliers tab → Verify specific records

3. **Use filters strategically:**
   - Indicator type filters help focus on program areas
   - Admin level filters match reporting hierarchies
   - Date range in derived indicators shows trends

---

## Recommendations for Country Action

Based on typical DQ review findings, countries should:

### Immediate Actions (Week 1-2)
1. **Prioritize units with < 80% completeness**
   - Contact facility focal points
   - Identify reporting barriers
   - Provide technical support

2. **Investigate negative values**
   - Trace to source system
   - Correct at entry point
   - Document corrections

### Short-term Actions (Month 1-3)
3. **Verify persistent outliers**
   - Review with program managers
   - Confirm legitimate vs. errors
   - Update if confirmed accurate

4. **Address systematic gaps**
   - Missing indicator patterns
   - Geographic reporting gaps
   - Calendar alignment issues

### Long-term Actions (Ongoing)
5. **Institutionalize quarterly DQ reviews**
   - Schedule regular dashboard reviews
   - Integrate into M&E workflows
   - Track improvement trends

6. **Use derived indicators cautiously**
   - Only after DQ verification
   - Document known limitations
   - Apply appropriate filters

---

## Using the Excel Workbook

The Excel output supports:
- Offline stakeholder reviews
- Ministry documentation requirements
- Archival compliance

### Recommended Workflow

1. **Review "completeness_indicator" sheet**
   - Identify indicators with high missingness
   - Note patterns by indicator type

2. **Review "completeness_unit" sheet**
   - Flag facilities needing follow-up
   - Group by admin level for targeted support

3. **Validate "outliers" sheet**
   - Sort by z-score magnitude
   - Cross-check with program knowledge
   - Document verification decisions

4. **Correct upstream errors**
   - Work with facility staff
   - Fix in source DHIS2 system
   - Re-run pipeline after corrections

5. **Use "derived_indicators" sheet**
   - Only after verifying numerator/denominator quality
   - Apply appropriate interpretation caveats

---

## Troubleshooting

### Common Issues

#### **Database Connection Issues**

**Issue:** `ModuleNotFoundError: No module named 'geopandas'` (or any other package)  
**Solution:** 
```bash
pip install -r requirements.txt
# Or install specific package:
pip install geopandas
```

**Issue:** `ModuleNotFoundError: No module named 'psycopg'`  
**Solution:**
```bash
pip install psycopg2-binary
# AND update .env to use psycopg2 (not psycopg)
DB_CONN=postgresql+psycopg2://user:pass@host:5432/db
```

**Issue:** `ImportError: no pq wrapper available`  
**Solution:** Change database driver in `.env`:
```bash
# Change from psycopg to psycopg2
DB_CONN=postgresql+psycopg2://user:pass@host:5432/db
```

**Issue:** `KeyError: 'DB_CONN'` or `DB_CONN not found in environment variables`  
**Solution:** 
1. Verify `.env` file exists in project root
2. Check format (no quotes, no spaces):
   ```env
   DB_CONN=postgresql+psycopg2://user:pass@host:5432/db
   ```
3. Test: `cat .env` should show the DB_CONN line

**Issue:** `sqlalchemy.exc.OperationalError: connection refused` or `could not connect to server`  
**Solution:**
1. Check VPN connection (if required)
2. Verify hostname and port are correct
3. Test connectivity: `ping your-database-host.com`
4. Check password encoding for special characters
5. Verify firewall allows connection on port 5432

**Issue:** Database connects but query fails with `column "value_clean" does not exist`  
**Solution:** This has been fixed in the latest version of `run_pipeline.py`. The script now correctly queries the `value` column and renames it to `value_clean` for processing.

#### **File and Path Issues**

**Issue:** `FileNotFoundError: [Errno 2] No such file or directory: '.env'`  
**Solution:** Create the `.env` file in the project root directory:
```bash
echo 'DB_CONN=postgresql+psycopg2://user:pass@host:5432/db' > .env
```

**Issue:** `FileNotFoundError: Data_id_12_10_25.csv`  
**Solution:** 
1. Verify the CSV file is in the project directory
2. Or update the filename in the script/notebook configuration

**Issue:** `PermissionError: [Errno 13]` when writing Excel file  
**Solution:** 
1. Close the Excel file if it's open
2. Delete existing output file: `rm dq_review_*.xlsx`
3. Run pipeline again

#### **Windows-Specific Issues**

**Issue:** `Execution of scripts is disabled` (PowerShell)  
**Solution:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue:** Virtual environment won't activate on Windows  
**Solution:**
```bash
# Use Git Bash instead of PowerShell:
source .venv/bin/activate

# Or in CMD:
.venv\Scripts\activate.bat
```

**Issue:** `error: Microsoft Visual C++ 14.0 or greater is required`  
**Solution:** Use pre-built binaries:
```bash
pip install --only-binary :all: package_name
# Or install Visual C++ Build Tools from Microsoft
```

#### **Data Quality Issues**

**Issue:** `ModuleNotFoundError: No module named 'ahead_etl'`  
**Solution:** This is optional. The warning can be ignored. If you want to install it:
```bash
pip install ahead-etl
```

**Issue:** Streamlit shows "Geo file not found"  
**Solution:** Run the pipeline first to generate the parquet file:
```bash
python run_pipeline.py
```

**Issue:** Map doesn't display any points  
**Solution:** 
1. Verify `lat`/`lon` columns exist in parquet file
2. Check that coordinates are valid (not NaN)
3. Re-run pipeline if needed

**Issue:** Excel file is empty or has 0 rows  
**Solution:** 
1. Check that data was successfully loaded from database
2. Verify `COUNTRY_CODE` and `UNIT_LEVEL` are correct
3. Check date filters aren't too restrictive
4. Review console output for errors

**Issue:** Percentages show over 100% (like 1273%)  
**Solution:** This was a bug in earlier versions. Update to the latest `run_pipeline.py` which stores percentages correctly.

**Issue:** Dashboard shows 0-1 instead of 0-100% for derived indicators  
**Solution:** This has been fixed in the latest version. Update `run_pipeline.py` and `dq_dashboard_app.py`.

#### **Performance Issues**

**Issue:** Pipeline runs very slowly (>30 minutes)  
**Solution:**
1. Add date filters to reduce data volume:
   ```python
   DATE_MIN = "2023-01-01"
   DATE_MAX = "2024-12-31"
   ```
2. Use script mode instead of notebook
3. Close other applications
4. Check database server load

**Issue:** Out of memory errors  
**Solution:**
1. Add date filters to process less data
2. Increase system RAM if possible
3. Process data in chunks (requires code modification)

---

## File Size Considerations

For large datasets (> 1 million observations):
- Notebook execution may take 10-30 minutes
- Excel file may be 10-50 MB
- Consider adding date filters to reduce scope
- Use script mode for better memory management

---

## 📊 Understanding Your Results

### Quick Interpretation Guide

After running the pipeline, you'll have two main outputs:

**1. Excel File (`dq_review_[country]_level[N].xlsx`)**
- 5 sheets with different quality dimensions
- Percentages show 0-100% (e.g., 95.4%)
- Lower percentages = more issues

**2. Interactive Dashboard**
- Visual exploration of quality metrics
- Geographic visualization of outliers
- Trend analysis for derived indicators

### Key Metrics Explained

**Completeness (%):** How much data is reported vs expected
- ✅ **80-100%:** Excellent reporting
- 🟡 **60-79%:** Good, some gaps
- 🟠 **40-59%:** Fair, significant gaps
- 🔴 **<40%:** Poor, urgent action needed

**Outliers (%):** Percentage of statistically unusual values
- ✅ **0-2%:** Excellent quality
- 🟡 **2-5%:** Good, minor issues
- 🟠 **5-10%:** Fair, investigate
- 🔴 **>10%:** Poor, urgent review

**For detailed interpretation guidance, see:** [INTERPRETATION_GUIDE.md](INTERPRETATION_GUIDE.md)

This comprehensive guide includes:
- How to read each dashboard tab
- What actions to take based on findings
- Common scenarios and responses
- Monthly review checklist
- Benchmarks and targets

---

## Support & Maintenance

### Getting Help

1. Check this README first
2. Review notebook comments and markdown cells
3. Contact project team (details below)

### Reporting Issues

When reporting problems, include:
- Error message (full traceback)
- Country and data period
- Steps to reproduce
- Environment details (Python version, OS)

---

## Contact & Support

**UNICEF Health and HIV Analytics Unit (HHU) within DAPM**

**Project Technical Contact:**  
Dr. Amobi Onovo  
HIV Data Scientist, Integrated Analytics  
UNICEF AHEAD Project  
Email: aonovo@unicef.org

**Project Context:**  
Integrated Analytics Consultancy for Data Quality Assessment

---

## License

MIT License  
© 2025 UNICEF AHEAD Project

---

**v1.0 (December 2024)** - Initial Release
- ✅ Core DQ metrics implementation
- ✅ Excel export functionality
- ✅ Streamlit dashboard with interactive map
- ✅ Automated pipeline script
- ✅ Notebook for interactive analysis

**Recommended Future Enhancements:**
- Automated email alerts for critical DQ issues
- Multi-country comparison dashboard
- Advanced outlier detection (ML-based)
- Integration with DHIS2 data quality app
- Trend analysis and forecasting

---

**Last Updated:** December 13, 2024  
**Document Version:** 1.1  
**Pipeline Version:** 1.1  
**Status:** Production-Ready ✅
