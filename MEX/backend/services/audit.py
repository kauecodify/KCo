from sqlalchemy.orm import Session

from backend.models import AuditLog


def log_action(db: Session, username: str, action: str, entity: str = "", detail: str = ""):
    db.add(AuditLog(username=username or "system", action=action, entity=entity, detail=detail[:2000]))
    db.commit()
