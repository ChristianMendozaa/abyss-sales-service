# app/schemas/cliente.py
from typing import Optional
from pydantic import BaseModel, EmailStr


class ClienteBase(BaseModel):
    nombre: str
    tipo: str
    telefono: str
    email: EmailStr
    notas: str


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    notas: Optional[str] = None


class ClienteResponse(ClienteBase):
    id_cliente: int

    class Config:
        from_attributes = True


class ClienteSummary(BaseModel):
    id_cliente: int
    nombre: str

    class Config:
        from_attributes = True
