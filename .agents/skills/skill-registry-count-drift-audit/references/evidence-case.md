# 证据案例：三版计数器与两次误报

本文件记录 2026-10-23 会话 `0df2781d-fbf2-4120-8257-602ed49d4f65` 中，为 `oversized-tool-output-slicing` 做四处登记时顺带审计分类计数的真实过程。所有数字均来自当时的工具输出，不是事后推算。

## 1. 第一版：标题正则漏掉带空格的分类

命令思路：用 `^###\s+(\S+)（(\d+)个）` 解析标题，再从标题下方取到下一个匹配标题。

实际输出（README）：

```text
=== .agents/skills/README.md ===
DRIFT 表头=11 行数=11  [0]
DRIFT 表头=15 行数=15  [0]
DRIFT 表头=6 行数=6    [0]
DRIFT 表头=16 行数=18  [17]
```

问题：README 当时有 8 个分类，只匹配到 4 个。被漏掉的是：

- `Trae 内置工作流 Skill（2个，来自 external/doutops）`
- `内置镜像 Skill（21个，来自 Trae IDE builtin 镜像）`
- `设计库镜像 Skill（16个，来自 Trae IDE design_libraries 镜像）`
- `TeleAgent 平台镜像 Skill（1个）`

它们没有截断上一节，导致后面的表格被累加到「脚本命令门面」，出现 16/18。

## 2. 第二版：反向取节导致 6/50

修正标题正则后，改用「从当前位置反向找最近的分类标题」界定区间。实际输出：

```text
=== .agents/skills/README.md ===
OK   命令集门面: 表头=11 行数=11
OK   完整Skill: 表头=15 行数=15
DRIFT 工作流门面: 表头=6 行数=50
DRIFT TeleAgent 平台镜像 Skill: 表头=1 行数=2
DRIFT 脚本命令门面: 表头=16 行数=18
```

问题：区间仍然跨过了带空格的分类标题，`工作流门面` 一路吞到后面的镜像分类，50 行是多个分类表格的总和。若采信这个结果，会把正确的 `6` 改成 `50`。

## 3. 第三版：下一条标题 + 只取首表

修正区间为「当前标题到下一个标题」，并且只统计区间内第一张表：

```text
=== .agents/skills/README.md ===
OK   命令集门面: 表头=11 首表行数=11
OK   完整Skill: 表头=15 首表行数=15
OK   工作流门面: 表头=6 首表行数=6
OK   Trae 内置工作流 Skill: 表头=2 首表行数=2
DRIFT 内置镜像 Skill: 表头=21 首表行数=8
OK   设计库镜像 Skill: 表头=16 首表行数=16
OK   TeleAgent 平台镜像 Skill: 表头=1 首表行数=1
OK   脚本命令门面: 表头=16 首表行数=16
```

问题：`内置镜像 Skill` 是合法的多子表分类，`21` 是四张子表之和：

| 家族 | 行数 |
|---|---|
| work | 8 |
| global | 6 |
| design | 4 |
| code | 3 |
| 合计 | 21 |

只数首表会得到 8，从而把正确的表头判成漂移。

## 4. 收敛：区间内全部表格求和 + 跨面名称差

把区间内所有表格的数据行求和后，README 全部分类一致；registry 仍有一处：

```text
=== .agents/capability-registry/02-skills.md ===
OK   完整Skill: 表头=13 行数=13
OK   工作流门面: 表头=6 行数=6
DRIFT 命令集门面: 表头=11 行数=10
OK   脚本命令门面: 表头=16 行数=16
```

随后做跨面名称差，差集恰好是 `token-optimize-cmd`：

- README 第 35 行有该行；
- registry 无该行；
- `.agents/skills/token-optimize-cmd/SKILL.md` 磁盘存在。

结论：这是 **registry 缺行**，不是表头写错。会话最后一轮用户要求补上该行，但该轮状态为 `failed`、无工具调用，因此缺行在会话结束时仍未修复。

## 5. 2026-10-24 复跑基线

在 rebase 进行中的检出（HEAD `d18b5e261`）上运行本技能脚本，结果为：

```text
README:     完整Skill 声明 11 / 实际 12  DRIFT
registry:   完整Skill 声明 9  / 实际 10  DRIFT
registry:   命令集门面 声明 11 / 实际 10  DRIFT
跨面差:     trae-computer-use-ptc、meoo-cli、token-optimize-cmd 均 disk:yes
退出码:     1
```

这组数字只用于证明脚本能同时检出两类问题；rebase 完成后登记面会变化，必须以最新一次复跑为准。

## 6. 复跑命令

```bash
node .agents/skills/skill-registry-count-drift-audit/scripts/audit_surface_counts.js \
  --self-test

node .agents/skills/skill-registry-count-drift-audit/scripts/audit_surface_counts.js \
  --readme .agents/skills/README.md \
  --registry .agents/capability-registry/02-skills.md \
  --skills-root .agents/skills
```

## 7. 可复用教训

1. **先自证计数器，再判登记面**。两次误报都指向「改表头」，但表头本来就是对的。
2. **标题正则必须允许空格**，否则漏匹配会以「行数累加」的形式伪装成漂移。
3. **区间必须由标题截断**，且不能只认「带计数的标题」。
4. **多子表必须求和**，首表行数只能作为诊断信息，不能作为判定依据。
5. **表头漂移与缺行分开处理**：前者核对实际行数，后者核对跨面名称差并验盘。
6. **缺行只报告**。缺行往往是他人刚入库、尚未同步的资产，擅改属于越权。
