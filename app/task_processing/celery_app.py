import time
from celery import Celery, signals
from celery.result import AsyncResult
from celery.exceptions import Ignore
from app.configs.environment_settings import settings
from app.pipelines.pipelines_app import execute_pipeline_step
from app.utils.webhooks import CallbackTask
from typing import Dict, Any
import asyncio
import copy
import logging
import random
import re
import time as _time
try:
    import openai
except Exception:
    openai = None

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

@celery_app.task(bind=True, base=CallbackTask, name='llm_call', serializer='json', soft_time_limit=3600, time_limit=7200)
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

    # Parallel handling
    parallel_task = step_input.get("parallel_task", False)
    parallel_merge = step_input.get("parallel_merge", False)

    if parallel_task and step_input.get("parallel_inputs"):
        logger.info(f"Executing step {step} in parallel mode over inputs: {step_input.get('parallel_inputs')}")
        response, version = process_parallel_tasks(
            workflow_id, step_input, inputs, step, workflow_output, step_outputs, parallel_merge
        )
        return {
            "workflow_id": workflow_id,
            "action": step_input.get("action"),
            "response": response,
            "version": version,
            "webhook_response": True if step_input.get("section_id") else False
        }

    # Execute the pipeline step sequentially
    try:
        # Light pacing for io-bound tasks to reduce burst rate limiting
        if step_input.get("queue") == "io_queue":
            sleep_s = random.uniform(0.5, 2.0)
            logger.info(f"Pacing io_queue task by {sleep_s:.2f}s before execution")
            _time.sleep(sleep_s)

        logger.info(f"Executing pipeline step {step} with inputs: {list(inputs.keys())}")
        result = execute_pipeline_step(
            inputs=inputs,
            project_name=step_input["project_name"],
            prompt_config=step_input["prompt_config"],
            pipeline_key=step_input["pipeline_key"],
            json_object=step_input.get("json_object", False),
            domain_id=step_input.get("domain_id"),
            save_to_db=step_input.get("save_to_db")
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
        # Detect rate-limits (HTTP 429) and apply exponential backoff with jitter
        msg = str(e)
        is_rate_limited = ("429" in msg) or (openai and isinstance(e, getattr(openai, "RateLimitError", Exception)))
        if is_rate_limited:
            attempt = (self.request.retries or 0) + 1
            # If we've already tried enough times, fail hard so Celery marks FAILURE
            if attempt >= 5:
                logger.error(f"Rate limit persisted for step {step} after {attempt} attempts; failing the task")
                raise
            # Parse suggested retry-after seconds if present
            retry_after = 2
            m = re.search(r"retry after\s+(\d+)\s*seconds", msg, flags=re.IGNORECASE)
            if m:
                try:
                    retry_after = max(1, int(m.group(1)))
                except Exception:
                    retry_after = 2
            # Exponential backoff with cap and jitter; more conservative on io_queue
            base = max(2, retry_after)
            delay = min(base * (2 ** (attempt - 1)), 300)
            delay = delay + random.uniform(0, min(5.0, delay / 5))
            if step_input.get("queue") == "io_queue":
                delay = min(delay * 1.5, 420)
            logger.warning(f"Rate limit detected for step {step}. Retrying in {delay:.1f}s (attempt {attempt})")
            raise self.retry(exc=e, countdown=int(delay))
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


def process_parallel_tasks(workflow_id: str, step_input: Dict[str, Any], inputs: Dict[str, Any], step: str, workflow_output: Dict[str, Any], step_outputs: Dict[str, str], parallel_merge: bool):
    """
    Create and run sub-tasks in parallel for the given step.

    - Uses the first key in parallel_inputs to determine iteration length
    - For each index, sets each parallel_input to its ith element (or the same value if not a list)
    - Queues a subtask for each item and aggregates responses
    """
    new_input = copy.deepcopy(step_input)
    parallel_inputs_keys = step_input.get("parallel_inputs", [])
    if not parallel_inputs_keys:
        logger.warning("parallel_task enabled but no parallel_inputs specified; falling back to sequential")
        result = execute_pipeline_step(
            inputs=inputs,
            project_name=step_input["project_name"],
            prompt_config=step_input["prompt_config"],
            pipeline_key=step_input["pipeline_key"],
            json_object=step_input.get("json_object", False),
            domain_id=step_input.get("domain_id"),
            save_to_db=step_input.get("save_to_db")
        )
        return result, "new_version"

    first_key = parallel_inputs_keys[0]
    if first_key not in inputs:
        logger.error(f"Parallel input '{first_key}' not found in inputs for step {step}")
        return [], "parallel_error"

    first_data = inputs[first_key]
    if not isinstance(first_data, list):
        logger.info(f"Parallel input '{first_key}' is not a list; treating as a single-item list for step {step}")
        first_data = [first_data]

    if not first_data:
        logger.warning(f"Parallel input '{first_key}' is empty for step {step}")
        return [], "parallel_empty"

    sub_tasks = []
    responses = []

    for i in range(len(first_data)):
        task_input = copy.deepcopy(new_input)
        # Set parallel inputs for index i
        for key in parallel_inputs_keys:
            if key in inputs:
                value = inputs[key]
                if isinstance(value, list):
                    task_input['inputs'][key] = value[i] if i < len(value) else None
                else:
                    task_input['inputs'][key] = value
            else:
                logger.warning(f"Parallel input '{key}' not found in inputs for subtask index {i}")
                task_input['inputs'][key] = None

        # Ensure subtasks run sequentially (no nested parallel)
        task_input['parallel_task'] = False

        sub_task = pipeline_call.apply_async(
            args=[workflow_id, step, task_input, workflow_output, step_outputs],
            queue=task_input.get('queue', 'default_queue')
        )
        sub_tasks.append(sub_task)
        # Stagger io_queue enqueueing slightly to avoid burst RPM spikes
        if task_input.get('queue') == 'io_queue':
            _time.sleep(random.uniform(0.05, 0.25))

    # Collect results
    for idx, t in enumerate(sub_tasks):
        try:
            sub_result = wait_for_task(t.id)
            # Expect dict with 'response'
            responses.append(sub_result.get('response') if isinstance(sub_result, dict) else sub_result)
        except Exception as e:
            logger.error(f"Parallel subtask {idx+1}/{len(sub_tasks)} for step {step} failed: {e}")
            responses.append(None)
            # Fail-fast: if any parallel subtask failed, propagate failure so Celery marks FAILURE
            # This ensures tasks with rate-limit or other errors are not reported as SUCCESS overall
            raise

    # Merge if requested
    if parallel_merge:
        merged = []
        for item in responses:
            if item is None:
                continue
            if isinstance(item, list):
                merged.extend(item)
            else:
                merged.append(item)
        responses = merged

    return responses, "parallel"
