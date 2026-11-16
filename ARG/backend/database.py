"""
KCo/ARG Backend - Configuracao do Banco de Dados
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# Criar engine do banco de dados
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# Criar sessao
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def get_db():
    """
    Dependencia para obter sessao do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """
    Inicializar banco de dados (criar tabelas)
    """
    logger.info("Inicializando banco de dados...")
    Base.metadata.create_all(bind=engine)
    logger.info("Banco de dados inicializado com sucesso")


async def close_db():
    """
    Fechar conexoes do banco de dados
    """
    logger.info("Fechando conexoes do banco de dados...")
    engine.dispose()
    logger.info("Conexoes fechadas")
