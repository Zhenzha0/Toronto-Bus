"""Database helpers: open a connection and run .sql files."""

import psycopg2

import config


def connect():
    """Open a new connection to the Postgres database using our DATABASE_URL."""
    return psycopg2.connect(config.DATABASE_URL)


def run_sql_file(path):
    """Run a whole .sql file in one transaction: everything commits together,
    or rolls back together if any statement fails."""
    sql = path.read_text(encoding="utf-8")

    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()             # success -> save the changes
    except Exception:
        conn.rollback()           # failure -> undo the whole file
        raise
    finally:
        conn.close()

    print(f"  ran {path.name}")
