from pathlib import Path

from .__about__ import __version__
from .config import params
from .dataset import PathsContainer

paths = PathsContainer(Path(__file__).parent.parent / "data")
