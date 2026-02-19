"""
QUICK START: Get G-Sheet Analyst Running in 5 Minutes
"""

# ==============================================================================
# OPTION 1: Run Demo (No Setup)
# ==============================================================================

python demo.py

# Output: Shows sample analysis with dummy data
# Time: < 1 minute
# Use case: Understand what the product does


# ==============================================================================
# OPTION 2: Local Setup (Testing)
# ==============================================================================

# 1. Setup environment
pip install -r requirements.txt
cp .env.example .env

# 2. Edit .env with YOUR values:
#    - ANTHROPIC_API_KEY (from https://console.anthropic.com)
#    - GSHEET_URL (your Google Sheet)
#    - EMAIL_SENDER, EMAIL_PASSWORD (Gmail credentials)
#    - EMAIL_RECIPIENTS

# 3. Prepare Google Sheet with columns:
#    nom, email, années_exp, compétences, disponibilité

# 4. Run analysis
python src/main.py

# 5. Check your email (or output in terminal)
# Time: 5-10 minutes
# Use case: Test before deploying to cloud


# ==============================================================================
# OPTION 3: Deploy to Google Cloud (Production)
# ==============================================================================

# Follow DEPLOYMENT.md step-by-step

# Key commands:
gcloud functions deploy recruitment_analyzer \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point recruitment_analyzer

gcloud scheduler jobs create http recruitment-analysis \
  --schedule="0 9 * * MON" \
  --uri="https://region-project.cloudfunctions.net/recruitment_analyzer?action=analyze"

# Time: 30 minutes (first time)
# Use case: Automated weekly reports
# Cost: ~€0.40/month


# ==============================================================================
# FILE STRUCTURE EXPLAINED
# ==============================================================================

g-sheet-analyst-hr/
├── src/
│   ├── main.py                      # Local orchestration (python main.py)
│   ├── cloud_function.py            # Cloud Function handler (deploy to GCP)
│   └── modules/
│       ├── gsheet_connector.py      # Fetch data from Google Sheets
│       ├── kpi_calculator.py        # Score candidates (experience, skills)
│       ├── llm_analyzer.py          # Generate insights using Claude/OpenAI
│       ├── email_delivery.py        # Send formatted HTML email
│       └── __init__.py
│
├── config/
│   └── config.json                  # Configuration (GSheet URL, emails, etc.)
│
├── data/
│   └── sample_candidates.csv        # Sample data for testing
│
├── tests/
│   └── test_kpi_calculator.py       # Unit tests
│
├── .env.example                      # Template for environment variables
├── app.yaml                          # Google Cloud config
├── requirements.txt                  # Python dependencies
├── demo.py                           # Run without setup
│
├── README.md                         # Product documentation
├── DEPLOYMENT.md                     # Cloud deployment guide
├── BUSINESS_MODEL.md                 # Pricing, sales, roadmap
└── QUICKSTART.md                     # This file


# ==============================================================================
# WHAT EACH MODULE DOES
# ==============================================================================

1. GSheetConnector
   - Fetches candidate data from Google Sheets
   - Handles API retries and errors
   - Returns pandas DataFrame

2. KPICalculator
   - Scores experience (0-100)
   - Calculates skill match (%)
   - Determines availability (days)
   - Ranks candidates (EXCELLENT/GOOD/AVERAGE/WEAK)
   - Outputs aggregate statistics

3. LLMAnalyzer
   - Takes scored candidates + metrics
   - Sends to Claude/OpenAI for analysis
   - Gets executive summary back
   - Identifies top talent, gaps, next actions

4. EmailDelivery
   - Formats results as beautiful HTML
   - Includes metrics, charts, top candidates
   - Sends via SMTP (Gmail, company email, etc.)

5. Main Orchestrator
   - Ties everything together
   - Error handling
   - Logging
   - Both local (main.py) and cloud (cloud_function.py)


# ==============================================================================
# SAMPLE OUTPUT
# ==============================================================================

INPUT (Google Sheet):
┌────────────────────┬─────────────────────┬──────────┬───────────────────┬──────────────┐
│ nom                │ email               │ années   │ compétences       │ disponibilité│
├────────────────────┼─────────────────────┼──────────┼───────────────────┼──────────────┤
│ Alice Durand       │ alice@email.com     │ 5        │ Python, SQL, ...  │ Immédiat     │
│ Bob Laurent        │ bob@email.com       │ 2        │ JavaScript, React │ 2024-02-15   │
│ Claire Moreau      │ claire@email.com    │ 8        │ Python, SQL, ML   │ Immédiat     │
└────────────────────┴─────────────────────┴──────────┴───────────────────┴──────────────┘

