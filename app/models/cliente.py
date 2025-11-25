# app/models/cliente.py
from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(30), nullable=False)
    tipo = Column(String(30), nullable=False)
    telefono = Column(String(30), nullable=False)
    email = Column(String(30), nullable=False)
    notas = Column(String(30), nullable=False)
    # 👇 Importante: SIN ForeignKey aquí
    empresas_id_empresa = Column(Integer, nullable=False, index=True)