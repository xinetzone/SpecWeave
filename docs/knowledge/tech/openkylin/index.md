---
okf_version: "0.2"
type: index
id: "openkylin-index"
title: "openKylin 知识枢纽：官方文档导读、发行版对比与工程沉淀"
category: "tech"
tags: [openkylin, linux-distro, index]
date: "2026-10-22"
status: "stable"
author: "SpecWeave Agent（方法论编排 session sc-20261022-openkylin-docs-unify）"
summary: "openKylin 相关文档在 SpecWeave 文档中心的统一入口：知识包就地集中为 docs-wiki（官方文档平台逆向导读，20 篇）与 openeuler-comparison（openEuler 与 openKylin 系统性对比，9 篇）两个子包，okw 工具包指南以指针页并列（1 篇）；复盘报告（15 篇）与模式库案例（13 篇）按 docs 分区规范保留原位，由本页建立跨区索引聚合。"
security_level: "public"
knowledge_type: "conditional"
validation_status: "verified"
stale_after: "2026-12-31"
generated:
  by: agent-trae
  at: "2026-10-22T23:30:00+08:00"
---

# openKylin 知识枢纽

> 一句话：**知识包就地集中**在本目录，**复盘与模式**按 `docs/` 分区规范保留原位并在此聚合索引——单点进入，全域可达。

本枢纽是 openKylin 相关文档在 SpecWeave 文档中心的**统一入口**。2026-10-22 归并前，相关文档分散在 `knowledge/tech/`（两个并列知识包）与 `tech/guides/`（okw 指针页）三处；归并后知识包集中于本目录，复盘报告与模式库案例因 `docs/knowledge/` 与 `docs/retrospective/` 的分区规范保留原位，由本页建立跨区索引。

```{toctree}
:hidden:
:maxdepth: 2

docs-wiki/index
openeuler-comparison/index
references/wsl-devkit-guide
```

## 一、知识包（30 篇 · 就地集中）

| 知识包 | 类型 | 时间 | 状态 | 摘要 |
|--------|------|------|------|------|
| [openKylin 官方文档平台学习教程（OKF Wiki）](docs-wiki/index.md) | 知识包 · 20 篇 | 2026-09-29（末次更新 2026-10-14） | verified | 递归解析 docs.openkylin.top 的 Gitee 源仓库 3181 条目 / 237 篇中文文档，精读 35 篇、提取 44 条事实，按学习者问题域重组为 7 张知识地图 |
| [openEuler 与 openKylin 系统性对比](openeuler-comparison/index.md) | 知识包 · 9 篇 | 2026-09-30 | verified | 新采集 openEuler 侧 35 条事实（O-001~O-035），以 12 条锚点引用 openKylin 侧 62 条事实，拆为画像、场景、治理、生命周期、技术栈、选型 6 个概念页 |
| [openKylin WSL 开发工具包（okw）指南入口](references/wsl-devkit-guide.md) | 指针页 · 1 篇 | 2026-10-22 | verified | okw CLI 的 8 篇原子页导航入口：WSL 发行版管理、openKylin 环境验收、deb/dput 脚手架、rootless Podman 操作 |

### docs-wiki · 官方文档平台逆向导读（20 篇）

- **概念页 7 篇**：[01 平台与源仓库地图](docs-wiki/concepts/01-platform-and-repository.md) · [02 版本发布与生命周期](docs-wiki/concepts/02-release-lifecycle.md) · [03 安装路径全景与选型](docs-wiki/concepts/03-install-paths.md) · [04 桌面环境与基础使用](docs-wiki/concepts/04-desktop-usage.md) · [05 AI 三层体系](docs-wiki/concepts/05-ai-stack.md) · [06 开发者基础设施](docs-wiki/concepts/06-developer-infrastructure.md) · [07 社区治理与贡献路径](docs-wiki/concepts/07-community-and-contribution.md) · [概念页索引](docs-wiki/concepts/index.md)
- **参考页 11 篇**：[全面调研：从桌面根社区到 Agent OS](docs-wiki/references/project-overview.md) · [AI SDK OCR 落机 POC](docs-wiki/references/ai-sdk-ocr-poc.md) · [AI 子系统源码架构剖析](docs-wiki/references/ai-subsystem-source-architecture.md) · [kylin-wayland-compositor 显示栈剖析](docs-wiki/references/kylin-wayland-compositor-architecture.md) · [openKylin 3.0 架构适配评估草案](docs-wiki/references/openkylin-v3-adaptation-assessment.md) · [WSL 安装与稀疏 VHD 实操指南](docs-wiki/references/wsl-install-sparse-vhd-guide.md) · [双 WSL 镜像对照与选型](docs-wiki/references/wsl-dual-image-selection.md) · [Desktop WSL 桌面启动教程](docs-wiki/references/wsl-desktop-startup-tutorial.md) · [完整文档分类地图](docs-wiki/references/full-catalog.md) · [信源台账](docs-wiki/references/source-inventory.md) · [V 对抗审查记录](docs-wiki/references/adversarial-review.md)

