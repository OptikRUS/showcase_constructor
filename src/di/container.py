from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider


def create_container() -> AsyncContainer:
    return make_async_container(FastapiProvider())
