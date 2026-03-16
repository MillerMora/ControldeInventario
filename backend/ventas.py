from datetime import datetime
from . import db


def listar_ventas():
    sql = """
        SELECT
            v.id,
            v.codigo,
            v.fecha,
            v.total,
            v.descuento,
            v.estado,
            u.nombre AS vendedor,
            GROUP_CONCAT(CONCAT(d.cantidad, '× ', p.nombre) SEPARATOR ', ') AS detalle
        FROM ventas v
        JOIN usuarios u ON u.id = v.vendedor_id
        LEFT JOIN ventas_detalle d ON d.venta_id = v.id
        LEFT JOIN productos p ON p.id = d.producto_id
        GROUP BY v.id
        ORDER BY v.fecha DESC, v.id DESC
        LIMIT 100
    """
    return db.query_all(sql)


def registrar_venta(data):
    """
    data:
        {
            "producto_id": int,
            "talla": str,
            "cantidad": int,
            "precio_unit": float,
            "descuento": float,
            "cliente": str | None,
            "vendedor_id": int,
            "notas": str | None,
        }
    """
    conn = db.get_connection()
    try:
        cur = conn.cursor()

        total_bruto = data["cantidad"] * data["precio_unit"]
        total_neto = total_bruto - data.get("descuento", 0.0)

        # Insert venta
        cur.execute(
            """
            INSERT INTO ventas
                (codigo, fecha, total, descuento, estado, cliente, vendedor_id, notas)
            VALUES
                (%(codigo)s, %(fecha)s, %(total)s, %(descuento)s,
                 'COMPLETADA', %(cliente)s, %(vendedor_id)s, %(notas)s)
            """,
            {
                "codigo": data.get("codigo"),
                "fecha": datetime.now(),
                "total": total_neto,
                "descuento": data.get("descuento", 0.0),
                "cliente": data.get("cliente"),
                "vendedor_id": data["vendedor_id"],
                "notas": data.get("notas"),
            },
        )
        venta_id = cur.lastrowid

        # Insert detalle
        cur.execute(
            """
            INSERT INTO ventas_detalle
                (venta_id, producto_id, talla, cantidad, precio_unit)
            VALUES
                (%(venta_id)s, %(producto_id)s, %(talla)s,
                 %(cantidad)s, %(precio_unit)s)
            """,
            {
                "venta_id": venta_id,
                "producto_id": data["producto_id"],
                "talla": data["talla"],
                "cantidad": data["cantidad"],
                "precio_unit": data["precio_unit"],
            },
        )

        # Actualizar stock
        cur.execute(
            """
            UPDATE productos
            SET stock_actual = stock_actual - %(cantidad)s
            WHERE id = %(producto_id)s
            """,
            {
                "cantidad": data["cantidad"],
                "producto_id": data["producto_id"],
            },
        )

        conn.commit()
        cur.close()
        return venta_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

