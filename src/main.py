"""
Main orchestration script - Scalable / Config-Driven Version
Reads configuration from GSheet -> Configures Pipeline -> Runs Analysis
"""

import os
import sys
import json
import logging
from typing import Optional
from dataclasses import asdict
import pandas as pd
from dotenv import load_dotenv

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules import (
    GSheetConnector,
    KPICalculator,
    create_analyzer,
    EmailDelivery,
    get_sa_key_from_secrets
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RecruitmentAnalysisPipeline:
    """End-to-end recruitment analysis pipeline (Scalable)."""
    
    def __init__(self, initial_config: dict):
        self.base_config = initial_config
        self.run_config = {} 
        
        # Components
        self.gs_connector = None
        self.kpi_calculator = None
        self.llm_analyzer = None
        self.email_delivery = None
    
    def run(self) -> dict:
        """Execute the full pipeline."""
        logger.info("=" * 50)
        logger.info("🚀 Starting Recruitment Analysis Pipeline (Gemini Edition)")
        logger.info("=" * 50)
        
        try:
            # Step 1: Initialize Connector
            logger.info("\n[1/5] Connecting to Data Source...")
            self._init_connector()
            
            # Step 2: LOAD CLIENT CONFIGURATION
            logger.info("\n[2/5] Fetching client configuration from '_CONFIG' tab...")
            self.run_config = self.gs_connector.fetch_run_config(
                self.base_config["gsheet_url"]
            )
            
            # Merge configs
            if "email_recipients" in self.run_config:
                logger.info(f"📧 Overriding recipients: {self.run_config['email_recipients']}")
                if "email_config" not in self.base_config:
                    self.base_config["email_config"] = {}
                self.base_config["email_config"]["recipients"] = self.run_config["email_recipients"]

            target_worksheet = self.run_config.get("worksheet_target", "Candidats")
            
            # Step 3: Initialize Components
            logger.info(f"\n[3/5] Initializing logic...")
            logger.info(f"    👉 Target: {target_worksheet}")
            logger.info(f"    👉 Skills: {self.run_config.get('required_skills', 'DEFAULT')}")
            
            self.kpi_calculator = KPICalculator(config=self.run_config)
            
            # --- CORRECTION CRITIQUE ICI : On force le provider Gemini ---
            llm_provider = self.base_config.get("llm_provider", "gemini")
            logger.info(f"    🧠 AI Brain: {llm_provider.upper()}")
            self.llm_analyzer = create_analyzer(llm_provider)
            
            email_cfg = self.base_config.get("email_config", {})
            if email_cfg.get("sender_email"):
                self.email_delivery = EmailDelivery(
                    sender_email=email_cfg.get("sender_email"),
                    sender_password=email_cfg.get("sender_password")
                )
            
            # Step 4: Fetch Data
            logger.info(f"\n[4/5] Processing data...")
            df = self.gs_connector.fetch_candidates_data(
                self.base_config["gsheet_url"], 
                target_worksheet
            )
            
            if df.empty:
                logger.error("No candidate data found.")
                return {"status": "error", "message": "No data found"}
            
            metrics_list, aggregate_stats = self.kpi_calculator.calculate_all_metrics(df)
            logger.info(f"✅ Calculated metrics for {len(metrics_list)} candidates")
            
            # Step 5: Generate Insights
            logger.info("\n[5/5] Asking Gemini for insights...")
            
            aggregate_stats["context_required_skills"] = self.run_config.get("required_skills")
            insights = self._generate_insights(metrics_list, aggregate_stats)
            
            if self._should_send_email():
                self._send_email(insights, metrics_list)
            else:
                logger.info("Email delivery skipped (Saved to file mode likely active)")
            
            logger.info("\n" + "=" * 50)
            logger.info("✅ SUCCESS! Check your folder for LAST_REPORT.html")
            logger.info("=" * 50)
            
            return {"status": "success"}
        
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def _init_connector(self):
        # Local Excel Mode
        self.gs_connector = GSheetConnector(sa_key_json=None)

    def _generate_insights(self, metrics_list, aggregate_stats) -> dict:
        metrics_dicts = [asdict(m) for m in metrics_list]
        return self.llm_analyzer.generate_insights(aggregate_stats, metrics_dicts)
    
    def _should_send_email(self) -> bool:
        # Toujours True pour déclencher le mode Fichier Local si pas de mail
        return self.email_delivery is not None
    
    def _send_email(self, insights: dict, metrics_list):
        email_cfg = self.base_config.get("email_config", {})
        recipients = email_cfg.get("recipients", [])
        subject = f"🎯 Recruitment Report - Top {len(metrics_list)} Candidates"
        
        self.email_delivery.send_insights_email(
            recipient_emails=recipients,
            subject=subject,
            insights_text=insights["analysis"],
            metrics_summary=insights["metrics_summary"],
            top_candidates=insights["top_candidates"]
        )

def load_config_from_file(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    # --- CORRECTION MAJEURE : CHARGEMENT ROBUSTE DU .ENV ---
    # On force le script à chercher le .env un dossier plus haut (à la racine)
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(env_path)
    
    # Vérification immédiate
    if not os.getenv("GEMINI_API_KEY"):
        logger.warning("⚠️ ATTENTION: GEMINI_API_KEY non trouvée. Vérifiez le chemin du fichier .env")

    # Base Config Force Gemini
    base_config = {
        "gsheet_url": os.getenv("GSHEET_URL", ""),
        "llm_provider": "gemini",  # <--- FORCÉ SUR GEMINI
        "email_config": {
            "sender_email": os.getenv("EMAIL_SENDER", ""),
            "sender_password": os.getenv("EMAIL_PASSWORD", ""),
            "recipients": [] 
        }
    }
    
    pipeline = RecruitmentAnalysisPipeline(base_config)
    result = pipeline.run()