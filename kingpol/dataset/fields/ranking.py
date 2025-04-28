from pydantic import Field, PositiveFloat

from .core import FieldDef

IsElite = FieldDef(
    type=bool,
    field=Field(
        title="Elite",
        description=(
            "Whether belongs to elite "
            "(see 'params.yaml' for the inclusion criteria)."
        ),
    ),
)


EntityRankingProductionValueShare = FieldDef(
    type=PositiveFloat | None,
    field=Field(
        default=None,
        title="Production value (share)",
        description=(
            "Entity's share in the yearly production value "
            "of all associated companies. "
            "The share is proportional to the number of records listing "
            "the entity as an associated person with a relationship of "
            "a high enough rank (configured by 'shares.relations' parameter)."
        ),
    ),
)

EntityRankingEmploymentShare = FieldDef(
    type=PositiveFloat | None,
    field=Field(
        default=None,
        title="Employment (share)",
        description=(
            "Entity's share in the employment of all associated companies. "
            "The share is proportional to the number of records listing "
            "the entity as an associated person with a relationship of "
            "a high enough rank (configured by 'shares.relations' parameter)."
        ),
    ),
)

EntityRankingProductionValueTotal = FieldDef(
    type=PositiveFloat | None,
    field=Field(
        default=None,
        title="Production value (total)",
        description=(
            "Total yearly production value of all associated companies. "
            "This measure is a simple sum over associated companies wihtout "
            "splitting proportional to shares"
        ),
    ),
)

EntityRankingEmploymentTotal = FieldDef(
    type=PositiveFloat | None,
    field=Field(
        default=None,
        title="Employment (total)",
        description=(
            "Total employment of all associated companies. "
            "This measure is a simple sum over associated companies wihtout "
            "splitting proportional to shares"
        ),
    ),
)

EntityRankingProductivity = FieldDef(
    type=PositiveFloat | None,
    field=Field(
        default=None,
        title="Productivity",
        description=("Yearly productivity of the entity (in rubles per employee)."),
    ),
)
