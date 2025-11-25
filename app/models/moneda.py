# app/models/moneda.py
from sqlalchemy import Column, Integer, String
from app.database import Base


class Moneda(Base):
    __tablename__ = "moneda"

    id_moneda = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(30), nullable=False)
