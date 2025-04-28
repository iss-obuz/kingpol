# from collections.abc import Iterable
# from typing import Any

# import choix
# import numpy as np


# def comparisons(*Xs: np.ndarray, dtype=np.uint8) -> np.ndarray:
#     """Count cases when ``X[i] > X[j]`` for all ``X in Xs``.

#     Parameters
#     ----------
#     Xs : np.ndarray
#         Input arrays.

#     Returns
#     -------
#     np.ndarray
#         The pairwise comparison results.

#     Examples
#     --------
#     >>> X = np.array([1, 2, 3])
#     >>> comparisons(X)
#     array([[0, 0, 0],
#            [1, 0, 0],
#            [1, 1, 0]], dtype=uint8)
#     >>> Y = np.array([4, 2, 11])
#     >>> comparisons(Y)
#     array([[0, 1, 0],
#            [0, 0, 0],
#            [1, 1, 0]], dtype=uint8)
#     >>> comparisons(X, Y)
#     array([[0, 1, 0],
#            [1, 0, 0],
#            [2, 2, 0]], dtype=uint8)
#     """
#     assert len(Xs) >= 1, "At least one array is required."
#     assert len({len(X) for X in Xs}) == 1, "All arrays must have the same length."
#     n = len(Xs[0])
#     counts = np.zeros((n, n), dtype=np.uint8)
#     for X in Xs:
#         counts += (X < X[:, None]).astype(dtype)  # noqa
#     return counts


# def rank(
#     cmp: np.ndarray, mask: int | Iterable[bool] | None = None, **kwargs: Any
# ) -> np.ndarray:
#     """Iterative Luce Spectral Ranking.

#     Parameters
#     ----------
#     cmp
#         Dense 2D array of pairwise comparisons as returned by :func:`comparisons`.
#     mask
#         Optional mask (1D boolean array) for selecting a subset of the comparisons.
#         Can be passsed as an integer, which amounts to selecting top :math:`n` items.
#     """
#     R = np.full(cmp.shape[0], np.nan)
#     if mask is not None:
#         if np.isscalar(mask):
#             stop = int(mask)
#             mask = np.full(cmp.shape[0], False)
#             mask[: int(stop)] = True
#         cmp = cmp[mask][:, mask]
#     ranking = choix.ilsr_pairwise_dense(cmp, **kwargs)
#     if mask is not None:
#         R[mask] = ranking
#     else:
#         R = ranking
#     return R
