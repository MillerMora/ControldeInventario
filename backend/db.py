import os
import pymysql
import pymysql.cursors
from pymysql import Error


class BackendUnavailable(Exception):
    """
    Excepción controlada cuando la base de datos no está disponible.
    El frontend la interpreta como un '404' del backend.
    """


def _load_dotenv_if_present():
    try:
        from dotenv import load_dotenv
    except Exception:
        return
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(project_root, ".env")
    load_dotenv(env_path, override=False)


_load_dotenv_if_present()


def get_db_config():
    return {
        "host": os.getenv("ALMACOR_DB_HOST", "localhost"),
        "port": int(os.getenv("ALMACOR_DB_PORT", "3306")),
        "user": os.getenv("ALMACOR_DB_USER", "root"),
        "password": os.getenv("ALMACOR_DB_PASSWORD", ""),
        "database": os.getenv("ALMACOR_DB_NAME", "almacor_db"),
    }


def get_connection():
    """
    Devuelve una conexión nueva con PyMySQL.
    Debe cerrarse siempre después de usarse (conn.close()).
    """
    print("[DB] Getting connection...")
    cfg = get_db_config()
    print(f"[DB POOL] Config: host={cfg['host']}, user={cfg['user']}, db={cfg['database']}")
    try:
        conn = pymysql.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
        print("[DB] Connection obtained")
        return conn
    except Error as exc:
        print(f"[DB ERROR connect] {exc}")
        raise BackendUnavailable(str(exc)) from exc


def query_one(sql, params=None):
    print(f"[DB QUERY ONE] SQL: {sql}")
    if params:
        print(f"[DB PARAMS] {params}")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or {})
        row = cur.fetchone()
        cur.close()
        if row:
            print("[DB RESULT ONE] Found row")
        else:
            print("[DB RESULT ONE] No row found")
        return row
    except Error as exc:
        print(f"[DB ERROR query_one] {exc}")
        raise
    finally:
        conn.close()


def query_all(sql, params=None):
    print(f"[DB QUERY ALL] SQL: {sql}")
    if params:
        print(f"[DB PARAMS] {params}")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or {})
        rows = cur.fetchall()
        cur.close()
        print(f"[DB RESULT ALL] Found {len(rows)} rows")
        return rows
    except Error as exc:
        print(f"[DB ERROR query_all] {exc}")
        raise
    finally:
        conn.close()


def execute(sql, params=None):
    """
    Ejecuta INSERT/UPDATE/DELETE y devuelve el último id insertado (si aplica).
    """
    print(f"[DB EXECUTE] SQL: {sql}")
    if params:
        print(f"[DB PARAMS] {params}")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or {})
        last_id = cur.lastrowid
        conn.commit()
        cur.close()
        print(f"[DB EXECUTE] Success, affected rows=1, last_id={last_id}")
        return last_id
    except Error as exc:
        print(f"[DB ERROR execute] {exc}")
        conn.rollback()
        raise
    finally:
        conn.close()


def is_available() -> bool:
    try:
        print("[DB] Checking availability...")
        conn = get_connection()
        conn.close()
        print("[DB] Available")
        return True
    except BackendUnavailable:
        print("[DB] Not available")
        return False