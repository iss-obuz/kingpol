# %% ---------------------------------------------------------------------------------

from typing import ClassVar

import pandas as pd

from kingpol import params, paths
from kingpol.dataset import (
    CompanyProperty,
    DataAux,
    DataProc,
    DataRaw,
)

# %% ---------------------------------------------------------------------------------

aux = DataAux(paths.aux)
raw = DataRaw(paths.raw)
proc = DataProc(paths.proc)


class Property(CompanyProperty):
    volumes: ClassVar[pd.DataFrame] = aux.volumes
    currencies: ClassVar[pd.DataFrame] = proc.currencies
    units: ClassVar[pd.DataFrame] = aux.units


# %% ---------------------------------------------------------------------------------

properties = (
    raw.companies.pipe(
        lambda df: pd.DataFrame(
            {
                "company_id": df["troi"],
                "record_id": df["tro"],
            }
        )
    )
    .merge(
        raw.properties.pipe(
            lambda df: pd.DataFrame(
                {
                    "record_id": df["fabryka"],
                    "property_id": df["tro"],
                    "volume": df["tom"],
                    "key": df["klucz"],
                    "unit": df["jednostka"],
                    "value": df["wartosc"],
                    "num_value": df["wartnum"],
                    "confirmed": df["potwierdzone"].astype(bool),
                    "official": df["urzedowe"].astype(bool),
                }
            )
        ),
        how="left",
        on="record_id",
    )
    .query("property_id.notnull()")
    .merge(aux.properties, how="left", on="key")
    .merge(aux.inferred_units, how="left", on="key", suffixes=["", "_new"])
    .assign(unit=lambda df: df["unit"].combine_first(df.pop("unit_new")))[
        [
            "company_id",
            "record_id",
            "property_id",
            "volume",
            "property",
            "object",
            "value",
            "num_value",
            "unit",
            "desc1",
            "desc2",
            "confirmed",
            "official",
        ]
    ]
    .set_index(["company_id", "record_id", "property_id"])
    .pipe(lambda df: aux.corrections_properties.combine_first(df))
    .reset_index()
    .pipe(
        lambda df: pd.DataFrame(
            [Property(**record).model_dump() for record in df.to_dict("records")]
        )
    )
    .fillna(pd.NA)
    .convert_dtypes()
    .query("(property != 'capital') | num_value.notnull()")
    .query("(property != 'address') | (desc1 == 'company')")
    .sort_values(["record_id", "property", "num_value", "property_id"], ascending=False)
    .drop_duplicates(subset=["record_id", "property"], keep="first")
    .reset_index(drop=True)
)

# %% ---------------------------------------------------------------------------------

if params.test:
    # Check test cases
    check = properties.set_index("property_id")
    case1 = check.loc["f.2.73.5"]
    assert case1["desc1"] == "limestone@sążeń kubiczny"
    assert case1["product"] == "limestone"
    assert case1["unit"] == "cubic fathom"
    case2 = check.loc["f.1.1.6"]
    assert case2["desc1"] == "limestone"
    assert case2["product"] == "limestone"
    assert case2["unit"] == "cubic fathom"

# %% Consistency checks --------------------------------------------------------------

if params.test:
    assert not properties[["record_id", "property"]].duplicated().any()
    assert properties.query("property == 'capital'").unit.eq("ruble").all()
    assert (
        properties.query(
            "(property == 'output') & num_value.notnull() & unit.isnull()"
        ).size
    ) == 0
    assert properties.groupby(["record_id", "property"]).size().eq(1).all()
    assert properties.query("product.notnull() & unit.isnull()").size == 0

# %% ---------------------------------------------------------------------------------

proc.write.properties(properties)

# %% ---------------------------------------------------------------------------------
