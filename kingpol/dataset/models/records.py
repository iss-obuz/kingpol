import re
from typing import Any, ClassVar, Self

import pandas as pd
from pydantic import (
    BaseModel,
    model_validator,
)

from kingpol.dataset.fields import (
    CompanyAddress,
    CompanyEmployment,
    CompanyFoundationYear,
    CompanyGovernorate,
    CompanyId,
    CompanyIndustry,
    CompanyName,
    CompanyOutput,
    CompanyProductionValue,
    CompanyProductivity,
    CompanyPublicYear,
    CompanySector,
    CompanySubsector,
    CompanyType,
    Product,
    RecordId,
    Unit,
    Volume,
    Year,
)
from kingpol.stats import mode

_numeric_props = (
    "employment",
    "output",
    "capital",
    "foundation",
    "become public",
)


class CompanyRecord(BaseModel):
    """Company record is a single entry in a specific volume of the address book.
    In some cases there may be mulitple records in the same volume for the same company.

    The compilation of the table depends on the following parameter
    groups in ``params.yaml`` file:

    * ``records``: parameters for the records table used for controlling
      threshold for outlier detection, inclusion of industries based on
      data (in)completeness, and selection of governorates.
    """

    company_id: CompanyId.T = CompanyId.field
    record_id: RecordId.T = RecordId.field
    volume: Volume.T = Volume.field
    year: Year.T = Year.field
    name: CompanyName.T = CompanyName.field
    type: CompanyType.T = CompanyType.field
    industry: CompanyIndustry.T = CompanyIndustry.field
    subsector: CompanySubsector.T = CompanySubsector.field
    sector: CompanySector.T = CompanySector.field
    value: CompanyProductionValue.T = CompanyProductionValue.field
    employment: CompanyEmployment.T = CompanyEmployment.field
    productivity: CompanyProductivity.T = CompanyProductivity.field
    output: CompanyOutput.T = CompanyOutput.field
    product: Product.T = Product.field
    unit: Unit.T = Unit.field
    address: CompanyAddress.T = CompanyAddress.field
    governorate: CompanyGovernorate.T = CompanyGovernorate.field
    foundation: CompanyFoundationYear.T = CompanyFoundationYear.field
    public: CompanyPublicYear.T = CompanyPublicYear.field

    prices: ClassVar[pd.DataFrame | None] = None
    conversions: ClassVar[pd.DataFrame | None] = None
    industries: ClassVar[pd.DataFrame | None] = None
    sectors: ClassVar[pd.DataFrame | None] = None
    types: ClassVar[pd.DataFrame | None] = None
    merging: ClassVar[pd.DataFrame | None] = None

    @model_validator(mode="before")
    @classmethod
    def preprocess(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in data.items() if not pd.isnull(v)}

    @model_validator(mode="after")
    def postprocess_address(self) -> Self:
        if self.address is not None:
            details = extract_address_details(self.address)
            for field, value in details.items():
                if field == "governorate" and value:
                    self.governorate = value
        if self.governorate:
            self.governorate = self.governorate.lower()
        return self

    @model_validator(mode="after")
    def postprocess_sector(self) -> Self:
        for table in ("industries", "sectors"):
            if getattr(self, table, None) is None:
                errmsg = f"cannot process company records without '{table}' table"
                raise AttributeError(errmsg)
        if self.industry:
            self.industry = self.types.get(
                self.type, self.industries.loc[self.industry]
            )
            subsector, sector = self.sectors.loc[self.industry]
            self.subsector = None if pd.isnull(subsector) else subsector
            self.sector = None if pd.isnull(sector) else sector
        return self

    @model_validator(mode="after")
    def postprocess_product(self) -> Self:
        # Always use 'galman' instead of 'zinc' in mines and 'zinc' in zinc mills
        if self.product == "galman" and "huta" in self.type.lower():
            self.product = "zinc"
        elif self.product == "zinc" and "kopalnia" in self.type.lower():
            self.product = "galman"
        return self

    @model_validator(mode="after")
    def postprocess_value(self) -> Self:
        for table in ("conversions", "prices"):
            if getattr(self, table, None) is None:
                errmsg = f"cannot calculate output values without '{table}' table"
                raise AttributeError(errmsg)
        self.value = calculate_value(
            output=self.output,
            product=self.product,
            unit=self.unit,
            year=self.year,
            prices=self.prices,
            conversions=self.conversions,
        )
        return self

    @model_validator(mode="after")
    def postprocess_dates(self) -> Self:
        for field in ("foundation", "public"):
            if (year := getattr(self, field, None)) and year > self.year:
                setattr(self, field, None)
        if self.public and self.foundation and self.public < self.foundation:
            self.public = None
        return self

    @model_validator(mode="after")
    def merge_company_ids(self) -> Self:
        if self.company_id in self.merging.index:
            self.company_id = self.merging.loc[self.company_id]
        return self

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> Self:
        """Construct from data frame."""
        data = dict(zip(["company_id", "record_id"], df.name, strict=True))
        data.update(
            df[
                [
                    "volume",
                    "year",
                    "name",
                    "type",
                    "industry",
                    "governorate",
                ]
            ]
            .agg(mode)
            .to_dict()
        )

        for _, row in df.iterrows():
            prop = row["property"]
            if pd.isnull(prop) or prop in data:
                continue
            if prop in _numeric_props:
                data[prop] = row["num_value"]
                if prop == "output":
                    for field in ("product", "unit"):
                        data[field] = row[field]
            elif prop in cls.model_fields:
                data[prop] = row["value"]

        return cls(**data)


