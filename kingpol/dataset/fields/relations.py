from pydantic import Field

from .core import FieldDef

RelationType = FieldDef(
    type=str,
    field=Field(
        title="Relation type",
        description="Type of the person-company relation.",
    ),
)
