---
title: "XMNN SDK 使用指南 docx→Sphinx 项目转换与双向导出 规格文档"
status: "draft"
---

# XMNN SDK 使用指南 docx→Sphinx 项目转换与双向导出 规格文档

## Why

`XMNN_SDK_使用指南v1.1.0.docx`（芯劢微 XMNPU 工具链使用指南）目前以单一 docx 文件形式维护，无法进行版本化协作、增量更新与多格式发布。需要将其转换为 Sphinx 项目作为单一事实源（Single Source of Truth），同时保持原文档的排版风格，并支持从 Sphinx 反向导出 docx/pdf，形成"docx 导入 → Sphinx 维护 → docx/pdf 导出"的完整文档工具链闭环。

## 内容敏感度判定

- **级别**：私域内容（内部商业 SDK 文档，含公司名称与版权页）
- **依据**：文档标题含公司名"浙江芯劢微电子股份有限公司"，属企业内部技术资料
- **工作流**：产出物直接存放于用户指定目录 `d:\AI\.chaos\xmtools\`，不进入根 `docs/` 公共文档中心

## What Changes

- 在 `d:\AI\.chaos\xmtools\xmnn-sdk-docs\` 创建 Sphinx 文档子项目（与现有 `npu_tvm/`、`npuusertools/` 平级）
- 编写 `docx2rst.py` 转换脚本：解析源 docx（536 段落/26 表格/11 图片），按样式映射生成 RST 章节文件并提取图片资源
- 生成 6 个一级章节的 RST 源文件：更新记录、开发环境准备、XMNN 工具链 npuusertools、XMNN C/C++ 使用指南、量化原理、模型样例
- 配置 Sphinx HTML 构建并保持原文档风格（黑体标题/仿宋正文/楷体代码的字体栈映射）
- 配置 `docxbuilder` 实现 Sphinx→docx 导出，样式映射回原文档字体体系
- 配置 `rst2pdf` 实现 Sphinx→pdf 导出（纯 Python 方案，无需 LaTeX，注册 Windows 中文字体）
- 提供一键构建脚本（html/docx/pdf 三格式）

## Impact

- Affected specs: 无（新建独立子项目，不修改现有规范）
- Affected code: 仅新增 `d:\AI\.chaos\xmtools\xmnn-sdk-docs\` 目录；不修改 `npu_tvm/`、`npuusertools/` 子仓库
- 环境依赖新增：`docxbuilder==1.2.0`、`rst2pdf==0.105`（均已确认 PyPI 可用；sphinx 9.1.0 与 python-docx 1.2.0 已安装；系统无 LaTeX 与 pandoc，故 PDF 采用 rst2pdf 纯 Python 路线）

## 源文档事实基线（G1 事实门已通过）

| 事实项 | 值 |
|---|---|
| 文件 | `d:\AI\.chaos\tests\old\work\doc\XMNN_SDK_使用指南v1.1.0.docx` |
| 标题 | 芯劢微XMNPU工具链使用指南 |
| 段落数 | 536（Normal 206 / code 217 / List Paragraph 32 / H1 6 / H2 22 / H3 34 / H4 18） |
| 表格数 | 26（行数分布：2~23 行不等） |
| 图片数 | 11（全部为嵌入式 PICTURE） |
| 一级章节 | 更新记录、开发环境准备、XMNN 工具链 npuusertools、XMNN C/C++ 使用指南、量化原理、模型样例 |
| 字体风格 | 正文：华文仿宋+Times New Roman（10.5pt）；标题 H1/H2/H3：黑体（18/16/15pt，黑色）；代码：华文楷体（9pt） |

## ADDED Requirements

### Requirement: Sphinx 子项目骨架
系统 SHALL 在 `d:\AI\.chaos\xmtools\xmnn-sdk-docs\` 提供完整可构建的 Sphinx 项目，包含 `source/conf.py`、`source/index.rst`、依赖声明与构建脚本。

#### Scenario: HTML 构建成功
- **WHEN** 在子项目目录执行 HTML 构建
- **THEN** 构建成功（无 ERROR），生成 `index.html` 且包含全部 6 个一级章节入口

### Requirement: docx 内容完整转换
系统 SHALL 通过 `docx2rst.py` 脚本将源 docx 转换为 RST，保持章节层级（H1~H4）、代码块、表格、图片、列表的完整映射。

#### Scenario: 转换完整性验证
- **WHEN** 转换脚本执行完毕
- **THEN** 生成 6 个章节 RST 文件；11 张图片提取至 `_static/images/` 并在 RST 中以 figure 引用；26 个表格转为 RST 表格；217 个 code 样式段落归入 code-block

### Requirement: HTML 输出保持原文档风格
系统 SHALL 通过自定义 CSS 使 HTML 输出在字体观感上贴近原文档：标题使用黑体系字体栈、正文使用仿宋系字体栈、代码使用楷体系字体栈，并保留中文字体回退链。

#### Scenario: 风格检查
- **WHEN** 查看生成的 HTML 页面
- **THEN** CSS 中标题/正文/代码三类字体栈分别包含黑体、仿宋、楷体族字体声明，页面中文内容渲染正常

### Requirement: Sphinx→docx 导出
系统 SHALL 通过 `docxbuilder` 提供 `docx` 构建目标，导出的 docx 中标题使用黑体、正文使用仿宋、代码使用楷体，章节层级映射为 Word 标题样式。

#### Scenario: docx 导出成功
- **WHEN** 执行 docx 构建目标
- **THEN** 生成 `.docx` 文件，可用 python-docx 打开，包含 6 个一级标题且样式字体配置生效

### Requirement: Sphinx→pdf 导出
系统 SHALL 通过 `rst2pdf` 提供 `pdf` 构建目标，注册 Windows 系统中文字体，导出的 PDF 中文正常显示。

#### Scenario: pdf 导出成功
- **WHEN** 执行 pdf 构建目标
- **THEN** 生成 `.pdf` 文件，文件大小大于 0 且构建过程无致命错误

### Requirement: 一键构建
系统 SHALL 提供统一构建入口（PowerShell 脚本），支持 `html`、`docx`、`pdf`、`all` 四个目标。

#### Scenario: 全格式构建
- **WHEN** 执行 `.\build.ps1 all`
- **THEN** 依次完成 html、docx、pdf 三种格式构建并输出产物路径

## Constraints

- 源 docx 为只读输入，转换过程不得修改源文件
- 子项目不得修改 `npu_tvm/`、`npuusertools/` 两个既有子仓库内容
- PDF 路线采用 rst2pdf（系统无 LaTeX）；字体取自 `C:\Windows\Fonts`，脚本需对字体文件缺失给出明确报错
- RST 为源格式（docxbuilder 与 rst2pdf 对 RST 支持最完整），不引入 MyST/Markdown 中间层
- 构建产物目录（`build/`）不纳入版本管理

## Assumptions

- 运行环境为 Windows + Python 3.14.7，已安装 sphinx 9.1.0、python-docx 1.2.0
- `C:\Windows\Fonts` 中存在黑体（simhei.ttf）、仿宋（fsfangsong/仿宋）、楷体（simkai.ttf）等字体文件
- 转换脚本对复杂表格（合并单元格）允许降级为 list-table 表示，不要求像素级还原
