import hashlib
import secrets
from typing import Annotated
from datetime import datetime, timedelta

from fastapi import Depends, Request
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_async_session
from models import Salt
from settings import settings


async def get_todays_salt(
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
) -> str:
    select_stmt = select(Salt).where(
        Salt.created_at
        >= datetime.now() - timedelta(minutes=settings.session.valid_for)
    )
    result = (await db_session.execute(select_stmt)).scalar_one_or_none()
    if result:
        return result.salt

    delete_stmt = delete(Salt)
    await db_session.execute(delete_stmt)

    salt = secrets.token_urlsafe(32)
    db_session.add(Salt(salt=salt))
    return salt

# this function ensures that the hash of the IP address cannot be reverse engineered in combination with the salt. For any forward going programming do not change the Salt!
async def session_dependency(
    request: Request,
    salt: Annotated[str, Depends(get_todays_salt)],
) -> str:
    user_agent = request.headers.get("User-Agent", "Unknown")
    ip = request.headers.get("X-Forwarded-For", None)
    if ip is None and request.client and request.client.host:
        ip = request.client.host
    if ip is None:
        ip = "Unknown"
    return hashlib.sha256(f"{salt}{user_agent}{ip}".encode()).hexdigest()
