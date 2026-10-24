# 已验证案例：方案提出后把目标根改到主权区

## 1. 来源与范围

| 项 | 内容 |
|---|---|
| 来源会话 | `767c40d5-6d6c-4bbe-9682-09774c17eaa2`，标题「请帮助我创建或更新一个可复用的 Skill」 |
| 时间 | 2026-10-24 |
| 被创建对象 | `shared-branch-merge-push-gate` |
| 初始目标根 | `~/.qoder/skills/shared-branch-merge-push-gate` |
| 改道后目标根 | 仓库主权区 `.agents/skills/shared-branch-merge-push-gate` |
| 本文用途 | 记录换根前后真实发生的步骤、门禁结果与证据边界 |

本案例不是「迁移已存在的 Skill」，而是**写入前改根**：旧根从未落过内容，因此没有复制、哈希比对或源目录删除环节。

## 2. 真实链路

| 阶段 | 已核实事实 |
|---|---|
| 首轮方案 | 方案明确写用户级目标根 `~/.qoder/skills/shared-branch-merge-push-gate`，并规划 SKILL.md、scripts、references、evals 四类文件 |
| 用户改道 | 第二轮用户只回一句「要写入 .agents/skills/」，没有重述内容或字段要求 |
| 重读约定 | 助手重读主权区 `.agents/skills/README.md`、同类 Skill 的 frontmatter（`version`、`argument-hint`、`user-invocable`、`paths`、`source`、`title`、`x-toml-ref`），并读取质量门与链接门的参数 |
| 并发发现 | `git status --short` 显示 `.agents/skills/README.md`、`.agents/skills/CHANGELOG.md`、`.agents/capability-registry/02-skills.md` 已被另一会话修改并暂存 |
| 写入范围 | 只创建 `.agents/skills/shared-branch-merge-push-gate/` 下的 SKILL.md、scripts、references、evals |
| 登记状态 | 四处登记与 TOML 镜像未做，最终报告明确写「登记延后」 |
| 旧根状态 | 首轮目录枚举显示目标不存在；最终报告写「未写入用户级目录」 |
| 最终工作树 | 仅 `?? .agents/skills/shared-branch-merge-push-gate/`，无 `index.lock`，登记面 grep 无本 Skill 命中 |

## 3. 门禁实测

| 检查 | 结果 |
|---|---|
| 质量门首次 | 95 分，唯一警告为 description 缺少触发场景说明 |
| 修补 | 按判定规则补齐「当用户…」类触发措辞 |
| 质量门复跑 | 100 分，34 项通过 |
| 链接门 | 退出 0，0 断链，frontmatter 路径字段全部有效 |
| 脚本帮助 | 退出 0 |
| 当前仓库只读运行 | 退出 0，未改索引与工作树 |
| 临时夹具 | 干净 0、前提漂移 2、冲突 3、路径碰撞 4、索引锁 5、上游缺失 6 |
| 文件编码 | 四个文件均为 UTF-8 无 BOM，无运行残留 |

门禁命令形态：

```bash
python .agents/scripts/check-skill-quality.py --path <skill-dir> --score --threshold 100
python .agents/scripts/check-links.py --path <skill-dir> --check-frontmatter-paths
```

## 4. 与 R1–R6 的映射

| 案例动作 | 对应步骤 |
|---|---|
| 收到「要写入 .agents/skills/」后停止按旧方案写入 | R1 冻结写入并复述 delta |
| 把 `.agents/skills` 解析到具体仓库目录 | R2 解析新根身份 |
| 重读主权区索引与同类 Skill frontmatter | R3/R4 新根查重与约定重读 |
| 发现登记面被并发修改，决定延后 | R4/R5 现状取证与延后 |
| 只在新根创建，未写用户级目录、未建联接 | 写入规则 |
| 在新根跑质量门、链接门、脚本与夹具 | R6 新根验收 |
| 报告写明未登记、未提交、未推送 | 报告模板 |

## 5. 证据边界

可以证明：

- 所有 `Write` 的落点都在 `.agents/skills/shared-branch-merge-push-gate/`。
- 质量门从 95 到 100、链接门 0 断链、脚本与夹具退出码，均有命令输出。
- 最终工作树只有该未跟踪目录，登记面未被本 Skill 改动。

不能证明或未执行：

- 换根后没有单独执行一次「旧根存在性 + 联接类型」检查；旧根未被写入的结论来自首轮目录枚举与最终报告，而非独立复验。
- 没有对旧根做 `rmdir` 或删除，因为从未创建。
- 没有做四处登记、TOML 镜像、用户级联接。
- 没有提交或推送。
- 首轮用户消息是「改目标根」而非「确认方案」，因此本案例只证明「改道后重新取证并执行」，不证明「批准后改道」的审批语义。

## 6. 复用要点

1. 换根后第一件事是重读新根约定，不是替换路径字符串。
2. 旧根取证要分存在性、联接类型、内容清单三层，`ls` 单看会误判。
3. 新根门禁必须在新根实跑，旧根结论不可继承。
4. 登记面有并发改动时，内容先行、登记延后，并在报告里写清延后原因。
5. 没有 TOML 镜像时不要写 `x-toml-ref`，否则链接门会把不存在的目标判为断链。
