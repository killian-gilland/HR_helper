"""
Google Cloud Function handler
Deploy this as Cloud Function with HTTP trigger.
Can be called by Cloud Scheduler or manual requests.
"""

import functions_framework
import json
import logging
import os
from typing import Tuple
from flask import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@functions_framework.http
def recruitment_analyzer(request: Request) -> Tuple[str, int]:
    """
    HTTP Cloud Function for recruitment analysis.
    
    Expected query parameters:
    - action: "analyze" (default), "list_sheets", or "health_check"
    - config_bucket: GCS bucket with config.json
    - config_file: Name of config file (default: config.json)
    
    Returns:
        JSON response with insights and metrics
    """
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    action = request_args.get("action", "analyze")
    
    try:
        if action == "health_check":
            return json.dumps({"status": "healthy", "service": "recruitment-analyzer"}), 200
        
        elif action == "analyze":
            return handle_analyze_request(request_json, request_args)
        
        elif action == "list_sheets":
            return handle_list_sheets_request(request_args)
        
        else:
            return json.dumps({"error": f"Unknown action: {action}"}), 400
    
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return json.dumps({"error": str(e)}), 500


def handle_analyze_request(request_json: dict, request_args) -> Tuple[str, int]:
    """Handle analysis request."""
    from modules import (
        GSheetConnector,
        KPICalculator,
        create_analyzer,
        EmailDelivery,
        get_sa_key_from_secrets
    )
    from dataclasses import asdict
    
    # Get configuration
    config_bucket = request_args.get("config_bucket", "gs-analyst-config")
    config_file = request_args.get("config_file", "config.json")
    
    # Load config from GCS
    config = _load_config_from_gcs(config_bucket, config_file)
    
    if not config:
        return json.dumps({"error": "Config not found in GCS"}), 404
    
    logger.info("Starting recruitment analysis...")
    
    # Get service account key from Secret Manager
    project_id = os.getenv("GCP_PROJECT_ID")
    sa_key = get_sa_key_from_secrets(
        project_id,
        "google_sheets_service_account_key",
        "latest"
    )
    
    # Initialize components
    gs_connector = GSheetConnector(sa_key)
    kpi_calculator = KPICalculator(required_skills=config.get("required_skills"))
    llm_analyzer = create_analyzer(config.get("llm_provider", "anthropic"))
    
    # Fetch data
    df = gs_connector.fetch_candidates_data(
        config.get("gsheet_url"),
        config.get("worksheet_name", "Candidats")
    )
    
    if df.empty:
        return json.dumps({"error": "No candidate data found"}), 400
    
    # Calculate KPIs
    metrics_list, aggregate_stats = kpi_calculator.calculate_all_metrics(df)
    
    # Generate insights
    metrics_dicts = [asdict(m) for m in metrics_list]
    insights = llm_analyzer.generate_insights(aggregate_stats, metrics_dicts)
    
    # Send email if configured
    email_cfg = config.get("email_config")
    if email_cfg and email_cfg.get("recipients"):
        sender_email = os.getenv("EMAIL_SENDER", email_cfg.get("sender_email", ""))
        sender_password = os.getenv("EMAIL_PASSWORD", email_cfg.get("sender_password", ""))
        
        if sender_email and sender_password:
            email_delivery = EmailDelivery(sender_email, sender_password)
            email_delivery.send_insights_email(
                recipient_emails=email_cfg.get("recipients", []),
                subject=f"🎯 Weekly Recruitment Report - {len(metrics_list)} Candidates",
                insights_text=insights["analysis"],
                metrics_summary=insights["metrics_summary"],
                top_candidates=insights["top_candidates"]
            )
            logger.info("Email sent successfully")
    
    return json.dumps({
        "status": "success",
        "metrics": aggregate_stats,
        "insights": insights["analysis"],
        "top_candidates": [asdict(m) for m in metrics_list[:3]],
        "timestamp": insights["generated_at"]
    }, default=str), 200


def handle_list_sheets_request(request_args) -> Tuple[str, int]:
    """List available worksheets in a Google Sheet."""
    from modules import GSheetConnector, get_sa_key_from_secrets
    
    gsheet_url = request_args.get("gsheet_url")
    if not gsheet_url:
        return json.dumps({"error": "gsheet_url parameter required"}), 400
    
    try:
        project_id = os.getenv("GCP_PROJECT_ID")
        sa_key = get_sa_key_from_secrets(
            project_id,
            "google_sheets_service_account_key",
            "latest"
        )
        
        gs_connector = GSheetConnector(sa_key)
        metadata = gs_connector.get_sheet_metadata(gsheet_url)
        
        return json.dumps(metadata), 200
    except Exception as e:
        return json.dumps({"error": str(e)}), 500


def _load_config_from_gcs(bucket_name: str, file_name: str) -> dict:
    """Load configuration from Google Cloud Storage."""
    try:
        from google.cloud import storage
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        
        if not blob.exists():
            logger.warning(f"Config file not found: {bucket_name}/{file_name}")
            return None
        
        config_data = blob.download_as_string()
        return json.loads(config_data)
    
    except Exception as e:
        logger.error(f"Error loading config from GCS: {e}")
        return None
