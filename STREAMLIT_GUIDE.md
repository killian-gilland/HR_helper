# 🎯 Streamlit Recruitment Analyst - User Guide

## Overview

The **Recruitment Analyst** is an interactive web application built with Streamlit that helps you:

- ✅ Upload candidate data (Excel or CSV files)
- 📝 Configure job requirements (manually or auto-detect from job announcements)
- 🤖 Get AI-powered insights using Gemini
- 📊 Rank and filter candidates with full control
- 📥 Export reports in multiple formats
- 📧 Send results via email

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
```

### 3. Run the Application
```bash
python run_app.py
```

Or directly:
```bash
streamlit run app_streamlit.py
```

The app will open at `http://localhost:8501`

---

## Features

### 📁 Step 1: Upload Data

1. Click "Upload Excel or CSV file" in the sidebar
2. Select your candidate file

**Required Columns:**
- `nom` or `name` - Candidate name
- `email` - Email address
- `années_exp` or `years_exp` - Years of experience
- `compétences` or `skills` - List of skills
- `disponibilité` or `availability` - Availability date or "Immédiat"

**Example Format:**
```
nom,email,années_exp,compétences,disponibilité
Alice Durand,alice@example.com,5,Python;SQL;AWS,Immédiat
Bob Martin,bob@example.com,3,Java;Spring,2024-02-15
```

---

### 💼 Step 2: Configure Job Requirements

#### Option A: Auto-Detect from Job Announcement
1. Check "📝 Use Job Announcement Text?"
2. Paste the full job announcement
3. Click "🔍 Analyze Announcement"
4. AI will extract top 5-7 required skills automatically

#### Option B: Manual Entry
1. Enter skills as comma-separated list: `Python, SQL, AWS, Machine Learning`
2. Set minimum years of experience with the slider

---

### 🔬 Step 3: Run Analysis

1. Click **📈 Run Analysis** - KPI calculations start
2. (Optional) Click **🧠 Generate AI Insights** - Get Gemini analysis
3. View results in the main area

---

### 🎯 Step 4: Control Candidate Selection

**Customize Results:**
- **Slider**: Choose how many top candidates to display (1-50)
- **Filter by Tier**: Select EXCELLENT, GOOD, AVERAGE, or WEAK
- **Include Unavailable**: Toggle to show unavailable candidates

---

### 📊 Results Dashboard

#### Candidate Rankings Table
Shows all analyzed candidates with:
- Rank position
- Name & Email
- Experience and skill match percentage
- Availability timeline
- Overall score (0-100)
- Tier classification

#### Candidate Details Cards
Click on any candidate to expand and see:
- Experience score breakdown
- Skill match details
- Availability status
- Overall ranking

#### Pool Statistics
- Total candidates analyzed
- Immediately available count
- Average skill match percentage
- Average experience level
- **Tier Distribution Chart** - Visual breakdown by quality tier
- **Availability Distribution Pie Chart** - Who's available now vs. later

#### AI Executive Summary
If insights were generated, see:
- Top talent highlights
- Critical skills gaps
- Pool health assessment
- Recommended next actions

---

### 💾 Export & Actions

#### Download Reports
- **📊 Excel Report**: Full analysis with multiple sheets
  - Candidates sheet with all metrics
  - Summary statistics sheet
  
- **📄 CSV Export**: Lightweight candidate list for spreadsheet tools

#### Email Report
- **📧 Send via Email**: Automatically formats and sends to configured recipients
- If no email credentials: Saves as `LAST_REPORT.html` in your project folder

---

## Configuration Details

### Job Requirements Config
```json
{
  "required_skills": ["Python", "SQL", "AWS"],
  "min_years_exp": 2,
  "email_recipients": ["recruiter@company.com"]
}
```

### Candidate Scoring

**Overall Score = (35% Experience + 50% Skill Match + 15% Availability)**

**Tier Classification:**
- 🟢 **EXCELLENT**: Score ≥ 80
- 🔵 **GOOD**: Score 65-79
- 🟡 **AVERAGE**: Score 45-64
- 🔴 **WEAK**: Score < 45

---

## AI Features

### Job Announcement Analysis
Automatically extracts required skills from unstructured job posting text. Uses Claude/Gemini to identify:
- Technical skills
- Tools and technologies
- Experience level requirements
- Soft skills

### Candidate Insights
Generates a structured analysis including:
- 🎯 Top talent tier identification
- ⚠️ Critical skill gaps in pool
- 📊 Overall pool health assessment
- 👉 Actionable recruitment recommendations

