# =====================================================
#                       imports
# =====================================================
# Libraries:
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from io import StringIO
from fastapi.responses import StreamingResponse
# Models:
from models import AuditLog
# Schemas:
from schemas import AuditLogsResponse, AuditLogResponse
# =====================================================


# =====================================================
#                       Business logic
# =====================================================

# Function for getting latest audit logs
async def get_latest_audit_logs(
    db: AsyncSession,
    current_user_roles: list[str]
) -> AuditLogsResponse:

    # Allow access only for administrators
    if "admin" not in current_user_roles:
        raise HTTPException(403, "Forbidden")

    # Fetch the latest 10 audit log entries
    result = await db.exec(
        select(AuditLog)
        .order_by(desc(AuditLog.created_at))
        .limit(10)
    )

    # Retrieve query results
    logs = result.all()

    # Convert database models to API response schema
    return AuditLogsResponse(
        logs=[
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                success=log.success,
                meta=log.meta,
                created_at=log.created_at
            )
            for log in logs
        ]
    )

# Function for downloading audit logs
async def download_audit_logs(
    db: AsyncSession,
    current_user_roles: list[str]
):

    # Allow access only for administrators
    if "admin" not in current_user_roles:
        raise HTTPException(403, "Forbidden")

    # Fetch all audit log entries ordered by creation date
    result = await db.exec(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
    )

    # Retrieve query results
    logs = result.all()

    # Create an in-memory text buffer
    buffer = StringIO()

    # Write audit log entries to the text file
    for log in logs:
        buffer.write(
            f"[{log.created_at}] "
            f"user_id={log.user_id} "
            f"action={log.action} "
            f"entity={log.entity_type}:{log.entity_id} "
            f"success={log.success} "
            f"meta={log.meta}\n"
        )

    # Reset cursor position to the beginning of the file
    buffer.seek(0)

    # Return the generated file as a downloadable response
    return StreamingResponse(
        buffer,
        media_type="text/plain",
        headers={
            # Force browser to download the file
            "Content-Disposition": 'attachment; filename="audit_logs.txt"'
        }
    )