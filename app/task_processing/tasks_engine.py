from typing import Dict, List
from app.task_processing.celery_app import celery_app, pipeline_call
from celery.result import AsyncResult


def get_levels(inputs: dict, template_steps: list) -> list:
    """
    Determine execution levels based on dependencies between steps.
    Steps with no dependencies or whose dependencies are satisfied can run in the same level.
    """
    initial_inputs = set(inputs.keys())
    levels = []
    available_inputs = initial_inputs.copy()
    steps = template_steps.copy()
    
    while steps:
        current_level = []
        for step in steps[:]:  # Iterate over a copy of steps
            step_inputs = set(step.get('inputs', []))
            # Check if all step inputs are available (either from initial inputs or completed steps)
            if step_inputs.issubset(available_inputs):
                current_level.append(step['step'])
                steps.remove(step)
        
        if current_level:
            levels.append(current_level)
            # Add completed step names to available inputs for next level
            available_inputs.update(current_level)
        else:
            # If no steps can be executed, we have a circular dependency or missing inputs
            if steps:
                print(f"Warning: Cannot resolve dependencies for remaining steps: {[s['step'] for s in steps]}")
            break
    
    return levels


def format_steps(steps, section, project_name, prompt_config_src, database, domain_id=None):
    formatted_steps = {}
    for step in steps:
        step_config = {
            "project_name": project_name,
            "prompt_config_src": prompt_config_src,
            "database": database,
            "pipeline_key": step['pipeline_key'],
            "action": step.get("action", "section"),
            "section_id": step.get("section_id", None),
            "inputs": {},
            "prerequisites": [],
            "notifications": step.get("notifications", None),
            "parallel_task": step.get("parallel_task", False),
            "parallel_inputs": step.get("parallel_inputs", None),
            "json_object": step.get("json_object", False),
            "queue": step.get("queue", "default_queue"),
            "parallel_merge": step.get("parallel_merge", False)
        }
        
        # Only add domain_id if it's provided
        if domain_id:
            step_config["domain_id"] = domain_id

        steps_dict = {item["step"]: item for item in steps}

        if "inputs" in step:
            for step_input in step["inputs"]:
                if step_input in section["inputs"]:
                    step_config["inputs"][step_input] = section["inputs"][step_input]
                else:
                    temp = steps_dict.get(step_input)
                    if temp:
                        step_config["prerequisites"].append(temp["step"])
                    elif step_input in step.get('optional_inputs', []):
                        step_config["inputs"][step_input] = ""
        formatted_steps[step["step"]] = step_config
    return formatted_steps


def execute_levels(workflow_id, workflow_input, workflow_output, levels, steps_input):
    tasks_ids: Dict[str, str] = {}
    list_steps = list(steps_input.keys())
    in_steps = list(set(list_steps).intersection(workflow_input))
    outputs = {list(item.keys())[0]: list(item.values())[0] for item in workflow_output} if workflow_output else {}

    for level in levels:
        for step in level:
            if step in in_steps:
                continue
            queue = "io_queue" if steps_input[step]['parallel_task'] else steps_input[step]['queue']
            task = pipeline_call.apply_async(
                args=[workflow_id, step, steps_input[step], outputs, tasks_ids],
                queue=queue
            )
            tasks_ids.update({step: task.id})
    return tasks_ids


def generate_tasks_structure(workflow_input: dict, template_config: dict):
    tasks = []
    workflow_id = workflow_input.get('workflow_id', 'default_workflow')
    
    # For graph preprocessing, we expect 'documents' as a top-level input, not nested in 'sections'
    # Prepare inputs for the first level of tasks
    initial_inputs = workflow_input.copy()
    initial_inputs.update(template_config['defaults'])  # Add defaults to inputs

    project_name = template_config['defaults']['template_id']
    prompt_config_src = template_config['defaults']['prompt_config_src']
    database = template_config['defaults']['database']

    required_config = template_config['steps']
    levels = get_levels(initial_inputs, template_config['steps'])

    # Extract domain_id from workflow_input (optional)
    domain_id = workflow_input.get("domain_id")
    
    steps = format_steps(required_config, {"inputs": initial_inputs}, project_name, prompt_config_src, database, domain_id)

    # Initialize empty outputs if not present
    workflow_output = workflow_input.get('outputs', {})

    workflow_task_ids = execute_levels(workflow_id, initial_inputs, workflow_output, levels, steps)
    
    # Format tasks for response
    template_steps_map = {step_config['step']: step_config for step_config in template_config['steps']}

    for step_key, task_id in workflow_task_ids.items():
        step_details = template_steps_map.get(step_key, {})
        tasks.append({
            "step_name": step_key,
            "pipeline_key": step_details.get("pipeline_key"),
            "task_id": task_id,
            "queue": step_details.get("queue"),
            "status": "PENDING"  # Initial status
        })

    return tasks


