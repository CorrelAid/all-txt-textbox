"""Seed gender_dictionary tables

Revision ID: 0004
Revises: 0003
Create Date: 2024-07-12 14:45:59.105343

"""

import yaml

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import Session

from models import GenderDictionary, GenderDictionarySuggestion


# revision identifiers, used by Alembic.
revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(bind=op.get_bind())
    with open("./database/migrations/data/gender-dictionary.yaml", mode="r") as fp:
        gender_dictionary = yaml.safe_load(fp)
    for entry_dict in gender_dictionary:
        entry = GenderDictionary(
            femininum=entry_dict.pop("femininum"),
            masculinum=entry_dict.pop("maskulinum"),
            comment=entry_dict.pop("erklärung")[0],
            updated_at=sa.func.now(),
        )
        entry.suggestions = [
            GenderDictionarySuggestion(type=type, value=value)
            for type, values in entry_dict.items()
            for value in values
        ]
        session.add(entry)
    session.commit()
    session.close()


def downgrade() -> None:
    delete_stmt = sa.delete(GenderDictionarySuggestion)
    op.execute(delete_stmt)
    delete_stmt = sa.delete(GenderDictionary)
    op.execute(delete_stmt)