### openeuler-comparison · 发行版系统性对比（9 篇）

- **概念页 6 篇**：[00 画像总览](openeuler-comparison/concepts/00-overview.md) · [01 定位与场景](openeuler-comparison/concepts/01-positioning-and-scenarios.md) · [02 治理与生态](openeuler-comparison/concepts/02-governance-and-ecosystem.md) · [03 版本生命周期](openeuler-comparison/concepts/03-release-lifecycle.md) · [04 技术栈](openeuler-comparison/concepts/04-technology-stack.md) · [05 选型指南](openeuler-comparison/concepts/05-selection-guide.md)
- **参考页 2 篇**：[信源台账](openeuler-comparison/references/source-inventory.md) · [V 对抗审查记录](openeuler-comparison/references/adversarial-review.md)

## 二、复盘报告（15 篇 · 保留原位，跨区聚合）

复盘区是 `docs/retrospective/` 独立分区，按文档中心分区规范不得与 `docs/knowledge/` 物理混居，故**保留原位**，由本页建立索引。

| 复盘主题 | 类型 | 时间 | 入口 |
|---------|------|------|------|
| openKylin WSL 导出转 podman 镜像转换 | 构建工程 | 2026-10-09 | [索引](../../../retrospective/reports/build-engineering/retrospective-openkylin-wsl-to-podman-20261009/index.md) · [复盘报告](../../../retrospective/reports/build-engineering/retrospective-openkylin-wsl-to-podman-20261009/README.md) |
| openKylin 全面评估调研 | 竞品分析 | 2026-10-14 | [索引](../../../retrospective/reports/competitive-analysis/retrospective-openkylin-evaluation-20261014/index.md) · [调研报告](../../../retrospective/reports/competitive-analysis/retrospective-openkylin-evaluation-20261014/README.md) · [技术选型事实清单](../../../retrospective/reports/competitive-analysis/retrospective-openkylin-evaluation-20261014/facts-technical-comparison.md) · [生态商业事实清单](../../../retrospective/reports/competitive-analysis/retrospective-openkylin-evaluation-20261014/facts-ecosystem-business.md) · [Q-1~Q-8 首轮核验记录](../../../retrospective/reports/competitive-analysis/retrospective-openkylin-evaluation-20261014/verification-q1-q8-20261014.md) |
| openKylin 评估与 Q 门双轮核验 | 项目报告 | 2026-10-14 | [索引](../../../retrospective/reports/project-reports/retrospective-openkylin-evaluation-qgate-20261014/index.md) · [里程碑复盘](../../../retrospective/reports/project-reports/retrospective-openkylin-evaluation-qgate-20261014/README.md) · [洞察萃取](../../../retrospective/reports/project-reports/retrospective-openkylin-evaluation-qgate-20261014/insight-extraction.md) · [原子行动项](../../../retrospective/reports/project-reports/retrospective-openkylin-evaluation-qgate-20261014/actionable-items.md) |
| openKylin 3.0 WSL 导入排障与稀疏 VHD 启用 | 任务报告 | 2026-09-29 | [索引](../../../retrospective/reports/task-reports/retrospective-openkylin-wsl-install-sparse-20260929/index.md) · [复盘报告](../../../retrospective/reports/task-reports/retrospective-openkylin-wsl-install-sparse-20260929/retrospective-report.md) |
| apps/containers 四成员 openKylin-3.0 WSL pytest 验证 | 任务报告 | 2026-10-19 | [问题解决报告](../../../retrospective/reports/task-reports/retrospective-containers-openkylin-wsl-pytest-20261019.md) |
| .temp/openkylin-wsl-pytest 产物目录存续价值复盘 | 任务报告 | 2026-10-20 | [复盘与保守档简化](../../../retrospective/reports/task-reports/retrospective-containers-openkylin-wsl-pytest-artifact-20261020.md) |

