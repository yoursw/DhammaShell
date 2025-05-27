"""
Research Report Generation Module for DhammaShell
Generates detailed research reports with analysis and visualizations
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ResearchReport:
    """Generates research reports from session data"""

    METRIC_DESCRIPTIONS = {
        "emotional_recognition": {
            "name": "Emotional Recognition",
            "description": "Measures the system's ability to detect and recognize emotional content in user input.",
            "scale": "0.0 to 1.0",
            "interpretation": {
                "high": "> 0.7: Strong emotional content detected",
                "medium": "0.4 - 0.7: Moderate emotional content",
                "low": "< 0.4: Limited emotional content",
            },
            "methodology": "Combines sentiment analysis with keyword and phrase detection for emotional expressions.",
        },
        "compassion_score": {
            "name": "Compassion Score",
            "description": "Evaluates the system's response quality in terms of compassionate engagement.",
            "scale": "0.0 to 1.0",
            "interpretation": {
                "high": "> 0.7: Highly compassionate response",
                "medium": "0.4 - 0.7: Moderately compassionate",
                "low": "< 0.4: Limited compassion demonstrated",
            },
            "methodology": "Analyzes response content for compassionate language, acknowledgment of feelings, and supportive phrases.",
        },
        "mindfulness_level": {
            "name": "Mindfulness Level",
            "description": "Assesses the presence of mindful communication elements in system responses.",
            "scale": "0.0 to 1.0",
            "interpretation": {
                "high": "> 0.7: Strong mindful communication",
                "medium": "0.4 - 0.7: Moderate mindfulness",
                "low": "< 0.4: Limited mindful elements",
            },
            "methodology": "Evaluates presence of mindful language, present-moment awareness, and balanced response patterns.",
        },
    }

    def __init__(self, output_dir: str = "research_reports"):
        """
        Initialize the research report generator

        Args:
            output_dir: Directory to store generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_report(
        self,
        session_data: Dict,
        output_format: str = "text",
        include_visualizations: bool = True,
    ) -> str:
        """
        Generate a research report from session data

        Args:
            session_data: Session data from ResearchDataCollector
            output_format: Output format ('text' or 'json')
            include_visualizations: Whether to generate visualizations

        Returns:
            Generated report in the specified format
        """
        # Extract metrics from session data
        metrics = []
        for interaction in session_data.get("interactions", []):
            if "analysis" in interaction and "metrics" in interaction["analysis"]:
                for metric_name, value in interaction["analysis"]["metrics"].items():
                    metrics.append(
                        {
                            "name": metric_name,
                            "value": float(value),
                            "timestamp": interaction.get(
                                "timestamp", datetime.now().isoformat()
                            ),
                        }
                    )

        # Generate report sections
        report = {
            "session_info": {
                "session_id": session_data.get("session_id", "unknown"),
                "start_time": session_data.get(
                    "start_time", datetime.now().isoformat()
                ),
                "total_interactions": len(session_data.get("interactions", [])),
            },
            "metrics_summary": self._summarize_metrics(metrics),
            "interaction_analysis": self._analyze_interactions(
                session_data.get("interactions", [])
            ),
            "metric_descriptions": self.METRIC_DESCRIPTIONS,
        }

        if output_format == "json":
            return json.dumps(report, indent=2)
        else:
            return self._format_text_report(report)

    def _summarize_metrics(self, metrics: List[Dict]) -> Dict:
        """Generate summary statistics for metrics"""
        if not metrics:
            return {}

        summary = {}
        for metric in metrics:
            name = metric["name"]
            value = metric["value"]

            if name not in summary:
                summary[name] = {
                    "count": 0,
                    "sum": 0,
                    "min": float("inf"),
                    "max": float("-inf"),
                }

            summary[name]["count"] += 1
            summary[name]["sum"] += value
            summary[name]["min"] = min(summary[name]["min"], value)
            summary[name]["max"] = max(summary[name]["max"], value)

        # Calculate averages
        for name in summary:
            summary[name]["mean"] = summary[name]["sum"] / summary[name]["count"]
            del summary[name]["sum"]  # Remove intermediate sum

        return summary

    def _analyze_interactions(self, interactions: List[Dict]) -> Dict:
        """Analyze interaction patterns"""
        if not interactions:
            return {}

        return {
            "total_interactions": len(interactions),
            "first_interaction": interactions[0].get("timestamp", "unknown"),
            "last_interaction": interactions[-1].get("timestamp", "unknown"),
        }

    def _format_text_report(self, report: Dict) -> str:
        """Format report as text"""
        sections = []

        # Header
        sections.append("DhammaShell Empathy Research Report")
        sections.append("=" * 50)
        sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append("")

        # Session Info
        sections.append("Session Information")
        sections.append("-" * 20)
        for key, value in report["session_info"].items():
            sections.append(f"{key}: {value}")

        # Metrics Description
        sections.append("\nMetrics Description")
        sections.append("-" * 20)
        sections.append(
            "This report analyzes three key metrics of empathetic interaction:"
        )
        sections.append("")

        for metric_id, metric_info in report["metric_descriptions"].items():
            sections.append(f"{metric_info['name']}:")
            sections.append(f"  Description: {metric_info['description']}")
            sections.append(f"  Scale: {metric_info['scale']}")
            sections.append("  Interpretation:")
            for level, desc in metric_info["interpretation"].items():
                sections.append(f"    • {level.title()}: {desc}")
            sections.append(f"  Methodology: {metric_info['methodology']}")
            sections.append("")

        # Metrics Summary
        sections.append("Metrics Summary")
        sections.append("-" * 20)
        for metric, stats in report["metrics_summary"].items():
            metric_info = report["metric_descriptions"].get(metric, {})
            sections.append(
                f"\n{metric_info.get('name', metric.replace('_', ' ').title())}:"
            )
            for stat, value in stats.items():
                sections.append(f"  {stat}: {value:.2f}")

            # Add interpretation based on mean value
            mean_value = stats["mean"]
            if mean_value > 0.7:
                level = "high"
            elif mean_value > 0.4:
                level = "medium"
            else:
                level = "low"
            sections.append(
                f"  Overall Assessment: {metric_info['interpretation'][level]}"
            )

        # Interaction Analysis
        sections.append("\nInteraction Analysis")
        sections.append("-" * 20)
        for key, value in report["interaction_analysis"].items():
            sections.append(f"{key}: {value}")

        return "\n".join(sections)

    def _extract_metrics(self, session_data: Dict) -> Dict[str, List[float]]:
        """Extract metrics from session data"""
        metrics = {
            "emotional_recognition": [],
            "compassion_score": [],
            "mindfulness_level": [],
        }

        for interaction in session_data["interactions"]:
            for metric_name, value in interaction["metrics"].items():
                metrics[metric_name].append(value)

        return metrics

    def _calculate_statistics(self, metrics: Dict[str, List[float]]) -> Dict:
        """Calculate statistical measures for each metric"""
        stats = {}

        for metric_name, values in metrics.items():
            if not values:
                continue

            stats[metric_name] = {
                "count": len(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "min": min(values),
                "max": max(values),
                "quartiles": (
                    statistics.quantiles(values, n=4) if len(values) >= 4 else None
                ),
            }

        return stats

    def _generate_visualizations(self, metrics: Dict[str, List[float]]):
        """Generate data visualizations"""
        # Set style
        plt.style.use("seaborn")
        sns.set_palette("husl")

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Empathy Research Metrics Analysis", fontsize=16)

        # Distribution plots
        for i, (metric_name, values) in enumerate(metrics.items()):
            row = i // 2
            col = i % 2
            sns.histplot(data=values, ax=axes[row, col], kde=True)
            axes[row, col].set_title(
                f'{metric_name.replace("_", " ").title()} Distribution'
            )
            axes[row, col].set_xlabel("Score")
            axes[row, col].set_ylabel("Frequency")

        # Save plot
        plt.tight_layout()
        plt.savefig(self.data_dir / "metrics_distribution.png")
        plt.close()

        # Correlation heatmap
        plt.figure(figsize=(10, 8))
        correlation_data = {name: values for name, values in metrics.items()}
        sns.heatmap(
            pd.DataFrame(correlation_data).corr(), annot=True, cmap="coolwarm", center=0
        )
        plt.title("Metric Correlations")
        plt.tight_layout()
        plt.savefig(self.data_dir / "metric_correlations.png")
        plt.close()

    def _format_json_report(self, session_data: Dict, stats: Dict) -> str:
        """Format report as JSON"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_data.get("session_id"),
            "total_interactions": len(session_data.get("interactions", [])),
            "statistical_analysis": stats,
            "visualizations": ["metrics_distribution.png", "metric_correlations.png"],
        }

        return json.dumps(report, indent=2)
