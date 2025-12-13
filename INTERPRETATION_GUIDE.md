# DATA QUALITY OUTPUTS - INTERPRETATION GUIDE

**How to Understand Your Data Quality Results**

---

## 📊 **PURPOSE OF THIS GUIDE**

This guide helps you interpret the outputs from the AHEAD Data Quality Pipeline. It explains:
- What each metric means
- How to interpret values (good vs concerning)
- What actions to take based on findings
- Real-world examples from country implementations

**Audience:** Country M&E teams, program managers, data quality focal points

---

## 🎯 **QUICK REFERENCE - INTERPRETING KEY METRICS**

### **Completeness (% of Expected Indicators Reported)**

| Value | Rating | Interpretation | Action |
|-------|--------|----------------|---------|
| 80-100% | ✅ EXCELLENT | Facility reports almost all indicators | Monitor, recognize |
| 60-79% | 🟡 GOOD | Most indicators reported | Identify gaps |
| 40-59% | 🟠 FAIR | Less than half reported | Targeted support needed |
| <40% | 🔴 POOR | Severe reporting gaps | Urgent intervention |

**Example:** "Avg Completeness: 41.4%" = FAIR - Less than half of indicators are reported on average

**Action:** Investigate which indicators are not reported and why (training? service availability? system issues?)

---

### **Outliers (% of Observations Flagged as Statistical Anomalies)**

| Value | Rating | Interpretation | Action |
|-------|--------|----------------|---------|
| 0-2% | ✅ EXCELLENT | Minimal anomalies | Review high-value outliers only |
| 2-5% | 🟡 GOOD | Some anomalies | Monthly review |
| 5-10% | 🟠 FAIR | Moderate anomalies | Investigate patterns |
| >10% | 🔴 POOR | Widespread issues | Urgent data quality intervention |

**Example:** "Median % Outliers: 0.07%" = EXCELLENT - Very few statistical anomalies

**Action:** Review outliers for data entry errors, but most data is statistically normal

---

### **Missing Data (% of Expected Values That Are Blank)**

| Value | Rating | Interpretation | Action |
|-------|--------|----------------|---------|
| 0-1% | ✅ EXCELLENT | Almost no blanks | No action needed |
| 1-5% | 🟡 GOOD | Few blanks | Monitor |
| 5-10% | 🟠 FAIR | Moderate blanks | Investigate causes |
| >10% | 🔴 POOR | Many blanks | Data collection issues |

**Example:** "High Missing (>10%): 0" = EXCELLENT - No indicators with severe missingness

**Action:** No action needed - facilities fill in data when they report

---

### **Duplicates (Identical Records Submitted Multiple Times)**

| Value | Rating | Interpretation | Action |
|-------|--------|----------------|---------|
| 0 | ✅ EXCELLENT | No duplicates | System working well |
| 1-10 | 🟡 GOOD | Minimal duplicates | Review and remove |
| 11-100 | 🟠 FAIR | Some duplicates | Check submission process |
| >100 | 🔴 POOR | Widespread duplication | System or training issue |

**Example:** "Duplicates Removed: 0" = EXCELLENT - No duplicate submissions

**Action:** No action needed - clean submission process

---

## 📈 **UNDERSTANDING DASHBOARD TABS**

### **🏠 OVERVIEW TAB**

**Purpose:** Bird's-eye view of overall data quality

**Key Metrics Explained:**

#### **1. Avg Completeness**
```
What it shows: Average % of indicators reported across all facilities
Example: 41.4%
Interpretation: Facilities report less than half of expected indicators
Action: Identify commonly unreported indicators, investigate barriers
```

#### **2. Median % Outliers**
```
What it shows: Typical outlier rate for an indicator
Example: 0.07%
Interpretation: Most indicators have very few outliers
Action: Minimal concern, review outliers to catch errors
```

#### **3. High Missing (>10%)**
```
What it shows: Number of indicators with severe missingness
Example: 0
Interpretation: When facilities report, they report completely
Action: No action needed (but see low completeness issue)
```

#### **4. Low Reporting (<80%)**
```
What it shows: Number of facilities reporting less than 80% of indicators
Example: 1,453 facilities
Interpretation: MOST facilities have reporting gaps - this is your main issue
Action: PRIORITY - Investigate why facilities don't report all indicators
```

#### **5. Outliers Flagged**
```
What it shows: Total number of statistical outliers across all data
Example: 272,162 outliers
Interpretation: Out of 3.8M observations, 7% are outliers (93% normal)
Action: Review high-value outliers first, verify with facilities
```

