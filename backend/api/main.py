"""
KCo Main API - Old But Gold TR8 IVSTO
FastAPI-based REST API for Fleet Management, Anomaly Detection, and Image Processing
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import uvicorn
import logging
from datetime import datetime
import json

from backend.config.settings import settings
from backend.services.fleet_service import FleetService
from backend.services.anomaly_service import AnomalyDetectionService
from backend.services.image_processing import ImageProcessingService
from backend.services.lowdataesc_integration import LOWDATAESCService
from backend.models.fleet import Vehicle, TelemetryData, Anomaly
from backend.models.image import ImageAnalysisResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="KCo API - Fleet Intelligence Platform",
    description="Old But Gold TR8 IVSTO - Fleet Management, Anomaly Detection, Image Processing",
    version=settings.API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency Injection
class Services:
    def __init__(self):
        self.fleet = FleetService()
        self.anomaly = AnomalyDetectionService()
        self.image = ImageProcessingService()
        self.lowdataesc = LOWDATAESCService()

services = Services()


# Language Middleware
class LanguageMiddleware:
    async def __call__(self, request: Request, call_next):
        language = request.headers.get("Accept-Language", "pt")
        if language not in settings.SUPPORTED_LANGUAGES:
            language = settings.DEFAULT_LANGUAGE
        request.state.language = language
        response = await call_next(request)
        return response

app.middleware("http")(LanguageMiddleware())


# Health Check Endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT,
            "pre_seed_target": f"${settings.PRE_SEED_TARGET:,.0f}",
            "countries": list(settings.COUNTRIES.keys())
        }
    )


# ==================== FLEET MANAGEMENT ENDPOINTS ====================

@app.get("/api/fleet/vehicles")
async def get_vehicles(country: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get list of all vehicles in fleet"""
    try:
        vehicles = services.fleet.get_all_vehicles(country)
        return [v.to_dict() for v in vehicles]
    except Exception as e:
        logger.error(f"Error getting vehicles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fleet/vehicles/{vehicle_id}")
