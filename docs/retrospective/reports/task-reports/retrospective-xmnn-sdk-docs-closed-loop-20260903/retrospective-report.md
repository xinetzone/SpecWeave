---
type: Report
id: "retrospective-xmnn-sdk-docs-closed-loop-20260903"
title: "XMNN SDK 文档三格式闭环复盘报告"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/reports/task-reports/retrospective-xmnn-sdk-docs-closed-loop-20260903.toml"
---

# XMNN SDK 文档三格式闭环复盘报告

**复盘日期**: 2026-09-03
**复盘对象**: `d:\AI\.chaos\xmtools\xmnn-sdk-docs`（Sphinx 文档项目）
**方法论**: 七概念方法论编排（R→I→E→C）
**复盘类型**: 里程碑复盘
**Session**: `sc-20260903-xmnn-sdk-docs`

---

## 一、项目概述

### 1.1 任务背景

将 `d:\AI\.chaos\tests\old\work\doc\XMNN_SDK_使用指南v1.1.0.docx` 转换为 Sphinx 项目，实现以下目标：
1. docx → RST 自动转换（保留原文档风格）
2. 支持 Sphinx 三格式构建：HTML / docx / PDF
3. 解决 PDF 导出中的图片缩放问题

### 1.2 项目结构

```
xmnn-sdk-docs/
├── build.ps1                          # 全格式构建脚本
├── requirements.txt                   # 项目依赖
├── scripts/
│   ├── docx2rst.py                    # docx→RST 核心转换脚本
│   ├── verify_docx.py                 # docx 产物验证
│   └── make_style_template.py         # 样式模板生成
├── source/
│   ├── conf.py                        # Sphinx 配置
│   ├── index.rst                      # 文档入口
│   ├── xmnn-zh.yaml                   # rst2pdf 样式表（YAML）
│   ├── _static/
│   │   ├── custom.css                 # HTML 自定义样式
│   │   └── images/                    # 原始图片（11张）
│   ├── changelog.rst
│   ├── environment.rst
│   ├── npuusertools.rst
│   ├── cpp-sdk.rst
│   ├── quantization.rst
│   └── examples.rst
└── build/
    ├── html/                          # HTML 产物（mystx 主题）
    ├── pdf/                           # PDF 产物
    └── docx/                          # docx 产物
```

### 1.3 最终构建结果

| 格式 | 产物 | 状态 | 备注 |
|------|------|------|------|
| HTML | `build/html/index.html` | ✅ 成功 | mystx 主题（基于 Sphinx Book Theme） |
| PDF | `build/pdf/XMNN_SDK_使用指南v1.1.0.pdf` (1.7MB) | ✅ 成功 | 无警告，无 LayoutError |
| docx | `build/docx/XMNN_SDK_使用指南v1.1.0.docx` | ✅ 成功 | docxbuilder 产物 |

---

## 二、事实清单（R 阶段产出，F-xxx，无因果词）

> 质量门 G1：事实阶段不包含因果推断词，纯客观描述。

### 2.1 源文档

