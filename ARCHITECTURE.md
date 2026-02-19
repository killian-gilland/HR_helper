# 📊 G-Sheet Analyst: Technical Architecture

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HR RECRUITMENT ANALYST                              │
└─────────────────────────────────────────────────────────────────────────────┘

INPUT LAYER:
┌──────────────┐
│ Google Sheet │  (Candidate data: name, email, exp, skills, availability)
│  (Candidats) │
└──────┬───────┘
       │ gspread library
       │ (with retry logic)
       ▼
┌────────────────────────────────────┐
│   GSheetConnector Module           │
│  - Fetch data                      │
│  - Handle API retries              │
│  - Return DataFrame                │
└────────┬─────────────────────────────┘
         │ pd.DataFrame
         ▼
PROCESSING LAYER:
┌────────────────────────────────────┐
│   KPICalculator Module             │
│  ✓ Experience Score (0-100)        │
│  ✓ Skill Match (%)                 │
│  ✓ Availability (days)             │
│  ✓ Overall Rank Score              │
│  ✓ Tier Assignment (EXCELLENT/...) │
│  ✓ Aggregate Statistics            │
└────────┬─────────────────────────────┘
         │ List[CandidateMetrics] + Dict
         │ (Scored, ranked candidates)
         ▼
┌────────────────────────────────────┐
│   LLMAnalyzer Module               │
│  - Send to Claude/OpenAI           │
│  - Executive summary generation    │
│  - Top talent identification       │
│  - Gap analysis                    │
│  - Action items                    │
└────────┬─────────────────────────────┘
         │ String (insights)
         ▼
OUTPUT LAYER:
┌────────────────────────────────────┐
│  EmailDelivery Module              │
│  - Format HTML                     │
│  - Metrics cards                   │
│  - Top candidates                  │
│  - Send via SMTP                   │
└────────┬─────────────────────────────┘
         │ Email (HTML)
         ▼
┌──────────────┐
│ HR Manager   │  (Receives: Top talent, gaps, next steps)
│   Inbox      │
└──────────────┘


DEPLOYMENT OPTIONS:
┌─────────────────────────────────────────────────────────────────────────────┐
│  LOCAL (Development)                │  CLOUD (Production)                     │
├─────────────────────────────────────┼─────────────────────────────────────────┤
│  python src/main.py                 │  Google Cloud Function (HTTP)           │
│  - One-off analysis                 │  - Triggered by Cloud Scheduler         │
│  - Manual execution                 │  - Fully automated weekly               │
│  - Local .env file                  │  - Secret Manager for credentials       │
│  - Direct email                     │  - Serverless (cost: ~€0.05/run)        │
└─────────────────────────────────────┴─────────────────────────────────────────┘
```

---

## Data Flow Example

```
STEP 1: Fetch
┌────────────────────────────────────┐
│ Google Sheet (50 candidates)       │
│ nom | email | years | skills | ... │
└────────────┬───────────────────────┘
             │ GSheetConnector.fetch()
             ▼
┌────────────────────────────────────┐
│ Pandas DataFrame (50 rows)         │
└────────────────────────────────────┘

STEP 2: Score
┌────────────────────────────────────┐
│ For each candidate:                │
│ - Parse years → exp_score (0-100)  │
│ - Match skills → match_pct (%)     │
│ - Check availability → days        │
│ - Weighted rank → overall_score    │
└────────────────────────────────────┘

STEP 3: Rank
┌────────────────────────────────────┐
│ Sort by overall_score DESC         │
│ 1. Alice (92/100) EXCELLENT        │
│ 2. Claire (88/100) EXCELLENT       │
│ 3. Emma (76/100) GOOD              │
│ ...                                │
│ 50. John (32/100) WEAK             │
└────────────────────────────────────┘

STEP 4: Analyze
┌────────────────────────────────────┐
│ Send to Claude:                    │
│ {                                  │
│   "total_candidates": 50,          │
│   "top_3": [...],                  │
│   "avg_match": 72%,                │
│   "pool_health": 78/100            │
│ }                                  │
│                                    │
│ Get back:                          │
│ "🎯 TOP TALENTS: Alice (100%)..."  │
│ "⚠️ GAPS: Need more senior..."     │
│ "👉 NEXT: Interview Alice today"   │
└────────────────────────────────────┘

STEP 5: Deliver
┌────────────────────────────────────┐
│ Beautiful HTML email:              │
│ ├─ Header                          │
│ ├─ Insights (from Claude)          │
│ ├─ Metrics cards                   │
│ ├─ Top 5 candidates                │
│ └─ Footer                          │
│                                    │
│ → To: hr-manager@company.com       │
└────────────────────────────────────┘
```

---

## Module Dependencies

```
main.py (orchestrator)
├── modules.gsheet_connector
│   └── gspread, pandas
├── modules.kpi_calculator
│   └── pandas
├── modules.llm_analyzer
│   ├── anthropic OR openai
│   └── requests
├── modules.email_delivery
│   └── smtplib, email
└── config.json / .env


cloud_function.py (Cloud Function handler)
├── Same modules as above
├── google.cloud.storage (load config)
├── google.cloud.secretmanager (credentials)
└── functions_framework (HTTP wrapper)