## 三、模式库案例（13 篇 · 保留原位，跨区聚合）

模式库中的这些条目**以 openKylin 为案例信源**，模式本体可跨场景迁移，故保留在 `docs/retrospective/patterns/`。

| 模式 | 分区 | 来源案例 |
|------|------|---------|
| [逆序文档学习法](../../../retrospective/patterns/methodology-patterns/research-knowledge/reverse-order-doc-learning.md) | 研究知识 | docs-wiki（官方文档平台逆向导读） |
| [场景区间选型法](../../../retrospective/patterns/methodology-patterns/governance-strategy/scenario-interval-selection.md) | 治理策略 | openeuler-comparison（发行版对比） |
| [社区指标三查法](../../../retrospective/patterns/methodology-patterns/governance-strategy/community-metric-triple-check.md) | 治理策略 | 全面评估调研 |
| [根社区—商业发行版双轮](../../../retrospective/patterns/methodology-patterns/product-growth/root-community-commercial-distro-flywheel.md) | 产品增长 | 全面调研（桌面根社区 → Agent OS） |
| [终端操作系统智能体原生化四级演进](../../../retrospective/patterns/methodology-patterns/product-growth/agent-native-os-capability-ladder.md) | 产品增长 | 全面调研（同上） |
| [大归档零下载远程预检法](../../../retrospective/patterns/code-patterns/large-archive-remote-preflight.md) | 代码模式 | Desktop WSL 双镜像选型 |
| [WSL 导入内存分诊与稀疏 VHD 决策模式](../../../retrospective/patterns/code-patterns/wsl-import-memory-triage-sparse-vhd.md) | 代码模式 | WSL 安装排障 |
| [WSL 发行版镜像化导出模式](../../../retrospective/patterns/code-patterns/wsl-rootfs-oci-image-export.md) | 代码模式 | WSL → podman 镜像转换 |
| [开发容器镜像构建纪律模式](../../../retrospective/patterns/code-patterns/dev-container-image-construction-discipline.md) | 代码模式 | openKylin dev container |
| [xrdp 黑屏三层分诊法](../../../retrospective/patterns/code-patterns/xrdp-black-screen-window-manager-triage.md) | 代码模式 | Desktop WSL 桌面启动 |
| [同源产物形态坍缩法](../../../retrospective/patterns/methodology-patterns/governance-strategy/artifact-form-collapse.md) | 治理策略 | 产物目录存续价值复盘 |
| [缺口双轮核验法](../../../retrospective/patterns/methodology-patterns/research-knowledge/gap-two-round-verification.md) | 研究知识 | Q 门双轮核验 |
| [WSL 网络共享 drvfs 挂载三段验证与幂等持久化法](../../../retrospective/patterns/methodology-patterns/tools-automation/wsl-network-share-drvfs-mount.md) | 工具自动化 | 挂载通道实践 |

## 四、关联：开源赛事中的 openKylin 孵化仓库

`knowledge/opensource-contest/os2026-shanghai/` 知识包中，openKylin 以社区孵化仓库身份出现，属**赛事视角的旁支内容**，不并入本枢纽，仅在此登记：

- [05 赛题深度下钻：openKylin 社区孵化仓库 openkylin-wsl](../../opensource-contest/os2026-shanghai/concepts/05-challenge-briefs-deep-dive.md)（该包另有 [总览](../../opensource-contest/os2026-shanghai/index.md) · [赛道与命题](../../opensource-contest/os2026-shanghai/concepts/01-tracks-and-challenges.md) · [参赛指南](../../opensource-contest/os2026-shanghai/concepts/03-participation-guide.md) · [方案介绍](../../opensource-contest/os2026-shanghai/concepts/00-contest-overview.md) 等 7 篇顺带提及）

## 五、阅读路径建议

