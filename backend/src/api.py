from contextlib import asynccontextmanager
from typing import Annotated

import redis.asyncio as redis
from fastapi import Body, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi_limiter import FastAPILimiter
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from models.requests import Request
from settings import settings
from pipelines import GenderNeutralizer, Pipeline, SuggestionTarget
from database.session import LocalAsyncSession, get_async_session
from dependencies import session_dependency, RateLimiterWithApiKey


pipeline: list[Pipeline] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize rate limiter
    await FastAPILimiter.init(redis.from_url(settings.redis.dsn, encoding="utf-8"))
    # initialize pipeline
    global pipeline
    async with LocalAsyncSession.begin() as session:
        pipeline.append(await GenderNeutralizer.from_database(db_session=session))
    yield
    # cleanup rate limiter
    await FastAPILimiter.close()
    # free pipeline resources
    pipeline = []


def custom_generate_unique_id(route: APIRoute) -> str:
    return route.name


app = FastAPI(lifespan=lifespan, generate_unique_id_function=custom_generate_unique_id)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)


class TextInput(BaseModel):
    text: str


class PipelineResponse(BaseModel):
    original_text: str
    suggestions: list[SuggestionTarget]


# API working with multiple sentences
@app.post(
    path="/",
    dependencies=[Depends(RateLimiterWithApiKey(times=5, minutes=1))],
    tags=["Pipeline"],
    response_model=PipelineResponse,
)
async def run(
    text: Annotated[TextInput, Body],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
    user_session: Annotated[str | None, Depends(session_dependency)] = None,
):
    db_session.add(
        Request(
            session=user_session,
            text=text.text,
        )
    )

    original_text = text.text
    suggestions: list[SuggestionTarget] = []

    for pipe in pipeline:
        suggestions.extend(pipe(original_text))
    return PipelineResponse(
        original_text=original_text,
        suggestions=suggestions,
    )
