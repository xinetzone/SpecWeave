# jupyterlab-translate 架构洞察与知识地图（I阶段）

> 基于 facts.md 中143条事实提炼

## 核心洞察

### 洞察1：三层洋葱架构 — CLI→API→Core

- **陈述**：jupyterlab-translate 采用严格的三层分离架构：cli.py 仅做Click命令定义和参数转发，api.py 做编排逻辑（参数校验、路径计算、流程串联），utils.py/converters.py/finder.py 承担核心功能实现。
- **证据**：F-033~F-042（CLI子命令定义均调用api.py中的函数）；F-045~F-052（api.py中函数调用utils.py和converters.py中的低层函数）；F-054~F-086（utils.py包含所有实际操作逻辑）
- **反常识**：初学者容易以为cli.py是核心入口而直接阅读，但cli.py几乎没有业务逻辑，只是一层薄壳。真正的入口点是utils.py中的 `extract_translations`/`update_translations`/`compile_translations` 三个全局方法。
- **行动**：文档应从架构总览入手，先展示三层结构，再分别深入核心层；CLI命令作为使用入口而非理解入口。

### 洞察2：双模式分发 — 独立包 vs 集中语言包

- **陈述**：工具支持两种翻译分发模式：(1)扩展包自带翻译文件（extract/update/compile命令），(2)集中式语言包仓库（extract_pack/update_pack/compile_pack命令）。两种模式共享核心提取/编译逻辑，区别仅在输出目录结构和文件移动方式。
- **证据**：F-034~F-040（CLI两组命令）；F-045~F-047（独立包API直接在包目录输出）；F-048~F-052（语言包API区分jupyterlab核心和extensions目录，编译后移动.mo/.json到language-packs目录）；F-052~F-053（语言包包名命名规则）
- **反常识**：`update` 和 `update_pack` 的输出目录结构不同（独立包在package/project/locale/，语言包在jupyterlab_extensions/project/），但核心调用的都是 `update_translations()`，区别只在调用前计算output_dir的逻辑。
- **行动**：概念文档应先讲解核心翻译工作流（提取→更新→编译），再分别说明两种分发模式的目录布局差异。

### 洞察3：三源字符串提取 — Python + TypeScript + JSON Schema

- **陈述**：字符串提取来自三个独立来源，使用不同工具和方法：Python文件通过pybabel extract（基于pybabel_config.cfg配置），TypeScript/TSX文件通过gettext-extract（Node.js工具，ncc打包为monolithic JS），JSON Schema文件通过自定义递归遍历+正则选择器匹配。三路结果合并后去重。
- **证据**：F-071~F-072（pybabel extract Python文件）；F-061~F-063（gettext-extract处理TS/TSX）；F-065~F-070（自定义schema字符串提取）；F-076~F-078（create_catalog中三路合并）；F-074~F-075（remove_duplicates按msgctxt+msgid+msgid_plural三元组去重）
- **反常识**：TS/TSX字符串提取依赖Node.js环境和打包在Python包内的index.js（通过ncc编译），不是纯Python方案。gettext-extract子命令（F-010）就是直接转发给这个JS文件。
- **行动**：需要专门的概念文档讲解三种提取机制，特别是JS部分如何工作、schema选择器如何配置自定义翻译路径。

### 洞察4：双格式编译输出 — MO（后端）+ JSON/Jed（前端）

- **陈述**：翻译编译同时产出两种格式：.mo是gettext标准二进制格式供Python后端使用，.json是Jed格式供JupyterLab前端消费。编译后两种格式文件并存于LC_MESSAGES目录。
- **证据**：F-082（compile_to_mo使用polib生成.mo）；F-087~F-097（convert_catalog_to_json生成Jed JSON）；F-047（compile_package对每个po同时调用convert_catalog_to_json和compile_to_mo）；F-112（wheel构建时compile_po_file同时生成两种格式）
- **反常识**：JSON格式中，有上下文（msgctxt）的key使用 `\x04`（EOT控制字符）分隔msgctxt和msgid（F-091），这是gettext的约定（"context\x04msgid"），不是普通的拼接字符。单复数形式在JSON中用数组表示，且nplurals=1的语言（如韩语）需要追加空字符串以满足JupyterLab前端校验（F-095）。
- **行动**：需要专门的概念文档讲解Jed JSON格式细节，特别是EOT分隔符和复数处理的坑点。

### 洞察5：构建时自动编译 — Hatch Hook + Entry Points

