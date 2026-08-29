"""
Repositorio de movimientos (ingresos_gastos).
"""
from ..database import get_cursor
from ..core.exceptions import ErrorControlador


class MovimientoRepositorio:
    """Operaciones SQL sobre la tabla `ingresos_gastos`."""

    def listar(self, usuario_id, tipo=None):
        condiciones = ["m.usuario_id = %s"]
        params = [usuario_id]
        if tipo in ("ingreso", "gasto"):
            condiciones.append("m.tipo = %s")
            params.append(tipo)
        where = " AND ".join(condiciones)
        sql = (
            "SELECT m.id, m.usuario_id, m.categoria_id, "
            "c.nombre AS categoria_nombre, m.tipo, m.monto, m.fecha, "
            "m.descripcion, m.creado_en "
            "FROM ingresos_gastos m "
            "LEFT JOIN categorias c ON c.id = m.categoria_id "
            f"WHERE {where} ORDER BY m.fecha DESC, m.id DESC"
        )
        with get_cursor() as cur:
            cur.execute(sql, tuple(params))
            return cur.fetchall()

    def obtener(self, movimiento_id):
        with get_cursor() as cur:
            cur.execute(
                "SELECT m.id, m.usuario_id, m.categoria_id, "
                "c.nombre AS categoria_nombre, m.tipo, m.monto, m.fecha, "
                "m.descripcion, m.creado_en "
                "FROM ingresos_gastos m "
                "LEFT JOIN categorias c ON c.id = m.categoria_id "
                "WHERE m.id = %s",
                (movimiento_id,),
            )
            return cur.fetchone()

    def crear(self, usuario_id, categoria_id, tipo, monto, fecha, descripcion):
        with get_cursor() as cur:
            cur.execute(
                "INSERT INTO ingresos_gastos "
                "(usuario_id, categoria_id, tipo, monto, fecha, descripcion) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (usuario_id, categoria_id, tipo, monto, fecha, descripcion),
            )
            return cur.lastrowid

    def actualizar(self, movimiento_id, campos):
        """Actualiza dinámicamente los campos indicados para un movimiento."""
        if not campos:
            raise ErrorControlador("No hay campos válidos para actualizar.")
        asignaciones = ", ".join(f"{col} = %s" for col in campos)
        params = list(campos.values()) + [movimiento_id]
        with get_cursor() as cur:
            cur.execute(
                f"UPDATE ingresos_gastos SET {asignaciones} WHERE id = %s",
                tuple(params),
            )
            return cur.rowcount

    def eliminar(self, movimiento_id):
        with get_cursor() as cur:
            cur.execute("DELETE FROM ingresos_gastos WHERE id = %s", (movimiento_id,))
            return cur.rowcount

    def totales(self, usuario_id):
        with get_cursor() as cur:
            cur.execute(
                "SELECT tipo, COALESCE(SUM(monto), 0) AS total "
                "FROM ingresos_gastos WHERE usuario_id = %s GROUP BY tipo",
                (usuario_id,),
            )
            filas = cur.fetchall()
        ingreso = gasto = 0.0
        for fila in filas:
            if fila["tipo"] == "ingreso":
                ingreso = float(fila["total"] or 0)
            elif fila["tipo"] == "gasto":
                gasto = float(fila["total"] or 0)
        return {"ingresos": round(ingreso, 2), "gastos": round(gasto, 2)}

    def gastos_por_usuario(self, usuario_id):
        """Gastos del usuario, usados por el módulo analítico."""
        with get_cursor() as cur:
            cur.execute(
                "SELECT m.id, m.categoria_id, c.nombre AS categoria, "
                "m.monto, m.fecha, m.descripcion "
                "FROM ingresos_gastos m "
                "LEFT JOIN categorias c ON c.id = m.categoria_id "
                "WHERE m.tipo = 'gasto' AND m.usuario_id = %s AND m.monto > 0",
                (usuario_id,),
            )
            return cur.fetchall()

    def gasto_por_mes(self, usuario_id):
        """Gasto mensual acumulado del usuario, usado por el predictor."""
        with get_cursor() as cur:
            cur.execute(
                "SELECT YEAR(fecha) AS anio, MONTH(fecha) AS mes, "
                "SUM(monto) AS total "
                "FROM ingresos_gastos "
                "WHERE tipo = 'gasto' AND usuario_id = %s AND fecha IS NOT NULL "
                "GROUP BY YEAR(fecha), MONTH(fecha) "
                "ORDER BY anio, mes",
                (usuario_id,),
            )
            filas = cur.fetchall()
        series = []
        for i, fila in enumerate(filas):
            series.append(
                {
                    "indice": i,
                    "anio": fila["anio"],
                    "mes": fila["mes"],
                    "total": float(fila["total"] or 0),
                }
            )
        return series


movimiento_repositorio = MovimientoRepositorio()
