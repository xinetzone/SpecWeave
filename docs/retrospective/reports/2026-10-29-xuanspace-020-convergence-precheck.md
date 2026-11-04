---
id: "precheck-20261029-xuanspace-020-convergence"
type: Report
title: "xuanspace 0.2.0 发布前「收口期三线」预检：三门禁拦截验证有效，线1/线3 各留必修项"
date: 2026-10-29
scope: project
status: active
topic: xuanspace-release-governance
source: "行动项 A-05（源报告：docs/retrospective/reports/2026-10-29-xuanspace-october-governance-retro.md）：在 xuanspace 0.2.0 发布前执行「收口期三线」预检清单，作为 convergence-period-triple-track 模式的首次复用验证。检查基准：xuanspace HEAD `991f635`（2026-10-29）。"
pattern: "convergence-period-triple-track"
x-toml-ref: "../../../.meta/toml/docs/retrospective/reports/2026-10-29-xuanspace-020-convergence-precheck.toml"
tags: ["release-governance", "convergence", "quality-gate", "precheck", "xuanspace", "pattern-reuse"]
---

# xuanspace 0.2.0 发布前「收口期三线」预检

## 执行摘要

对第一方子项目 [xuanspace（玄境）](../../../projects/xuanspace/README.md) 执行
`convergence-period-triple-track` 模式的**首次复用**：把复盘（2026-10-29）萃取的
「版本定源 → 门禁固化 → 文档诚实化」三线，转写为可在发布前逐项判定的预检清单，
并在 HEAD `991f635` 上逐条实测。

**结论：0.2.0 发布资格为「有条件放行」——3 项必修、3 项登记、7 项通过。**

| 线 | 判定 | 关键证据 |
|---|---|---|
| 线1 版本元数据定源 | ⚠️ 基本闭合，1 项必修 | `tools/okf` 仍保留 `__version__` 双声明，无门禁覆盖 |
| 线2 约定门禁化 | ✅ 闭合 | 三门禁本地全绿；两处人为注入漂移均被拦截（exit 1） |
| 线3 文档诚实化 | ❌ 未闭合，2 项必修 | README 索引版本列与子模块指针漂移；`libs/caffe-ffi/docs/**` 40 处断链 |

