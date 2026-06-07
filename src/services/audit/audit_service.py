from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from models import AuditLog
from schemas import AuditLogsResponse, AuditLogResponse
from io import StringIO
from fastapi.responses import StreamingResponse

async def get_latest_audit_logs(
    db: AsyncSession,
    current_user_roles: list[str]
) -> AuditLogsResponse:

    if "admin" not in current_user_roles:
        raise HTTPException(403, "Forbidden")

    result = await db.exec(
        select(AuditLog)
        .order_by(desc(AuditLog.created_at))
        .limit(20)
    )

    logs = result.all()

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


async def download_audit_logs(
    db: AsyncSession,
    current_user_roles: list[str]
):

    if "admin" not in current_user_roles:
        raise HTTPException(403, "Forbidden")

    result = await db.exec(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
    )

    logs = result.all()

    buffer = StringIO()

    for log in logs:
        buffer.write(
            f"[{log.created_at}] "
            f"user_id={log.user_id} "
            f"action={log.action} "
            f"entity={log.entity_type}:{log.entity_id} "
            f"success={log.success} "
            f"meta={log.meta}\n"
        )

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/plain",
        headers={
            "Content-Disposition": 'attachment; filename="audit_logs.txt"'
        }
    )