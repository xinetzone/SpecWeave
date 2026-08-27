@echo off
REM ============================================================================
REM jpman.cmd — Windows wrapper for jupyter-podman-rootless CLI (jpman)
REM
REM Usage from PowerShell or cmd.exe (from anywhere):
REM   path\to\bin\jpman <command>
REM
REM Set JUPYTER_WSL_DISTRO to use a specific WSL distro (default: wsl default distro).
REM This wrapper auto-detects its location via wslpath — no hardcoded paths.
REM ============================================================================
setlocal

set "WIN_DIR=%~dp0"

if defined JUPYTER_WSL_DISTRO (
    wsl -d "%JUPYTER_WSL_DISTRO%" -- bash -c 'BIN_DIR=$(wslpath -u "$1"); shift; exec bash "$BIN_DIR/jpman" "$@"' _ "%WIN_DIR%" %*
) else (
    wsl -- bash -c 'BIN_DIR=$(wslpath -u "$1"); shift; exec bash "$BIN_DIR/jpman" "$@"' _ "%WIN_DIR%" %*
)

endlocal
