from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.di.providers.admin_auth import AdminAuthProvider


def create_container() -> AsyncContainer:
    return make_async_container(FastapiProvider(), AdminAuthProvider())
