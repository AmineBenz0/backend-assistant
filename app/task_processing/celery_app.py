import time
from celery import Celery, signals
from celery.result import AsyncResult
from celery.exceptions import Ignore
from app.configs.environment_settings import settings
from app.pipelines.pipelines_app import execute_pipeline_step
from app.utils.webhooks import CallbackTask
from typing import Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    "tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_broker_url,
    result_serializer='pickle'
)

celery_app.config_from_object('app.configs.celery_config')
celery_app.conf.accept_content = ['application/json', 'application/x-python-serialize']
celery_app.conf.update(result_extended=True)

@celery_app.task(name='health_check')
def health_check():
    return {"status": "ok"}

def wait_for_task(task_id: str, timeout: int = 3600) -> Dict[str, Any]:
    """
    Waits for a Celery task to complete with a timeout.
    
    :param task_id: The task ID string.
    :param timeout: The maximum time (in seconds) to wait for the task. Default is 3600 seconds (1 hour).
    :return: The result of the task if it completes within the timeout.
    :raises TimeoutError: If the task does not complete within the timeout period.
    """
    result = AsyncResult(task_id, app=celery_app)
    start_time = time.time()
    check_interval = 5  # Check every 5 seconds to reduce CPU usage
    
    logger.info(f"Waiting for prerequisite task {task_id} (timeout: {timeout}s)")
    
    while not result.ready():
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"Task {task_id} timed out after {timeout} seconds")
        
        # Log progress every 60 seconds
        if int(elapsed) % 60 == 0 and elapsed > 0:
            logger.info(f"Still waiting for task {task_id}... ({int(elapsed)}s elapsed)")
        
        time.sleep(check_interval)
    
    if result.successful():
        logger.info(f"Prerequisite task {task_id} completed successfully")
        return result.result
    else:
        # If task failed, raise the exception
        logger.error(f"Prerequisite task {task_id} failed: {result.result}")
        raise result.result

@celery_app.task(bind=True, base=CallbackTask, name='llm_call', autoretry_for=(Exception,), retry_kwargs={'max_retries': 2}, serializer='json', soft_time_limit=3600, time_limit=7200)
def pipeline_call(self, workflow_id: str, step: str, step_input: Dict[str, Any], workflow_output: Dict[str, Any], step_outputs: Dict[str, str]):
    logger.info(f"Executing pipeline step: {step} for workflow {workflow_id}")
    inputs = step_input["inputs"]

    # Resolve prerequisites - match the example pattern
    if step_input.get("prerequisites", []):
        logger.info(f"Resolving prerequisites for {step}: {step_input['prerequisites']}")
        for prerequisite in step_input["prerequisites"]:
            # Check if the prerequisite is already in the inputs
            if prerequisite in inputs:
                logger.info(f"Prerequisite {prerequisite} already in inputs")
                continue
            else:
                # Wait for the prerequisite task to finish
                prerequisite_task_id = step_outputs.get(prerequisite)
                if prerequisite_task_id:
                    logger.info(f"Waiting for prerequisite task {prerequisite_task_id} ({prerequisite})")
                    try:
                        # Check if the task is already completed before waiting
                        result = AsyncResult(prerequisite_task_id, app=celery_app)
                        if result.ready():
                            if result.successful():
                                prerequisite_result = result.result
                                logger.info(f"Prerequisite {prerequisite} already completed")
                            else:
                                logger.error(f"Prerequisite {prerequisite} failed: {result.result}")
                                # Don't retry if prerequisite failed - fail immediately
                                raise Exception(f"Prerequisite {prerequisite} failed: {result.result}")
                        else:
                            # Task is still running, wait for it with a reasonable timeout
                            # Use a shorter timeout for individual prerequisites to avoid blocking too long
                            prerequisite_result = wait_for_task(prerequisite_task_id, timeout=1800)  # 30 minutes max per prerequisite
                        
                        # Extract the actual result from the response structure
                        if isinstance(prerequisite_result, dict) and 'response' in prerequisite_result:
                            inputs.update({prerequisite: prerequisite_result['response']})
                        else:
                            inputs.update({prerequisite: prerequisite_result})
                        logger.info(f"Successfully resolved prerequisite {prerequisite}")
                    except Exception as e:
                        logger.error(f"Failed to resolve prerequisite {prerequisite}: {e}")
                        raise
                else:
                    logger.warning(f"Prerequisite task ID not found for {prerequisite}")

    # Process inputs to resolve any remaining task IDs
    inputs = process_inputs(inputs)
    
    # Execute the pipeline step
    try:
        logger.info(f"Executing pipeline step {step} with inputs: {list(inputs.keys())}")
        result = execute_pipeline_step(
            inputs=inputs,
            project_name=step_input["project_name"],
            prompt_config_src=step_input["prompt_config_src"],
            pipeline_key=step_input["pipeline_key"],
            json_object=step_input.get("json_object", False),
            domain_id=step_input.get("domain_id")
        )
        logger.info(f"Successfully completed pipeline step {step}")
        return {
            "workflow_id": workflow_id,
            "action": step_input.get("action"),
            "response": result,
            "version": "new_version",
            "webhook_response": True if step_input.get("section_id") else False
        }
    except Exception as e:
        logger.error(f"Error executing pipeline step {step}: {e}", exc_info=True)
        raise


def process_inputs(inputs):
    """Process inputs to resolve any task IDs to their results."""
    import re
    
    for key, value in inputs.items():
        if isinstance(value, str):
            continue
        if isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], str):
                # Check if it's a UUID (task ID)
                if re.match(r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$', value[0]):
                    output = ""
                    for item in value:
                        task_result = wait_for_task(item)
                        if isinstance(task_result, dict) and 'response' in task_result:
                            output += str(task_result["response"])
                        else:
                            output += str(task_result)
                    inputs.update({key: output})
    
    return inputs
