"""
Alignment and Self-Healing Module for MiddleSeek
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import Counter

# Configure healing logger
healing_logger = logging.getLogger(f"{__name__}.healing")
healing_logger.setLevel(logging.INFO)
healing_logger.propagate = False

class SystemHealth:
    """Monitors and maintains system health."""

    def __init__(self):
        self.health_metrics = {
            "api_calls": 0,
            "errors": 0,
            "compassion_scores": [],
            "response_times": [],
            "last_audit": time.time(),
            "healing_attempts": 0,
            "consecutive_errors": 0,
            "total_healing_events": 0
        }
        self.health_thresholds = {
            "max_errors_per_minute": 10,
            "min_compassion_average": 2.5,
            "max_response_time": 30.0,
            "max_healing_attempts": 3,
            "response_time_window": 10,
            "max_consecutive_errors": 5,
            "min_health_check_interval": 60  # seconds
        }
        self.healing_logger = healing_logger

    def record_metric(self, metric: str, value: Any) -> None:
        """Record a health metric."""
        if metric in self.health_metrics:
            if isinstance(self.health_metrics[metric], list):
                self.health_metrics[metric].append(value)
                # Keep only last 100 entries
                if len(self.health_metrics[metric]) > 100:
                    self.health_metrics[metric] = self.health_metrics[metric][-100:]
            else:
                self.health_metrics[metric] = value

    def check_health(self) -> Tuple[bool, str]:
        """Check system health and return status with message."""
        current_time = time.time()
        time_since_last_audit = current_time - self.health_metrics["last_audit"]

        # Check if enough time has passed since last audit
        if time_since_last_audit < self.health_thresholds["min_health_check_interval"]:
            return True, "System healthy (recently checked)"

        # Check error rate
        if self.health_metrics["errors"] > self.health_thresholds["max_errors_per_minute"]:
            self.healing_logger.warning(f"Error rate {self.health_metrics['errors']} exceeds threshold {self.health_thresholds['max_errors_per_minute']}")
            return False, "Error rate exceeds threshold"

        # Check consecutive errors
        if self.health_metrics["consecutive_errors"] > self.health_thresholds["max_consecutive_errors"]:
            self.healing_logger.warning(f"Consecutive errors {self.health_metrics['consecutive_errors']} exceed threshold {self.health_thresholds['max_consecutive_errors']}")
            return False, "Too many consecutive errors"

        # Check compassion scores
        if self.health_metrics["compassion_scores"]:
            avg_compassion = sum(self.health_metrics["compassion_scores"]) / len(self.health_metrics["compassion_scores"])
            if avg_compassion < self.health_thresholds["min_compassion_average"]:
                self.healing_logger.warning(f"Average compassion score {avg_compassion:.2f} below threshold {self.health_thresholds['min_compassion_average']}")
                return False, "Compassion scores below threshold"

        # Check response times using a rolling window
        if self.health_metrics["response_times"]:
            recent_times = self.health_metrics["response_times"][-self.health_thresholds["response_time_window"]:]
            avg_response_time = sum(recent_times) / len(recent_times)
            if avg_response_time > self.health_thresholds["max_response_time"]:
                self.healing_logger.warning(f"Average response time {avg_response_time:.2f}s exceeds threshold {self.health_thresholds['max_response_time']}s")
                return False, "Response times above threshold"

        # Update last audit time
        self.health_metrics["last_audit"] = current_time
        return True, "System healthy"

    def attempt_healing(self) -> bool:
        """Attempt to heal the system."""
        if self.health_metrics["healing_attempts"] >= self.health_thresholds["max_healing_attempts"]:
            self.healing_logger.error(f"Maximum healing attempts ({self.health_thresholds['max_healing_attempts']}) reached")
            return False

        self.health_metrics["healing_attempts"] += 1
        self.health_metrics["total_healing_events"] += 1
        self.health_metrics["errors"] = 0
        self.health_metrics["consecutive_errors"] = 0
        self.health_metrics["last_audit"] = time.time()
        self.healing_logger.info(f"Healing attempt {self.health_metrics['healing_attempts']} initiated")
        return True

    def reset_metrics(self) -> None:
        """Reset health metrics."""
        self.health_metrics = {
            "api_calls": 0,
            "errors": 0,
            "compassion_scores": [],
            "response_times": [],
            "last_audit": time.time(),
            "healing_attempts": 0,
            "consecutive_errors": 0,
            "total_healing_events": 0
        }
        self.healing_logger.info("Health metrics reset")

@dataclass
class AlignmentMetrics:
    """Metrics for AI alignment analysis."""
    total_interactions: int
    healing_events: int
    compassion_scores: List[float]
    response_times: List[float]
    harmful_patterns: Counter
    healing_reasons: Counter
    time_period: timedelta
    alignment_score: float  # 0-1 scale
    consecutive_errors: int
    total_healing_events: int

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary for serialization."""
        return {
            "total_interactions": self.total_interactions,
            "healing_events": self.healing_events,
            "avg_compassion": sum(self.compassion_scores) / len(self.compassion_scores) if self.compassion_scores else 0,
            "avg_response_time": sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            "harmful_patterns": dict(self.harmful_patterns),
            "healing_reasons": dict(self.healing_reasons),
            "time_period_hours": self.time_period.total_seconds() / 3600,
            "alignment_score": self.alignment_score,
            "consecutive_errors": self.consecutive_errors,
            "total_healing_events": self.total_healing_events
        }

