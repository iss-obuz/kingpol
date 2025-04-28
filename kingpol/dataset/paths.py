"""Dataset builder module."""
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any

__all__ = (
    "Paths",
    "PathsRaw",
    "PathsProc",
)


class Paths:
    """Paths manager.

    Attributes
    ----------
    root
        Root path for resolving relative paths.

    Examples
    --------
    >>> from tempfile import TemporaryDirectory
    >>> with TemporaryDirectory() as tmpdir:
    ...     paths = Paths(tmpdir)
    ...     paths.root == Path(tmpdir).absolute()
    True
    >>> with TemporaryDirectory() as tmpdir:
    ...     paths = Paths(tmpdir, data="data")
    ...     paths.data == Path(tmpdir) / "data"
    True
    >>> with TemporaryDirectory() as tmpdir:
    ...     paths = Paths(tmpdir, data="data")
    ...     paths.config = "@data/config.yaml"
    ...     paths.config == Path(tmpdir) / paths.data / "config.yaml"
    True
    """

    root: Path
    _paths: MutableMapping[str, str | Path]

    def __repr__(self) -> str:
        data = {"root": self.root, **self._paths}
        return f"{self.__class__.__name__}({data})"

    def __init__(self, root: str | Path, **kwargs: str | Path) -> None:
        self.__dict__["root"] = Path(root).absolute()
        self.__dict__["_paths"] = kwargs.copy()

    def __getattr__(self, attr: str) -> Path:
        path = Path(self._paths[attr])
        orig, *rest = path.parts
        if orig.startswith("@"):
            path = Path(getattr(self, orig.removeprefix("@")), *rest)
        return path if path.is_absolute() else self.root / path

    def __setattr__(self, attr: str, path: str | Path) -> None:
        self._paths[attr] = Path(path)

    def __delattr__(self, attr: str) -> None:
        del self._paths[attr]


class PathsAux(Paths):
    """Paths manager for the auxiliary _Bourgeoisie_ data."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.properties = Path("properties.xlsx")
        self.prices = Path("prices.xlsx")
        self.corrections = Path("corrections.xlsx")
        self.merging = Path("merging.xlsx")


class PathsRaw(Paths):
    """Paths manager for the raw _Bourgeoisie_ data."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.companies = Path("companies.tsv.gz")
        self.properties = Path("properties.tsv.gz")
        self.relations = Path("relations.tsv.gz")
        self.entities = Path("entities.tsv.gz")


class PathsProc(Paths):
    """Paths manager for the processed ``KINGPOL_INDUSTRY`` data."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.conversions = Path("conversions.parquet")
        self.prices = Path("prices.parquet")
        self.currencies = Path("currencies.parquet")
        self.properties = Path("properties.parquet")
        self.industries = Path("industries.parquet")
        self.records = Path("records.parquet")
        self.yearly = Path("yearly.parquet")
        self.companies = Path("companies.parquet")
        self.entities = Path("entities.parquet")
        self.relations = Path("relations.parquet")
        self.shares = Path("shares.parquet")
        self.ranking = Path("ranking.parquet")
        self.groups = Path("groups.parquet")
        self.excel = Path("kingpol.xlsx")
        self.tables = Path("tables.xlsx")


class PathsContainer:
    """Paths container.

    Attributes
    ----------
    raw
        Paths to raw data.
    proc
        Paths to processed data.
    """

    def __init__(self, datadir: str | Path) -> None:
        datadir = Path(datadir)
        self.aux = PathsAux(datadir / "aux")
        self.raw = PathsRaw(datadir / "raw")
        self.proc = PathsProc(datadir / "proc")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(raw={self.raw}, proc={self.proc})"
