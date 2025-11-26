# envsnap/python_core/format.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import json


def _fmt_list(items: Optional[List[str]]) -> str:
    if not items:
        return "（未取得）"
    return ", ".join([x for x in items if x]) or "（未取得）"


def _fmt_optional(value: Any) -> str:
    if value is None:
        return "（未取得）"
    if isinstance(value, str) and not value.strip():
        return "（未取得）"
    return str(value)


def to_text(report: Dict[str, Any]) -> str:
    ts = report.get("timestamp")
    try:
        ts_display = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "（不明）"
    except Exception:
        ts_display = _fmt_optional(ts)

    lines: List[str] = []
    lines.append(f"EnvSnap Report: {ts_display}")
    lines.append("")
    lines.append(f"OS:      {_fmt_optional(report.get('os_name'))} {_fmt_optional(report.get('os_version'))}")
    lines.append(f"Arch:    {_fmt_optional(report.get('arch'))}")
    lines.append(f"Device:  {_fmt_optional(report.get('device_model'))}")
    lines.append(f"Host:    {_fmt_optional(report.get('hostname'))}")
    lines.append("")
    lines.append(f"CPU:     {_fmt_optional(report.get('cpu'))}")
    lines.append(f"Memory:  {_fmt_optional(report.get('memory_gb'))} GB")
    lines.append(f"GPU:     {_fmt_list(report.get('gpus'))}")
    lines.append("")
    lines.append(f"TZ:      {_fmt_optional(report.get('timezone'))}")
    lines.append(f"Locale:  {_fmt_optional(report.get('locale'))}")
    lines.append("")
    lines.append("Notes:")
    lines.append("- This report intentionally excludes identifiers (serial/MAC/UUID).")
    return "\n".join(lines) + "\n"


def to_json(report: Dict[str, Any], pretty: bool = True) -> str:
    if pretty:
        return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(report, ensure_ascii=False) + "\n"