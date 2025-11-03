from pydantic import BaseModel, Field
from typing import List, Dict, Any


class WorkflowRequest(BaseModel):
    input: Dict[str, Any] = Field(
        ...,
        description="Workflow input parameters",
        example={
            "workflow_id": "graph_preprocessing_001",
            "client_id": "testclient",
            "project_id": "testproject",
            "domain_id": "resume"
        }
    )


class ChatRequest(BaseModel):
    input: Dict[str, Any] = Field(
        ...,
        description="Chat workflow input parameters",
        example={
            "workflow_id": "graph_inference_001",
            "client_id": "testclient",
            "domain_id": "dpac",
            "project_id": "dpac",
            "session_id": "123",
            "input_text": "what is dpac?"
        }
    )


class TaskInfo(BaseModel):
    step_name: str = Field(..., description="Name of the pipeline step")
    pipeline_key: str = Field(..., description="Pipeline key for the step")
    task_id: str = Field(..., description="Celery task ID")
    queue: str = Field(..., description="Queue name where the task is running")
    status: str = Field(..., description="Current status of the task")


class WorkflowResponse(BaseModel):
    workflow_id: str = Field(..., description="Unique identifier for the workflow")
    tasks: List[TaskInfo] = Field(..., description="List of tasks in the workflow")
