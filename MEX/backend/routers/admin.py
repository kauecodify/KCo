from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import config
from backend.database import get_db
from backend.models import AIModelVersion, AuditLog, Inspection, Part, User
from backend.schemas import ModelVersionOut, UserCreate, UserOut
from backend.security import hash_password, require_role
from backend.services import metrics
from backend.services.audit import log_action
from backend.services.vision_engine import reference_store

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/metrics")
def platform_metrics(user=Depends(require_role("supervisor")), db: Session = Depends(get_db)):
    total = db.query(func.count(Inspection.id)).scalar() or 0
    approved = db.query(func.count(Inspection.id)).filter(Inspection.status == "GREEN").scalar() or 0
    review_pending = (
        db.query(func.count(Inspection.id))
        .filter(Inspection.status.in_(["AMBER", "RED", "GRAY"]), Inspection.review_status == "pending")
        .scalar()
        or 0
    )
    parts_total = db.query(func.count(Part.id)).filter(Part.active.is_(True)).scalar() or 0
    snap = metrics.snapshot()
    accuracy = round(approved / total, 4) if total else 0.0
    return {
        "inspections_total": total,
        "inspections_approved": approved,
        "inspections_pending_review": review_pending,
        "accuracy": accuracy,
        "parts_registered": parts_total,
        **snap,
    }


@router.get("/users", response_model=list[UserOut])
def list_users(user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.username).all()


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(body: UserCreate, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(409, "Usuario ja existe")
    new_user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        role=body.role,
        full_name=body.full_name,
        plant=body.plant,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    log_action(db, user.username, "user_create", f"user:{body.username}", body.role)
    return new_user


@router.patch("/users/{user_id}", response_model=UserOut)
def toggle_user(user_id: int, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == user_id).first()
    if target is None:
        raise HTTPException(404, "Usuario nao encontrado")
    if target.id == user.id:
        raise HTTPException(400, "Nao e possivel desativar o proprio usuario")
    target.active = not target.active
    db.commit()
    log_action(db, user.username, "user_toggle", f"user:{target.username}", str(target.active))
    return target


@router.get("/models", response_model=list[ModelVersionOut])
def list_models(user=Depends(require_role("supervisor")), db: Session = Depends(get_db)):
    return db.query(AIModelVersion).order_by(AIModelVersion.created_at.desc()).all()


@router.post("/models/{model_id}/activate", response_model=ModelVersionOut)
def activate_model(model_id: int, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    model = db.query(AIModelVersion).filter(AIModelVersion.id == model_id).first()
    if model is None:
        raise HTTPException(404, "Modelo nao encontrado")
    db.query(AIModelVersion).update({AIModelVersion.active: False})
    model.active = True
    db.commit()
    db.refresh(model)
    log_action(db, user.username, "model_activate", f"model:{model.name}", model.version)
    return model


@router.get("/audit", response_model=list[dict])
def list_audit(limit: int = 100, user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(min(limit, 500)).all()
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp,
            "username": log.username,
            "action": log.action,
            "entity": log.entity,
            "detail": log.detail,
        }
        for log in logs
    ]


@router.post("/cache/refresh")
def refresh_cache(user=Depends(require_role("supervisor")), db: Session = Depends(get_db)):
    references = reference_store.load(db)
    return {"references_loaded": len(references), "engine_thresholds": {
        "min_match": config.MIN_MATCH_THRESHOLD,
        "amber": config.AMBER_THRESHOLD,
        "default_approval": config.DEFAULT_APPROVAL_CONFIDENCE,
    }}
