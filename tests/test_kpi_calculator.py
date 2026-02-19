"""
Test suite for recruitment analyzer
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
from src.modules import KPICalculator, CandidateMetrics


class TestKPICalculator(unittest.TestCase):
    """Test KPI calculations."""
    
    def setUp(self):
        self.calculator = KPICalculator(
            required_skills=["python", "sql", "project management"]
        )
    
    def test_parse_years_experience(self):
        """Test parsing years of experience."""
        assert self.calculator._parse_years_experience("5") == 5.0
        assert self.calculator._parse_years_experience("5 ans") == 5.0
        assert self.calculator._parse_years_experience("5-7 years") == 5.0
        assert self.calculator._parse_years_experience("") == 0.0
    
    def test_experience_score(self):
        """Test experience scoring."""
        assert self.calculator._calculate_experience_score(0.5) == 20.0
        assert self.calculator._calculate_experience_score(1.5) == 40.0
        assert self.calculator._calculate_experience_score(3) == 65.0
        assert self.calculator._calculate_experience_score(7) == 85.0
        assert self.calculator._calculate_experience_score(15) == 100.0
    
    def test_skill_matching(self):
        """Test skill matching logic."""
        matched, pct = self.calculator._calculate_skill_match("Python, SQL")
        assert matched == 2
        assert pct == 66.66666666666666
        
        matched, pct = self.calculator._calculate_skill_match("JavaScript, React")
        assert matched == 0
        assert pct == 0.0
    
    def test_rank_tier(self):
        """Test rank tier assignment."""
        assert self.calculator._get_rank_tier(90) == "EXCELLENT"
        assert self.calculator._get_rank_tier(70) == "GOOD"
        assert self.calculator._get_rank_tier(50) == "AVERAGE"
        assert self.calculator._get_rank_tier(30) == "WEAK"
    
    def test_full_calculation(self):
        """Test full candidate metrics calculation."""
        df = pd.DataFrame({
            "nom": ["Alice Durand"],
            "email": ["alice@example.com"],
            "années_exp": ["5"],
            "compétences": ["Python, SQL, Project Management"],
            "disponibilité": ["Immédiat"]
        })
        
        metrics_list, stats = self.calculator.calculate_all_metrics(df)
        
        assert len(metrics_list) == 1
        assert metrics_list[0].name == "Alice Durand"
        assert metrics_list[0].rank_tier == "EXCELLENT"
        assert metrics_list[0].match_percentage == 100.0


class TestDataFrameHandling(unittest.TestCase):
    """Test DataFrame handling and edge cases."""
    
    def test_empty_dataframe(self):
        """Test handling of empty data."""
        calculator = KPICalculator()
        df = pd.DataFrame()
        
        metrics_list, stats = calculator.calculate_all_metrics(df)
        
        assert len(metrics_list) == 0
        assert stats == {}
    
    def test_missing_columns(self):
        """Test handling of missing columns."""
        calculator = KPICalculator()
        df = pd.DataFrame({
            "nom": ["Test User"],
            # Missing other columns
        })
        
        # Should not crash
        metrics_list, stats = calculator.calculate_all_metrics(df)
        assert len(metrics_list) == 1


if __name__ == "__main__":
    unittest.main()
