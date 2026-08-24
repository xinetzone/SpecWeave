---
type: Retrospective
title: awesome-okf-xs Sphinx toctree 警告清零里程碑复盘（2026-08-24）
description: 基于 seven-concepts 编排（R→I→E→C），对 awesome-okf-xs 文档构建中 4888 个 toc.not_included 警告的根因分析、自动化修复脚本开发、867 文件变更与 2 个原子提交的完整复盘；2026-08-24 跟进推进 A-2——「toctree 与目录文件清单一致性校验」并入 check-toctrees.py 门禁
tags: [retrospective, sphinx, toctree, myst-parser, okf, awesome-okf-xs, milestone]
generated: { by: "process:seven-concepts", at: "2026-08-24" }
verified: { by: "process:seven-concepts", at: "2026-08-24" }
status: stable
source: "projects/awesome-okf-xs 文档构建 toc.not_included 警告清零任务"
---

# awesome-okf-xs Sphinx toctree 警告清零里程碑复盘

> 场景：里程碑复盘。链路：R（事实）→ I（洞察）→ E（萃取）→ C（原子提交）。
> 产出物关联：`.temp/fix_toctrees.py`（自动化脚本）、867 文件变更、2 个原子提交（`e661cd1` / `afc989b`）、本报告。
> **2026-08-24 跟进（A-2 推进）**：将「toctree 与目录文件清单一致性校验」并入既有 CI 门禁 `scripts/check-toctrees.py`——新增 `check_consistency` 一致性检查与 `consistency` 自检拦截用例，真实树零缺失条目。

## 1. R 事实采集（G1 通过：无因果词、可溯源）

| # | 事实 | 来源 |
|---|------|------|
| R-1 | Sphinx + MyST-Parser 构建；警告类型 `toc.not_included`（文档未加入任何目录树） | 构建日志 `.temp/build*.log` |
| R-2 | 初始警告数 4888；907 个 `index.md` 中仅 34 个含 `{toctree}`（约 96% 缺失） | Grep / Glob |
| R-3 | `doc/bundles/web/fastapi/fastapi`、`web/graphql/graphql`、`think/psi/psi-universe` 等 bundle 缺 `{toctree}` | 文件阅读 |
| R-4 | 正常 bundle（`document/katex`）index.md 含 `{toctree}` 引子目录 `concepts/examples/references` | 文件阅读 |
| R-5 | 项目无 `_toc.yml`、无 Makefile；构建由 `tasks.py` 管理 | LS/Glob |
| R-6 | 因文件含假 `{toctree}` 语法示例，验证脚本误报 12 处"缺失引用"；实际 0 不可达 | 脚本 double-check |
| R-7 | `extension-examples/`、`jupyter-client/` 无 index.md，子文档游离；`ai/trae/spec` 缺 index.md | 目录扫描 |
| R-8 | `ai/coze`、`ai/trae`、`document/myst`、`document/jupyter` 的 index.md 已有 toctree 但缺 `log`/`spec` 条目 | 文件阅读 |
| R-9 | 脚本 dry-run：正确排序（CER 子目录前、meta 后、辅助文件最后） | 脚本执行 |
| R-10 | 修复后 dummy 构建 `toc.not_included` 为 0；`build succeeded, 6406 warnings`（其余为 myst.header/topmatter 内容问题） | `.temp/build-dummy.log` |
| R-11 | `.gitignore` 追加 `.temp/` 忽略临时脚本目录 | git diff |
| R-12 | 追加逻辑曾破坏 4 个已有 toctree 文件（游离闭合标记），经 git 恢复后改为在闭合前插入条目的精确追加 | git 恢复记录 |
| R-13 | `scripts/check-toctrees.py` 为既有 CI 门禁（提交 `a4056b8`，接入 `.github/workflows/pages.yml`），但仅含断链 + 全局可达性两类检查，无「目录文件清单一致性」 | 脚本阅读 / git log |
| R-14 | A-2 向 `check-toctrees.py` 新增 `expected_entries`/`_to_docname`/`check_consistency`：对每个含 toctree 的 index.md 比对目录内容清单（子目录 index 与直接 .md 文件） | 脚本 diff |
| R-15 | 一致性检查在真实树运行零缺失条目（867 文件修复后目录清单已一致）；`--self-test` 5 用例全部通过，其中 `consistency` 用例唯一覆盖「文件经其他路径可达但其所在目录 toctree 未收录」的盲区 | 脚本执行 |

## 2. I 洞察（G2 通过：四元组完整）

