---
id: "skill-registration-writer-edit-model"
date: "2026-11-09"
type: "reference"
source: "../SKILL.md#3. 写入边界模型"
title: "登记面写入的边界与回滚模型"
---
# 登记面写入的边界与回滚模型

本文说明 `apply_registration.py` 为什么只允许两类改动、凭什么证明没有多改、以及回滚依赖哪些落盘物。

## 1. 允许改动的两类行

| 类型 | 落点 | 变更粒度 |
|---|---|---|
| 计数 token | 分类标题行内 `（N个）` 的数字 | 只替换数字，标题文案与来源后缀不动 |
| 整行插入 | 指定分类首表最后一行之后；CHANGELOG 最新条目之前 | 一行一条，不改动既有行 |

不允许：重排表格、改写既有行、调整标题层级、修改 SKILL.md 正文或 frontmatter、批量对齐两面的分类集合。

> **为什么？** 登记面是多人共写的共享文件。改动粒度越接近「一个数字」「一行」，并发冲突的面越小，review 也越容易看清「这次到底动了什么」。

## 2. 三道具名检查

1. **越界断言**：`difflib.SequenceMatcher` 对旧/新行序列求 opcode；`insert` 的 `i1 == i2` 必须落在允许插入点，`replace` 必须只覆盖一行且该行是计数行。任何其他 opcode 抛错中止。
2. **行数守恒**：新行数 == 旧行数 + 计划插入行数。
3. **写前哈希**：计划阶段记录目标文件 sha256，写入前重算；不等即中止，提示「文件被并发修改」。

> **为什么？** 只靠「代码里只改了这一处」是自证。opcode 断言把「改动的集合」与「允许的集合」做集合相等判断，越界会显式失败；写前哈希则处理共享工作树里另一会话刚提交的情形 —— 此时旧行号已经失效，继续写就是把改动插到错误位置。

## 3. 备份、journal 与回滚

```text
.temp/skill-registration-writer/
├── backup/<ts>/README.md
├── backup/<ts>/02-skills.md
├── backup/<ts>/CHANGELOG.md
└── journal-<ts>.json
```

journal 逐文件记录 `path`、`action`（`modify` / `create`）、`backup`、`before_sha256`、`after_sha256`。

`--revert` 倒序处理：`modify` 用备份覆盖并校验 `before_sha256`；`create` 直接删除。缺省取目录中最新一条 journal，也可显式传路径。

> **为什么？** `.temp/` 已被 gitignore 覆盖，备份不会污染工作树，也不会被误提交。回滚必须能回答「恢复到哪一版」——只存内容不存哈希，就无法判断恢复是否成功。

## 4. 幂等判定

| 动作 | 已满足的判据 |
|---|---|
| README / registry 表行 | 该面已存在同名行 |
| 分类计数 | 声明值 == 实际行数 + 待插入数 |
| CHANGELOG | 已存在以同一 `--note` 结尾的条目 |
| TOML 镜像 | 目标路径已存在 |

`--write` 完成后立即复跑；剩余动作或阻塞非 0 即返回 2。

> **为什么？** 幂等的验收标准是「同一命令第二次执行零改动」，而不是「第二次执行不报错」。把判据写进计划阶段，复跑自然会退化为空计划。

## 5. 已知不做的事

- 不自动决定分类归属（必须 `--assign`）。
- 不修改 SKILL.md frontmatter 的 `x-toml-ref`（由登记流程或 `registered-skill-frontmatter-completion` 负责）。
- 不修正 `version` 漂移（镜像惯例为两段快照，与 SKILL.md 不同属正常）。
- 不处理镜像轨技能的 registry 登记（按仓库惯例不登记）。
