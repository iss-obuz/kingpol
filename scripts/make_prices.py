# %% ---------------------------------------------------------------------------------

import pandas as pd

from kingpol import params, paths
from kingpol.dataset import DataAux, DataProc
from kingpol.dataset.models import (
    CurrencyExchangeRate,
    Price,
    ProductUnitConversionRate,
)

# %% ---------------------------------------------------------------------------------

aux = DataAux(paths.aux)
proc = DataProc(paths.proc)

# %% Product units -------------------------------------------------------------------

produnits = aux.prices.index.to_frame(index=False)

# %% Count measure conversions -------------------------------------------------------

count = (
    aux.conversions.loc["count"]
    .to_frame()
    .reset_index()
    .pipe(lambda df: produnits.merge(df, how="right", on="unit"))
    .drop(columns=["standard", "rate"])
    .assign(item=1.0)
)

# %% Mass measures conversions -------------------------------------------------------

mass = (
    aux.conversions.loc["mass"]
    .to_frame()
    .reset_index()
    .pipe(lambda df: produnits.merge(df, how="right", on="unit"))
    .rename(columns={"rate": "kg"})
    .drop(columns="standard")
    .merge(aux.masses.reset_index(), how="left", on="product")
    .assign(m3=lambda df: df["kg"] / df.pop("kg_per_m3"))
)

# %% Volume measures conversions -----------------------------------------------------

volume = (
    aux.conversions.loc["volume"]
    .to_frame()
    .reset_index()
    .pipe(lambda df: produnits.merge(df, how="right", on="unit"))
    .rename(columns={"rate": "m3"})
    .drop(columns="standard")
    .merge(aux.masses.reset_index(), how="left", on="product")
    .assign(kg=lambda df: df["m3"] * df.pop("kg_per_m3"))
)

# %% Make conversion table -----------------------------------------------------------

conversions = (
    pd.concat([count, mass, volume], axis=0)
    .dropna(subset=["product", "unit"])
    .melt(
        id_vars=["product", "unit"],
        value_vars=["kg", "m3", "item"],
        var_name="measure",
        value_name="rate",
    )
    .sort_values(["product", "unit", "measure"])
    .dropna(ignore_index=True)
    .pipe(
        lambda df: pd.DataFrame(
            [
                ProductUnitConversionRate(**record).model_dump()
                for record in df.to_dict(orient="records")
            ]
        )
    )
)

# %% Make standard prices table ------------------------------------------------------

prices = (
    aux.prices.dropna()
    .reset_index()
    .pipe(lambda df: conversions.merge(df, how="left", on=["product", "unit"]))
    .dropna()
    .assign(unit=lambda df: df.pop("measure"))
    .set_index(["product", "unit"])
    .sort_index()
    .pipe(lambda df: df.div(df.pop("rate"), axis=0))
    .melt(var_name="year", value_name="price", ignore_index=False)
    .reset_index()
    .sort_values(["product", "unit", "year"], ignore_index=True)
    .pipe(
        lambda df: pd.DataFrame(
            [Price(**record).model_dump() for record in df.to_dict(orient="records")]
        )
    )
)

# %% Check consistency ---------------------------------------------------------------

if params.test:
    assert prices.size > 0

# %% Make currency conversion table --------------------------------------------------

currencies = (
    aux.currencies.melt(var_name="year", value_name="rate", ignore_index=False)
    .reset_index(drop=False)
    .sort_values(["currency", "year"])
    .pipe(
        lambda df: pd.DataFrame(
            [
                CurrencyExchangeRate(**record).model_dump()
                for record in df.to_dict(orient="records")
            ]
        )
    )
)

# %% ---------------------------------------------------------------------------------

proc.write.conversions(conversions)
proc.write.prices(prices)
proc.write.currencies(currencies)

# %% ---------------------------------------------------------------------------------
