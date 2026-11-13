import os
import time
import uuid

import cv2
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend import config
from backend.database import get_db
from backend.models import Inspection
from backend.schemas import InspectionOut, ReviewRequest
from backend.security import get_current_user, require_role
from backend.services import metrics
from backend.services.audit import log_action
from backend.services.image_validation import decode_image
from backend.services.vision_engine import get_engine, reference_store

router = APIRouter(prefix="/api/inspections", tags=["inspections"])

ACTIVE_ENGINE = "orb_matching"


@router.get("", response_model=list[InspectionOut])
def list_inspections(
    limit: int = 50,
    status_filter: str | None = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Inspection).order_by(Inspection.created_at.desc())
    if status_filter:
        query = query.filter(Inspection.status == status_filter.upper())
    return query.limit(min(limit, 200)).all()


@router.get("/{inspection_id}", response_model=InspectionOut)
def get_inspection(inspection_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if inspection is None:
        raise HTTPException(404, "Inspecao nao encontrada")
    return inspection


@router.post("", response_model=InspectionOut, status_code=201)
def create_inspection(
    file: UploadFile = File(...),
    capture_ms: float = Form(0.0),
    upload_ms: float = Form(0.0),
    device_info: str = Form(""),
    synced_offline: bool = Form(False),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    t_start = time.perf_counter()
    data = file.file.read()
    if len(data) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Arquivo excede o limite de tamanho")
    image = decode_image(data)
    if image is None:
        raise HTTPException(400, "Imagem ilegivel ou corrompida")

    max_side = max(image.shape[0], image.shape[1])
    if max_side > 1600:
        scale = 1600.0 / max_side
        image = cv2.resize(image, (int(image.shape[1] * scale), int(image.shape[0] * scale)))

    references = reference_store.load(db)
    engine = get_engine(ACTIVE_ENGINE)
    result = engine.identify(image, references)
    inference_ms = (time.perf_counter() - t_start) * 1000.0
    total_ms = float(capture_ms) + float(upload_ms) + inference_ms

    filename = f"{uuid.uuid4().hex[:12]}.jpg"
    image_path = os.path.join(config.CAPTURES_DIR, filename)
    cv2.imwrite(image_path, image, [cv2.IMWRITE_JPEG_QUALITY, 80])

    inspection = Inspection(
        part_id=result["part_id"],
        part_code=result["part_code"],
        part_name=result["part_name"],
        image_path=image_path,
        status=result["status"],
        confidence=result["confidence"],
        match_score=result["match_score"],
        divergences=result["divergences"],
        latency_ms={
            "capture_ms": round(float(capture_ms), 1),
            "upload_ms": round(float(upload_ms), 1),
            "inference_ms": round(inference_ms, 1),
            "total_ms": round(total_ms, 1),
            "quality": result["quality"],
        },
        operator=user.username,
        device_info=device_info[:200],
        synced_offline=synced_offline,
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    metrics.record(
        {
            "capture": capture_ms,
            "upload": upload_ms,
            "inference": inference_ms,
            "total": total_ms,
            "status": result["status"],
        }
    )
    log_action(db, user.username, "inspection_create", inspection.id, f"{result['status']} {result['part_code']}")
    return inspection


@router.get("/{inspection_id}/image")
def get_inspection_image(inspection_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if inspection is None or not inspection.image_path or not os.path.exists(inspection.image_path):
        raise HTTPException(404, "Imagem nao encontrada")
    return FileResponse(inspection.image_path, media_type="image/jpeg")


@router.post("/{inspection_id}/review", response_model=InspectionOut)
def review_inspection(
    inspection_id: str,
    body: ReviewRequest,
    user=Depends(require_role("supervisor")),
    db: Session = Depends(get_db),
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if inspection is None:
        raise HTTPException(404, "Inspecao nao encontrada")
    if inspection.status not in ("AMBER", "RED", "GRAY"):
        raise HTTPException(400, "Somente inspecoes pendentes de revisao podem ser avaliadas")
    inspection.review_status = body.decision
    inspection.reviewed_by = user.username
    inspection.review_note = body.note
    db.commit()
    db.refresh(inspection)
    log_action(db, user.username, "inspection_review", inspection.id, body.decision)
    return inspection
