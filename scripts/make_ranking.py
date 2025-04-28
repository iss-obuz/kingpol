# %% ---------------------------------------------------------------------------------

import numpy as np
import pandas as pd

from kingpol import params, paths
from kingpol.dataset import DataProc, EntityRanking

# from bourgeoisie.ranking import comparisons, rank

# %% ---------------------------------------------------------------------------------

proc = DataProc(paths.proc)

# %% Ranking -------------------------------------------------------------------------


def productivity(prod: pd.Series, emp: pd.Series) -> float:
    """Compute productivity."""
    return ((prod * emp).sum() / emp.sum()) if prod.notnull().any() else np.nan


ranking = (
    proc.shares.merge(proc.companies, how="left", on="company_id")
    .groupby(["entity_id"])
    .apply(
        lambda df: pd.Series(
            {
                "value_share": (df["value"] * df["share"]).sum(),
                "employment_share": (df["employment"] * df["share"]).sum(),
                "value_total": df["value"].sum(),
                "employment_total": df["employment"].sum(),
                "productivity": productivity(df["productivity"], df["employment"]),
            }
        ),
        include_groups=False,
    )
    .reset_index()
    .replace({0: pd.NA})
    .fillna(pd.NA)
    .pipe(lambda df: proc.entities.merge(df, how="left", on="entity_id"))[
        [
            "entity_id",
            "fullname",
            "physical",
            "legal",
            "surname",
            "name",
            "sex",
            "birth_year",
            "death_year",
            "title_noble",
            "title_other",
            "value_share",
            "employment_share",
            "value_total",
            "employment_total",
            "productivity",
        ]
    ]
    .query("value_share.notnull() | employment_share.notnull()")
    .sort_values("value_share", ascending=False, ignore_index=True)
    .assign(
        elite=lambda df: (
            df["value_share"].ge(params.elite.min_value)
            | df["employment_share"].ge(params.elite.min_employment)
        )
        .fillna(False)
        .astype(int)
    )
    .pipe(lambda df: pd.Series([EntityRanking(**r) for r in df.to_dict("records")]))
    .map(EntityRanking.model_dump)
    .pipe(lambda s: pd.DataFrame(s.tolist()))
    .query("physical or legal")
    .reset_index(drop=True)
    .convert_dtypes()
)

# %% Test cases ----------------------------------------------------------------------

if params.test:
    # Use Kleniewski's employment as check
    check = ranking.set_index("entity_id")
    assert check.at["10.224.132", "employment_total"] < 8000

# %% Compute Iterative Luce Spectral Ranking -----------------------------------------

# opts = params["ranking"]
# X = ranking[opts["use"]].to_numpy()
# X[pd.isnull(X)] = np.nan
# X = X.astype(float)
# C = comparisons(*X.T)
# R = rank(C, **opts["latent"])

# idx = ranking.columns.tolist().index("value")
# ranking.insert(idx, "latent", np.exp(R))
# ranking.sort_values(opts["sortby"], ascending=False, ignore_index=True, inplace=True)

# %% ---------------------------------------------------------------------------------

proc.write.ranking(ranking)

# %% ---------------------------------------------------------------------------------
