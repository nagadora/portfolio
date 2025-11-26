# envsnap/python_core/collect.py
from __future__ import annotations

import argparse
import locale as pylocale
import os
import platform
import re
import socket
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# --- 重要：実行場所に依存せず同ディレクトリの format.py を読めるようにする ---
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from format import to_json, to_text  # noqa: E402


def _run(cmd: List[str], timeout: int = 6) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=timeout)
        return out.decode(errors="replace").strip()
    except Exception:
        return ""


def _run_ps(ps_command: str, timeout: int = 8) -> str:
    # Windows PowerShell
    return _run(["powershell", "-NoProfile", "-Command", ps_command], timeout=timeout)


def _guess_timezone() -> str:
    try:
        return datetime.now().astimezone().tzname() or ""
    except Exception:
        return ""


def _norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _safe_locale_tag() -> Optional[str]:
    """
    Python 3.14+ で locale.getdefaultlocale() が将来的に不安定になりやすいので、
    例外に強い方法で locale を取得する。
    """
    try:
        # ユーザー環境に合わせてロケールを初期化（失敗しても無視）
        try:
            pylocale.setlocale(pylocale.LC_ALL, "")
        except Exception:
            pass

        loc = pylocale.getlocale()[0]  # 例: 'ja_JP'
        if loc and str(loc).strip():
            return str(loc).strip()
    except Exception:
        pass
    return None


def _collect_windows() -> Dict[str, Any]:
    cpu = _norm_space(_run_ps("(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name)"))
    model = _norm_space(_run_ps("(Get-CimInstance Win32_ComputerSystem | Select-Object -First 1 -ExpandProperty Model)"))

    mem_bytes_s = _norm_space(
        _run_ps("(Get-CimInstance Win32_ComputerSystem | Select-Object -First 1 -ExpandProperty TotalPhysicalMemory)")
    )
    memory_gb: Optional[float] = None
    try:
        mem_bytes = int(mem_bytes_s)
        memory_gb = round(mem_bytes / (1024 ** 3), 2)
    except Exception:
        memory_gb = None

    gpus_raw = _run_ps("(Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name)")
    gpus: List[str] = []
    if gpus_raw:
        for line in gpus_raw.splitlines():
            line = _norm_space(line)
            if line and line.lower() != "name":
                gpus.append(line)

    return {
        "cpu": cpu or None,
        "device_model": model or None,
        "memory_gb": memory_gb,
        "gpus": gpus or None,
    }


def _collect_macos() -> Dict[str, Any]:
    model = _norm_space(_run(["sysctl", "-n", "hw.model"]))
    mem_bytes_s = _norm_space(_run(["sysctl", "-n", "hw.memsize"]))
    memory_gb: Optional[float] = None
    try:
        memory_gb = round(int(mem_bytes_s) / (1024 ** 3), 2)
    except Exception:
        memory_gb = None

    cpu = _norm_space(_run(["sysctl", "-n", "machdep.cpu.brand_string"]))
    if not cpu:
        cpu = "Apple Silicon" if platform.machine().lower() in ("arm64", "aarch64") else ""

    sp = _run(["system_profiler", "SPDisplaysDataType"])
    gpus: List[str] = []
    if sp:
        for m in re.finditer(r"Chipset Model:\s*(.+)", sp):
            name = _norm_space(m.group(1))
            if name:
                gpus.append(name)

    return {
        "cpu": cpu or None,
        "device_model": model or None,
        "memory_gb": memory_gb,
        "gpus": gpus or None,
    }


def collect() -> Dict[str, Any]:
    os_name = platform.system()
    base: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "os_name": os_name,
        "os_version": platform.version(),
        "arch": platform.machine(),
        "hostname": socket.gethostname(),
        "timezone": _guess_timezone() or None,
        "locale": _safe_locale_tag(),
        "cpu": None,
        "device_model": None,
        "memory_gb": None,
        "gpus": None,
    }

    if os_name.lower() == "windows":
        base.update(_collect_windows())
    elif os_name.lower() == "darwin":
        base["os_name"] = "macOS"
        base["os_version"] = platform.mac_ver()[0] or base["os_version"]
        base.update(_collect_macos())
    else:
        base["cpu"] = platform.processor() or None

    return base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["json", "text"], default="text")
    parser.add_argument("--pretty", action="store_true", help="json整形")
    args = parser.parse_args()

    report = collect()
    if args.format == "json":
        print(to_json(report, pretty=bool(args.pretty)), end="")
    else:
        print(to_text(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())