**模式复用验证结论**：检验标准 1~5 在第二个收口窗口上**形式不变地复用成功**，
且预检本身产出 3 项必修——证明清单不是走过场。但本次为**同一项目、同一谱系**
的第二个收口窗口，与模式原文「第二个非同谱系案例」的 L2 判据存在冲突，
裁决见 [§5](#5-模式成熟度裁决待定)。

---

## 1. 预检基准与口径

| 项 | 值 |
|---|---|
| 检查对象 | `projects/xuanspace` @ `991f635`（工作区干净，`git status` 空） |
| 发布目标 | 0.2.0（`CHANGELOG.md` 仍为 `[Unreleased]`，仓库无 tag） |
| 触发窗口 | 0.1.0（2026-07-23）之后的第一个收口期 |
| 门禁基线 | `scripts/check_pyproject_style.py`、`check_declaration_consistency.py`、`check_dependency_direction.py` |
| 本地 Python | 3.13.14（三门禁脚本仅依赖标准库，可本地复现；CI 为 3.14） |

**口径声明**：断链统计只计仓内 `.md`/目录型相对链接，排除 `http(s)`、`<占位>`、
含空格的伪链接、`vendor/` 与 `doc/_build` 目标——未收敛口径的粗扫为 106 条，
其中绝大多数是 C++ 符号与未初始化子模块路径造成的误报。

---

## 2. 预检清单与实测结果

### 线1：版本与构建元数据定源

| # | 预检项 | 判定方式 | 实测 | 结果 |
|---|---|---|---|---|
| T1-1 | 版本号单一真源 | 仓库内无 `__version__` 与 `[project].version` 并存 | `tools/xs` 已清理（F-019）；**`tools/okf/src/okf/__init__.py:3` 仍为 `__version__ = "0.1.0"`**，与 `[project].version` 并列 | ❌ 必修 |
| T1-2 | 构建后端统一 | 全部 pyproject `build-backend == scikit_build_core.build`、无 setuptools 残留 | 12 个 pyproject 全部合规 | ✅ |
| T1-3 | 构建下限统一 ≥0.11 | `check_pyproject_style.py` 规则 6 | 全部 ≥0.11（写法两种：`>=0.11` / `>=0.11.0`，语义等价） | ✅（形态瑕疵） |
| T1-4 | 许可形态统一 | 各 pyproject `license` 字段比对 | 11 个 `Apache-2.0`；**`libs/xuan-compose` 为 `GPL-2.0-only`**（其 README 第 14 行声明「继承上游，不得重新许可」，属有意例外） | ⚠️ 例外未登记 |
| T1-5 | `requires-python` ≥3.14.6 | 与 AGENTS.md「所有子项目」条款比对 | **仅 `libs/xuan-compose` 为 `>=3.14`** | ⚠️ 待裁定 |
| T1-6 | 子模块指针 = 索引（A-04 G1-G3） | `git submodule status` 无 `+` 漂移 + 快照比对 | mystx `18f3486` / tvm-book `103bea7` / caffe `f938d88` / tvm-ffi `e9fdc58`，四项均无漂移 | ✅ |
| T1-7 | 发布坐标闭合 | `CHANGELOG` 有 `[0.2.0]` 段 + 存在 tag | `[Unreleased]` 未转段、`git tag` 为空；`release.yml` 由 `xs-cli-v*` tag 触发 | ⚠️ 发布动作未完成 |

### 线2：约定门禁化

| # | 预检项 | 判定方式 | 实测 | 结果 |
|---|---|---|---|---|
| T2-1 | 关键约定有可执行断言 | 三个门禁脚本覆盖面对账 | 构建风格 6 规则 / 声明一致性 六类 + G 类 / 依赖方向，共 3 脚本 | ✅ |
| T2-2 | 门禁进 CI 且失败即阻断 | `.github/workflows/ci.yml` 步骤与 `continue-on-error` 扫描 | 行 184/188/192 挂载三脚本；全文件无 `continue-on-error` | ✅ |
| T2-3 | linkcheck 不放行 | CI 配置与 F-015 复核 | 行 151 执行 `xs doc linkcheck`，无 `continue-on-error` | ✅ |
| T2-4 | **故意改一处副本 → 检查失败** | 注入人为漂移后跑门禁，须 exit 1 | 见 §3，两处均被拦截 | ✅ |
| T2-5 | 门禁与文档同步 | 门禁口径变更随提交同步文档 | F-027（依赖方向门禁 + 文档 + CI 同步） | ✅ |

### 线3：文档诚实化

| # | 预检项 | 判定方式 | 实测 | 结果 |
|---|---|---|---|---|
| T3-1 | 顶层无 `docs/`（文档目录为 `doc/`） | 门禁 C 类断言 | 通过 | ✅ |
| T3-2 | 相对链接统一带 `.md` | 链接形态统计 | 451 条受检链接中 10 条为目录型（无 `.md`） | ⚠️ 轻微 |
| T3-3 | 无失效陈述 / 断链 | 仓内 `.md` 相对链接目标存在性 | **43 条断链**：`doc/okf/synthesis.md` 3 条（示例占位引用）+ `libs/caffe-ffi/docs/**` 40 条（历史过程性文档引用已删/未随迁文件），其中 1 条指向已废止的 `.agents/docs/` 路径 | ❌ 必修 |
| T3-4 | 索引版本列 ↔ 指针/清单 | README「项目索引」版本列 vs `git submodule status` 标签 | **`tvm-ffi` 标 `v0.1.12`，实际 `v0.1.15-36-ge9fdc58`**（A-04 推进指针后未同步）；`mystx` 标 `-` 而实际 `v0.3.8-9`（与 `tvm-book` 填 `v0.1.4` 口径不一） | ❌ 必修 |
| T3-5 | 索引条目 ↔ 目录实态 | 门禁 F 类断言 | 13 行 = tools 3 + libs 8 + vendor 2，一致 | ✅ |

### 顺序约束（模式的硬条件）

| # | 预检项 | 实测 | 结果 |
|---|---|---|---|
| T0-1 | 线1 早于线2 早于线3 | 沿用复盘 F-018~F-019（10-27）→ F-022/F-023/F-027（10-27~28）→ F-028~F-031（10-28） | ✅ |
| T0-2 | 本轮线3 清理须在线1 缺口闭合后执行 | T1-1（okf `__version__`）未闭合 → **T3-3/T3-4 的清理动作须排在 B-01 之后** | ⚠️ 顺序待守 |

---

## 3. 拦截验证（检验标准 #2 的实测）

在干净工作区注入两处人为漂移，跑门禁后**立即还原**（还原后 `git status` 为空）：

| 注入 | 门禁 | 结果 |
|---|---|---|
| `libs/xuan-core/pyproject.toml` 的 `scikit-build-core>=0.11` → `>=0.9` | `check_pyproject_style.py` | exit **1**：「下限低于 0.11（PEP 639 元数据所需）」 |
| `README.md` 项目索引插入幽灵项 `ghost-lib` | `check_declaration_consistency.py` | exit **1**：「项目索引表 与事实不一致（声明多：['ghost-lib']）」 |

复现方式（注入→运行→`cp` 还原三步，勿在并发会话期间执行）：

```bash
cd projects/xuanspace
cp libs/xuan-core/pyproject.toml /tmp/xc.bak && cp README.md /tmp/readme.bak
# 注入后：python scripts/check_pyproject_style.py ; python scripts/check_declaration_consistency.py
cp /tmp/xc.bak libs/xuan-core/pyproject.toml && cp /tmp/readme.bak README.md && git status --short
```

**判定**：线2 的门禁不是「假绿」——漂移注入即失败，模式的检验标准 #2 成立。

---

## 4. 发布资格判定

| 类别 | 项 | 说明 |
|---|---|---|
| ❌ 必修（阻塞 0.2.0） | T1-1 | 清理 `tools/okf` 的 `__version__` 双声明（或为其补门禁断言） |
| | T3-4 | 同步 README 索引版本列（`tvm-ffi` → v0.1.15；统一 `mystx` 口径） |
| | T3-3 | 清理 `libs/caffe-ffi/docs/**` 40 处断链（删除失效引用或补回文件） |
| ⚠️ 登记（不阻塞） | T1-4 / T1-5 | 把 `xuan-compose` 的 GPL-2.0-only 与 `>=3.14` 登记为**显式例外**，否则每次预检都要重新裁定 |
| | T3-2 | 10 条目录型链接统一口径 |
| | T1-7 | 发布时 `[Unreleased]` → `[0.2.0]` + 打 `xs-cli-v*` tag |
| ✅ 通过 | T1-2、T1-3、T1-6、T2-1~T2-5、T3-1、T3-5、T0-1 | 共 10 项 |

---

## 5. 模式成熟度裁决（待定）

`convergence-period-triple-track` 现为 L1（`validation_count = 1`、`reuse_count = 0`）。
本次构成**第二次应用**，但两者谱系相同（同一项目、相邻的两个收口窗口），
与模式原文「失效条件与演进」条款的判据——*「出现第二个**非同谱系**案例
（如内容站点、合同交付）后可升 L2」*——存在冲突；而行动项 A-05 的文字承诺是
「验证后 L1→L2」。

| 选项 | 处置 | 影响 |
|---|---|---|
| A（严守原文判据） | 保持 L1，`reuse_count: 0 → 1`，在案例中登记「同谱系第二次复用」 | 判据不被稀释；L2 仍需一个非同谱系案例 |
| B（修订判据后升 L2） | 明确「同项目跨发布周期复用计 reuse，不计 validation」，并另设 L2 门槛 | A-05 字面达成，但等于放宽 L2 门槛 |

本报告**不擅自改判**——裁决前模式成熟度字段维持原值，待确认后按选项更新。

---

## 6. 行动项

| 编号 | 行动项 | 归属 | 状态 |
|---|---|---|---|
| B-01 | 清理 `tools/okf/src/okf/__init__.py` 的 `__version__` 双声明（版本单一真源），并评估是否补「`__version__` 不得并存」门禁断言 | xuanspace 子项目（需授权） | 待授权 |
| B-02 | 同步 README 项目索引版本列，并把「索引版本列 ↔ 子模块标签/清单版本」补为 G 类第 4 条断言（A-04 的自然延伸：G3 目前只覆盖 CONTRIBUTING §3.5） | xuanspace 子项目（需授权） | 待授权 |
| B-03 | 清理 `libs/caffe-ffi/docs/**` 40 处断链（失效过程性文档引用），与 F-029/F-030 同类动作 | xuanspace 子项目（需授权） | 待授权 |
| B-04 | 把 `libs/xuan-compose` 的 `GPL-2.0-only` 与 `>=3.14` 登记为显式例外（CONTRIBUTING 或子项目 README） | xuanspace 子项目（需授权） | 待授权 |
| B-05 | 按 §5 裁决更新 `convergence-period-triple-track` 的成熟度字段与案例证据 | SpecWeave 主权区 | 待裁决 |

> **执行顺序约束**：B-03（线3 删除动作）须排在 B-01（线1 定源）之后——
> 这是本模式顺序约束在本轮的直接应用，不得并行。

---

## 7. 关联资产

| 资产 | 关系 |
|---|---|
| [2026-10-29-xuanspace-october-governance-retro.md](2026-10-29-xuanspace-october-governance-retro.md) | 源复盘，行动项 A-05 的出处 |
| [convergence-period-triple-track](../patterns/methodology-patterns/governance-strategy/convergence-period-triple-track.md) | 被复用的模式（预检清单的方法论依据） |
| [xuanspace 子模块指针对账门禁 spec](../../../projects/xuanspace/.trae/specs/submodule-alignment-gate/spec.md) | A-04 产物，T1-6 的判据来源 |
| [xuanspace CHANGELOG](../../../projects/xuanspace/CHANGELOG.md) | T1-7 的检查对象 |
