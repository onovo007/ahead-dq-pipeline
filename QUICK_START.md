# AHEAD DATA QUALITY PIPELINE - QUICK START GUIDE

**For Country Teams & Non-Technical Users**

---

## ⚡ FASTEST WAY TO GET STARTED (5 Minutes)

### Step 1: Get the Files

Download or copy all these files to a folder on your computer:
- `run_pipeline.py`
- `dq_dashboard_app.py`
- `Data_id_12_10_25.csv`
- `requirements.txt`

---

### Step 1.5: Create Your .env File ⚠️ CRITICAL

**Create a file named `.env` in your project folder** with your database credentials.

**IMPORTANT FORMAT RULES:**
```env
DB_CONN=postgresql+psycopg2://username:password@host:5432/database
```

**⚠️ Common Mistakes - AVOID THESE:**

```env
# ✗ WRONG - Has quotes (will fail!)
DB_CONN="postgresql+psycopg2://username:password@host:5432/database"

# ✗ WRONG - Has spaces around = (will fail!)
DB_CONN = postgresql+psycopg2://username:password@host:5432/database

# ✓ CORRECT - No quotes, no spaces
DB_CONN=postgresql+psycopg2://username:password@host:5432/database
```

**🔐 If Your Password Has Special Characters:**

Some characters need to be encoded:

| If password has | Change to |
|-----------------|-----------|
| @ | %40 |
| # | %23 |
| % | %25 |

**Example:**
- Original password: `MyP@ss#123`
- Encoded password: `MyP%40ss%23123`

```env
DB_CONN=postgresql+psycopg2://user:MyP%40ss%23123@host:5432/db
```

**✅ Test Your Connection:**

After creating `.env`, test it works:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ DB_CONN loaded!' if os.environ.get('DB_CONN') else '✗ DB_CONN missing!')"
```

**Expected:** `✓ DB_CONN loaded!`

---

### Step 2: Install Python Requirements

Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:

```bash
# Navigate to your project folder
cd C:\path\to\your\project

# Install required packages
pip install -r requirements.txt
```

**Wait 2-3 minutes** while packages download and install.

**🪟 Windows Users:** If you get errors, try these commands instead:

```bash
# Install database driver first (fixes common Windows error)
pip install psycopg2-binary

# Then install other packages
pip install -r requirements.txt
```

**✅ Verify Installation:**

```bash
# Check critical packages are installed
pip list | findstr "pandas sqlalchemy geopandas streamlit plotly"
```

You should see all these packages listed.

---

### Step 3: Run the Pipeline

In the same Command Prompt/Terminal:

```bash
python run_pipeline.py
```

**What happens:**
- Connects to database
- Loads your country's data
- Runs quality checks
- Creates Excel file (5-10 minutes for large datasets)
- Creates map file

**You'll see:** Progress messages showing each step

**When done:** Look for two new files:
- `dq_review_ken_level4.xlsx` (your DQ workbook)
- `dq_unit_with_outliers.parquet` (map data)

---

### Step 4: Launch the Dashboard

```bash
streamlit run dq_dashboard_app.py
```

**Your browser will open automatically** showing the dashboard!

**Default address:** http://localhost:8501

---

## 🎯 WHAT TO DO IN THE DASHBOARD

### First Time Using the Dashboard:

1. **Start with Overview Tab** 🏠
   - See overall data quality stats
   - Identify priority areas

2. **Check Map Tab** 🗺️
   - See where outliers are concentrated
   - **TRY THIS:** Select an indicator from the dropdown
   - **WATCH:** The map updates to show only those outliers!

3. **Review Indicators Tab** 📊
   - Find indicators with quality issues
   - Sort by different metrics

4. **Verify Outliers Tab** ⚠️
   - Review flagged records
   - Prepare for validation with program staff

5. **Export Tab** 💾
   - Download CSVs for offline review
   - Share with colleagues

---

## 🔧 TROUBLESHOOTING

### Problem: "ModuleNotFoundError: No module named 'X'"

**Solution:**
```bash
pip install X
```

For example:
```bash
pip install plotly      # For interactive maps
pip install geopandas   # For geographic data
pip install psycopg2-binary  # For database connection
```

---

### Problem: "ImportError: no pq wrapper available" or "No module named 'psycopg'"

**Solution (Windows users especially):**
```bash
pip install psycopg2-binary
```

Then verify your `.env` file uses `psycopg2` (not `psycopg`):
```env
DB_CONN=postgresql+psycopg2://...  ✓ CORRECT
```

---

### Problem: "KeyError: 'DB_CONN'" or "DB_CONN not found"

**Check these in order:**

1. **Does .env file exist?**
   ```bash
   # On Windows
   dir .env
   
   # On Mac/Linux
   ls -la .env
   ```

2. **Is .env format correct?**
   ```env
   # ✓ CORRECT - No quotes, no spaces
   DB_CONN=postgresql+psycopg2://user:pass@host:5432/db
   
   # ✗ WRONG - Has quotes
   DB_CONN="postgresql+psycopg2://..."
   ```

3. **Test if .env loads:**
   ```bash
   python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.environ.get('DB_CONN', 'NOT FOUND'))"
   ```

---

### Problem: "column 'value_clean' does not exist"

**Solution:** Update to the latest `run_pipeline.py` (v1.1 or higher). This bug was fixed in December 2024.

Download the updated file from your technical lead.

---

### Problem: Database connection fails or "could not connect to server"

**Check these:**
1. **Are you on the office network?** (Connect to VPN if remote)
2. **Is your password encoded correctly?**
   - If password has `@`, `#`, or `%`, you MUST encode them
   - See Step 1.5 above for encoding rules
