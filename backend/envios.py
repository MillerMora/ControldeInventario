from datetime import datetime
from . import db


def listar_envios():
    sql = """
        SELECT
            e.id,
            e.guia,
            e.fecha,
            e.producto_descripcion,
            e.ciudad_destino,
            e.estado,
            u.nombre AS vendedor
        FROM envios e
        JOIN usuarios u ON u.id = e.vendedor_id
        ORDER BY e.fecha DESC, e.id DESC
        LIMIT 100
    """
    return db.query_all(sql)


def registrar_envio(data):
    """
    data:
        {
            "guia": str,
            "producto_descripcion": str,
            "cliente": str,
            "ciudad_destino": str,
            "direccion": str,
            "vendedor_id": int,
        }
    """
    sql = """
        INSERT INTO envios
            (guia, fecha, producto_descripcion, cliente,
             ciudad_destino, direccion, estado, vendedor_id)
        VALUES
            (%(guia)s, %(fecha)s, %(producto)s, %(cliente)s,
             %(ciudad)s, %(direccion)s, 'EN_TRANSITO', %(vendedor_id)s)
    """
    return db.execute(
        sql,
        {
            "guia": data["guia"],
            "fecha": datetime.now(),
            "producto": data["producto_descripcion"],
            "cliente": data["cliente"],
            "ciudad": data["ciudad_destino"],
            "direccion": data["direccion"],
            "vendedor_id": data["vendedor_id"],
        },
    )