- **陈述**：通过Hatch Build Hook实现构建时自动编译：wheel构建时自动将.po编译为.json和.mo（并排除.po），sdist保留.po源文件。运行时通过entry points（jupyterlab.languagepack和jupyterlab.locale）发现已安装的语言包和扩展翻译。
- **证据**：F-011~F-012（hatch entry point注册）；F-105~F-113（JupyterLanguageBuildHook实现）；F-098~F-103（finder.py通过entry points发现语言包）；F-142（测试验证wheel包含.json/.mo，sdist包含.po）
- **反常识**：finder.py中的 `merge_data()` 函数是空实现（F-100），意味着运行时合并语言包数据和扩展包locale数据的功能尚未完成，目前只提供了查找接口。另外，Hatch Hook在非wheel构建时（如sdist）不编译PO，而是尝试更新贡献者列表。
- **行动**：需要文档说明如何在自己的扩展中配置Hatch Hook实现自动编译，以及entry points的配置方式。

## 知识地图

### 学习路径

```
入门层（了解是什么）
├── 00-introduction.md          → 项目定位、功能概览、安装
├── 01-getting-started.md       → 快速上手：3条命令完成翻译流程
└── 02-architecture-overview.md → 三层架构、双模式分发、数据流向

核心层（理解怎么工作）
├── 03-cli-commands.md          → CLI命令详解（6个子命令+选项）
├── 04-extraction-pipeline.md   → 三源字符串提取（Python/TS/Schema）
├── 05-catalog-management.md    → POT/PO/MO/JSON目录结构与管理
├── 06-json-jed-format.md       → Jed JSON格式详解（EOT分隔符、复数处理）
├── 07-hatch-build-hook.md      → 构建时自动编译集成
└── 08-runtime-discovery.md     → 运行时语言包发现（entry points + finder）

进阶层（扩展与定制）
├── 09-schema-i18n-selectors.md → JSON Schema自定义翻译选择器
├── 10-contributors-crowdin.md  → Crowdin贡献者集成
└── 11-dual-mode-distribution.md → 独立包 vs 语言包仓库两种模式
```

### 文档清单

#### references/（信源登记）
| 文件 | 类型 | 内容 |
|------|------|------|
| cli-source.md | Reference | cli.py CLI命令源码映射 |
| api-source.md | Reference | api.py API层源码映射 |
| utils-source.md | Reference | utils.py核心工具源码映射 |
| converters-source.md | Reference | converters.py格式转换源码映射 |
| finder-source.md | Reference | finder.py运行时发现源码映射 |
| plugin-source.md | Reference | plugin.py Hatch Hook源码映射 |
| constants-config.md | Reference | 常量与配置（constants.py + pybabel_config.cfg） |
| contributors-source.md | Reference | contributors.py Crowdin集成源码 |

#### concepts/（概念文档）
| 文件 | 标题 | 覆盖事实 |
|------|------|---------|
| 00-introduction.md | JupyterLab Translate 简介 | F-001~F-016 |
| 01-getting-started.md | 快速开始 | F-136~F-140 |
| 02-architecture-overview.md | 架构总览 | F-017~F-018, F-033~F-052, 洞察1-5 |
| 03-cli-commands.md | CLI命令参考 | F-009~F-010, F-033~F-042 |
| 04-extraction-pipeline.md | 字符串提取流水线 | F-027~F-032, F-060~F-078 |
| 05-catalog-management.md | 翻译目录管理 | F-079~F-086, F-128~F-135 |
| 06-json-jed-format.md | Jed JSON翻译格式 | F-087~F-097 |
| 07-hatch-build-hook.md | Hatch构建钩子集成 | F-011~F-012, F-105~F-113 |
| 08-runtime-discovery.md | 运行时语言包发现 | F-098~F-104 |
| 09-schema-i18n-selectors.md | JSON Schema国际化选择器 | F-065~F-070 |
| 10-contributors-crowdin.md | Crowdin贡献者集成 | F-116~F-125 |
| 11-dual-mode-distribution.md | 双模式分发机制 | F-045~F-053, F-132~F-135 |

#### examples/（示例文档）
| 文件 | 标题 | 内容 |
|------|------|------|
| 01-basic-extension-i18n.md | 扩展包国际化基础流程 | 从零配置到编译的完整示例 |
| 02-language-pack-workflow.md | 语言包仓库工作流 | extract_pack→update_pack→compile_pack示例 |
| 03-custom-schema-selectors.md | 自定义Schema选择器 | 配置jupyter.lab.internationalization示例 |
| 04-hatch-hook-integration.md | Hatch构建钩子配置 | pyproject.toml配置示例 |
