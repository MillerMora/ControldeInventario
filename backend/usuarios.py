from . import db


def crear_usuario(data):
    # Plain text password (INSECURE - per user request)
    password_hash = data["password"]
    sql = """
        INSERT INTO usuarios
            (nombre, usuario, email, password_hash, rol_id, estado)
        VALUES
            (%(nombre)s, %(usuario)s, %(email)s, %(password_hash)s, %(rol_id)s, %(estado)s)
    """
    return db.execute(
        sql,
        {
            "nombre": data["nombre"],
            "usuario": data["usuario"],
            "email": data.get("email", ""),
            "password_hash": password_hash,
            "rol_id": data["rol_id"],
            "estado": data["estado"],
        },
    )


def actualizar_usuario(user_id, data):
    fields = ["nombre = %(nombre)s", "usuario = %(usuario)s", "email = %(email)s", "rol_id = %(rol_id)s", "estado = %(estado)s"]
    params = {
        "id": user_id,
        "nombre": data["nombre"],
        "usuario": data["usuario"],
        "email": data.get("email", ""),
        "rol_id": data["rol_id"],
        "estado": data["estado"],
    }
    if data.get("password"):
        fields.append("password_hash = %(password_hash)s")
        params["password_hash"] = data["password"]  # Plain text (INSECURE)

    sql = "UPDATE usuarios SET " + ", ".join(fields) + " WHERE id = %(id)s"
    db.execute(sql, params)


def get_delete_info(user_id):
    """
    Verifica dependencias antes de eliminar usuario.
    Retorna info para mostrar en UI de confirmación.
    """
    sql_ventas = """
        SELECT COUNT(*) as ventas 
        FROM ventas 
        WHERE vendedor_id = %(id)s
    """
    sql_envios = """
        SELECT COUNT(*) as envios 
        FROM envios 
        WHERE vendedor_id = %(id)s
    """
    result_ventas = db.query_one(sql_ventas, {"id": user_id})
    result_envios = db.query_one(sql_envios, {"id": user_id})
    
    ventas = result_ventas["ventas"] if result_ventas else 0
    envios = result_envios["envios"] if result_envios else 0
    total = ventas + envios
    
    info = {
        "dependencias": total,
        "ventas": ventas,
        "envios": envios,
        "puede_eliminar": total == 0,
        "mensaje": f"Este usuario tiene {{ventas}} venta(s) y {{envios}} envío(s) asociados.".format(ventas=ventas, envios=envios)
    }
    return info


def eliminar_usuario(user_id):
    sql = "DELETE FROM usuarios WHERE id = %(id)s"
    db.execute(sql, {"id": user_id})


def listar_usuarios():
    sql = """
        SELECT
            u.id,
            u.nombre,
            u.usuario,
            u.email,
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
