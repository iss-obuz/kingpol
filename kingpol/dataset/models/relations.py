import re

from pydantic import (
    BaseModel,
    field_validator,
)

from kingpol.dataset.fields import EntityId, RecordId, RelationType

rx_relations = {
    "board": re.compile(r"cz[łl]one?k|zarz[aą]d|rada|komitet", re.IGNORECASE),
    "namesake": re.compile(r"imienni", re.IGNORECASE),
    "owner": re.compile(r"w[łl]a[śs]ciciel", re.IGNORECASE),
    "director": re.compile(r"dyrektor", re.IGNORECASE),
    "president": re.compile(r"prezes", re.IGNORECASE),
    "manager": re.compile(
        r"kierownik|naczelni|zarz[aą]dzaj|zawiadowc|prokurent"
        r"|reprezentat|plenipoten|pe[łl]nomoc|administra",
        re.IGNORECASE,
    ),
    "leaseholder": re.compile(r"dzier[zż]awc", re.IGNORECASE),
    "sales": re.compile(r"sprzeda", re.IGNORECASE),
}


class Relation(BaseModel):
    """Relations between entities (physical or legal persons) and companies."""

    entity_id: EntityId.T = EntityId.field
    record_id: RecordId.T = RecordId.field
    relation: RelationType.T = RelationType.field

    @field_validator("relation", mode="before")
    @classmethod
    def validate_relation(cls, rel: str) -> str:
        return normalize_relation(rel)


# Utils ------------------------------------------------------------------------------


def normalize_relation(rel: str) -> str:
    """Normalize relation types."""
    for name, rx in rx_relations.items():
        if rx.search(rel):
            return name
    return "other"
