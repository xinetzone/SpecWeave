# 持久性守卫的来源取证

本文件记录 `skill-junction-durability-guard` 的事实底座：来源会话读到了什么、磁盘当时是什么状态、哪些结论是实测、哪些没有取证。

## 1. 来源会话 f42493e0

- 会话 `f42493e0-b2e8-46ad-ba54-5d08fadce06d` 的快照只有 **2 条消息**（一条用户指令 + 一条助手方案），`runtimeState=cold`、`hasMoreBefore=false`。
- 助手方案停在「请确认」；会话**没有执行任何联接创建或提交**。
- 方案中的关键发现：主权区 `version-floor-contract-guard` 已存在且过双门，但用户级目标不存在，且权威副本尚未跟踪。

结论：该会话只到提案阶段，不能作为「联接已交付」的证据。

## 2. 来源会话 2559ea47

在 f42493e0 的落盘工具结果中读到了更早的会话 `2559ea47`（标题「创建版本底线校验技能」），其中记录了：

- 用户纠正：**「改为写入 SpecWeave 主权区」**——最初目标在用户级，被纠正到主权区。
- 质量门 100/100、链接门 0 断链、计数审计 0 漂移、无 `__pycache__`。
- 明确没有创建用户级联接，也没有提交。

结论：内容质量与「是否持久」是两条独立结论；该会话证明前者，没有覆盖后者。

## 3. 取证时的磁盘事实（2026-10-24）

```text
git ls-files -- .agents/skills/version-floor-contract-guard \
               .meta/toml/.agents/skills/version-floor-contract-guard
→ 空（未跟踪）

git status --porcelain=v1 -- <上述路径> <三个登记面>
 M .agents/capability-registry/02-skills.md
 M .agents/skills/CHANGELOG.md
 M .agents/skills/README.md
?? .agents/skills/version-floor-contract-guard/
?? .meta/toml/.agents/skills/version-floor-contract-guard/
```

同时：

- `C:/Users/xinzo/.qoder/skills/version-floor-contract-guard` **不存在**。
- `skill-junction-durability-guard` 在主权区、`.meta`、用户级三个根均不存在，仓库 grep 零命中。

## 4. 由事实得出的判定

| 对象 | 判定 | 依据 |
|---|---|---|
| `version-floor-contract-guard` 副本 | D2（未跟踪） | `git ls-files` 空 + `??` |
| 其镜像 | D2 | 同上 |
| 三个登记面 | D1（已跟踪、已修改未提交） | ` M` 前缀 |
| 用户级联接 | 不存在 | `ls` 失败 |

若此时先建联接再执行 `git clean -fd`：权威副本被删除，联接指向不存在的路径，技能从「可触发」直接变为「消失」，而 `git status` 在清理前后都可能是干净的。

若先在联接交付时提交（B 未授权却执行）：会把同一工作树里其它在途改动一并带走。这正是 A/B/C/D 必须拆分的直接理由。

## 5. 目标路径链接门的实测局限

联接交付后按 `check-links.py --path <用户级目录> --check-frontmatter-paths` 复跑，实测结果：

```text
[C:\Users\xinzo\.qoder\skills\skill-junction-durability-guard\SKILL.md]
x-toml-ref: ../../../.meta/toml/.agents/skills/skill-junction-durability-guard/SKILL.toml
(文件不存在: C:\Users\xinzo\.meta\toml\.agents\skills\skill-junction-durability-guard\SKILL.toml)
→ 本地 0 断链，frontmatter 1 处失败，退出码 1
```

对已联接的同族技能 `user-level-skill-junction-delivery` 跑同一条命令，得到**完全相同**的一条失败。结论：`x-toml-ref` 的三级上跳是相对仓库位置的约定，经用户级根解析必然越出仓库；这是联接模式的固有局限，不是本次引入的断链。

健康判据因此改为两条同时成立：仓库路径链接门 0 断链退出 0；目标路径链接门本地 0 断链且 frontmatter 只有 `x-toml-ref` 一项失败。

## 6. 登记面复跑基线

- 全集链接门（`.agents/skills` + `.agents/capability-registry`）：117 处既有 frontmatter 断链，退出码 1；本次新增技能零命中。
- v1.40 记录的历史基线为 118，差值 -1 来自 `version-floor-contract-guard` 的镜像已落盘、其 `x-toml-ref` 现在可解析，与本技能无关。
- 计数审计：README 与 registry 的完整 Skill 均声明 26、实际 26，0 处表头漂移、0 处跨面缺行。

## 7. 未取证项

- 推荐 JSON 中提到的 PowerShell `$env:USERPROFILE` 失败，**不在**该会话快照内。正文只把它写成「PowerShell 用 `$env:USERPROFILE`、Git Bash 用 `$HOME`」的通用语义 Gotcha，没有声称本案例实测过该失败。
- 无法在本会话内验证 Qoder 重新索引用户级技能的时间窗口；只能验证目标路径可读、联接类型正确、门禁经目标路径通过。
- 无法验证其它机器 clone 后的行为，相关表述按「未跟踪即不可复现」的通用结论书写。
