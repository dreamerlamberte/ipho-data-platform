"""Column-level PII transforms applied before data reaches the lake."""

from __future__ import annotations

import hashlib
import hmac

import pyarrow as pa
import pyarrow.compute as pc


def pseudonymize(value: str | None, salt: bytes) -> str | None:
    if value is None or value == "":
        return value
    return hmac.new(salt, value.encode("utf-8"), hashlib.sha256).hexdigest()[:24]


def apply_policy(table: pa.Table, policy: dict[str, str], salt: bytes) -> pa.Table:
    for column, action in policy.items():
        if column not in table.column_names:
            raise KeyError(f"PII policy references unknown column {column!r}")
        idx = table.column_names.index(column)
        values = table.column(column)

        if action == "drop":
            table = table.remove_column(idx)
            continue
        if action == "hash":
            new = pa.array([pseudonymize(v, salt) for v in values.to_pylist()], pa.string())
        elif action == "year_only":
            new = pc.utf8_slice_codeunits(values, 0, 4)
        elif action == "presence":
            new = pc.cast(pc.greater(pc.utf8_length(pc.fill_null(values, "")), 0), pa.string())
        else:
            raise ValueError(f"Unknown PII action {action!r} for column {column!r}")
        table = table.set_column(idx, column, new)
    return table
