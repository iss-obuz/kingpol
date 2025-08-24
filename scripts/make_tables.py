# %% ---------------------------------------------------------------------------------

import pandas as pd

from kingpol import params, paths
from kingpol.dataset import DataProc, DataRaw
from kingpol.excel import write_sheet
from kingpol.stats import gini

# %% ---------------------------------------------------------------------------------

raw = DataRaw(paths.raw)
proc = DataProc(paths.proc)

basic_tables = {}
employment_and_value_tables = {}
top_tables = {}

# %% General summary -----------------------------------------------------------------

records_raw = (
    raw.companies.rename(
        columns={"tom": "volume", "tro": "record_id", "troi": "company_id"}
    )
    .groupby(["volume"])
    .size()
)
records_proc = (
    proc.records.assign(
        is_nonoutlier=lambda df: df["outlier_rank"].eq(0),
        has_employment=lambda df: df["employment"].notnull(),
        has_value=lambda df: df["value"].notnull(),
        has_both=lambda df: df["has_employment"] & df["has_value"],
    )
    .groupby(["volume", "year"])
    .apply(
        lambda df: pd.Series(
            {
                "number of valid records": len(df),
                "non-outlier records": df["is_nonoutlier"].sum(),
                "records with employment": df["has_employment"].sum(),
                "records with value": df["has_value"].sum(),
                "records with both": df["has_both"].sum(),
            }
        ),
        include_groups=False,
    )
)
records_proc.insert(0, "number of records", records_raw.to_numpy())

records_table = (
    pd.concat(
        {
            "n": records_proc,
            "%": records_proc.div(records_raw, axis=0) * 100,
        }
    )
    .swaplevel(0, 2, axis=0)
    .swaplevel(0, 1, axis=0)
    .sort_index(level=[0, 1, 2], axis=0, ascending=[True, True, False])
    .style.format(
        precision=0, subset=pd.IndexSlice[pd.IndexSlice[:, :, "n"], :], na_rep="—"
    )
    .format(precision=1, subset=pd.IndexSlice[pd.IndexSlice[:, :, "%"], :], na_rep="—")
)

yearly_table = (
    proc.yearly.assign(
        has_employment=lambda df: df["employment"].notnull(),
        has_value=lambda df: df["value"].notnull(),
        has_both=lambda df: df["has_employment"] & df["has_value"],
    )
    .groupby(["year"])
    .apply(
        lambda df: pd.Series(
            {
                "number of records": len(df),
                "records with employment": df["has_employment"].sum(),
                "records with value": df["has_value"].sum(),
                "records with both": df["has_both"].sum(),
            }
        ),
        include_groups=False,
    )
    .pipe(
        lambda df: pd.concat(
            {
                "n": df,
                "%": df.div(df.iloc[:, 0], axis=0) * 100,
            }
        )
    )
    .swaplevel(0, 1, axis=0)
    .sort_index(level=[0, 1], axis=0, ascending=[True, False])
    .style.format(
        precision=0, subset=pd.IndexSlice[pd.IndexSlice[:, "n"], :], na_rep="—"
    )
    .format(precision=1, subset=pd.IndexSlice[pd.IndexSlice[:, "%"], :], na_rep="—")
)

basic_tables.update(
    {
        "Reported records summary": records_table,
        "Yearly records summary": yearly_table,
    }
)

# %% Employment & value in 1911 ------------------------------------------------------

formats = {
    ("employment", "sum"): "{:,.0f}",
    ("employment", "gini"): "{:.2f}",
    ("value", "sum"): "{:,.0f}",
    ("value", "gini"): "{:,.2f}",
}

spec = params.tables.employment_and_value

# %%

companies1911 = (
    proc.yearly[
        [
            "company_id",
            "name",
            "year",
            "employment",
            "value",
            "governorate",
            "industry",
            "subsector",
            "sector",
        ]
    ]
    .groupby(["company_id"])
    .apply(lambda df: df.ffill(), include_groups=False)
    .reset_index("company_id")
    .reset_index(drop=True)
    .query("year == 1911")
    .sort_values("employment", ascending=False, ignore_index=True)
    .assign(
        elite=lambda df: df["employment"].ge(params.elite.min_employment).fillna(False)
    )
)