3. **Test connection:**
   ```bash
   python -c "from dotenv import load_dotenv; import os; from sqlalchemy import create_engine; load_dotenv(); create_engine(os.environ['DB_CONN']).connect(); print('✓ Connected!')"
   ```

If connection test fails, contact your IT team.

---

### Problem: Excel shows percentages over 100% (like 1273%)

**Solution:** Update to `run_pipeline.py` v1.1 or later. This bug was fixed.

**How to check your version:**
```bash
# Look for this in the console output when running:
# "Pipeline Version: 1.1" or similar
```

---

### Problem: "Geo file not found" in Map tab

**Solution:** Run Section 9 of the notebook OR:

```bash
python run_pipeline.py  # This creates the geo file
```

The file `dq_unit_with_outliers.parquet` should appear.

---

### Problem: Dashboard doesn't open in browser

**Try:**
1. Manually go to: http://localhost:8501
2. If port busy, use different port:
   ```bash
   streamlit run dq_dashboard_app.py --server.port 8502
   ```

---

### Problem: Map doesn't update when I select indicators

**This was fixed in December 2024** in `dq_dashboard_app.py` v1.1.

**Make sure you have the latest version:**
- File should be named `dq_dashboard_app.py`
- When you select indicators, you should see: "Showing outliers for: [indicator names]"
- The map bubbles should change when you select/deselect indicators

**If still not working:**
```bash
pip install plotly --upgrade
streamlit cache clear
streamlit run dq_dashboard_app.py
```

**Still having issues?** Download the latest `dq_dashboard_app.py` from your technical lead.

---

## 📋 REGULAR WORKFLOW (Monthly/Quarterly)

### For Routine Data Quality Reviews:

**Every Month/Quarter:**

1. **Update Data** (if needed)
   ```bash
   # Just run the pipeline again
   python run_pipeline.py
   ```

2. **Review New Excel File**
   - Open `dq_review_ken_level4.xlsx`
   - Compare with previous month
   - Note improvements or new issues

3. **Launch Dashboard for Interactive Review**
   ```bash
   streamlit run dq_dashboard_app.py
   ```

4. **Prepare Actions**
   - List units with <80% completeness
   - Document outliers needing verification
   - Share findings with program teams

---

## 🎓 UNDERSTANDING THE OUTPUTS

### Excel File Sheets:

| Sheet Name | What It Shows | Action |
|-----------|--------------|---------|
| completeness_indicator | Each indicator's quality | Find worst performers |
| completeness_unit | Each facility's reporting | Contact low reporters |
| outliers | Unusual values flagged | Verify with program staff |
| duplicates | Records removed | Review for system issues |
| derived_indicators | Calculated percentages | Use for trend analysis |

---

### Dashboard Tabs Explained:

**🏠 Overview**
- Bird's eye view
- Start here every time

**📊 Indicators**
- Which indicators have issues?
- Filter by program area

**🏥 Units**
- Which region/ districts need support?
- Filter by admin level

**🔥 DQ Heatmap**
- Visual comparison
- Quick scan for problems

**🗺️ Map**
- Geographic patterns
- **Select indicators to filter!**

**⚠️ Outliers**
- Detailed record review
- For validation with clinics

**📈 Derived Indicators**
- Cleaned trend analysis
- Safe for program monitoring
- **Note:** Percentages now show correctly (0-100%) - fixed in v1.1

**💾 Export**
- Download for sharing
- Import to other tools

---

## 💡 PRO TIPS

### Tip 1: Use Filters Strategically

In the **Indicators** tab:
1. Select your program area (e.g., immunization)
2. Sort by "pct_outliers"
3. Focus on top 5-10 worst

### Tip 2: Geographic Targeting

In the **Map** tab:
1. Select specific indicators
2. Zoom to areas with many bubbles
3. Use table below map to get unit names
4. Plan targeted support visits

### Tip 3: Monthly Comparisons

Keep previous Excel files:
```
dq_review_ken_level4_2024_01.xlsx
dq_review_ken_level4_2024_02.xlsx
dq_review_ken_level4_2024_03.xlsx
```

Compare month-to-month to track improvements!

### Tip 4: Outlier Verification Workflow

1. Dashboard → Outliers tab
2. Filter to one indicator
3. Download CSV
4. Share with program manager
5. Get verification (keep/remove)
6. Document decisions

---

## 📞 WHO TO CONTACT

UNICEF Health and HIV Analytics (DAPM)

**Project Technical Contact:**  
Dr. Amobi Onovo  
HIV Data Scientist, Integrated Analytics  
UNICEF AHEAD Project  
Email: aonovo@unicef.org
---

## 🎯 KEY TAKEAWAYS

1. **Run pipeline monthly** to get fresh DQ reports
2. **Use dashboard for interactive exploration**
3. **Map filtering to explore outliers by districts** - use it!
4. **Focus on <80% completeness units** first
5. **Verify outliers before removing** them
6. **Share Excel file** with non-technical stakeholders

---

## ✅ CHECKLIST FOR SUCCESS

Before Your First DQ Review Meeting:

- [ ] Pipeline runs without errors
- [ ] Excel file opens and has 5 sheets
- [ ] Dashboard launches in browser
- [ ] Map shows points (bubbles)
- [ ] Can filter map by indicators
- [ ] Understand what each metric means
- [ ] Identified 3-5 priority issues to discuss
- [ ] Prepared action plan template

---

## 📚 ADDITIONAL RESOURCES

- Full README: See `README.md` for detailed documentation

---

**Remember:** Data quality is a journey, not a destination. Use these tools monthly to continuously improve!

---

**Last Updated:** December 13, 2024  
**Quick Start Version:** 1.1  
**Pipeline Version:** 1.1  
**Compatible with:** run_pipeline.py v1.1, dq_dashboard_app.py v1.1
