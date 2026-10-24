# 案例：零源改根（旧根从未写入）

本案例来自会话 `82aa536e-ed72-4370-bd04-6f0ef014f959`，记录一次「方案已提出、源从未落盘，用户只说迁入」的真实链路。它证明 `user-skill-sovereign-migration` 不能把所有「迁入」都当成有源复制。

## 1. 背景

会话前一段已完成 `skill-target-root-switch-replan` 的内容方案，原计划把 Skill 写入用户级目录 `C:\Users\xinzo\.qoder\skills\skill-target-root-switch-replan`。方案尚未落盘时，用户只回了一句：

> 迁入.agents/skills

没有重新描述内容，也没有说明源目录在哪里。

## 2. 零写入预检的实际输出

| 检查项 | 结果 |
|---|---|
| 仓库根 | `D:/spaces/SpecWeave`，`git rev-parse --show-superproject-working-tree` 为空（非 submodule） |
| 新根目标 | `.agents/skills/skill-target-root-switch-replan` 不存在 |
| 旧根目标 | `~/.qoder/skills/skill-target-root-switch-replan` 不存在，且不是联接 |
| 同名登记 | `git grep` 无命中；`.meta/toml` 无镜像 |
| 并发状态 | `README.md`、`CHANGELOG.md`、`capability-registry/02-skills.md` 均被他处修改（` M`），无 `index.lock` |

结论：这不是迁移，而是**零源改根**——源从未存在，复制与哈希没有对象。

## 3. 正确执行链

1. 冻结写入，复述 delta：旧根不改，新根为 `.agents/skills/<name>`。
2. 旧根取证：不存在、非联接，因此无空壳、无副本、无联接需要清理。
3. 新根跨根查重：三个根均无同名副本；仓库登记面只有一处历史提及，不是登记行。
4. 重读新根约定：`version`、`argument-hint`、`user-invocable`、`paths`、`source`、`title`；TOML 未建时不写 `x-toml-ref`。
5. 输出修订方案，用户回复「没问题，按此方案开始执行」。
6. 直接在新根写入 `SKILL.md` 与 `references/verified-case.md`，未读源全文、未复制、未做 SHA256。
7. 在新根跑质量门与链接门，并核对旧根仍不存在。

## 4. 实际验收结果

- 质量门：`100/100`，退出码 0。
- 链接门：0 断链，frontmatter 路径字段有效，退出码 0。
- 工作树：仅新增 `?? .agents/skills/skill-target-root-switch-replan/`，三个登记面未被触碰，无 `index.lock`。
- 旧根：仍不存在，也不是联接。

## 5. 被跳过的步骤及原因

| 常规迁移步骤 | 本案例处置 | 原因 |
|---|---|---|
| 读取源 Skill 全文 | 不执行 | 源不存在 |
| 复制正文与资源 | 不执行 | 无可复制对象 |
| 逐文件 SHA256 比对 | 不执行，报告写「不适用」 | 没有比对基准 |
| 正文逐字比对 | 不执行，报告写「不适用」 | 同上 |

> 把「不适用」写成「PASS」会制造审计假象：后续读者无法区分「确实比对过且一致」与「根本没有源」。

## 6. 与既有技能的分工

| 场景 | 归属 |
|---|---|
| 方案批准后仅改目标根，源从未写入 | 重规划由 `skill-target-root-switch-replan` 负责；本技能负责判定无源并完成创建 |
| 已有用户级实体 Skill 要迁入 | 本技能的有源迁移轨道 |
| 首次收到推荐，判断 create/update/补登记 | `skill-recommendation-disk-triage` |

## 7. 边界

本案例只覆盖「无源改根」这一条链，不证明以下事项：

- 四处登记与 TOML 镜像（本案例延后未做）
- 用户级 Junction（未创建）
- 提交与推送（未执行）
