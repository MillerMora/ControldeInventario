from . import db


def listar_productos():
    sql = """
        SELECT
            p.id,
            p.referencia,
            p.nombre,
            p.talla,
            p.color,
            p.stock_actual,
            p.ubicacion,
            p.precio,
            p.stock_minimo,
            CASE
                WHEN p.stock_actual <= 0 THEN 'Inactivo'
                WHEN p.stock_actual <= p.stock_minimo * 0.4 THEN 'Crítico'
                WHEN p.stock_actual <= p.stock_minimo THEN 'Stock bajo'
                ELSE 'Disponible'
            END AS estado
        FROM productos p
        ORDER BY p.nombre
    """
    return db.query_all(sql)


def productos_con_bajo_stock():
    sql = """
        SELECT
            p.id,
            p.nombre,
            p.talla,
            p.stock_actual,
            p.stock_minimo
        FROM productos p
        WHERE p.stock_actual <= p.stock_minimo
        ORDER BY p.stock_actual ASC
    """
    return db.query_all(sql)


def crear_producto(data):
    sql = """
        INSERT INTO productos
            (referencia, nombre, talla, color, stock_actual,
             ubicacion, precio, stock_minimo)
        VALUES
            (%(referencia)s, %(nombre)s, %(talla)s, %(color)s,
             %(stock)s, %(ubicacion)s, %(precio)s, %(stock_minimo)s)
    """
    return db.execute(sql, data)


def actualizar_producto(producto_id, data):
    sql = """
        UPDATE productos
        SET
            nombre = %(nombre)s,
            talla = %(talla)s,
            color = %(color)s,
            stock_actual = %(stock)s,
            ubicacion = %(ubicacion)s,
            precio = %(precio)s,
            stock_minimo = %(stock_minimo)s
        WHERE id = %(id)s
    """
    params = dict(data)
    params["id"] = producto_id
    db.execute(sql, params)


def get_delete_info(producto_id):
    """
    Verifica dependencias antes de eliminar producto.
    Retorna info para mostrar en UI de confirmación.
    """
    sql_count = """
        SELECT COUNT(*) as dependencias 
        FROM ventas_detalle vd 
        WHERE vd.producto_id = %(id)s
    """
    result = db.query_one(sql_count, {"id": producto_id})
    count = result["dependencias"] if result else 0
    
    info = {
        "dependencias": count,
        "puede_eliminar": count == 0,
        "mensaje": f"Este producto está asociado a {count} venta(s)." if count > 0 else "No hay dependencias."
    }
    return info


def eliminar_producto(producto_id):
    sql = "DELETE FROM productos WHERE id = %(id)s"
    db.execute(sql, {"id": producto_id})

