# %% ---------------------------------------------------------------------------------

import pandas as pd

from kingpol import params, paths
from kingpol.dataset import DataProc
from kingpol.dataset.models import Shares

# from bourgeoisie.ranking import comparisons, rank

# %% ---------------------------------------------------------------------------------

proc = DataProc(paths.proc)

# %% Relations -----------------------------------------------------------------------

relations = proc.relations.pipe(
    lambda df: df[df["relation"].isin(params.shares.relations)]
)

# %% Entity shares -------------------------------------------------------------------

entity_shares = (
    relations.groupby(["record_id", "entity_id"])
    .size()
    .reset_index(name="entity_shares")
    .merge(
        proc.records[["company_id", "record_id", "year"]],
        how="left",
        on="record_id",
    )
    .dropna(subset="company_id", ignore_index=True)
    .merge(proc.yearly[["company_id", "year"]], how="outer", on=["company_id", "year"])
    .groupby(["company_id", "entity_id"])
    .apply(lambda df: df.ffill(), include_groups=False)
    .reset_index(["company_id", "entity_id"])
    .reset_index(drop=True)
    .pipe(lambda df: df[df["year"].isin(params.years)])
    .reset_index(drop=True)
    .groupby(["company_id", "entity_id"])[["entity_shares"]]
    .sum()
    .reset_index()
)

# %% Company shares ------------------------------------------------------------------

company_shares = (
    entity_shares.groupby(["company_id"])["entity_shares"]
    .sum()
    .reset_index(name="n_shares")
)

# %% Proportional shares -------------------------------------------------------------

shares = (
    entity_shares.merge(company_shares, how="left", on="company_id")
    .assign(share=lambda df: df["entity_shares"] / df["n_shares"])
    .pipe(
        lambda df: pd.DataFrame(
            [Shares(**record).model_dump() for record in df.to_dict(orient="records")]
        )
    )
)

# %% Consistency tests ---------------------------------------------------------------

if params.test:
    assert shares["share"].gt(0).all()
    assert shares["share"].le(1).all()
    assert shares["share"].lt(1).any()

# %% ---------------------------------------------------------------------------------

proc.write.shares(shares)

# %% ---------------------------------------------------------------------------------
