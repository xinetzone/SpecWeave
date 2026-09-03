---
id: "sphinx-rst2pdf-image-handling"
title: "Sphinx RST→PDF 图片处理标准流程（DPI 元数据覆盖 + figure 指令控宽）"
type: process-pattern
date: 2026-09-03
maturity: L1
maturity_note: "单案例验证（XMNN SDK 文档三格式闭环），待二次验证升级 L2"
source: "../reports/task-reports/retrospective-xmnn-sdk-docs-closed-loop-20260903/retrospective-report.md"
related_patterns:
  - "sphinx-build-acceleration-metering.md"
  - "../process-patterns/ops-sop-standard-template.md"
tags: ["sphinx", "rst2pdf", "pdf", "image", "dpi", "figure", "docx2rst", "reportlab", "layout-error"]
validation_count: 1
reuse_count: 0
---

# Sphinx RST→PDF 图片处理标准流程（DPI 元数据覆盖 + figure 指令控宽）

## 触发场景

- 当 Sphinx 项目使用 `rst2pdf` 构建 PDF，且源文档含内嵌图片（docx/Markdown 转换而来）时
- 当 PDF 构建报 `LayoutError: More than 10 pages generated without content` 或图片超出页面边界时
- 当 docx 内嵌图片 DPI 元数据为 72（屏幕分辨率），而 rst2pdf 按此计算自然尺寸导致竖长图片无法分页时
- 当 `.. figure::` 指令硬编码 `:width: 100%`，在竖长图片场景下宽度撑满页面、高度超出 A4 页高引发布局错误时

**识别信号**：
- PDF 构建失败，错误信息包含 `LayoutError` 或 `Too large for any frame`
- HTML 构建正常，仅 PDF 异常（说明问题在 rst2pdf 特有渲染路径）
- 图片在 docx 中显示正常，但在 PDF 中溢出或截断

## 不适用场景（反目标场景）

- **纯 HTML 输出项目**：本模式聚焦 rst2pdf 路径；若只用 `sphinx-build -b html`，无需 DPI 覆盖
- **图片已携带正确 DPI 元数据（≥300）**：若源图已是印刷级 DPI，`resize_for_pdf()` 仍会运行但无实际修改
- **使用其他 PDF 后端（如 weasyprint/sphinxcontrib-weasyprint）**：weasyprint 走 CSS 渲染路径，DPI 元数据影响方式不同

## 核心步骤

### 步骤 1：图档 DPI 元数据标准化

在转换脚本（docx2rst.py 等）中，提取图片后调用 `resize_for_pdf()` 函数：

```python
from PIL import Image

PDF_DPI = 600  # 与 source/conf.py 中的 pdf_default_dpi 保持一致
PDF_MAX_IMG_WIDTH = 2000
PDF_MAX_IMG_HEIGHT = 3000

def resize_for_pdf(path: Path) -> None:
    """限制图片像素尺寸，并固定 DPI 元数据，避免 rst2pdf 按 72dpi 推算出过大的自然尺寸。"""
    try:
        with Image.open(path) as img:
            changed = False
            if img.width > PDF_MAX_IMG_WIDTH or img.height > PDF_MAX_IMG_HEIGHT:
                img.thumbnail((PDF_MAX_IMG_WIDTH, PDF_MAX_IMG_HEIGHT), Image.Resampling.LANCZOS)
                changed = True
            # 强制写入 PDF_DPI，覆盖源图可能携带的 72dpi 等元数据
            if 'dpi' not in img.info or img.info.get('dpi') != (PDF_DPI, PDF_DPI):
                changed = True
            if changed:
                img.save(path, dpi=(PDF_DPI, PDF_DPI))
    except Exception:
        pass  # 静默失败，不影响主流程
```

**要点**：
- DPI 值必须与 `conf.py` 中 `pdf_default_dpi` 一致（本项目用 600）
- 用 `try/except` 包裹，单张图片异常不阻断整个构建
- `img.info.get('dpi')` 检查避免重复写入相同 DPI

### 步骤 2：figure 指令宽度控制

在生成 RST 时，**普通段落下的 figure 指令不加 `:width: 100%`**：

```python
# ❌ 反模式：硬编码 :width: 100% 导致竖长图片超出页高
for ref in refs:
    out_target().append(f'.. figure:: {ref}\n   :align: center\n   :width: 100%\n')

# ✅ 正模式：移除宽度硬编码，由图片 DPI 元数据控制自然尺寸
for ref in refs:
    out_target().append(f'.. figure:: {ref}\n   :align: center\n')
```

`xmnn-zh.yaml` 中的样式配置保留 `figure` 的 `width: "100%"` 作为兜底（仅对可缩放图片生效），但不在 RST 指令层硬编码。

### 步骤 3：yaml 样式表兜底

在 `source/xmnn-zh.yaml` 中保留 figure/image 样式，确保 rst2pdf 有合理默认：

```yaml
styles:
  - [image, {width: "100%"}]
  - [figure, {width: "100%"}]
```

注意：此处 `width: "100%"` 作用于 rst2pdf 的 flowable 布局，而非 RST figure 指令的 `:width:`，两者作用层不同。

### 步骤 4：构建验证

```bash
# 全格式构建验证
python build.ps1
# 确认 PDF 构建 EXIT=0，无 LayoutError
```

## 反模式

| 反模式 | 症状 | 正确做法 |
|--------|------|----------|
| 在 figure 指令中硬编码 `:width: 100%` | 竖长图片超出 A4 页高，LayoutError | 移除 `:width: 100%`，让 DPI 元数据驱动尺寸 |
| 忽略源图 DPI 元数据 | rst2pdf 按 72dpi 计算，图片自然尺寸放大 3-4 倍 | 转换时强制写入 600dpi |
| 在 conf.py 设 pdf_default_dpi 但转换脚本不匹配 | DPI 声明与实际不符，尺寸仍错误 | 两处 DPI 值保持一致 |
| resize_for_pdf() 不包裹异常 | 单张损坏图片导致整个构建失败 | try/except 静默跳过 |
| 用 `:width: XXpx` 硬编码具体数值 | 不同分辨率源图表现不一致 | 依赖 DPI 元数据 + yaml 样式兜底 |

## 迁移验证

- [ ] 新建 Sphinx 项目使用 rst2pdf 时，复制 `resize_for_pdf()` 函数
- [ ] 检查 `conf.py` 中 `pdf_default_dpi` 与代码中 `PDF_DPI` 常量一致
- [ ] 运行全格式构建（HTML + PDF + docx），确认无 LayoutError
- [ ] 随机抽查 3-5 张 PDF 图片，确认无溢出、无模糊

## 根因摘要

docx 内嵌图片携带 72 DPI 元数据（屏幕分辨率），rst2pdf 的 `size_for_node()` 按 DPI 反算自然尺寸，导致竖长图片在 A4 页面上宽度撑满、高度远超 25.7cm 正文区域，触发 reportlab `LayoutError`。修复路径：①强制写入 600 DPI 元数据缩小自然尺寸估算；②移除 `:width: 100%` 避免宽度硬撑。
