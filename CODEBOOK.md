# Codebook

This codebook provides a detailed description of the table and table fields included
in the ``KINGPOL_INDUSTRY`` database. A general discussion of the database is provided
in the ``README.md`` file.

## Tables

### Company

Company information and statistics aggregated over yearly records.

Compilation of this table is controlled  by the following parameter
groups in ``params.yaml`` file:

* `years`: yearly records to be included and aggregated in the table
* `companies`: other parameters specific to the table,
e.g. threshold for outlier dectection.

|    | label        | field           | description                                                              |
|---:|:-------------|:----------------|:-------------------------------------------------------------------------|
|  0 | company_id   | Company ID      | Unique company identifier. Can be used for joining tables.               |
|  1 | name         | Company name    | Name of the company.                                                     |
|  2 | elite        | Elite           | Whether belongs to elite (see 'params.yaml' for the inclusion criteria). |
|  3 | type         | Company type    | Type of the company.                                                     |
|  4 | industry     | Industry        | Industry of the company.                                                 |
|  5 | subsector    | Subsector       | Detailed sector the company belongs to.                                  |
|  6 | sector       | Sector          | Sector the company belongs to.                                           |
|  7 | product      | Product         | Product name.                                                            |
|  8 | address      | Address         | Company address.                                                         |
|  9 | governorate  | Governorate     | Governorate where the company is located.                                |
| 10 | foundation   | Foundation year | Year the company was founded.                                            |
| 11 | public       | Public year     | Year the company was publicly listed.                                    |
| 12 | value        | Value           | Yearly production value (in rubles).                                     |
| 13 | employment   | Employment      | Number of employees.                                                     |
| 14 | productivity | Productivity    | Yearly productivity (in rubles per employee).                            |

### CompanyProperty

Detailed information on individual properties within company records.

This table is an implementation detail of the dataset compilation process
and is not intended for direct use by end users.

|    | label       | field                  | description                                                       |
|---:|:------------|:-----------------------|:------------------------------------------------------------------|
|  0 | company_id  | Company ID             | Unique company identifier. Can be used for joining tables.        |
|  1 | record_id   | Record ID              | Unique company-record identifier. Can be used for joining tables. |
|  2 | property_id | Property ID            | Unique property identifier.                                       |
|  3 | volume      | Volume                 | Address book volume number.                                       |
|  4 | year        | Year                   | Publication year of the address book volume.                      |
|  5 | property    | Property               | Property name.                                                    |
|  6 | object      | Object                 | Object name.                                                      |
|  7 | value       | Property value         | Raw property value as string.                                     |
|  8 | num_value   | Property numeric value | Numeric property value.                                           |
|  9 | product     | Product                | Product name.                                                     |
| 10 | unit        | Unit                   | Unit of measurement.                                              |
| 11 | desc1       | Description            | Additional property description.                                  |
| 12 | desc2       | Description            | Additional property description.                                  |
| 13 | confirmed   | Confirmed              | Whether the property value is confirmed.                          |
| 14 | official    | Official               | Whether the property value is official.                           |

### CompanyRecord

Company record is a single entry in a specific volume of the address book.
In some cases there may be mulitple records in the same volume for the same company.

The compilation of the table depends on the following parameter
groups in ``params.yaml`` file:

* ``records``: parameters for the records table used for controlling
threshold for outlier detection, inclusion of industries based on
data (in)completeness, and selection of governorates.

|    | label        | field           | description                                                       |
|---:|:-------------|:----------------|:------------------------------------------------------------------|
|  0 | company_id   | Company ID      | Unique company identifier. Can be used for joining tables.        |
|  1 | record_id    | Record ID       | Unique company-record identifier. Can be used for joining tables. |
|  2 | volume       | Volume          | Address book volume number.                                       |
|  3 | year         | Year            | Publication year of the address book volume.                      |
|  4 | name         | Company name    | Name of the company.                                              |
|  5 | type         | Company type    | Type of the company.                                              |
|  6 | industry     | Industry        | Industry of the company.                                          |
|  7 | subsector    | Subsector       | Detailed sector the company belongs to.                           |
|  8 | sector       | Sector          | Sector the company belongs to.                                    |
|  9 | value        | Value           | Yearly production value (in rubles).                              |
| 10 | employment   | Employment      | Number of employees.                                              |
| 11 | productivity | Productivity    | Yearly productivity (in rubles per employee).                     |
| 12 | output       | Output          | Yearly product output.                                            |
| 13 | product      | Product         | Product name.                                                     |
| 14 | unit         | Unit            | Unit of measurement.                                              |
| 15 | address      | Address         | Company address.                                                  |
| 16 | governorate  | Governorate     | Governorate where the company is located.                         |
| 17 | foundation   | Foundation year | Year the company was founded.                                     |
| 18 | public       | Public year     | Year the company was publicly listed.                             |

### CompanyYearlyRecord

Yearly records are obtained by aggregating all simple records associated with
the same company within the same year.

The compilation of the table depends on the following parameter groups
in the ``params.yaml`` file:

