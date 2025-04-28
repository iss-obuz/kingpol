from collections.abc import Iterable, Mapping
from typing import Any


def getrc(
    opts: Mapping[str, Any] | None = None,
    *,
    preamble: str | Iterable[str] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Get default :mod:`matplotlib` ``rcParams``."""
    opts = opts or {}
    preamble = preamble or []
    if isinstance(preamble, str):
        preamble = [preamble]
    preamble = "\n".join(
        [
            r"\usepackage{amsmath,amsfonts,amssymb,sfmath,xcolor}",
            r"\usepackage[utf8]{inputenc}",
            *preamble,
        ]
    )
    return {
        "font.family": "sans-serif",
        "text.latex.preamble": preamble,
        "figure.figsize": (5, 5),
        "figure.labelsize": "x-large",
        "figure.titlesize": "xx-large",
        "figure.titleweight": "bold",
        "savefig.bbox": "tight",
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.titleweight": "bold",
        "axes.titlesize": "large",
        "axes.labelsize": "large",
        "scatter.marker": "o",
        "scatter.edgecolors": "black",
        "lines.markeredgecolor": "black",
        "lines.markeredgewidth": 1,
        "image.cmap": "viridis",
        **opts,
        **kwargs,
    }
