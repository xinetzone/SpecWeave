# 证据案例：2026-10-24 共享工作树 rebase 中断

本文件记录触发本技能的实测事件，供后人逐字复跑比对。所有数字来自当时的 `git status`、rebase 元数据、reflog 与登记面实读，不包含推断值。

## 1. 结论摘要

- 另一进程在 `main` 上执行 `git pull --tags origin main`，以 interactive rebase 方式重放 9 个提交。
- rebase 停在 `1/9`，唯一冲突是子模块 gitlink：`UU projects/awesome-okf-xs`。
- 中断期间登记面回退：README 完整Skill `18→11`、registry 完整Skill `16→9`、CHANGELOG `v1.35→v1.29`。
- 代理停止共享写入，只创建未跟踪 Skill 目录与用户级 Junction；脚本自检 `8/8 PASS`、质量门 `100/100`、链接门 `0 断链`。
- 未执行 `rebase --abort/--continue/--skip`，未暂存，未提交，未改共享登记面。
- 09:22:42 rebase 由另一进程完成，登记面恢复为 `18/16/v1.35`。状态在调查中途翻转，证明「每个写入批次前重探」是必要条件。

## 2. 时间线

| 时间（+0800） | 事件 | 证据 |
|---|---|---|
| 09:12:10 | 共享登记面被 checkout 改写 | README、registry、CHANGELOG 的 mtime 均为 09:12:10 |
| 09:12:11 | `git pull --tags origin main` 启动 rebase | reflog：`pull --tags origin main (start): checkout d18b5e261` |
| 09:12 后 | rebase 停在 1/9 | `git status`：interactive rebase in progress; onto d18b5e261 |
| 调查中 | 登记面读到旧基线 | README 完整Skill 11、registry 完整Skill 9、CHANGELOG v1.29 |
| 09:22:42 | rebase 完成，回到 `main` | reflog：`rebase (finish): returning to refs/heads/main` |
| 09:22:42 后 | 登记面恢复 | README 完整Skill 18、registry 完整Skill 16、CHANGELOG v1.35 |

## 3. 探测输出（节选）

```text
$ git status
interactive rebase in progress; onto d18b5e261
Last command done (1 command done):
   pick 3ffea862f # chore(submodule): 前移 awesome-okf-xs 指针至 f766116c（知乎盐言作者平台知识包）
Next commands to do (8 remaining commands):
   pick 805da9c9d # docs(references): 统一三个 Bundle 的 references 索引页命名并修正目录清单
   ...
Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   projects/awesome-okf-xs
```

```text
$ cat .git/rebase-merge/head-name     -> refs/heads/main
$ cat .git/rebase-merge/onto          -> d18b5e26162251df4c6fed24b0476cbeff47d79a
$ cat .git/rebase-merge/orig-head     -> baccb02c4eebf8cc2fe8dbdb1be627d0f30eea70
$ cat .git/rebase-merge/stopped-sha   -> 3ffea862f99eb1dedd4750282cf9dc3bf571d7e7
$ cat .git/rebase-merge/msgnum        -> 1
$ cat .git/rebase-merge/end           -> 9
```

```text
$ git reflog -8 --date=iso
d18b5e261 HEAD@{2026-10-24 09:12:11 +0800}: pull --tags origin main (start): checkout d18b5e261
baccb02c4 HEAD@{2026-10-24 02:04:26 +0100}: commit: feat(skills): 入库 registered-skill-frontmatter-completion 并同步登记面
...
```

```text
$ git rev-parse --abbrev-ref HEAD
HEAD
```

## 4. 为什么中途写入会失败

1. **已跟踪文件是旧基线**：中断检出对应 `onto=d18b5e261`，而待重放的 8 个提交尚未落回。读到 README 的 11 个完整 Skill，不是「有人删了 7 个」，而是重放尚未发生。
2. **写入会被后续 pick 覆盖**：rebase 继续时，每个 pick 都会改写工作树。中途写 README/registry/CHANGELOG，等于在会被替换的字节上做修改。
3. **冲突会被放大**：原本只有 `projects/awesome-okf-xs` 一个 gitlink 冲突；若中途改同一批共享文件，后续提交可能在文本层面产生新冲突。
4. **中止/继续是越权**：rebase 由其他进程发起，`--abort` 会丢弃正在重放的提交，`--continue` 会在冲突未解决时推进历史。

## 5. 已验证步骤（来源会话）

| 步骤 | 结果 | 复跑方式 |
|---|---|---|
| 只创建未跟踪 Skill 目录 | `git status` 仅新增 `??`，无共享文件改动 | `git status --short` |
| 用户级 Junction | 指向主权区目录，`cmp` 字节一致；经联接运行自检通过 | `cmp` + 经用户级路径运行脚本 |
| 审计脚本自检 | `8/8 PASS` | `node scripts/audit_surface_counts.js --self-test`（位于 `skill-registry-count-drift-audit`） |
| 质量门 | `100/100`，34 项全 PASS，退出码 0 | `python .agents/scripts/check-skill-quality.py --path <skill> --score --threshold 100` |
| 链接门 | `0 断链` | `python .agents/scripts/check-links.py --paths <skill> --check-frontmatter-paths` |
| 未执行的操作 | 无 abort/continue/skip、无 reset/checkout/clean、无暂存、无提交 | reflog 与 `git status` 可复核 |

## 6. 恢复后的基线（2026-10-24 09:2x）

用只读审计脚本对当前文件实跑，结果显示：

| 登记面 | 分类 | 声明 | 实际 | 判定 |
|---|---|---|---|---|
| README | 完整Skill | 18 | 18 | OK |
| README | 命令集门面 | 11 | 11 | OK |
| registry | 完整Skill | 16 | 16 | OK |
| registry | 命令集门面 | 11 | 10 | DRIFT |

跨面名称差：`token-optimize-cmd`（命令集门面）、`trae-computer-use-ptc`、`meoo-cli`（完整Skill）。这些是 rebase 之前就存在的登记漂移，不是本次 rebase 造成的；处理它们属于 `skill-registry-count-drift-audit` 与 `native-skill-surface-registration` 的职责，本技能只负责在恢复后重跑审计、拿到当前基线。

## 7. 可复跑命令

```bash
SKILL_DIR=".agents/skills/shared-worktree-rebase-write-guard"

# 1) 自检：11 个夹具
node "$SKILL_DIR/scripts/check_rebase_guard.js" --self-test

# 2) 当前仓库总体状态
node "$SKILL_DIR/scripts/check_rebase_guard.js" --repo . --json

# 3) 写入目标分类
node "$SKILL_DIR/scripts/check_rebase_guard.js" --repo . --target .agents/skills/<new-skill> --json

# 4) 严格模式：已跟踪目标有未提交改动时延后
node "$SKILL_DIR/scripts/check_rebase_guard.js" --repo . --target .agents/skills/README.md --strict
```

退出码：`0` 可写；`1` 延后（操作进行中/目标被锁或 dirty）；`2` 有冲突只读；`3` 参数或 git 错误。

## 8. 关联

- [.agents/skills 目录索引](../../README.md)
- [Skill 变更记录](../../CHANGELOG.md)
- [capability-registry/02-skills.md](../../../capability-registry/02-skills.md)
- [登记面计数漂移审计](../../skill-registry-count-drift-audit/SKILL.md)
- [四处登记本体](../../native-skill-surface-registration/SKILL.md)
- [探测脚本](../scripts/check_rebase_guard.js)
