---
id: "weasyprint-04-installation"
title: "安装与配置指南"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/04-installation-cli.toml"
source: "https://weasyprint.org/ | https://doc.courtbouillon.org/weasyprint/stable/first_steps.html | https://github.com/Kozea/WeasyPrint"
category: "learning"
tags: ["weasyprint","installation","cli","setup","windows","gtk"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint安装指南：Linux/macOS/Windows多平台方案对比、pip安装、验证方法、命令行完整用法、故障排查"
---
# 安装与配置指南

## 核心要点

Windows 原生安装 WeasyPrint **确实比 Linux/macOS 复杂**，因为它依赖 Pango/Cairo 等 GNOME 图形库（这些库在 Linux/macOS 上通常预装或一键安装，但在 Windows 上需要额外配置运行时）。

**好消息**：官方现在提供多种简化方案，无需手动折腾 GTK 运行时也能使用。

---

## 安装方案对比（Windows）

| 方案 | 难度 | 是否需要Python | 适用场景 |
|---|---|---|---|
| ① 官方独立可执行文件 | ⭐ 极简 | ❌ 不需要 | 命令行批量转换、不想装Python的用户 |
| ② WSL2 (Linux子系统) | ⭐⭐ 简单 | 是（WSL内） | 开发环境、需要Python API、熟悉Linux |
| ③ MSYS2 + Pango | ⭐⭐⭐ 中等 | 是 | 必须原生Windows Python、不想用WSL |
| ④ GTK3 Runtime 安装器 | ⭐⭐⭐⭐ 较复杂 | 是 | 旧版兼容方案、不推荐新项目 |
| ⑤ Docker | ⭐⭐ 简单 | ❌ 不需要 | CI/CD、服务端部署、隔离环境 |

---

## 方案一：官方独立可执行文件（推荐⭐）

这是**最简单**的方式，不需要安装 Python，不需要 GTK 运行时，下载即用。

### 步骤

1. 前往 GitHub Releases 页面下载最新版：
   https://github.com/Kozea/WeasyPrint/releases

2. 下载 Windows 可执行文件（`weasyprint-windows-x86_64.exe` 或类似命名）

3. 重命名为 `weasyprint.exe` 并放到 PATH 目录下（如 `C:\Windows\` 或自定义目录加入 PATH）

### 使用

```powershell
weasyprint input.html output.pdf
```

> ⚠️ **注意**：部分杀毒软件可能误报为恶意软件（已知问题，参见 [#2081](https://github.com/Kozea/WeasyPrint/issues/2081)、[#2092](https://github.com/Kozea/WeasyPrint/issues/2092)），请添加信任或上报误报。

---

## 方案二：WSL2（开发推荐⭐⭐）

在 Windows Subsystem for Linux 中安装，体验与原生 Linux 一致，零依赖问题。

### 步骤

1. 安装 WSL2（如果尚未安装）：
   ```powershell
   wsl --install
   ```

2. 进入 WSL（Ubuntu）后，按 Linux 方式安装：
   ```bash
   # 直接用包管理器（最简单）
   sudo apt update && sudo apt install -y weasyprint
   
   # 或者在虚拟环境中安装最新版
   sudo apt install -y python3-pip python3-venv libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0
   python3 -m venv venv
   source venv/bin/activate
   pip install weasyprint
   ```

3. Windows 文件系统在 WSL 中挂载于 `/mnt/c/`、`/mnt/d/` 等路径，可直接转换：
   ```bash
   weasyprint /mnt/d/input.html /mnt/d/output.pdf
   ```

---

## 方案三：原生 Python + MSYS2（官方推荐Python方式）

如果必须使用原生 Windows Python（而非 WSL），官方推荐通过 MSYS2 安装 Pango 依赖。

### 前置要求
- Windows 10/11 64位
- Python 3.10+（推荐从 Microsoft Store 或官网安装）

### 步骤

1. **安装 MSYS2**
   - 下载：https://www.msys2.org/#installation
   - 保持默认选项安装（默认路径 `C:\msys64`）

2. **安装 Pango 及依赖**
   - 打开「MSYS2 MinGW 64-bit」终端（从开始菜单）
   - 执行：
     ```bash
     pacman -Syu
     # 关闭终端后重新打开，再执行：
     pacman -S mingw-w64-x86_64-pango
     ```
   - 关闭 MSYS2 终端

3. **配置环境变量**
   - 将 `C:\msys64\mingw64\bin` 添加到系统 PATH：
     - 按 `Win + R` → 输入 `sysdm.cpl` → 「高级」→「环境变量」
     - 在「系统变量」中找到 `Path` → 编辑 → 新建 → 填入 `C:\msys64\mingw64\bin`
     - 确定保存
   
   或者临时设置（仅当前cmd会话生效）：
   ```cmd
   set WEASYPRINT_DLL_DIRECTORIES=C:\msys64\mingw64\bin
   ```

4. **安装 WeasyPrint**
   - 打开**新的** Windows 命令提示符（cmd）或 PowerShell（必须重启才能加载新 PATH）
   - 创建虚拟环境并安装：
   ```cmd
   python -m venv venv
   venv\Scripts\activate.bat
   python -m pip install weasyprint
   python -m weasyprint --info
   ```

### 验证安装

```python
from weasyprint import HTML
HTML(string="<h1>Hello WeasyPrint!</h1>").write_pdf("test.pdf")
print("PDF生成成功！")
```

---

## 方案四：旧版 GTK3 Runtime 安装器（备选）

tschoonj 维护的 GTK3 运行时安装包是早期常用方案，适合不想装 MSYS2 的用户。

### 步骤

1. 下载安装包：
   https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
   （选择最新的 `gtk3-runtime-*-ts-win64.exe`）

2. 运行安装程序，建议**勾选「Add to PATH」选项**，默认安装到 `C:\gtk`

3. 重启终端，验证 GTK 是否安装成功：
   ```cmd
   gtk3-demo
   ```
   如果弹出 GTK 演示窗口，说明安装成功。

4. 将 GTK bin 目录加入 PATH（如果安装时未勾选）：
   ```
   C:\gtk\bin
   ```

5. 然后按方案三的步骤4安装 WeasyPrint Python 包。

> ⚠️ 注意：此安装器更新可能不及时，优先使用 MSYS2 方案获取最新版本的 Pango。

---

## Linux 安装

### 直接用发行版包（最简单）

```bash
# Debian ≥ 11 / Ubuntu ≥ 20.04
sudo apt install weasyprint

# Fedora ≥ 39
sudo dnf install weasyprint

# Arch Linux
sudo pacman -S python-weasyprint

# Alpine ≥ 3.17
sudo apk add weasyprint
```

### 虚拟环境安装最新版

```bash
# Debian/Ubuntu
sudo apt install python3-pip python3-venv libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0

python3 -m venv venv
source venv/bin/activate
pip install weasyprint
weasyprint --info
```

---

## macOS 安装

### 使用 Homebrew（最简单）

```bash
brew install weasyprint
```

### 或 pip + Homebrew 依赖

```bash
brew install python pango libffi
python3 -m venv venv
source venv/bin/activate
pip install weasyprint
```

如果遇到库找不到的问题：
```bash
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH
```

---

## 其他方案

### Conda（Linux/macOS）

```bash
conda install -c conda-forge weasyprint
```

### Docker

社区维护的 Docker 镜像：https://github.com/luca-vercelli/WeasyPrint-docker-images/

```bash
docker run --rm -v $(pwd):/work weasyprint input.html output.pdf
```

---

## 命令行完整用法

```bash
# 基本用法：本地HTML → PDF
weasyprint input.html output.pdf

# 直接转换网页URL
weasyprint https://weasyprint.org website.pdf

# 添加自定义CSS
weasyprint input.html output.pdf -s style.css

# 指定媒体类型（screen/print）
weasyprint input.html output.pdf -m screen

# 设置PDF变体（PDF/A-1b, PDF/UA-1等）
weasyprint input.html output.pdf --pdf-variant pdf/a-1b

# 指定编码
weasyprint input.html output.pdf -e utf-8

# 查看版本和系统信息
weasyprint --info

# 获取帮助
weasyprint --help
```

---

## 常见问题排查

### ❌ `cannot load library 'libgobject-2.0-0': error 0x7e`

**原因**：找不到 GTK/Pango 的 DLL 文件。

**解决**：
1. 确认已安装 MSYS2 并执行了 `pacman -S mingw-w64-x86_64-pango`
2. 确认 `C:\msys64\mingw64\bin` 在系统 PATH 中
3. **必须重启** cmd/PowerShell/IDE 才能让新 PATH 生效
4. 或设置环境变量指定 DLL 目录：
   ```cmd
   set WEASYPRINT_DLL_DIRECTORIES=C:\msys64\mingw64\bin
   ```

### ❌ 安装后还是报错，"Requirement already satisfied" 但导入失败

**原因**：可能安装到了错误的 Python 环境（系统Python vs conda/venv）。

**解决**：始终使用 `python -m pip` 绑定到当前解释器：
```cmd
# 先确认当前用的是哪个Python
where python
python --version

# 用这个Python对应的pip安装
python -m pip install weasyprint

# 验证：用同一个Python导入
python -c "from weasyprint import HTML; print('OK')"
```

### ❌ PDF 中文字显示为方块/空白

**原因**：缺少中文字体。

**解决**：安装中文字体（如思源黑体、微软雅黑）到系统字体目录，或在 CSS 中通过 `@font-face` 引入字体文件。

### ❌ 杀毒软件报毒

**原因**：PyInstaller 打包的可执行文件常被误报。

**解决**：这是已知问题（参见 GitHub Issues），可添加白名单或改用 WSL/MSYS2 方案。

---

## 代码中的容错处理建议

如果你的程序需要在 Windows 上运行，建议对 WeasyPrint 做软依赖处理，缺失时降级：

```python
WEASYPRINT_AVAILABLE = False
try:
    from weasyprint import HTML as WeasyHTML
    # 尝试实际加载库（捕获OSError，不仅仅是ImportError）
    WeasyHTML(string="<p>test</p>")
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"WeasyPrint不可用，将使用文本/HTML格式: {e}")

def generate_report(input_html, output_path):
    if WEASYPRINT_AVAILABLE:
        WeasyHTML(filename=input_html).write_pdf(output_path)
        return output_path
    else:
        # 降级：保存为HTML
        html_path = output_path.replace('.pdf', '.html')
        import shutil
        shutil.copy(input_html, html_path)
        print(f"PDF功能不可用，已保存为HTML: {html_path}")
        return html_path
```

---

| [返回总览](00-overview.md) | [上一章：核心依赖与技术栈](03-tech-stack-dependencies.md) | [下一章：Python API 指南](05-python-api-guide.md) |
|---|---|---|
