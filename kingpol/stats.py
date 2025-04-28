from collections.abc import Sequence

import numpy as np
import pandas as pd


def mode(s: pd.Series):
    """Find mode.

    Examples
    --------
    >>> X = [None, 2, 2, None, 1, 1, None]
    >>> mode(X).item()
    1.0
    """
    modes = pd.Series(s).mode(dropna=True)
    if modes.size <= 0:
        return pd.NA
    return modes.iloc[0]


def gini(x: Sequence[float], *, dropna: bool = True):
    """Calculate Gini coefficient."""
    # Mean absolute difference
    X = np.asarray(x)
    if dropna:
        X = X[~pd.isnull(X)]
    if X.size <= 1:
        return np.nan
    mad = np.abs(np.subtract.outer(X, X)).mean()
    # Relative mean absolute difference
    rmad = mad / np.mean(x)
    # Gini coefficient
    g = 0.5 * rmad
    return g