**Overall Story:**
```
✅ Good: Data quality is excellent when facilities report
⚠️ Concern: Only 41% of indicators are reported on average
🎯 Action: Focus on COMPLETENESS, not quality
```

---

### **📊 INDICATORS TAB**

**Purpose:** Identify which indicators have quality issues

#### **"Worst-Performing Indicators" Chart**

**How to read:**
- X-axis: `pct_outliers` (percentage of outliers)
- Y-axis: Indicator names
- Longer bars = More outliers

**Example interpretation:**
```
Chart shows:
- vitamina: 0.14% outliers
- hpv1: 0.13% outliers  
- HIV testing at L&D: 0.13% outliers

Interpretation:
✅ All <2% = EXCELLENT quality
These are "worst" relatively, but still very good in absolute terms

Think of it like:
- Student A: 98% (worst in class)
- Student B: 99%
- Student C: 99.5%
All excellent students!
```

**Action based on values:**
```
If top indicators have:
- <2% outliers: ✅ Monitor only
- 2-5% outliers: 🟡 Review quarterly
- 5-10% outliers: 🟠 Investigate patterns
- >10% outliers: 🔴 Urgent review needed
```

**Pro tip:** Sort by different columns:
- `pct_outliers` - Find indicators with data quality issues
- `pct_missing` - Find indicators with blanks
- `n_expected` - Find most important indicators (high volume)

---

### **🏥 UNITS TAB**

**Purpose:** Identify which facilities have reporting gaps

#### **"Lowest Reporting Units" Chart**

**How to read:**
- X-axis: `pct_reported` (% of indicators reported)
- Y-axis: Facility names
- Shorter bars = Worse reporting

**Example interpretation:**
```
Chart shows:
- Elwak South Ward: 37% reporting
- Thingithu Ward: 35% reporting
- Mahoo Ward: 38% reporting

Interpretation:
🔴 SEVERE reporting gaps - these facilities report less than 40%
Likely reasons:
1. Service availability (don't offer all services)
2. Training gaps (don't know how to report)
3. System issues (DHIS2 access problems)
4. Workload (too busy to report)
5. Stock-outs (can't provide services)
```

**Action plan:**

**Week 1: Contact & Understand**
```bash
1. Contact the 10 lowest-reporting facilities
2. Ask: "Why are you not reporting [specific indicators]?"
3. Categorize reasons (training vs system vs service availability)
```

**Month 1: Targeted Interventions**
```bash
1. Training for facilities with knowledge gaps
2. Fix system access for connectivity issues  
3. Adjust expected indicators if services not offered
4. Provide additional staffing support if workload issue
```

**Quarter 1: Monitor Improvement**
```bash
1. Re-run pipeline monthly
2. Track improvement in bottom 10 facilities
3. Share best practices from top performers
4. Recognize improving facilities
```

---

### **🔥 DQ HEATMAP TAB**

**Purpose:** Visual comparison across all indicators and quality dimensions

#### **How to Read the Heatmap**

**Colors:**
- 🟪 **Dark purple (0.00)** = No issues ✅
- 🟦 **Light blue (0.02-0.06)** = Minor issues ✅  
- 🟩 **Green (0.08-0.10)** = Moderate issues ⚠️
- 🟨 **Yellow (0.12-0.14)** = Higher issues ⚠️
- 🟥 **Red (>0.15)** = Severe issues 🔴

**Columns:**
1. **pct_missing** - How much data is blank?
2. **pct_negative** - How many negative values?
3. **pct_duplicates** - How many duplicates?
4. **pct_outliers** - How many statistical anomalies?

**Example interpretation:**
```
Looking at the heatmap:

Column 1 (pct_missing):
🟪 Almost all dark purple
✅ Interpretation: No missing data issues

Column 2 (pct_negative):  
🟪 All dark purple
✅ Interpretation: No negative values (good validation)

Column 3 (pct_duplicates):
🟪 All dark purple
✅ Interpretation: No duplicate records

Column 4 (pct_outliers):
🟦 Mostly light blue
🟩 Some green for vitamina, hpv1
⚠️ Interpretation: Minimal outliers, some indicators slightly higher

Overall Story:
✅ Data quality is VERY GOOD across all dimensions
The problem is NOT quality - it's completeness (41%)
```

**Action priorities:**
1. 🔴 **Red cells** = Urgent investigation needed
2. 🟨 **Yellow cells** = Review within 2 weeks
3. 🟩 **Green cells** = Monitor next month
4. 🟦 **Blue cells** = Low priority
5. 🟪 **Purple cells** = No action needed

