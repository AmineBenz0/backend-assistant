import os
import hashlib
from datetime import datetime
import psycopg
from psycopg.rows import dict_row
from .base import ChatHistoryProvider


class PgSQLProvider(ChatHistoryProvider):
    def __init__(self):
        self.db_host = os.environ.get("POSTGRES_HOST", "host.docker.internal")
        self.db_port = os.environ.get("OUSIDE_POSTGRES_PORT", "8432")
        self.db_name = os.environ.get("POSTGRES_DB", "postgres")
        self.db_user = os.environ.get("POSTGRES_USER", "postgres")
        self.db_password = os.environ.get("POSTGRES_PASSWORD", "postgres")

    def _get_connection(self):
        return psycopg.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            row_factory=dict_row
        )

    def _generate_message_id(self, client_id, project_id, session_id, role, content, created_at):
        raw = f"{client_id}:{project_id}:{session_id}:{role}:{content}:{created_at}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def store_message(self, client_id, project_id, session_id, role, content):
        created_at = datetime.utcnow().isoformat()
        message_id = self._generate_message_id(client_id, project_id, session_id, role, content, created_at)

        query = """
            INSERT INTO chathistory (message_id, client_id, project_id, session_id, role, content, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (message_id) DO NOTHING;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (message_id, client_id, project_id, session_id, role, content, created_at))
            conn.commit()
        return message_id

    def get_messages(self, client_id, project_id, session_id):
        query = """
            SELECT message_id, client_id, project_id, session_id, role, content, created_at
            FROM chathistory
            WHERE client_id = %s AND project_id = %s AND session_id = %s
            ORDER BY created_at ASC;
        """
        with self._get_connection() as conn, conn.cursor() as cur:
            cur.execute(query, (client_id, project_id, session_id))
            rows = cur.fetchall()
        return rows

    def get_recent_messages(self, client_id, project_id, session_id, limit=10):
        query = """
            SELECT message_id, client_id, project_id, session_id, role, content, created_at
            FROM chathistory
            WHERE client_id = %s AND project_id = %s AND session_id = %s
            ORDER BY created_at DESC
            LIMIT %s;
        """
        with self._get_connection() as conn, conn.cursor() as cur:
            cur.execute(query, (client_id, project_id, session_id, limit))
            rows = cur.fetchall()
        return rows[::-1]

    def search_messages(self, client_id, project_id, session_id, keyword):
        query = """
            SELECT message_id, client_id, project_id, session_id, role, content, created_at
            FROM chathistory
            WHERE client_id = %s AND project_id = %s AND session_id = %s
              AND content ILIKE %s
            ORDER BY created_at ASC;
        """
        with self._get_connection() as conn, conn.cursor() as cur:
            cur.execute(query, (client_id, project_id, session_id, f"%{keyword}%"))
            rows = cur.fetchall()
        return rows

    def delete_session_messages(self, client_id, project_id, session_id):
        query = """
            DELETE FROM chathistory
            WHERE client_id = %s AND project_id = %s AND session_id = %s;
        """
        with self._get_connection() as conn, conn.cursor() as cur:
            cur.execute(query, (client_id, project_id, session_id))
            conn.commit()
        return True

    def delete_message(self, message_id):
        query = "DELETE FROM chathistory WHERE message_id = %s;"
        with self._get_connection() as conn, conn.cursor() as cur:
            cur.execute(query, (message_id,))
            conn.commit()
        return True
