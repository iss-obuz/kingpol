from functools import cached_property

import pandas as pd

from .paths import PathsRaw
from .utils import read_tsv


class DataRaw:
    """Raw data manager.

    Attributes
    ----------
    properties
        Companies' properties data.
    """

    def __init__(self, paths: PathsRaw) -> None:
        self.paths = paths

    @cached_property
    def properties(self) -> pd.DataFrame:
        return read_tsv(self.paths.properties)

    @cached_property
    def companies(self) -> pd.DataFrame:
        data = read_tsv(self.paths.companies)
        return data

    @cached_property
    def relations(self) -> pd.DataFrame:
        return read_tsv(self.paths.relations)

    @cached_property
    def entities(self) -> pd.DataFrame:
        return _makeentities(self.paths)


# Internals --------------------------------------------------------------------------


def _makeentities(paths: PathsRaw) -> pd.DataFrame:
    columns = [
        "entity_id",
        "sex",
        "name",
        "name2",
        "name3",
        "surname",
        "birth_estim_year",
        "death_estim_year",
        "birth_day",
        "birth_month",
        "birth_year",
        "birth_datetext",
        "birth_place",
        "baptism_day",
        "baptism_month",
        "baptism_year",
        "baptism_datetext",
        "baptism_place",
        "death_day",
        "death_month",
        "death_year",
        "death_datetext",
        "death_place",
        "burial_day",
        "burial_month",
        "burial_year",
        "burial_datetext",
        "burial_place",
    ]
    return (
        read_tsv(paths.entities, names=columns)
        .query("entity_id.notnull()")
        .reset_index(drop=True)
    )
