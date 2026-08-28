"""
Predicción de gastos mediante regresión lineal.

Agrupa los gastos por mes, entrena un modelo `LinearRegression` de
scikit-learn y predice el gasto del próximo mes.

Si hay menos de 2 meses de registros no se puede entrenar un modelo
significativo, por lo que se devuelve el promedio histórico como fallback
sin lanzar excepción.
"""
import numpy as np
from sklearn.linear_model import LinearRegression

from ..conexion import ejecutar_consulta


def _gasto_por_mes(usuario_id):
    """
    Devuelve una lista de (indice, anio, mes, total_gasto) ordenada por fecha.

    Cada mes con gastos queda representado por una fila.
    """
    filas = ejecutar_consulta(
        """
        SELECT YEAR(fecha) AS anio, MONTH(fecha) AS mes,
               SUM(monto) AS total
        FROM ingresos_gastos
        WHERE tipo = 'gasto' AND usuario_id = %s AND fecha IS NOT NULL
        GROUP BY YEAR(fecha), MONTH(fecha)
        ORDER BY anio, mes
        """,
        (usuario_id,),
        fetch=True,
    )
    if not filas:
        return []

    series = []
    for i, fila in enumerate(filas):
        series.append({
            "indice": i,
            "anio": fila["anio"],
            "mes": fila["mes"],
            "total": float(fila["total"] or 0),
        })
    return series


def predecir_proximo_mes(usuario_id):
    """
    Calcula la predicción de gasto del próximo mes.

    Returns
    -------
    dict
        {
          "meses": [ {anio, mes, total}, ... ],
          "prediccion": float,
          "metodo": "regresion" | "promedio" | "sin_datos",
          "mensaje": str
        }
    """
    series = _gasto_por_mes(usuario_id)

    if len(series) < 2:
        # Fallback: promedio histórico (si hay al menos 1 mes con datos)
        if series:
            promedio = float(np.mean([s["total"] for s in series]))
            resultado = round(promedio, 2)
            metodo = "promedio"
            mensaje = (
                "Datos insuficientes para regresión lineal; "
                "se usó el promedio histórico."
            )
        else:
            resultado = 0.0
            metodo = "sin_datos"
            mensaje = "No hay gastos registrados para calcular una predicción."

        return {
            "meses": series,
            "prediccion": round(resultado, 2),
            "metodo": metodo,
            "mensaje": mensaje,
        }

    # Entrenar regresión lineal sobre el índice cronológico de los meses
    x = np.array([s["indice"] for s in series]).reshape(-1, 1)
    y = np.array([s["total"] for s in series])

    modelo = LinearRegression()
    modelo.fit(x, y)

    proximo_indice = series[-1]["indice"] + 1
    prediccion = float(modelo.predict([[proximo_indice]])[0])
    prediccion = max(round(prediccion, 2), 0.0)  # el gasto no puede ser negativo

    # Mes siguiente en el calendario
    ultimo = series[-1]
    prox_anio = ultimo["anio"]
    prox_mes = ultimo["mes"] + 1
    if prox_mes > 12:
        prox_mes = 1
        prox_anio += 1

    mesa_objetivo = {"anio": prox_anio, "mes": prox_mes}

    return {
        "meses": series,
        "mes_objetivo": mesa_objetivo,
        "prediccion": prediccion,
        "metodo": "regresion",
        "mensaje": (
            "Predicción calculada por regresión lineal sobre el "
            "gasto mensual acumulado."
        ),
    }
