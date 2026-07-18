---
id: "weasyprint-11-faq"
title: "十一、常见问题与故障排查"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/11-faq-troubleshooting.toml"
source: "https://weasyprint.org/ | https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#troubleshooting | 经验沉淀"
category: "learning"
tags: ["weasyprint","faq","troubleshooting","debugging","windows"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint常见问题解答：Windows DLL缺失、中文乱码、图片不显示、表格跨页断裂、安装失败、PDF文件过大、页眉页脚不显示、counter(pages)显示为0等高频问题的原因分析和解决方案"
---
# 十一、常见问题与故障排查

## 安装相关问题

### Q1: Windows 上报错 `cannot load library 'libgobject-2.0-0': error 0x7e`

**原因**：Windows 上缺少 Pango/GTK 运行时 DLL，或 DLL 目录不在 PATH 中。

**解决方案**（按优先级排序）：

1. **最简单方案**：直接使用官方独立可执行文件，无需 Python 和 GTK（参见[安装指南方案一](04-installation-cli.md#方案一官方独立可执行文件推荐)）
2. **推荐开发方案**：使用 WSL2，体验与 Linux 一致，零 DLL 问题
3. **原生 Python 方案**：
   - 确认已通过 MSYS2 安装了 `mingw-w64-x86_64-pango`
   - 确认 `C:\msys64\mingw64\bin` 已添加到系统 PATH
   - **必须重启** cmd/PowerShell/IDE 才能加载新的 PATH
   - 或设置环境变量（当前会话临时生效）：
     ```cmd
     set WEASYPRINT_DLL_DIRECTORIES=C:\msys64\mingw64\bin
     ```
4. 验证 DLL 是否可被找到：
   ```cmd
   where libgobject-2.0-0.dll
   ```

### Q2: `Requirement already satisfied` 但导入时仍报错

**原因**：pip 将包装到了另一个 Python 环境中（系统 Python vs conda/venv），当前运行的解释器找不到包。

**解决**：始终使用 `python -m pip` 绑定到当前解释器：

```cmd
:: 确认当前 Python
where python
python --version

:: 用当前 Python 的 pip 安装
python -m pip install weasyprint

:: 用同一个 Python 验证导入
python -c "from weasyprint import HTML; print('WeasyPrint 可用')"
```

### Q3: Linux/macOS 安装失败（cffi/libpango 错误）

**原因**：缺少系统 C 库。

**解决**：
```bash
# Debian/Ubuntu
sudo apt install weasyprint
# 或
sudo apt install python3-pip libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0

# macOS
brew install weasyprint
# 或
brew install pango libffi
```

### Q4: 官方 Windows exe 被杀毒软件报毒

**原因**：PyInstaller 打包的可执行文件常被误报为恶意软件，这是已知问题。

**解决**：
- 参见 GitHub Issues [#2081](https://github.com/Kozea/WeasyPrint/issues/2081)、[#2092](https://github.com/Kozea/WeasyPrint/issues/2092)
- 添加白名单信任
- 或改用 WSL2 / MSYS2 方案（Python 包方式通常不会被误报）

---

## 渲染相关问题

### Q5: 中文显示为方块/乱码

**原因**：未找到中文字体。

**解决**：
1. Linux: `sudo apt install fonts-noto-cjk`
2. Windows: 确保系统已安装中文字体（微软雅黑、宋体等）
3. 在 CSS 中显式指定中文字体：
   ```css
   body { font-family: "Noto Sans CJK SC", "Microsoft YaHei", sans-serif; }
   ```
4. 使用 `@font-face` 嵌入字体文件（推荐用于跨平台一致渲染）

### Q6: 图片不显示

**原因**：相对路径无法解析；图片 URL 不可达；图片格式不支持。

**解决**：
1. 使用绝对路径或设置正确的 `base_url`：
   ```python
   HTML(filename="report.html", base_url=".").write_pdf("out.pdf")
   ```
2. 本地文件使用 `file://` 协议或绝对路径
3. 确保 Pillow 已安装（JPEG/GIF 等格式需要）：`pip install Pillow`

### Q7: 表格跨页断裂

**解决**：
```css
tr { break-inside: avoid; }
thead { display: table-header-group; } /* 表头在每页重复 */
tfoot { display: table-footer-group; } /* 表脚在每页重复 */
```

### Q8: PDF 文件太大

**解决**：
```python
HTML(string=html).write_pdf(
    "output.pdf",
    optimize_images=True,
    jpeg_quality=80,
    dpi=150,
    full_fonts=False  # 字体子集化（默认已开启）
)
```

### Q9: 页眉页脚不显示

**原因**：边距太小放不下内容，或 `@page` 规则未正确应用。

**解决**：确保 `@page` 的 margin 足够大以容纳边距盒内容：

```css
@page {
  size: A4;
  margin: 2.5cm 2cm; /* 上下边距至少2cm才能放下页眉页脚 */
  
  @top-center {
    content: "页眉内容";
  }
  @bottom-center {
    content: "第 " counter(page) " 页 / 共 " counter(pages) " 页";
  }
}
```

### Q10: `counter(pages)` 显示为 0

**原因**：多遍重排尚未收敛，或 CSS 中有导致内容无限变化的循环（例如页眉中引用总页数导致页数变化，进而导致页眉变化）。

**解决**：检查是否有依赖 `counter(pages)` 的内容改变了页数。这是定点迭代的固有限制，尽量避免在边距盒中使用影响布局的动态内容。

### Q11: 背景色/背景图不打印

**原因**：CSS 默认不打印背景，需要显式设置。

**解决**：
```css
@media print {
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
```

### Q12: 链接在 PDF 中不可点击

**原因**：WeasyPrint 支持超链接，但需要确保使用正确的锚点标签。

**解决**：
1. 使用标准 `<a href="...">` 标签，不要用 JS 点击事件
2. 内部锚点链接：`<a href="#section-id">` 配合 `id="section-id"`
3. 外部链接必须是完整 URL 或相对于文档的路径

---

| [返回总览](00-overview.md) | [上一章：十、局限性与最佳实践](10-limitations-best-practices.md) | [下一章：十二、架构洞察与个人理解 →](12-architecture-insights.md) |
|---|---|---|
