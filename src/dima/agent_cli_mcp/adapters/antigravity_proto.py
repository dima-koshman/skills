"""Minimal observed Step fields; unknown protobuf fields remain uninterpreted.

Field numbers were cross-checked against the published observations at
https://github.com/xhluca/session-migrate/blob/main/docs/antigravity-format.md.
This is a read-only projection, not a schema for writing native histories.
"""

import collections.abc
import typing

import google.protobuf.descriptor_pb2
import google.protobuf.message
import google.protobuf.message_factory


class User(typing.Protocol):
    text: str


class Call(typing.Protocol):
    id: str
    name: str
    arguments: str


class Planner(typing.Protocol):
    text: str
    id: str
    calls: collections.abc.Sequence[Call]


class Result(typing.Protocol):
    text: str


class Tool(typing.Protocol):
    result: Result


class Step(typing.Protocol):
    """The Step fields this projection declares; the message class is built at runtime."""

    type: int
    status: int
    user: User
    planner: Planner
    tool: Tool

    def HasField(self, field_name: str) -> bool: ...


def parse_step(payload: bytes) -> Step:
    """Decode a Step; raises google.protobuf.message.DecodeError on invalid bytes."""
    return typing.cast(Step, typing.cast(object, _STEP_CLASS.FromString(payload)))


def _step_class() -> type[google.protobuf.message.Message]:
    field_proto = google.protobuf.descriptor_pb2.FieldDescriptorProto
    schema = google.protobuf.descriptor_pb2.FileDescriptorProto(
        name="dima_antigravity_step.proto", package="dima.agy", syntax="proto3"
    )
    definitions = {
        "User": [(2, "text", "string", False)],
        "Call": [
            (1, "id", "string", False),
            (2, "name", "string", False),
            (3, "arguments", "string", False),
        ],
        "Planner": [
            (1, "text", "string", False),
            (6, "id", "string", False),
            (7, "calls", "Call", True),
        ],
        "Result": [(1, "text", "string", False)],
        "Entry": [(1, "key", "string", False), (2, "value", "string", False)],
        "Tool": [(1, "arguments", "Entry", True), (2, "result", "Result", False)],
        "Step": [
            (1, "type", "int32", False),
            (4, "status", "int32", False),
            (19, "user", "User", False),
            (20, "planner", "Planner", False),
            (140, "tool", "Tool", False),
        ],
    }
    for name, fields in definitions.items():
        message = schema.message_type.add(name=name)
        for number, field_name, typ, repeated in fields:
            field = message.field.add(
                name=field_name,
                number=number,
                label=(
                    field_proto.LABEL_REPEATED
                    if repeated
                    else field_proto.LABEL_OPTIONAL
                ),
            )
            if typ == "string":
                field.type = field_proto.TYPE_STRING
            elif typ == "int32":
                field.type = field_proto.TYPE_INT32
            else:
                field.type, field.type_name = (
                    field_proto.TYPE_MESSAGE,
                    f".dima.agy.{typ}",
                )
    # Without a pool argument, the schema is built in a fresh private pool.
    return google.protobuf.message_factory.GetMessages([schema])["dima.agy.Step"]


_STEP_CLASS = _step_class()
