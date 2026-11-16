"""
KCo/ARG Backend - Configuracoes
"""

import os
from typing import Optional
from pydantic import BaseSettings, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Configuracoes da aplicacao"""
    
    # Ambiente
    ENVIRONMENT: str = os.getenv("ARG_ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("ARG_DEBUG", True)
    
    # Aplicacao
    APP_NAME: str = "KCo/ARG API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API RESTful para a operacao KCo Argentina"
    
    # Seguranca
    SECRET_KEY: str = os.getenv("ARG_SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720  # 12 horas
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Banco de Dados
    POSTGRES_HOST: str = os.getenv("ARG_POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = os.getenv("ARG_POSTGRES_PORT", 5432)
    POSTGRES_USER: str = os.getenv("ARG_POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("ARG_POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("ARG_POSTGRES_DB", "kco_arg")
    DATABASE_URL: Optional[PostgresDsn] = None
    
    # Redis
    REDIS_HOST: str = os.getenv("ARG_REDIS_HOST", "localhost")
    REDIS_PORT: int = os.getenv("ARG_REDIS_PORT", 6379)
    REDIS_PASSWORD: Optional[str] = os.getenv("ARG_REDIS_PASSWORD")
    REDIS_URL: Optional[RedisDsn] = None
    
    # Armazenamento
    STORAGE_TYPE: str = os.getenv("ARG_STORAGE_TYPE", "local")  # local, s3, minio
    STORAGE_PATH: str = os.getenv("ARG_STORAGE_PATH", "./data/storage")
    S3_ENDPOINT: Optional[str] = os.getenv("ARG_S3_ENDPOINT")
    S3_ACCESS_KEY: Optional[str] = os.getenv("ARG_S3_ACCESS_KEY")
    S3_SECRET_KEY: Optional[str] = os.getenv("ARG_S3_SECRET_KEY")
    S3_BUCKET: Optional[str] = os.getenv("ARG_S3_BUCKET")
    
    # Integracao com Veraz
    VERAZ_ENABLED: bool = os.getenv("ARG_VERAZ_ENABLED", False)
    VERAZ_API_KEY: Optional[str] = os.getenv("ARG_VERAZ_API_KEY")
    VERAZ_API_SECRET: Optional[str] = os.getenv("ARG_VERAZ_API_SECRET")
    VERAZ_ENDPOINT: str = os.getenv("ARG_VERAZ_ENDPOINT", "https://api.veraz.com.ar")
    
    # Integracao com Mercado Pago
    MERCADO_PAGO_ENABLED: bool = os.getenv("ARG_MERCADO_PAGO_ENABLED", False)
    MERCADO_PAGO_ACCESS_TOKEN: Optional[str] = os.getenv("ARG_MERCADO_PAGO_ACCESS_TOKEN")
    MERCADO_PAGO_PUBLIC_KEY: Optional[str] = os.getenv("ARG_MERCADO_PAGO_PUBLIC_KEY")
    MERCADO_PAGO_ENDPOINT: str = os.getenv("ARG_MERCADO_PAGO_ENDPOINT", "https://api.mercadopago.com")
    
    # CORS
    CORS_ORIGINS: list[str] = os.getenv("ARG_CORS_ORIGINS", "*").split(",")
    
    # Logging
    LOG_LEVEL: str = os.getenv("ARG_LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("ARG_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Rate Limiting
    RATE_LIMIT: int = os.getenv("ARG_RATE_LIMIT", 100)  # requests por minuto
    
    # Upload
    MAX_UPLOAD_SIZE: int = os.getenv("ARG_MAX_UPLOAD_SIZE", 8 * 1024 * 1024)  # 8MB
    ALLOWED_EXTENSIONS: list[str] = [".jpg", ".jpeg", ".png", ".pdf", ".json"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Configurar DATABASE_URL
        self.DATABASE_URL = PostgresDsn.build(
            scheme="postgresql",
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=f"/{self.POSTGRES_DB}"
        )
        
        # Configurar REDIS_URL
        if self.REDIS_PASSWORD:
            self.REDIS_URL = RedisDsn.build(
                scheme="redis",
                user="",
                password=self.REDIS_PASSWORD,
                host=self.REDIS_HOST,
                port=self.REDIS_PORT
            )
        else:
            self.REDIS_URL = RedisDsn.build(
                scheme="redis",
                user="",
                password="",
                host=self.REDIS_HOST,
                port=self.REDIS_PORT
            )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instancia das configuracoes
settings = Settings()
