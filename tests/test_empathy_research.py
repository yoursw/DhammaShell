"""
Test suite for DhammaShell's Empathy Research Module
Designed for neuroscience research validation
"""

import pytest
from datetime import datetime
from dhammashell.empathy_research import (
    EmpathyAnalyzer,
    ResearchDataCollector,
    EmpathyMetrics,
    EmpathyMetric
)

# Test data representing different emotional states and responses
NEUTRAL_INPUT = "What is the weather like today?"
POSITIVE_INPUT = "I'm feeling really happy and grateful for this opportunity."
NEGATIVE_INPUT = "I'm feeling overwhelmed and anxious about my research."
MINDFUL_RESPONSE = "I understand your feelings. Let's take a moment to breathe and reflect on this together."
COMPASSIONATE_RESPONSE = "I hear your pain, and I want you to know that you're not alone in this journey."
NEUTRAL_RESPONSE = "The weather is currently sunny with a temperature of 25°C."

class TestEmpathyAnalyzer:
    """Tests for emotional recognition and empathy analysis"""
    
    @pytest.fixture
    def analyzer(self):
        return EmpathyAnalyzer()
    
    def test_emotional_recognition_positive(self, analyzer):
        """Test recognition of positive emotional content"""
        analysis = analyzer.analyze_interaction(POSITIVE_INPUT, NEUTRAL_RESPONSE)
        assert "emotional_recognition" in analysis["metrics"]
        # Positive emotions should be recognized
        assert analysis["metrics"]["emotional_recognition"] > 0.5
    
    def test_emotional_recognition_negative(self, analyzer):
        """Test recognition of negative emotional content"""
        analysis = analyzer.analyze_interaction(NEGATIVE_INPUT, NEUTRAL_RESPONSE)
        assert "emotional_recognition" in analysis["metrics"]
        # Negative emotions should be recognized
        assert analysis["metrics"]["emotional_recognition"] > 0.5
    
    def test_emotional_recognition_neutral(self, analyzer):
        """Test recognition of neutral emotional content"""
        analysis = analyzer.analyze_interaction(NEUTRAL_INPUT, NEUTRAL_RESPONSE)
        assert "emotional_recognition" in analysis["metrics"]
        # Neutral content should have lower emotional recognition
        assert analysis["metrics"]["emotional_recognition"] < 0.3
    
    def test_compassion_scoring(self, analyzer):
        """Test compassion scoring in responses"""
        analysis = analyzer.analyze_interaction(NEGATIVE_INPUT, COMPASSIONATE_RESPONSE)
        assert "compassion_score" in analysis["metrics"]
        # Compassionate responses should score higher
        assert analysis["metrics"]["compassion_score"] > 0.7
    
    def test_mindfulness_assessment(self, analyzer):
        """Test mindfulness level assessment"""
        analysis = analyzer.analyze_interaction(NEGATIVE_INPUT, MINDFUL_RESPONSE)
        assert "mindfulness_level" in analysis["metrics"]
        # Mindful responses should score higher
        assert analysis["metrics"]["mindfulness_level"] > 0.7

class TestResearchDataCollector:
    """Tests for research data collection and management"""
    
    @pytest.fixture
    def collector(self, tmp_path):
        return ResearchDataCollector(data_dir=str(tmp_path))
    
    def test_session_creation(self, collector):
        """Test creation of new research sessions"""
        session_id = collector.start_session()
        assert session_id is not None
        assert collector.current_session is not None
        assert collector.current_session["session_id"] == session_id
    
    def test_interaction_recording(self, collector):
        """Test recording of research interactions"""
        collector.start_session()
        analysis = {
            "metrics": {
                "emotional_recognition": 0.8,
                "compassion_score": 0.9,
                "mindfulness_level": 0.7
            }
        }
        collector.record_interaction(POSITIVE_INPUT, MINDFUL_RESPONSE, analysis)
        assert len(collector.current_session["interactions"]) == 1
    
    def test_session_persistence(self, collector):
        """Test saving and loading of research sessions"""
        collector.start_session()
        analysis = {
            "metrics": {
                "emotional_recognition": 0.8,
                "compassion_score": 0.9,
                "mindfulness_level": 0.7
            }
        }
        collector.record_interaction(POSITIVE_INPUT, MINDFUL_RESPONSE, analysis)
        filepath = collector.save_session()
        
        # Load the session and verify data integrity
        loaded_session = collector.load_session(collector.current_session["session_id"])
        assert loaded_session["session_id"] == collector.current_session["session_id"]
        assert len(loaded_session["interactions"]) == 1

class TestEmpathyMetrics:
    """Tests for empathy metrics calculation and analysis"""
    
    @pytest.fixture
    def metrics(self):
        return EmpathyMetrics()
    
    def test_metric_recording(self, metrics):
        """Test recording of empathy metrics"""
        metrics.add_metric("compassion", 0.8, {"context": "positive_interaction"})
        metrics.add_metric("compassion", 0.9, {"context": "negative_interaction"})
        history = metrics.get_metric_history("compassion")
        assert len(history) == 2
    
    def test_statistical_analysis(self, metrics):
        """Test statistical analysis of empathy metrics"""
        # Add test data
        test_values = [0.8, 0.9, 0.7, 0.85]
        for value in test_values:
            metrics.add_metric("compassion", value)
        
        stats = metrics.calculate_statistics("compassion")
        assert stats["count"] == 4
        assert 0.7 <= stats["mean"] <= 0.9
        assert stats["min"] == 0.7
        assert stats["max"] == 0.9
    
    def test_metric_export(self, metrics):
        """Test export of metrics for research analysis"""
        # Add test data for multiple metrics
        metrics.add_metric("compassion", 0.8)
        metrics.add_metric("mindfulness", 0.9)
        metrics.add_metric("emotional_recognition", 0.7)
        
        exported = metrics.export_metrics()
        assert "compassion" in exported
        assert "mindfulness" in exported
        assert "emotional_recognition" in exported

def test_integration_scenario():
    """Integration test simulating a complete research session"""
    analyzer = EmpathyAnalyzer()
    collector = ResearchDataCollector()
    metrics = EmpathyMetrics()
    
    # Start a research session
    session_id = collector.start_session()
    
    # Simulate a series of interactions
    interactions = [
        (POSITIVE_INPUT, MINDFUL_RESPONSE),
        (NEGATIVE_INPUT, COMPASSIONATE_RESPONSE),
        (NEUTRAL_INPUT, NEUTRAL_RESPONSE)
    ]
    
    for user_input, response in interactions:
        # Analyze interaction
        analysis = analyzer.analyze_interaction(user_input, response)
        
        # Record interaction
        collector.record_interaction(user_input, response, analysis)
        
        # Record metrics
        for metric_name, value in analysis["metrics"].items():
            metrics.add_metric(metric_name, value)
    
    # Save session
    filepath = collector.save_session()
    
    # Verify data integrity
    loaded_session = collector.load_session(session_id)
    assert len(loaded_session["interactions"]) == len(interactions)
    
    # Verify metrics
    exported_metrics = metrics.export_metrics()
    assert len(exported_metrics) == 3  # emotional_recognition, compassion_score, mindfulness_level 