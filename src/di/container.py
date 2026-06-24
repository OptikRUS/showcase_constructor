from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.di.providers.database import DatabaseProvider
from src.di.providers.general import GeneralProvider
from src.di.providers.showcases import ShowcaseProvider


def create_container() -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        DatabaseProvider(),
        GeneralProvider(),
        ShowcaseProvider(),
    )
