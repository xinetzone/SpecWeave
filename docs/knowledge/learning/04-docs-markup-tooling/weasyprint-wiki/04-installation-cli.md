---
id: "weasyprint-04-installation"
title: "安装与配置指南"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/04-installation-cli.toml"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
category: "learning"
tags: ["weasyprint","installation","cli","setup"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint安装指南：Linux/macOS/Windows系统依赖、pip安装、验证方法、命令行完整用法"
---

# 安装与配置指南

### 5.1 系统依赖

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install python3-pip python3-cffi libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 libjpeg-dev
```

**macOS**:
```bash
brew install python pango cairo libffi
```

**Windows**: 推荐 WSL2；原生 Windows 需安装 GTK3 Runtime。

### 5.2 Python 安装

```bash
pip install weasyprint
```

验证：
```python
from weasyprint import HTML
HTML(string="<h1>Hello WeasyPrint!</h1>").write_pdf("test.pdf")
```

### 5.3 命令行使用

```bash
# 基本用法
weasyprint input.html output.pdf

# 添加自定义 CSS
weasyprint input.html output.pdf -s style.css

# 指定媒体类型
weasyprint input.html output.pdf -m screen

# 设置 PDF 变体（PDF/A-1b, PDF/UA-1 等）
weasyprint input.html output.pdf --pdf-variant pdf/a-1b

# 编码指定
weasyprint input.html output.pdf -e utf-8

# 获取帮助
weasyprint --help
```

---

| [返回总览](00-overview.md) | [上一章：核心依赖与技术栈](03-tech-stack-dependencies.md) | 下一章：无 |
|---|---|---|
