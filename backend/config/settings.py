"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

KCo Configuration Settings - Old But Gold TR8 IVSTO Infrastructure
Environment: Production/Development for Brazil & Mexico Operations
"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD


import os
from typing import Dict, Any

class Settings:
    """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Core Configuration for KCo Backend"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_VERSION: str = "v1"
    
    # Database Configuration (Old But Gold - PostgreSQL)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "kco_production")
    DB_USER: str = os.getenv("DB_USER", "kco_admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # LOWDATAESC Integration
    LOWDATAESC_API_URL: str = os.getenv("LOWDATAESC_API_URL", "https://api.lowdataesc.com")
    LOWDATAESC_API_KEY: str = os.getenv("LOWDATAESC_API_KEY", "")
    LOWDATAESC_TIMEOUT: int = 30
    
    # Redis Cache (For High-Speed Data Processing)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = 0
    
    # Fleet Configuration
    FLEET_BRAZIL_MAX: int = 500  # Target: 500 vehicles Brazil
    FLEET_MEXICO_MAX: int = 500  # Target: 500 vehicles Mexico
    FLEET_GROWTH_MONTHLY: float = 0.15  # 15% monthly growth
    
    # Image Processing Configuration
    IMAGE_PROCESSING_ENABLED: bool = True
    IMAGE_MAX_SIZE_MB: int = 10
    IMAGE_FORMATS: list = ["jpg", "jpeg", "png", "webp"]
    
    # AI/ML Configuration
    ML_MODELS_PATH: str = "/workspace/github__kauecodify__KCo by CíliaML/models"
    ML_INFERENCE_TIMEOUT: int = 60
    
    # Financial Projections (24 Months)
    PRE_SEED_TARGET: float = 30_000_000  # USD 30M+
    MONTHLY_REVENUE_BRAZIL: float = 1_500_000  # USD
    MONTHLY_REVENUE_MEXICO: float = 1_200_000  # USD
    ROI_TARGET: float = 3.5  # 350% ROI
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "kco-old-but-gold-tr8-ivsto-2024")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_EXPIRE_HOURS: int = 24
    
    # Language Support
    SUPPORTED_LANGUAGES: list = ["pt", "es"]
    DEFAULT_LANGUAGE: str = "pt"
    
    # Brazil & Mexico Specific
    COUNTRIES: Dict[str, Dict[str, Any]] = {
        "br": {
            "name": "Brazil",
            "currency": "BRL",
            "timezone": "America/Sao_Paulo",
            "fleet_target": 500,
            "revenue_per_vehicle": 3000,  # USD/month
            "partners": ["Localiza", "Movida", "WebMotors", "iFood Fleet"]
        },
        "mx": {
            "name": "Mexico", 
            "currency": "MXN",
            "timezone": "America/Mexico_City",
            "fleet_target": 500,
            "revenue_per_vehicle": 2500,  # USD/month
            "partners": ["AXA Mexico", "Banorte", "Nissan Mexico", "Volkswagen Mexico"]
        }
    }
    
    # Anomaly Detection Thresholds
    ANOMALY_THRESHOLDS: Dict[str, float] = {
        "engine_temperature": 120.0,  # Celsius
        "oil_pressure": 80.0,  # psi
        "battery_voltage": 14.5,  # volts
        "vibration_level": 0.5,  # g-force
        "fuel_efficiency": 0.7  # multiplier
    }
    
    # Telemetry Configuration
    TELEMETRY_INTERVAL_SECONDS: int = 5
    TELEMETRY_BATCH_SIZE: int = 100
    TELEMETRY_RETENTION_DAYS: int = 365


settings = Settings()
