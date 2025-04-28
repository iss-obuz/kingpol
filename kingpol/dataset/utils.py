from pathlib import Path
from typing import Any

import pandas as pd

# Read method s-----------------------------------------------------------------------


def read_tsv(path: str | Path, *args: Any, **kwargs: Any) -> pd.DataFrame:
    return pd.read_csv(path, *args, **{"sep": "\t", "na_values": r"\N", **kwargs})


def read_excel(
    path: str | Path, *args: Any, index_col=None, **kwargs: Any
) -> pd.DataFrame:
    return pd.read_excel(path, *args, index_col=index_col, **kwargs)


def read_parquet(path: str | Path, *args: Any, **kwargs: Any) -> pd.DataFrame:
    return pd.read_parquet(path, *args, **kwargs)


# Write methods ----------------------------------------------------------------------


def write_parquet(df: pd.DataFrame, path: str | Path, **kwargs: Any) -> None:
    df.to_parquet(
        path=path,
        **{
            "compression": "zstd",
            "compression_level": 9,
            "engine": "pyarrow",
            **kwargs,
        },
    )