- **F-001**: 源文件 `XMNN_SDK_使用指南v1.1.0.docx`，位于 `d:\AI\.chaos\tests\old\work\doc\`
- **F-002**: 源文档含 6 个一级章节（更新记录、开发环境准备、XMNN 工具链 npuusertools、XMNN C/C++ 使用指南、量化原理、模型样例）
- **F-003**: 源文档含 11 张内嵌图片（img-01 至 img-11，格式含 PNG/JPG）
- **F-004**: 源文档含约 209 个代码块（Python/C++ 混合）
- **F-005**: 源文档使用中文，含表格、列表、标题层级（Heading 1-4）

### 2.2 技术栈

- **F-006**: Sphinx 9.1.0
- **F-007**: mystx 主题（pip 包，基于 Sphinx Book Theme）
- **F-008**: myst-nb >= 1.4.0、myst-parser >= 5.1.0
- **F-009**: rst2pdf 0.105 + reportlab 4.2.5（PDF 后端）
- **F-010**: docxbuilder 1.2.0（docx 后端）
- **F-011**: python-docx（docx 解析）
- **F-012**: Pillow（图片 DPI 元数据操作）

### 2.3 关键配置文件

- **F-013**: `source/conf.py` 中设置 `html_theme = 'mystx'`、`pdf_default_dpi = 600`
- **F-014**: `source/xmnn-zh.yaml` 为 rst2pdf 样式表，含中文字体配置（simhei/simfang/simkai）
- **F-015**: `scripts/docx2rst.py` 核心转换逻辑，含 `resize_for_pdf()` 函数（PDF_DPI=600，最大尺寸 2000×3000px）
- **F-016**: `build.ps1` 幂等构建脚本，按顺序执行 RST 生成→HTML→PDF→docx

### 2.4 构建日志

- **F-017**: 首次 PDF 构建失败，日志 `build_all.log` 显示 `LayoutError: More than 10 pages generated without content`
- **F-018**: 修复后 PDF 构建 EXIT=0，无警告，无错误
- **F-019**: HTML 构建包含 mystx 主题 CSS/JS 资源（含多语言本地化文件）
- **F-020**: 清理了临时脚本文件（check_img_attrs.py、calc_img_pct.py、test_figure.rst）

### 2.5 修改文件清单

- **F-021**: `scripts/docx2rst.py` — 新增 `resize_for_pdf()` 函数 + 移除 figure 指令 `:width: 100%`
- **F-022**: `source/conf.py` — 添加 mystx 扩展、设置主题、pdf_default_dpi=600
- **F-023**: `requirements.txt` — 添加 mystx>=0.3.4、myst-nb>=1.4.0、myst-parser>=5.1.0
- **F-024**: `source/xmnn-zh.yaml` — 新建，替代旧 .style RSON 格式

---

## 三、洞察（I 阶段产出，四元组）

> 质量门 G2：每条洞察包含 陈述/证据/反常识/行动 四元组。

### I-01 PDF LayoutError 根本原因：docx 图片 DPI 元数据与 rst2pdf 计算逻辑不匹配

- **陈述**: docx 内嵌图片携带 72 DPI 元数据（屏幕分辨率标准），rst2pdf 的 `size_for_node()` 按 DPI 反算自然尺寸，导致竖长图片在 A4 页面上宽度过大或高度超出正文区域。
- **证据**: F-017（首次构建 LayoutError）；F-015（resize_for_pdf 强制写入 600 DPI）；修复后 F-018（EXIT=0）。
- **反常识**: 图片在 docx 中显示正常（Word 按 72 DPI 渲染），但在 PDF 中异常——问题不在图片内容，而在元数据与渲染引擎的 DPI 假设不匹配。
- **行动**: 所有 docx→RST 转换脚本须在图片提取后强制写入与 `pdf_default_dpi` 一致的 DPI 元数据；同时避免在 figure 指令中硬编码 `:width: 100%`。

### I-02 figure 指令 :width: 100% 在竖长图片场景下触发布局溢出

- **陈述**: 普通段落下的 `.. figure::` 指令若硬编码 `:width: 100%`，rst2pdf 会将图片宽度强制撑满页面正文宽度，竖长图片的高度随之超出 A4 页高（25.7cm），reportlab 无法分页导致 LayoutError。
- **证据**: F-017（首次构建失败）；F-021（移除 `:width: 100%` 后修复）。
- **反常识**: `:width: 100%` 在横向图片场景下表现正常（宽度撑满、高度自适应），仅在竖长图片（宽高比 > 页宽高比）下触发溢出——同一指令在不同图片比例下行为不一致。
- **行动**: 转换脚本生成 figure 指令时不加 `:width: 100%`；PDF 样式兜底通过 `xmnn-zh.yaml` 的 `figure: {width: "100%"}` 实现（作用于 flowable 层，非 RST 指令层）。

### I-03 mystx 主题切换依赖隐式依赖链

- **陈述**: mystx 作为 pip 包安装时，其核心依赖（myst-nb、myst-parser）不会自动随 `pip install mystx` 安装到环境，需显式声明。
- **证据**: 首次 `pip install mystx` 后构建报 `ModuleNotFoundError: No module named 'myst_nb'`；F-023（requirements.txt 同步添加三个依赖）。
- **反常识**: mystx 包名与 myst-parser/myst-nb 无命名关联，开发者容易误认为安装 mystx 即完整可用。
- **行动**: requirements.txt 须完整声明 mystx 及其直接依赖；迁移或部署时先安装 requirements.txt 而非单独安装主题包。

---

## 四、潜在问题清单（P0/P1/P2 分级）

### P0（阻断性，需修复）

- 无。本次迭代所有阻断性问题已修复。

### P1（重要，建议修复）

- **P1-1**: `docx2rst.py` 中 figure 指令生成逻辑仅处理了普通段落场景，未覆盖嵌套在列表/表格中的图片——此类场景可能仍存在宽度/布局问题。
- **P1-2**: `xmnn-zh.yaml` 中 `figure: {width: "100%"}` 与 RST 层不加 `:width: 100%` 的配合依赖 rst2pdf 内部优先级规则，若 rst2pdf 版本升级改变此行为，需重新验证。

### P2（优化项，择机处理）

- **P2-1**: 转换脚本未处理 GIF 动图（仅静态帧），若源文档含动图，PDF 输出将丢失动画。
- **P2-2**: `build.ps1` 未做增量构建优化，全量重建耗时约 2-3 分钟；对仅修改单一 RST 文件的场景可进一步优化。
- **P2-3**: 未配置 `.gitignore` 排除 `build/` 目录（已添加但需验证 CI 环境兼容性）。

---

## 五、萃取模式（E 阶段产出）

> 质量门 G3：模式包含触发场景 + 核心步骤 + 反模式 + 迁移验证。

已从本次迭代萃取模式：「**Sphinx RST→PDF 图片处理标准流程**」（DPI 元数据覆盖 + figure 指令控宽）。

- 模式文件：[`docs/retrospective/patterns/process-patterns/sphinx-rst2pdf-image-handling.md`](../../patterns/process-patterns/sphinx-rst2pdf-image-handling.md)
- 成熟度：L1（单案例验证）
- 标签：`sphinx` `rst2pdf` `pdf` `image` `dpi` `figure` `docx2rst`

---

## 六、质量门通过记录

| 质量门 | 判定 | 说明 |
|--------|------|------|
| G1（事实无因果词） | ✅ 通过 | F-001~F-024 均为客观描述，无"因为"/"导致"/"所以" |
| G2（洞察四元组） | ✅ 通过 | I-01~I-03 均含陈述/证据/反常识/行动 |
| G3（模式可迁移） | ✅ 通过 | 模式文件含触发场景、核心步骤、反模式、迁移验证 |
| G4（行动项原子化） | ✅ 通过 | P1/P2 项均可独立验证，无合并依赖 |

---

## 七、交付物清单

| 交付物 | 路径 | 状态 |
|--------|------|------|
| Sphinx 项目源码 | `d:\AI\.chaos\xmtools\xmnn-sdk-docs\` | ✅ 完成 |
| HTML 产物（mystx 主题） | `build\html\index.html` | ✅ 完成 |
| PDF 产物 | `build\pdf\XMNN_SDK_使用指南v1.1.0.pdf` | ✅ 完成 |
| docx 产物 | `build\docx\XMNN_SDK_使用指南v1.1.0.docx` | ✅ 完成 |
| 模式文件 | `docs/retrospective/patterns/process-patterns/sphinx-rst2pdf-image-handling.md` | ✅ 完成 |
| 复盘报告 | 本文档 | ✅ 完成 |

---

## 八、结论

XMNN SDK 文档三格式闭环项目圆满完成。核心成果：

1. **技术闭环**：docx → RST → HTML(docx)/PDF 三格式构建全部成功，mystx 主题切换无兼容问题。
2. **问题根治**：PDF LayoutError 根本原因已定位（DPI 元数据不匹配 + figure 宽度硬编码），修复方案已固化到转换脚本。
3. **知识沉淀**：萃取「Sphinx RST→PDF 图片处理标准流程」模式入库，供后续同类项目参考。

后续同类项目（docx→Sphinx PDF 导出）可直接复用本项目的 `resize_for_pdf()` 函数与 figure 指令生成策略。
