import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CmdlineResult:
    ok: bool
    cmdline: Optional[str] = None
    error: Optional[str] = None
    source: Optional[str] = None


def is_process_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
            )
        except Exception:
            return False
        return str(pid) in (result.stdout or "")
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def _get_cmdline_linux(pid: int) -> CmdlineResult:
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            raw = f.read()
    except Exception as e:
        return CmdlineResult(ok=False, error=str(e), source="procfs")
    cmdline = raw.replace(b"\x00", b" ").decode("utf-8", errors="replace").strip()
    if not cmdline:
        return CmdlineResult(ok=False, error="empty cmdline", source="procfs")
    return CmdlineResult(ok=True, cmdline=cmdline, source="procfs")


def _get_cmdline_windows(pid: int) -> CmdlineResult:
    try:
        result = subprocess.run(
            ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine", "/VALUE"],
            capture_output=True,
            text=True,
        )
        out = (result.stdout or "").strip()
        if "CommandLine=" in out:
            cmdline = out.split("CommandLine=", 1)[1].strip()
            if cmdline:
                return CmdlineResult(ok=True, cmdline=cmdline, source="wmic")
    except Exception:
        pass

    try:
        ps = (
            "Get-CimInstance Win32_Process -Filter \"ProcessId="
            + str(pid)
            + "\" | Select-Object -ExpandProperty CommandLine"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
        )
        cmdline = (result.stdout or "").strip()
        if cmdline:
            return CmdlineResult(ok=True, cmdline=cmdline, source="cim")
        err = (result.stderr or "").strip()
        return CmdlineResult(ok=False, error=err or "empty cmdline", source="cim")
    except Exception as e:
        return CmdlineResult(ok=False, error=str(e), source="cim")


def get_process_cmdline(pid: int) -> CmdlineResult:
    if sys.platform == "win32":
        return _get_cmdline_windows(pid)
    return _get_cmdline_linux(pid)


def cmdline_matches(cmdline: str, must_contain: list[str]) -> bool:
    return all(k in cmdline for k in must_contain)


def safe_kill(
    pid: int,
    must_contain: list[str],
    *,
    kill: bool,
) -> tuple[bool, str]:
    if not is_process_running(pid):
        return False, "process not running"

    res = get_process_cmdline(pid)
    if not res.ok or not res.cmdline:
        return False, f"cmdline unavailable ({res.source}): {res.error or 'unknown error'}"

    if must_contain and not cmdline_matches(res.cmdline, must_contain):
        return False, "cmdline mismatch"

    if not kill:
        return True, "verified (dry-run)"

    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, text=True)
        else:
            os.kill(pid, 15)
    except Exception as e:
        return False, str(e)
    return True, "killed"

