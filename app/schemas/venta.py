# app/schemas/venta.py
from typing import List
from pydantic import BaseModel, Field

from .cliente import ClienteSummary
from .moneda import MonedaSummary


class UsuarioSummary(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    email: str


class ProductoSummary(BaseModel):
    id_producto: int
    nombre: str
    codigo_sku: str
    codigo_barra: str


class VentaDetalleCreate(BaseModel):
    producto_id: int = Field(..., ge=1)
    cantidad: int = Field(..., ge=1)
    precio_unitario: int = Field(..., ge=0)
    descuento_item: int = Field(0, ge=0)


class VentaCreate(BaseModel):
    descuento: int = Field(0, ge=0)
    razon_social: str
    nit: str
    cliente_id: int
    moneda_id: int
    items: List[VentaDetalleCreate]


class VentaDetalleResponse(BaseModel):
    id_venta_detalle: int
    cantidad: int
    precio_unitario: int
    descuento_item: int
    producto: ProductoSummary


class VentaResponse(BaseModel):
    id_venta: int
    descuento: int
    razon_social: str
    nit: str
    total: int
    cliente: ClienteSummary
    moneda: MonedaSummary
    usuario: UsuarioSummary
    items: List[VentaDetalleResponse]


class VentaListItem(BaseModel):
    id_venta: int
    descuento: int
    razon_social: str
    nit: str
    total: int
    cliente: ClienteSummary
    moneda: MonedaSummary
    usuario: UsuarioSummary
