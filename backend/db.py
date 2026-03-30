import os
import mysql.connector
from mysql.connector import pooling, Error


class BackendUnavailable(Error):
    """
    Excepción controlada cuando la base de datos no está disponible.
    El frontend la interpreta como un '404' del backend.
    """


def _load_dotenv_if_present():
    """
    Carga variables desde .env (si existe) en la raíz del proyecto.
    No falla si python-dotenv no está instalado o si el archivo no existe.
    """
    try:
        from dotenv import load_dotenv
    except Exception:
        return

    # backend/db.py -> raíz del proyecto
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(project_root, ".env")
    load_dotenv(env_path, override=False)


_load_dotenv_if_present()


def get_db_config():
    """
    Lee la configuración de conexión desde variables de entorno.
    Proporciona valores por defecto razonables para desarrollo local.
    """
    return {
        "host": os.getenv("ALMACOR_DB_HOST", "localhost"),
        "port": int(os.getenv("ALMACOR_DB_PORT", "3306")),
        "user": os.getenv("ALMACOR_DB_USER", "root"),
        "password": os.getenv("ALMACOR_DB_PASSWORD", ""),
        "database": os.getenv("ALMACOR_DB_NAME", "almacor_db"),
    }


_POOL = None


def _get_pool():
    global _POOL
    if _POOL is None:
        cfg = get_db_config()
        print(f"[DB POOL] Config: host={cfg['host']}, user={cfg['user']}, db={cfg['database']}")
        try:
            _POOL = pooling.MySQLConnectionPool(
                pool_name="almacor_pool",
                pool_size=5,
                **cfg,
            )
            print("[DB POOL] Pool created successfully")
        except Error as exc:
            print(f"[DB POOL ERROR] {exc}")
            raise BackendUnavailable(str(exc)) from exc
    return _POOL


def get_connection():
    """
    Devuelve una conexión desde el pool.
    Debe cerrarse siempre después de usarse (conn.close()).
    """
    print("[DB] Getting connection...")
    try:
        conn = _get_pool().get_connection()
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
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or {})
        row = cur.fetchone()
        cur.close()
        if row:
            print(f"[DB RESULT ONE] Found row")
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
        cur = conn.cursor(dictionary=True)
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
        if conn:
            conn.rollback()
        raise
    finally:
        conn.close()


def is_available() -> bool:
    """
    Comprueba de forma rápida si la BD está disponible.
    Nunca lanza excepción (solo True/False).
    """
    try:
        print("[DB] Checking availability...")
        conn = get_connection()
        conn.close()
        print("[DB] Available")
        return True
    except BackendUnavailable:
        print("[DB] Not available")
        return False

