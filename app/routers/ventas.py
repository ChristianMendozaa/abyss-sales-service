# app/routers/ventas.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.database import get_db
from app.deps import require_permission, CurrentUser
from app.models.venta import Venta
from app.models.venta_detalle import VentaDetalle
from app.models.cliente import Cliente
from app.schemas.venta import (
    VentaCreate,
    VentaResponse,
    VentaListItem,
    VentaDetalleCreate,
    ClienteSummary,
    MonedaSummary,
    UsuarioSummary,
    ProductoSummary,
    VentaDetalleResponse,
)

router = APIRouter(prefix="/ventas", tags=["ventas"])


async def _build_venta_response(
    venta_id: int,
    current_user: CurrentUser,
    db: AsyncSession,
) -> VentaResponse:
    # Cabecera
    sql_header = text(
        """
        SELECT 
            v.id_venta,
            v.descuento,
            v.razon_social,
            v.nit,
            v.total,
            c.id_cliente,
            c.nombre AS cliente_nombre,
            m.id_moneda,
            m.nombre AS moneda_nombre,
            u.id_usuario,
            u.nombre AS usuario_nombre,
            u.apellido AS usuario_apellido,
            u.email AS usuario_email
        FROM venta v
        JOIN clientes c ON c.id_cliente = v.clientes_id_cliente
        JOIN moneda m ON m.id_moneda = v.moneda_id_moneda
        JOIN usuarios u ON u.id_usuario = v.usuarios_id_usuario
        WHERE v.id_venta = :venta_id
          AND c.empresas_id_empresa = :empresa_id
        LIMIT 1
        """
    )

    res_header = await db.execute(
        sql_header,
        {"venta_id": venta_id, "empresa_id": current_user.empresa.id_empresa},
    )
    header = res_header.mappings().first()
    if not header:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    # Detalles
    sql_items = text(
        """
        SELECT
            d.id_venta_detalle,
            d.cantidad,
            d.precio_unitario,
            d.descuento_item,
            p.id_producto,
            p.nombre AS producto_nombre,
            p.codigo_sku,
            p.codigo_barra
        FROM venta_detalle d
        JOIN productos p ON p.id_producto = d.productos_id_producto
        WHERE d.venta_id_venta = :venta_id
        ORDER BY d.id_venta_detalle
        """
    )

    res_items = await db.execute(sql_items, {"venta_id": venta_id})
    rows_items = res_items.mappings().all()

    items: List[VentaDetalleResponse] = []
    for r in rows_items:
        producto = ProductoSummary(
            id_producto=r["id_producto"],
            nombre=r["producto_nombre"],
            codigo_sku=r["codigo_sku"],
            codigo_barra=r["codigo_barra"],
        )
        items.append(
            VentaDetalleResponse(
                id_venta_detalle=r["id_venta_detalle"],
                cantidad=r["cantidad"],
                precio_unitario=r["precio_unitario"],
                descuento_item=r["descuento_item"],
                producto=producto,
            )
        )

    cliente = ClienteSummary(
        id_cliente=header["id_cliente"],
        nombre=header["cliente_nombre"],
    )
    moneda = MonedaSummary(
        id_moneda=header["id_moneda"],
        nombre=header["moneda_nombre"],
    )
    usuario = UsuarioSummary(
        id_usuario=header["id_usuario"],
        nombre=header["usuario_nombre"],
        apellido=header["usuario_apellido"],
        email=header["usuario_email"],
    )

    return VentaResponse(
        id_venta=header["id_venta"],
        descuento=header["descuento"],
        razon_social=header["razon_social"],
        nit=header["nit"],
        total=header["total"],
        cliente=cliente,
        moneda=moneda,
        usuario=usuario,
        items=items,
    )


