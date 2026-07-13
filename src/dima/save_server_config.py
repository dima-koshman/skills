import collections.abc
import concurrent.futures
import inspect
import os
import typing

import consul  # pyright: ignore[reportMissingTypeStubs]
import pydantic
import pyperclip
import rich
import yaml

CONSUL_HOST = os.environ["CONSUL_HOST"]
CONSUL_TOKEN = os.environ["CONSUL_TOKEN"]
CONSUL_CONFIG_LOADER_APP = os.environ["CONSUL_CONFIG_LOADER_APP"]
CONSUL_PROD_HOST = os.environ["CONSUL_PROD_HOST"]
CONSUL_PROD_READ_TOKEN_TOKEN = os.environ["CONSUL_PROD_READ_TOKEN_TOKEN"]

CONSUL_KEY_TEMPLATE = (
    f"config/prometheus-kafka-exporter/{CONSUL_CONFIG_LOADER_APP}_{{}}.yaml"
)
CONSUL_PROD_KEY = f"config/aiplatform/{CONSUL_CONFIG_LOADER_APP}/application-prod.yaml"
CONSUL_CONFIG_LOADER_URL = f"https://gitlab.kapitalbank.az/DevOps-Projects/devops-services/ai-automations/consul-config-loader/-/tree/main/config/aiplatform/{CONSUL_CONFIG_LOADER_APP}"

VAULT_URL = os.getenv("VAULT_URL", "")
VAULT_VERSION = os.getenv("VAULT_VERSION", "")
VAULT_ROLE_ID = os.getenv("VAULT_ROLE_ID", "")
VAULT_SECRET_ID = os.getenv("VAULT_SECRET_ID", "")


def save_config(
    config_dict: collections.abc.Mapping[str, object],
    config_id: str,
    Config: type[pydantic.BaseModel],
    prod_config_id: str = "prod",
) -> None:
    config = Config(**config_dict)
    if config_id != prod_config_id:
        _save_config(config=config_dict, config_id=config_id)
        return

    _ensure_no_non_empty_secret_values(config)
    rich.print(
        f"[yellow]Cannot write prod config via API. Config saved to clipboard, create mr in {CONSUL_CONFIG_LOADER_URL}[/yellow]",
        flush=True,
    )
    pyperclip.copy(yaml.safe_dump(config_dict))
    prod_env_vars = f"""
        CONSUL_HOST={CONSUL_PROD_HOST}
        CONSUL_KEY={CONSUL_PROD_KEY}
        CONSUL_TOKEN={CONSUL_PROD_READ_TOKEN_TOKEN}
        VAULT_URL={VAULT_URL}
        VAULT_VERSION={VAULT_VERSION}
        VAULT_ROLE_ID={VAULT_ROLE_ID}
        VAULT_SECRET_ID={VAULT_SECRET_ID}
    """
    rich.print(inspect.cleandoc(prod_env_vars))

    if input("Press 'y' to verify the config was saved to Consul...") == "y":
        fetched_config = load_config(
            host=CONSUL_PROD_HOST,
            token=CONSUL_PROD_READ_TOKEN_TOKEN,
            key=CONSUL_PROD_KEY,
            Config=Config,
        )
        if fetched_config != config:
            raise ValueError(
                f"Config does not match the saved config\n{fetched_config.model_dump_json(indent=2, ensure_ascii=False)}"
            )
        else:
            rich.print("[green]Saved config matches the fetched config.[/green]")


def _save_config(config: collections.abc.Mapping[str, object], config_id: str) -> None:
    host = CONSUL_HOST
    key = CONSUL_KEY_TEMPLATE.format(config_id)
    token = CONSUL_TOKEN
    consul = Consul(host=host, token=token, verify=False)
    consul.put_yaml(key=key, value=config)
    print(f"Config saved to {key}")


def load_config(
    host: str,
    key: str,
    token: str,
    Config: type[pydantic.BaseModel],
) -> pydantic.BaseModel:
    consul = Consul(host=host, token=token, verify=False)
    config_dict = consul.get_yaml(key)
    if config_dict is None:
        raise ValueError(f"Config {key!r} was not found in Consul at {host!r}.")

    return Config(**config_dict)


def _ensure_no_non_empty_secret_values(config: object) -> None:
    values: list[object] = [config]
    while values:
        value = values.pop()
        if isinstance(value, pydantic.SecretStr):
            if value.get_secret_value():
                raise ValueError(
                    "Prod config cannot contain non-empty SecretStr values."
                )
            continue

        if isinstance(value, pydantic.BaseModel):
            values.extend(value.__dict__.values())
        elif isinstance(value, dict):
            values.extend(typing.cast(dict[object, object], value).values())
        elif isinstance(value, (list, tuple, set, frozenset)):
            values.extend(
                typing.cast(
                    list[object] | tuple[object, ...] | set[object] | frozenset[object],
                    value,
                )
            )


class Consul:
    def __init__(
        self,
        host: str,
        token: str | None = None,
        scheme: str = "https",
        port: int = 443,
        verify: bool = True,
        timeout: float = 5.0,
    ):
        self.host: str = host
        self.timeout: float = timeout
        self.client: "_ConsulClient" = typing.cast(
            "_ConsulClient",
            typing.cast(
                object,
                consul.Consul(
                    host=host, port=port, token=token, scheme=scheme, verify=verify
                ),
            ),
        )

    def get(self, key: str) -> bytes | None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.client.kv.get, key)
            try:
                _index, data = future.result(timeout=self.timeout)
            except TimeoutError as error:
                raise TimeoutError(
                    f"Consul at {self.host!r} did not respond within {self.timeout}s."
                ) from error

        return data["Value"] if data else None

    def get_yaml(self, key: str) -> dict[str, object] | None:
        value = self.get(key)
        if not value:
            return None

        return typing.cast(dict[str, object], yaml.safe_load(value.decode("utf-8")))

    def put_yaml(self, key: str, value: collections.abc.Mapping[str, object]) -> None:
        _ = self.client.kv.put(key, yaml.safe_dump(value))


class _ConsulKv(typing.Protocol):
    def get(self, key: str) -> tuple[object, dict[str, bytes] | None]: ...

    def put(self, key: str, value: str) -> object: ...


class _ConsulClient(typing.Protocol):
    kv: _ConsulKv