class AlignmentAuditor:
    """Analyzes chat history for AI alignment metrics."""

    def __init__(self, chat_history):
        self.chat_history = chat_history
        self.healing_logger = healing_logger
        self.harmful_patterns = [
            # Direct harm
            "harm you", "harm others", "harmful", "violence", "abuse", "illegal", "unethical",
            "manipulation", "deception", "exploitation",
            # Indirect harm
            "hack", "crack", "bypass", "circumvent", "unauthorized", "breach",
            # Privacy concerns
            "personal data", "private information", "sensitive data", "confidential",
            # Ethical concerns
            "discrimination", "bias", "prejudice", "stereotype", "offensive",
            # Security concerns
            "password", "credential", "authentication", "security", "vulnerability",
            # Misinformation
            "fake", "false", "misleading", "deceptive", "misinformation"
        ]

    def analyze_alignment(self, time_window: Optional[timedelta] = None) -> AlignmentMetrics:
        """Analyze chat history for AI alignment metrics."""
        if not self.chat_history.history:
            return AlignmentMetrics(
                total_interactions=0,
                healing_events=0,
                compassion_scores=[],
                response_times=[],
                harmful_patterns=Counter(),
                healing_reasons=Counter(),
                time_period=timedelta(0),
                alignment_score=1.0,
                consecutive_errors=0,
                total_healing_events=0
            )

        # Filter entries by time window if specified
        now = datetime.now()
        entries = [
            entry for entry in self.chat_history.history
            if not time_window or (now - entry.timestamp) <= time_window
        ]

        if not entries:
            return AlignmentMetrics(
                total_interactions=0,
                healing_events=0,
                compassion_scores=[],
                response_times=[],
                harmful_patterns=Counter(),
                healing_reasons=Counter(),
                time_period=time_window or timedelta(0),
                alignment_score=1.0,
                consecutive_errors=0,
                total_healing_events=0
            )

        # Calculate metrics
        healing_events = sum(1 for entry in entries if entry.healed_response is not None)
        compassion_scores = [entry.compassion_score for entry in entries]
        response_times = [entry.response_time for entry in entries if hasattr(entry, 'response_time')]
        harmful_patterns = Counter()
        healing_reasons = Counter()
        consecutive_errors = 0
        current_streak = 0

        for entry in entries:
            if entry.healing_reason:
                healing_reasons[entry.healing_reason] += 1
                # Check for harmful patterns in original response
                response_lower = entry.original_response.lower()
                for pattern in self.harmful_patterns:
                    if pattern in response_lower:
                        harmful_patterns[pattern] += 1
                        current_streak += 1
                        consecutive_errors = max(consecutive_errors, current_streak)
                    else:
                        current_streak = 0

        # Calculate alignment score (0-1 scale)
        alignment_score = self._calculate_alignment_score(
            total_interactions=len(entries),
            healing_events=healing_events,
            avg_compassion=sum(compassion_scores) / len(compassion_scores) if compassion_scores else 0,
            harmful_patterns=harmful_patterns,
            consecutive_errors=consecutive_errors,
            response_times=response_times
        )

        return AlignmentMetrics(
            total_interactions=len(entries),
            healing_events=healing_events,
            compassion_scores=compassion_scores,
            response_times=response_times,
            harmful_patterns=harmful_patterns,
            healing_reasons=healing_reasons,
            time_period=time_window or (now - entries[0].timestamp),
            alignment_score=alignment_score,
            consecutive_errors=consecutive_errors,
            total_healing_events=healing_events
        )

    def _calculate_alignment_score(self, total_interactions: int, healing_events: int,
                                 avg_compassion: float, harmful_patterns: Counter,
                                 consecutive_errors: int, response_times: List[float]) -> float:
        """Calculate alignment score based on various metrics."""
        if total_interactions == 0:
            return 1.0

        # Weights for different factors
        weights = {
            'healing_rate': 0.25,
            'compassion': 0.25,
            'harmful_patterns': 0.2,
            'consecutive_errors': 0.15,
            'response_time': 0.15
        }

        # Calculate healing rate score (lower is better)
        healing_rate = healing_events / total_interactions
        healing_score = 1.0 - healing_rate

        # Calculate compassion score (normalized to 0-1)
        compassion_score = min(avg_compassion / 5.0, 1.0)

        # Calculate harmful patterns score (lower is better)
        harmful_score = 1.0 - (sum(harmful_patterns.values()) / total_interactions)

        # Calculate consecutive errors score (lower is better)
        error_score = 1.0 - (consecutive_errors / total_interactions)

        # Calculate response time score
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            response_score = 1.0 - (avg_response_time / 30.0)  # Normalize against 30s threshold
        else:
            response_score = 1.0

        # Calculate weighted average
        alignment_score = (
            weights['healing_rate'] * healing_score +
            weights['compassion'] * compassion_score +
            weights['harmful_patterns'] * harmful_score +
            weights['consecutive_errors'] * error_score +
            weights['response_time'] * response_score
        )

        return max(0.0, min(1.0, alignment_score))

    def generate_alignment_report(self, time_window: Optional[timedelta] = None) -> str:
        """Generate a human-readable alignment report."""
        metrics = self.analyze_alignment(time_window)

        report = [
            "=== AI Alignment Report ===",
            f"Time Period: {metrics.time_period.total_seconds() / 3600:.1f} hours",
            f"Total Interactions: {metrics.total_interactions}",
            f"Alignment Score: {metrics.alignment_score:.2%}",
            "\nCompassion Metrics:",
            f"- Average Compassion Score: {sum(metrics.compassion_scores) / len(metrics.compassion_scores):.2f}/5.0" if metrics.compassion_scores else "- No compassion scores recorded",
            "\nHealing Events:",
            f"- Total Healing Events: {metrics.healing_events}",
            f"- Healing Rate: {metrics.healing_events / metrics.total_interactions:.1%}" if metrics.total_interactions > 0 else "- No interactions recorded",
            f"- Consecutive Errors: {metrics.consecutive_errors}",
            "\nResponse Times:",
            f"- Average Response Time: {sum(metrics.response_times) / len(metrics.response_times):.2f}s" if metrics.response_times else "- No response times recorded"
        ]

        if metrics.healing_reasons:
            report.append("\nHealing Reasons:")
            for reason, count in metrics.healing_reasons.most_common():
                report.append(f"- {reason}: {count} times")

        if metrics.harmful_patterns:
            report.append("\nDetected Harmful Patterns:")
            for pattern, count in metrics.harmful_patterns.most_common():
                report.append(f"- {pattern}: {count} times")

        report.append("\nRecommendations:")
        if metrics.alignment_score < 0.7:
            report.append("- Consider reviewing and adjusting response patterns")
            report.append("- Monitor for recurring harmful patterns")
            report.append("- Evaluate compassion score distribution")
            if metrics.consecutive_errors > 0:
                report.append("- Address consecutive error patterns")
            if metrics.response_times and sum(metrics.response_times) / len(metrics.response_times) > 20:
                report.append("- Investigate response time performance")
        else:
            report.append("- System is maintaining good alignment")
            report.append("- Continue monitoring for any changes in patterns")

        return "\n".join(report)
