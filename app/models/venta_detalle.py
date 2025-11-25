from sqlalchemy import Column, Integer, ForeignKey, Numeric
from app.database import Base

class VentaDetalle(Base):
    __tablename__ = "venta_detalle"

    id_venta_detalle = Column(Integer, primary_key=True, index=True)
    venta_id_venta = Column(Integer, ForeignKey("venta.id_venta"), nullable=False)
    productos_id_producto = Column(Integer, nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric, nullable=False)
    descuento_item = Column(Integer, nullable=False)
