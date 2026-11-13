from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend import config
from backend.database import get_db

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "MEX | Intelligent Vision AI",
        "database": "ok" if db_ok else "error",
        "region": "MX",
        "targets": {
            "inference_p95_ms": config.INFERENCE_P95_TARGET_MS,
            "full_flow_p95_ms": config.FULL_FLOW_P95_TARGET_MS,
        },
    }


@router.get("/metrics/prometheus")
def prometheus():
    from backend.services import metrics as m

    return m.prometheus_format()