| # | 现象 | 根因 | 影响 | 建议 |
|---|------|------|------|------|
| I-1 | 96% 的 index.md 缺 `{toctree}` | bundle 生成时未补目录树，结构未统一 | 近 5000 文档游离、构建告警泛滥 | OKF bundle 生成即带目录树，纳入生成规范 |
| I-2 | 已含 toctree 的 4 个父索引缺 `log`/`spec` 条目 | toctree 与文件清单不同步，人工维护易漏 | 顶层元数据文档游离 | toctree 与目录文件清单做一致性校验 |
| I-3 | 两个 bundle 无 index.md，整子树不可达 | 生成时缺顶层索引 | 内容存在但导航不到 | 目录含子目录即强制生成 index.md |
| I-4 | 一次性批量脚本 vs 定向补充：先全量后精确修正 | 全量脚本不处理"无 index 目录"与"已含 toctree 缺条目"两类边界 | 首次运行后需二次定向补漏 | 脚本需覆盖建索引、追加、补充三类场景 |
| I-5 | 追加逻辑破坏已有 toctree（游离 ```） | 字符串拼接未定位闭合标记 | 4 文件格式损坏需回滚 | 追加须先定位 toctree 块闭合位置再插入 |
| I-6 | 验证脚本把文档内 toctree 语法示例当真实引用 | 误判 `---`、`maxdepth: 2` 等为条目 | 误报 12 缺失引用 | 解析须过滤选项行与非 toctree 代码块 |
| I-7 | 断链+可达性门禁存在盲区：文件经其他路径全局可达、但其所在目录 toctree 未收录自身内容 | 门禁只验全局可达，未做单目录清单比对 | 目录 toctree 与磁盘内容静默漂移，新增内容易漏收录 | A-2 并入 `check_consistency` 单目录清单一致性比对（R-13/R-15） |

## 3. E 萃取（G3 通过：模式可迁移）

| 模式 | 类型 | 核心思路 | 反模式 |
|------|------|---------|:--:|
| OKF bundle 目录树完整性修复工作流 | 方法论 | 全量扫描缺索引 → 建索引/追加/补充三类处理 → 精确追加需定位闭合 → git 兜底回滚 | 盲目拼接、一次性脚本不覆盖边界 |
| toctree 动态验证法 | 方法论 | 自 `.temp/verify_toctrees.py` BFS 可达性演进为 CI 门禁 `scripts/check-toctrees.py`（断链 + 可达性 + A-2 目录文件清单一致性），过滤 toctree 选项行与语法示例 | 把示例代码块当真实引用导致误报；只验全局可达漏判单目录缺失条目 |

两个模式跨 Sphinx/知识库文档工程可复用，前期论证充分后可通过 pattern-extraction-cmd 入库。

## 4. C 原子提交（G4 通过：单一职责、可独立验证、已落盘）

变更已实际落盘并经 git 核对，按单一职责拆分为 2 个原子提交：

1. `fix(docs): 补齐 toctree 消除 toc.not_included 警告`（`e661cd1`）
   - 文件：867 文件（859 个 index.md 修改 + `ai/trae/spec`、`document/jupyter/extension-examples`、`document/jupyter/jupyter-client` 3 个新建 index.md；`extension-examples/README.md`、`jupyter-client/README.md` 合并重命名为 index.md）
   - 验证：dummy 构建 `toc.not_included` 0
2. `chore: 忽略 .temp 临时脚本目录`（`afc989b`）
   - 文件：`.gitignore`，追加 `.temp/`
   - 验证：`.temp/` 不再纳入版本控制

## 5. 关键改进行动项

| # | 行动项 | 优先级 | 状态 | 验收标准 |
|---|--------|:--:|:--:|----------|
| A-1 | OKF bundle 生成规范纳入"必须生成 index.md 并带 toctree"约束 | 高 | 🔲 待推进 | bundle 目录扫描零缺失 index.md |
| A-2 | 新增 toctree 与目录文件清单一致性校验脚本 | 中 | ✅ 已完成（2026-08-24） | 已有 toctree 文件无缺失条目告警——`check_consistency` 并入 `check-toctrees.py`，真实树零缺失条目、自检 5 用例通过 |
| A-3 | 将目录树完整性修复工作流沉淀为可复用模式 | 中 | 🔲 待推进 | pattern 入库并登记索引 |
| A-4 | 修复剩余 6406 个非 TOC 警告（myst.header / myst.topmatter） | 低 | 🔲 待推进 | 内容格式警告分类归零 |

## 6. 数据验证

- 修改文件数与 git `867 files changed, 9209 insertions` 一致（R-2/R-10 三查通过）
- 警告数 4888 → 0 与 dummy 构建日志 `.temp/build-dummy.log` 一致
- A-2 一致性检查：`python scripts/check-toctrees.py` 在真实树零缺失条目；`--self-test` 5 用例通过（R-15 三查通过）
- 报告引用路径均为相对路径，无 `file:///` 绝对路径