from pydantic import BaseModel, Field, PositiveFloat, PositiveInt

from kingpol.dataset.fields import Product, Unit


class Price(BaseModel):
    """Prices of standard amounts of products in different year."""

    product: Product.T = Product.field
    unit: Unit.T = Unit.field
    year: PositiveInt = Field(
        title="Year",
        description="Year of the price",
    )
    price: PositiveFloat = Field(
        description="Price of the product in the given unit and year",
    )
