import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in the Jetski framework.
    """
    def __init__(self, name: str, role: str, system_prompt: str, config_path: str = "config.json"):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.config = self._load_config(config_path)
        self.gcp_project = self.config.get("gcp", {}).get("project_id")
        self.gcp_region = self.config.get("gcp", {}).get("region")
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Loads GCP and database configurations."""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return {}

    @abstractmethod
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes a task given a specific context.
        
        Args:
            task: A string description of what the agent needs to do.
            context: A dictionary of key-value pairs representing execution state, history, or variables.
            
        Returns:
            A dictionary containing execution results, status, and updated context.
        """
        pass

    def get_system_context(self) -> str:
        """Helper to compile the full system instructions for the LLM."""
        return (
            f"You are {self.name}, the {self.role}.\n"
            f"Active GCP Project: {self.gcp_project}\n"
            f"Active Region: {self.gcp_region}\n\n"
            f"System Instructions:\n{self.system_prompt}"
        )
