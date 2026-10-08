"""Signed, revision-bound pagination without holding database transactions open."""

import base64
import hmac
import secrets
import time
import typing

import pydantic

from .models import ChatError, Model

RequestT = typing.TypeVar("RequestT", bound=Model)


class Cursors:
    def __init__(self):
        self._key: bytes = secrets.token_bytes(32)

    def encode(
        self, method: str, revision: int, request: Model, position: dict[str, int]
    ) -> str:
        payload = (
            _Payload(
                method=method,
                revision=revision,
                expires=time.time() + 300,
                request=request.model_dump(mode="json", exclude={"cursor"}),
                position=position,
            )
            .model_dump_json()
            .encode()
        )
        signature = hmac.digest(self._key, payload, "sha256")
        return base64.urlsafe_b64encode(signature + payload).decode()

    def decode(
        self, token: str, method: str, revision: int, request: RequestT
    ) -> tuple[RequestT, dict[str, int]]:
        try:
            raw = base64.b64decode(token, altchars=b"-_", validate=True)
            signature, payload = raw[:32], raw[32:]
            if not hmac.compare_digest(
                signature, hmac.digest(self._key, payload, "sha256")
            ):
                raise ValueError("signature")
            data = _Payload.model_validate_json(payload)
            if data.method != method:
                raise ValueError("tool")
            if data.expires < time.time() or data.revision != revision:
                raise ChatError(
                    "CURSOR_EXPIRED",
                    "The index changed or this cursor expired; repeat the original request",
                )
            values = typing.cast(
                dict[str, object], request.model_dump(mode="json", exclude={"cursor"})
            )
            if any(
                values[key] != data.request.get(key)
                for key in request.model_fields_set - {"cursor"}
            ):
                raise ValueError("arguments")
            return type(request).model_validate(data.request), data.position
        except ChatError:
            raise
        except (ValueError, KeyError, TypeError):
            raise ChatError(
                "INVALID_CURSOR",
                "Use an unmodified cursor with its original tool and arguments",
            ) from None


class _Payload(pydantic.BaseModel):
    method: str
    revision: int
    expires: float
    request: dict[str, object]
    position: dict[str, int]
