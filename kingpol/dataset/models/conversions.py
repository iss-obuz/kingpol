from pydantic import BaseModel, Field, PositiveFloat

from kingpol.dataset.fields import Product, Unit


class ProductUnitConversionRate(BaseModel):
    """Rates for converting between different product amounts and standard measures
    (kg, cubic meters and items).
    """

    product: Product.T = Product.field
    unit: Unit.T = Unit.field
    measure: Product.T = Product.field
    rate: PositiveFloat = Field(
        title="Conversion rate",
        description="Conversion rate from the product to the standard measure",
    )
