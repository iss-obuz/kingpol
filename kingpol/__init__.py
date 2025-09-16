from pathlib import Path

from dvc.repo import Repo

from .__about__ import __version__
from .config import params
from .dataset import PathsContainer

paths = PathsContainer(Path(Repo().root_dir) / "data")
