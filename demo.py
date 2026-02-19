#!/usr/bin/env python3
"""
Quick demo script - Run this to test locally without setup
Usage: python demo.py
"""

import pandas as pd
from datetime import datetime, timedelta
import json

# Simulate the pipeline with sample data
def run_demo():
    print("\n" + "="*60)
    print("🎯 G-SHEET ANALYST - HR RECRUITMENT DEMO")
    print("="*60 + "\n")
    
    # Step 1: Create sample candidate data
    print("[1/4] Loading sample candidate data...")
    candidates_data = {
        "nom": [
            "Alice Durand",
            "Bob Laurent", 
            "Claire Moreau",
            "David Chen",
            "Emma Wilson"
        ],
        "email": [
            "alice@example.com",
            "bob@example.com",
            "claire@example.com",
            "david@example.com",
            "emma@example.com"
        ],
        "années_exp": [5, 2, 8, 3, 6],
        "compétences": [
            "Python, SQL, Data Analysis, Project Management",
            "JavaScript, React, Node.js",
            "Python, SQL, Machine Learning, Leadership",
            "Java, Spring, Microservices",
            "Python, FastAPI, PostgreSQL, AWS"
        ],
        "disponibilité": [
            "Immédiat",
            "2024-02-15",
            "Immédiat",
            "2024-02-20",
            "Immédiat"
        ]
    }
    
    df = pd.DataFrame(candidates_data)
    print(f"✅ Loaded {len(df)} candidates\n")
    print(df.to_string(index=False))
    
    # Step 2: Calculate KPIs (simulate)
    print("\n[2/4] Calculating recruitment KPIs...")
    print("  - Experience scoring")
    print("  - Skill matching")
    print("  - Availability analysis")
    
    metrics_summary = {
        "total_candidates": 5,
        "candidates_immediately_available": 3,
        "average_match_percentage": 72.5,
        "average_years_experience": 4.8,
        "tier_distribution": {
            "EXCELLENT": 2,
            "GOOD": 2,
            "AVERAGE": 1,
            "WEAK": 0
        }
    }
    
    print("✅ KPI Summary:")
    for key, value in metrics_summary.items():
        if isinstance(value, dict):
            print(f"  {key}: {json.dumps(value)}")
        else:
            print(f"  {key}: {value}")
    
    # Step 3: Generate LLM insights (simulate)
    print("\n[3/4] Generating AI insights (Claude 3)...")
    
    insights = """🎯 TOP TALENTS:
- Alice Durand (100% match, 5 years, available now) → Schedule interview THIS WEEK
  Reason: Perfect fit on all required skills, senior-level experience, immediately available
  
- Claire Moreau (100% match, 8 years, available now) → Interview ASAP for lead role
  Reason: Expert-level experience, perfect skill match, can start immediately
  
- Emma Wilson (80% match, 6 years, available now) → Interview for backend position
  Reason: Strong AWS/backend skills, senior experience, available immediately

⚠️ CRITICAL INSIGHTS:
- Pool is 60% senior (5+ years) - very strong
- 3/5 candidates immediately available (60%)
- Average skill match: 72.5% (good for early-stage pipeline)
- Gap: Only 1 candidate with leadership experience

📊 POOL HEALTH: 78/100 - EXCELLENT
- Senior experience: ✅ Strong
- Technical depth: ✅ Strong  
- Availability: ✅ Good
- Diversity: ⚠️ Mostly backend/data roles

👉 NEXT ACTIONS (Priority Order):
1. Interview Alice & Claire this week (high ROI)
2. Make offer to best performer within 3 days
3. Add Emma to shortlist for follow-up
4. Continue sourcing: need more frontend/leadership profiles
"""
    
    print("✅ Insights generated:")
    print(insights)
    
    # Step 4: Email delivery simulation
    print("\n[4/4] Sending email report...")
    print("✅ Email prepared (HTML with metrics + insights)")
    print("   To: hr-manager@example.com")
    print("   Subject: 🎯 Weekly Recruitment Report - 5 Candidates")
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETE!")
    print("="*60)
    
    print("\n📚 NEXT STEPS:")
    print("1. Review this demo output above")
    print("2. Create a Google Sheet with your candidate data")
    print("   (Use columns: nom, email, années_exp, compétences, disponibilité)")
    print("3. Update .env with your configuration")
    print("4. Run: python src/main.py")
    print("\n📖 Read README.md for detailed setup instructions")
    print("🚀 Deploy to Google Cloud: See DEPLOYMENT.md")
    

if __name__ == "__main__":
    run_demo()
