import bcrypt
from . import db


def crear_usuario(data):
    password_hash = bcrypt.hashpw(
        data["password"].encode("utf-8"), bcrypt.gensalt()
    )
    sql = """
        INSERT INTO usuarios
            (nombre, usuario, password_hash, rol_id, estado)
        VALUES
            (%(nombre)s, %(usuario)s, %(password_hash)s, %(rol_id)s, %(estado)s)
    """
    return db.execute(
        sql,
        {
            "nombre": data["nombre"],
            "usuario": data["usuario"],
            "password_hash": password_hash,
            "rol_id": data["rol_id"],
            "estado": data["estado"],
        },
    )


def actualizar_usuario(user_id, data):
    fields = ["nombre = %(nombre)s", "usuario = %(usuario)s", "rol_id = %(rol_id)s", "estado = %(estado)s"]
    params = {
        "id": user_id,
        "nombre": data["nombre"],
        "usuario": data["usuario"],
        "rol_id": data["rol_id"],
        "estado": data["estado"],
    }
    if data.get("password"):
        fields.append("password_hash = %(password_hash)s")
        params["password_hash"] = bcrypt.hashpw(
            data["password"].encode("utf-8"), bcrypt.gensalt()
        )

    sql = "UPDATE usuarios SET " + ", ".join(fields) + " WHERE id = %(id)s"
    db.execute(sql, params)


def eliminar_usuario(user_id):
    sql = "DELETE FROM usuarios WHERE id = %(id)s"
    db.execute(sql, {"id": user_id})


def listar_usuarios():
    sql = """
        SELECT
            u.id,
            u.nombre,
            u.usuario,
            u.estado,
            r.nombre AS rol
        FROM usuarios u
        JOIN roles r ON r.id = u.rol_id
        ORDER BY u.nombre
    """
    return db.query_all(sql)


def obtener_rol_id_por_nombre(nombre_rol: str):
    sql = "SELECT id FROM roles WHERE UPPER(nombre) = UPPER(%(nombre)s)"
    row = db.query_one(sql, {"nombre": nombre_rol})
    return row["id"] if row else None

