from collections.abc import Callable
from functools import cached_property
from typing import Any

import pandas as pd

from .paths import PathsProc
from .utils import read_parquet, write_parquet


class DataProc:
    """Processed data files manager.

    Attributes
    ----------
    properties
        Company properties dataset.
    """

    class ParquetWriter:
        def __init__(self, paths: PathsProc) -> None:
            self.paths = paths

        def __getattr__(self, name: str) -> Callable[[pd.DataFrame, ...], None]:
            if path := getattr(self.paths, name, None):

                def writer(data: pd.DataFrame, *args: Any, **kwargs: Any) -> None:
                    return write_parquet(data, path, *args, **kwargs)

                return writer
            errmsg = f"'{self.__class__.__name__}' object has not '{name}' attribute"
            raise AttributeError(errmsg)

    def __init__(self, paths: PathsProc) -> None:
        self.paths = paths

    @property
    def write(self) -> ParquetWriter:
        return self.ParquetWriter(self.paths)

    @cached_property
    def properties(self) -> pd.DataFrame:
        return read_parquet(self.paths.properties)

    @cached_property
    def records(self) -> pd.DataFrame:
        return read_parquet(self.paths.records)

    @cached_property
    def yearly(self) -> pd.DataFrame:
        return read_parquet(self.paths.yearly)

    @cached_property
    def companies(self) -> pd.DataFrame:
        return read_parquet(self.paths.companies)

    @cached_property
    def entities(self) -> pd.DataFrame:
        return read_parquet(self.paths.entities)

    @cached_property
    def relations(self) -> pd.DataFrame:
        return read_parquet(self.paths.relations)

    @cached_property
    def shares(self) -> pd.DataFrame:
        return read_parquet(self.paths.shares)

    @cached_property
    def ranking(self) -> pd.DataFrame:
        return read_parquet(self.paths.ranking)

    @cached_property
    def groups(self) -> pd.DataFrame:
        return read_parquet(self.paths.groups)

    @cached_property
    def conversions(self) -> pd.DataFrame:
        return read_parquet(self.paths.conversions).set_index(
            ["product", "unit", "measure"]
        )["rate"]

    @cached_property
    def prices(self) -> pd.DataFrame:
        data = read_parquet(self.paths.prices).pivot(
            index=["product", "unit"],
            columns="year",
            values="price",
        )
        return data

    @cached_property
    def currencies(self) -> pd.DataFrame:
        return read_parquet(self.paths.currencies).pivot(
            index="currency", columns="year", values="rate"
        )

    @cached_property
    def industries(self) -> pd.DataFrame:
        data = read_parquet(self.paths.industries).set_index("industry")
        return data
