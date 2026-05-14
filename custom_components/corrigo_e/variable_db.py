"""Variable database loader for Regin Corrigo E."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

_VARS_PATH = os.path.join(os.path.dirname(__file__), "variables", "CorrigoEVentilation.variables")


@dataclass
class VarRecord:
    name: str
    ref: str
    rw: bool
    unit: str
    fmt: Optional[int]
    values: dict[int, str]
    visible_if: str
    group: str

    @property
    def datatype(self) -> str:
        return self.ref.split(",")[-1].upper()

    @property
    def ln(self) -> int:
        return int(self.ref.split(",")[1])


def _parse_values(s: str) -> dict[int, str]:
    result: dict[int, str] = {}
    if not s.strip():
        return result
    for part in s.split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        idx, _, label = part.partition("=")
        try:
            result[int(idx.strip())] = label.strip()
        except ValueError:
            pass
    return result


def load_variables(path: str = _VARS_PATH) -> list[VarRecord]:
    records: list[VarRecord] = []
    current_group = ""
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current_group = line[1:-1]
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 3:
                continue
            while len(parts) < 7:
                parts.append("")
            name, ref, rw_s, unit, fmt_s, values_s, visible_if = parts[:7]
            records.append(VarRecord(
                name=name,
                ref=ref,
                rw=(rw_s.lower() == "rw"),
                unit=unit,
                fmt=int(fmt_s) if fmt_s.strip().lstrip("-").isdigit() else None,
                values=_parse_values(values_s),
                visible_if=visible_if.strip(),
                group=current_group,
            ))
    return records


def load_unique_variables(path: str = _VARS_PATH) -> list[VarRecord]:
    """Load variables, keeping only the first occurrence of each ref."""
    seen: set[str] = set()
    result: list[VarRecord] = []
    for var in load_variables(path):
        if var.ref not in seen:
            seen.add(var.ref)
            result.append(var)
    return result
