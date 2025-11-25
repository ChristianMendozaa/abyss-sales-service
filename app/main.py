# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import clientes, monedas, ventas

settings = get_settings()

app = FastAPI(
    title="Sale Service",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"ok": True}

# Routers
app.include_router(clientes.router)
app.include_router(monedas.router)
app.include_router(ventas.router)
