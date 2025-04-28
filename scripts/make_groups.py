# %% ---------------------------------------------------------------------------------

import pandas as pd

from kingpol import paths
from kingpol.dataset import DataProc
from kingpol.dataset.models import Group

# %% ---------------------------------------------------------------------------------

proc = DataProc(paths.proc)

# %% ---------------------------------------------------------------------------------

groups = (
    proc.ranking[["entity_id", "fullname", "elite"]]
    .merge(
        proc.shares[["entity_id", "share", "company_id"]], how="left", on="entity_id"
    )
    .merge(proc.companies, how="left", on="company_id", suffixes=("", "_company"))
    .dropna(subset="name", ignore_index=True)
    .rename(columns={"name": "company_name", "elite_company": "company_elite"})
    .pipe(
        lambda df: pd.DataFrame(
            [Group(**record).model_dump() for record in df.to_dict(orient="records")]
        )
    )
)

# %% ---------------------------------------------------------------------------------

proc.write.groups(groups)

# %% ---------------------------------------------------------------------------------
