from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseMemoryProvider(ABC):
    """
    Abstract base class for sync memory providers.
    """

    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def create_memory(
        self,
        messages: List[Dict[str, str]],
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_memories(self, user_id: Optional[str] = None,
                     agent_id: Optional[str] = None,
                     run_id: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def delete_memories(self, user_id: Optional[str] = None,
                        agent_id: Optional[str] = None,
                        run_id: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_memory(self, memory_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_memory(self, memory_id: str, updated_memory: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def search_memories(self, query: str,
                        user_id: Optional[str] = None,
                        agent_id: Optional[str] = None,
                        run_id: Optional[str] = None,
                        filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_memory_history(self, memory_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def reset(self) -> Dict[str, Any]:
        pass
