import pathlib

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DirSettings(BaseSettings):
    ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent.parent
    SRC: pathlib.Path = ROOT / "src"

    model_config = SettingsConfigDict(env_prefix="DIR_")


class Constants(BaseSettings):
    DIRS: DirSettings = Field(default_factory=DirSettings)


constants = Constants()
