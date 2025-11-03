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
        """Send webhook notification to configured endpoints."""
        if not settings.webhooks:
            logger.info("No webhooks configured, skipping notification")
            return payload
            
        for webhook in settings.webhooks:
            if not webhook.get("url"):
                continue
                
            url = webhook["url"] + str(payload["task_id"])
            basic = HTTPBasicAuth(webhook.get("username", ""), webhook.get("password", ""))

            headers = {"Content-Type": "application/json"}
            try:
                response = requests.request(
                    "POST", url, headers=headers, data=json.dumps(payload), auth=basic, timeout=30
                )
                logger.info(f"Webhook notification sent to {url}, status: {response.status_code}")
            except Exception as e:
                logger.error(f"Failed to send webhook notification to {url}: {e}")
        return payload

    def on_success(self, retval, task_id, args, kwargs):
        """Handle successful task completion."""
        webhook_response = retval.get('webhook_response')
        if webhook_response: 
            payload = {
                "workflow_id": retval.get('workflow_id'),
                "task_id": task_id,
                "status": "SUCCESS",
                "action": retval.get('action'),
                "result": retval['response'],
                "version": retval.get('version', 'new_version')
            }
            if is_json_serializable(payload):
                return self.send_webhook_notification(payload)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        workflow_id = args[0] if len(args) > 0 else "unknown"
        step_input = args[2] if len(args) > 2 else {}
        action = step_input.get('action')
        webhook_response = True if step_input.get("section_id") else False
        
        if webhook_response:
            payload = {
                "workflow_id": workflow_id,
                "task_id": task_id,
                "status": "FAILURE",
                "action": action,
                "result": str(exc)
            }
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