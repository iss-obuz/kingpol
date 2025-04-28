import dvc.api
from omegaconf import OmegaConf

params = OmegaConf.create(dvc.api.params_show())
