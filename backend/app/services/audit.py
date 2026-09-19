import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.audit import AuditLog

logger = logging.getLogger("ekmat.audit")

def log_action(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: Optional[int],
    actor: str = "SYSTEM",
    before_state: Optional[Dict[str, Any]] = None,
    after_state: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Appends an immutable audit log entry.
    Actions: IMPORT | MATCH_GENERATED | APPROVE | REJECT | EDIT_APPROVE
    """
    entry = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor=actor,
        before_state=before_state,
        after_state=after_state
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    logger.info(f"Audit log recorded: {action} on {entity_type}:{entity_id} by {actor}")
    return entry
