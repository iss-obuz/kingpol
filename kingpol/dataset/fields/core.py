from dataclasses import dataclass
from typing import Literal

from pydantic import Field, PositiveInt


@dataclass
class FieldDef:
    """Base class for defining fields in a dataset."""

    type: type
    field: Field

    @property
    def T(self) -> type:
        """Return the type of the field."""
        return self.type


Volume = FieldDef(
    type=Literal[1, 2, 3, 4, 5, 6, 7, 8],
    field=Field(
        title="Volume",
        description="Address book volume number.",
    ),
)

Year = FieldDef(
    type=PositiveInt | None,  # type: ignore
    field=Field(
        default=None,
        title="Year",
        description="Publication year of the address book volume.",
        ge=1904,
        le=1911,
    ),
)

Product = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Product",
        description="Product name.",
    ),
)

Unit = FieldDef(
    type=str | None,
    field=Field(
        default=None,
        title="Unit",
        description="Unit of measurement.",
    ),
)
