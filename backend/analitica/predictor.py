"""
Predicción de gastos mediante regresión lineal.

Referencia del repo base: agrupar gastos por mes, entrenar LinearRegression
sobre el índice cronológico y proyectar el próximo mes. Si hay menos de 2
meses se devuelve el promedio histórico como fallback (sin crashear).
"""
import numpy as np
from sklearn.linear_model import LinearRegression

UMBRAL_CONFIANZA_ALTA = 6
UMBRAL_CONFIANZA_MEDIA = 2


def _nivel_confianza(n_meses):
    if n_meses >= UMBRAL_CONFIANZA_ALTA:
        return "alta"
    if n_meses >= UMBRAL_CONFIANZA_MEDIA:
        return "media"
    return "baja"


def calcular_prediccion(series):
    """
    series: lista de dicts con {indice, anio, mes, total} ordenada por fecha.
    """
    if len(series) < 2:
        # Fallback: promedio histórico
        if series:
            promedio = round(float(np.mean([s["total"] for s in series])), 2)
            metodo = "promedio"
            mensaje = "Datos insuficientes para regresión lineal; se usó el promedio histórico."
        else:
            promedio = 0.0
            metodo = "sin_datos"
            mensaje = "No hay gastos registrados para calcular una predicción."

        return {
            "meses": _series_publicas(series),
            "prediccion": round(promedio, 2),
            "metodo": metodo,
            "nivel_confianza": _nivel_confianza(len(series)),
            "mensaje": mensaje,
        }

    x = np.array([s["indice"] for s in series]).reshape(-1, 1)
    y = np.array([s["total"] for s in series])

    modelo = LinearRegression()
    modelo.fit(x, y)

    proximo_indice = series[-1]["indice"] + 1
    prediccion = float(modelo.predict([[proximo_indice]])[0])
    prediccion = max(round(prediccion, 2), 0.0)

    ultimo = series[-1]
    prox_anio = ultimo["anio"]
    prox_mes = ultimo["mes"] + 1
    if prox_mes > 12:
        prox_mes = 1
        prox_anio += 1

    return {
        "meses": _series_publicas(series),
        "mes_objetivo": {"anio": prox_anio, "mes": prox_mes},
        "prediccion": prediccion,
        "metodo": "regresion",
        "nivel_confianza": _nivel_confianza(len(series)),
        "mensaje": "Predicción calculada por regresión lineal sobre el gasto mensual acumulado.",
    }


def _series_publicas(series):
    return [
        {"anio": s["anio"], "mes": s["mes"], "total": round(s["total"], 2)}
        for s in series
    ]
