"""
Email Delivery Module - Smart Dev Mode
Sends email via SMTP if configured, OR saves as HTML file locally if credentials are missing.
"""

import smtplib
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailDelivery:
    """Handles email sending OR local file saving for recruitment insights."""
    
    def __init__(self, sender_email: str, sender_password: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        
        # Mode détection : Si pas de mot de passe, on passe en mode "Fichier Local"
        self.local_mode = not (self.sender_email and self.sender_password)
        if self.local_mode:
            logger.warning("⚠️ No email credentials found. Switching to LOCAL FILE MODE (report.html).")

    def send_insights_email(
        self,
        recipient_emails: List[str],
        subject: str,
        insights_text: str,
        metrics_summary: dict,
        top_candidates: list,
        attachment_path: Optional[str] = None
    ) -> bool:
        """
        Send recruitment insights via email OR save to disk.
        """
        try:
            # 1. Build Content (HTML)
            html_body = self._build_html_content(insights_text, metrics_summary, top_candidates)
            
            # CASE A: LOCAL MODE (Save to file)
            if self.local_mode:
                return self._save_to_disk(html_body, subject)

            # CASE B: EMAIL MODE (Send via SMTP)
            msg = MIMEMultipart("alternative")
            msg["From"] = self.sender_email
            msg["To"] = ", ".join(recipient_emails)
            msg["Subject"] = subject
            
            msg.attach(MIMEText(insights_text, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            if attachment_path:
                self._attach_file(msg, attachment_path)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_emails, msg.as_string())
            
            logger.info(f"✅ Email sent to {', '.join(recipient_emails)}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error sending email: {e}")
            logger.info("👉 Attempting to save as local file instead...")
            return self._save_to_disk(html_body, subject)
    
    def _save_to_disk(self, html_content: str, subject: str) -> bool:
        """Fallback: Save the email as an HTML file."""
        try:
            filename = "LAST_REPORT.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"\n")
                f.write(html_content)
            
            logger.info("="*60)
            logger.info(f"💾 REPORT SAVED LOCALLY: {os.path.abspath(filename)}")
            logger.info("📂 Open this file in your browser to see the result!")
            logger.info("="*60)
            return True
        except Exception as e:
            logger.error(f"Failed to save local file: {e}")
            return False

    def _build_html_content(self, insights_text: str, metrics_summary: dict, top_candidates: list) -> str:
        """Build HTML email content."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Convert Markdown-style bolding (**text**) to HTML bold (<b>text</b>) for better display
        formatted_insights = insights_text.replace("\n", "<br>")
        formatted_insights = formatted_insights.replace("**", "") # Simple cleanup for now
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; padding: 20px; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ border-bottom: 2px solid #2c3e50; padding-bottom: 20px; margin-bottom: 20px; }}
                    .header h1 {{ margin: 0; color: #2c3e50; font-size: 24px; }}
                    .timestamp {{ color: #7f8c8d; font-size: 14px; margin-top: 5px; }}
                    
                    .section-title {{ background-color: #3498db; color: white; padding: 10px 15px; border-radius: 4px; margin-top: 30px; font-weight: bold; }}
                    
                    .insights-box {{ background-color: #f8f9fa; border-left: 5px solid #3498db; padding: 20px; margin: 20px 0; white-space: pre-line; }}
                    
                    .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
                    .metric-card {{ background: #fff; border: 1px solid #e0e0e0; padding: 15px; text-align: center; border-radius: 6px; }}
                    .metric-val {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                    .metric-lbl {{ font-size: 12px; color: #7f8c8d; text-transform: uppercase; margin-top: 5px; }}
                    
                    .candidate-card {{ border: 1px solid #eee; padding: 15px; margin-bottom: 10px; border-radius: 6px; transition: transform 0.2s; }}
                    .candidate-card:hover {{ background-color: #fafafa; border-color: #ccc; }}
                    .cand-name {{ font-size: 18px; font-weight: bold; color: #2980b9; }}
                    .cand-meta {{ font-size: 14px; color: #555; margin-top: 5px; }}
                    
                    .badge {{ display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 11px; color: white; vertical-align: middle; margin-left: 10px; }}
                    .badge-EXCELLENT {{ background-color: #27ae60; }}
                    .badge-GOOD {{ background-color: #2980b9; }}
                    .badge-AVERAGE {{ background-color: #f39c12; }}
                    .badge-WEAK {{ background-color: #c0392b; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎯 Recruitment Intelligence Report</h1>
                        <div class="timestamp">Generated via G-Sheet Analyst • {timestamp}</div>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-val">{metrics_summary.get('total_candidates', 0)}</div>
                            <div class="metric-lbl">Total Profiles</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-val">{metrics_summary.get('candidates_immediately_available', 0)}</div>
                            <div class="metric-lbl">Available Now</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-val">{metrics_summary.get('average_match_percentage', 0):.0f}%</div>
                            <div class="metric-lbl">Avg Match</div>
                        </div>
                    </div>

                    <div class="section-title">🧠 AI Executive Summary</div>
                    <div class="insights-box">{formatted_insights}</div>
                    
                    <div class="section-title">⭐ Top Recommended Candidates</div>
                    {self._build_candidates_html(top_candidates)}
                    
                    <div style="text-align: center; margin-top: 40px; color: #aaa; font-size: 12px;">
                        Automated Report • Powered by Gemini/Claude
                    </div>
                </div>
            </body>
        </html>
        """
        return html
    
    def _build_candidates_html(self, candidates: list) -> str:
        html = ""
        for cand in candidates[:5]:
            tier = cand.get('rank_tier', 'WEAK')
            html += f"""
            <div class="candidate-card">
                <div class="cand-name">
                    {cand.get('name', 'Unknown')}
                    <span class="badge badge-{tier}">{tier}</span>
                </div>
                <div class="cand-meta">
                    📧 {cand.get('email', 'N/A')} | 
                    💼 {cand.get('years_experience', 0):.0f} years exp | 
                    ✅ Match: {cand.get('match_percentage', 0):.0f}%
                </div>
                <div class="cand-meta" style="color: #e67e22; margin-top: 4px;">
                    ⏰ Availability: {cand.get('availability_days', 0)} days
                </div>
            </div>
            """
        return html
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            filename = file_path.split("/")[-1]
            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
            msg.attach(part)
        except Exception:
            pass