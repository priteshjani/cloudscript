import logging
from typing import Dict, Any, Type
from workflow.base import BaseWorkflow

logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    """
    Registry and execution manager for workflows. Can be connected to
    a web framework (like FastAPI or Flask) to serve endpoints to the React frontend.
    """
    def __init__(self):
        self._registry: Dict[str, Type[BaseWorkflow]] = {}

    def register_workflow(self, name: str, workflow_cls: Type[BaseWorkflow]):
        """Registers a workflow class to the registry."""
        self._registry[name] = workflow_cls
        logger.info(f"Registered workflow: {name}")

    def execute_workflow(self, name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Instantiates and executes a registered workflow.
        """
        if name not in self._registry:
            raise ValueError(f"Workflow '{name}' not found in registry.")

        workflow_cls = self._registry[name]
        workflow_instance = workflow_cls()
        
        logger.info(f"Starting execution of workflow '{name}'...")
        try:
            result = workflow_instance.run(input_data)
            logger.info(f"Workflow '{name}' finished with state: {workflow_instance.state}")
            return result
        except Exception as e:
            logger.error(f"Error executing workflow '{name}': {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
                "state": workflow_instance.state,
                "context": workflow_instance.context
            }
        
    def get_registered_workflows(self) -> list:
        """Returns the list of registered workflow names."""
        return list(self._registry.keys())
