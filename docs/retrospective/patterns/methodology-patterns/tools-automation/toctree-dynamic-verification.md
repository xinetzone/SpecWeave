---
id: "toctree-dynamic-verification"
title: "toctree 动态验证法"
type: methodology-pattern
date: 2026-08-24
maturity: L1-draft
maturity_note: "单案例验证（awesome-okf-xs check-toctrees.py 门禁 + A-2 一致性检查），待二次验证"
source: "../../../reports/documentation-governance/retrospective-sphinx-toctree-clear-20260824/README.md#3-e-萃取g3-通过模式可迁移"
related_patterns:
  - "validation-semantic-gap.md"
  - "spec-as-code-automated-gates.md"
  - "link-check-dual-coverage.md"
  - "tool-self-validation.md"
  - "dry-run-first.md"
  - "../process-patterns/okf-bundle-toctree-repair-workflow.md"
tags: ["toctree", "sphinx", "myst", "verification", "ci-gate", "reachability", "consistency-check"]
validation_count: 1
reuse_count: 0
---

# toctree 动态验证法

## 触发场景

- 当需要验证 Sphinx/MyST 文档集的目录树（toctree）导航完整性时——所有文档是否可达、是否被正确收录
- 当需要把"目录文件清单一致性"约束落地为 CI 门禁，防止 toctree 与磁盘内容静默漂移时
- 当已有一个简单验证脚本（如 `.temp/verify_toctrees.py` BFS 可达性），需要演进为可长期运行的自动化门禁时

**识别信号**：
- 文档集规模大（数百~数千文档），人工核对 toctree 清单不可行
- 现有门禁只验"全局可达"，但新增文档经其他路径可达却漏收录所在目录 toctree（静默漂移）
- 验证脚本把文档内的 toctree 语法示例当真实引用，产生误报

## 不适用场景（反目标用户/场景）

- **单目录/小文档集**（<50 文档）：人工维护 toctree 即可，脚本化收益低，本模式不适用
- **纯内容质量验证需求**：目标是处理 myst.header/topmatter 等内容告警——本模式只验证目录树结构，对内容质量不适用
- **无 toctree 结构的纯 Markdown 平铺文档**：无目录树可验，本模式不适用
- **一次性交付即归档的文档集**：构建后不再持续演进、无长期维护，部署 CI 门禁不合适（过度工程）

## 问题背景

toctree 是 Sphinx/MyST 的导航骨架，其完整性有两类独立的失效模式：

1. **全局不可达**：文档未加入任何 toctree，构建报 `toc.not_included`（R-2：4888 警告）。
2. **局部漏收录**：文档**经其他路径全局可达**，但其**所在目录的 toctree 未收录自身内容**——目录 toctree 与磁盘内容静默漂移，新增内容易漏收录（I-7）。这类问题**只验全局可达性的门禁无法发现**（R-13/R-15）。

同时，验证工具自身存在解析陷阱：文档正文中的 `{toctree}` **语法示例**（含 `---`、`maxdepth: 2` 等选项行）会被误判为真实引用条目，导致误报（I-6/R-6：本案例误报 12 处）。

本模式通过 **BFS 可达性 + 单目录清单一致性 + 选项行/示例过滤 + 自检用例** 四要素，将 toctree 验证从一次性脚本演进为可长期运行的 CI 门禁。

## 核心步骤（5步）

1. **BFS 可达性验证**：从根文档出发 BFS 遍历 toctree 引用图，识别 `toc.not_included`（未加入任何目录树）的游离文档（演进自 `.temp/verify_toctrees.py`）。
2. **单目录清单一致性检查（check_consistency）**：对每个含 toctree 的 index.md，比对目录内容清单（子目录 index 与直接 .md 文件）与 toctree 实际收录条目，识别"文件经其他路径可达但其所在目录 toctree 未收录自身内容"的盲区（A-2 新增，R-14/R-15）。
3. **过滤 toctree 选项行与语法示例**：解析 toctree 条目时过滤 `---`、`maxdepth: 2` 等选项行，并排除非 toctree 代码块中的 `{toctree}` 语法示例（I-6）。
4. **演进为 CI 门禁**：将验证逻辑沉淀为 `scripts/check-toctrees.py`，接入 `.github/workflows/pages.yml`，作为提交/构建前的强制检查（R-13）。
5. **自检用例覆盖盲区**：提供 `--self-test` 用例集，其中 `consistency` 用例必须覆盖"文件经其他路径可达但其所在目录 toctree 未收录"这一盲区，防止门禁自身退化（R-15：5 用例全部通过）。

## 反模式（不要这么做）

