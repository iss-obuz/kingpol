from typing import Literal

from pydantic import Field, PositiveFloat, PositiveInt

from .core import FieldDef

EntityId = FieldDef(
    type=str,
    field=Field(
        title="Entity ID",
        description=("Unique entity identifier. Can be used for joining tables."),
    ),
)

EntityFullName = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Full name",
        description="Full name of the entity.",
    ),
)

EntitySurname = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Surname",
        description="Surname of the person.",
    ),
)

EntityName = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Name",
        description="Name of the person.",
    ),
)

EntityBiographicalEventYear = FieldDef(
    type=PositiveInt | None,  # type: ignore
    field=Field(
        default=None,
        title="Year",
        description="Year of a biographical event.",
    ),
)

EntityBiographicalEventMonth = FieldDef(
    type=PositiveInt | None,  # type: ignore
    field=Field(
        default=None,
        title="Month",
        description="Month of a biographical event.",
    ),
)

EntityBiographicalEventDay = FieldDef(
    type=PositiveInt | None,  # type: ignore
    field=Field(
        default=None,
        title="Day",
        description="Day of a biographical event.",
    ),
)

EntityIsPhysical = FieldDef(
    type=bool,
    field=Field(
        default=True,
        title="Physical",
        description="Whether the entity is a physical person.",
    ),
)

EntityIsLegal = FieldDef(
    type=bool,
    field=Field(
        default=False,
        title="Legal",
        description="Whether the entity is a legal person.",
    ),
)

EntityTitleNoble = FieldDef(
    type=Literal["prince", "count", "baron"] | None,
    field=Field(
        default=None,
        title="Noble title",
        description="Noble title of the entity.",
    ),
)

EntityTitleOther = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Other title",
        description="Other title of the entity.",
    ),
)

EntitySex = FieldDef(
    type=Literal["male", "female"] | None,
    field=Field(
        default=None,
        title="Sex",
        description="Sex of the person.",
    ),
)

EntityShare = FieldDef(
    type=PositiveFloat | None,  # type: ignore
    field=Field(
        default=None,
        title="Share",
        description="Share of the entity in the company.",
    ),
)
