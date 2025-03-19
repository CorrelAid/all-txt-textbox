import secrets
import uuid
from typing import Any, Annotated, Callable, Optional

from fastapi import Depends, Request, Response
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter
from pwdlib import PasswordHash

from database.session import get_async_session, LocalAsyncSession
from models import ApiKey
from settings import settings


class RateLimiterWithApiKey:

    def __init__(
        self,
        times: Annotated[int, Field(ge=0)] = 1,
        milliseconds: Annotated[int, Field(ge=-1)] = 0,
        seconds: Annotated[int, Field(ge=-1)] = 0,
        minutes: Annotated[int, Field(ge=-1)] = 0,
        hours: Annotated[int, Field(ge=-1)] = 0,
        identifier: Optional[Callable] = None,
        callback: Optional[Callable] = None,
    ) -> None:
        self.password_hasher = PasswordHash.recommended()
        self.rate_limiter = RateLimiter(
            times=times,
            milliseconds=milliseconds,
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            identifier=identifier,
            callback=callback,
        )

    async def _check_api_key(self, request: Request, db_session: AsyncSession) -> bool:
        if not request.headers.get("Authorization", None):
            return False

        # deconstruct the api key from the header
        _, short_token, long_token = request.headers["Authorization"].split("_")

        # check if the api key exists
        api_key = await db_session.get(ApiKey, short_token)
        if not api_key:
            return False

        # check if the api key is valid
        if not self.password_hasher.verify(password=long_token, hash=api_key.key):
            return False

        return True

    async def __call__(
        self,
        request: Request,
        response: Response,
        db_session: Annotated[AsyncSession, Depends(get_async_session)],
    ) -> Any | None:
        # check if the api key is valid otherwise rate limit the request
        if await self._check_api_key(request=request, db_session=db_session):
            return None
        return await self.rate_limiter(request=request, response=response)

    @classmethod
    async def create_api_key(cls, comment: str, prefix: str | None = None) -> str:
        # generate a new api key
        prefix = prefix or settings.api_key.prefix
        short_token = uuid.uuid4().hex
        long_token = secrets.token_urlsafe(48)
        # ensure that the long token does not contain the underscore character
        while "_" in long_token:
            long_token = secrets.token_urlsafe(48)

        # store the api key in the database
        password_hasher = PasswordHash.recommended()
        async with LocalAsyncSession.begin() as db_session:
            db_session.add(
                ApiKey(
                    id=short_token,
                    key=password_hasher.hash(long_token),
                    comment=comment,
                )
            )

        # return the client api key
        return f"{prefix}_{short_token}_{long_token}"
