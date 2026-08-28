"""
Detección de anomalías de gasto mediante Z-Score.

Calcula la media y la desviación estándar de los gastos por categoría y
retorna aquellas cuyo valor absoluto de Z es mayor al umbral (por defecto 2).

Aplica Z-Score a cada movimiento individual respecto al promedio de su propia
categoría, lo que permite identificar gastos inusualmente altos.
"""
import numpy as np

from ..config import Config
from ..conexion import ejecutar_consulta


def detectar_anomalias(usuario_id, umbral=None):
    """
    Devuelve una lista de gastos anómalos (|Z| > umbral) por categoría.

    Parameters
    ----------
    usuario_id : int
        Id del usuario cuyos gastos se analizan.
    umbral : float | None
        Umbral Z-Score. Si es None, se usa Config.Z_THRESHOLD (por defecto 2).

    Returns
    -------
    dict
        {
          "umbral": float,
          "anomalias": [ { ... movimiento ... , "z_score": float, "categoria": str } ],
          "total_anomalias": int
        }
    """
    if umbral is None:
        umbral = Config.Z_THRESHOLD

    filas = ejecutar_consulta(
        """
        SELECT m.id, m.categoria_id, c.nombre AS categoria,
               m.monto, m.fecha, m.descripcion
        FROM ingresos_gastos m
        LEFT JOIN categorias c ON c.id = m.categoria_id
        WHERE m.tipo = 'gasto' AND m.usuario_id = %s AND m.monto > 0
        """,
        (usuario_id,),
        fetch=True,
    )

    if not filas:
        return {"umbral": umbral, "anomalias": [], "total_anomalias": 0}

    # Agrupar montos por categoría para calcular media y desviación estándar
    montos_por_categoria = {}
    for fila in filas:
        clave = fila["categoria_id"]
        montos_por_categoria.setdefault(clave, []).append(float(fila["monto"]))

    estadisticas = {}
    for clave, montos in montos_por_categoria.items():
        media = float(np.mean(montos))
        desv = float(np.std(montos))
        estadisticas[clave] = {"media": media, "desviacion": desv}

    anomalias = []
    for fila in filas:
        clave = fila["categoria_id"]
        est = estadisticas.get(clave, {"media": 0.0, "desviacion": 0.0})
        monto = float(fila["monto"])

        # Si la desviación es 0 (un solo dato o valores idénticos), Z es 0
        if est["desviacion"] == 0:
            z_score = 0.0
        else:
            z_score = (monto - est["media"]) / est["desviacion"]

        if abs(z_score) > umbral:
            anomalias.append({
                "id": fila["id"],
                "categoria_id": fila["categoria_id"],
                "categoria": fila["categoria"],
                "monto": round(monto, 2),
                "fecha": fila["fecha"],
                "descripcion": fila["descripcion"],
                "media_categoria": round(est["media"], 2),
                "z_score": round(z_score, 3),
            })

    anomalias.sort(key=lambda a: abs(a["z_score"]), reverse=True)
    return {
        "umbral": umbral,
        "anomalias": anomalias,
        "total_anomalias": len(anomalias),
    }
