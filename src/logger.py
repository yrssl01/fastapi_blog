import logging 
import yaml
from logging.config import dictConfig


with open("logging.yaml", "rt") as f:
    config = yaml.safe_load(f.read())


dictConfig(config)


logger = logging.getLogger("app")
