# app/routers/clientes.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import require_permission, CurrentUser
from app.models.cliente import Cliente
from app.schemas.cliente import (
    ClienteCreate,
    ClienteUpdate,
    ClienteResponse,
)

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=List[ClienteResponse])
async def list_clientes(
    current_user: CurrentUser = Depends(require_permission("read", "clientes")),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(Cliente)
        .where(Cliente.empresas_id_empresa == current_user.empresa.id_empresa)
        .order_by(Cliente.id_cliente)
    )
    result = await db.execute(q)
    rows = result.scalars().all()
    return [ClienteResponse.model_validate(r) for r in rows]


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def get_cliente(
    cliente_id: int,
    current_user: CurrentUser = Depends(require_permission("read", "clientes")),
    db: AsyncSession = Depends(get_db),
):
    q = select(Cliente).where(
        Cliente.id_cliente == cliente_id,
        Cliente.empresas_id_empresa == current_user.empresa.id_empresa,
    )
    result = await db.execute(q)
    cliente = result.scalar_one_or_none()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return ClienteResponse.model_validate(cliente)


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def create_cliente(
    cliente_create: ClienteCreate,
    current_user: CurrentUser = Depends(require_permission("create", "clientes")),
    db: AsyncSession = Depends(get_db),
):
    cliente = Cliente(
        nombre=cliente_create.nombre,
        tipo=cliente_create.tipo,
        telefono=cliente_create.telefono,
        email=cliente_create.email,
        notas=cliente_create.notas,
        empresas_id_empresa=current_user.empresa.id_empresa,
    )
    db.add(cliente)
    await db.flush()
    await db.refresh(cliente)
    return ClienteResponse.model_validate(cliente)

@router.patch("/{cliente_id}", response_model=ClienteResponse)
async def update_cliente(
    cliente_id: int,
    payload: ClienteUpdate,
    current_user: CurrentUser = Depends(require_permission("update", "clientes")),
    db: AsyncSession = Depends(get_db),
):
    q = select(Cliente).where(
        Cliente.id_cliente == cliente_id,
        Cliente.empresas_id_empresa == current_user.empresa.id_empresa,
    )
    result = await db.execute(q)
    cliente = result.scalar_one_or_none()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(cliente, field, value)

    await db.flush()
    await db.refresh(cliente)
    return ClienteResponse.model_validate(cliente)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cliente(
    cliente_id: int,
    current_user: CurrentUser = Depends(require_permission("delete", "clientes")),
    db: AsyncSession = Depends(get_db),
):
    q = select(Cliente).where(
        Cliente.id_cliente == cliente_id,
        Cliente.empresas_id_empresa == current_user.empresa.id_empresa,
    )
    result = await db.execute(q)
    cliente = result.scalar_one_or_none()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    await db.delete(cliente)
    return None
