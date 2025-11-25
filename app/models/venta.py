from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func
from app.database import Base

class Venta(Base):
    __tablename__ = "venta"

    id_venta = Column(Integer, primary_key=True, index=True)
    descuento = Column(Integer, nullable=False)
    razon_social = Column(String(30), nullable=False)
    nit = Column(String(30), nullable=False)

    clientes_id_cliente = Column(Integer, nullable=False)
    moneda_id_moneda = Column(Integer, nullable=False)
    usuarios_id_usuario = Column(Integer, nullable=False)

    total = Column(Numeric, nullable=False)

    empresas_id_empresa = Column(Integer, nullable=False, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
