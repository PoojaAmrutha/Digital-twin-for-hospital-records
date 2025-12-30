from sqlalchemy.orm import Session
from models import AuditLog
import json
from datetime import datetime

class AuditLogger:
    def log_change(
        self, 
        db: Session, 
        user_id: int, 
        target_table: str, 
        target_id: int, 
        action: str, 
        old_value: dict = None, 
        new_value: dict = None
    ):
        """
        Log a change to the audit table
        """
        log = AuditLog(
            user_id=user_id,
            target_table=target_table,
            target_id=target_id,
            action=action,
            old_value=json.dumps(old_value, default=str) if old_value else None,
            new_value=json.dumps(new_value, default=str) if new_value else None,
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        print(f"✅ Audit Log: User {user_id} {action} on {target_table} {target_id}")

audit_logger = AuditLogger()