* ``yearly`` - parameters specific to yearly records table.
They can be used to specify outlier detection thresholds
as well as top-level economy sectors to be included in the table,
and as a result in all downstream tables.

|    | label        | field           | description                                                |
|---:|:-------------|:----------------|:-----------------------------------------------------------|
|  0 | company_id   | Company ID      | Unique company identifier. Can be used for joining tables. |
|  1 | year         | Year            | Publication year of the address book volume.               |
|  2 | name         | Company name    | Name of the company.                                       |
|  3 | type         | Company type    | Type of the company.                                       |
|  4 | industry     | Industry        | Industry of the company.                                   |
|  5 | subsector    | Subsector       | Detailed sector the company belongs to.                    |
|  6 | sector       | Sector          | Sector the company belongs to.                             |
|  7 | value        | Value           | Yearly production value (in rubles).                       |
|  8 | employment   | Employment      | Number of employees.                                       |
|  9 | productivity | Productivity    | Yearly productivity (in rubles per employee).              |
| 10 | output       | Output          | Yearly product output.                                     |
| 11 | product      | Product         | Product name.                                              |
| 12 | unit         | Unit            | Unit of measurement.                                       |
| 13 | address      | Address         | Company address.                                           |
| 14 | governorate  | Governorate     | Governorate where the company is located.                  |
| 15 | foundation   | Foundation year | Year the company was founded.                              |
| 16 | public       | Public year     | Year the company was publicly listed.                      |

### CurrencyExchangeRate

Exchange rates to Russian rubles.

|    | label    | field         | description                     |
|---:|:---------|:--------------|:--------------------------------|
|  0 | currency | Currency      | Currency name                   |
|  1 | year     | Year          | Year of exchange rate           |
|  2 | rate     | Exchange rate | Exchange rate to Russian rubles |

### Entity

Entity information including indication of physical vs legal person.
Most fields are defined only for physical persons.

|    | label         | field       | description                                              |
|---:|:--------------|:------------|:---------------------------------------------------------|
|  0 | entity_id     | Entity ID   | Unique entity identifier.Can be used for joining tables. |
|  1 | surname       | Surname     | Surname of the person.                                   |
|  2 | name          | Name        | Name of the person.                                      |
|  3 | name2         | Name        | Name of the person.                                      |
|  4 | name3         | Name        | Name of the person.                                      |
|  5 | fullname      | Full name   | Full name of the entity.                                 |
|  6 | physical      | Physical    | Whether the entity is a physical person.                 |
|  7 | legal         | Legal       | Whether the entity is a legal person.                    |
|  8 | sex           | Sex         | Sex of the person.                                       |
|  9 | title_noble   | Noble title | Noble title of the entity.                               |
| 10 | title_other   | Other title | Other title of the entity.                               |
| 11 | birth_year    | Year        | Year of a biographical event.                            |
| 12 | birth_month   | Month       | Month of a biographical event.                           |
| 13 | birth_day     | Day         | Day of a biographical event.                             |
| 14 | death_year    | Year        | Year of a biographical event.                            |
| 15 | death_month   | Month       | Month of a biographical event.                           |
| 16 | death_day     | Day         | Day of a biographical event.                             |
| 17 | baptism_year  | Year        | Year of a biographical event.                            |
| 18 | baptism_month | Month       | Month of a biographical event.                           |
| 19 | baptism_day   | Day         | Day of a biographical event.                             |
| 20 | burial_year   | Year        | Year of a biographical event.                            |
| 21 | burial_month  | Month       | Month of a biographical event.                           |
| 22 | burial_day    | Day         | Day of a biographical event.                             |

### EntityRanking

Entity ranking table contains main entity identifiers and metadata
together with production value and employment corresponding to the given entity
by aggregating value and employment of associated companies.

The compilation of the table depends on the following
parameter groups in ``params.yaml``:

* ``ranking`` - parameters specific to the ranking table
* ``elite`` - specify who is considered _elite_
* ``share`` - control what entity-company relationships are considered when
calculating shares.

