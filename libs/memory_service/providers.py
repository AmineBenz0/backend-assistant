import os
import httpx
from typing import Dict, Any, Optional, List
from .base import BaseMemoryProvider
from app.configs.mem0_config import mem0_config


class Mem0Provider(BaseMemoryProvider):
    """
    Sync Mem0 REST API implementation.
    """

    def __init__(self, base_url: str = os.environ['MEM0_URL']):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        response = self.client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}

    def configure(self, config: Dict[str, Any] = mem0_config) -> Dict[str, Any]:
        return self._request("POST", "/configure", json=config)

    def create_memory(self, messages: List[Dict[str, str]], user_id=None, agent_id=None, run_id=None, metadata=None):
        payload = {"messages": messages, "user_id": user_id, "agent_id": agent_id, "run_id": run_id, "metadata": metadata}
        return self._request("POST", "/memories", json=payload)

    def get_memories(self, user_id=None, agent_id=None, run_id=None):
        params = {"user_id": user_id, "agent_id": agent_id, "run_id": run_id}
        return self._request("GET", "/memories", params=params)

    def delete_memories(self, user_id=None, agent_id=None, run_id=None):
        params = {"user_id": user_id, "agent_id": agent_id, "run_id": run_id}
        return self._request("DELETE", "/memories", params=params)

    def get_memory(self, memory_id: str):
        return self._request("GET", f"/memories/{memory_id}")

    def update_memory(self, memory_id: str, updated_memory: Dict[str, Any]):
        return self._request("PUT", f"/memories/{memory_id}", json=updated_memory)

    def delete_memory(self, memory_id: str):
        return self._request("DELETE", f"/memories/{memory_id}")

    def search_memories(self, query: str, user_id=None, agent_id=None, run_id=None, filters=None):
        payload = {"query": query, "user_id": user_id, "agent_id": agent_id, "run_id": run_id, "filters": filters}
        return self._request("POST", "/search", json=payload)

    def get_memory_history(self, memory_id: str):
        return self._request("GET", f"/memories/{memory_id}/history")

    def reset(self):
        return self._request("POST", "/reset")

    def close(self):
        self.client.close()
