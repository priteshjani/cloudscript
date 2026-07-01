import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BaseWorkflow(ABC):
    """
    Abstract base class for all orchestrations and workflows in the Jetski framework.
    """
    def __init__(self, name: str):
        self.name = name
        self.context: Dict[str, Any] = {}
        self.state: str = "INITIALIZED"

    def update_context(self, updates: Dict[str, Any]):
        """Safely updates the shared execution context."""
        if updates:
            self.context.update(updates)

    def set_state(self, new_state: str):
        """Transitions workflow to a new state."""
        logger.info(f"Workflow '{self.name}': Transitioning state from {self.state} to {new_state}")
        self.state = new_state

    @abstractmethod
    def run(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the workflow.
        
        Args:
            initial_input: Starting parameters and variables for the execution.
            
        Returns:
            The final execution context and summary.
        """
        pass
