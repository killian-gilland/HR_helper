# 🎯 G-Sheet Analyst: HR Recruitment Edition

**Transform recruitment data into actionable intelligence. Zero manual reporting.**

---

## 📋 What This Does

GSheet Analyst automatically analyzes candidate pools stored in Google Sheets and sends **weekly recruitment reports** with:

✅ **Top Talent Identification** - Ranks candidates by experience + skill match + availability  
✅ **Pool Health Assessment** - Identifies gaps and risks  
✅ **Executive Insights** - AI-powered analysis (Claude/GPT) with actionable next steps  
✅ **Automated Delivery** - Reports sent via email on schedule  

**Price Target:** €49-99/month per recruitment firm

---

## 🏗️ Architecture

```
Google Sheets (Candidate Data)
    ↓
GSheetConnector (fetch + retry logic)
    ↓
KPICalculator (experience, skill match, availability scores)
    ↓
LLMAnalyzer (Claude/GPT - generate executive summary)
    ↓
EmailDelivery (formatted HTML report)
    ↓
HR Manager's Inbox
```

**Tech Stack:**
- **Ingestion:** Python + gspread (no servers 24/7)
- **Processing:** Pandas (in-memory, < 1s for 100 candidates)
- **Intelligence:** Anthropic Claude 3 (€0.003 per analysis)
- **Delivery:** Google Cloud Functions + Cloud Scheduler
- **Cost:** ~€0.10/analysis on GCP (very profitable margin)

---

## 🚀 Quick Start

### 1. Local Setup

```bash
# Clone repo
cd g-sheet-analyst-hr

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your credentials
# ANTHROPIC_API_KEY, GSHEET_URL, EMAIL_PASSWORD, etc.
```

### 2. Prepare Your Google Sheet

Create a sheet called "Candidats" with columns:
```
| Nom                | Email              | années_exp | compétences                      | disponibilité |
|--------------------|--------------------|------------|----------------------------------|---------------|
| Alice Durand       | alice@email.com    | 5          | Python, SQL, Data Analysis       | Immédiat      |
| Bob Laurent        | bob@email.com      | 2          | JavaScript, React, Node.js       | 2024-02-15    |
| Claire Moreau      | claire@email.com   | 8          | Python, SQL, Project Management  | Immédiat      |
```

**Supported columns (case-insensitive, French/English):**
- `nom` / `name` - Candidate name
- `email` - Email address
- `années_exp` / `years_exp` - Years of experience
- `compétences` / `skills` - Comma-separated skills
- `disponibilité` / `availability` - Availability date or "Immédiat"

### 3. Run Locally

```bash
python src/main.py
```

**Output:**
```json
{
  "status": "success",
  "metrics": {
    "total_candidates": 42,
    "candidates_immediately_available": 18,
    "average_match_percentage": 72.5,
    "average_years_experience": 4.2,
    "tier_distribution": {
      "EXCELLENT": 8,
      "GOOD": 15,
      "AVERAGE": 14,
      "WEAK": 5
    }
  },
  "insights": "🎯 TOP TALENTS:\n- Alice Durand...",
  "top_candidates": [...]
}
```

### 4. Deploy to Google Cloud

```bash
# Install Cloud SDK
gcloud init

# Create Cloud Function
gcloud functions deploy recruitment_analyzer \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point recruitment_analyzer \
  --source src/ \
  --memory 512MB \
  --timeout 60

# Schedule weekly execution
gcloud scheduler jobs create http recruitment-analysis \
  --schedule="0 9 * * MON" \
  --time-zone="Europe/Paris" \
  --uri="https://REGION-PROJECT_ID.cloudfunctions.net/recruitment_analyzer?action=analyze" \
  --http-method=GET
```

---

## 📊 Key Metrics Calculated

### Experience Score (0-100)
- < 1 year: 20
- 1-2 years (Junior): 40
- 2-5 years (Mid-level): 65
- 5-10 years (Senior): 85
- > 10 years (Expert): 100

### Skill Match (%)
Compares required skills vs. candidate skills  
Example: 4/6 skills = 67%

### Overall Rank Score (0-100)
Weighted: Experience (35%) + Skill Match (50%) + Availability (15%)

### Rank Tiers
- **EXCELLENT:** 80-100 → Interview immediately
- **GOOD:** 65-79 → Interview this week
- **AVERAGE:** 45-64 → Add to pipeline
- **WEAK:** < 45 → Re-source

---

## 🧠 LLM Analysis (Claude 3 Haiku)

The system sends **pre-digested KPI data** to Claude, not raw sheets:

```json
{
  "total_candidates": 42,
  "average_match_percentage": 72.5,
  "candidates_immediately_available": 18,
  "top_3_candidates": [
    {
      "name": "Alice Durand",
      "years_experience": 5,
      "experience_score": 85,
      "match_percentage": 100,
      "rank_tier": "EXCELLENT"
    },
    ...
  ]
}
```

