# %% ---------------------------------------------------------------------------------

import pandas as pd

from kingpol import params, paths
from kingpol.dataset import DataAux, DataProc, DataRaw, Entity

# %% ---------------------------------------------------------------------------------

aux = DataAux(paths.aux)
raw = DataRaw(paths.raw)
proc = DataProc(paths.proc)

# %% ---------------------------------------------------------------------------------

entities = (
    raw.relations.pipe(
        lambda df: pd.DataFrame(
            {
                "entity_id": df["troio"],
                "name": df["i"],
                "surname": df["n"],
                "fullname": df["kto"],
                "title_noble": df["aryst"],
                "title_other": df["reszta"],
            }
        )
    )
    .drop_duplicates()
    .merge(
        raw.entities.drop(columns=["name", "surname"]),
        how="outer",
        on="entity_id",
    )
    .assign(entity_id=lambda df: df["entity_id"].replace(aux.corrections_entity_ids))
    .groupby(["entity_id"])
    .apply(Entity.from_dataframe, include_groups=False)
    .map(Entity.model_dump)
    .pipe(lambda s: pd.DataFrame(s.tolist()))
    .set_index(["entity_id"])
    .pipe(lambda df: aux.corrections_entities.combine_first(df))
    .reset_index()
    .convert_dtypes()
    .fillna(pd.NA)[list(Entity.model_fields)]
)

# %% Test consistency ----------------------------------------------------------------

if params.test:
    assert entities["entity_id"].is_unique
    for which in ("birth", "death", "baptism", "burial"):
        col = which + "_year"
        mask = entities[col].isnull() | (entities[col] >= 1750)
        col = which + "_month"
        mask = entities[col].isnull() | entities[col].between(1, 12)
        col = which + "_day"
        mask = entities[col].isnull() | entities[col].between(1, 31)
        assert mask.all()


# %% ---------------------------------------------------------------------------------

proc.write.entities(entities)

# %% ---------------------------------------------------------------------------------
