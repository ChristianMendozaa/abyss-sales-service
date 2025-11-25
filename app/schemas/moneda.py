# app/schemas/moneda.py
from typing import Optional
from pydantic import BaseModel


class MonedaBase(BaseModel):
    nombre: str


class MonedaCreate(MonedaBase):
    pass


class MonedaUpdate(BaseModel):
    nombre: Optional[str] = None


class MonedaResponse(MonedaBase):
    id_moneda: int

    class Config:
        from_attributes = True


class MonedaSummary(BaseModel):
    id_moneda: int
    nombre: str

    class Config:
        from_attributes = True
