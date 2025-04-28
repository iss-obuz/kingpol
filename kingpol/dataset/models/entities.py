import re
from typing import Any, Self

import pandas as pd
from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
)

from kingpol.dataset.fields import (
    EntityBiographicalEventDay,
    EntityBiographicalEventMonth,
    EntityBiographicalEventYear,
    EntityFullName,
    EntityId,
    EntityIsLegal,
    EntityIsPhysical,
    EntityName,
    EntitySex,
    EntitySurname,
    EntityTitleNoble,
    EntityTitleOther,
)

rx_titles = {
    "engineer": re.compile(r"in[zż]|budow", re.IGNORECASE),
    "scholar": re.compile(r"dr\.?\b|mgr|magist|prof", re.IGNORECASE),
    "technician": re.compile(r"techn", re.IGNORECASE),
    "chemist": re.compile(r"chemi|farmac", re.IGNORECASE),
    "lawyer": re.compile(r"radc|adw", re.IGNORECASE),
    "cleric": re.compile(r"ksi[aą]d|kanoni|duchow", re.IGNORECASE),
    "architect": re.compile(r"archite", re.IGNORECASE),
}


class Entity(BaseModel):
    """Entity information including indication of physical vs legal person.
    Most fields are defined only for physical persons.
    """

    entity_id: EntityId.T = EntityId.field
    surname: EntitySurname.T = EntitySurname.field
    name: EntityName.T = EntityName.field
    name2: EntityName.T = EntityName.field
    name3: EntityName.T = EntityName.field
    fullname: EntityFullName.T = EntityFullName.field
    physical: EntityIsPhysical.T = EntityIsPhysical.field
    legal: EntityIsLegal.T = EntityIsLegal.field
    sex: EntitySex.T = EntitySex.field
    title_noble: EntityTitleNoble.T = EntityTitleNoble.field
    title_other: EntityTitleOther.T = EntityTitleOther.field
    # Biographical events - birth
    birth_year: EntityBiographicalEventYear.T = EntityBiographicalEventYear.field
    birth_month: EntityBiographicalEventMonth.T = EntityBiographicalEventMonth.field
    birth_day: EntityBiographicalEventDay.T = EntityBiographicalEventDay.field
    # Biographical events - death
    death_year: EntityBiographicalEventYear.T = EntityBiographicalEventYear.field
    death_month: EntityBiographicalEventMonth.T = EntityBiographicalEventMonth.field
    death_day: EntityBiographicalEventDay.T = EntityBiographicalEventDay.field
    # Biographical events - baptism
    baptism_year: EntityBiographicalEventYear.T = EntityBiographicalEventYear.field
    baptism_month: EntityBiographicalEventMonth.T = EntityBiographicalEventMonth.field
    baptism_day: EntityBiographicalEventDay.T = EntityBiographicalEventDay.field
    # Biographical events - burial
    burial_year: EntityBiographicalEventYear.T = EntityBiographicalEventYear.field
    burial_month: EntityBiographicalEventMonth.T = EntityBiographicalEventMonth.field
    burial_day: EntityBiographicalEventDay.T = EntityBiographicalEventDay.field

    @field_validator(
        "birth_month",
        "death_month",
        "baptism_month",
        "burial_month",
        mode="before",
    )
    @classmethod
    def validate_month(cls, month: str | float) -> int:
        if pd.isnull(month):
            return None
        if isinstance(month, int | float):
            return int(month)
        return {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }[str(month).strip().lower()]

    @field_validator("title_noble", mode="before")
    @classmethod
    def validate_title_noble(cls, title: str | None) -> str | None:
        if pd.isnull(title):
            return None
        return normalize_title_noble(title)

    @field_validator("title_other", mode="before")
    @classmethod
    def validate_title_other(cls, title: str | None) -> str | None:
        if pd.isnull(title):
            return None
        return normalize_title_other(title)

    @field_validator("sex", mode="before")
    @classmethod
    def validate_sex(cls, sex: str) -> str | None:
        if pd.isnull(sex):
            return None
        sex = str(sex).strip().lower()
        if sex == "f":
            return "female"
        if sex == "m":
            return "male"
        return sex

    @field_validator("physical", "legal", mode="before")
    @classmethod
    def validate_physical_legal(cls, value: Any) -> bool | None:
        if pd.isnull(value):
            return None
        return bool(value)

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, data: dict[str, Any]) -> dict[str, Any]:
        for which in ("birth", "death", "baptism", "burial"):
            est = data.pop(f"{which}_estim_year", None)
            field = f"{which}_year"
            year = data.get(field)
            if not year and est:
                year = est
            data[field] = year or None
        data = {
            k: v if not pd.isnull(v) else None
            for k, v in data.items()
            if k in cls.model_fields
        }
        return data

    @model_validator(mode="after")
    def validate_physical_and_legal(self) -> Self:
        if self.name or self.name2 or self.name3:
            if self.physical is None:
                self.physical = True
            if self.legal is None:
                self.legal = False
        else:
            self.physical = False
        return self

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> Self:
        def select_most_complete(s: pd.Series) -> int | float | str:
            s = s.dropna()
            if s.size <= 0:
                return pd.NA
            if pd.api.types.is_string_dtype(s):
                return max(s, key=len)
            return s.mode().iloc[0]

        record = df.agg(select_most_complete)
        data = dict.fromkeys(["entity_id"], df.name)
        data.update(record.to_dict())
        return cls(**data)


# Utils ------------------------------------------------------------------------------


def normalize_title_noble(title: str) -> str | None:
    """Normalize noble title."""
    title = title.strip().lower()
    return {
        "hr.": "count",
        "ks.": "prince",
        "wlk. ks.": "prince",
        "bar.": "baron",
        "bar": "baron",
        "baronowa": "baron",
        "baron": "baron",
    }.get(title)


def normalize_title_other(title: str) -> str | None:
    """Normalize other title."""
    for name, rx in rx_titles.items():
        if rx.search(title):
            return name
    return None
