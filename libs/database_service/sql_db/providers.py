import os
import hashlib
from datetime import datetime
from typing import Any
import json
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

    def _generate_message_id(self, client_id, project_id, session_id, user_id, role, content, created_at):
        raw = f"{client_id}:{project_id}:{session_id}:{user_id}:{role}:{content}:{created_at}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def store_message(self, client_id, project_id, session_id, user_id, role, content, references=None):
        created_at = datetime.utcnow().isoformat()
        message_id = self._generate_message_id(client_id, project_id, session_id, user_id, role, content, created_at)

        # Serialize references if provided (stored as TEXT JSON)
        references_value = None
        if references is not None:
            if isinstance(references, (dict, list)):
                references_value = json.dumps(references, ensure_ascii=False)
            else:
                references_value = str(references)

        query = """
            INSERT INTO chathistory (message_id, client_id, project_id, session_id, user_id, role, content, "references", created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (message_id) DO NOTHING;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (message_id, client_id, project_id, session_id, user_id, role, content, references_value, created_at))
            conn.commit()
        return message_id

  
    def get_messages(self, client_id=None, project_id=None, session_id=None, user_id=None, limit=None):
        query = (
            """
            SELECT message_id, client_id, project_id, session_id, user_id, role, content, "references", created_at
            FROM chathistory
            """
        )
        conditions = []
        params = []

        if client_id is not None:
            conditions.append("client_id = %s")
            params.append(client_id)
        if project_id is not None:
            conditions.append("project_id = %s")
            params.append(project_id)
        if session_id is not None:
            conditions.append("session_id = %s")
            params.append(session_id)
        if user_id is not None:
            conditions.append("user_id = %s")
            params.append(user_id)

        if conditions:
            query += "\nWHERE " + " AND ".join(conditions)

        query += "\nORDER BY created_at DESC"

        if limit is not None:
            query += "\nLIMIT %s"
            params.append(limit)

        query += ";"

        with self._get_connection() as conn, conn.cursor() as cur:
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
        return rows

    def get_recent_messages(self, client_id, project_id, session_id, user_id=None, limit=10):
        rows = self.get_messages(
            client_id=client_id,
            project_id=project_id,
            session_id=session_id,
            user_id=user_id,
            limit=limit,
        )
        return rows[::-1]



    def delete_session_messages(self, client_id=None, project_id=None, session_id=None, user_id=None):
        query = "DELETE FROM chathistory"
        conditions = []
        params = []

        if client_id is not None:
            conditions.append("client_id = %s")
            params.append(client_id)
        if project_id is not None:
            conditions.append("project_id = %s")
            params.append(project_id)
        if session_id is not None:
            conditions.append("session_id = %s")
            params.append(session_id)
        if user_id is not None:
            conditions.append("user_id = %s")
            params.append(user_id)

        if not conditions:
            raise ValueError("At least one filter parameter must be provided to delete messages.")

        query += "\nWHERE " + " AND ".join(conditions) + ";"

        with self._get_connection() as conn, conn.cursor() as cur:
            cur.execute(query, tuple(params))
            conn.commit()
        return True

    def delete_message(self, message_id):
        query = "DELETE FROM chathistory WHERE message_id = %s;"
        with self._get_connection() as conn, conn.cursor() as cur:
            cur.execute(query, (message_id,))
            conn.commit()
        return True
