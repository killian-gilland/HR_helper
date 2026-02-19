"""
KPI Calculator Module - Multi-Tenant Ready
Computes recruitment metrics based on injected configuration.
"""

import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class CandidateMetrics:
    """Candidate metrics computed from raw data."""
    name: str
    email: str
    years_experience: float
    experience_score: float  # 0-100
    skill_match_count: int
    total_required_skills: int
    match_percentage: float
    availability_days: int
    available: bool
    overall_rank_score: float # 0-100
    rank_tier: str  # "EXCELLENT", "GOOD", "AVERAGE", "WEAK"

class KPICalculator:
    """Calculates recruitment KPIs using dynamic configuration."""
    
    # Fallback defaults ONLY used if client config is empty/broken
    DEFAULT_SKILLS = ["communication", "motivation"] 
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize calculator with dynamic configuration.
        
        Args:
            config: Dictionary containing 'required_skills', 'min_years_exp', etc.
                    This comes from the Google Sheet '_CONFIG' tab.
        """
        self.config = config or {}
        
        # Load skills from config or fallback
        # Key in sheet must be 'required_skills'
        self.required_skills = self.config.get("required_skills", self.DEFAULT_SKILLS)
        
        # Ensure list format if it came in as something else (safety check)
        if isinstance(self.required_skills, str):
            self.required_skills = [s.strip() for s in self.required_skills.split(",")]
            
        # Ensure skills are lowercase for matching
        self.required_skills = [str(s).lower() for s in self.required_skills]
        
        logger.info(f"🔧 KPICalculator initialized with {len(self.required_skills)} skills: {self.required_skills}")

    def calculate_all_metrics(self, df: pd.DataFrame) -> Tuple[List[CandidateMetrics], Dict]:
        """
        Calculate metrics for all candidates.
        """
        metrics_list = []
        
        for idx, row in df.iterrows():
            try:
                metrics = self._calculate_candidate_metrics(row)
                metrics_list.append(metrics)
            except Exception as e:
                logger.warning(f"Error calculating metrics for row {idx}: {e}")
        
        # Sort by overall rank score descending (Best first)
        metrics_list.sort(key=lambda x: x.overall_rank_score, reverse=True)
        
        # Calculate aggregate stats
        aggregate_stats = self._compute_aggregate_stats(metrics_list)
        
        return metrics_list, aggregate_stats
    
    def _calculate_candidate_metrics(self, row: pd.Series) -> CandidateMetrics:
        """Calculate metrics for a single candidate using dynamic config."""
        
        # 1. Name & Email (Attempt to find common column names)
        name = str(row.get("nom", row.get("name", "Unknown"))).strip()
        email = str(row.get("email", "")).strip()
        
        # 2. Experience Calculation
        years_exp = self._parse_years_experience(row.get("années_exp", row.get("years_exp", 0)))
        exp_score = self._calculate_experience_score(years_exp)
        
        # 3. Skills Matching (Dynamic)
        skills_raw = str(row.get("compétences", row.get("skills", ""))).lower()
        skill_match_count, match_pct = self._calculate_skill_match(skills_raw)
        
        # 4. Availability
        availability_date = row.get("disponibilité", row.get("availability", ""))
        availability_days, is_available = self._calculate_availability(availability_date)
        
        # 5. Overall Rank Score (Weighted Average)
        # Weights could also be in config later, currently hardcoded standard logic
        overall_rank = (exp_score * 0.35 + match_pct * 0.50 + availability_days / 30 * 0.15)
        
        rank_tier = self._get_rank_tier(overall_rank)
        
        return CandidateMetrics(
            name=name,
            email=email,
            years_experience=years_exp,
            experience_score=exp_score,
            skill_match_count=skill_match_count,
            total_required_skills=len(self.required_skills),
            match_percentage=match_pct,
            availability_days=availability_days,
            available=is_available,
            overall_rank_score=overall_rank,
            rank_tier=rank_tier
        )
    
    def _parse_years_experience(self, value) -> float:
        """Parse years of experience from various formats."""
        try:
            import re
            val_str = str(value).strip().lower()
            if not val_str or val_str in ["", "n/a", "unknown"]:
                return 0.0
            
            # Extract first number found
            match = re.search(r'(\d+)', val_str)
            if match:
                return float(match.group(1))
            return 0.0
        except:
            return 0.0
    
    def _calculate_experience_score(self, years: float) -> float:
        """Convert years of experience to 0-100 score."""
        # Simple thresholds. Could be dynamic in future versions.
        if years < 1:
            return 20.0
        elif years < 2:
            return 40.0 # Junior
        elif years < 5:
            return 65.0 # Mid
        elif years < 10:
            return 85.0 # Senior
        else:
            return 100.0 # Expert
    
    def _calculate_skill_match(self, skills_raw: str) -> Tuple[int, float]:
        """Calculate match against DYNAMIC required skills."""
        if not skills_raw or not self.required_skills:
            return 0, 0.0
        
        matched_count = 0
        
        # Check for each required skill in the candidate's skill text
        for required in self.required_skills:
            if required in skills_raw:
                matched_count += 1
        
        match_percentage = (matched_count / len(self.required_skills)) * 100
        return matched_count, match_percentage
    
    def _calculate_availability(self, availability_date) -> Tuple[int, bool]:
        """Calculate availability score."""
        txt = str(availability_date).lower()
        
        # Simple text matching for immediate availability
        if "immédiat" in txt or "immediate" in txt or "now" in txt or "maintenant" in txt:
            return 0, True
        
        # If it's a date, we could parse it, but for MVP/Robustness, 
        # if it's not immediate, we penalize slightly.
        # Returning 30 days default if not immediate logic
        return 30, False 

    def _get_rank_tier(self, score: float) -> str:
        """Convert overall score to tier."""
        if score >= 80:
            return "EXCELLENT"
        elif score >= 65:
            return "GOOD"
        elif score >= 45:
            return "AVERAGE"
        else:
            return "WEAK"
    
    def _compute_aggregate_stats(self, metrics_list: List[CandidateMetrics]) -> Dict:
        """Compute aggregate statistics."""
        if not metrics_list:
            return {}
        
        return {
            "total_candidates": len(metrics_list),
            "average_years_experience": sum(m.years_experience for m in metrics_list) / len(metrics_list),
            "average_match_percentage": sum(m.match_percentage for m in metrics_list) / len(metrics_list),
            "candidates_immediately_available": sum(1 for m in metrics_list if m.available),
            "tier_distribution": {
                "EXCELLENT": sum(1 for m in metrics_list if m.rank_tier == "EXCELLENT"),
                "GOOD": sum(1 for m in metrics_list if m.rank_tier == "GOOD"),
                "AVERAGE": sum(1 for m in metrics_list if m.rank_tier == "AVERAGE"),
                "WEAK": sum(1 for m in metrics_list if m.rank_tier == "WEAK")
            },
            "top_3_candidates": [asdict(m) for m in metrics_list[:3]]
        }