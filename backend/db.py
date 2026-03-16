import os
import mysql.connector
from mysql.connector import pooling, Error


class BackendUnavailable(Error):
    """
    Excepción controlada cuando la base de datos no está disponible.
    El frontend la interpreta como un '404' del backend.
    """


def get_db_config():
    """
    Lee la configuración de conexión desde variables de entorno.
    Proporciona valores por defecto razonables para desarrollo local.
    """
    return {
        "host": os.getenv("ALMACOR_DB_HOST", "localhost"),
        "port": int(os.getenv("ALMACOR_DB_PORT", "3306")),
        "user": os.getenv("ALMACOR_DB_USER", "almacor_user"),
        "password": os.getenv("ALMACOR_DB_PASSWORD", "almacor_pass"),
        "database": os.getenv("ALMACOR_DB_NAME", "almacor_db"),
    }


_POOL = None


def _get_pool():
    global _POOL
    if _POOL is None:
        cfg = get_db_config()
        try:
            _POOL = pooling.MySQLConnectionPool(
                pool_name="almacor_pool",
                pool_size=5,
                **cfg,
            )
        except Error as exc:
            # Cualquier problema de conexión se traduce en un BackendUnavailable
            raise BackendUnavailable(str(exc)) from exc
    return _POOL


def get_connection():
    """
    Devuelve una conexión desde el pool.
    Debe cerrarse siempre después de usarse (conn.close()).
    """
    try:
        return _get_pool().get_connection()
    except Error as exc:
        raise BackendUnavailable(str(exc)) from exc


def query_one(sql, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or {})
        row = cur.fetchone()
        cur.close()
        return row
    finally:
        conn.close()


def query_all(sql, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or {})
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()


def execute(sql, params=None):
    """
    Ejecuta INSERT/UPDATE/DELETE y devuelve el último id insertado (si aplica).
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or {})
        last_id = cur.lastrowid
        conn.commit()
        cur.close()
        return last_id
    finally:
        conn.close()


def is_available() -> bool:
    """
    Comprueba de forma rápida si la BD está disponible.
    Nunca lanza excepción (solo True/False).
    """
    try:
        conn = get_connection()
        conn.close()
        return True
    except BackendUnavailable:
        return False
