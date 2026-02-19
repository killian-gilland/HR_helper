# 🚀 Deployment Guide - G-Sheet Analyst HR Edition

This guide covers deploying the recruitment analyzer to Google Cloud Platform (GCP) for automated weekly reports.

---

## Prerequisites

- Google Cloud Project (with billing enabled)
- `gcloud` CLI installed locally
- Service account with roles:
  - Cloud Functions Developer
  - Cloud Scheduler Admin
  - Secret Manager Admin
  - Storage Admin

---

## Step 1: Setup Google Cloud Project

```bash
# Set project ID
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  storage-api.googleapis.com \
  sheets.googleapis.com
```

---

## Step 2: Store Secrets in Secret Manager

### Create service account key for Google Sheets

1. Go to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Name: `recruitment-analyzer-sa`
4. Grant roles: `Editor`
5. Download JSON key
6. Upload to Secret Manager:

```bash
gcloud secrets create google-sheets-service-account-key \
  --replication-policy="automatic" \
  --data-file=/path/to/downloaded-key.json
```

### Store LLM API Key

```bash
gcloud secrets create anthropic-api-key \
  --replication-policy="automatic" \
  --data-file=- <<< "sk-ant-your-api-key"

# Or for OpenAI:
gcloud secrets create openai-api-key \
  --replication-policy="automatic" \
  --data-file=- <<< "sk-your-api-key"
```

### Store Email Password

```bash
gcloud secrets create email-password \
  --replication-policy="automatic" \
  --data-file=- <<< "your-app-specific-password"
```

---

## Step 3: Create Cloud Storage Bucket for Config

```bash
# Create bucket
gsutil mb gs://gs-analyst-config-${PROJECT_ID}

# Upload config.json
gsutil cp config/config.json gs://gs-analyst-config-${PROJECT_ID}/config.json

# Make it readable by Cloud Function
gsutil iam ch serviceAccount:recruitment-analyzer-sa@${PROJECT_ID}.iam.gserviceaccount.com:roles/storage.objectViewer \
  gs://gs-analyst-config-${PROJECT_ID}
```

---

## Step 4: Deploy Cloud Function

```bash
# Navigate to src directory
cd src

# Deploy function
gcloud functions deploy recruitment_analyzer \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point recruitment_analyzer \
  --memory 512MB \
  --timeout 120 \
  --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},LLM_PROVIDER=anthropic" \
  --source . \
  --region europe-west1

cd ..
```

**Output:**
```
Deploying function (may take a minute or two)...
  ✓ [###############################] 100.0%

Deployed function [recruitment_analyzer]
httpsTrigger:
  url: https://europe-west1-${PROJECT_ID}.cloudfunctions.net/recruitment_analyzer
status: ACTIVE
```

---

## Step 5: Grant Cloud Function Access to Secrets

```bash
# Get Cloud Function service account
export CF_SA="$(gcloud functions describe recruitment_analyzer \
  --region europe-west1 --format='value(serviceConfig.serviceAccountEmail)')"

# Grant Secret Accessor role
gcloud secrets add-iam-policy-binding google-sheets-service-account-key \
  --member=serviceAccount:${CF_SA} \
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member=serviceAccount:${CF_SA} \
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding email-password \
  --member=serviceAccount:${CF_SA} \
  --role=roles/secretmanager.secretAccessor

# Grant Storage access to config bucket
gsutil iam ch serviceAccount:${CF_SA}:roles/storage.objectViewer \
  gs://gs-analyst-config-${PROJECT_ID}
```

---

## Step 6: Create Cloud Scheduler Job

```bash
# Create scheduler job (Monday 9:00 AM UTC)
gcloud scheduler jobs create http recruitment-analysis \
  --schedule="0 9 * * MON" \
  --time-zone="UTC" \
  --location=europe-west1 \
  --uri="https://europe-west1-${PROJECT_ID}.cloudfunctions.net/recruitment_analyzer?action=analyze&config_bucket=gs-analyst-config-${PROJECT_ID}&config_file=config.json" \
  --http-method=GET

# If job already exists, update it:
gcloud scheduler jobs update http recruitment-analysis \
  --schedule="0 9 * * MON" \
  --time-zone="UTC" \
  --location=europe-west1 \
  --uri="https://europe-west1-${PROJECT_ID}.cloudfunctions.net/recruitment_analyzer?action=analyze&config_bucket=gs-analyst-config-${PROJECT_ID}&config_file=config.json" \
  --http-method=GET
```

### Change Schedule