|    | label            | field                    | description                                                                                                                                                                                                                                                      |
|---:|:-----------------|:-------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  0 | entity_id        | Entity ID                | Unique entity identifier.Can be used for joining tables.                                                                                                                                                                                                         |
|  1 | fullname         | Full name                | Full name of the entity.                                                                                                                                                                                                                                         |
|  2 | elite            | Elite                    | Whether belongs to elite (see 'params.yaml' for the inclusion criteria).                                                                                                                                                                                         |
|  3 | physical         | Physical                 | Whether the entity is a physical person.                                                                                                                                                                                                                         |
|  4 | legal            | Legal                    | Whether the entity is a legal person.                                                                                                                                                                                                                            |
|  5 | surname          | Surname                  | Surname of the person.                                                                                                                                                                                                                                           |
|  6 | name             | Name                     | Name of the person.                                                                                                                                                                                                                                              |
|  7 | sex              | Sex                      | Sex of the person.                                                                                                                                                                                                                                               |
|  8 | birth_year       | Year                     | Year of a biographical event.                                                                                                                                                                                                                                    |
|  9 | death_year       | Year                     | Year of a biographical event.                                                                                                                                                                                                                                    |
| 10 | title_noble      | Noble title              | Noble title of the entity.                                                                                                                                                                                                                                       |
| 11 | title_other      | Other title              | Other title of the entity.                                                                                                                                                                                                                                       |
| 12 | value_share      | Production value (share) | Entity's share in the yearly production value of all associated companies. The share is proportional to the number of records listing the entity as an associated person with a relationship of a high enough rank (configured by 'shares.relations' parameter). |
| 13 | employment_share | Employment (share)       | Entity's share in the employment of all associated companies. The share is proportional to the number of records listing the entity as an associated person with a relationship of a high enough rank (configured by 'shares.relations' parameter).              |
| 14 | value_total      | Production value (total) | Total yearly production value of all associated companies. This measure is a simple sum over associated companies wihtout splitting proportional to shares                                                                                                       |
| 15 | employment_total | Employment (total)       | Total employment of all associated companies. This measure is a simple sum over associated companies wihtout splitting proportional to shares                                                                                                                    |
| 16 | productivity     | Productivity             | Yearly productivity of the entity (in rubles per employee).                                                                                                                                                                                                      |

### Group

Group consists of companies associated with a given entity.

Each record in the group table corresponds to a company associated with an specific
entity and includes also information on the company share belonging to the entity.

This is a convenience table which does not contain any new information, which could
not be derived by joining and transforming other tables.

|    | label         | field           | description                                                              |
|---:|:--------------|:----------------|:-------------------------------------------------------------------------|
|  0 | entity_id     | Entity ID       | Unique entity identifier.Can be used for joining tables.                 |
|  1 | fullname      | Full name       | Full name of the entity.                                                 |
|  2 | elite         | Elite           | Whether belongs to elite (see 'params.yaml' for the inclusion criteria). |
|  3 | share         | Share           | Share of the entity in the company.                                      |
|  4 | company_id    | Company ID      | Unique company identifier. Can be used for joining tables.               |
|  5 | company_name  | Company name    | Name of the company.                                                     |
|  6 | company_elite | Elite           | Whether belongs to elite (see 'params.yaml' for the inclusion criteria). |
|  7 | type          | Company type    | Type of the company.                                                     |
|  8 | industry      | Industry        | Industry of the company.                                                 |
|  9 | subsector     | Subsector       | Detailed sector the company belongs to.                                  |
| 10 | sector        | Sector          | Sector the company belongs to.                                           |
| 11 | product       | Product         | Product name.                                                            |
| 12 | address       | Address         | Company address.                                                         |
| 13 | governorate   | Governorate     | Governorate where the company is located.                                |
| 14 | foundation    | Foundation year | Year the company was founded.                                            |
| 15 | public        | Public year     | Year the company was publicly listed.                                    |
| 16 | value         | Value           | Yearly production value (in rubles).                                     |
| 17 | employment    | Employment      | Number of employees.                                                     |
| 18 | productivity  | Productivity    | Yearly productivity (in rubles per employee).                            |

### Price

Prices of standard amounts of products in different year.

|    | label   | field   | description                                     |
|---:|:--------|:--------|:------------------------------------------------|
|  0 | product | Product | Product name.                                   |
|  1 | unit    | Unit    | Unit of measurement.                            |
|  2 | year    | Year    | Year of the price                               |
|  3 | price   |         | Price of the product in the given unit and year |

### ProductUnitConversionRate

Rates for converting between different product amounts and standard measures
(kg, cubic meters and items).

|    | label   | field           | description                                              |
|---:|:--------|:----------------|:---------------------------------------------------------|
|  0 | product | Product         | Product name.                                            |
|  1 | unit    | Unit            | Unit of measurement.                                     |
|  2 | measure | Product         | Product name.                                            |
|  3 | rate    | Conversion rate | Conversion rate from the product to the standard measure |

### Relation

Relations between entities (physical or legal persons) and companies.

|    | label     | field         | description                                                       |
|---:|:----------|:--------------|:------------------------------------------------------------------|
|  0 | entity_id | Entity ID     | Unique entity identifier.Can be used for joining tables.          |
|  1 | record_id | Record ID     | Unique company-record identifier. Can be used for joining tables. |
|  2 | relation  | Relation type | Type of the person-company relation.                              |

### Shares

Share of entities in companies.

The compilation of the table depends on the following parameter groups
in the ``params.yaml`` file:

* ``shares`` - parameters specific to the shares table which
can be used to control the types of entity-company relations
that are considered when calculating shares.

|    | label         | field            | description                                                |
|---:|:--------------|:-----------------|:-----------------------------------------------------------|
|  0 | company_id    | Company ID       | Unique company identifier. Can be used for joining tables. |
|  1 | entity_id     |                  |                                                            |
|  2 | entity_shares | Entity shares    | Number of company shares owned by the entity               |
|  3 | n_shares      | Number of shares | Total number of shares in the company                      |
|  4 | share         | Share            | Share of the entity in the company.                        |
