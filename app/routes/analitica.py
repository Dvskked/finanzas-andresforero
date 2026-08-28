"""
Rutas del módulo analítico: predicción y anomalías (RF08, RF09, RF10).
"""

from fastapi import APIRouter, HTTPException

from ..database import get_connection
from ..services.analitica import (
    cargar_datos,
    detectar_anomalias,
    predecir_gasto_proximo_mes,
)

router = APIRouter(prefix="/api/analitica", tags=["Analítica"])


@router.get("/prediccion")
def api_prediccion(id_usuario: int):
    """Predice el gasto del próximo mes usando regresión lineal (RF08)."""
    conn = get_connection()
    try:
        df = cargar_datos(conn, id_usuario)
        resultado = predecir_gasto_proximo_mes(df)
        return {"id_usuario": id_usuario, **resultado}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.get("/anomalias")
def api_anomalias(id_usuario: int, umbral: float = 2.0):
    """Lista movimientos anómalos mediante Z-score (RF09)."""
    conn = get_connection()
    try:
        df = cargar_datos(conn, id_usuario)
        anomalias = detectar_anomalias(df, umbral_z=umbral)
        return {"id_usuario": id_usuario, "anomalias": anomalias}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()