async def get_vehicle(vehicle_id: str) -> Dict[str, Any]:
    """Get specific vehicle details"""
    try:
        vehicle = services.fleet.get_vehicle(vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return vehicle.to_dict()
    except Exception as e:
        logger.error(f"Error getting vehicle {vehicle_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fleet/vehicles")
async def create_vehicle(vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
    """Register new vehicle in fleet"""
    try:
        vehicle = Vehicle.from_dict(vehicle_data)
        created = services.fleet.create_vehicle(vehicle)
        return created.to_dict()
    except Exception as e:
        logger.error(f"Error creating vehicle: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/fleet/telemetry")
async def submit_telemetry(telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
    """Submit telemetry data from vehicle"""
    try:
        telemetry = TelemetryData.from_dict(telemetry_data)
        result = services.fleet.submit_telemetry(telemetry)
        
        # Check for anomalies
        anomalies = services.anomaly.detect_anomalies(telemetry)
        if anomalies:
            for anomaly in anomalies:
                services.fleet.log_anomaly(anomaly)
            
            # Send to LOWDATAESC for cross-sector analysis
            services.lowdataesc.send_anomaly_data(anomalies)
        
        return {
            "status": "received",
            "telemetry_id": result.id,
            "anomalies_detected": len(anomalies),
            "anomalies": [a.to_dict() for a in anomalies]
        }
    except Exception as e:
        logger.error(f"Error submitting telemetry: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== ANOMALY DETECTION ENDPOINTS ====================

@app.get("/api/anomalies")
async def get_anomalies(
    vehicle_id: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get detected anomalies"""
    try:
        anomalies = services.anomaly.get_anomalies(vehicle_id, severity, limit)
        return [a.to_dict() for a in anomalies]
    except Exception as e:
        logger.error(f"Error getting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/anomalies/stats")
async def get_anomaly_stats() -> Dict[str, Any]:
    """Get anomaly statistics"""
    try:
        stats = services.anomaly.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting anomaly stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== IMAGE PROCESSING ENDPOINTS ====================

@app.post("/api/images/process")
async def process_image(image_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process vehicle image for anomaly detection"""
    try:
        # Validate image data
        if "image_url" not in image_data and "image_base64" not in image_data:
            raise HTTPException(status_code=400, detail="Image URL or base64 required")
        
        # Process image
        result = services.image.process_image(image_data)
        
        # Store in LOWDATAESC for cross-reference
        services.lowdataesc.store_image_analysis(result)
        
        return result.to_dict()
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/images/batch")
async def process_image_batch(image_urls: List[str]) -> List[Dict[str, Any]]:
    """Process multiple images in batch"""
    try:
        results = []
        for url in image_urls:
            result = services.image.process_image({"image_url": url})
            results.append(result.to_dict())
        return results
    except Exception as e:
        logger.error(f"Error processing batch images: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/images/analysis/{analysis_id}")
async def get_image_analysis(analysis_id: str) -> Dict[str, Any]:
    """Get image analysis results"""
    try:
        result = services.image.get_analysis(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return result.to_dict()
    except Exception as e:
        logger.error(f"Error getting image analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LOWDATAESC INTEGRATION ENDPOINTS ====================

@app.get("/api/lowdataesc/sync")
async def sync_with_lowdataesc() -> Dict[str, Any]:
    """Sync data with LOWDATAESC platform"""
    try:
        result = services.lowdataesc.sync_data()
        return result
    except Exception as e:
        logger.error(f"Error syncing with LOWDATAESC: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/lowdataesc/sectors")
async def get_lowdataesc_sectors() -> Dict[str, Any]:
    """Get connected sectors from LOWDATAESC"""
    try:
        sectors = services.lowdataesc.get_connected_sectors()
        return {"sectors": sectors}
    except Exception as e:
        logger.error(f"Error getting LOWDATAESC sectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== FINANCIAL PROJECTIONS ENDPOINTS ====================

@app.get("/api/financial/projections")
async def get_financial_projections() -> Dict[str, Any]:
    """Get 24-month financial projections"""
    try:
        projections = {
            "pre_seed_target": f"${settings.PRE_SEED_TARGET:,.0f} USD",
            "monthly_revenue": {
                "brazil": f"${settings.MONTHLY_REVENUE_BRAZIL:,.0f} USD",
                "mexico": f"${settings.MONTHLY_REVENUE_MEXICO:,.0f} USD",
                "total": f"${settings.MONTHLY_REVENUE_BRAZIL + settings.MONTHLY_REVENUE_MEXICO:,.0f} USD"
            },
            "roi_target": f"{settings.ROI_TARGET * 100:.0f}%",
            "fleet_targets": {
                "brazil": settings.FLEET_BRAZIL_MAX,
                "mexico": settings.FLEET_MEXICO_MAX,
                "total": settings.FLEET_BRAZIL_MAX + settings.FLEET_MEXICO_MAX
            },
            "24_month_projection": {
                "total_revenue": f"${(settings.MONTHLY_REVENUE_BRAZIL + settings.MONTHLY_REVENUE_MEXICO) * 24:,.0f} USD",
                "cumulative_fleet": settings.FLEET_BRAZIL_MAX + settings.FLEET_MEXICO_MAX,
                "estimated_valuation": f"${settings.PRE_SEED_TARGET * 10:,.0f} USD"
            }
        }
        return projections
    except Exception as e:
        logger.error(f"Error getting financial projections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/financial/unit-economics")
async def get_unit_economics(country: str = "br") -> Dict[str, Any]:
    """Get unit economics for specific country"""
    try:
        country_data = settings.COUNTRIES.get(country, settings.COUNTRIES["br"])
        
        return {
            "country": country_data["name"],
            "currency": country_data["currency"],
            "fleet_target": country_data["fleet_target"],
            "revenue_per_vehicle": f"${country_data['revenue_per_vehicle']:,.0f} USD/month",
            "monthly_revenue": f"${country_data['revenue_per_vehicle'] * country_data['fleet_target']:,.0f} USD",
            "annual_revenue": f"${country_data['revenue_per_vehicle'] * country_data['fleet_target'] * 12:,.0f} USD",
            "partners": country_data["partners"]
        }
    except Exception as e:
        logger.error(f"Error getting unit economics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STRATEGY ENDPOINTS ====================

@app.get("/api/strategy/brazil")
async def get_brazil_strategy() -> Dict[str, Any]:
    """Get Brazil market strategy"""
    try:
        return {
            "country": "Brazil",
            "strategy": {
                "market_entry": "Q1 2025",
                "fleet_target_24_months": 500,
                "revenue_model": [
                    "Subscription fees from fleet operators",
                    "Anomaly detection licensing to manufacturers",
                    "Image processing for insurance claims",
                    "Data marketplace for automotive industry"
                ],
                "key_partners": settings.COUNTRIES["br"]["partners"],
                "regulatory_compliance": [
                    "LGPD (Lei Geral de Protecao de Dados)",
                    "ANTT regulations for fleet operations",
                    "Local data sovereignty requirements"
                ],
                "competitive_advantage": [
                    "LOWDATAESC integration for cross-sector insights",
                    "AI-powered anomaly detection with 95%+ accuracy",
                    "Real-time image processing for damage assessment",
                    "Old but gold infrastructure with 99.9% uptime"
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error getting Brazil strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/strategy/mexico")
async def get_mexico_strategy() -> Dict[str, Any]:
    """Get Mexico market strategy"""
    try:
        return {
            "country": "Mexico",
            "strategy": {
                "market_entry": "Q2 2025",
                "fleet_target_24_months": 500,
                "revenue_model": [
                    "Subscription fees from dealerships",
                    "Predictive maintenance for insurance companies",
                    "Certified vehicle resale with transparency reports",
                    "Fleet management for corporate clients"
                ],
                "key_partners": settings.COUNTRIES["mx"]["partners"],
                "regulatory_compliance": [
                    "LFPDPPP (Ley Federal de Proteccion de Datos Personales)",
                    "Secretaria de Communicaciones y Transportes regulations",
                    "Local insurance industry standards"
                ],
                "competitive_advantage": [
                    "Established relationships with AXA, Banorte, Nissan",
                    "LOWDATAESC integration for automotive sector insights",
                    "Real-time telemetry with anomaly detection",
                    "Image-based damage assessment for claims"
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error getting Mexico strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/strategy/lowdataesc")
async def get_lowdataesc_strategy() -> Dict[str, Any]:
    """Get LOWDATAESC integration strategy"""
    try:
        return {
            "lowdataesc_integration": {
                "purpose": "Cross-sector data sharing and anomaly correlation",
                "benefits": [
                    "Real-time anomaly correlation across automotive and other sectors",
                    "Enhanced predictive capabilities through diverse data sources",
                    "Reduced false positives in anomaly detection",
                    "Improved fleet management through sector-wide insights",
                    "Cost reduction through shared infrastructure"
                ],
                "sectors_connected": [
                    "Automotive (Primary)",
                    "Insurance",
                    "Transportation & Logistics",
                    "Manufacturing",
                    "Energy",
                    "Smart Cities"
                ],
                "data_types_shared": [
                    "Vehicle telemetry",
                    "Anomaly patterns",
                    "Image analysis results",
                    "Maintenance records",
                    "Environmental conditions"
                ],
                "implementation": {
                    "api_integration": "RESTful API with OAuth2",
                    "data_sync_frequency": "Real-time for critical anomalies, batch for analytics",
                    "security": "End-to-end encryption, token-based authentication",
                    "compliance": "GDPR, LGPD, LFPDPPP compliant"
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting LOWDATAESC strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Run server
if __name__ == "__main__":
    logger.info(f"Starting KCo API server on {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Pre-Seed Target: ${settings.PRE_SEED_TARGET:,.0f}")
    
    uvicorn.run(
        "backend.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
