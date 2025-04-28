# ruff: noqa: S101

from functools import cached_property

import pandas as pd

from .paths import PathsAux
from .utils import read_excel


class DataAux:
    """Auxiliary (meta)data manager.

    Attributes
    ----------
    Properties
        Property definitions.
    corrections
        Arbitrary corrections applied to the raw companies props data.
    types
        Data about inferred industry types.
    units
        Data about inferred reported units of production.
    products
        Data about inferred reported products.
    volumes
        Map from volume numbers to years.
    """

    def __init__(self, paths: PathsAux) -> None:
        self.paths = paths

    @cached_property
    def properties(self) -> pd.DataFrame:
        data = (
            read_excel(self.paths.properties, sheet_name="properties")
            .query("object.notnull()")
            .set_index("key")
        )
        assert len(data) == data.index.nunique()
        return data

    @cached_property
    def inferred_types(self) -> pd.DataFrame:
        data = read_excel(self.paths.properties, sheet_name="inferred types")
        return data.set_index("record_id")

    @cached_property
    def inferred_units(self) -> pd.DataFrame:
        data = read_excel(self.paths.properties, sheet_name="inferred units")
        return data.set_index("key")

    @cached_property
    def inferred_products(self) -> pd.DataFrame:
        data = read_excel(
            self.paths.properties, sheet_name="inferred products"
        ).drop_duplicates()
        return data.set_index("type")

    @cached_property
    def volumes(self) -> pd.DataFrame:
        return read_excel(self.paths.properties, sheet_name="volumes").set_index(
            "volume"
        )["year"]

    @cached_property
    def sectors(self) -> pd.DataFrame:
        return read_excel(self.paths.properties, sheet_name="sectors").set_index(
            "industry"
        )

    @cached_property
    def industries(self) -> pd.DataFrame:
        return read_excel(self.paths.properties, sheet_name="industries").set_index(
            "key"
        )["industry"]

    @cached_property
    def types(self) -> pd.DataFrame:
        return read_excel(self.paths.properties, sheet_name="types").set_index("type")[
            "industry"
        ]

    @cached_property
    def units(self) -> pd.DataFrame:
        return read_excel(self.paths.prices, sheet_name="units").set_index("key")[
            "unit"
        ]

    @cached_property
    def prices(self) -> pd.DataFrame:
        return (
            read_excel(self.paths.prices, sheet_name="prices")
            .assign(product=lambda df: df["product"].ffill())
            .set_index(["product", "unit"])
            .pipe(lambda df: df.mul(df.pop("multiplier"), axis=0))
            .T.ffill()
            .bfill()
            .T
        )

    @cached_property
    def conversions(self) -> pd.DataFrame:
        return (
            read_excel(self.paths.prices, sheet_name="conversions")
            .assign(measure=lambda df: df["measure"].ffill())
            .set_index(["measure", "unit", "standard"])["rate"]
        )

    @cached_property
    def masses(self) -> pd.DataFrame:
        return read_excel(self.paths.prices, sheet_name="masses").set_index("product")[
            "kg_per_m3"
        ]

    @cached_property
    def currencies(self) -> pd.DataFrame:
        return read_excel(self.paths.prices, sheet_name="currencies").set_index(
            "currency"
        )

    @cached_property
    def corrections_properties(self) -> pd.DataFrame:
        data = (
            read_excel(self.paths.corrections, sheet_name="properties")
            .set_index(["property_id", "record_id"])
            .assign(
                value=lambda df: df["value"].astype(str),
                confirmed=lambda df: df["confirmed"].astype(bool),
            )
        )
        assert data.index.is_unique
        return data

    @cached_property
    def corrections_records(self) -> pd.DataFrame:
        data = read_excel(self.paths.corrections, sheet_name="records").set_index(
            ["record_id"]
        )
        assert data.index.is_unique
        return data

    @cached_property
    def corrections_entities(self) -> pd.DataFrame:
        data = (
            read_excel(self.paths.corrections, sheet_name="entities")
            .set_index(["entity_id"])
            .assign(
                physical=lambda df: df["physical"].astype(bool),
                legal=lambda df: df["legal"].astype(bool),
            )
        )
        assert data.index.is_unique
        return data

    @cached_property
    def corrections_entity_ids(self) -> dict[str, str]:
        data = read_excel(self.paths.corrections, sheet_name="entity_id")
        assert data["from"].is_unique
        return data.pipe(lambda df: dict(zip(df["from"], df["to"], strict=True)))

    @cached_property
    def drop_record_ids(self) -> dict[str, str]:
        return read_excel(self.paths.corrections, sheet_name="drop_records")[
            "record_id"
        ].to_numpy()

    @cached_property
    def merging_companies(self) -> pd.DataFrame:
        data = read_excel(self.paths.merging, sheet_name="companies")
        recs = data.columns[data.columns.str.match(r"^R\d+")]
        recs = [
            sorted([x for x in rec if not pd.isnull(x)], reverse=True)
            for rec in data.loc[:, recs].to_numpy()
        ]
        data = (
            pd.DataFrame(
                {
                    "source": [r[1:] for r in recs],
                    "target": [r[0] for r in recs],
                }
            )
            .explode("source")
            .groupby("source")["target"]
            .max()
        )
        return data