---

### **🗺️ MAP TAB**

**Purpose:** Visualize geographic distribution of outliers

#### **How to Use the Interactive Map**

**Step 1: Select Indicators**
```
Use dropdown: "Select indicator(s) to filter outliers"
- Select 1 indicator: See where that specific indicator has issues
- Select multiple: See facilities with ANY of those indicators flagged
- Leave empty: Show ALL outliers
```

**Step 2: Interpret Geographic Patterns**

**Pattern 1: Clustered Outliers**
```
What: Many bubbles in one region
Possible causes:
1. Regional data entry training issue
2. Regional DHIS2 form configuration problem
3. Legitimate regional differences (outbreak, campaign)
Action: Contact regional supervisor to investigate
```

**Pattern 2: Scattered Outliers**
```
What: Bubbles spread across country
Possible causes:
1. Individual facility data entry errors
2. Random data quality issues
3. Natural variation
Action: Review each facility individually
```

**Pattern 3: Urban Concentration**
```
What: Many bubbles in cities/capitals
Possible causes:
1. Higher population = higher service volumes = more outliers flagged
2. Urban facilities more likely to have data entry issues
3. Better reporting = more data = more outliers detected
Action: Verify values proportional to population served
```

**Step 3: Zoom and Investigate**
```
1. Click on bubble = See facility name
2. Check table below map = Get exact values
3. Cross-reference with other indicators = Is it isolated or widespread?
4. Contact facility = Verify or correct
```

**Example interpretation:**
```
Selected indicator: eid_8wks (Early Infant Diagnosis at 8 weeks)
Map shows: 
- Heavy concentration in central region
- Scattered in western region
- Few in north/eastern

Possible interpretations:
Option 1: Data Entry Errors
- Central facilities adding extra zeros (1,000 instead of 100)
- Action: Contact and verify

Option 2: Legitimate High Values  
- Central region has higher population density
- Recent testing campaign in that region
- Action: Verify with program staff

Option 3: System Issue
- DHIS2 form issue in central region
- Action: Check if other indicators show same pattern
```

---

### **⚠️ OUTLIERS TAB**

**Purpose:** Detailed review of flagged values for verification

#### **Understanding the Outlier Columns**

**Essential columns:**
```
unit_name: Which facility?
indicator_name: Which service/data element?
date: When was this reported?
value_clean: What value was reported?
zscore: How many standard deviations from mean?
outlier_threshold_lo: Minimum acceptable value (statistically)
outlier_threshold_hi: Maximum acceptable value (statistically)
```

**Example record interpretation:**
```
Record shows:
- unit_name: Nairobi Ward
- indicator_name: ANC first visit
- date: 2024-10-01
- value_clean: 112,312
- zscore: 8.5
- outlier_threshold_lo: -167.79
- outlier_threshold_hi: 112,711.98

Interpretation:
⚠️ Value (112,312) exceeds upper threshold (112,711.98)
⚠️ Zscore of 8.5 = Very unusual (normal is -3 to +3)

Likely issues:
1. Extra zero? Should be 11,231?
2. Cumulative vs monthly report?
3. Data entered in wrong field?

Action:
📞 Call Nairobi Ward to verify
```

#### **Outlier Review Workflow**

**Step 1: Sort by Severity**
```
Sort by: zscore (descending)
Focus on: Records with zscore > 5
Why: These are the most extreme outliers
```

**Step 2: Group by Indicator**
```
Filter to one indicator at a time
Start with: Critical indicators (anc1, delivery, vaccination)
Why: Prioritize high-impact data
```

**Step 3: Download for Verification**
```
Export filtered table to CSV
Share with program managers
Request facility verification within 2 weeks
```

**Step 4: Document Decisions**
```
Track in spreadsheet:
- Facility name
- Indicator
- Original value
- Verified value
- Action taken (kept/corrected/removed)
- Notes
```

**Step 5: Update Data**
```
For confirmed errors:
1. Contact facility to correct in DHIS2
2. OR manually correct in database
3. Re-run pipeline to verify fix
```

---

### **📈 DERIVED INDICATORS TAB**

**Purpose:** Monitor cleaned percentage indicators over time

#### **How to Read Derived Indicator Charts**

**Chart elements:**
```
Y-axis: Percentage (0-100%)
X-axis: Date (monthly)
Line: 3-month moving average (smoothed trend)
```

