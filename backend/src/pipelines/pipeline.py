from abc import ABC, abstractmethod
from typing import Any, Literal
import uuid

from typing_extensions import Self
from pydantic import BaseModel, model_validator


class Suggestion(BaseModel):
    variant: str
    text: str


class SuggestionTarget(BaseModel):
    id: str
    type: Literal["gender"]
    comment: str
    original: str
    suggestions: list[Suggestion]
    start: int
    stop: int

    @model_validator(mode="before")
    @classmethod
    def check_passwords_match(cls, data: Any) -> Any:
        if "id" not in data or data["id"] is None:
            data["id"] = uuid.uuid4().hex
        return data


class Pipeline(ABC):

    @abstractmethod
    def __call__(self, text: str) -> list[SuggestionTarget]:
        pass
