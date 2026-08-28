"""
Módulo analítico: predicción de gastos con Regresión Lineal (Scikit-learn).

Se entrena un modelo ``LinearRegression`` a partir de la serie de gastos
agregados por mes. Si no hay datos históricos suficientes, se usa un promedio
simple para no producir predicciones sin sentido.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

MIN_MESES_CONFIANZA_ALTA = 6


def cargar_datos(conexion, id_usuario: int) -> pd.DataFrame:
    """Consulta los movimientos del usuario y los convierte en un DataFrame."""
    query = """
        SELECT fecha, tipo, monto, id_categoria
        FROM ingresos_gastos
        WHERE id_usuario = %s
    """
    df = pd.read_sql(query, conexion, params=(id_usuario,))
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])
        df["mes"] = df["fecha"].dt.to_period("M")
        df["monto"] = df["monto"].astype(float)
    return df


def predecir_gasto_proximo_mes(df: pd.DataFrame) -> dict:
    """
    Predice el gasto acumulado del próximo mes.

    Retorna: {prediccion, confianza, detalle_por_categoria, razon}
    """
    gastos = df[df["tipo"] == "gasto"]
    if gastos.empty:
        return {
            "prediccion": 0.0,
            "confianza": "baja",
            "detalle_por_categoria": {},
            "razon": "Sin registros de gastos.",
        }

    # Agregación mensual de gastos
    resumen_mensual = gastos.groupby("mes")["monto"].sum().reset_index()
    cant_meses = len(resumen_mensual)

    # Con menos de dos meses no hay tendencia: se usa el promedio simple.
    if cant_meses < 2:
        promedio = float(resumen_mensual["monto"].mean())
        return {
            "prediccion": round(promedio, 2),
            "confianza": "baja",
            "detalle_por_categoria": _detalle_por_categoria(gastos),
            "razon": "Datos insuficientes (<2 meses). Se usó promedio simple.",
        }

    # Regresión lineal sobre índice de mes (0,1,2,...)
    resumen_mensual["n_mes"] = range(cant_meses)
    X = resumen_mensual[["n_mes"]]
    y = resumen_mensual["monto"]

    modelo = LinearRegression()
    modelo.fit(X, y)

    siguiente_mes_idx = np.array([[cant_meses]])
    prediccion_raw = float(modelo.predict(siguiente_mes_idx)[0])
    prediccion = max(0.0, prediccion_raw)  # nunca negativa

    confianza = "alta" if cant_meses >= MIN_MESES_CONFIANZA_ALTA else "media"

    return {
        "prediccion": round(prediccion, 2),
        "confianza": confianza,
        "detalle_por_categoria": _detalle_por_categoria(gastos),
        "razon": f"Regresión Lineal aplicada sobre {cant_meses} meses.",
    }


def _detalle_por_categoria(gastos: pd.DataFrame) -> dict:
    """Promedio mensual de gasto por categoría (id -> monto)."""
    detalle = gastos.groupby("id_categoria")["monto"].mean()
    return {int(k): round(float(v), 2) for k, v in detalle.items()}


def detectar_anomalias(df: pd.DataFrame, umbral_z: float = 2.0) -> list:
    """
    Detecta movimientos anómalos mediante Z-score por categoría.

    Un movimiento se considera anómalo si su |Z| supera el umbral.
    """
    gastos = df[df["tipo"] == "gasto"].copy()
    if gastos.empty:
        return []

    stats = gastos.groupby("id_categoria")["monto"].agg(["mean", "std"]).reset_index()
    stats["std"] = stats["std"].fillna(0)

    gastos = gastos.merge(stats, on="id_categoria")

    gastos["z_score"] = np.where(
        gastos["std"] > 0,
        (gastos["monto"] - gastos["mean"]) / gastos["std"],
        0.0,
    )

    anomalias = gastos[gastos["z_score"].abs() > umbral_z]

    resultado = []
    for _, row in anomalias.iterrows():
        resultado.append(
            {
                "id_categoria": int(row["id_categoria"]),
                "monto": float(row["monto"]),
                "promedio_categoria": float(row["mean"]),
                "z_score": round(float(row["z_score"]), 2),
            }
        )
    return resultado
