from typing import Any

import pandas as pd
from pydantic import BaseModel, model_validator

from kingpol.dataset.fields import (
    EntityBiographicalEventYear,
    EntityFullName,
    EntityId,
    EntityIsLegal,
    EntityIsPhysical,
    EntityName,
    EntityRankingEmploymentShare,
    EntityRankingEmploymentTotal,
    EntityRankingProductionValueShare,
    EntityRankingProductionValueTotal,
    EntityRankingProductivity,
    EntitySex,
    EntitySurname,
    EntityTitleNoble,
    EntityTitleOther,
    IsElite,
)


class EntityRanking(BaseModel):
    """Entity ranking table contains main entity identifiers and metadata
    together with production value and employment corresponding to the given entity
    by aggregating value and employment of associated companies.

    The compilation of the table depends on the following
    parameter groups in ``params.yaml``:

    * ``ranking`` - parameters specific to the ranking table
    * ``elite`` - specify who is considered _elite_
    * ``share`` - control what entity-company relationships are considered when
      calculating shares.
    """

    entity_id: EntityId.T = EntityId.field
    fullname: EntityFullName.T = EntityFullName.field
    elite: IsElite.T = IsElite.field
    physical: EntityIsPhysical.T = EntityIsPhysical.field
    legal: EntityIsLegal.T = EntityIsLegal.field
    surname: EntitySurname.T = EntitySurname.field
    name: EntityName.T = EntityName.field
    sex: EntitySex.T = EntitySex.field
    birth_year: EntityBiographicalEventYear.T = EntityBiographicalEventYear.field
    death_year: EntityBiographicalEventYear.T = EntityBiographicalEventYear.field
    title_noble: EntityTitleNoble.T = EntityTitleNoble.field
    title_other: EntityTitleOther.T = EntityTitleOther.field
    value_share: EntityRankingProductionValueShare.T = (
        EntityRankingProductionValueShare.field
    )
    employment_share: EntityRankingEmploymentShare.T = (
        EntityRankingEmploymentShare.field
    )
    value_total: EntityRankingProductionValueTotal.T = (
        EntityRankingProductionValueTotal.field
    )
    employment_total: EntityRankingEmploymentTotal.T = (
        EntityRankingEmploymentTotal.field
    )
    productivity: EntityRankingProductivity.T = EntityRankingProductivity.field

    @model_validator(mode="before")
    @classmethod
    def preprocess(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in data.items() if not pd.isnull(v)}
