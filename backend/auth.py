from . import db


def _verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Compare plain text passwords directly (INSECURE - per user request)
    """
    return plain_password == password_hash


def login_user(username: str, password: str):
    """
    Valida credenciales contra la tabla usuarios.

    Devuelve dict con:
        {id, nombre, usuario, rol, es_admin}
    o None si las credenciales no son válidas.
    """
    sql = """
        SELECT u.id, u.nombre, u.usuario, u.password_hash, r.nombre AS rol
        FROM usuarios u
        JOIN roles r ON r.id = u.rol_id
        WHERE u.usuario = %(usuario)s AND u.estado = 'ACTIVO'
    """
    row = db.query_one(sql, {"usuario": username})
    if not row:
        return None

    password_hash = row.get("password_hash")  # Already str from VARCHAR

    if not _verify_password(password, password_hash):
        return None

    rol = row["rol"]
    es_admin = rol.upper() == "ADMIN"
    return {
        "id": row["id"],
        "nombre": row["nombre"],
        "usuario": row["usuario"],
        "rol": rol,
        "es_admin": es_admin,
    }
