from typing import Type, Any, Optional
from dataclasses import dataclass
import dataclasses
import typing

from quickforex.providers.base import ProviderBase
import quickforex.utils


@dataclass
class SettingFieldDescription:
    class NoDefault(object):
        pass

    name: str
    required: bool
    nullable: bool
    default_value: Any
    setting_type: Type

    @property
    def has_default(self):
        return self.default_value is not self.NoDefault

    def parse_str_override(self, override_str: str) -> Any:
        override_str = override_str.strip()
        if self.nullable and override_str in {"null", "None"}:
            return None
        if self.setting_type is bool:
            override_str = override_str.lower()
            return True if override_str in {"true", "1", "yes"} else False
        return self.setting_type(override_str)

    @staticmethod
    def from_dataclass_field(field: dataclasses.Field) -> "SettingFieldDescription":
        is_optional_type = quickforex.utils.is_optional_type(field.type)
        return SettingFieldDescription(
            name=field.name,
            required=quickforex.utils.is_dataclass_field_required(field),
            nullable=is_optional_type,
            default_value=(
                quickforex.utils.get_dataclass_field_default_value(field)
                if quickforex.utils.dataclass_field_has_default(field)
                else SettingFieldDescription.NoDefault
            ),
            setting_type=(
                quickforex.utils.extract_optional_type(field.type)
                if is_optional_type
                else field.type
            ),
        )


@dataclass
class ProviderMetadata:
    identifier: str
    description: str
    settings_type: Optional[Type]

    @property
    def settings_required(self) -> bool:
        return self.settings_type and any(
            field.required for field in self.settings_schema
        )

    @property
    def exposes_settings(self) -> bool:
        return self.settings_type is not None

    @property
    def required_settings_fields(self) -> list[SettingFieldDescription]:
        return [field for field in self.settings_schema if field.required]

    @property
    def settings_schema(self) -> Optional[list[SettingFieldDescription]]:
        if not self.settings_type:
            return None
        return [
            SettingFieldDescription.from_dataclass_field(field)
            for field in dataclasses.fields(self.settings_type)
        ]

    @staticmethod
    def from_provider_type(provider_type: Type[ProviderBase]) -> "ProviderMetadata":
        return ProviderMetadata(
            identifier=provider_type.identifier,
            description=provider_type.__doc__.strip(),
            settings_type=_infer_provider_settings_type(provider_type),
        )


def _infer_provider_settings_type(provider_type: Type[ProviderBase]) -> Optional[Type]:
    type_hints = typing.get_type_hints(provider_type.__init__)
    if "settings" not in type_hints:
        return None
    raw_settings_type = type_hints["settings"]
    return (
        quickforex.utils.extract_optional_type(raw_settings_type)
        if quickforex.utils.is_optional_type(raw_settings_type)
        else raw_settings_type
    )