@router.get("", response_model=List[VentaListItem])
async def list_ventas(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(require_permission("read", "ventas")),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista ventas de la empresa del usuario actual, incluyendo
    cliente, moneda y vendedor.
    """

    sql = text(
        """
        SELECT 
            v.id_venta,
            v.descuento,
            v.razon_social,
            v.nit,
            v.total,
            c.id_cliente,
            c.nombre AS cliente_nombre,
            m.id_moneda,
            m.nombre AS moneda_nombre,
            u.id_usuario,
            u.nombre AS usuario_nombre,
            u.apellido AS usuario_apellido,
            u.email AS usuario_email
        FROM venta v
        JOIN clientes c ON c.id_cliente = v.clientes_id_cliente
        JOIN moneda m ON m.id_moneda = v.moneda_id_moneda
        JOIN usuarios u ON u.id_usuario = v.usuarios_id_usuario
        WHERE c.empresas_id_empresa = :empresa_id
        ORDER BY v.id_venta DESC
        LIMIT :limit OFFSET :offset
        """
    )

    res = await db.execute(
        sql,
        {
            "empresa_id": current_user.empresa.id_empresa,
            "limit": limit,
            "offset": offset,
        },
    )

    rows = res.mappings().all()
    ventas: List[VentaListItem] = []

    for r in rows:
        cliente = ClienteSummary(
            id_cliente=r["id_cliente"],
            nombre=r["cliente_nombre"],
        )
        moneda = MonedaSummary(
            id_moneda=r["id_moneda"],
            nombre=r["moneda_nombre"],
        )
        usuario = UsuarioSummary(
            id_usuario=r["id_usuario"],
            nombre=r["usuario_nombre"],
            apellido=r["usuario_apellido"],
            email=r["usuario_email"],
        )
        ventas.append(
            VentaListItem(
                id_venta=r["id_venta"],
                descuento=r["descuento"],
                razon_social=r["razon_social"],
                nit=r["nit"],
                total=r["total"],
                cliente=cliente,
                moneda=moneda,
                usuario=usuario,
            )
        )

    return ventas


@router.get("/{venta_id}", response_model=VentaResponse)
async def get_venta(
    venta_id: int,
    current_user: CurrentUser = Depends(require_permission("read", "ventas")),
    db: AsyncSession = Depends(get_db),
):
    return await _build_venta_response(venta_id, current_user, db)


@router.post("", response_model=VentaResponse, status_code=status.HTTP_201_CREATED)
async def create_venta(
    payload: VentaCreate,
    current_user: CurrentUser = Depends(require_permission("create", "ventas")),
    db: AsyncSession = Depends(get_db),
):
    """
    Crea una venta con sus items. Calcula el total a partir de los detalles.

    - descuento: descuento global de la venta
    - items: lista de productos, cantidad, precio_unitario, descuento_item
    """

    if not payload.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sale must contain at least one item",
        )

    # 1) Validar cliente pertenece a la empresa
    q_cliente = select(Cliente).where(
        Cliente.id_cliente == payload.cliente_id,
        Cliente.empresas_id_empresa == current_user.empresa.id_empresa,
    )
    res_cliente = await db.execute(q_cliente)
    cliente = res_cliente.scalar_one_or_none()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client does not belong to your company or does not exist",
        )

    # 2) Validar moneda existe
    # (tabla global, sin empresa)
    moneda_sql = text("SELECT id_moneda FROM moneda WHERE id_moneda = :id LIMIT 1")
    res_moneda = await db.execute(moneda_sql, {"id": payload.moneda_id})
    if not res_moneda.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currency does not exist",
        )

    # 3) Validar productos pertenecen a la empresa
    product_ids = {item.producto_id for item in payload.items}
    prod_sql = text(
        """
        SELECT id_producto
        FROM productos
        WHERE id_producto = ANY(:ids)
          AND empresas_id_empresa = :empresa_id
        """
    )
    res_prod = await db.execute(
        prod_sql,
        {
            "ids": list(product_ids),
            "empresa_id": current_user.empresa.id_empresa,
        },
    )
    found_ids = {row[0] for row in res_prod.fetchall()}
    missing = product_ids - found_ids
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Some products do not belong to your company or do not exist: {sorted(missing)}",
        )

    # 4) Calcular total (int)
    total_items = 0
    for item in payload.items:
        line = (item.precio_unitario - item.descuento_item) * item.cantidad
        total_items += line
    total = total_items - payload.descuento
    if total < 0:
        total = 0

    # 5) Crear venta
    venta = Venta(
        descuento=payload.descuento,
        razon_social=payload.razon_social,
        nit=payload.nit,
        clientes_id_cliente=payload.cliente_id,
        moneda_id_moneda=payload.moneda_id,
        total=total,
        usuarios_id_usuario=current_user.usuario.id_usuario,
    )
    db.add(venta)
    await db.flush()  # para tener id_venta

    # 6) Crear detalles
    for item in payload.items:
        detalle = VentaDetalle(
            venta_id_venta=venta.id_venta,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            descuento_item=item.descuento_item,
            productos_id_producto=item.producto_id,
        )
        db.add(detalle)

    await db.flush()

    # 7) Devolver venta completa
    return await _build_venta_response(venta.id_venta, current_user, db)