# %% Generate tables


def make_table_data(df: pd.DataFrame, factor: str | list[str]) -> pd.DataFrame:
    cols = ["employment", "value"]
    grouped = df.groupby(factor)[cols]
    data = grouped.agg(["sum", gini])

    data.insert(0, ("", "n"), grouped.size())
    data.insert(1, ("", "%"), grouped.size().pipe(lambda s: s / s.sum() * 100))

    for col in cols:
        key = (col, "sum")
        idx = data.columns.tolist().index(key) + 1
        data.insert(idx, (col, "%"), data[key] / data[key].sum() * 100)

    data = data.sort_values(("employment", "sum"), ascending=False)
    data = pd.concat([data, data.sum().to_frame("overall").T], axis=0)

    for col in cols:
        data.at["overall", (col, "gini")] = gini(companies1911[col])

    data[("", "n")] = data[("", "n")].astype(int)
    return data


for factor, name in spec.items():
    data = (
        make_table_data(companies1911, factor)
        .assign(subset="all")
        .set_index("subset", append=True)
        .swaplevel(0, 1)
    )
    top = (
        make_table_data(companies1911.query("elite"), factor)
        .assign(subset="major")
        .set_index("subset", append=True)
        .swaplevel(0, 1)
    )
    share = top.loc["major"] / data.loc["all"] * 100
    for col in share:
        if col[-1] in ("%", "gini"):  # type: ignore
            share[col] = pd.NA
    share = (
        share.assign(subset="major (%)")
        .set_index("subset", append=True)
        .swaplevel(0, 1)
        .dropna(axis=1, thresh=1)
    )
    data = pd.concat([data, top, share]).pipe(lambda df: df[df[("", "n")].notnull()])
    order = data.loc["all"].index
    data = data.groupby(level=0).apply(
        lambda df: (
            df.loc[df.name].loc[order[order.isin(df.index.get_level_values(1))]]  # noqa
        )
    )
    table = data.style.format(formats, precision=1).apply(
        lambda x: ["font-weight: bold"] * len(x),
        subset=pd.IndexSlice[
            [("all", "overall"), ("major", "overall"), ("major (%)", "overall")], :
        ],
    )
    employment_and_value_tables[name] = table

# %% Largest companies by employment -------------------------------------------------

companies1911_top = (
    companies1911.query(
        f"employment.notnull() & employment.ge({params.elite.min_employment})"
    )
    .query("sector.eq('industry')")[
        [
            "name",
            "employment",
            "value",
            "governorate",
            "industry",
            "subsector",
        ]
    ]
    .rename(columns={"subsector": "sector"})
    .sort_values("employment", ascending=False, ignore_index=True)
    .assign(name=lambda df: df["name"].str.split(";").map(lambda x: x[0].strip()))
)

top_tables["Companies (1911)"] = companies1911_top.set_index("name")

# %% Top physical persons by value ---------------------------------------------------

persons = (
    proc.ranking.query("elite & physical")
    .query("birth_year.notnull() & birth_year.le(1880)")
    .query("death_year.notnull() & death_year.ge(1904)")
    .sort_values("value_share", ascending=False, ignore_index=True)
    .head(30)[
        [
            "surname",
            "name",
            "sex",
            "title_noble",
            "birth_year",
            "death_year",
            "value_share",
            "employment_share",
        ]
    ]
)

top_tables["Wealthiest persons (1911)"] = persons.set_index(["surname", "name"])

# %% Top legal entites by value ------------------------------------------------------

legal = (
    proc.ranking.query("elite & legal")
    .sort_values("value_share", ascending=False, ignore_index=True)
    .head(10)[
        [
            "fullname",
            "value_share",
            "employment_share",
        ]
    ]
)

top_tables["Wealthiest entities (1911)"] = legal.set_index("fullname")

# %% Write tables --------------------------------------------------------------------

with pd.ExcelWriter(paths.proc.tables, engine="xlsxwriter") as writer:
    for name, table in basic_tables.items():
        write_sheet(table, writer, name, index=True)
    for name, table in top_tables.items():
        write_sheet(table, writer, name, index=True)
    for name, table in employment_and_value_tables.items():
        write_sheet(table, writer, name, index=True)

# %% ---------------------------------------------------------------------------------
