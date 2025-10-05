import os
import time
import sys
import psycopg2
from psycopg2 import OperationalError


host = os.getenv("POSTGRES_HOST", "db")
port = int(os.getenv("POSTGRES_PORT", "5432"))
db = os.getenv("POSTGRES_DB", "usr-db")
user = os.getenv("POSTGRES_USER", "usr-user")
pwd = os.getenv("POSTGRES_PASSWORD", "password")


for i in range(60):
    try:
        conn = psycopg2.connect(
            host=host, port=port, dbname=db, user=user, password=pwd
        )
        conn.close()
        print("DB is ready.")
        sys.exit(0)
    except OperationalError as e:
        print(f"Waiting for DB... ({i+1}) {e}")
        time.sleep(1)

print("DB not ready in time.")
sys.exit(1)