Claude then analyzes and outputs:
```
🎯 TOP TALENTS:
- Alice Durand (100% match, 5 years, available now) → Schedule interview tomorrow
- Bob Laurent (83% match, available in 2 weeks) → Add to pipeline

⚠️ CRITICAL GAPS:
- Only 2/42 candidates have project management skills
- Average experience: 4.2 years (gap for senior role)

📊 POOL HEALTH: 55/100 - AVERAGE
Reason: Low senior representation, good junior pipeline

👉 NEXT ACTIONS:
1. Interview Alice immediately (ROI: high)
2. Launch senior-level recruitment campaign
3. Add Bob to follow-up list for in 2 weeks
```

---

## 💾 Configuration

### config/config.json

```json
{
  "gsheet_url": "https://docs.google.com/spreadsheets/d/...",
  "worksheet_name": "Candidats",
  "llm_provider": "anthropic",
  "required_skills": ["python", "sql", "data analysis", ...],
  "email_config": {
    "sender_email": "recruitment@yourdomain.com",
    "recipients": ["hr@yourdomain.com"],
    "send_on_schedule": true
  }
}
```

### Environment Variables (.env)

```bash
GCP_PROJECT_ID=my-gcp-project
ANTHROPIC_API_KEY=sk-ant-...
GSHEET_URL=https://docs.google.com/spreadsheets/d/...
EMAIL_SENDER=recruitment@yourdomain.com
EMAIL_PASSWORD=app-specific-password
EMAIL_RECIPIENTS=hr@yourdomain.com
```

---

## 🔧 Customization

### Change Required Skills

Edit `config/config.json`:
```json
{
  "required_skills": [
    "django", "postgresql", "aws",
    "rest apis", "docker", "leadership"
  ]
}
```

The calculator will automatically match candidate skills against this list.

### Use OpenAI Instead of Claude

```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-...
```

### Add Custom KPI Logic

Extend `KPICalculator` in `src/modules/kpi_calculator.py`:

```python
def _calculate_candidate_metrics(self, row: pd.Series):
    # ... existing code ...
    
    # Add custom metric
    github_repos = int(row.get("github_repos", 0))
    github_score = min(github_repos * 10, 100)
    
    # Adjust overall score
    overall_rank = (... + github_score * 0.10)
```

---

## 📧 Email Report Format

Recipients receive an HTML email with:

1. **Header** - Report date/time
2. **Key Insights** - LLM-generated summary
3. **Metric Cards** - Total candidates, available, avg match, avg experience
4. **Top Candidates** - Top 5 with detailed stats
5. **Footer** - Contact info

---

## 🧪 Testing

### Local Test

```bash
# Requires GSHEET_URL and ANTHROPIC_API_KEY in .env
python src/main.py
```

### Cloud Function Test

```bash
# Test the HTTP endpoint
curl "https://REGION-PROJECT_ID.cloudfunctions.net/recruitment_analyzer?action=health_check"

# Run analysis
curl "https://REGION-PROJECT_ID.cloudfunctions.net/recruitment_analyzer?action=analyze"

# List available worksheets
curl "https://REGION-PROJECT_ID.cloudfunctions.net/recruitment_analyzer?action=list_sheets&gsheet_url=https://docs.google.com/spreadsheets/d/..."
```

---

## 🚨 Troubleshooting

### "No data found"
- Ensure worksheet name matches exactly (case-sensitive)
- Check that first row has headers
- Verify data is not filtered/hidden in Google Sheets

### "API error (401)"
- Service account key is invalid or expired
- Check Google Secret Manager has correct key
- Verify key has `sheets.readonly` scope

### "LLM timeout"
- Claude API is slow (rare)
- Increase Cloud Function timeout: `--timeout=120`
- Check network connectivity

### Email not sent
- SMTP credentials invalid (use app-specific password for Gmail)
- Recipients list is empty
- Check spam folder

---

## 💡 Product Strategy

### Pitch to HR Firms

*"Stop wasting 4 hours/week on manual candidate reviews. Get AI-powered candidate ranking delivered to your inbox every Monday for €59/month."*

**ROI:**
- Recruiter at €45/hour saves 4h/week = €180/month
- Payback period: 3 days
- Margin: 70%+

### Upsell Ideas

1. **Tier 2 (€99/month):** Custom integrations (LinkedIn, Indeed APIs)
2. **Tier 3 (€199/month):** Custom AI prompts + private training data
3. **Enterprise:** On-premises deployment + white-label

---

## 📁 File Structure

```
g-sheet-analyst-hr/
├── src/
│   ├── main.py                 # Local orchestration script
│   ├── cloud_function.py       # Google Cloud Function handler
│   └── modules/
│       ├── gsheet_connector.py # Google Sheets integration
│       ├── kpi_calculator.py   # Recruitment metrics
│       ├── llm_analyzer.py     # Claude/GPT analysis
│       ├── email_delivery.py   # Email sending
│       └── __init__.py
├── config/
│   └── config.json             # Configuration
├── tests/
│   └── test_*.py               # Unit tests (optional)
├── data/
│   └── sample_candidates.csv   # Demo data
├── requirements.txt
├── .env.example
├── app.yaml                    # Cloud Function config
└── README.md
```

---

## 📞 Support

For issues or feature requests, file an issue on GitHub or contact: support@gsheet-analyst.dev

---

**Made with ❤️ for HR Recruitment Teams**  
*Automate the boring, focus on talent.*
