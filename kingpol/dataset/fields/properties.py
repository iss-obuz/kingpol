from pydantic import Field

from .core import FieldDef

PropertyId = FieldDef(
    type=str,
    field=Field(
        title="Property ID",
        description="Unique property identifier.",
    ),
)

PropertyName = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Property",
        description="Property name.",
    ),
)

PropertyObjectName = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Object",
        description="Object name.",
    ),
)

PropertyValue = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Property value",
        description="Raw property value as string.",
    ),
)

PropertyNumValue = FieldDef(
    type=float | None,
    field=Field(
        default=None,
        title="Property numeric value",
        description="Numeric property value.",
    ),
)

PropertyDescription = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Description",
        description="Additional property description.",
    ),
)

PropertyConfirmed = FieldDef(
    type=bool | None,
    field=Field(
        default=None,
        title="Confirmed",
        description="Whether the property value is confirmed.",
    ),
)

PropertyOfficial = FieldDef(
    type=bool | None,
    field=Field(
        default=None,
        title="Official",
        description="Whether the property value is official.",
    ),
)
