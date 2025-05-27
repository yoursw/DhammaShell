"""
Empathy Metrics Module for DhammaShell
Defines metrics and scoring for empathy analysis
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class EmpathyMetric:
    """Represents a single empathy metric measurement"""
    name: str
    value: float
    timestamp: datetime
    context: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert metric to dictionary format"""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EmpathyMetric':
        """Create metric from dictionary format"""
        return cls(
            name=data["name"],
            value=data["value"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            context=data.get("context")
        )

class EmpathyMetrics:
    """Manages collection and analysis of empathy metrics"""
    
    def __init__(self):
        self.metrics: List[EmpathyMetric] = []
        
    def add_metric(self, metric: EmpathyMetric) -> None:
        """Add a new metric measurement"""
        self.metrics.append(metric)
        
    def get_metrics_by_name(self, name: str) -> List[EmpathyMetric]:
        """Get all metrics with the given name"""
        return [m for m in self.metrics if m.name == name]
        
    def get_latest_metric(self, name: str) -> Optional[EmpathyMetric]:
        """Get the most recent metric with the given name"""
        metrics = self.get_metrics_by_name(name)
        return max(metrics, key=lambda m: m.timestamp) if metrics else None
        
    def get_average(self, name: str) -> float:
        """Calculate average value for metrics with the given name"""
        metrics = self.get_metrics_by_name(name)
        if not metrics:
            return 0.0
        return sum(m.value for m in metrics) / len(metrics)
        
    def get_trend(self, name: str) -> float:
        """Calculate trend (slope) for metrics with the given name"""
        metrics = sorted(self.get_metrics_by_name(name), key=lambda m: m.timestamp)
        if len(metrics) < 2:
            return 0.0
            
        # Simple linear regression
        x = [i for i in range(len(metrics))]
        y = [m.value for m in metrics]
        n = len(x)
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(i * v for i, v in zip(x, y))
        sum_xx = sum(i * i for i in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        return slope
        
    def to_dict(self) -> Dict:
        """Convert all metrics to dictionary format"""
        return {
            "metrics": [m.to_dict() for m in self.metrics]
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'EmpathyMetrics':
        """Create metrics collection from dictionary format"""
        metrics = cls()
        for metric_data in data["metrics"]:
            metrics.add_metric(EmpathyMetric.from_dict(metric_data))
        return metrics 