| 诉求 | 建议入口 |
|------|---------|
| 「openKylin 是什么、靠不靠谱」 | [全面调研：从桌面根社区到 Agent OS](docs-wiki/references/project-overview.md) → [openEuler 对比](openeuler-comparison/index.md) |
| 「官方文档怎么读、怎么参与贡献」 | [docs-wiki 教程](docs-wiki/index.md) → [社区治理与贡献路径](docs-wiki/concepts/07-community-and-contribution.md) |
| 「怎么在 Windows 上装 openKylin」 | [WSL 安装与稀疏 VHD 实操指南](docs-wiki/references/wsl-install-sparse-vhd-guide.md) → [双镜像选型](docs-wiki/references/wsl-dual-image-selection.md) |
| 「桌面怎么用、界面问题怎么查」 | [Desktop WSL 桌面启动教程](docs-wiki/references/wsl-desktop-startup-tutorial.md) → [xrdp 黑屏三层分诊法](../../../retrospective/patterns/code-patterns/xrdp-black-screen-window-manager-triage.md) |
| 「AI SDK 能不能落地用」 | [AI 三层体系](docs-wiki/concepts/05-ai-stack.md) → [OCR 落机 POC](docs-wiki/references/ai-sdk-ocr-poc.md) → [AI 子系统源码架构](docs-wiki/references/ai-subsystem-source-architecture.md) |
| 「okw 工具怎么用」 | [okw 指南入口](references/wsl-devkit-guide.md) |
| 「这些结论是怎么得出来的、踩过哪些坑」 | 本页「复盘报告」与「模式库案例」两节 |

## 六、归并记录（2026-10-22）

| 旧路径 | 新路径 | 处置 |
|--------|--------|------|
| `docs/knowledge/tech/openkylin-docs-wiki/` | `docs/knowledge/tech/openkylin/docs-wiki/` | 目录整体迁入本枢纽 |
| `docs/knowledge/tech/openeuler-vs-openkylin/` | `docs/knowledge/tech/openkylin/openeuler-comparison/` | 目录整体迁入本枢纽 |
| `docs/tech/guides/openkylin-wsl-devkit/index.md` | `docs/knowledge/tech/openkylin/references/wsl-devkit-guide.md` | 指针页迁入本枢纽；`docs/tech/guides/index.md` 保留为指向本枢纽的指引页 |

**处置边界**：

