---
okf_version: "0.2"
type: retrospective
title: "xuanspace 许可口径统一与双仓交付里程碑复盘（A1 落地 + 合并并发防护）"
description: "2026-10-23 xuanspace 第一方许可口径统一为 Apache-2.0 的子模块交付，与父仓 11 条上游提交的合并推送。含 31 条客观事实、4 条四元组洞察、2 个 L1 可迁移模式、V 四视角 6 条意见（采纳 4 条、部分采纳 1 条、不采纳 1 条）、4 项原子行动项与质量门记录。"
tags: ["retrospective", "milestone", "xuanspace", "license", "shared-worktree", "七概念"]
generated: { by: "seven-concepts-cmd", at: "2026-10-24T10:52:00+08:00" }
session: "sc-20261024-xuanspace-license-dual-repo"
source:
  - id: submodule-commit
    resource: "子模块提交 185c3e0（fix(license): 统一第一方发行版许可口径为 Apache-2.0）"
    title: "8 文件 +20/−10 的许可声明切换"
  - id: parent-merge
    resource: "父仓合并提交 5b59be9c2（Merge remote-tracking branch origin main）"
    title: "11 条上游提交 / 116 路径合并与推送"
  - id: memory-rule
    resource: "会话记忆 specweave-shared-worktree-commits"
    title: "并发提交者下的合并前三取证规则"
status: active
stale_after: "2027-04-24"
---

# xuanspace 许可口径统一与双仓交付里程碑复盘

> **复盘对象**：2026-10-23 `projects/xuanspace` A1（许可口径）落地 + 父仓合并推送
> **复盘日期**：2026-10-24（事实基线锁定于 10:52）
> **链路**：七概念场景 1 里程碑复盘 R→I→E→V→A→C（depth=standard，F 不适用故裁剪；本轮无新增提交，C 段只登记待执行项）
> **对外可见载体**：README 声明文本、各包 `pyproject.toml` 的 license 字段与 classifiers、根 `LICENSE`
> **质量门**：31 事实（G1）、4 条四元组洞察（G2）、2 个 L1 模式（G3）、V 四视角 6 条意见采纳 4 条（V 门）、4 项原子行动项（G4）

***

## 一、时间线

| 时间（+0800） | 事件 | 证据 |
|---|---|---|
| 2026-10-19 13:01-13:31 | 子模块前四提交（pdm 依赖、CI venv、xs 自覆盖） | `git log` 7e5d251 及之前 |
| 2026-10-23 15:26:51 | 子模块 `185c3e0` 提交，许可口径统一为 Apache-2.0 | F-002 / F-003 |
| 2026-10-23 15:49:44 | 父仓合并提交 `5b59be9c2`，并入 11 条上游提交 | F-017 |
| 2026-10-23 15:49 之后 | 子模块与父仓分别推送至远端 `main` | F-019 / F-020 |
| 2026-10-24 10:52 | 复盘基线取证：父仓 HEAD `919754b30`，相对远端 `2 0` | F-021 |

***

## 二、事实清单（R）

> 口径：全部为命令直读结果，不含因果推断；编号 F-001 起，正文与索引行计数一致（共 31 条）。

