"""
Rutas de movimientos (ingresos/gastos): CRUD con filtros (RF03, RF04).
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..database import get_connection
from ..schemas import MovimientoCreate, MovimientoOut, MovimientoUpdate

router = APIRouter(prefix="/api/movimientos", tags=["Movimientos"])

_BASE_SELECT = (
    "SELECT m.id_movimiento, m.id_usuario, m.id_categoria, c.nombre AS categoria, "
    "m.tipo, m.monto, DATE_FORMAT(m.fecha, '%%Y-%%m-%%d') AS fecha, m.descripcion "
    "FROM ingresos_gastos m "
    "JOIN categorias c ON c.id_categoria = m.id_categoria "
)


@router.post("", response_model=dict, status_code=201)
def registrar_movimiento(m: MovimientoCreate):
    """Registra un nuevo ingreso o gasto."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ingresos_gastos "
            "(id_usuario, id_categoria, tipo, monto, fecha, descripcion) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (m.id_usuario, m.id_categoria, m.tipo, m.monto, m.fecha, m.descripcion),
        )
        conn.commit()
        return {
            "id_movimiento": cursor.lastrowid,
            "mensaje": "Movimiento registrado exitosamente",
        }
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        cursor.close()
        conn.close()


@router.get("", response_model=list[MovimientoOut])
def listar_movimientos(
    id_usuario: int,
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    categoria: Optional[int] = Query(None),
):
    """Lista movimientos con filtros por rango de fechas y categoría (RF04)."""
    query = _BASE_SELECT + "WHERE m.id_usuario = %s"
    params = [id_usuario]

    if desde:
        query += " AND m.fecha >= %s"
        params.append(desde)
    if hasta:
        query += " AND m.fecha <= %s"
        params.append(hasta)
    if categoria:
        query += " AND m.id_categoria = %s"
        params.append(categoria)

    query += " ORDER BY m.fecha DESC, m.id_movimiento DESC"

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@router.put("/{id_movimiento}", response_model=dict)
def actualizar_movimiento(id_movimiento: int, m: MovimientoUpdate):
    """Edita un movimiento existente."""
    campos, params = [], []
    for campo, valor in {
        "id_categoria": m.id_categoria,
        "tipo": m.tipo,
        "monto": m.monto,
        "fecha": m.fecha,
        "descripcion": m.descripcion,
    }.items():
        if valor is not None:
            campos.append(f"{campo} = %s")
            params.append(valor)

    if not campos:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    params.append(id_movimiento)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE ingresos_gastos SET {', '.join(campos)} WHERE id_movimiento = %s",
            tuple(params),
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        return {"mensaje": "Movimiento actualizado"}
    finally:
        cursor.close()
        conn.close()


@router.delete("/{id_movimiento}", response_model=dict)
def eliminar_movimiento(id_movimiento: int):
    """Elimina un movimiento por ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM ingresos_gastos WHERE id_movimiento = %s",
            (id_movimiento,),
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        return {"mensaje": "Movimiento eliminado"}
    finally:
        cursor.close()
        conn.close()
