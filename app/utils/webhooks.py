from celery import Task
import requests
import json
from app.configs.environment_settings import settings
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__name__)

def is_json_serializable(obj):
    """Check if an object is JSON serializable."""
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False

class CallbackTask(Task):
    @staticmethod
    def send_webhook_notification(payload):
        logger.info(f"#####################################################")
        logger.info(f"#####################################################")
        logger.info(f"#####################################################")
        logger.info(f"{payload=}")
        """Send webhook notification to configured endpoints."""
        if not settings.webhooks:
            logger.info("No webhooks configured, skipping notification")
            return payload
            
        for webhook in settings.webhooks:
            if not webhook.get("url"):
                continue
                
            url = webhook["url"] 
            basic = HTTPBasicAuth(webhook.get("username", ""), webhook.get("password", ""))
            headers = {"Content-Type": "application/json"}
            try:
                response = requests.request(
                    "POST", url, headers=headers, data=json.dumps(payload), timeout=30, auth=basic
                )
                logger.info(f"Webhook notification sent to {url}, status: {response.status_code}")
                logger.info(f"Webhook response: {response.text}")
            except Exception as e:
                logger.error(f"Failed to send webhook notification to {url}: {e}")
        return payload
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle successful task completion."""
        webhook_response = retval.get('webhook_response')
        if webhook_response:
            # Extract original request data from kwargs (passed when task was called)
            # Fallback to args[2]['inputs'] which contains the original inputs
            step_input = args[2] if len(args) > 2 else {}
            inputs = step_input.get('inputs', {}) if isinstance(step_input, dict) else {}
            client_id = kwargs.get('client_id') or retval.get('client_id') or inputs.get('client_id')
            project_id = kwargs.get('project_id') or retval.get('project_id') or inputs.get('project_id')
            session_id = kwargs.get('session_id') or retval.get('session_id') or inputs.get('session_id')
            input_text = kwargs.get('input_text') or retval.get('input_text') or inputs.get('input_text')
            workflow_id = retval.get('workflow_id') or (args[0] if len(args) > 0 else None)
            
            # Build payload; for preprocessing workflows exclude results
            is_preprocessing = False
            try:
                is_preprocessing = bool(workflow_id and "preprocessing" in str(workflow_id).lower())
            except Exception:
                is_preprocessing = False

            if is_preprocessing:
                payload = {
                    "workflow_id": workflow_id,
                    "task_id": task_id,
                    "status": "SUCCESS",
                    "action": retval.get('action'),
                    "client_id": client_id,
                    "project_id": project_id,
                    "session_id": session_id,
                    "input_text": input_text,
                    "version": retval.get('version', 'new_version')
                }
            else:
                # Build complete payload with ALL fields
                logger.info(f"####################################\n########################{type(retval['response'])=}")
                logger.info(f"####################################\n########################{retval['response']=}")

                payload = {
                    "workflow_id": workflow_id,
                    "task_id": task_id,
                    "status": "SUCCESS",
                    "action": retval.get('action'),
                    "result_text": retval['response'].get('llm_output') if 'llm_output' in retval['response'] else retval['response'],
                    "references": retval['response'].get('references') if 'references' in retval['response'] else retval['response'],  
                    "client_id": client_id,
                    "project_id": project_id,
                    "session_id": session_id,
                    "input_text": input_text,
                    "version": retval.get('version', 'new_version')
                }
            
            logger.info(f"✅ SUCCESS webhook payload: {payload}")
            
            if is_json_serializable(payload):
                return self.send_webhook_notification(payload)
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        workflow_id = args[0] if len(args) > 0 else "unknown"
        step_input = args[2] if len(args) > 2 else {}
        action = step_input.get('action') if isinstance(step_input, dict) else None
        webhook_response = True if step_input.get("section_id") else False
        
        if webhook_response:
            # Extract original request data from kwargs
            inputs = step_input.get('inputs', {}) if isinstance(step_input, dict) else {}
            client_id = kwargs.get('client_id') or inputs.get('client_id')
            project_id = kwargs.get('project_id') or inputs.get('project_id')
            session_id = kwargs.get('session_id') or inputs.get('session_id')
            input_text = kwargs.get('input_text') or inputs.get('input_text')
            
            payload = {
                "workflow_id": workflow_id,
                "task_id": task_id,
                "status": "FAILURE",
                "action": action,
                "result": str(exc),
                "result_text": str(exc),
                "client_id": client_id,
                "project_id": project_id,
                "session_id": session_id,
                "input_text": input_text,
            }
            
            logger.info(f"❌ FAILURE webhook payload: {payload}")
            
            if is_json_serializable(payload):
                return self.send_webhook_notification(payload)
                
    def update_custom_state(self, task_id, state, info, step_name=None):
        """Update task state with custom information."""
        self.update_state(task_id=task_id, state=state, meta={'info': info, "exc_type": ""})
        payload = {
            "task_id": task_id,
            "status": state,
            "step_name": step_name,
            "result": info
        }
        self.send_webhook_notification(payload)
