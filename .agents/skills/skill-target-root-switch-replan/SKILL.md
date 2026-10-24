---
name: skill-target-root-switch-replan
version: 1.0.0
description: 当用户把已批准的 Skill 方案目标根从 ~/.qoder/skills 改成 .agents/skills 或其他目录时，重新在新根跨根查重、重读该根 frontmatter 与登记约定、核对旧根未被写入，并在新根重跑格式、链接与质量门。用户说「要写入 .agents/skills/」「迁入 .agents/skills」「改到主权区」「目标目录换成」「不要写用户级目录」「方案批了但目录变了」时必须使用此技能；不用于首次跨根分诊（用 skill-recommendation-disk-triage）、已有 Skill 的位置迁移（用 user-skill-sovereign-migration）或从零设计内容（用 skill-creator）。
argument-hint: "<旧根> <新根>"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/skill-target-root-switch-replan/**"
title: "Skill 目标根切换重规划"
source: "会话 767c40d5-6d6c-4bbe-9682-09774c17eaa2；shared-branch-merge-push-gate 方案提出后、写入前改根实测"
---

# Skill 目标根切换重规划

方案已经提出、甚至已经批准，用户突然用一句话把目标根改到别处（典型是「要写入 .agents/skills/」或「迁入 .agents/skills」）。这不是在同一个计划里替换一个路径字符串，而是**授权范围发生了变化**：新根有不同的查重面、frontmatter 契约、登记面和验收门。把旧方案的内容原样搬到新路径，会把旧根的假设一起带过去。

本技能把这次改道变成一次**零写入的重规划**：先在新根重新取证，再给出路径、字段、文件清单与门禁命令的差异，确认后才落盘。

## Why

三种失败最贵，且都不会当场报错：

1. **只换路径不查新根**：旧根查重为空，不代表新根没有权威副本。照搬路径会在新根制造第二份真相，后续修改只落在其中一份。
2. **旧根已经被写过，却当作没发生**：可能留下空壳目录、半套文件或指向别处的联接。新根再写一份，就从「一份权威」变成「两份实体 + 一个悬空入口」。
3. **继承旧根的验收结论**：旧根跑过门禁不等于新根通过；新根的 frontmatter 字段、相对引用层级、登记面都不同，旧结论会掩盖真实断链和掉分。

> **为什么把换根当作授权变更而不是路径替换？** 用户批准的是「在某个根创建某个 Skill」。根变了，审批对象的边界、可写范围、后续登记责任都变了。把新根当成旧根的别名，等于在未经确认的新范围里写入。重规划的成本是一次读盘和一张差异表，误写的成本是清理两处实体并重新证明哪一份是权威。

> **为什么旧根取证必须显式做？** 空目录、联接和半套副本在 `ls` 里看起来都像「不存在」或「有个目录」。只有分别检查存在性、联接类型和内容清单，才能判断是需要清理、需要保留，还是确实从未写入。

## 1. 适用边界

| 场景 | 使用本技能 | 交给谁 |
|---|---|---|
| 方案已提出或已批准，写入前用户改目标根 | 是 | — |
| 换根后需要重读新根约定并重跑门禁 | 是 | — |
| 旧根可能已留下空壳、副本或联接 | 是（取证与处置建议） | 删除实体需单独授权 |
| 首次收到推荐，判断 create/update/补登记 | 否 | `skill-recommendation-disk-triage` |
| 已有 Skill 从用户级正式迁入主权区 | 否 | `user-skill-sovereign-migration` |
| 从零设计 Skill 内容 | 否 | `skill-creator` |
| 共享工作树 rebase 中的写入安全 | 否 | `shared-worktree-rebase-write-guard` |

判定口诀：**还没写 → 重规划；已经写完 → 迁移；还没判 → 分诊。**

## 2. 重规划六步（R1–R6，全部只读）

### R1 冻结写入并复述 delta

停止任何 `Write`、`Edit`、`mkdir`、`cp`。用一句话复述变化：

```text
旧根：<old-root>/<skill-name>
新根：<new-root>/<skill-name>
状态：尚未写入 / 旧根已有 N 个文件 / 旧根是联接
```

不静默继承旧方案的目录结构、frontmatter 字段和验收命令。

### R2 解析新根身份

| 新根形态 | 典型路径 | 约束 |
|---|---|---|
| 用户级 | `~/.qoder/skills/<name>` | 跨项目可见，通常只要求 `name` 与 `description` |
| 兼容用户级 | `~/.agents/skills/<name>` | 先确认是否与当前产品目录重叠 |
| 仓库主权区 | `<repo>/.agents/skills/<name>` | 需原生 frontmatter、登记面、仓库门禁 |
| 其他项目根 | 用户显式给出的绝对路径 | 只按该项目的实际约定，不套用 SpecWeave 规则 |

先确认仓库边界，再谈路径：

```bash
git rev-parse --show-toplevel
git rev-parse --show-superproject-working-tree
```

> **为什么不能用相对路径猜新根？** `.agents/skills/` 是相对当前工作目录的写法。在子目录、子模块或另一个 worktree 里执行时，它会指向完全不同的位置。新根必须解析成绝对路径并回显给用户。

### R3 在新根跨根查重

至少检查四个位置，名称一律用目录名与 frontmatter `name` 双重匹配：

```bash
for root in "$HOME/.qoder/skills" "$HOME/.agents/skills" "<repo>/.agents/skills"; do
  test -e "$root/<name>" && echo "EXISTS: $root/<name>"
  test -L "$root/<name>" && echo "LINK:   $root/<name>"
done
```

在仓库内再查受追踪登记面与 TOML 镜像：

```bash
git grep -n "<name>" -- .
ls -d .meta/toml/.agents/skills/<name> 2>/dev/null || echo "NO_TOML"
```

任一同名命中即停止写入，转入现状阅读与 update/补登记判断；不得用改名绕过。

### R4 重读新根约定

不要凭记忆套字段。读取新根的索引与两三个同类 Skill 的 frontmatter，列出字段差异：

| 字段 | 用户级常见 | 主权区常见 | 说明 |
|---|---|---|---|
| `name` / `description` | 必需 | 必需 | 目录名必须与 `name` 一致 |
| `version` | 可选 | 推荐 | 原生轨质量门按推荐字段计分 |
| `argument-hint` | 可选 | 推荐 | 有参数时填写 |
| `user-invocable` | 可选 | 推荐 | — |
| `paths` | 可选 | 推荐 | 指向该 Skill 自身目录 |
| `source` | 可选 | 推荐 | 溯源用自由文本，不是文件路径 |
| `title` | 可选 | 推荐 | 人类可读标题 |
| `x-toml-ref` | 不适用 | 有 TOML 镜像时才写 | 层级按文件实际位置推算 |

同时记录新根的登记面与门禁位置：

```bash
git status --short -- .agents/skills/README.md .agents/skills/CHANGELOG.md \
  .agents/capability-registry/02-skills.md
```

若这些文件正被其他会话修改，登记必须延后，不能把他人改动卷进来。

### R5 核对旧根从未写入

分别检查存在性、联接类型和内容，不要只看 `ls`：

```bash
test -e "<old-root>/<name>" && echo OLD_EXISTS || echo OLD_NOT_FOUND
test -L "<old-root>/<name>" && echo OLD_IS_LINK || echo OLD_NOT_LINK
find "<old-root>/<name>" -mindepth 1 -maxdepth 2 2>/dev/null | head -20
```

按结果分类处置：

| 旧根状态 | 含义 | 动作 |
|---|---|---|
| 不存在 | 从未写入 | 直接在新根创建，报告旧根未触碰 |
| 空目录 | 可能创建过目录但未落文件 | 报告；经授权后只用 `rmdir` 清理 |
| 完整或半套副本 | 曾写入实体内容 | 先比对文件清单与哈希，报告哪份是权威；删除需单独授权 |
| 联接 | 可能指向新根或其他位置 | 先读 `LinkType`/`Target`，不得直接复制或删除 |

> **为什么删除旧根不是重规划的默认步骤？** 目录里可能有用户或其他会话的产物。重规划只负责证明旧根状态并给出处置建议；删除是不可逆动作，必须有独立授权，且优先用可失败的空目录删除而不是递归强删。

### R6 输出修订方案等待确认

方案至少包含：

| 项目 | 内容 |
|---|---|
| 新目标路径 | 绝对路径 |
| 旧根状态 | 不存在 / 空壳 / 副本 / 联接，附命令证据 |
| 同名校验 | 四根 + `git grep` + TOML 结果 |
| frontmatter | 保留、新增、删除的字段，及 `x-toml-ref` 是否有真实目标 |
| 文件清单 | SKILL.md、references、scripts、evals 各写什么 |
| 验收命令 | 新根质量门与链接门的实际命令 |
| 延后事项 | 登记面、TOML、联接，以及延后原因 |

等待用户确认后再进入写入阶段。批准范围外的扩展回到 R6 补充。

## 3. 写入规则

- 只在**一个**根创建，不做双写兜底。
- 不用 `cp -r` 把旧方案目录搬过来；没有源目录时直接写新内容。
- 不用联接掩盖位置错误；联接是登记阶段的收尾手段，不是创建手段。
- 目标目录已存在时停止，先读现状，转 update 或冲突裁决。
- 新根是仓库主权区时，先写内容与资源，不碰正在被并发修改的登记面。

## 4. 新根验收

按新根实际能力选择门禁，不要拿旧根结论替代：

```bash
# 仓库主权区示例，路径按实际仓库探测
python .agents/scripts/check-skill-quality.py \
  --path .agents/skills/<name> --score --threshold 100
python .agents/scripts/check-links.py \
  --path .agents/skills/<name> --check-frontmatter-paths
```

无仓库门禁时，至少完成等价直接校验：

1. 解析 YAML frontmatter，确认 `name` 与目录名一致、`description` 非空。
2. 正文引用的每个相对路径真实存在。
3. 全文无绝对路径链接、无盘符绝对路径、无临时目录引用。
4. 文件为 UTF-8 无 BOM，无 `__pycache__`、`*.pyc` 等运行残留。
5. 有脚本时实跑一次帮助或只读模式，记录退出码。

> **为什么门禁必须在最终根上跑？** 用户级根通常没有仓库的质量门与链接门；在旧根跑过的分数不能证明新根的引用层级和登记字段成立。换根后重跑，才是对新交付物的验收。

## 5. 登记延后规则

新根是共享仓库且登记面有并发改动时：

- 只交付 Skill 内容与验证结果。
- 明确写「四处登记与 TOML 镜像延后」，并列出被并发修改的文件。
- 不在 `frontmatter` 写指向尚不存在 TOML 的 `x-toml-ref`，避免制造断链。
- 等并发会话提交后，重新读取计数，再走 `native-skill-surface-registration`。

## 6. 报告模板

```text
旧根：<path> — 不存在 / 空壳 / 副本 / 联接（附证据）
新根：<path> — 新建 N 个文件
同名校验：四根 0 命中；git grep 0 命中；TOML 无镜像
frontmatter：新增 <字段>；未写 x-toml-ref（TOML 待建）
质量门：<分数> / <通过项数>
链接门：<断链数>
未做：登记面（并发修改中）、TOML、联接、提交、推送
```

## 7. Gotchas

1. **`ls` 返回空不等于从未写入**：空目录、联接和权限失败都可能表现相似，必须分别测试存在性与联接类型。
2. **相对新根会跑偏**：`.agents/skills/` 相对 cwd 解析；在子目录或子模块里执行会写到别处，先解析绝对路径。
3. **质量门 95 分常是 description 缺触发场景**：补齐「当用户…」或「when…」措辞即可到 100，不要为此重写正文。
4. **`x-toml-ref` 层级按文件位置数**：`.agents/skills/<name>/SKILL.md` 到仓库根是三级；照抄根目录模板会多算或少算一层。
5. **没有 TOML 时写 `x-toml-ref` 会制造断链**：链接门开启 frontmatter 校验后会直接报错，登记延后就先省略。
6. **双写不是保险**：两个根各留实体，必然产生两份真相；最终应是一个权威副本，必要时再加联接。
7. **不要把 `source` 当路径字段**：它是溯源自由文本；写成仓库相对路径会被链接门当成失效引用。
8. **并发登记面不能顺手改**：`README`、`CHANGELOG`、`registry` 可能已暂存他人改动，延后并在报告中写明。
9. **旧根清理优先 `rmdir`**：非空目录是实体副本信号，先报告；递归强删会销毁未知产物。

## 8. 安全检查清单（逐项确认）

- [ ] 已冻结写入并复述旧根到新根的 delta
- [ ] 新根已解析为绝对路径，仓库根与 submodule 状态已确认
- [ ] 四根查重与 `git grep` 完成，同名命中时未覆盖
- [ ] 新根 frontmatter 与登记约定已从磁盘原文读取，非凭记忆
- [ ] 旧根存在性、联接类型与内容清单已取证并分类
- [ ] 修订方案已输出并取得确认，批准前零写入
- [ ] 只在单一根创建，无双写、无 `cp -r`、无联接掩盖
- [ ] 新根质量门与链接门已实跑，结果与退出码已记录
- [ ] 引用资源真实存在，无绝对链接与运行残留
- [ ] 并发登记面未被触碰，延后事项已写明
- [ ] 未提交、未推送，旧根删除有独立授权

## 参考

- 来源会话证据与可/不可证明边界：[references/verified-case.md](references/verified-case.md)
