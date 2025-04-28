# %% ---------------------------------------------------------------------------------

import pandas as pd

from kingpol import params, paths
from kingpol.dataset import (
    DataAux,
    DataProc,
    DataRaw,
    Relation,
)

# %% ---------------------------------------------------------------------------------

aux = DataAux(paths.aux)
raw = DataRaw(paths.raw)
proc = DataProc(paths.proc)

# %% ---------------------------------------------------------------------------------

relations = (
    raw.relations.pipe(
        lambda df: pd.DataFrame(
            {
                "entity_id": df["troio"].replace(aux.corrections_entity_ids),
                "record_id": df["fabryka"],
                "relation": df["klucz"],
            }
        )
    )
    .pipe(
        lambda df: pd.DataFrame(
            [Relation(**d).model_dump() for d in df.to_dict("records")]
        )
    )
    .drop_duplicates()
)

# %% Test consistency ----------------------------------------------------------------

if params.test:
    assert relations.set_index(["entity_id", "record_id", "relation"]).index.is_unique
    assert relations.notnull().all().all()

# %% ---------------------------------------------------------------------------------

proc.write.relations(relations)

# %% ---------------------------------------------------------------------------------
