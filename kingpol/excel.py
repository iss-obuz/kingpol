from typing import Any

import pandas as pd
from pandas.io.formats.style import Styler


def write_sheet(
    data: pd.DataFrame | Styler,
    writer: pd.ExcelWriter,
    name: str,
    *,
    index: bool | None = None,
    autofit: bool = False,
    **kwds: Any,
) -> None:
    if index is None:
        index = isinstance(data, Styler)
    data.to_excel(writer, sheet_name=name, index=index, **kwds)
    if isinstance(data, Styler):
        data = data.data
    max_row, max_col = data.shape
    if index:
        max_col += data.index.nlevels
    if (nlevels := data.columns.nlevels) > 1:
        max_row += nlevels
    sheet = writer.sheets[name]
    if autofit:
        sheet.autofit()
    else:
        sheet.set_column(0, max_col - 1, 20)
    sheet.autofilter(0, 0, max_row, max_col - 1)
