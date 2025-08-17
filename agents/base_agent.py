from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from datetime import datetime


class BaseAgent(ABC):
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
        self._metrics = {
            "processed_count": 0,
            "error_count": 0,
            "last_processed": None
        }
    
    @abstractmethod
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    def log_processing(self, success: bool = True):
        self._metrics["processed_count"] += 1
        if not success:
            self._metrics["error_count"] += 1
        self._metrics["last_processed"] = datetime.now()
    
    def get_metrics(self) -> Dict[str, Any]:
        return self._metrics.copy()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"