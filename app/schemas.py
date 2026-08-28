"""
Esquemas (Pydantic) para validación de datos de entrada y salida de la API.
"""

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field

TipoMovimiento = Literal["ingreso", "gasto"]


# --- Usuarios ---
class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    correo: EmailStr
    contrasena: str = Field(..., min_length=8, max_length=128)


class UsuarioOut(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    fecha_registro: Optional[str] = None


# --- Categorías ---
class CategoriaCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    tipo: TipoMovimiento
    id_usuario: int


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    tipo: Optional[TipoMovimiento] = None


class CategoriaOut(BaseModel):
    id_categoria: int
    nombre: str
    tipo: str
    id_usuario: int


# --- Movimientos ---
class MovimientoCreate(BaseModel):
    id_usuario: int
    id_categoria: int
    tipo: TipoMovimiento
    monto: float = Field(..., gt=0)
    fecha: date
    descripcion: Optional[str] = Field(None, max_length=255)


class MovimientoUpdate(BaseModel):
    id_categoria: Optional[int] = None
    tipo: Optional[TipoMovimiento] = None
    monto: Optional[float] = Field(None, gt=0)
    fecha: Optional[date] = None
    descripcion: Optional[str] = Field(None, max_length=255)


class MovimientoOut(BaseModel):
    id_movimiento: int
    id_usuario: int
    id_categoria: int
    categoria: Optional[str] = None
    tipo: str
    monto: float
    fecha: str
    descripcion: Optional[str] = None


# --- Resumen ---
class ResumenOut(BaseModel):
    total_ingresos: float
    total_gastos: float
    balance: float
    porcentaje_ahorro: float
