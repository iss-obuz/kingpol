# %% ---------------------------------------------------------------------------------

import numpy as np
import pandas as pd

from kingpol import params, paths
from kingpol.dataset import CompanyYearlyRecord, DataAux, DataProc
from kingpol.outliers import rank_outliers

# %% ---------------------------------------------------------------------------------

aux = DataAux(paths.aux)
proc = DataProc(paths.proc)

# %% ---------------------------------------------------------------------------------

yearly = (
    proc.records.query("outlier_rank.notnull() & outlier_rank.eq(0)")
    .pipe(lambda df: df[~df["record_id"].isin(aux.drop_record_ids)])
    .pipe(lambda df: df[df["sector"].isin(params.yearly.sectors)])
    .reset_index(drop=True)
    .groupby(["company_id", "year"])
    .apply(CompanyYearlyRecord.from_dataframe, include_groups=False)
    .map(lambda record: record.model_dump())
    .pipe(lambda s: pd.DataFrame(s.tolist()))
    .fillna(pd.NA)
    .convert_dtypes()
    .reset_index(drop=True)
    .pipe(lambda df: df.groupby(["industry"])[df.columns])
    .apply(
        lambda df: df.assign(
            outlier_rank=rank_outliers(
                df["productivity"],
                threshold=params.yearly.outliers.threshold,
            )
        )
    )
    .sort_values(["outlier_rank", "company_id", "year"], ascending=True)
    .query("outlier_rank == 0")
    .reset_index(drop=True)
    .groupby("company_id")
    .apply(
        lambda df: df.assign(
            year_first=df["year"].min().astype(int),
            year_last=df["year"].max().astype(int),
        ),
        include_groups=False,
    )
    .reset_index("company_id", drop=False)
    .reset_index(drop=True)
)

# %% Prepare time grid ---------------------------------------------------------------

timegrid = (
    yearly[["company_id"]]
    .drop_duplicates()
    .assign(
        year=lambda df: [np.arange(aux.volumes.min(), aux.volumes.max() + 1)] * len(df)
    )
    .explode("year")
)

# %% Re-grid -------------------------------------------------------------------------

yearly = (
    yearly.pipe(lambda df: pd.Series(df.to_dict("records")))
    .map(CompanyYearlyRecord.model_validate)
    .pipe(
        lambda s: pd.DataFrame(
            {
                "company_id": [record.company_id for record in s],
                "year": [record.year for record in s],
                "record": s,
            }
        )
    )
    .pipe(lambda df: timegrid.merge(df, how="left", on=["company_id", "year"]))
    .groupby("company_id")
    .apply(
        lambda df: df.infer_objects(copy=False).ffill().bfill(), include_groups=False
    )
    .reset_index("company_id", drop=False)
    .dropna(subset=["record"], ignore_index=True)
    .set_index(["company_id", "year"])["record"]
    .map(CompanyYearlyRecord.model_dump)
    .pipe(lambda s: pd.DataFrame(s.tolist(), index=s.index))
    .drop(columns=["company_id", "year"])
    .reset_index(drop=False)
    .dropna(subset=["name"], ignore_index=True)
    .fillna(pd.NA)
    .convert_dtypes()
    .query("foundation.isnull() | year.ge(foundation)")
    .reset_index(drop=True)
)

# %% Check consistency ---------------------------------------------------------------

if params.test:
    assert (
        yearly["foundation"].isnull() | yearly["year"].ge(yearly["foundation"])
    ).all()

# %% Check test cases ----------------------------------------------------------------

if params.test:
    grid = timegrid[["year"]].drop_duplicates(ignore_index=True)
    check = yearly.set_index("company_id")

    # %% Zawiercie
    # ============
    data = check.loc[["f.1.3259.1"]].reset_index(drop=True)
    assert data["year"].eq(grid["year"]).all()

    x = data["value"]
    y = [6000000.0] + [7000000.0] * 5 + [8000000.0, None]
    assert x.eq(y).all()

    x = data["employment"]
    y = [5000.0, 6000.0, 6000.0, 6000.0, 6050.0, 6050.0, 6050.0, 6050.0]
    x.eq(y).all()

    x = data["productivity"].fillna(np.nan).to_numpy()
    y = np.array([1200.0] + [1166.6666666666667] * 5 + [1322.314049586777, np.nan])
    assert np.isclose(x, y, equal_nan=True).all()

    # %%  Biała
    # =========
    data = check.loc[["f.7.96.1"]].reset_index(drop=True)
    assert data["year"].eq(grid["year"]).all()
    assert np.allclose(data["value"], [2138.043359])
    assert data["employment"].eq(2).all()
    assert np.allclose(data["productivity"], [1069.0216795])

# %% ---------------------------------------------------------------------------------

proc.write.yearly(yearly)

# %% ---------------------------------------------------------------------------------
