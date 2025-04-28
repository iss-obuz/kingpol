# %% ---------------------------------------------------------------------------------

import numpy as np
import pandas as pd

from kingpol import params, paths
from kingpol.dataset import Company, DataProc
from kingpol.outliers import rank_outliers
from kingpol.stats import mode

# %% ---------------------------------------------------------------------------------

proc = DataProc(paths.proc)

# %% ---------------------------------------------------------------------------------

cols_mode = [
    "type",
    "industry",
    "subsector",
    "sector",
    "product",
    "address",
    "governorate",
]
cols_time = ["foundation", "public"]
cols_numeric = ["value", "employment", "productivity"]

companies = (
    proc.yearly.pipe(lambda df: df[df["year"].isin(params.years)])
    .groupby(["company_id"])
    .agg(
        {
            "name": lambda x: x.iloc[-1],
            **dict.fromkeys(cols_mode, mode),
            **dict.fromkeys(cols_time, "min"),
            **dict.fromkeys(cols_numeric, "mean"),
        }
    )
    .reset_index(drop=False)
    .pipe(lambda df: df.groupby(["industry"])[df.columns])
    .apply(
        lambda df: df.assign(
            outlier_rank=rank_outliers(
                df["productivity"],
                threshold=params.companies.outliers.threshold,
            )
        )
    )
    .sort_values(["outlier_rank", "employment"], ascending=[True, False])
    .reset_index(drop=True)
    .assign(
        elite=lambda df: (
            df["value"].ge(params.elite.min_value)
            | df["employment"].ge(params.elite.min_employment)
        )
        .fillna(False)
        .astype(int)
    )
    .query("outlier_rank == 0")
    .reset_index(drop=True)
    .drop(columns="outlier_rank")
    .pipe(lambda df: pd.Series([Company(**r) for r in df.to_dict(orient="records")]))
    .map(Company.model_dump)
    .pipe(lambda s: pd.DataFrame(s.tolist()))
    .convert_dtypes()
)

# %% Check test cases ----------------------------------------------------------------

if params.test:
    check = companies.set_index("company_id")
    record = check.loc["f.1.3259.1"]
    assert np.allclose(
        record[["value", "employment", "productivity"]],
        [7000000.0, 5887.5, 1193.663912],
    )


# %% ---------------------------------------------------------------------------------

proc.write.companies(companies)

# %% ---------------------------------------------------------------------------------
