import secrets
import re
from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from models import GenderDictionary
from pipelines.pipeline import Pipeline, SuggestionTarget, Suggestion


class DictionaryEntry(TypedDict):
    comment: str
    suggestions: list[Suggestion]


class GenderNeutralizer(Pipeline):

    def __init__(self, gender_dict: dict[str, DictionaryEntry] = {}):
        self.gender_dict = gender_dict

    def __call__(self, text: str) -> list[SuggestionTarget]:
        """
        Suggests other words in a text based on masculine, feminine, and neutral forms of pronouns, nouns, articles, and adjectives.

        Args:
          text: The text to suggest other words for.

        Returns:
          A list of suggested words for each word in the text.
        """
        possible_replacements: list[SuggestionTarget] = []
        # PROCESSING: NOT OPEN SOURCE
        return possible_replacements

    @classmethod
    async def from_database(cls, db_session: AsyncSession) -> "GenderNeutralizer":

        # PREPROCESSING: NOT OPEN SOURCE
        
        gender_dict = {}
        
        # PROCESSING: NOT OPEN SOURCE

        return cls(gender_dict=gender_dict)