- ❌ **AP-1 把示例代码块当真实引用**：不区分"真实 toctree 条目"与"文档内的 toctree 语法示例"，把 `---`、`maxdepth: 2`、示例子条目都当真实引用 → 误报（本案例 12 处）→ **正确做法**：过滤选项行，排除非 toctree 代码块中的语法示例。
- ❌ **AP-2 只验全局可达漏判单目录缺失条目**：门禁只做 BFS 全局可达性，不做单目录清单比对 → "文件经其他路径可达但所在目录 toctree 未收录"静默漂移（R-13 盲区）→ **正确做法**：A-2 并入 `check_consistency` 单目录清单一致性比对。
- ❌ **AP-3 一次性脚本不沉淀为门禁**：验证逻辑只存在于 `.temp/` 临时脚本，不演进为 CI 门禁 → 修复后无人持续检查，同类问题复发 → **正确做法**：沉淀为 `scripts/check-toctrees.py` 并接入 CI。
- ❌ **AP-4 门禁无自检退化防护**：验证脚本修改后可能悄悄丢失对盲区的检查，却无测试兜底 → 门禁"形同虚设" → **正确做法**：`--self-test` 用例集覆盖盲区（consistency 用例），每次改动回归验证。

## 失败案例

- **案例1（语法示例误判为真实引用，误报 12 处）**：早期验证脚本解析 toctree 条目时，把文档正文中的 `{toctree}` 语法示例（含 `---`、`maxdepth: 2` 选项行）误判为真实引用，误报 12 处缺失引用（I-6/R-6）。**失败根因**：未区分"真实 toctree 条目"与"文档内语法示例"，未过滤选项行。
- **案例2（门禁只验全局可达，漏判单目录缺失条目）**：初版门禁只做 BFS 全局可达性，"文件经其他路径可达但其所在目录 toctree 未收录"的静默漂移漏判（R-13 盲区）。**失败根因**：验证维度单一，未做单目录文件清单与 toctree 收录条目的比对。

## 检验标准

- [ ] 真实文档树运行 `check-toctrees.py` 零缺失条目（R-15）
- [ ] `--self-test` 全部用例通过，且 `consistency` 用例覆盖"经其他路径可达但单目录未收录"盲区
- [ ] 无 toctree 选项行/语法示例导致的误报
- [ ] dummy 构建 `toc.not_included` 为 0（可达性验证通过）
- [ ] 已接入 CI 门禁（pages.yml），提交/构建前自动执行

## 迁移示例

- **场景1（其他文档导航体系）**：Hugo/VuePress/Jekyll 的菜单/导航清单与目录文件一致性校验——同样需要"单目录清单比对 + 语法示例过滤 + 自检用例"。
- **场景2（软件包依赖树）**：conda/pip 依赖树的"可达性 + 完整性"验证——BFS 可达性对应依赖闭包，单目录清单一致性对应"某包声明依赖 vs 实际依赖文件清单"比对。
- **场景3（链接/引用验证）**：任意链接检查工具都可补"对象存在但引用清单未收录"的一致性检查维度（与 [link-check-dual-coverage](link-check-dual-coverage.md) 的"显性+隐性引用"互补）。

## 与其他模式的关系

| 关联模式 | 关系类型 | 关系说明 |
|---------|---------|---------|
| [validation-semantic-gap.md](validation-semantic-gap.md) | 理论支撑 | 本模式是"验证层级语义缺口"在 toctree 场景的应用——"全局可达"是 L2 应用层验证，"单目录清单一致"是 L3 约定层验证 |
| [spec-as-code-automated-gates.md](spec-as-code-automated-gates.md) | 落地方式 | 把"toctree 完整性"规范写成自动化门禁脚本并接入 CI，正是 Spec-as-Code 的具体实现 |
| [link-check-dual-coverage.md](link-check-dual-coverage.md) | 互补 | 链接检查双覆盖（显性+隐性引用）关注"链接是否被检查"，本模式关注"toctree 是否收录全部内容" |
| [tool-self-validation.md](tool-self-validation.md) | 前置依赖 | `--self-test` 自检用例确保验证工具自身不退化，是工具自生验证的一种形式 |
| [dry-run-first.md](dry-run-first.md) | 方法关联 | 修复脚本 dry-run 与验证门禁结合，形成"验证-修复-再验证"闭环 |
| [okf-bundle-toctree-repair-workflow.md](../../process-patterns/okf-bundle-toctree-repair-workflow.md) | 配套修复 | 本模式负责"验证"，该模式负责"修复"，二者构成修复+门禁闭环 |

## 验证状态

- ✅ 本次任务验证：`check-toctrees.py` 演进为断链 + 可达性 + A-2 一致性三类检查；`--self-test` 5 用例通过，其中 `consistency` 用例覆盖单目录缺失条目盲区；真实树零缺失条目
- ⚠️ 待推广：需在第二类文档集（其他 Sphinx/知识库项目）上二次验证后升级 L2

## 关联资源

- 来源复盘：[awesome-okf-xs Sphinx toctree 警告清零里程碑复盘](../../../reports/documentation-governance/retrospective-sphinx-toctree-clear-20260824/README.md)
