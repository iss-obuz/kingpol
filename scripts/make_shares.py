# %% ---------------------------------------------------------------------------------

import numpy as np

from kingpol import params, paths
from kingpol.dataset import DataProc

# from bourgeoisie.ranking import comparisons, rank

# %% ---------------------------------------------------------------------------------

proc = DataProc(paths.proc)

# %% Relations -----------------------------------------------------------------------

relations = proc.relations.pipe(
    lambda df: df[df["relation"].isin(params.shares.relations)]
)

# %% Company shares ------------------------------------------------------------------

company_shares = (
    relations.merge(
        proc.records[["company_id", "record_id", "year"]], how="left", on="record_id"
    )
    .dropna(ignore_index=True)
    .groupby(["company_id", "year"])
    .size()
    .reset_index(name="n_shares")
    .merge(proc.yearly[["company_id", "year"]], how="outer", on=["company_id", "year"])
    .assign(reports=lambda df: df["n_shares"].notnull())
    .groupby(["company_id"])
    .apply(lambda df: df.ffill().bfill(), include_groups=False)
    .reset_index(["company_id"])
    .dropna(ignore_index=True)
    .assign(n_shares=lambda df: df["n_shares"].astype(int))
)

# %% Entity shares -------------------------------------------------------------------


year_ranges = (
    proc.yearly[["company_id", "year"]]
    .groupby("company_id")["year"]
    .agg(["min", "max"])
    .reset_index()
)

possible_relations = (
    relations.merge(
        proc.records[["company_id", "record_id", "year"]], how="left", on="record_id"
    )[["entity_id", "company_id"]]
    .dropna()
    .drop_duplicates(ignore_index=True)
    .merge(year_ranges, how="left", on="company_id")
    .dropna(ignore_index=True)
    .assign(
        year=lambda df: (df.apply(lambda r: np.arange(r["min"], r["max"] + 1), axis=1))
    )
    .drop(columns=["min", "max"])
    .explode("year", ignore_index=True)
)

assert (
    possible_relations.groupby(["entity_id", "company_id"])["year"].min().gt(1904).any()
), "All starting years are equal to 1904, which is suspicious."

# %% ---------------------------------------------------------------------------------

shares = (
    relations.merge(
        proc.records[["company_id", "record_id", "year"]], how="left", on="record_id"
    )
    .groupby(["entity_id", "company_id", "year"])
    .size()
    .reset_index(name="entity_shares")
    .merge(possible_relations, how="right", on=["entity_id", "company_id", "year"])
    .sort_values(["entity_id", "company_id", "year"], ascending=True, ignore_index=True)
    .merge(company_shares, how="left", on=["company_id", "year"])
    .assign(
        entity_shares=lambda df: np.where(
            df["entity_shares"].isnull() & df["reports"], 0, df["entity_shares"]
        )
    )
    .groupby(["entity_id", "company_id"])
    .apply(
        lambda df: df.assign(
            entity_shares=lambda d: d["entity_shares"].ffill().bfill()
        ),
        include_groups=False,
    )
    .reset_index(["entity_id", "company_id"])
    .query("entity_shares.notnull() & entity_shares > 0")
    .reset_index(drop=True)
    .drop(columns=["reports"])
    .assign(
        entity_shares=lambda df: df["entity_shares"].astype(int),
        share=lambda df: df["entity_shares"] / df["n_shares"],
    )
    .convert_dtypes()
)

# %% Consistency tests ---------------------------------------------------------------

if params.test:
    assert shares["share"].gt(0).all()
    assert shares["share"].le(1).all()
    assert shares["share"].lt(1).any()

# %% ---------------------------------------------------------------------------------

proc.write.shares(shares)

# %% ---------------------------------------------------------------------------------
