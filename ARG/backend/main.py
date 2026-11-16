"""
KCo/ARG Backend - Aplicacao principal FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
import logging
from typing import Optional

# Configuracao de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Criar aplicacao FastAPI
app = FastAPI(
    title="KCo/ARG API",
    description="API RESTful para a operacao KCo Argentina - Plataforma de Inteligencia de Frota",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {"name": "auth", "description": "Autenticacao"},
        {"name": "users", "description": "Gerenciamento de usuarios"},
        {"name": "fleets", "description": "Gerenciamento de frotas"},
        {"name": "vehicles", "description": "Gerenciamento de veiculos"},
        {"name": "telemetry", "description": "Dados de telemetria"},
        {"name": "images", "description": "Processamento de imagens"},
        {"name": "anomalies", "description": "Detecao de anomalias"},
        {"name": "transactions", "description": "Gerenciamento de transacoes"},
        {"name": "reports", "description": "Relatorios"},
        {"name": "admin", "description": "Administracao"},
        {"name": "health", "description": "Health check"},
    ]
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configurar para ambientes de producao
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Health check endpoint
@app.get("/api/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "KCo/ARG API",
        "environment": "development"  # TODO: Configurar por ambiente
    }


# Root endpoint
@app.get("/", tags=["health"])
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Bem-vindo a KCo/ARG API",
        "documentation": "/api/docs",
        "health": "/api/health"
    }


# Incluir roteadores
# TODO: Adicionar os roteadores conforme forem sendo criados
# from backend.routers import auth, users, fleets, vehicles, telemetry, images, anomalies
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(users.router, prefix="/api/users", tags=["users"])
# app.include_router(fleets.router, prefix="/api/fleets", tags=["fleets"])
# app.include_router(vehicles.router, prefix="/api/vehicles", tags=["vehicles"])
# app.include_router(telemetry.router, prefix="/api/telemetry", tags=["telemetry"])
# app.include_router(images.router, prefix="/api/images", tags=["images"])
# app.include_router(anomalies.router, prefix="/api/anomalies", tags=["anomalies"])


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
