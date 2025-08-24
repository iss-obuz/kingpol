# %% ---------------------------------------------------------------------------------

import inspect
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

from kingpol.dataset import models
from kingpol.strings import normalize_docstring

root = Path(__file__).parent.parent.absolute()
codebook_path = root / "CODEBOOK.md"

# %% ---------------------------------------------------------------------------------

# %% ---------------------------------------------------------------------------------

content = """
---
lang: en-US
---

# Codebook

> [!NOTE]
> Access online version [here](https://github.com/iss-obuz/kingpol/blob/master/CODEBOOK.md)

This codebook provides a detailed description of the table and table fields included
in the ``KINGPOL_INDUSTRY`` database. A general discussion of the database is provided
in the ``README.md`` file.

## Tables
""".strip()

# %%  --------------------------------------------------------------------------------

for name, model in inspect.getmembers(models, inspect.isclass):
    if issubclass(model, BaseModel):
        content += f"\n\n### {name}\n\n"
        content += f"{normalize_docstring(model.__doc__)}\n\n"
        schema = pd.DataFrame(
            [
                {"label": name, "field": field.title, "description": field.description}
                for name, field in model.model_fields.items()
            ]
        )
        schema["description"] = schema["description"].str.wrap(60)
        content += schema.to_markdown(index=True).strip()

# %% ---------------------------------------------------------------------------------

with codebook_path.open("w") as fh:
    fh.write(content.strip() + "\n")

# %% ---------------------------------------------------------------------------------
