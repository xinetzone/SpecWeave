---
id: awesome-okf-facts
title: Awesome OKF 深度分析 - 事实清单（R阶段）
type: Facts
version: 1.0
source: yzfly/awesome-okf (commit 730e6ff 附近)
description: awesome-okf 项目客观事实清单，覆盖Producer插件、Skill工作流、扩展提案、Dogfooding四个维度
tags: [okf, awesome-okf, 事实, retrospective]
category: case-study
date: 2026-08-06
---

# Awesome OKF 深度分析 - 事实清单（R阶段）

> **说明**：本清单仅记录客观事实（"是什么"），不包含因果判断或价值评价。OKF通用概念（如frontmatter、Bundle定义）请参考 [okf-wiki](../README.md) 对应章节，不在此处重复。

---

## 一、项目概览事实

**F01**：awesome-okf 仓库定位为"中文世界第一个OKF落点"，包含规范翻译、7个producer插件、7个Claude Code Skill、3份向上游扩展提案，自身即符合OKF v0.1规范的bundle。
- 证据：[README.md](file:///d:/AI/vendor/awesome-okf/README.md#L1-L16) 第4行描述、第15行内容清单、第103行dogfooding声明

**F02**：仓库根目录存在 `index.md`，其frontmatter仅包含 `okf_version: "0.1"` 一个字段，符合OKF v0.1对根index.md的约定。
- 证据：[index.md](file:///d:/AI/vendor/awesome-okf/index.md#L1-L3)

**F03**：README.md的frontmatter包含 `type: Overview`、`title`、`description`、`tags`、`lang: zh`、`timestamp`、`author` 字段，其中 `lang: zh` 为i18n扩展字段。
- 证据：[README.md](file:///d:/AI/vendor/awesome-okf/README.md#L1-L9)

---

## 二、Producer插件维度事实（plugins/）

**F04**：仓库包含7个producer/consumer工具插件，分别为：feishu-to-okf、obsidian-to-okf、notion-to-okf、github-to-okf、awesome-to-okf、html-to-okf、myokf-cli（统一CLI入口）。
- 证据：[README.md](file:///d:/AI/vendor/awesome-okf/README.md#L37-L49) 工具表格

**F05**：myokf-cli的 `pyproject.toml` 中 `dependencies = []`，即零第三方Python依赖，仅使用Python标准库。
- 证据：[pyproject.toml](file:///d:/AI/vendor/awesome-okf/plugins/myokf-cli/pyproject.toml#L10)

**F06**：awesome-to-okf的 `pyproject.toml` 中 `dependencies = []`，注释标注"仅用标准库，开箱即跑"。
- 证据：[pyproject.toml](file:///d:/AI/vendor/awesome-okf/plugins/awesome-to-okf/pyproject.toml#L10)

**F07**：feishu-to-okf的 `pyproject.toml` 中 `dependencies = []`，注释标注"仅用标准库"。
- 证据：[pyproject.toml](file:///d:/AI/vendor/awesome-okf/plugins/feishu-to-okf/pyproject.toml#L10)

**F08**：myokf-cli通过 `MODULES` 字典实现子命令分发，包含两种执行方式：`"module"`（通过PYTHONPATH注入后 `python -m` 执行）和 `"script"`（直接 `python 脚本路径` 执行）。
- 证据：[cli.py](file:///d:/AI/vendor/awesome-okf/plugins/myokf-cli/src/myokf/cli.py#L33-L43) MODULES字典定义、第48-57行_run_module/_run_script实现

**F09**：myokf-cli的根路径定位方式为 `Path(__file__).resolve().parents[4]`，即从 `plugins/myokf-cli/src/myokf/cli.py` 向上回溯4级到达仓库根目录。
- 证据：[cli.py](file:///d:/AI/vendor/awesome-okf/plugins/myokf-cli/src/myokf/cli.py#L30)

**F10**：myokf-cli的 `to-web` 子命令为特殊实现：先调用build_web.py生成HTML，若检测到系统有node则调用minify.mjs压缩，无node则输出未压缩版本并打印警告。
- 证据：[cli.py](file:///d:/AI/vendor/awesome-okf/plugins/myokf-cli/src/myokf/cli.py#L59-L88)

**F11**：validate_okf.py校验器实现了"优先用PyYAML，缺失时回退到内置最小YAML解析器"的降级策略，确保零依赖也能运行。
- 证据：[validate_okf.py](file:///d:/AI/vendor/awesome-okf/skills/okf-creator/scripts/validate_okf.py#L28-L47) try-except ImportError块

**F12**：validate_okf.py的硬性检查项共3条：(1)每个非保留.md文件含可解析YAML头信息；(2)头信息含非空type字段；(3)index.md/log.md遵循保留文件结构。
- 证据：[validate_okf.py](file:///d:/AI/vendor/awesome-okf/skills/okf-creator/scripts/validate_okf.py#L2-L8) docstring、第72-88行check_concept实现

**F13**：validate_okf.py对description缺失仅输出warn（SHOULD级别），对type缺失/头信息缺失/index.md含非法字段输出error（MUST级别）。
- 证据：[validate_okf.py](file:///d:/AI/vendor/awesome-okf/skills/okf-creator/scripts/validate_okf.py#L82-L87)

---

## 三、Skill维度事实（skills/）

**F14**：仓库包含7个Claude Code Skill，分别为：okf-creator、awesome-to-okf、book-to-okf、code-to-okf、github-to-okf、okf-to-book、okf-to-web。
- 证据：[README.md](file:///d:/AI/vendor/awesome-okf/README.md#L51-L62) Skill表格

**F15**：okf-creator SKILL.md的frontmatter同时包含两套字段：Claude Code Skill要求的 `name`/`description`，与OKF要求的 `type: Skill`/`title`/`lang`/`tags`/`license`。
- 证据：[SKILL.md](file:///d:/AI/vendor/awesome-okf/skills/okf-creator/SKILL.md#L1-L9)

**F16**：okf-creator明确声明"OKF的硬要求极低，本Skill的真正价值不在产出合规文件，而在产出读了就懂、agent检索得动的知识"。
- 证据：[SKILL.md](file:///d:/AI/vendor/awesome-okf/skills/okf-creator/SKILL.md#L13)

**F17**：okf-creator定义了5条核心原则（按重要性排序）：(1)先定边界再动手；(2)一个概念一个文件，路径即概念ID；(3)正文用结构不用流水账；(4)链接成图；(5)质量自检。
- 证据：[SKILL.md](file:///d:/AI/vendor/awesome-okf/skills/okf-creator/SKILL.md#L22-L28)

**F18**：okf-creator列出了5条反模式：(1)巨型概念文件；(2)散文式正文无结构；(3)只贴代码不解释；(4)图片不写图说；(5)跳过validate_okf.py。
- 证据：[SKILL.md](file:///d:/AI/vendor/awesome-okf/skills/okf-creator/SKILL.md#L62-L68)

**F19**：code-to-okf Skill定义了9种代码类型词表：`Repository | Package | Module | Class | Function | Interface | Config | Script | Notebook`。
- 证据：[SKILL.md](file:///d:/AI/vendor/awesome-okf/skills/code-to-okf/SKILL.md#L22)

**F20**：code-to-okf为代码概念定义了3个扩展frontmatter字段：`language`（编程语言）、`symbol`（符号全名）、`signature`（函数签名），并约定resource使用GitHub permalink带行号锚点 `#Lxx-Lyy`。
- 证据：[SKILL.md](file:///d:/AI/vendor/awesome-okf/skills/code-to-okf/SKILL.md#L26-L39)

**F21**：code-to-okf定义了有类型链接前缀约定：`calls:`、`depends-on:`、`implements:`、`deprecated-by:`，通过链接文字前缀表达关系类型，既人读友好又可被简单规则机读。
- 证据：[SKILL.md](file:///d:/AI/vendor/awesome-okf/skills/code-to-okf/SKILL.md#L51-L60)

**F22**：code-to-okf的正文结构约定包含5个标准章节：`# Signature`、`# Behavior`、`# Calls`、`# Cited by`、`# Examples`。
- 证据：[SKILL.md](file:///d:/AI/vendor/awesome-okf/skills/code-to-okf/SKILL.md#L41-L49)

---

## 四、扩展提案维度事实（docs/）

**F23**：仓库包含3份向后兼容的扩展提案：(1)i18n扩展（`lang` + `canonical`字段）；(2)代码支持扩展（类型词表、扩展字段、行号锚点、有类型链接）；(3)HTML一等公民扩展（`.html`作为合法概念文件）。
- 证据：[README.md](file:///d:/AI/vendor/awesome-okf/README.md#L72-L77) 三份提案清单；[dogfooding-zh.md](file:///d:/AI/vendor/awesome-okf/docs/dogfooding-zh.md#L121)

**F24**：三份扩展提案均遵循同一原则：只做向后兼容的次版本新增，不动任何MUST级别的硬要求。
- 证据：[html-first-class-proposal-zh.md](file:///d:/AI/vendor/awesome-okf/docs/html-first-class-proposal-zh.md#L97-L100) 向后兼容性声明；[code-support-research-zh.md](file:///d:/AI/vendor/awesome-okf/docs/code-support-research-zh.md#L54) "不动任何MUST"声明

**F25**：HTML一等公民提案为HTML概念设计了3种元数据编码方式（推荐度递减）：(A)前置OKF注释块 `<!--okf ... -->`；(B)`<head>`中的meta标签；(C)内嵌 `<script type="application/okf+yaml">` 块。
- 证据：[html-first-class-proposal-zh.md](file:///d:/AI/vendor/awesome-okf/docs/html-first-class-proposal-zh.md#L29-L65)

**F26**：HTML一等公民提案推荐"双表示"模式：HTML文件内嵌 `<script type="text/markdown" id="okf-body">` 存放纯文本/Markdown镜像，agent直接取该脚本内容无需解析DOM。
- 证据：[html-first-class-proposal-zh.md](file:///d:/AI/vendor/awesome-okf/docs/html-first-class-proposal-zh.md#L67-L80)

**F27**：i18n扩展提案使用两个字段：`lang`（BCP 47语言标签，如zh/en）标识正文语言，`canonical`（规范概念的包内绝对路径）实现多语言去重，同一概念的不同语言版本通过canonical互链。
- 证据：[okf-spec-zh.md](file:///d:/AI/vendor/awesome-okf/docs/okf-spec-zh.md#L1-L10) frontmatter包含 `lang: zh` 和 `canonical` 指向官方英文版；[html-first-class-proposal-zh.md](file:///d:/AI/vendor/awesome-okf/docs/html-first-class-proposal-zh.md#L104-L112) 双表示canonical约定

**F28**：代码支持调研结论明确指出：OKF v0.1面向数据知识（表、数据集、指标、术语表、操作手册）设计，三个官方示例bundle（crypto_bitcoin、ga4、stackoverflow）全是数据类，无代码bundle。
- 证据：[code-support-research-zh.md](file:///d:/AI/vendor/awesome-okf/docs/code-support-research-zh.md#L13-L23)

---

## 五、Dogfooding维度事实

**F29**：awesome-okf仓库自身作为OKF v0.1合规范例（dogfooding），每个非保留.md文件都带YAML头信息且有非空type字段。
- 证据：[dogfooding-zh.md](file:///d:/AI/vendor/awesome-okf/docs/dogfooding-zh.md#L17) 第1条；[README.md](file:///d:/AI/vendor/awesome-okf/README.md#L103-L107)

**F30**：dogfooding实践使用了7种概念type取值：`Overview`、`Specification`、`Article`、`Reference`、`Producer`、`Skill`、`Resource`。
- 证据：[dogfooding-zh.md](file:///d:/AI/vendor/awesome-okf/docs/dogfooding-zh.md#L19)

**F31**：所有中文文档统一标注 `lang: zh`，为i18n提案打样；okf-spec-zh.md同时标注 `canonical` 指向官方英文SPEC.md。
- 证据：[dogfooding-zh.md](file:///d:/AI/vendor/awesome-okf/docs/dogfooding-zh.md#L20)；[okf-spec-zh.md](file:///d:/AI/vendor/awesome-okf/docs/okf-spec-zh.md#L7) canonical字段

**F32**：SKILL.md文件的frontmatter同时满足两套规范：Claude Code Skill需要的 `name`/`description`，与OKF需要的 `type`，两者共存，Skill加载器忽略不认识的键。
- 证据：[dogfooding-zh.md](file:///d:/AI/vendor/awesome-okf/docs/dogfooding-zh.md#L33-L36)

**F33**：仓库根目录log.md未使用 `## YYYY-MM-DD` 日期标题格式，而是使用 `### 初始化建立` 和 `### 持续收集整理` 两个分类标题，validate_okf.py对此仅输出warn而非error。
- 证据：[log.md](file:///d:/AI/vendor/awesome-okf/log.md#L1-L49)；[validate_okf.py](file:///d:/AI/vendor/awesome-okf/skills/okf-creator/scripts/validate_okf.py#L107-L115) check_log实现

**F34**：references/目录下有12个社区头部工具被提升为一等OKF概念文件（各带frontmatter+互链），完整60+工具清单仍保留在docs/resources-zh.md中。
- 证据：[log.md](file:///d:/AI/vendor/awesome-okf/log.md#L39-L40) 记录"把头部社区仓库提升为一等OKF概念文件"

---

## 事实统计

| 维度 | 事实数量 | 编号范围 |
|---|---|---|
| 项目概览 | 3 | F01-F03 |
| Producer插件 | 10 | F04-F13 |
| Skill工作流 | 9 | F14-F22 |
| 扩展提案 | 6 | F23-F28 |
| Dogfooding | 6 | F29-F34 |
| **总计** | **34** | F01-F34 |

---

**G1质量门自检**：
- ✅ 事实总数34条 ≥ 20条
- ✅ 覆盖四个维度：Producer插件(10)、Skill工作流(9)、扩展提案(6)、Dogfooding(6)
- ✅ 所有事实为客观描述，不含因果判断词
- ✅ 每条事实附带具体文件路径和行号引用
- ✅ 事实按编号F01-F34有序组织
- ✅ 聚焦awesome-okf特有内容，OKF通用概念通过链接指向okf-wiki
