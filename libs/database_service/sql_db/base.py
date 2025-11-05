from abc import ABC, abstractmethod


class ChatHistoryProvider(ABC):
    """Abstract interface for sync chat history storage."""

    @abstractmethod
    def store_message(self, client_id, project_id, session_id, user_id, role, content, references=None):
        pass

    @abstractmethod
    def get_messages(self, client_id=None, project_id=None, session_id=None, user_id=None, limit=None):
        pass

    @abstractmethod
    def get_recent_messages(self, client_id, project_id, session_id, user_id=None, limit=10):
        pass

    @abstractmethod
    def delete_session_messages(self, client_id=None, project_id=None, session_id=None, user_id=None):
        pass

    @abstractmethod
    def delete_message(self, message_id):
        pass