| 编号 | 事实 |
|---|---|
| F-001 | 父仓以 gitlink 记录 `projects/xuanspace`，当前指向 `185c3e04bbc4cb23e696351fd18cd015078b5e82`。 |
| F-002 | 子模块提交 `185c3e0` 的 subject 为 `fix(license): 统一第一方发行版许可口径为 Apache-2.0`，作者 `Trae Agent <xin@trae.dev>`，提交时间 `2026-10-23 15:26:51 +0800`。 |
| F-003 | `185c3e0` 的父提交为 `7e5d251`，diffstat 为 8 files changed, 20 insertions(+), 10 deletions(-)。 |
| F-004 | `185c3e0` 改动路径 8 条：`README.md`、`tools/xs/README.md`、`tools/xs/pyproject.toml`、`tools/okf/pyproject.toml`、`libs/xuan-core/pyproject.toml`、`libs/xuan-ext-demo/pyproject.toml`、`tools/templates/python/pyproject.toml`、`tools/templates/native/pyproject.toml`。 |
| F-005 | 子模块内第一方 `pyproject.toml` 共 14 个（排除 `vendor/`、`.test-venv/`、`.git/`）。 |
| F-006 | 14 个 `pyproject.toml` 的 license 行分布：`"Apache-2.0"` 6 个、`{ file = "LICENSE" }` 7 个、`"GPL-2.0-only"` 1 个。 |
| F-007 | 14 个 `pyproject.toml` 中 `\bMIT\b` 匹配 0 处。 |
| F-008 | 14 个 `pyproject.toml` 中 `license = {text` 匹配 0 处。 |
| F-009 | 子模块根 `LICENSE` 首两行为 `Apache License` 与 `Version 2.0, January 2004`。 |
| F-010 | `libs/xuan-core/pyproject.toml` 与 `tools/xs/pyproject.toml` 各含 1 条 `License ::` classifier。 |
| F-011 | 子模块 `git rev-list --left-right --count HEAD...origin/main` 输出 `0 0`；工作区 `git status --porcelain` 输出 0 行。 |
| F-012 | 子模块 `origin/main` 指向 `185c3e0`。 |
| F-013 | 父仓合并前 `git rev-list --left-right --count HEAD...origin/main` 输出 `36 11`（ahead 36、behind 11）。 |
| F-014 | 上游 11 条提交涉及 116 个变更路径。 |
| F-015 | 116 个上游变更路径与本地 dirty/untracked 路径集合的交集为 0 条。 |
| F-016 | `git merge-tree --write-tree HEAD origin/main` 退出码为 0。 |
| F-017 | 合并提交为 `5b59be9c269268ace2028e8a96ffb4db9650cb8f`，父提交 `9d8667139` 与 `04f1440ec`，提交时间 `2026-10-23 15:49:44 +0800`，subject 为 `Merge remote-tracking branch 'origin/main'`。 |
| F-018 | 合并提交相对第一父 `9d8667139` 的 diff 含 116 个路径，其中 `vendor/` 下 9 条 gitlink 记录。 |
| F-019 | 推送区间为 `04f1440ec..5b59be9c2`，目标为 `gitcode.com:daoCollective/SpecWeave.git` 的 `main`。 |
| F-020 | 推送完成后父仓 `HEAD...origin/main` 输出 `0 0`，子模块输出 `0 0`。 |
| F-021 | 复盘基线时父仓 HEAD 为 `919754b30`，`HEAD...origin/main` 输出 `2 0`，`5b59be9c2..HEAD` 之间 12 条提交。 |
| F-022 | 合并前仓库存在 0 字节 `index.lock`，mtime 为 `2026-10-20 18:38`；处置动作为改名保留。 |
| F-023 | 首次合并命令 `git merge --no-rebase --no-edit origin/main` 输出 git 用法提示，未生成提交。 |
| F-024 | 第二次命令 `GIT_EDITOR=true git merge --no-edit origin/main` 退出码 0，生成 `5b59be9c2`。 |
| F-025 | `git submodule status` 输出 21 行，首列全为空格；`git status --porcelain` 中 ` M vendor/` 前缀行 0 条。 |
| F-026 | `projects/xuanspace/.github/workflows/ci.yml` 第 149–152 行为 `# --- 链接检查 ---`、`- name: Check documentation links`、`run: xs docs linkcheck`、`continue-on-error: true`。 |
| F-027 | `tools/xs/src/xs/commands/docs_cmd.py` 第 126–127 行定义 `docs_linkcheck()`，函数体为 `docs_build(builder="linkcheck")`；`output_dir` 参数定义在第 31 行，位于 `docs_build` 签名内。 |
| F-028 | 会话记忆 `specweave-shared-worktree-commits.md` 本轮新增两条规则：合并/推送前重取 divergence 与脏集合；以过期分叉数为前提的授权视为过期。 |
| F-029 | 本报告落盘前，`docs/retrospective/reports/concepts/milestone/` 含 46 个报告文件（不含 `index.md`）、索引表 41 行、toctree 43 条有效条目（另有 `:maxdepth: 2` 选项行）。 |
| F-030 | 同目录 4 个报告文件不在 toctree 中：`retrospective-jpman-client-stability-milestone-20260910`、`retrospective-jpman-nested-podman-newuidmap-milestone-20260912`、`specweave-project-review-20261013`、`wsl-drvfs-mount-wiki-milestone-20261013`。 |
| F-031 | 同目录 2026-10-23 两份里程碑报告的前置元数据使用 `okf_version: "0.2"`、`type: retrospective`、`generated`、`stale_after` 字段。 |

