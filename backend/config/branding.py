"""
Branding Configuration - KCo Fleet Intelligence
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
KCo by Cília | Laboratory of K and RockNewVenture

Centralized branding and company information.
"""

from typing import Dict, Any


class BrandingConfig:
    """
    Branding Configuration Manager
    
    Centralizes all branding information for KCo platform.
    """
    
    # Company Information
    COMPANY_NAME = "KCo by Cília"
    COMPANY_FULL_NAME = "KCo Fleet Intelligence Platform"
    COMPANY_TAGLINE = "Old But Gold TR8 IVSTO"
    COMPANY_LABORATORY = "Laboratory of K and RockNewVenture"
    
    # Contact Information
    COMPANY_EMAIL = "contato@kco.ai"
    COMPANY_WEBSITE = "https://kco.ai"
    COMPANY_GITHUB = "https://github.com/kauecodify/KCo"
    
    # Financial Targets
    PRE_SEED_TARGET = "$30M+ USD"
    VALUATION_TARGET = "$150M+ USD"
    ROI_TARGET = "350%"
    
    # Market Information
    TARGET_MARKETS = ["Brazil", "Mexico"]
    TARGET_COUNTRIES = {
        "br": {
            "name": "Brazil",
            "currency": "BRL",
            "fleet_target": 500,
            "revenue_target": "$15M-20M USD"
        },
        "mx": {
            "name": "Mexico",
            "currency": "MXN",
            "fleet_target": 500,
            "revenue_target": "$12M-18M USD"
        }
    }
    
    # Technology Stack
    TECHNOLOGY_STACK = {
        "backend": "FastAPI (Python)",
        "database": "PostgreSQL (Old But Gold)",
        "cache": "Redis",
        "ml": "PyTorch/TensorFlow",
        "image_processing": "OpenCV",
        "container": "Docker",
        "orchestration": "Docker Compose"
    }
    
    # LOWDATAESC Integration
    LOWDATAESC_PARTNER = "LOWDATAESC"
    LOWDATAESC_PURPOSE = "Cross-sector data sharing and anomaly correlation"
    LOWDATAESC_SECTORS = [
        "Automotive",
        "Insurance", 
        "Transportation & Logistics",
        "Manufacturing",
        "Energy",
        "Smart Cities"
    ]
    
    # AI/ML Capabilities
    AI_MODELS = [
        "YOLOv8 (Object Detection)",
        "Custom CNN (Anomaly Detection)",
        "Ensemble Models (Damage Assessment)",
        "Time Series (Telemetry Analysis)"
    ]
    
    AI_ACCURACY = {
        "anomaly_detection": "95%+",
        "object_detection": "95.5%",
        "damage_assessment": "93.8%",
        "telemetry_analysis": "97.2%"
    }
    
    # Product Information
    PRODUCT_NAME = "KCo Fleet Intelligence Platform"
    PRODUCT_VERSION = "v1.0"
    PRODUCT_DESCRIPTION = (
        "AI-Powered Fleet Intelligence Platform with LOWDATAESC integration "
        "for cross-sector anomaly detection and vehicle analysis"
    )
    
    # Footer Information
    FOOTER_TEXT = "© 2024-2026 KCo by Cília | Laboratory of K and RockNewVenture | All Rights Reserved"
    
    # API Information
    API_NAME = "KCo API"
    API_VERSION = "v1"
    API_DESCRIPTION = (
        "RESTful API for Fleet Management, Anomaly Detection, and Image Processing. "
        "Old But Gold TR8 IVSTO Infrastructure."
    )
    
    # Documentation
    DOCS_URL = "/api/docs"
    REDOC_URL = "/api/redoc"
    
    def get_company_info(self) -> Dict[str, Any]:
        """Get complete company information"""
        return {
            "name": self.COMPANY_NAME,
            "full_name": self.COMPANY_FULL_NAME,
            "tagline": self.COMPANY_TAGLINE,
            "laboratory": self.COMPANY_LABORATORY,
            "email": self.COMPANY_EMAIL,
            "website": self.COMPANY_WEBSITE,
            "github": self.COMPANY_GITHUB,
            "pre_seed_target": self.PRE_SEED_TARGET,
            "valuation_target": self.VALUATION_TARGET,
            "roi_target": self.ROI_TARGET
        }
    
    def get_market_info(self, country: str = None) -> Dict[str, Any]:
        """Get market information for specific country or all"""
        if country:
            return self.TARGET_COUNTRIES.get(country, {})
        return {"countries": self.TARGET_COUNTRIES, "all": self.TARGET_MARKETS}
    
    def get_technology_info(self) -> Dict[str, Any]:
        """Get technology stack information"""
        return {
            "stack": self.TECHNOLOGY_STACK,
            "ai_models": self.AI_MODELS,
            "ai_accuracy": self.AI_ACCURACY
        }
    
    def get_lowdataesc_info(self) -> Dict[str, Any]:
        """Get LOWDATAESC integration information"""
        return {
            "partner": self.LOWDATAESC_PARTNER,
            "purpose": self.LOWDATAESC_PURPOSE,
            "sectors": self.LOWDATAESC_SECTORS
        }
    
    def get_product_info(self) -> Dict[str, Any]:
        """Get product information"""
        return {
            "name": self.PRODUCT_NAME,
            "version": self.PRODUCT_VERSION,
            "description": self.PRODUCT_DESCRIPTION
        }
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information"""
        return {
            "name": self.API_NAME,
            "version": self.API_VERSION,
            "description": self.API_DESCRIPTION,
            "docs_url": self.DOCS_URL,
            "redoc_url": self.REDOC_URL
        }


# Singleton instance
branding_config = BrandingConfig()


def get_branding_config() -> BrandingConfig:
    """Get branding configuration instance"""
    return branding_config
