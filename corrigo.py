#!/usr/bin/env python3
"""
corrigo.py — command-line tool for Regin Corrigo E ventilation controllers.

Usage:
  corrigo.py HOST read  VAR [VAR ...]    read by name or ref
  corrigo.py HOST write VAR VALUE        write by name or ref
  corrigo.py HOST list  [FILTER]         list known variables
  corrigo.py HOST dump  [GROUP]          read all readable variables

Options:
  --port PORT     TCP port (default 26486)
  --ela  ELA      End Layer Address (default 30)
  --vars FILE     path to .variables file
  --json          output JSON Lines
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Optional

# Locate the default variables file next to this script.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_VARS = os.path.join(_SCRIPT_DIR, "CorrigoEVentilation.variables")


# ---------------------------------------------------------------------------
# Variables file
# ---------------------------------------------------------------------------

@dataclass
class VarRecord:
    name: str
    ref: str          # e.g. "V,3,0x1E9,X"
    rw: bool          # True = read-write, False = read-only
    unit: str         # "" if dimensionless
    fmt: Optional[int]  # decimal places, None if not applicable
    values: dict      # {int: str} for enum labels, {} otherwise
    visible_if: str   # ref string or ""
    group: str        # "Section > Subsection"


def _parse_values(s: str) -> dict:
    """Parse '0=Off;1=On;2=Auto' into {0: 'Off', 1: 'On', 2: 'Auto'}."""
    result = {}
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


def load_variables(path: str) -> list[VarRecord]:
    records = []
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
            # Pad to 7 fields
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


# ---------------------------------------------------------------------------
# Variable lookup
# ---------------------------------------------------------------------------

def _looks_like_ref(s: str) -> bool:
    """True if the string looks like a raw ref (e.g. 'V,3,0x1E9,X')."""
    return "," in s and ("0x" in s.lower() or s.count(",") >= 3)


def find_vars(records: list[VarRecord], query: str) -> list[VarRecord]:
    """Return matching VarRecords for a name substring or exact ref."""
    if _looks_like_ref(query):
        # Normalise by upper-casing the hex part for comparison
        q = query.strip()
        return [r for r in records if r.ref.upper() == q.upper()]
    q = query.lower()
    return [r for r in records if q in r.name.lower()]


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _label(rec: VarRecord, value) -> str:
    """Return the enum label for an integer value, or '' if not applicable."""
    if rec.values and isinstance(value, (int, bool)):
        return rec.values.get(int(value), "")
    return ""


def _format_value(rec: VarRecord, value) -> str:
    """Format a raw value for human display."""
    if isinstance(value, float):
        if rec.fmt is not None:
            return f"{value:.{rec.fmt}f}"
        return f"{value:g}"
    if isinstance(value, bool):
        return "1" if value else "0"
    return str(value)


def _human_line(rec: VarRecord, value) -> str:
    parts = [f"{rec.group} > {rec.name}:"]
    parts.append(_format_value(rec, value))
    if rec.unit:
        parts.append(rec.unit)
    lbl = _label(rec, value)
    if lbl:
        parts.append(f"({lbl})")
    return " ".join(parts)


def _json_line(rec: VarRecord, value) -> str:
    raw = value
    if isinstance(raw, bool):
        raw = int(raw)
    obj = {
        "group": rec.group,
        "name": rec.name,
        "ref": rec.ref,
        "value": raw,
        "unit": rec.unit or None,
        "label": _label(rec, value) or None,
    }
    return json.dumps(obj, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_read(args, records, ctrl):
    found_any = False
    for query in args.var:
        matches = find_vars(records, query)
        if not matches:
            print(f"error: no variable matches {query!r}", file=sys.stderr)
            sys.exit(1)
        for rec in matches:
            found_any = True
            try:
                value = ctrl.read(rec.ref)
            except Exception as e:
                print(f"error reading {rec.ref}: {e}", file=sys.stderr)
                continue
            if args.json:
                print(_json_line(rec, value))
            else:
                print(_human_line(rec, value))
    if not found_any:
        sys.exit(1)


def cmd_write(args, records, ctrl):
    matches = find_vars(records, args.var)
    if not matches:
        print(f"error: no variable matches {args.var!r}", file=sys.stderr)
        sys.exit(1)
    if len(matches) > 1:
        print(f"error: {len(matches)} variables match {args.var!r}; use an exact ref:", file=sys.stderr)
        for r in matches:
            print(f"  {r.ref}  {r.group} > {r.name}", file=sys.stderr)
        sys.exit(1)
    rec = matches[0]
    if not rec.rw:
        print(f"error: {rec.name!r} is read-only", file=sys.stderr)
        sys.exit(1)

    # Parse value according to the datatype in the ref
    datatype = rec.ref.split(",")[-1].upper()
    raw = args.value
    try:
        if datatype == "R":
            value = float(raw)
        elif datatype in ("I", "X"):
            value = int(raw, 0) if raw.startswith("0x") or raw.startswith("0X") else int(raw)
        elif datatype == "L":
            if raw.lower() in ("1", "true", "on", "yes"):
                value = True
            elif raw.lower() in ("0", "false", "off", "no"):
                value = False
            else:
                raise ValueError(f"expected 0/1/true/false, got {raw!r}")
        else:
            value = raw
    except ValueError as e:
        print(f"error: bad value for {datatype} type: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        ctrl.write(rec.ref, value)
    except Exception as e:
        print(f"error writing {rec.ref}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps({"group": rec.group, "name": rec.name, "ref": rec.ref,
                          "written": value if not isinstance(value, bool) else int(value)}))
    else:
        lbl = _label(rec, value)
        suffix = f" ({lbl})" if lbl else ""
        print(f"OK  {rec.group} > {rec.name} = {_format_value(rec, value)}{' ' + rec.unit if rec.unit else ''}{suffix}")


def cmd_list(args, records):
    query = args.filter.lower() if args.filter else ""
    shown = 0
    for rec in records:
        if query and query not in rec.name.lower() and query not in rec.group.lower():
            continue
        rw_s = "r/w" if rec.rw else "r  "
        unit_s = rec.unit if rec.unit else "-"
        if args.json:
            obj = {"group": rec.group, "name": rec.name, "ref": rec.ref,
                   "rw": rec.rw, "unit": rec.unit or None, "visible_if": rec.visible_if or None}
            print(json.dumps(obj, ensure_ascii=False))
        else:
            print(f"{rw_s}  {rec.ref:<20}  {rec.group} > {rec.name}  [{unit_s}]")
        shown += 1
    if shown == 0:
        print(f"(no variables match {args.filter!r})", file=sys.stderr)


def cmd_dump(args, records, ctrl):
    group_filter = args.group.lower() if args.group else ""
    from libexolink import EXONakError

    for rec in records:
        if group_filter and group_filter not in rec.group.lower():
            continue
        try:
            value = ctrl.read(rec.ref)
        except EXONakError:
            continue
        except Exception as e:
            print(f"error reading {rec.ref} ({rec.name}): {e}", file=sys.stderr)
            continue

        if args.json:
            print(_json_line(rec, value))
        else:
            print(_human_line(rec, value))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="corrigo.py",
        description="Command-line tool for Regin Corrigo E ventilation controllers.",
    )
    parser.add_argument("host", help="Controller IP address or hostname")
    parser.add_argument("--port", type=int, default=26486, help="TCP port (default 26486)")
    parser.add_argument("--ela", type=int, default=30, help="End Layer Address (default 30)")
    parser.add_argument("--vars", default=_DEFAULT_VARS, metavar="FILE",
                        help="path to .variables file")
    parser.add_argument("--json", action="store_true", help="output JSON Lines")

    sub = parser.add_subparsers(dest="command", required=True)

    p_read = sub.add_parser("read", help="read one or more variables")
    p_read.add_argument("var", nargs="+", help="variable name (substring) or ref string")

    p_write = sub.add_parser("write", help="write a variable value")
    p_write.add_argument("var", help="variable name (unique match) or ref string")
    p_write.add_argument("value", help="value to write")

    p_list = sub.add_parser("list", help="list known variables")
    p_list.add_argument("filter", nargs="?", default="", help="optional substring filter")

    p_dump = sub.add_parser("dump", help="read all readable variables")
    p_dump.add_argument("group", nargs="?", default="", help="optional group substring filter")

    args = parser.parse_args()

    try:
        records = load_variables(args.vars)
    except FileNotFoundError:
        print(f"error: variables file not found: {args.vars}", file=sys.stderr)
        sys.exit(1)

    if args.command == "list":
        cmd_list(args, records)
        return

    # Commands that need a live connection
    sys.path.insert(0, _SCRIPT_DIR)
    try:
        from libexolink import EXOlink, EXOConnectionError
    except ImportError as e:
        print(f"error: cannot import libexolink: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with EXOlink(args.host, port=args.port, ela=args.ela) as ctrl:
            if args.command == "read":
                cmd_read(args, records, ctrl)
            elif args.command == "write":
                cmd_write(args, records, ctrl)
            elif args.command == "dump":
                cmd_dump(args, records, ctrl)
    except EXOConnectionError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