**Example derived indicators:**
```
pct_anc4: % of women with ≥4 ANC visits (of those with ≥1 visit)
pct_skilled_del: % of deliveries with skilled attendant
pct_penta3: % completing 3 doses pentavalent vaccine
pct_fp_new: % of ANC clients accepting family planning
```

**Interpretation:**
```
Chart shows pct_anc4 over time:
- Jan 2024: 45%
- Apr 2024: 52%
- Jul 2024: 58%
- Oct 2024: 63%

Interpretation:
✅ Improving trend (45% → 63%)
✅ Moving toward 80% target
🎯 Continue current interventions
```

**Warning signs to watch for:**
```
📉 Declining trend: Investigate causes immediately
📊 Stagnant (no change): Interventions not working
📈 Spike then drop: Temporary campaign, not sustained
🎯 Below 50%: Severe service delivery issue
```

**Action based on trends:**
```
Improving (↗️):
✅ Document what's working
✅ Share best practices

Declining (↘️):
⚠️ Investigate causes
⚠️ Review facility-level data
⚠️ Check for stock-outs, staffing issues

Stagnant (→):
🟡 Reassess interventions
🟡 Try different approaches
🟡 Get program staff input
```

---

## 🎯 **COMMON SCENARIOS & HOW TO RESPOND**

### **Scenario 1: Low Completeness, Good Quality**

**What you see:**
```
Avg Completeness: 42%
Median % Outliers: 0.05%
High Missing: 0
Duplicates: 0
```

**Interpretation:**
```
✅ Data that exists is high quality
⚠️ Most indicators are not reported at all
🎯 Problem: Completeness, not quality
```

**Actions:**
```
Week 1:
- Identify top 10 unreported indicators
- Survey 20 facilities to understand why

Month 1:
- Provide targeted training
- Fix system access issues
- Adjust expected indicators if needed

Quarter 1:
- Monitor completeness improvement
- Target: 60% within 3 months
```

---

### **Scenario 2: High Outliers in Specific Indicator**

**What you see:**
```
Most indicators: <1% outliers
HIV testing at L&D: 15% outliers
```

**Interpretation:**
```
⚠️ ONE indicator has severe issues
✅ Other indicators are fine
🎯 Problem: Likely data entry or form issue
```

**Actions:**
```
Week 1:
- Review outlier records for HIV testing
- Check if all from same region/facilities
- Look for patterns (all same date? same error type?)

Week 2:
- Contact affected facilities
- Verify values or identify error source
- Check DHIS2 form configuration

Month 1:
- Correct identified errors
- Retrain if needed
- Re-run pipeline to verify fix
```

---

### **Scenario 3: Geographic Clustering of Outliers**

**What you see:**
```
Map shows: All outliers in western region
Other regions: Clean data
```

**Interpretation:**
```
⚠️ Regional issue, not national
Possible causes:
1. Regional training issue
2. Regional DHIS2 configuration
3. Regional campaign or outbreak (legitimate)
```

**Actions:**
```
Week 1:
- Contact regional supervisor
- Ask: "Did anything change in reporting?"
- Check: Recent trainings? System changes?

Week 2:
- Review regional DHIS2 form
- Compare with other regions
- Test data entry process

Month 1:
- Standardize forms if configuration issue
- Retrain if training issue
- Document if legitimate (campaign)
```

---

### **Scenario 4: Sudden Change in Derived Indicator**

**What you see:**
```
pct_anc4 trend:
- Jan-Aug: Stable at 55%
- Sep: Drops to 35%
- Oct: Still at 35%
```

**Interpretation:**
```
⚠️ Sudden significant drop
Unlikely to be real program decline
Likely causes:
1. Denominator changed (ANC1 overreported)
2. Numerator changed (ANC4 underreported)
3. System or reporting change
```

**Actions:**
```
Immediate:
- Check raw data for ANC1 and ANC4
- Look for: Data entry errors, system changes
- Verify with program staff

Week 1:
- Identify affected facilities
- Review September reports specifically
- Contact facilities to verify

Week 2:
- Correct if error found
- Document if system change
- Adjust baseline if legitimate
```

---

## 📋 **MONTHLY DQ REVIEW CHECKLIST**

Use this checklist for regular data quality reviews:

### **Week 1: Run Pipeline**
```
☐ Run: python run_pipeline.py
☐ Verify: Both output files created
☐ Open: dq_review_[country]_level[N].xlsx
☐ Open: Dashboard (streamlit run dq_dashboard_app.py)
```

