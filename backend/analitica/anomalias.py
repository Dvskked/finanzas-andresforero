"""
Detección de anomalías de gasto por Z-Score (umbral = 2).
"""
import numpy as np

UMBRAL_Z = 2.0


def detectar_anomalias(gastos, umbral=None):
    """
    gastos: lista de dicts con {id, categoria_id, categoria, monto, fecha, descripcion}.

    Calcula media y desviación estándar por categoría y retorna los movimientos
    cuyo |Z| > umbral. Controla la división por cero cuando la desviación es 0.
    """
    umbral = umbral or UMBRAL_Z

    if not gastos:
        return {"umbral": umbral, "anomalias": [], "total_anomalias": 0}

    montos_por_categoria = {}
    for g in gastos:
        montos_por_categoria.setdefault(g["categoria_id"], []).append(float(g["monto"]))

    estadisticas = {}
    for clave, montos in montos_por_categoria.items():
        media = float(np.mean(montos))
        desv = float(np.std(montos))
        estadisticas[clave] = {"media": media, "desviacion": desv}

    anomalias = []
    for g in gastos:
        clave = g["categoria_id"]
        est = estadisticas.get(clave, {"media": 0.0, "desviacion": 0.0})
        monto = float(g["monto"])

        if est["desviacion"] == 0:
            z = 0.0
        else:
            z = (monto - est["media"]) / est["desviacion"]

        if abs(z) > umbral:
            anomalias.append(
                {
                    "id": g["id"],
                    "categoria_id": g["categoria_id"],
                    "categoria": g["categoria"],
                    "monto": round(monto, 2),
                    "fecha": g["fecha"],
                    "descripcion": g["descripcion"],
                    "media_categoria": round(est["media"], 2),
                    "z_score": round(z, 3),
                }
            )

    anomalias.sort(key=lambda a: abs(a["z_score"]), reverse=True)
    return {"umbral": umbral, "anomalias": anomalias, "total_anomalias": len(anomalias)}
