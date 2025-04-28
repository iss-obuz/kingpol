import re
from typing import Any, ClassVar, Self

import numpy as np
import pandas as pd
from pydantic import (
    BaseModel,
    model_validator,
)

from kingpol.dataset.fields import (
    CompanyId,
    Product,
    PropertyConfirmed,
    PropertyDescription,
    PropertyId,
    PropertyName,
    PropertyNumValue,
    PropertyObjectName,
    PropertyOfficial,
    PropertyValue,
    RecordId,
    Unit,
    Volume,
    Year,
)

_numeric_props = (
    "employment",
    "output",
    "capital",
    "foundation",
    "become public",
)


class CompanyProperty(BaseModel):
    """Detailed information on individual properties within company records.

    This table is an implementation detail of the dataset compilation process
    and is not intended for direct use by end users.
    """

    company_id: CompanyId.T = CompanyId.field
    record_id: RecordId.T = RecordId.field
    property_id: PropertyId.T = PropertyId.field
    volume: Volume.T = Volume.field
    year: Year.T = Year.field
    property: PropertyName.T = PropertyName.field
    object: PropertyObjectName.T = PropertyObjectName.field
    value: PropertyValue.T = PropertyValue.field
    num_value: PropertyNumValue.T = PropertyNumValue.field
    product: Product.T = Product.field
    unit: Unit.T = Unit.field
    desc1: PropertyDescription.T = PropertyDescription.field
    desc2: PropertyDescription.T = PropertyDescription.field
    confirmed: PropertyConfirmed.T = PropertyConfirmed.field
    official: PropertyOfficial.T = PropertyOfficial.field

    volumes: ClassVar[pd.DataFrame | None] = None
    currencies: ClassVar[pd.DataFrame | None] = None
    units: ClassVar[pd.DataFrame | None] = None

    @model_validator(mode="before")
    @classmethod
    def preprocess(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in data.items() if not pd.isnull(v)}

    @model_validator(mode="after")
    def postprocess_unit(self) -> Self:
        if self.property == "output" and self.desc1:
            product, unit = self.desc1, None
            if "@" in product:
                product, unit = (s.strip() for s in product.split("@"))
            self.product = product
            if unit:
                self.unit = unit
            # Correct units
            self.unit = {"metr kubiczny": "m3"}.get(self.unit, self.unit)

        if self.units is None:
            errmsg = "cannot set 'unit' without 'units' table"
            raise AttributeError(errmsg)
        if self.unit is not None and self.unit in self.units.index:
            self.unit = self.units.loc[self.unit]

        return self

    @model_validator(mode="after")
    def postprocess_numeric_values(self) -> Self:
        if self.property in _numeric_props and not self.num_value:
            self.num_value = process_num_value(self.value)
        self.num_value = rescale_nonfull_year_output(self.product, self.num_value)
        return self

    @model_validator(mode="after")
    def postprocess_year(self) -> Self:
        if self.volumes is None:
            errmsg = "cannot set 'year' without 'volumes' table"
            raise AttributeError(errmsg)
        self.year = int(self.volumes.loc[self.volume])
        return self

    @model_validator(mode="after")
    def postprocess_currencies(self) -> Self:
        if self.property == "capital":
            if self.unit is None:
                self.unit = "ruble"
            if self.num_value and self.unit != "ruble":
                if self.currencies is None:
                    errmsg = (
                        f"cannot convert from '{self.unit}' "
                        "without 'currencies' table"
                    )
                    raise AttributeError(errmsg)
                rate = self.currencies.loc[self.unit, self.year]
                self.num_value *= float(rate)
                self.unit = "ruble"
        return self


# Utils ------------------------------------------------------------------------------

rx_nv_approx = re.compile(r"\s*(oko[lł]o|do|[śs]rednio)\s*", re.IGNORECASE)
rx_nv_note = re.compile(r"\s*\(.*?\)\s*", re.IGNORECASE)
rx_nv_digit = re.compile(r"\d", re.IGNORECASE)
rx_nv_nonum = re.compile(r"[^\d,\.–-]", re.IGNORECASE)
rx_nv_split = re.compile(r"[,+\s]", re.IGNORECASE)
rx_nv_range = re.compile(r"(?<=\d)[–\-](?=\d)", re.IGNORECASE)
rx_nv_numsep = re.compile(r"(?<=\d)[,.](?=\d)", re.IGNORECASE)
rx_nv_monthly = re.compile(r"^\s*\d+\s*month", re.IGNORECASE)
rx_nv_months = re.compile(r"(\d+)")


def process_num_value(s: str) -> float:
    """Process `num_value` company property.

    Examples
    --------
    >>> float(process_num_value("6"))
    6.0
    >>> float(process_num_value("1-3"))
    2.0
    >>> float(process_num_value("12,5 (sążni)" ))
    12.5
    >>> float(process_num_value("1200–1500 bali drewnianych"))
    1350.0
    >>> float(process_num_value("Dziwne coś, hej!"))
    nan
    >>> float(process_num_value(""))
    nan
    >>> float(process_num_value("'w papierach % 8292970,79 w nieruch. 624800"))
    8917770.79
    >>> float(process_num_value("7,5+12,5 (elektryczny 7,5 KM i gazowy 12,5 KM)"))
    20.0
    """
    x = s
    if isinstance(x, float):
        return x
    if not rx_nv_digit.search(x):
        return np.nan
    x = rx_nv_approx.sub(r"", x)
    x = rx_nv_note.sub(r"", x)
    x = rx_nv_numsep.sub(r".", x)

    num = np.nan
    for xi in rx_nv_split.split(x):
        if not rx_nv_digit.search(xi):
            continue
        xi = rx_nv_nonum.sub(r"", xi)
        xi = xi.strip()
        if not xi:
            continue
        xi = np.mean([float(i.strip()) for i in rx_nv_range.split(xi)])
        if not np.isnan(xi):
            if not np.isnan(num):
                num += xi
            else:
                num = xi
    return num


def rescale_nonfull_year_output(
    product: str | None, num_value: float | None
) -> float | None:
    """Rescale output value reported only for several months to full year.

    Parameters
    ----------
    product
        Product name.
    num_value
        Numeric output value.

    Examples
    --------
    >>> rescale_nonfull_year_output("9 months", 900)
    1200.0
    >>> rescale_nonfull_year_output("dupa", 1)
    1.0
    """
    if pd.isnull(num_value):
        return None
    num_value = float(num_value)
    if pd.isnull(product) or not rx_nv_monthly.search(product):
        return num_value
    nmonths = int(rx_nv_months.search(product).group(0))
    num_value *= 12 / nmonths
    return num_value