**G1 检查**：事实 31 条（≥20）；无因果/判断词；关键数字（提交号、路径数、计数）均带命令来源；正文、frontmatter `description` 与索引行三处计数逐词一致（31/4/2/4）。

***

## 三、洞察（I）

### I-1 许可声明是分布式真值，不是单文件

- **陈述**：许可切换的作用对象是全仓所有声明载体，根 `LICENSE` 只是其中一个副本；生成模板属于载体之一。
- **证据**：F-002（提交信息点名模板属再生产源）、F-004（8 条改动路径含 2 个模板）、F-006（14 个 pyproject 各自声明）、F-007（复扫后 MIT 归零）。
- **反常识**：默认「根 LICENSE 改了就等于许可改了」。实际有 14 个 `pyproject.toml` 独立声明许可，其中 2 个是脚手架模板——只改实例的切换会在下一次生成时失效。
- **行动**：许可类变更先做载体枚举（实例 / 模板 / README / classifier / LICENSE 本体），再一次性替换；模板与实例同批提交。

### I-2 语义统一与形态统一是两个独立验收维度

- **陈述**：本轮统一使许可语义一致（MIT 匹配 0），但元数据形态仍分三种：6 个 SPDX 字符串、7 个 `{ file = "LICENSE" }` 表形态、1 个 GPL SPDX 字符串。
- **证据**：F-005、F-006、F-008。
- **反常识**：默认「没有 MIT 就算完成」。语义与形态可以同时存在：`{ file = ... }` 表达的是文件引用，不提供 SPDX 标识符，下游 SBOM/包索引的可读性弱于 `license = "Apache-2.0"`。
- **行动**：把 7 个 `{ file = ... }` 收敛为 SPDX 字符串 + `license-files`，作为独立原子提交，不与语义切换混批。

### I-3 共享工作树里的合并授权有保鲜期

- **陈述**：「合并 + 推送」的批准对象是执行时刻的分叉快照，不是整会话的无限期授权。
- **证据**：F-013（合并前 36/11）、F-020（推送后 0/0）、F-021（复盘时 2/0、合并后新增 12 条提交）、F-028（记忆规则新增）。
- **反常识**：默认一次批准覆盖后续所有合并。并发提交者存在时，上游提交数、HEAD 位置、脏文件集合都在动；按旧快照执行时，实际并入的范围已不是用户批准的那个范围。
- **行动**：任何 merge/push 前重跑三取证（分叉计数、上游路径∩脏集合、`merge-tree`），把相对上次授权的 delta 报给用户后再执行。

### I-4 门禁的「存在」与「生效」是两个变量

- **陈述**：CI 中存在 `xs docs linkcheck` 步骤，`continue-on-error: true` 使该步骤失败不改变作业结论。
- **证据**：F-026（第 148–152 行原文）。
- **反常识**：默认「流水线里有这一步就等于有这道门」。`continue-on-error: true` 把失败降级为日志，作业仍绿。
- **行动**：先跑一次全量 linkcheck 取断链基线，再移除 `continue-on-error: true`，让失败进入阻断通道。

***

## 四、萃取（E）

### PATTERN-1 许可口径四面清算