### **Week 2: Review Metrics**
```
☐ Check: Overall completeness (target: >60%)
☐ Check: Outlier rate (target: <5%)
☐ Check: Missing data rate (target: <5%)
☐ Check: Duplicates (target: 0)
☐ Identify: Top 5 worst-performing indicators
☐ Identify: Top 10 lowest-reporting facilities
```

### **Week 3: Investigation**
```
☐ Contact: 5 lowest-reporting facilities
☐ Review: Top 100 highest-value outliers
☐ Analyze: Geographic patterns on map
☐ Compare: Month-over-month trends
☐ Document: Key findings and causes
```

### **Week 4: Action Planning**
```
☐ Develop: Action plan for identified issues
☐ Assign: Responsibilities and deadlines
☐ Schedule: Follow-up for next month
☐ Share: Results with program teams
☐ Recognize: Improving facilities
```

---

## 📊 **BENCHMARKS & TARGETS**

### **Completeness Targets**

| Timeframe | Target | Status |
|-----------|--------|--------|
| Month 1 | Establish baseline | - |
| Month 3 | +10% from baseline | 🎯 |
| Month 6 | +20% from baseline | 🎯 |
| Month 12 | ≥70% national average | 🎯 |

### **Outlier Targets**

| Metric | Target | Stretch Goal |
|--------|--------|--------------|
| National outlier rate | <5% | <2% |
| Indicators with >10% outliers | 0 | 0 |
| High-value outliers reviewed | 100% | Within 2 weeks |

### **Response Time Targets**

| Issue | Response Time |
|-------|---------------|
| Critical outlier (>10x median) | 48 hours |
| Facility <40% completeness | 1 week |
| Declining trend detected | 1 week |
| Geographic clustering | 2 weeks |
| Monthly report | End of month |

---

## 💡 **PRO TIPS**

### **Tip 1: Compare Month-to-Month**
```bash
# Save files with dates
dq_review_ken_level4_2024_10.xlsx
dq_review_ken_level4_2024_11.xlsx
dq_review_ken_level4_2024_12.xlsx

# Compare completeness trends
# Track improvement in bottom 10 facilities
```

### **Tip 2: Use Map for Field Visits**
```bash
# Plan support visits based on map
1. Filter to critical indicators
2. Zoom to region you're visiting
3. Identify clusters of outliers
4. Schedule verification visits
5. Bring printouts for field staff
```

### **Tip 3: Focus on High-Impact Indicators**
```bash
# Prioritize quality improvement for:
✓ High-volume indicators (ANC, delivery)
✓ National targets (90-90-90 for HIV)
✓ Donor-reported indicators (PEPFAR, GAVI)
✓ Policy-critical indicators (maternal mortality)
```

### **Tip 4: Celebrate Improvements**
```bash
# Monthly recognition for:
✓ Most improved facility (completeness)
✓ Best quality maintenance (lowest outliers)
✓ Highest overall performance
✓ Regional champions

# Share success stories
# Document best practices
```

### **Tip 5: Use Filters Strategically**
```bash
# In Indicators tab:
1. Filter by program area (immunization)
2. Sort by pct_outliers (descending)
3. Focus on top 5 worst
4. Investigate causes
5. Develop targeted interventions
```

---

## 📞 **GETTING HELP**

### **Technical Issues**
- Contact: **UNICEF Health & HIV Unit (HHU) within DAPM*
- Email: Send an email
- Include: Error message, screenshot, steps to reproduce

  
 **project Technical Contact**  
 Dr. Amobi Onovo  
 HIV Data Scientist, Integrated Analytics  
 UNICEF AHEAD project  
 Email: aonovo@unicef.org

---

## 🎓 **KEY TAKEAWAYS**

1. **Completeness ≠ Quality**
   - You can have high quality but low completeness
   - Both need attention, but different interventions

2. **Context Matters**
   - Outliers might be legitimate (campaigns, outbreaks)
   - Always verify before removing
   - Talk to program staff

3. **Geographic Patterns Tell Stories**
   - Clusters = Systematic issues
   - Scattered = Random errors
   - Use map to prioritize interventions

4. **Trends Over Snapshots**
   - One month is a data point
   - Three months is a trend
   - Six months is a pattern
   - Track improvement over time

5. **Focus on Actionable**
   - Worst 10 facilities (not all 1,453)
   - Top 5 indicators (not all 43)
   - Highest 100 outliers (not all 272k)
   - What you can actually fix this month

---

**Remember:** The goal is not perfect data - it's continuous improvement! 🎯

---

**Document Version:** 1.0  
**Last Updated:** December 13, 2024  
**Compatible with:** Pipeline v1.1, Dashboard v1.1
