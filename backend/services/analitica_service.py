"""
Servicio de analítica: delega en los módulos predictor y anomalías.
"""
from ..repositories.movimiento_repository import movimiento_repositorio
from ..analitica.predictor import calcular_prediccion
from ..analitica.anomalias import detectar_anomalias


class AnaliticaServicio:
    """Cálculos analíticos sobre los gastos del usuario."""

    def prediccion(self, usuario_id):
        series = movimiento_repositorio.gasto_por_mes(usuario_id)
        return calcular_prediccion(series)

    def anomalias(self, usuario_id):
        gastos = movimiento_repositorio.gastos_por_usuario(usuario_id)
        return detectar_anomalias(gastos)


analitica_servicio = AnaliticaServicio()
