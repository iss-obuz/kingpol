from pydantic import BaseModel, Field, PositiveInt

from kingpol.dataset.fields import CompanyId, EntityId, EntityShare


class Shares(BaseModel):
    """Share of entities in companies.

    The compilation of the table depends on the following parameter groups
    in the ``params.yaml`` file:

    * ``shares`` - parameters specific to the shares table which
      can be used to control the types of entity-company relations
      that are considered when calculating shares.
    """

    company_id: CompanyId.T = CompanyId.field
    entity_id: EntityId.T = (EntityId.field,)
    entity_shares: PositiveInt = Field(
        title="Entity shares",
        description="Number of company shares owned by the entity",
    )
    n_shares: PositiveInt = Field(
        title="Number of shares",
        description="Total number of shares in the company",
    )
    share: EntityShare.T = EntityShare.field