```bash
# Monday at 9:00 AM Paris time (CET/CEST)
gcloud scheduler jobs update http recruitment-analysis \
  --schedule="0 8 * * MON" \
  --time-zone="Europe/Paris" \
  --location=europe-west1
```

---

## Step 7: Manual Testing

### Health Check
```bash
curl "https://europe-west1-${PROJECT_ID}.cloudfunctions.net/recruitment_analyzer?action=health_check"
```

### List Worksheets
```bash
GSHEET_URL="https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
curl "https://europe-west1-${PROJECT_ID}.cloudfunctions.net/recruitment_analyzer?action=list_sheets&gsheet_url=${GSHEET_URL}"
```

### Run Analysis Manually
```bash
curl "https://europe-west1-${PROJECT_ID}.cloudfunctions.net/recruitment_analyzer?action=analyze&config_bucket=gs-analyst-config-${PROJECT_ID}&config_file=config.json"
```

### View Cloud Function Logs
```bash
gcloud functions logs read recruitment_analyzer \
  --region=europe-west1 \
  --limit=50 \
  --follow
```

---

## Step 8: Configure Email Credentials

Update `config/config.json` in GCS bucket:

```bash
# Download current config
gsutil cp gs://gs-analyst-config-${PROJECT_ID}/config.json config/config-prod.json

# Edit config-prod.json with your values:
# - gsheet_url: Your Google Sheet URL
# - email_config.sender_email: recruitment@yourdomain.com
# - email_config.recipients: ["hr-manager@yourdomain.com"]

# Upload updated config
gsutil cp config/config-prod.json gs://gs-analyst-config-${PROJECT_ID}/config.json
```

---

## Monitoring & Logs

### View recent executions
```bash
gcloud functions logs read recruitment_analyzer \
  --region=europe-west1 \
  --limit=100

# Or view only errors:
gcloud functions logs read recruitment_analyzer \
  --region=europe-west1 \
  --limit=100 | grep -i error
```

### View scheduler job history
```bash
gcloud scheduler jobs describe recruitment-analysis --location=europe-west1

# View past executions
gcloud logging read "resource.type=cloud_scheduler_job AND resource.labels.job_id=recruitment-analysis" \
  --limit=20 \
  --format=json
```

---

## Cost Estimation

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Cloud Functions | 4 invocations/month, ~5s each | ~€0.05 |
| Cloud Scheduler | 4 jobs/month | ~€0.04 |
| Secret Manager | 3 secrets | ~€0.30 |
| Google Sheets API | 4 reads/month | ~€0.00 |
| Claude API (Haiku) | 4 analyses × €0.003 | ~€0.01 |
| **Total** | | **~€0.40/month** |

**Revenue at €59/month = Margin of 99%**

---

## Troubleshooting Deployment

### Cloud Function not accessible
```bash
# Check if function is deployed
gcloud functions describe recruitment_analyzer --region=europe-west1

# Check IAM permissions
gcloud functions get-iam-policy recruitment_analyzer --region=europe-west1
```

### Secret access denied
```bash
# Re-grant permissions
export CF_SA="$(gcloud functions describe recruitment_analyzer \
  --region europe-west1 --format='value(serviceConfig.serviceAccountEmail)')"

gcloud secrets add-iam-policy-binding google-sheets-service-account-key \
  --member=serviceAccount:${CF_SA} \
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member=serviceAccount:${CF_SA} \
  --role=roles/secretmanager.secretAccessor
```

### Configuration bucket not found
```bash
# Verify bucket exists and is accessible
gsutil ls gs://gs-analyst-config-${PROJECT_ID}/

# Check Cloud Function has read access
gsutil iam get gs://gs-analyst-config-${PROJECT_ID}
```

---

## Cleanup

```bash
# Delete Cloud Function
gcloud functions delete recruitment_analyzer --region=europe-west1

# Delete Cloud Scheduler job
gcloud scheduler jobs delete recruitment-analysis --location=europe-west1

# Delete secrets
gcloud secrets delete google-sheets-service-account-key
gcloud secrets delete anthropic-api-key
gcloud secrets delete email-password

# Delete storage bucket
gsutil -m rm -r gs://gs-analyst-config-${PROJECT_ID}
```

---

## Next Steps

1. **Test the pipeline** - Run manual analysis before scheduling
2. **Configure email** - Update recipients in `config/config.json`
3. **Schedule reports** - Adjust schedule to match business hours
4. **Monitor & iterate** - Review first reports and refine KPIs
5. **Scale features** - Add custom skills, integrations, or branding

---

**Questions?** Check `README.md` for troubleshooting or file an issue.
