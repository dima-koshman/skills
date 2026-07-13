import os

import pydantic
import pyperclip
import pytest

for env_var in (
    "CONSUL_HOST",
    "CONSUL_TOKEN",
    "CONSUL_CONFIG_LOADER_APP",
    "CONSUL_PROD_HOST",
    "CONSUL_PROD_READ_TOKEN_TOKEN",
):
    _ = os.environ.setdefault(env_var, "test")

import dima.save_server_config as save_server_config  # noqa: E402


class ConfigWithSecret(pydantic.BaseModel):
    token: pydantic.SecretStr


class NestedConfigWithSecret(pydantic.BaseModel):
    settings: dict[str, ConfigWithSecret]


def test_save_config_rejects_non_empty_secret_str(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_copy(_value: str) -> None:
        raise AssertionError(
            "clipboard should not be used when prod config contains secrets"
        )

    monkeypatch.setattr(pyperclip, "copy", fail_copy)

    with pytest.raises(ValueError, match="SecretStr"):
        save_server_config.save_config(
            config_dict={"settings": {"service": {"token": "secret"}}},
            config_id="prod",
            Config=NestedConfigWithSecret,
        )


def test_save_config_allows_empty_secret_str(monkeypatch: pytest.MonkeyPatch) -> None:
    copied_values: list[str] = []
    config_dict: dict[str, str] = {"token": ""}

    def decline_verification(_prompt: str) -> str:
        return "n"

    monkeypatch.setattr(pyperclip, "copy", copied_values.append)
    monkeypatch.setattr("builtins.input", decline_verification)

    save_server_config.save_config(
        config_dict=config_dict,
        config_id="prod",
        Config=ConfigWithSecret,
    )

    assert copied_values
