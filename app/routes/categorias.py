"""
Rutas de categorías: CRUD (RF02).
"""

from fastapi import APIRouter, HTTPException

from ..database import get_connection
from ..schemas import CategoriaCreate, CategoriaOut, CategoriaUpdate

router = APIRouter(prefix="/api/categorias", tags=["Categorías"])


@router.post("", response_model=CategoriaOut, status_code=201)
def crear_categoria(c: CategoriaCreate):
    """Crea una nueva categoría para un usuario."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categorias (nombre, tipo, id_usuario) VALUES (%s, %s, %s)",
            (c.nombre, c.tipo, c.id_usuario),
        )
        conn.commit()
        return {
            "id_categoria": cursor.lastrowid,
            "nombre": c.nombre,
            "tipo": c.tipo,
            "id_usuario": c.id_usuario,
        }
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        cursor.close()
        conn.close()


@router.get("", response_model=list[CategoriaOut])
def listar_categorias(id_usuario: int):
    """Lista las categorías de un usuario."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_categoria, nombre, tipo, id_usuario "
            "FROM categorias WHERE id_usuario = %s ORDER BY nombre",
            (id_usuario,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@router.put("/{id_categoria}", response_model=dict)
def actualizar_categoria(id_categoria: int, c: CategoriaUpdate):
    """Edita el nombre y/o tipo de una categoría."""
    campos, params = [], []
    if c.nombre is not None:
        campos.append("nombre = %s")
        params.append(c.nombre)
    if c.tipo is not None:
        campos.append("tipo = %s")
        params.append(c.tipo)

    if not campos:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    params.append(id_categoria)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE categorias SET {', '.join(campos)} WHERE id_categoria = %s",
            tuple(params),
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return {"mensaje": "Categoría actualizada"}
    finally:
        cursor.close()
        conn.close()


@router.delete("/{id_categoria}", response_model=dict)
def eliminar_categoria(id_categoria: int):
    """Elimina una categoría (falla si tiene movimientos asociados)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM categorias WHERE id_categoria = %s", (id_categoria,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return {"mensaje": "Categoría eliminada"}
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar la categoría (¿tiene movimientos asociados?): "
            + str(exc),
        )
    finally:
        cursor.close()
        conn.close()
