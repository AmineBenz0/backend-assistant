import os
import psycopg


db_host = os.environ.get("POSTGRES_HOST", "localhost")
db_port = os.environ.get("OUSIDE_POSTGRES_PORT", "8432")
db_name = os.environ.get("POSTGRES_DB", "postgres")
db_user = os.environ.get("POSTGRES_USER", "postgres")
db_password = os.environ.get("POSTGRES_PASSWORD", "postgres")


from psycopg import Error

def create_chathistory_table():
    conn = None
    cursor = None
    try:
        conn = psycopg.connect(
            host=db_host,   # or "postgres" if inside Docker Compose
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()

        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS chathistory (
            message_id  CHAR(64) PRIMARY KEY,   -- SHA-256 hex string
            client_id   VARCHAR(255) NOT NULL,
            project_id  VARCHAR(255) NOT NULL,
            session_id  VARCHAR(255) NOT NULL,
            user_id     VARCHAR(255) NOT NULL,           
            role        VARCHAR(50)  NOT NULL,
            content     TEXT         NOT NULL,
            "references" TEXT,
            created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        );
        """
        cursor.execute(create_table_sql)

        cursor.execute("SELECT current_database(), current_schema();")
        print("Connected to:", cursor.fetchone())

        conn.commit()
        print("✅ Table 'public.chathistory' created successfully.")

    except Error as e:
        print(f"❌ Error while creating table: {e}")

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    create_chathistory_table()
