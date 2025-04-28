from pydantic import Field, PositiveFloat, PositiveInt

from .core import FieldDef

RecordId = FieldDef(
    type=str,
    field=Field(
        title="Record ID",
        description=(
            "Unique company-record identifier. " "Can be used for joining tables."
        ),
    ),
)

CompanyId = FieldDef(
    type=str,
    field=Field(
        title="Company ID",
        description=("Unique company identifier. " "Can be used for joining tables."),
    ),
)

CompanyName = FieldDef(
    type=str,
    field=Field(
        title="Company name",
        description="Name of the company.",
    ),
)

CompanyType = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Company type",
        description="Type of the company.",
    ),
)

CompanyIndustry = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Industry",
        description="Industry of the company.",
    ),
)

CompanySubsector = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Subsector",
        description="Detailed sector the company belongs to.",
    ),
)

CompanySector = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Sector",
        description="Sector the company belongs to.",
    ),
)

CompanyProductionValue = FieldDef(
    type=PositiveFloat | None,
    field=Field(
        default=None,
        title="Value",
        description="Yearly production value (in rubles).",
    ),
)

CompanyEmployment = FieldDef(
    type=PositiveFloat | None,  # type: ignore
    field=Field(
        default=None,
        title="Employment",
        description="Number of employees.",
    ),
)

CompanyProductivity = FieldDef(
    type=PositiveFloat | None,
    field=Field(
        default=None,
        title="Productivity",
        description="Yearly productivity (in rubles per employee).",
    ),
)

CompanyOutput = FieldDef(
    type=PositiveFloat | None,
    field=Field(
        default=None,
        title="Output",
        description="Yearly product output.",
    ),
)

CompanyAddress = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Address",
        description="Company address.",
    ),
)

CompanyGovernorate = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Governorate",
        description="Governorate where the company is located.",
    ),
)

CompanyFoundationYear = FieldDef(
    type=PositiveInt | None,  # type: ignore
    field=Field(
        default=None,
        title="Foundation year",
        description="Year the company was founded.",
    ),
)

CompanyPublicYear = FieldDef(
    type=PositiveInt | None,  # type: ignore
    field=Field(
        default=None,
        title="Public year",
        description="Year the company was publicly listed.",
        alias="become public",
    ),
)
