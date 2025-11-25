# app/routers/monedas.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import require_permission, CurrentUser
from app.models.moneda import Moneda
from app.schemas.moneda import (
    MonedaCreate,
    MonedaUpdate,
    MonedaResponse,
)

router = APIRouter(prefix="/monedas", tags=["monedas"])


@router.get("", response_model=List[MonedaResponse])
async def list_monedas(
    current_user: CurrentUser = Depends(require_permission("read", "monedas")),
    db: AsyncSession = Depends(get_db),
):
    q = select(Moneda).order_by(Moneda.id_moneda)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [MonedaResponse.model_validate(r) for r in rows]


@router.get("/{moneda_id}", response_model=MonedaResponse)
async def get_moneda(
    moneda_id: int,
    current_user: CurrentUser = Depends(require_permission("read", "monedas")),
    db: AsyncSession = Depends(get_db),
):
    q = select(Moneda).where(Moneda.id_moneda == moneda_id)
    result = await db.execute(q)
    moneda = result.scalar_one_or_none()
    if not moneda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currency not found",
        )
    return MonedaResponse.model_validate(moneda)


@router.post("", response_model=MonedaResponse, status_code=status.HTTP_201_CREATED)
async def create_moneda(
    payload: MonedaCreate,
    current_user: CurrentUser = Depends(require_permission("create", "monedas")),
    db: AsyncSession = Depends(get_db),
):
    moneda = Moneda(nombre=payload.nombre)
    db.add(moneda)
    await db.flush()
    await db.refresh(moneda)
    return MonedaResponse.model_validate(moneda)


@router.patch("/{moneda_id}", response_model=MonedaResponse)
async def update_moneda(
    moneda_id: int,
    payload: MonedaUpdate,
    current_user: CurrentUser = Depends(require_permission("update", "monedas")),
    db: AsyncSession = Depends(get_db),
):
    q = select(Moneda).where(Moneda.id_moneda == moneda_id)
    result = await db.execute(q)
    moneda = result.scalar_one_or_none()
    if not moneda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currency not found",
        )

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(moneda, field, value)

    await db.flush()
    await db.refresh(moneda)
    return MonedaResponse.model_validate(moneda)


@router.delete("/{moneda_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_moneda(
    moneda_id: int,
    current_user: CurrentUser = Depends(require_permission("delete", "monedas")),
    db: AsyncSession = Depends(get_db),
):
    q = select(Moneda).where(Moneda.id_moneda == moneda_id)
    result = await db.execute(q)
    moneda = result.scalar_one_or_none()
    if not moneda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currency not found",
        )

    await db.delete(moneda)
    return None