| 项 | 内容 |
|---|---|
| **适用** | 多包 monorepo、含脚手架/模板生成器的仓库，需要切换许可或发现对外声明分裂 |
| **不适用** | 单一 `pyproject.toml` 且无模板的小仓库（一个文件即可完成） |
| **核心步骤** | 1. 载体枚举：`rg -n 'license\s*=\|License ::\|MIT\|Apache' --glob '!vendor/**'`<br>2. 分级：实例声明 / 生成模板 / 文档文本 / 源码头 / LICENSE 本体<br>3. 定单一真值：SPDX 表达式 + 根 LICENSE 文件<br>4. 模板与实例同批改，提交信息写明「模板属再生产源」<br>5. 经批准的例外（如 GPL 对等基线）保留并在提交信息注明<br>6. 全仓复扫：`\bMIT\b`、`license = {text`、classifier 计数<br>7. 记录分布快照（SPDX / file / 例外各几），作为下一轮基线 |
| **反模式** | ① 只改根 LICENSE，pyproject / README / 模板不动<br>② 只改实例不改模板，下一次脚手架生成回滚<br>③ 语义切换与形态收敛混成一个提交，无法独立回滚<br>④ 静默覆盖有意例外，把 GPL 对等基线改成 Apache |
| **检验标准** | 全部第一方 pyproject 的许可语义为目标值；`\bMIT\b` 匹配 0；模板与实例形态一致；例外项在提交信息有说明；分布快照已记录 |
| **跨域迁移** | ICU 语言资源包的 locale 声明（实例 + 模板 + 文档）、Dockerfile base image tag、CI runner 版本声明——同为「实例 + 模板 + 文档」多副本结构 |
| **成熟度** | L1（单案例，待第二次独立许可切换验证） |

### PATTERN-2 合并前三分叉取证

| 项 | 内容 |
|---|---|
| **适用** | 共享工作树 + 存在其他提交者 + 需要 merge/push |
| **不适用** | 独占克隆、无并发写入、纯本地快进 |
| **核心步骤** | 1. `git rev-list --left-right --count HEAD...origin/main` 取分叉快照（带时间戳）<br>2. `git status --porcelain` 取脏集合，与上游变更路径求交集，非空即停<br>3. `git merge-tree --write-tree HEAD origin/main`，退出码非 0 即停<br>4. 检查 `index.lock` 的存在与 mtime，异常锁先取证再处理<br>5. 推送后重取 divergence 与「合并点到 HEAD」提交数，把他人新增提交单独报出 |
| **反模式** | ① 用 `git pull` 参数 `--no-rebase` 做 merge，误判合并完成<br>② 直接删除异常 `index.lock` 而不取证<br>③ 把一次授权当成整会话授权，不重取快照<br>④ 合并后不重扫 divergence，把他人新提交算进本次交付 |
| **检验标准** | 三项取证输出可复跑；merge 退出码 0；推送区间唯一定位；推送后 divergence 与预期一致；他人提交已单独列出 |
| **跨域迁移** | 多人共享数据库 schema 迁移分支、共享 K8s 集群的配置合并、共享文档的版本合并——都需「先取快照、再看交集、最后执行」 |
| **成熟度** | L1（单案例；已有会话记忆规则佐证，但未在第二个仓库验证） |

***

## 五、V 对抗审查（四视角）

| 编号 | 视角 | 意见 | 处置 |
|---|---|---|---|
| V-1 | 魔鬼代言人 | I-2 把 `{ file = "LICENSE" }` 标为「债」是价值判断；报告未核验 PEP 原文，不应断言该形态「弃用/非法」 | **采纳**：I-2 陈述与行动改为「形态收敛」；F-008 只保留可实测的 `{text` 归零，不引用未核验的规范结论 |
| V-2 | 新人 | 事实清单给了结论数字，但没给复跑命令，新人无法自行验证 | **采纳**：新增「六、复现命令」章节 |
| V-3 | 老板 | 许可统一的可感知收益未说明 | **采纳**：概览补「对外可见载体」一行；不编造量化收益 |
| V-4 | 未来 | 模板已改，但无守卫；未来新增模板仍可能写回 MIT | **采纳**：ACT-003 增加 TOML 解析守卫测试 |
| V-5 | 魔鬼代言人 | 索引漂移（46 文件 / 41 表行 / 43 toctree）与本次里程碑无关，写进报告会扩大范围 | **部分采纳**：仅登记为 F-029/F-030 与 ACT-004，本轮不批量修复 |
| V-6 | 未来 | 合并后 12 条他人提交是否应纳入复盘 | **不采纳**：仅作并发事实登记（F-021），不评价内容 |

**V 门检查**：4 个视角全覆盖；意见 6 条（≥5），采纳 4 条（≥2）、部分采纳 1 条、不采纳 1 条；每条含具体攻击点与处置。

***

## 六、复现命令