# Utils ------------------------------------------------------------------------------


def calculate_value(
    output: float,
    product: str,
    unit: str,
    year: int,
    prices: pd.DataFrame,
    conversions: pd.DataFrame,
) -> float | None:
    """Calculate value (in rubles) of ``product`` ``output`` measured in ``units``.

    Parameters
    ----------
    output
        Numeric output value.
    product, unit, year
        Product, unit and year.
    prices, conversion
        Prices and conversion table.
    """
    if output is None:
        return None
    if product is None:
        if unit is None:
            unit = "ruble"
    elif product not in prices.index.get_level_values("product"):
        return None
    if unit == "ruble":
        return float(output)
    if (product, unit) in prices.index:
        price = float(prices.loc[(product, unit), year])
    else:
        measures = conversions.loc[(product, unit)].index.intersection(
            prices.loc[product].index
        )
        if measures.size <= 0:
            errmsg = (
                f"there is no conversion path to standard price for {(product, unit)}"
            )
            raise ValueError(errmsg)
        # if product in measures:
        measure = measures[0]
        output *= conversions.loc[(product, unit, measure)]
        price = float(prices.loc[(product, measure), year])
    value = output * price
    return float(value)


rx_addr_governorate = re.compile(r"(^|[,\s])gub.\s*([^,]*)([,\s]|$)", re.IGNORECASE)
rx_addr_county = re.compile(r"(^|[\s,])*pow\.\s*([^,]*)([,\s]|$)", re.IGNORECASE)
rx_addr_municipal = re.compile(r"(^|[\s,])\s*gm\.\s*([^,]*)([,\s]|$)", re.IGNORECASE)
rx_addr_city = re.compile(r"(^|[\s,])\s*m\.\s*([^,]*)([,.]|$)", re.IGNORECASE)
rx_addr_village = re.compile(r"(^|[\s,])\s*w\.\s*([^,]*)([,\s]|$)", re.IGNORECASE)
rx_addr_street = re.compile(r"(^|[\s,]+)ul\.\s*([^,]*)([,\s]|$)")
rx_addr_postal = re.compile(r"(^|[\s,])\s*poczta\s+([^,]*)([,\s]|$)", re.IGNORECASE)


def extract_address_details(address: str) -> dict[str, str]:
    """Extract details from an ``address`` string.

    Examples
    --------
    >>> addr = "gub. kielecka, pow. stok, poczta Ram"
    >>> extract_address_details(addr)
    {'governorate': 'kielecka', 'county': 'stok', 'postoffice': 'Ram'}
    >>> addr = "gub. warszawska, w. Nowa Jabłonna"
    >>> extract_address_details(addr)
    {'governorate': 'warszawska', 'locality': 'Nowa Jabłonna', 'is_city': False}
    >>> addr = "gm. Nora, m. Krany"
    >>> extract_address_details(addr)
    {'municipality': 'Nora', 'locality': 'Krany', 'is_city': True}
    """
    data = {}
    if match := rx_addr_governorate.search(address):
        data["governorate"] = match.group(2)
    if match := rx_addr_county.search(address):
        data["county"] = match.group(2)
    if match := rx_addr_municipal.search(address):
        data["municipality"] = match.group(2)
    if match := rx_addr_city.search(address):
        data["locality"] = match.group(2)
        data["is_city"] = True
    elif match := rx_addr_village.search(address):
        data["locality"] = match.group(2)
        data["is_city"] = False
    if match := rx_addr_street.search(address):
        data["street"] = match.group(2)
    if match := rx_addr_postal.search(address):
        data["postoffice"] = match.group(2)
    if (key := "is_city") in data:
        data[key] = data.pop(key)
    return data
