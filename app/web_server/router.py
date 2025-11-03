from fastapi import APIRouter, status, Path, Query, HTTPException
from fastapi.responses import JSONResponse
import os
import yaml
from app.task_processing.celery_app import celery_app
from celery.result import AsyncResult
from app.task_processing.tasks_engine import generate_tasks_structure
from app.utils.schemas import WorkflowRequest, ChatRequest, WorkflowResponse
from libs.database_service.sql_db.providers import PgSQLProvider

router = APIRouter()

@router.get("/health")
def health():
    task = celery_app.send_task('health_check', args=[])
    result = AsyncResult(task.id, app=celery_app)
    return JSONResponse({"api": "ok", "celery_task": task.id, "celery_state": result.state})

@router.get("/api/workflow/{workflow_id}/status")
def get_workflow_status(workflow_id: str):
    """Get the status of all tasks in a workflow"""
    try:
        # This is a simplified version - in production you'd want to store task IDs in a database
        return JSONResponse({
            "workflow_id": workflow_id,
            "message": "Workflow status endpoint - task IDs should be stored in database for full implementation",
            "status": "active"
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "internal_error", "details": str(e)})

@router.post(
    "/api/workflow/{template}",
    summary="Start a workflow",
    description="Start a new workflow using the specified template. The workflow will process documents through the graph preprocessing pipeline.",
    response_description="Returns the workflow ID and task structure for monitoring progress",
    response_model=WorkflowResponse
)
def start_workflow(
    request: WorkflowRequest,
    template: str = Path(..., description="Template name (e.g., 'graph_preprocessing')")
):
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_dir = os.path.join(base_dir, 'templates')
        template_path = os.path.join(templates_dir, f"{template}.yml")
        if not os.path.exists(template_path):
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content={"error": "invalid_template", "details": "Template not found"})

        with open(template_path, 'r', encoding='utf-8') as f:
            template_config = yaml.safe_load(f) or {}

        # Assuming workflow_id is part of the input for now
        workflow_id = request.input.get("workflow_id", "default_workflow")

        # Generate tasks structure
        tasks_structure = generate_tasks_structure(
            workflow_input={"workflow_id": workflow_id, **request.input},
            template_config=template_config
        )

        return WorkflowResponse(
            workflow_id=workflow_id,
            tasks=tasks_structure
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": "internal_error", "details": str(e)})



@router.post(
    "/api/chat/{template}",
    summary="Start a chat workflow",
    description="Start a new chat workflow using the specified template. The workflow will process user input through the graph inference pipeline.",
    response_description="Returns the workflow ID and task structure for monitoring progress",
    response_model=WorkflowResponse
)
def start_chat_workflow(
    request: ChatRequest,
    template: str = Path(..., description="Template name (e.g., 'graph_inference')")
):
    try:
        print('################# /api/chat/{template} #################')
        print(f'{request.input=}')
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_dir = os.path.join(base_dir, 'templates')
        template_path = os.path.join(templates_dir, f"{template}.yml")
        if not os.path.exists(template_path):
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content={"error": "invalid_template", "details": "Template not found"})

        with open(template_path, 'r', encoding='utf-8') as f:
            template_config = yaml.safe_load(f) or {}

        # Assuming workflow_id is part of the input for now
        workflow_id = request.input.get("workflow_id", "default_workflow")

        # Generate tasks structure
        tasks_structure = generate_tasks_structure(
            workflow_input={"workflow_id": workflow_id, **request.input},
            template_config=template_config
        )

        return WorkflowResponse(
            workflow_id=workflow_id,
            tasks=tasks_structure
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": "internal_error", "details": str(e)})



@router.get("/api/results/{task_id}")
def job_result(task_id: str):
    """
    Get final result (200) or 202 if still running.
    """
    ar: AsyncResult = celery_app.AsyncResult(task_id)
    if not ar.ready():
        raise HTTPException(status_code=202, detail={"state": ar.state})
    if ar.failed():
        raise HTTPException(status_code=500, detail=str(ar.info))
    return {"task_id": task_id, "result": ar.result}


@router.get(
    "/api/chat-history",
    summary="Get chat history",
    description="Fetch all chat history messages for a specific session using project_id and session_id",
    response_description="Returns all chat history messages (user and assistant) for the specified session"
)
def get_chat_history(
    project_id: str = Query(..., description="Project ID to filter chat history"),
    session_id: str = Query(..., description="Session ID to filter chat history"),
    client_id: str = Query(None, description="Optional client ID to filter chat history")
):
    """
    Get all chat history for a specific session.
    
    Args:
        project_id: The project identifier
        session_id: The session identifier
        client_id: Optional client identifier (defaults to project_id if not provided)
    
    Returns:
        JSON response with all chat history messages and metadata
    """
    try:
        # Use project_id as client_id if client_id is not provided
        if not client_id:
            client_id = project_id
            
        # Initialize database provider
        db = PgSQLProvider()
        
        # Fetch all messages for this session
        messages = db.get_messages(
            client_id=client_id,
            project_id=project_id,
            session_id=session_id
        )
        
        # Convert datetime objects to ISO format strings for JSON serialization
        serialized_messages = []
        for message in messages:
            message_dict = dict(message)
            if 'created_at' in message_dict and hasattr(message_dict['created_at'], 'isoformat'):
                message_dict['created_at'] = message_dict['created_at'].isoformat()
            serialized_messages.append(message_dict)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "chat_history": serialized_messages,
                "metadata": {
                    "total_messages": len(serialized_messages),
                    "client_id": client_id,
                    "project_id": project_id,
                    "session_id": session_id
                }
            }
        )
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error fetching chat history: {error_traceback}")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "internal_error",
                "details": str(e),
                "chat_history": [],
                "metadata": {
                    "total_messages": 0,
                    "client_id": client_id,
                    "project_id": project_id,
                    "session_id": session_id
                }
            }
        )