tests/ (optional)
├── unittest
├── pandas
└── All modules above
```

---

## API Contracts

### GSheetConnector

```python
def fetch_candidates_data(
    sheet_url: str,
    worksheet_name: str = "Candidats"
) -> pd.DataFrame:
    """
    Returns DataFrame with columns:
    - nom/name (str)
    - email (str)
    - années_exp/years_exp (float)
    - compétences/skills (str, comma-separated)
    - disponibilité/availability (str, date or "Immédiat")
    """
```

### KPICalculator

```python
def calculate_all_metrics(
    df: pd.DataFrame
) -> Tuple[List[CandidateMetrics], Dict]:
    """
    Returns:
    - List of CandidateMetrics (sorted by rank)
    - Dict with aggregate statistics
    """

CandidateMetrics:
    name: str
    email: str
    years_experience: float
    experience_score: float (0-100)
    skill_match_count: int
    match_percentage: float
    availability_days: int
    overall_rank_score: float (0-100)
    rank_tier: str ("EXCELLENT", "GOOD", "AVERAGE", "WEAK")
```

### LLMAnalyzer

```python
def generate_insights(
    metrics_dict: Dict,
    candidate_list: List[Dict]
) -> Dict:
    """
    Input: Aggregated statistics + top candidates
    Output: {
        "analysis": "🎯 TOP TALENTS: ...",
        "metrics_summary": {...},
        "top_candidates": [...],
        "generated_at": "2024-01-07T09:00:00"
    }
    """
```

### EmailDelivery

```python
def send_insights_email(
    recipient_emails: List[str],
    subject: str,
    insights_text: str,
    metrics_summary: dict,
    top_candidates: list,
    attachment_path: Optional[str] = None
) -> bool:
    """
    Sends HTML email with metrics, insights, and candidate details
    Returns: True if successful, False otherwise
    """
```

---

## Error Handling Strategy

```
Pipeline Execution:
├── Success
│   └── Email sent ✅
│
├── Recoverable Error (retry)
│   ├── Google Sheets API timeout
│   │   └── Retry 3 times with 2s delay
│   └── LLM API temporary failure
│       └── Retry once, log warning
│
├── Data Quality Error
│   ├── No candidates found
│   │   └── Log error, skip analysis, notify ops
│   └── Invalid column format
│       └── Parse error, suggest column mapping
│
└── Critical Error (stop, alert)
    ├── Invalid credentials
    │   └── Check Secret Manager
    ├── Email delivery failure
    │   └── Check SMTP credentials
    └── Cloud Function deployment error
        └── Check IAM permissions
```

---

## Performance Characteristics

```
Candidate Count | KPI Calc | LLM Call | Email | Total
────────────────┼──────────┼──────────┼───────┼─────
10              | 50ms     | 2s       | 1s    | ~3.5s
50              | 200ms    | 2s       | 1s    | ~3.5s
100             | 400ms    | 2s       | 1s    | ~3.5s
500             | 1.5s     | 2s       | 1s    | ~4.5s

Bottleneck: LLM API call (Claude/OpenAI takes ~2s)
Solution: Cache results if same data, async processing for large pools

Storage Usage:
- Per candidate: ~500 bytes (score + metadata)
- 1,000 candidates: ~500 KB
- 1 year of data (weekly): ~25 MB
- BigQuery not needed for <3 month history
```

---

## Security Considerations

```
Authentication:
├── Google Sheets: Service account key (JSON)
│   └── Stored in Secret Manager
├── LLM API: API key (Anthropic/OpenAI)
│   └── Stored in Secret Manager + environment
└── Email: SMTP password
    └── Stored in Secret Manager

Authorization:
├── Cloud Function service account
│   ├── secretmanager.secretAccessor
│   ├── storage.objectViewer
│   └── sheets.readonly
└── Cloud Scheduler service account
    └── cloudfunctions.invoker

Data Privacy:
├── No personal data stored (only in emails)
├── No data in BigQuery (cost optimization)
├── Audit trail: Cloud Logging
├── GDPR compliant: No tracking/profiling
└── CCPA compliant: Can delete all data on request
```

---

## Scaling Considerations

```
Current Limits:
├── Cloud Function: 512 MB memory, 120s timeout
├── Google Sheets API: 500 requests/100 seconds
├── Claude API: 10 API calls/minute (paid tier)
└── Email: 500/day (Gmail limit)

Scaling Strategies:
├── Move KPI calculation to Dataflow (for >10k candidates)
├── Cache LLM results (if same data, use previous analysis)
├── Batch email processing (group multiple firms)
├── BigQuery warehouse (if historical trends needed)
└── Message queue (Pub/Sub) for async processing
```

---

## Monitoring & Observability

```
Metrics to Track:
├── Cloud Function
│   ├── Execution time
│   ├── Error rate
│   └── Memory usage
├── Candidate Analysis
│   ├── Candidates processed
│   ├── Average rank score
│   └── Tier distribution
├── Email Delivery
│   ├── Send success rate
│   └── Bounce rate
└── Cost
    ├── API cost (Claude/OpenAI)
    ├── Cloud cost
    └── Total COGS per customer

Alerts:
├── Cloud Function errors > 1%
├── Email delivery failure
├── API quota exceeded
└── Cost spike > expected
```

---

**For detailed deployment, see DEPLOYMENT.md**  
**For business strategy, see BUSINESS_MODEL.md**  
**For quick start, see QUICKSTART.md**
