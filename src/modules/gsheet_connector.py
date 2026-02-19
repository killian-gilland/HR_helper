"""
Local Excel Connector
Replaces GSheetConnector for local testing without Credit Card/Google Cloud.
"""

import pandas as pd
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GSheetConnector:
    """Fake GSheet Connector that actually reads a local Excel file."""
    
    def __init__(self, sa_key_json: str = None):
        # On s'en fiche de la clé JSON en local
        self.file_path = r"C:\Users\33698\Downloads\g-sheet-analyst-hr\data\candidats_100_random.xlsx"
        logger.info(f"📂 LOCAL MODE: Using file '{self.file_path}'")
    
    def fetch_run_config(self, sheet_url: str = "", config_sheet_name: str = "_CONFIG") -> Dict[str, Any]:
        """Reads configuration from the Excel tab."""
        try:
            if not os.path.exists(self.file_path):
                logger.error(f"❌ File not found: {self.file_path}")
                return {}

            # Read Excel without header first to process Key-Value manually
            df = pd.read_excel(self.file_path, sheet_name=config_sheet_name, header=None)
            
            config = {}
            # Iterate rows. Assume Col 0 is Key, Col 1 is Value
            for index, row in df.iterrows():
                key = str(row[0]).strip()
                val = str(row[1]).strip()
                
                if key in ["required_skills", "email_recipients"]:
                    config[key] = [x.strip() for x in val.split(",") if x.strip()]
                elif key in ["min_years_exp"]:
                    try:
                        config[key] = int(val)
                    except:
                        config[key] = 0
                else:
                    config[key] = val
            
            logger.info(f"✅ Loaded local config: {list(config.keys())}")
            return config

        except Exception as e:
            logger.error(f"❌ Error reading local config: {e}")
            return {}

    def fetch_candidates_data(self, sheet_url: str = "", worksheet_name: str = "Candidats") -> pd.DataFrame:
        """Reads candidate data from the Excel tab."""
        try:
            df = pd.read_excel(self.file_path, sheet_name=worksheet_name)
            # Remove empty rows
            df = df.dropna(how='all')
            logger.info(f"✅ Fetched {len(df)} candidates from local Excel.")
            return df
        except Exception as e:
            logger.error(f"❌ Error reading local data: {e}")
            return pd.DataFrame()

# Fonction inutile en local mais gardée pour éviter les erreurs d'import
def get_sa_key_from_secrets(p, s, v="latest"):
    return ""