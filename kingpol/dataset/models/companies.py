from pydantic import BaseModel

from kingpol.dataset.fields import (
    CompanyAddress,
    CompanyEmployment,
    CompanyFoundationYear,
    CompanyGovernorate,
    CompanyId,
    CompanyIndustry,
    CompanyName,
    CompanyProductionValue,
    CompanyProductivity,
    CompanyPublicYear,
    CompanySector,
    CompanySubsector,
    CompanyType,
    IsElite,
    Product,
)


class Company(BaseModel):
    """Company information and statistics aggregated over yearly records.

    Compilation of this table is controlled  by the following parameter
    groups in ``params.yaml`` file:

    * `years`: yearly records to be included and aggregated in the table
    * `companies`: other parameters specific to the table,
      e.g. threshold for outlier dectection.
    """

    company_id: CompanyId.T = CompanyId.field
    name: CompanyName.T = CompanyName.field
    elite: IsElite.T = IsElite.field
    type: CompanyType.T = CompanyType.field
    industry: CompanyIndustry.T = CompanyIndustry.field
    subsector: CompanySubsector.T = CompanySubsector.field
    sector: CompanySector.T = CompanySector.field
    product: Product.T = Product.field
    address: CompanyAddress.T = CompanyAddress.field
    governorate: CompanyGovernorate.T = CompanyGovernorate.field
    foundation: CompanyFoundationYear.T = CompanyFoundationYear.field
    public: CompanyPublicYear.T = CompanyPublicYear.field
    value: CompanyProductionValue.T = CompanyProductionValue.field
    employment: CompanyEmployment.T = CompanyEmployment.field
    productivity: CompanyProductivity.T = CompanyProductivity.field
