# %% ---------------------------------------------------------------------------------

import pandas as pd

from kingpol import paths
from kingpol.dataset import DataProc
from kingpol.excel import write_sheet

# %% ---------------------------------------------------------------------------------

proc = DataProc(paths.proc)

# %% ---------------------------------------------------------------------------------

with pd.ExcelWriter(paths.proc.excel, engine="xlsxwriter") as writer:
    write_sheet(proc.conversions.reset_index(), writer, "conversions")
    write_sheet(proc.prices.reset_index(), writer, "prices")
    write_sheet(proc.industries.reset_index(), writer, "industries")
    write_sheet(proc.records, writer, "records")
    write_sheet(proc.yearly, writer, "yearly")
    write_sheet(proc.companies, writer, "companies")
    write_sheet(proc.entities, writer, "entities")
    write_sheet(proc.relations, writer, "relations")
    write_sheet(proc.shares, writer, "shares")
    write_sheet(proc.ranking, writer, "ranking")
    write_sheet(proc.groups, writer, "groups")

# %% ---------------------------------------------------------------------------------
