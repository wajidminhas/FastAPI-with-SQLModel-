

from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
    
except FileNotFoundError:
    config = Config()

DATABASE_URL_POSTGRES= config("DATABASE_URL_POSTGRES", cast=Secret)

TODO_DATABASE_URL = config("TODO_DATABASE_URL", cast=Secret)

TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)