# 已验证案例：2026-10-24 用户级目录联接交付

## 1. 来源

- 会话 ID：`55d75850-2970-4739-b3f2-5226175d4a6f`
- 会话标题：创建共享分支预检技能
- 取证方式：`read_chat_session` 读取消息与工具输出；另读取上游会话 `767c40d5-6d6c-4bbe-9682-09774c17eaa2` 的用户原话
- 涉及仓库：SpecWeave（`D:\spaces\SpecWeave`）
- 交付对象：`shared-branch-merge-push-gate`

## 2. 推荐与磁盘的错配

推荐 JSON 要求：

```text
skillName: shared-branch-merge-push-gate
action:    create
target:    C:\Users\xinzo\.qoder\skills\shared-branch-merge-push-gate
```

磁盘实况：

| 探针 | 结果 |
|---|---|
| 用户级目标 `~/.qoder/skills/shared-branch-merge-push-gate` | 不存在 |
| 主权区 `.agents/skills/shared-branch-merge-push-gate` | 存在，含 `SKILL.md`、`scripts/merge_gate.py`、`references/verified-case.md`、`evals/evals.json` |
| 质量门（主权区） | `100` 分，退出码 0 |
| 链接门（主权区） | 0 断链，退出码 0 |
| 四处登记 `git grep` | 零命中（登记延后） |

结论：推荐的 `create` 不成立。内容已经存在且已验收，缺的只是用户级可见性。

## 3. 用户纠正与决策

上游会话 `767c40d5` 中，首次提案后用户原话：

```text
要写入 .agents/skills/
```

因此该 Skill 的权威副本落在主权区，而不是用户级根。

本次会话 `55d75850` 中，提案后的选择：

```text
目标路径 C:\Users\xinzo\.qoder\skills\shared-branch-merge-push-gate 采用哪种落地方式？
→ 目录联接到主权区（推荐）
```

关键点：用户批准的是「联接」，不是「复制」，也不是「登记」。

## 4. 实际创建

```powershell
New-Item -ItemType Junction `
  -Path "$env:USERPROFILE\.qoder\skills\shared-branch-merge-push-gate" `
  -Target "D:\spaces\SpecWeave\.agents\skills\shared-branch-merge-push-gate"
```

回读：

```text
FullName : C:\Users\xinzo\.qoder\skills\shared-branch-merge-push-gate
LinkType : Junction
Target   : {D:\spaces\SpecWeave\.agents\skills\shared-branch-merge-push-gate}
```

未复制任何文件；权威内容仍只有主权区一份。

## 5. 经目标路径的验证输出

### 5.1 联接类型

```text
LinkType : Junction
Target   : D:\spaces\SpecWeave\.agents\skills\shared-branch-merge-push-gate
```

### 5.2 文件枚举必须带 `-L`

```bash
find "C:/Users/xinzo/.qoder/skills/shared-branch-merge-push-gate" -type f
# （无输出）

find -L "C:/Users/xinzo/.qoder/skills/shared-branch-merge-push-gate" -type f
# SKILL.md
# evals/evals.json
# references/verified-case.md
# scripts/merge_gate.py
```

不带 `-L` 的 `find` 返回空，是本案例最容易被误判为「交付为空」的点。

### 5.3 经目标路径的质量门与链接门

```bash
python .agents/scripts/check-skill-quality.py \
  --path "C:/Users/xinzo/.qoder/skills/shared-branch-merge-push-gate" \
  --score --threshold 100
# shared-branch-merge-push-gate: 100
# 平均: 100
# exit 0

python .agents/scripts/check-links.py \
  --path "C:/Users/xinzo/.qoder/skills/shared-branch-merge-push-gate" \
  --check-frontmatter-paths
# 校验通过: 所有链接均有效
# exit 0
```

### 5.4 frontmatter 与 evals

```text
name: shared-branch-merge-push-gate
dir_match: True
description_len: 473
desc_colon_space: False
desc_angle: False
body_nonempty: True
evals: 4  skill: shared-branch-merge-push-gate
utf8_bom: False
```

### 5.5 捆绑脚本经联接可执行

```bash
python "$HOME/.qoder/skills/shared-branch-merge-push-gate/scripts/merge_gate.py" --help
# HELP_EXIT=0
```

一次只读预检也经目标路径跑通：

```text
upstream:  origin/main @ d2d35375e4d1
divergence: ahead 2 / behind 0
merge-tree: clean
index.lock: absent
verdict: CLEAR - nothing to merge; push directly if authorized
GATE_EXIT=0
```

### 5.6 只读证明

```text
STATUS_BEFORE=790b3c6183b4d6214bacb3b9d1f238b08f497faae835e15f3992ac56bdf3bfe8
STATUS_AFTER =790b3c6183b4d6214bacb3b9d1f238b08f497faae835e15f3992ac56bdf3bfe8
STATUS_UNCHANGED=yes
```

运行残留检查：技能目录内无 `__pycache__`。

## 6. 本案例能证明什么

- 「用户级不存在」不等于「Skill 不存在」；同一名字可能在主权区已有验收副本。
- 目录联接可以同时满足 Qoder 的发现路径与仓库的版本控制路径，且不产生第二份内容。
- 双门可以经联接路径复跑，分数与断链结果不变。
- `find` 必须加 `-L` 才能看到联接内文件。
- 创建联接不会改动仓库工作树；`git status` 哈希前后一致可作为证据。

## 7. 本案例不能证明什么

- 没有验证 `native-skill-surface-registration` 的四处登记流程；本案例明确未登记。
- 没有验证目标路径已存在实体目录时的替换流程；本技能要求停下报告，而不是自动删除。
- 没有在 macOS/Linux 上验证目录联接的行为；命令片段以 Windows PowerShell 为准。
- 没有验证多人同时修改用户级技能根时的竞争情况。
