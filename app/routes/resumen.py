"""
Rutas de resumen financiero: totales y tendencia mensual (RF05).
"""

from fastapi import APIRouter, HTTPException

from ..database import get_connection

router = APIRouter(prefix="/api/resumen", tags=["Resumen"])


@router.get("")
def obtener_resumen(id_usuario: int):
    """Calcula totales de ingresos, gastos, balance y porcentaje de ahorro (RF05)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END) AS total_ingresos,
                SUM(CASE WHEN tipo = 'gasto' THEN monto ELSE 0 END)   AS total_gastos
            FROM ingresos_gastos
            WHERE id_usuario = %s
            """,
            (id_usuario,),
        )
        data = cursor.fetchone()

        # Tendencia mensual para el gráfico de líneas (RF07).
        cursor.execute(
            """
            SELECT DATE_FORMAT(fecha, '%%Y-%%m') AS mes,
                   SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END) AS ingresos,
                   SUM(CASE WHEN tipo = 'gasto' THEN monto ELSE 0 END)   AS gastos
            FROM ingresos_gastos
            WHERE id_usuario = %s
            GROUP BY DATE_FORMAT(fecha, '%%Y-%%m')
            ORDER BY mes
            """,
            (id_usuario,),
        )
        tendencia = cursor.fetchall()

        # Distribución de gastos por categoría para el gráfico de dona (RF06).
        cursor.execute(
            """
            SELECT c.nombre AS categoria, SUM(m.monto) AS total
            FROM ingresos_gastos m
            JOIN categorias c ON c.id_categoria = m.id_categoria
            WHERE m.id_usuario = %s AND m.tipo = 'gasto'
            GROUP BY c.nombre
            ORDER BY total DESC
            """,
            (id_usuario,),
        )
        por_categoria = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    ingresos = float(data["total_ingresos"] or 0)
    gastos = float(data["total_gastos"] or 0)
    balance = ingresos - gastos

    return {
        "total_ingresos": ingresos,
        "total_gastos": gastos,
        "balance": balance,
        "porcentaje_ahorro": round((balance / ingresos * 100), 2) if ingresos > 0 else 0,
        "tendencia": tendencia,
        "gastos_por_categoria": por_categoria,
    }
