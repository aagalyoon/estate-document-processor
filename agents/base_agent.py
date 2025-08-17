from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from datetime import datetime
import time


class BaseAgent(ABC):
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
        self._metrics = {
            "processed_count": 0,
            "error_count": 0,
            "success_count": 0,
            "last_processed": None,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "min_processing_time": float('inf'),
            "max_processing_time": 0.0
        }
        self._start_time = None
    
    @abstractmethod
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    def start_processing(self):
        """Mark the start of processing for timing metrics"""
        self._start_time = time.time()
    
    def log_processing(self, success: bool = True):
        """Log processing completion and update metrics"""
        if self._start_time:
            processing_time = time.time() - self._start_time
            self._update_timing_metrics(processing_time)
            self._start_time = None
        
        self._metrics["processed_count"] += 1
        if success:
            self._metrics["success_count"] += 1
        else:
            self._metrics["error_count"] += 1
        self._metrics["last_processed"] = datetime.now()
    
    def _update_timing_metrics(self, processing_time: float):
        """Update timing-related metrics"""
        self._metrics["total_processing_time"] += processing_time
        self._metrics["min_processing_time"] = min(
            self._metrics["min_processing_time"], 
            processing_time
        )
        self._metrics["max_processing_time"] = max(
            self._metrics["max_processing_time"], 
            processing_time
        )
        
        # Calculate average
        if self._metrics["processed_count"] > 0:
            self._metrics["average_processing_time"] = (
                self._metrics["total_processing_time"] / 
                (self._metrics["processed_count"] + 1)  # +1 for current
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get a copy of current metrics"""
        metrics = self._metrics.copy()
        
        # Calculate success rate
        if metrics["processed_count"] > 0:
            metrics["success_rate"] = (
                metrics["success_count"] / metrics["processed_count"]
            ) * 100
        else:
            metrics["success_rate"] = 0.0
        
        # Format times for readability
        if metrics["min_processing_time"] == float('inf'):
            metrics["min_processing_time"] = 0.0
        
        # Round times to 4 decimal places
        for key in ["total_processing_time", "average_processing_time", 
                   "min_processing_time", "max_processing_time"]:
            metrics[key] = round(metrics[key], 4)
        
        return metrics
    
    def reset_metrics(self):
        """Reset all metrics to initial state"""
        self._metrics = {
            "processed_count": 0,
            "error_count": 0,
            "success_count": 0,
            "last_processed": None,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "min_processing_time": float('inf'),
            "max_processing_time": 0.0
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"