```bash
# 子模块许可分布（14 个第一方 pyproject）
cd projects/xuanspace
find . -name pyproject.toml -not -path './vendor/*' -not -path './.test-venv/*' -not -path './.git/*' \
  | xargs grep -n '^license'
grep -rIn --include=pyproject.toml -E '\bMIT\b' . --exclude-dir=vendor --exclude-dir=.test-venv --exclude-dir=.git | wc -l

# 子模块与父仓分叉
git rev-list --left-right --count HEAD...origin/main
cd ../.. && git rev-list --left-right --count HEAD...origin/main

# 合并事实
git log -1 --format='%H%n%p%n%ci%n%s' 5b59be9c2
git diff --name-only 9d8667139 5b59be9c2 | wc -l
git diff --name-only 9d8667139 5b59be9c2 | grep -c '^vendor/'

# 链接门现状
sed -n '149,152p' projects/xuanspace/.github/workflows/ci.yml

# 索引漂移
cd docs/retrospective/reports/concepts/milestone
ls *.md | grep -v '^index.md$' | wc -l
awk '/^```\{toctree\}/{f=1;next} /^```$/{f=0} f&&NF{print}' index.md | grep -v '^:maxdepth' | wc -l
```

***

## 七、行动项（A / G4）

| 编号 | 动作 | 单一职责 | 验收标准 | Owner | 截止 |
|---|---|---|---|---|---|
| ACT-001 | 删除 `projects/xuanspace/.github/workflows/ci.yml:152` 的 `continue-on-error: true`（先跑一次 linkcheck 取基线） | 只改该步骤的门禁语义 | `grep -c 'continue-on-error: true'` = 0；一次 CI 运行的 linkcheck 步骤状态反映真实结果 | xuanspace 维护者 | 2026-10-31 |
| ACT-002 | 7 个 `{ file = "LICENSE" }` 收敛为 `license = "Apache-2.0"` + `license-files = ["LICENSE"]`（GPL 包保持原状） | 只做形态收敛，不动许可语义 | 第一方 pyproject 中 SPDX 字符串 13 个、GPL 1 个、`license = { file` 0 个 | xuanspace 维护者 | 2026-11-07 |
| ACT-003 | 新增 `tests/test_license_metadata.py`：解析 TOML 断言 license 为 SPDX 字符串；模板目录不得出现 `MIT` 与 `{text` | 只加守卫测试，不改现有元数据 | 注入 `license = "MIT"` 后测试失败；恢复后通过 | xuanspace 维护者 | 2026-11-07 |
| ACT-004 | 对账 `docs/retrospective/reports/concepts/milestone/index.md`：4 个未挂载报告补入 toctree，表格行数与文件数对齐 | 只做索引对账 | 文件数、表格行数、toctree 有效条目数三者一致，或有显式豁免登记 | docs 维护者 | 2026-10-31 |

**G4 检查**：4 项（3–5 区间）；每项单一职责、可独立交付、有验收标准、有 Owner、有截止日期；均可独立回滚。

***

## 八、质量门记录

| 门 | 检查项 | 结果 |
|---|---|---|
| G1 | 事实 ≥20、无因果词、关键数字可追溯、跨文档口径一致 | ✅ 31 条，正文/description/索引行计数一致 |
| G2 | ≥3 条洞察，四元组完整（陈述/证据/反常识/行动） | ✅ 4 条，均引用 F 编号 |
| G3 | 模式命名 4–8 字、触发+边界、3–7 步、≥3 反模式、检验标准、跨域迁移、成熟度 | ✅ 2 个，均 L1，各 4 条反模式 |
| V | 4 视角、≥5 意见、≥2 采纳 | ✅ 6 条，采纳 4、部分采纳 1、不采纳 1 |
| G4 | 行动项单一职责、可独立验证、有 Owner 与时间 | ✅ 4 项 |

***

## 九、遗留与边界

- 本轮只产出报告与索引登记，未提交仓库变更（C 段待用户确认后执行）。
- 父仓当前 `2 0` 的 2 条未推送提交属其他提交者，未纳入本报告评价范围（V-6）。
- A2 的另一处断言「`docs_cmd.py:128` 的 `output_dir` 落到 `OptionInfo`」在本轮未复现：第 31 行签名内 `output_dir` 由 `typer.Option` 正常声明，第 126–127 行 `docs_linkcheck()` 只调用 `docs_build(builder="linkcheck")`。该断言未列入本轮 4 项行动项，作为遗留项单独复核；本报告不将其记为缺陷。
