from typing import Literal

from pydantic import BaseModel, Field, PositiveFloat, PositiveInt


class CurrencyExchangeRate(BaseModel):
    """Exchange rates to Russian rubles."""

    currency: Literal["ruble", "german mark", "french frank"] = Field(
        title="Currency",
        description="Currency name",
    )
    year: PositiveInt = Field(
        title="Year",
        description="Year of exchange rate",
    )
    rate: PositiveFloat = Field(
        title="Exchange rate",
        description="Exchange rate to Russian rubles",
    )