PROCESSING:
1. Parse data → 3 candidates
2. Score experience → 5y=85, 2y=40, 8y=85
3. Match skills → 100%, 50%, 100%
4. Calculate availability → 0d, 15d, 0d
5. Rank → EXCELLENT, AVERAGE, EXCELLENT

KPI OUTPUT:
{
  "total_candidates": 3,
  "candidates_immediately_available": 2,
  "average_match_percentage": 83.3,
  "average_years_experience": 5.0,
  "tier_distribution": {
    "EXCELLENT": 2,
    "GOOD": 0,
    "AVERAGE": 1,
    "WEAK": 0
  }
}

CLAUDE ANALYSIS:
🎯 TOP TALENTS:
- Alice Durand (100% match, 5 years, available now)
- Claire Moreau (100% match, 8 years, available now)

⚠️ CRITICAL GAPS:
- Only 1/3 have project management skills
- Junior representation: 1/3

📊 POOL HEALTH: 82/100 (GOOD)

👉 NEXT ACTIONS:
1. Interview Alice & Claire this week
2. Continue sourcing juniors + PM skills

EMAIL REPORT:
Sent to: hr-manager@company.com
Subject: 🎯 Weekly Recruitment Report - 3 Candidates


# ==============================================================================
# COMMON CUSTOMIZATIONS
# ==============================================================================

Change Required Skills:
├─ Edit config/config.json
└─ Update "required_skills" array

Use OpenAI Instead of Claude:
├─ Set LLM_PROVIDER=openai in .env
├─ Add OPENAI_API_KEY
└─ Code handles it automatically

Add Custom KPI:
├─ Edit src/modules/kpi_calculator.py
├─ Add new scoring logic in _calculate_candidate_metrics()
├─ Adjust overall_rank calculation

Change Email Design:
├─ Edit src/modules/email_delivery.py
├─ Modify _build_html_content()
└─ Update CSS styles in HTML template


# ==============================================================================
# DEPLOYMENT FLOW
# ==============================================================================

LOCAL TESTING:
1. python demo.py → See how it works
2. python src/main.py → Real data
3. Check email inbox

CLOUD DEPLOYMENT:
1. gcloud services enable ... → Enable GCP APIs
2. gcloud secrets create ... → Store credentials securely
3. gcloud functions deploy ... → Deploy code
4. gcloud scheduler jobs create ... → Schedule weekly runs
5. Test with curl → Verify it works
6. Monitor logs → Check for errors

Manual triggers:
curl "https://region-project.cloudfunctions.net/recruitment_analyzer?action=analyze"

View logs:
gcloud functions logs read recruitment_analyzer --limit=50


# ==============================================================================
# PRICING & BUSINESS MODEL
# ==============================================================================

Target Customer: Recruitment Firms (10-50 recruiters)

Monthly Cost to Operate:
├─ Cloud Functions: €0.05
├─ Claude API: €0.01
├─ Secret Manager: €0.30
└─ TOTAL: €0.36/customer/month

Selling Price: €49-99/month

Gross Margin: 80-85%

Time to Launch MVP: 1 week
Time to First Sale: 2 weeks
Payback Period: 1 week

See BUSINESS_MODEL.md for full go-to-market strategy


# ==============================================================================
# TROUBLESHOOTING
# ==============================================================================

"ModuleNotFoundError: No module named 'anthropic'"
└─ Run: pip install -r requirements.txt

"Error: Google Sheets API access denied"
└─ Check GOOGLE_CREDENTIALS in .env
└─ Verify service account has sheets.readonly scope

"Email not sent"
└─ Check EMAIL_SENDER, EMAIL_PASSWORD in .env
└─ Use Gmail app-specific password, not regular password
└─ Check EMAIL_RECIPIENTS is comma-separated

"No data found in worksheet"
└─ Worksheet name must match exactly (case-sensitive)
└─ First row should be headers
└─ Data must be in "Candidats" worksheet (default)

"LLM timeout"
└─ Increase timeout: --timeout=120 in Cloud Function deployment
└─ Check internet connection
└─ Try again (APIs have transient failures)

More help: See README.md and DEPLOYMENT.md


# ==============================================================================
# NEXT STEPS
# ==============================================================================

1. Run demo.py to understand the product
2. Create a Google Sheet with test data
3. Get API keys:
   - Anthropic: https://console.anthropic.com
   - Gmail: Generate app password
4. Update .env with your credentials
5. Run: python src/main.py
6. Review email report
7. Deploy to GCP (see DEPLOYMENT.md)
8. Set up Cloud Scheduler for weekly reports
9. Start selling to recruitment firms!

---

Questions? Check README.md or file an issue on GitHub.
Happy recruiting! 🚀
"""
