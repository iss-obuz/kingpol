# %% ---------------------------------------------------------------------------------

from typing import ClassVar

import numpy as np
import pandas as pd

from kingpol import params, paths
from kingpol.dataset import (
    CompanyRecord,
    DataAux,
    DataProc,
    DataRaw,
)
from kingpol.outliers import rank_outliers

# %% ---------------------------------------------------------------------------------

aux = DataAux(paths.aux)
raw = DataRaw(paths.raw)
proc = DataProc(paths.proc)


class Record(CompanyRecord):
    prices: ClassVar[pd.DataFrame] = proc.prices
    conversions: ClassVar[pd.DataFrame] = proc.conversions
    industries: ClassVar[pd.DataFrame] = aux.industries
    sectors: ClassVar[pd.DataFrame] = aux.sectors
    types: ClassVar[pd.DataFrame] = aux.types
    merging: ClassVar[pd.DataFrame] = aux.merging_companies


# %% ---------------------------------------------------------------------------------

records = (
    raw.companies.pipe(
        lambda df: pd.DataFrame(
            {
                "company_id": df["troi"],
                "record_id": df["tro"],
                "volume": df["tom"],
                "year": df["tom"].map(aux.volumes),
                "name": df["nazwa"],
                "type": df["typ"],
                "industry": df["branza"],
                "governorate": df["gubernia"],
            }
        )
    )
    .set_index("record_id")
    .pipe(lambda df: aux.inferred_types.combine_first(df))
    .reset_index()
    .merge(
        proc.properties.drop(columns=["property_id", "volume", "year"]),
        how="left",
        on=["company_id", "record_id"],
    )
    .merge(
        aux.inferred_products.reset_index(),
        how="left",
        on="type",
        suffixes=["", "_new"],
    )
    .assign(product=lambda df: df.pop("product_new").combine_first(df["product"]))
    .query("name.notnull()")
    .groupby(["company_id", "record_id"])
    .apply(Record.from_dataframe, include_groups=False)
    .map(lambda record: record.model_dump())
    .pipe(lambda s: pd.DataFrame(s.tolist()))
    .fillna(pd.NA)
    .convert_dtypes()
    .reset_index(drop=True)
    .set_index("record_id")
    .pipe(lambda df: aux.corrections_records.combine_first(df))
    .reset_index()
    .assign(productivity=lambda df: df["value"] / df["employment"])
    .convert_dtypes()[[*Record.model_fields]]
    .pipe(
        lambda df: df[
            df["governorate"].pipe(
                lambda s: s.isnull() | s.isin(params.records.governorates)
            )
        ]
    )
    .query("industry.ne('other')")
    .reset_index(drop=True)
)

# %% Consistency tests ---------------------------------------------------------------

if params.test:
    assert not records["record_id"].duplicated().any()
    assert records.query("product.notnull() & unit.isnull()").size == 0
    assert (records.query("product.isnull() & unit.notnull()")["unit"] == "ruble").all()
    assert records.query("output.notnull() & unit.isnull()").size == 0
    for col in ("output", "employment", "value"):
        assert records[col].pipe(lambda s: s.isnull() | (s > 0)).all()
    assert records.query("output.isnull()")["value"].isnull().all()
    assert records.query("output.notnull() & value.isnull()").size == 0
    assert np.isfinite(records["productivity"]).all()
    assert (
        records.query("value.isnull() | employment.isnull()")["productivity"]
        .isnull()
        .all()
    )
    assert (
        records.query("value.notnull() & employment.notnull()")["productivity"]
        .notnull()
        .all()
    )

    assert records["industry"].notnull().all()
    assert records["subsector"].notnull().all()
    assert records["sector"].notnull().all()

    for field in ("foundation", "public"):
        assert (records[field].isnull() | records[field].le(records["year"])).all()
    assert (
        records["foundation"].isnull()
        | records["public"].isnull()
        | records["foundation"].le(records["public"])
    ).all()

# %% Check specific cases ------------------------------------------------------------

if params.test:
    check = records.set_index("record_id")
    assert check.at["f.2.1276.1", "value"] == 2900

# %% Value & employment information availability by industry -------------------------

industries = (
    records.groupby(["industry"])[["value", "employment"]]
    .apply(lambda df: df.notnull().all(axis=1).mean())
    .sort_values(ascending=False)
    .to_frame("complete")
    .reset_index()
)
min_complete = params.records.industries.min_complete

# %% Rank outliers (by industry) -----------------------------------------------------

records = (
    records.reset_index(drop=True)
    .pipe(lambda df: df.groupby(["industry"])[df.columns])
    .apply(
        lambda df: df.assign(
            outlier_rank=(
                rank_outliers(
                    df["productivity"],
                    threshold=params.records.outliers.threshold,
                )
                if df["productivity"].notnull().mean() >= min_complete
                else pd.NA
            )
        )
    )
    .reset_index(drop=True)
)

# %% ---------------------------------------------------------------------------------

proc.write.records(records)
proc.write.industries(industries)

# %% ---------------------------------------------------------------------------------
