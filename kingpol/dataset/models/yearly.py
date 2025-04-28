from typing import Any, Self

import pandas as pd
from pydantic import BaseModel, model_validator

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
    Unit,
    Year,
)
from kingpol.stats import mode


class CompanyYearlyRecord(BaseModel):
    """Yearly records are obtained by aggregating all simple records associated with
    the same company within the same year.

    The compilation of the table depends on the following parameter groups
    in the ``params.yaml`` file:

    * ``yearly`` - parameters specific to yearly records table.
      They can be used to specify outlier detection thresholds
      as well as top-level economy sectors to be included in the table,
      and as a result in all downstream tables.
    """

    company_id: CompanyId.T = CompanyId.field
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

    @model_validator(mode="before")
    def preprocess(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in data.items() if not pd.isnull(v)}

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> Self:
        """Construct from dataframe."""
        data = dict(zip(["company_id", "year"], df.name, strict=True))
        data["name"] = "; ".join(df["name"].unique())
        data.update(
            df[
                [
                    "type",
                    "industry",
                    "subsector",
                    "sector",
                    "address",
                    "governorate",
                    "product",
                    "unit",
                ]
            ]
            .agg(mode)
            .to_dict()
        )
        data.update(df[["foundation", "public"]].min().to_dict())
        data.update(
            df[["value", "employment", "output"]].sum().replace(0, pd.NA).to_dict()
        )
        mask = df[["value", "employment"]].notnull().all(axis=1)
        if mask.any():
            data["productivity"] = (
                df.loc[mask, ["value", "employment"]]
                .sum()
                .pipe(lambda s: s["value"] / s["employment"])
            )
        else:
            data["productivity"] = pd.NA

        return cls(**data)
