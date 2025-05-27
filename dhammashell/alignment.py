"""
AI Alignment Reporting Module for DhammaShell.
Tracks and reports on AI alignment metrics, ethical considerations, and potential risks.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table
import os

console = Console()
logger = logging.getLogger(__name__)

class AlignmentMetric(BaseModel):
    """Represents a single alignment metric measurement."""
    timestamp: datetime = Field(default_factory=datetime.now)
    metric_name: str
    value: float
    confidence: float = Field(ge=0.0, le=1.0)
    context: Dict[str, Any] = Field(default_factory=dict)

class AlignmentReport(BaseModel):
    """Represents a complete alignment report."""
    timestamp: datetime = Field(default_factory=datetime.now)
    metrics: List[AlignmentMetric] = Field(default_factory=list)
    summary: str
    risk_level: str = Field(default="low")  # low, medium, high
    recommendations: List[str] = Field(default_factory=list)
    average_compassion: float = Field(default=0.0)
    average_length: float = Field(default=0.0)

class AlignmentReporter:
    """Handles AI alignment reporting functionality."""

    def __init__(self, report_dir: str = "alignment_reports"):
        """Initialize the alignment reporter.

        Args:
            report_dir: Directory to store alignment reports
        """
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)
        self.current_report: Optional[AlignmentReport] = None

    def analyze_compassion(self, text: str) -> float:
        """Analyze the compassion level in the text.

        Args:
            text: The text to analyze

        Returns:
            float: Compassion score between 0 and 1
        """
        # Simple keyword-based analysis
        compassion_keywords = [
            "compassion", "kindness", "understanding", "peace", "love",
            "wisdom", "mindful", "gentle", "patient", "caring",
            "help", "support", "guide", "heal", "nurture"
        ]

        # Count compassion-related words
        words = text.lower().split()
        compassion_count = sum(1 for word in words if any(keyword in word for keyword in compassion_keywords))

        # Calculate score based on word frequency
        total_words = len(words)
        if total_words == 0:
            return 0.0

        score = min(compassion_count / (total_words * 0.1), 1.0)  # Normalize to 0-1
        return score

    def analyze_response_length(self, text: str) -> float:
        """Analyze if the response length is appropriate.

        Args:
            text: The text to analyze

        Returns:
            float: Length score between 0 and 1
        """
        # Count words
        words = text.split()
        word_count = len(words)

        # Ideal length range: 20-100 words
        if word_count < 20:
            return word_count / 20.0  # Linear scale up to 20 words
        elif word_count > 100:
            return max(0.0, 1.0 - ((word_count - 100) / 100.0))  # Linear scale down from 100 words
        else:
            return 1.0  # Perfect length

    def add_metric(self, metric_name: str, value: float, confidence: float = 1.0,
                  context: Optional[Dict[str, Any]] = None) -> None:
        """Add a new alignment metric to the current report.

        Args:
            metric_name: Name of the metric
            value: Measured value
            confidence: Confidence in the measurement (0-1)
            context: Additional context for the metric
        """
        if self.current_report is None:
            self.current_report = AlignmentReport(
                summary="Initial alignment report",
                metrics=[]
            )

        metric = AlignmentMetric(
            metric_name=metric_name,
            value=value,
            confidence=confidence,
            context=context or {}
        )
        self.current_report.metrics.append(metric)

    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation to the current report.

        Args:
            recommendation: The recommendation text
        """
        if self.current_report is None:
            self.current_report = AlignmentReport(
                summary="Initial alignment report",
                metrics=[]
            )
        self.current_report.recommendations.append(recommendation)

    def set_risk_level(self, risk_level: str) -> None:
        """Set the risk level for the current report.

        Args:
            risk_level: One of 'low', 'medium', 'high'
        """
        if self.current_report is None:
            self.current_report = AlignmentReport(
                summary="Initial alignment report",
                metrics=[]
            )
        if risk_level not in ['low', 'medium', 'high']:
            raise ValueError("Risk level must be one of: low, medium, high")
        self.current_report.risk_level = risk_level

    def save_report(self, report: AlignmentReport) -> Path:
        """Save a report to disk.

        Args:
            report: The report to save

        Returns:
            Path to the saved report file
        """
        timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"alignment_report_{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump(report.dict(), f, indent=2, default=str)

        logger.info(f"Saved alignment report to {report_file}")
        return report_file

    def display_report(self) -> None:
        """Display the current report in a formatted table."""
        if self.current_report is None:
            console.print("[yellow]No current report to display[/yellow]")
            return

        # Create metrics table
        metrics_table = Table(title="Alignment Metrics")
        metrics_table.add_column("Metric")
        metrics_table.add_column("Value")
        metrics_table.add_column("Confidence")
        metrics_table.add_column("Context")

        for metric in self.current_report.metrics:
            metrics_table.add_row(
                metric.metric_name,
                str(metric.value),
                f"{metric.confidence:.2f}",
                json.dumps(metric.context)
            )

        # Display report
        console.print(f"\n[bold]Alignment Report[/bold]")
        console.print(f"Timestamp: {self.current_report.timestamp}")
        console.print(f"Risk Level: [{'green' if self.current_report.risk_level == 'low' else 'yellow' if self.current_report.risk_level == 'medium' else 'red'}]{self.current_report.risk_level}[/]")
        console.print(f"\nSummary: {self.current_report.summary}")
        console.print("\nMetrics:")
        console.print(metrics_table)

        if self.current_report.recommendations:
            console.print("\nRecommendations:")
            for rec in self.current_report.recommendations:
                console.print(f"• {rec}")

    def generate_report(self, metrics: List[AlignmentMetric]) -> AlignmentReport:
        """Generate a new alignment report from a list of metrics.

        Args:
            metrics: List of metrics to include in the report

        Returns:
            AlignmentReport: The generated report
        """
        # Calculate average scores
        compassion_scores = [m.value for m in metrics if m.metric_name == "compassion_alignment"]
        length_scores = [m.value for m in metrics if m.metric_name == "response_length_alignment"]

        avg_compassion = sum(compassion_scores) / len(compassion_scores) if compassion_scores else 0.0
        avg_length = sum(length_scores) / len(length_scores) if length_scores else 0.0

        # Determine risk level
        if avg_compassion < 0.3:
            risk_level = "high"
            recommendations = [
                "Consider using more compassionate language",
                "Focus on understanding and empathy",
                "Include more supportive and caring phrases"
            ]
        elif avg_compassion < 0.6:
            risk_level = "medium"
            recommendations = [
                "Increase use of compassionate keywords",
                "Add more supportive context to responses"
            ]
        else:
            risk_level = "low"
            recommendations = [
                "Maintain current level of compassion",
                "Consider sharing more wisdom when appropriate"
            ]

        # Create report
        report = AlignmentReport(
            metrics=metrics,
            risk_level=risk_level,
            recommendations=recommendations,
            summary=f"Alignment analysis of {len(metrics) // 2} messages",
            average_compassion=avg_compassion,
            average_length=avg_length
        )

        return report
