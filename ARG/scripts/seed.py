#!/usr/bin/env python3
"""
KCo/ARG - Seed de Dados Iniciais
"""

import asyncio
import logging
from backend.database import engine, Base, init_db
from backend.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def seed_database():
    """
    Seed inicial do banco de dados
    """
    logger.info("Iniciando seed do banco de dados...")
    
    try:
        # Inicializar banco de dados (criar tabelas)
        await init_db()
        logger.info("Tabelas criadas com sucesso")
        
        # TODO: Adicionar seed de dados reais
        # Exemplo: criar usuario admin, empresas, frotas, etc.
        
        logger.info("Seed concluido com sucesso")
        
    except Exception as e:
        logger.error(f"Erro durante o seed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_database())
