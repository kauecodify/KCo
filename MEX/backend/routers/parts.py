import os
import uuid

import cv2
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend import config
from backend.database import get_db
from backend.models import Part, PartImage
from backend.schemas import PartCreate, PartImageOut, PartOut, PartUpdate
from backend.security import require_role
from backend.services.audit import log_action
from backend.services.image_validation import decode_image

router = APIRouter(prefix="/api/parts", tags=["parts"])


@router.get("/reference/{filename}")
def get_reference_image(filename: str, user=Depends(require_role("operator"))):
    safe = os.path.basename(filename)
    path = os.path.join(config.REFERENCE_DIR, safe)
    if not os.path.exists(path):
        raise HTTPException(404, "Imagem nao encontrada")
    return FileResponse(path, media_type="image/jpeg")


def save_reference_image(db: Session, part: Part, data: bytes, is_primary: bool) -> PartImage:
    if len(data) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Arquivo excede o limite de tamanho")
    image = decode_image(data)
    if image is None:
        raise HTTPException(400, "Imagem de referencia invalida")
    filename = f"{part.code}_{uuid.uuid4().hex[:8]}.jpg"
    path = os.path.join(config.REFERENCE_DIR, filename)
    cv2.imwrite(path, image, [cv2.IMWRITE_JPEG_QUALITY, 90])
    entry = PartImage(part_id=part.id, path=path, is_primary=is_primary)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=list[PartOut])
def list_parts(
    include_inactive: bool = False,
    user=Depends(require_role("operator")),
    db: Session = Depends(get_db),
):
    query = db.query(Part)
    if not include_inactive:
        query = query.filter(Part.active.is_(True))
    return query.order_by(Part.code).all()


@router.get("/{part_id}", response_model=PartOut)
def get_part(part_id: int, user=Depends(require_role("operator")), db: Session = Depends(get_db)):
    part = db.query(Part).filter(Part.id == part_id).first()
    if part is None:
        raise HTTPException(404, "Peca nao encontrada")
    return part


@router.post("", response_model=PartOut, status_code=201)
def create_part(
    body: PartCreate,
    user=Depends(require_role("supervisor")),
    db: Session = Depends(get_db),
):
    if db.query(Part).filter(Part.code == body.code).first():
        raise HTTPException(409, "Codigo de peca ja cadastrado")
    part = Part(
        code=body.code.upper(),
        name=body.name,
        category=body.category,
        description=body.description,
        specifications=body.specifications,
        dimensions=body.dimensions,
        tolerances=body.tolerances,
        approval_criteria=body.approval_criteria,
        active=body.active,
        version_history=[{"version": 1, "action": "criacao", "by": user.username}],
    )
    db.add(part)
    db.commit()
    db.refresh(part)
    log_action(db, user.username, "part_create", f"part:{part.code}")
    return part


@router.put("/{part_id}", response_model=PartOut)
def update_part(
    part_id: int,
    body: PartUpdate,
    user=Depends(require_role("supervisor")),
    db: Session = Depends(get_db),
):
    part = db.query(Part).filter(Part.id == part_id).first()
    if part is None:
        raise HTTPException(404, "Peca nao encontrada")
    changes = body.model_dump(exclude_none=True)
    if not changes:
        raise HTTPException(400, "Nenhum campo para atualizar")
    for field, value in changes.items():
        setattr(part, field, value)
    part.version += 1
    part.version_history = (part.version_history or []) + [
        {"version": part.version, "action": "atualizacao", "fields": list(changes.keys()), "by": user.username}
    ]
    db.commit()
    db.refresh(part)
    log_action(db, user.username, "part_update", f"part:{part.code}", str(list(changes.keys())))
    return part


@router.post("/{part_id}/images", response_model=PartImageOut, status_code=201)
def upload_reference_image(
    part_id: int,
    file: UploadFile = File(...),
    is_primary: bool = False,
    user=Depends(require_role("supervisor")),
    db: Session = Depends(get_db),
):
    part = db.query(Part).filter(Part.id == part_id).first()
    if part is None:
        raise HTTPException(404, "Peca nao encontrada")
    data = file.file.read()
    if not is_primary and not part.images:
        is_primary = True
    entry = save_reference_image(db, part, data, is_primary)
    log_action(db, user.username, "part_image_upload", f"part:{part.code}", entry.path)
    return entry


@router.delete("/{part_id}/images/{image_id}", status_code=204)
def delete_reference_image(
    part_id: int,
    image_id: int,
    user=Depends(require_role("supervisor")),
    db: Session = Depends(get_db),
):
    entry = db.query(PartImage).filter(PartImage.id == image_id, PartImage.part_id == part_id).first()
    if entry is None:
        raise HTTPException(404, "Imagem nao encontrada")
    if os.path.exists(entry.path):
        os.remove(entry.path)
    db.delete(entry)
    db.commit()
    log_action(db, user.username, "part_image_delete", f"part:{part_id}", str(image_id))