---

## Tips & Best Practices

### 📋 Data Quality
- Ensure consistent column naming (see Required Columns section)
- Date formats: `YYYY-MM-DD` or text like "Immédiat"
- Skills: Comma or semicolon separated
- Experience: Numbers only (handles "5 years", "5 ans", etc.)

### 🎯 Getting Better Results
1. **Be specific with skills** - Use exact tool names (e.g., "AWS" not "Cloud")
2. **Test the auto-detection** - Paste a real job posting to see what skills are extracted
3. **Adjust experience threshold** - Slider lets you filter by minimum requirement
4. **Use filters** - Combine tier and availability filters for fine-tuning

### 📧 Email Setup
For Gmail:
1. Enable 2-factor authentication
2. Create an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password in `.env` (not your Google password)

For other email providers:
- Use SMTP credentials from your email service
- Update `EmailDelivery` class if needed

---

## Troubleshooting

### App won't start
```bash
# Check if Streamlit is installed
pip list | grep streamlit

# Reinstall if needed
pip install streamlit --upgrade
```

### "GEMINI_API_KEY not found"
- Verify `.env` file exists in project root
- Check key format (no extra spaces or quotes)
- Regenerate key at [Google AI Studio](https://aistudio.google.com)

### Candidate file won't load
- Check file format (`.xlsx`, `.xls`, or `.csv`)
- Verify column names match expected format
- Check for special characters in headers
- Try saving Excel file in newer format

### AI insights not generating
- Check GEMINI_API_KEY is valid
- Verify internet connection
- Check Gemini API quota limits
- See logs in terminal for detailed errors

### Email not sending
- Verify EMAIL_SENDER and EMAIL_PASSWORD in `.env`
- For Gmail: Ensure you're using App Password, not Google password
- Check recipient email addresses are valid
- If credentials missing: Report saves as HTML file instead

---

## File Reference

| File | Purpose |
|------|---------|
| `app_streamlit.py` | Main Streamlit application |
| `run_app.py` | Launcher script |
| `src/modules/kpi_calculator.py` | Candidate scoring logic |
| `src/modules/llm_analyzer.py` | AI insights generation |
| `src/modules/email_delivery.py` | Email sending functionality |
| `.env` | Environment variables (create this) |
| `requirements.txt` | Python dependencies |

---

## Example Workflow

### Scenario: Hiring a Senior Data Engineer

1. **Upload Data**
   - Upload `candidates.xlsx` with 50 candidates

2. **Configure Requirements**
   - Paste job announcement: "We're looking for a Senior Data Engineer with 5+ years..."
   - Click "Analyze Announcement"
   - AI extracts: Python, SQL, Spark, AWS, Airflow, Kubernetes

3. **Set Minimum Experience**
   - Set slider to 5 years minimum

4. **Run Analysis**
   - Click "Run Analysis" → 50 candidates scored
   - Click "Generate AI Insights" → Gemini analyzes pool

5. **Select Top Candidates**
   - Slider set to 15 candidates
   - Filter: EXCELLENT + GOOD tiers only
   - Uncheck "Include Unavailable"
   - Shows 8 immediately-available candidates matching well

6. **Export Results**
   - Download Excel report for detailed metrics
   - Send via email to hiring team
   - Attach top 3 detailed profiles

---

## Advanced Usage

### Batch Processing
To analyze multiple job openings:
1. Create separate CSV files for each job
2. Run app once per file
3. Export all reports
4. Compare talent pools across roles

### Custom Scoring
Edit `kpi_calculator.py` to adjust weights:
```python
# Current: 35% Experience, 50% Skills, 15% Availability
# Change to: 25% Experience, 60% Skills, 15% Availability
overall_rank = (exp_score * 0.25 + match_pct * 0.60 + availability_days / 30 * 0.15)
```

### API Integration
Use the underlying modules in your own scripts:
```python
from src.modules import KPICalculator, create_analyzer

calculator = KPICalculator(config={"required_skills": ["Python"]})
metrics_list, stats = calculator.calculate_all_metrics(df)
analyzer = create_analyzer("gemini")
insights = analyzer.generate_insights(stats, metrics_list)
```

---

## Support

For issues or questions:
1. Check logs in terminal (Streamlit output)
2. Review `.env` configuration
3. Verify file format matches requirements
4. Test with sample data from `tests/generate_dataset.py`

---

**Happy Hiring! 🎯**
