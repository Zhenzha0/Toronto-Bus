"""Database helpers: open a connection and run .sql files."""

import psycopg2

import config


def connect():
    """Open a new connection to the Postgres database using our DATABASE_URL."""
    return psycopg2.connect(config.DATABASE_URL)


def run_sql_file(path):
    """Run every statement in a .sql file as ONE transaction.

    Either all statements succeed and are committed together, or if any
    statement fails, the whole thing is rolled back (nothing is applied).
    """
    sql = path.read_text(encoding="utf-8")

    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)      # send the SQL to Postgres
        conn.commit()             # make the changes permanent
    except Exception:
        conn.rollback()           # undo everything if any statement failed
        raise                     # re-raise so the caller sees the error
    finally:
        conn.close()              # always release the connection

    print(f"  ran {path.name}")
