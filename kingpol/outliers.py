import numpy as np
import numpy.typing as npt


def deviation(X: npt.ArrayLike):
    r"""Get deviation scores for observations.

    Deviation scores measures the relative difference
    between a given observation and the corresponding sample mean:

    .. math::

    \text{dev}(x_i) = \log_{10}\frac{nx_i}{\sum_j xj}

    The purpose of this definition is to capture relative deviations
    in terms of the orders of magnitudes.
    """
    return np.log10(X / np.nanmean(X))


def rank_outliers(X: npt.ArrayLike, threshold: float = 1.0):
    """Rank outliers based on :func:`deviation` scores.

    Parameters
    ----------
    X
        1D array-like.
    threshold
        Threshold values for defining outlier ranks.
    """

    def get_deviation(X: npt.NDArray, active: npt.NDArray[np.bool_] | None = None):
        if active is not None:
            dev = np.full_like(X, np.nan, dtype=float)
            dev[active] = deviation(X[active])
        else:
            dev = deviation(X)
        return np.abs(dev)

    X = np.asarray(X)
    rank = 0
    oranks = np.zeros_like(X, dtype=np.uint32)
    active = np.ones_like(X, dtype=bool)

    while True:
        dev = get_deviation(X, active)
        if np.nanmax(dev) > threshold:
            rank += 1
            idx = np.nanargmax(dev)
            active[idx] = False
            oranks[idx] = rank
        else:
            break

    mask = oranks > 0
    oranks[mask] = oranks.max() + 1 - oranks[mask]
    return oranks
