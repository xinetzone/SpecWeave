+++
id = "finding-concept-domain-separation"
date = "2026-06-26"
type = "insight"
scope = "shared-library,architecture,module-design"
source = "../insight-extraction.md#发现-3共享库的概念域分离原则"
archived_to = "docs/retrospective/patterns/methodology-patterns/governance-strategy/structure-first-extension.md"
+++

# 发现3：共享库的"概念域分离"原则

→ 正式模式：[structure-first-extension.md](../../../../../patterns/methodology-patterns/governance-strategy/structure-first-extension.md)（结构优先扩展 L3）

## 事件发现

`lib/` 包按概念域组织为多个模块，每个模块聚焦单一关注点。新增 `lib/markdown.py` 时，先阅读 `lib/__init__.py` 了解现有模块组织，确认"Markdown 处理"是独立概念域后新建模块，而非追加到已有的 `lib/cli.py` 或 `lib/link_fixer.py`。

后续执行复盘建议时，新增 `parse_toml_frontmatter_as_dict` 放入现有 `lib/frontmatter.py`（属于frontmatter解析概念域），而非新建模块。添加 `lib/rules.py` 时确认"误报过滤规则引擎"是独立于已有模块的新概念域。

## 模块概念域表

| 模块 | 概念域 | 职责 |
|------|--------|------|
| `lib/project.py` | 路径解析 | 项目根目录自适应定位 |
| `lib/cli.py` | CLI输出与参数 | 终端彩色输出与通用参数注册 |
| `lib/frontmatter.py` | 元数据解析 | TOML frontmatter 解析与字段提取 |
| `lib/markdown.py` | Markdown处理 | 文件遍历、标题/描述提取、标记区替换 |
| `lib/link_fixer.py` | 链接处理 | 链接解析、修复、路径校正 |
| `lib/patterns.py` | 模式成熟度分析 | 成熟度字段检查与升级建议 |
| `lib/spec/` | Spec体系 | spec 解析、检查、目录发现 |
| `lib/checks/` | 检查器框架 | CheckResult基类与共享逻辑 |
| `lib/rules.py` | 误报过滤规则 | 通用规则加载与四层过滤 |

## 规律

共享库应按概念域分离（而非按功能类型），每个模块用一句话即可描述职责。违反此原则会导致模块膨胀和导入链混乱。

## 关联洞察

- [law-02-shared-lib-gravity.md](law-02-shared-lib-gravity.md) — 概念域覆盖度决定引力效应
- [finding-07-tool-self-validation.md](finding-07-tool-self-validation.md) — 新工具开发也需遵循概念域原则

---
*来源：[脚本共享库提取复盘](../README.md)*
