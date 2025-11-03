from abc import ABC, abstractmethod


class ChatHistoryProvider(ABC):
    """Abstract interface for sync chat history storage."""

    @abstractmethod
    def store_message(self, client_id, project_id, session_id, role, content):
        pass

    @abstractmethod
    def get_messages(self, client_id, project_id, session_id):
        pass

    @abstractmethod
    def get_recent_messages(self, client_id, project_id, session_id, limit=10):
        pass

    @abstractmethod
    def search_messages(self, client_id, project_id, session_id, keyword):
        pass

    @abstractmethod
    def delete_session_messages(self, client_id, project_id, session_id):
        pass

    @abstractmethod
    def delete_message(self, message_id):
        pass
