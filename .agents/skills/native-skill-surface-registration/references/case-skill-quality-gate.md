# 案例：skill-quality-gate-remediation 入库（CHANGELOG v1.31）

本案例是 `native-skill-surface-registration` 流程的真实来源，证据于 2026-10-23 从磁盘逐项核实（来源会话 82bdd798-8c2b-4dfb-a04d-1153618957a5、b2c97a46-89db-466b-837a-01b88669ae4b；部分执行记录在会话读取时仍在流式进行，因此本文件只记录已能在磁盘上复验的事实）。

## 时间线

1. Skill 由 declared-consistency-fix 质量门 65→100 实战萃取，在用户级 `~/.qoder/skills` 起草。
2. 用户纠正落点：「为何没有放在 .agents/skills?」→「移入」——权威副本必须在主权区。
3. 迁入后首跑质量门 65/100（1 error + 4 warn），按检查器正则实质性补齐后 100/100、34 项全过（该分诊细节归 `skill-quality-gate-remediation` 本身）。
4. 完成四处登记 + 用户级联接（下节）。

## 登记面终态（磁盘实测）

| 登记面 | 实测证据 |
|---|---|
| `.agents/skills/README.md` | 完整Skill 分类行 `skill-quality-gate-remediation`（表头 14 个 = 表体 14 行） |
| `.agents/capability-registry/02-skills.md` | 完整Skill 分类行（表头 12 个 = 表体 12 行；与 README 基数不同属正常） |
| `.agents/skills/CHANGELOG.md` | v1.31 条目：记录 65→100 萃取、S0–S6 流程、判据源码行号、验收数据「100/100（34 项全 PASS，Why 引用块 8 处、安全清单 12 项、正文 193 行）」 |
| `.meta/toml/.agents/skills/skill-quality-gate-remediation/SKILL.toml` | 5 字段镜像：id/title/category/date/version，category=`skills/skill-quality-gate-remediation` |
| 用户级 | `~/.qoder/skills/skill-quality-gate-remediation` 为 symlink/junction，target=`D:\spaces\SpecWeave\.agents\skills\skill-quality-gate-remediation`，零内容复制 |

## 本流程吸收的规则

1. **登记面基数不同不是漂移**：README 14 vs registry 12 是收录范围差异，各自表头=自身表行数才算一致；把两者「拉平」反而是错误修复。
2. **HEAD 计数会先行漂移**：该入库批次的前一版（v1.30）CHANGELOG 明确记录「顺带修正既有计数漂移：README 表头 11→13（原有 12 行）、registry 表头 9→11（原有 10 行）」——登记时必须顺带审计，不能只 +1 本次。
3. **联接改造前用户级可能出现空副作用目录树**：以 `rmdir`（仅空目录可删）清理后建联接；非空即实体副本信号，须先报告。
4. **mklink /J 中文乱码**：`cmd /c mklink /J` 失败后改用 PowerShell `New-Item -ItemType Junction` 成功；工具替换发生在真实执行中，处方保留 PowerShell 形式。
5. **验收数据写进 CHANGELOG**：v1.31 条目内嵌分数、通过项数、Why 块数、清单项数、正文行数，后续维护者可直接复跑比对，不必翻会话。
