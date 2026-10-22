import collections.abc
import concurrent.futures
import inspect
import os
import shlex
import typing

import consul  # pyright: ignore[reportMissingTypeStubs]
import pydantic
import pyperclip
import rich
import yaml

# Name of the app config
CONSUL_CONFIG_LOADER_APP = os.environ["CONSUL_CONFIG_LOADER_APP"]
CONSUL_CONFIG_LOADER_URL = f"https://gitlab.kapitalbank.az/DevOps-Projects/devops-services/ai-automations/consul-config-loader/-/tree/main/config/aiplatform/{CONSUL_CONFIG_LOADER_APP}"

VAULT_URL = os.getenv("VAULT_URL", "")
VAULT_VERSION = os.getenv("VAULT_VERSION", "")
VAULT_ROLE_ID = os.getenv("VAULT_ROLE_ID", "")
VAULT_SECRET_ID = os.getenv("VAULT_SECRET_ID", "")


def is_debug_config(config_id: str) -> bool:
    return config_id.lower() == "debug"


def get_consul_host(config_id: str) -> str:
    return (
        "cmap-pre.kapitalbank.az"
        if is_debug_config(config_id)
        else "cmap.kapitalbank.az"
    )


def get_consul_key(config_id: str) -> str:
    config_id = config_id.lower()
    return (
        f"config/prometheus-kafka-exporter/{CONSUL_CONFIG_LOADER_APP}_{config_id}.yaml"
        if is_debug_config(config_id)
        else f"config/aiplatform/{CONSUL_CONFIG_LOADER_APP}/application-{config_id}.yaml"
    )


def get_consul_read_token(config_id: str) -> str:
    return os.environ[f"CONSUL_{config_id.upper()}_READ_TOKEN"]


def get_consul_write_token(config_id: str) -> str:
    return os.environ[f"CONSUL_{config_id.upper()}_WRITE_TOKEN"]


def save_config(
    config_dict: collections.abc.Mapping[str, object],
    config_id: str,
    Config: type[pydantic.BaseModel],
) -> None:
    config = Config(**config_dict)
    if is_debug_config(config_id):
        _save_config_directly_to_consul(config=config_dict, config_id=config_id)
        return

    _ensure_no_non_empty_secret_values(config)
    rich.print(
        f"[yellow]Cannot write non-debug config via API. Config saved to clipboard, create mr in {CONSUL_CONFIG_LOADER_URL}[/yellow]",
        flush=True,
    )
    pyperclip.copy(yaml.safe_dump(config_dict))
    CONSUL_HOST = get_consul_host(config_id)
    CONSUL_KEY = get_consul_key(config_id)
    CONSUL_READ_TOKEN = get_consul_read_token(config_id)
    deployment_env_vars = f"""
        CONSUL_HOST={CONSUL_HOST}
        CONSUL_KEY={CONSUL_KEY}
        CONSUL_TOKEN={CONSUL_READ_TOKEN}
        VAULT_URL={VAULT_URL}
        VAULT_VERSION={VAULT_VERSION}
        VAULT_ROLE_ID={VAULT_ROLE_ID}
        VAULT_SECRET_ID={VAULT_SECRET_ID}
    """
    rich.print(inspect.cleandoc(deployment_env_vars))

    if input("Press 'y' to verify the config was saved to Consul...") == "y":
        fetched_config = load_config(
            host=CONSUL_HOST,
            token=CONSUL_READ_TOKEN,
            key=CONSUL_KEY,
            Config=Config,
        )
        if fetched_config != config:
            raise ValueError(
                f"Config does not match the saved config\n{fetched_config.model_dump_json(indent=2, ensure_ascii=False)}"
            )
        else:
            rich.print("[green]Saved config matches the fetched config.[/green]")


def _save_config_directly_to_consul(
    config: collections.abc.Mapping[str, object], config_id: str
) -> None:
    host = get_consul_host(config_id)
    key = get_consul_key(config_id)
    write_token = get_consul_write_token(config_id)
    consul = Consul(host=host, token=write_token, verify=False)
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
                raise ValueError("Config cannot contain non-empty SecretStr values.")
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
        self.client: _ConsulClient = typing.cast(
            _ConsulClient,
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


def build_secret_mappings(
    enter_enriched_environ_from_secret_store,
    SecretMapping: type[pydantic.BaseModel],
    Config: type[pydantic.BaseModel],
    secret_env_var_path_values: dict[str, str | None],
):
    """Build the config's secret mappings, verifying each one is readable from Vault.

    Maps every config field path to the Vault field of the same (prefixed) name under this
    app's secret, then reads them all back to prove the deployment will find them. If that
    fails, the values passed here are the ones that belong in Vault, so the raised error
    carries a ready ``vault`` CLI command an operator can copy and run to store them.
    """
    env_var_prefix = Config.model_config["env_prefix"]
    secret_mappings = [
        {
            "mount_point": "secret",
            "key": f"apollo/{CONSUL_CONFIG_LOADER_APP}",
            "payload_field": f"{env_var_prefix}{secret_env_var_path}",
            "env_var": f"{env_var_prefix}{secret_env_var_path}",
        }
        for secret_env_var_path in secret_env_var_path_values
    ]
    try:
        with enter_enriched_environ_from_secret_store(
            [SecretMapping(**secret_mapping) for secret_mapping in secret_mappings]
        ):
            pass
    except Exception as error:
        command = build_vault_write_command(secret_env_var_path_values)
        raise RuntimeError(
            f"{error}\n\nStore these secrets in Vault by running:\n\n{command}\n"
        ) from error

    return secret_mappings


def build_vault_write_command(
    Config: type[pydantic.BaseModel], secret_env_var_path_values: dict[str, str | None]
) -> str:
    """Build a copy-pasteable ``vault`` CLI command that stores every mapped secret.

    Writes every mapping rather than only the ones that failed to read: the write is
    idempotent, so re-storing a value Vault already holds leaves the same value there, and
    it keeps this independent of how the read failure was reported.

    A field with no value in this process is named in a comment instead of being written,
    so running the command unedited cannot overwrite a healthy Vault field with a
    placeholder.

    Uses ``kv patch``, never ``kv put``: the secret is shared and may hold fields belonging
    to other apps, which ``put`` would delete since it replaces the whole payload. The
    trade-off is that patch fails when the secret does not exist yet, which someone has to
    create by hand.
    """
    env_var_prefix = Config.model_config["env_prefix"]
    values_by_field = {
        f"{env_var_prefix}{secret_env_var_path}": value
        for secret_env_var_path, value in secret_env_var_path_values.items()
    }
    lines = []
    if vault_url := os.environ.get("VAULT_URL"):
        lines.append(f"export VAULT_ADDR={shlex.quote(vault_url)}")

    lines.append("# vault login  # skip if VAULT_TOKEN is already set")
    lines.extend(
        f"# No value available for {field}; add it to the command by hand."
        for field, value in values_by_field.items()
        if not value
    )
    arguments = " \\\n    ".join(
        shlex.quote(f"{field}={value}")
        for field, value in values_by_field.items()
        if value
    )
    if arguments:
        lines.append(
            f"vault kv patch -mount=secret {shlex.quote(f'apollo/{CONSUL_CONFIG_LOADER_APP}')} \\\n"
            f"    {arguments}"
        )

    return "\n".join(lines)
