@echo off
REM build_caffe_ffi.bat - Thin wrapper that calls the PowerShell build script
REM All hardcoded paths have been removed; auto-discovery is handled by build_caffe_ffi.ps1

setlocal
set "SCRIPT_DIR=%~dp0"

pwsh -NoProfile -File "%SCRIPT_DIR%build_caffe_ffi.ps1" %*
exit /b %ERRORLEVEL%
