@echo off
REM ===================================================================
REM  一键构建脚本（Windows）
REM  学生用法：双击这个文件，然后打开 docs\_build\html\index.html
REM
REM  设计说明：本脚本自动寻找可用的 Python 并验证能 import sphinx。
REM  若预置 .venv 失效（跨机器复制时常见），自动回退到系统 Python。
REM ===================================================================

setlocal enabledelayedexpansion

echo.
echo   正在把你的文档变成网页...
echo.

REM --- 逐个验证候选 Python：必须能 import sphinx ---
set PY=

REM 1. 预置虚拟环境
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sphinx" >nul 2>&1
    if !errorlevel! equ 0 (
        set PY=.venv\Scripts\python.exe
        echo   [使用预置环境 .venv]
    ) else (
        echo   [警告] 预置环境已失效（可能是复制到别的电脑导致的）
        echo          正在尝试系统 Python...
    )
)

REM 2. 系统 Python
if not defined PY (
    python -c "import sphinx" >nul 2>&1
    if !errorlevel! equ 0 (
        set PY=python
        echo   [使用系统 Python]
    )
)

REM 3. py launcher
if not defined PY (
    py -c "import sphinx" >nul 2>&1
    if !errorlevel! equ 0 (
        set PY=py
        echo   [使用 py 启动器]
    )
)

if not defined PY (
    echo.
    echo   ==================================================
    echo   ✗ 找不到可用的 Python（或没装 sphinx）
    echo   ==================================================
    echo.
    echo   请把这句话告诉老师：
    echo     warmup-docs 环境的 sphinx 不可用，需要重新准备环境
    echo.
    echo   临时替代方案（不需要 Python）：
    echo     把你 index.md 的内容粘贴到任意在线 Markdown 预览器，
    echo     也能看到渲染效果。
    echo.
    pause
    exit /b 1
)

echo.
%PY% -m sphinx -b html docs docs\_build\html

if errorlevel 1 (
    echo.
    echo   ============================================
    echo   ✗ 构建失败了。请把上面的报错拍照给老师。
    echo   ============================================
    pause
    exit /b 1
)

echo.
echo   ============================================
echo   ✓ 成功！现在打开这个文件看看效果：
echo.
echo     docs\_build\html\index.html
echo   ============================================
echo.

REM 尝试自动打开浏览器
start "" "docs\_build\html\index.html"
pause