- `docs/knowledge/` 与 `docs/retrospective/` 是文档中心明确定义的独立分区，复盘报告与模式库案例**不物理迁入**本目录，仅由本页索引聚合；
- 知识包内部结构（`index.md` + `concepts/` + `references/`）保持不变，迁移只改变目录层级，条目级链接按相对路径重算；
- 分类/标签分片（`categories/tech.md`、`categories/unknown.md`、`tags/14-cjk-3.md`）中的旧路径引用已同步改写。

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261022-openkylin-docs-unify | msg=全面调研 docs 树内 openKylin 文档并集中到统一目录 | ctx={"scenario":"refactor","chain":"I→F→A→V→C","target":"docs/knowledge/tech/openkylin/"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=A2 | event=ATOMIC_MOVE | session=sc-20261022-openkylin-docs-unify | msg=两个知识包与 okw 指针页迁入新枢纽目录 | ctx={"moved_files":30,"from":["knowledge/tech/openkylin-docs-wiki/","knowledge/tech/openeuler-vs-openkylin/","tech/guides/openkylin-wsl-devkit/index.md"],"to":"knowledge/tech/openkylin/"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=A4 | event=REFACTOR_MERGE | session=sc-20261022-openkylin-docs-unify | msg=按相对路径解析式重写受迁移影响的条目链接，并同步分类/标签分片旧路径引用 | ctx={"inbound_links_fixed":80,"index_path_replaced":58}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=A5 | event=TOCTREE_SYNC | session=sc-20261022-openkylin-docs-unify | msg=knowledge/tech/index.md toctree 收敛为 openkylin/index；新建枢纽页登记子包与跨区索引 | ctx={"toctree_entries":1,"hub_created":true}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=A6 | event=TOCTREE_BACKFILL | session=sc-20261022-openkylin-docs-unify | msg=修复迁移引入的指针页孤儿回归与 docs-wiki 继承的 18 篇未登记缺陷 | ctx={"hub_toctree_added":["references/wsl-devkit-guide"],"docs_wiki_toctree_added":18,"orphan_regression_fixed":1,"inherited_orphan_fixed":18}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V | event=VALIDATED | session=sc-20261022-openkylin-docs-unify | msg=迁移后链接与 toctree 可达性复验：迁移未引入任何新断链或新孤儿 | ctx={"link_baseline":"HEAD 全量归档树","link_pre_broken":1594,"link_post_broken":587,"link_new_broken":0,"frontmatter_new_broken":0,"toctree_broken_pre":8,"toctree_broken_post":8,"toctree_new_broken":0,"reachable_pre":3314,"reachable_post":3334,"orphan_pre":777,"orphan_post":758,"orphan_new":0,"bytes_pre":474914,"bytes_post":490565,"bytes_delta":15651,"bytes_ledger_closed":true,"openkylin_scope_reachable":31}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V | event=RESIDUAL_AUDIT | session=sc-20261022-openkylin-docs-unify | msg=全仓旧路径残留审计：18 处命中中 12 处系迁移新产生，逐条语境判定后仅 1 处属现行有效引用并已改写，其余 11 处为历史记录语境按约定保留；另 6 处为迁移前既存悬空债务，不在本次责任范围 | ctx={"scope":"全仓受控文本文件","prefixes":3,"hits_total":18,"migrated_new":12,"rewritten":1,"rewritten_target":"docs/knowledge/tech/openkylin/docs-wiki/references/project-overview.md","history_kept":11,"pre_existing":6,"pre_existing_files":[".trae/specs/infra-env/extend-okw-openkylin-ai/review.md",".trae/specs/infra-env/extend-okw-openkylin-ai/tasks.md",".trae/specs/infra-env/extend-okw-openkylin-desktop/tasks.md",".trae/specs/infra-env/openkylin-dev-container/review.md",".trae/specs/infra-env/openkylin-dev-container/spec.md",".trae/specs/infra-env/openkylin-dev-container/tasks.md"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V | event=GATE_DISATTESTED | session=sc-20261022-openkylin-docs-unify | msg=mermaid 门禁 147 处「新增」违规经归因证伪：19 个命中文件中 18 个在本次两笔提交中内容逐字未变，唯一有变文件变更仅落在路径字符串行、mermaid 行前后逐字相同，且 19 个文件均在基线 revision 0aff6f367 之后已被其他提交修改；判定为基线陈旧导致的既有债务漂移，与本次迁移无关 | ctx={"baseline_rev":"0aff6f367","known":4938,"reported_new":147,"resolved":81,"hit_files":19,"unchanged_files":18,"changed_file":"apps/AGENTS.md","verdict":"pre-existing drift, not introduced by migration"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V | event=BASELINE_FIDELITY | session=sc-20261022-openkylin-docs-unify | msg=mermaid 历史基线随迁移改写的保真度机械验证：29 条真实重命名映射下，迁移前基线施加路径变换后与现态基线的 identity 集合与 count 完全相等，无增无漏 | ctx={"rename_map_entries":29,"transformed_identity":4861,"current_identity":4861,"transformed_count_sum":5019,"current_count_sum":5019,"only_in_transformed":0,"only_in_current":0,"count_mismatch":0,"verdict":"保真"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=A | event=COMMIT_BOUNDARY_REBUILT | session=sc-20261022-openkylin-docs-unify | msg=按「路径改写必须与文件移动同提交」不变量重建提交边界：由原 5 笔重建为 2 笔（A' 结构归并+全部路径改写含 mermaid 基线、B' 索引分片登记与计数同步），消除中间提交态悬空链接；随后将残留审计定位的 1 处现行有效引用改写并入 A' | ctx={"rebuild_rounds":3,"commit_A":"c721bcca2","commit_B":"bb9497f62","commit_A_files":67,"commit_B_files":8,"tree_equivalence":"仅 1 处新改写","dangling_links_per_commit":0}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V | event=HUB_REACHABILITY_VERIFIED | session=sc-20261022-openkylin-docs-unify | msg=枢纽页可达性三核验：枢纽页 75 条本地链接零失效；两个子包 toctree 登记与实际文件数逐一相符（docs-wiki 19/19、openeuler-comparison 8/8）；knowledge 索引分片登记的 openkylin 路径全部可达 | ctx={"hub_local_links":75,"broken":0,"docs_wiki":"19/19","openeuler_comparison":"8/8","shards_registered_reachable":true,"hub_doc_count":31}
[CMD-LOG] | level=WARN | cmd=seven-concepts | step=V | event=PENDING_HUMAN_DECISION | session=sc-20261022-openkylin-docs-unify | msg=Sphinx 渲染验证未执行：默认环境 py314 缺 sphinx/myst-parser/sphinx-book-theme，安装属新增依赖需人类批准；toctree 完整性已由自建校验器覆盖 | ctx={"checked_env":"py314","missing":["sphinx","myst-parser","sphinx-book-theme"],"fallback":"check_toctree.py 无依赖校验器"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261022-openkylin-docs-unify | msg=openKylin 文档集中到统一目录：知识包30篇就地集中，复盘15篇+模式13篇保留原位并跨区索引 | ctx={"gates":["I","F","A","V","C"],"hub":"docs/knowledge/tech/openkylin/index.md"}
```
