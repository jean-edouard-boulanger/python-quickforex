from typing import Type, Any, Optional

from quickforex.errors import QuickForexError
from quickforex.providers.base import ProviderBase
from quickforex.providers.provider_metadata import (
    ProviderMetadata,
    SettingFieldDescription,
)


class AlreadyRegisteredProviderError(QuickForexError):
    def __init__(self, provider_id: str):
        super().__init__(
            f"provider with identifier '{provider_id}' was already registered"
        )


class MissingProviderError(QuickForexError):
    def __init__(self, provider_id: str):
        super().__init__(f"provider with identifier '{provider_id}' does not exist")


class Directory(object):
    def __init__(self):
        self._providers: dict[str, Type[ProviderBase]] = {}

    def register(self, provider_type: Type[ProviderBase]):
        provider_id = provider_type.identifier
        if provider_id in self._providers:
            raise AlreadyRegisteredProviderError(provider_id)
        self._providers[provider_id] = provider_type

    def is_registered(self, provider_id: str) -> bool:
        return provider_id in self._providers

    def get_provider_type(self, provider_id: str) -> Type[ProviderBase]:
        if not self.is_registered(provider_id):
            raise MissingProviderError(provider_id)
        return self._providers[provider_id]

    def get_provider_metadata(self, provider_id: str) -> ProviderMetadata:
        provider_type = self.get_provider_type(provider_id)
        return ProviderMetadata.from_provider_type(provider_type)

    def create(
        self, provider_id: str, settings_overrides: Optional[dict[str, Any]] = None
    ):
        meta = self.get_provider_metadata(provider_id)
        provider_type = self.get_provider_type(provider_id)
        if settings_overrides and not meta.settings_type:
            raise QuickForexError(
                f"provider '{meta.identifier}' does not accept settings"
            )
        if meta.settings_required:
            if not settings_overrides:
                raise QuickForexError(
                    f"provider '{meta.identifier}' expects settings but none were provided"
                )
            missing_settings: list[SettingFieldDescription] = [
                field
                for field in meta.settings_schema
                if field.name not in settings_overrides
            ]
            if missing_settings:
                raise QuickForexError(
                    f"provider '{meta.identifier}' expects the following settings which were not "
                    f"provided: {', '.join(s.name for s in missing_settings)}"
                )
        provider_kwargs = {"settings": None}
        if meta.settings_type:
            settings_overrides = settings_overrides or {}
            provider_kwargs["settings"] = meta.settings_type(**settings_overrides)
        return provider_type(**provider_kwargs)

    @property
    def available_providers(self) -> list[ProviderMetadata]:
        return [
            self.get_provider_metadata(provider_id)
            for provider_id in self._providers.keys()
        ]


_DIRECTORY = Directory()


def registered_provider(provider_type: Type[ProviderBase]) -> Type[ProviderBase]:
    _DIRECTORY.register(provider_type)
    return provider_type


def get_available_providers() -> list[ProviderMetadata]:
    return _DIRECTORY.available_providers


def get_provider_metadata(provider_id: str) -> ProviderMetadata:
    return _DIRECTORY.get_provider_metadata(provider_id)


def provider_exists(provider_id: str) -> bool:
    return _DIRECTORY.is_registered(provider_id)


def create_provider(
    provider_id: str, settings_overrides: Optional[dict[str, Any]] = None
):
    return _DIRECTORY.create(provider_id, settings_overrides)
