---
title: "Skill 包验收门禁的实测案例"
source: "来源会话 767c40d5-6d6c-4bbe-9682-09774c17eaa2 的原始工具输出"
---

# Skill 包验收门禁的实测案例

本文件记录 `skill-package-verification-gates` 的证据来源：一次真实的 Skill 包交付，从 95 分到 100 分、链接门显式扫描、并发登记面判定。所有数字与命令均取自来源会话的工具输出，不是事后估算。

## 1. 被测对象

| 项目 | 内容 |
|---|---|
| Skill 目录 | `.agents/skills/shared-branch-merge-push-gate/` |
| 文件清单 | `SKILL.md`、`references/verified-case.md`、`evals/evals.json`、`evals/fixtures/`（共 4 个文本文件 + 1 个夹具目录） |
| 正文规模 | `SKILL.md` 200 行 |
| 结构要素 | 4 处 `> **为什么？**`、9 项安全检查清单、12 条 Gotchas |

## 2. 质量门：95 → 100

首次验收命令与结果：

```text
python .agents/scripts/check-skill-quality.py --path .agents/skills/shared-branch-merge-push-gate --score
shared-branch-merge-push-gate: 95
平均: 95
```

`--verbose` 输出中仅一项失败：

```text
[WARN] description.trigger_context
  description 缺少触发时机说明（建议包含"当用户..."/"提到..."）
```

34 项检查中 33 项通过、1 项 warn、0 项 error，按 `error −15 / warn −5 / info −1` 计分正好是 95。补上「当用户提到…时必须使用此技能」的触发句后复跑：

```text
python .agents/scripts/check-skill-quality.py --path .agents/skills/shared-branch-merge-push-gate --score --threshold 100
shared-branch-merge-push-gate: 100
平均: 100
QUALITY_EXIT=0
```

34 项全部 PASS，退出码 0。

**这组数据证明的**：95 分可以由单个 warn 造成；`--score` 只给分数，不指出失分项，诊断必须加 `--verbose` 或 `--json`。

**这组数据不能证明的**：默认阈值 70 下的「通过」与 100 分验收等价。两者不是一回事，验收命令必须显式写 `--threshold 100`。

## 3. 链接门：显式扫描 frontmatter

```text
python .agents/scripts/check-links.py --path .agents/skills/shared-branch-merge-push-gate --check-frontmatter-paths
扫描 4 个 Markdown 文件
broken_local: 0
broken_frontmatter: 0
LINKS_EXIT=0
```

同一目录若去掉 `--check-frontmatter-paths`，`broken_frontmatter` 不会进入统计，报告仍是 0。来源会话没有把这个默认值当成证据，而是显式加了参数。

**这组数据证明的**：该包内的相对链接与 `source` 回指均可解析。

**这组数据不能证明的**：整个仓库 0 断链。定向扫描只覆盖被测目录，仓库全集另有既有断链。

## 4. 字节级卫生

```text
UTF-8 without BOM: 4/4
BOM found: none
__pycache__: none
*.pyc: none
evals.json parse: ok (4 scenarios)
git status --porcelain -- .agents/skills/shared-branch-merge-push-gate
?? .agents/skills/shared-branch-merge-push-gate/
```

被测时该目录尚未 `git add`，所以状态是单个未跟踪目录，没有混入其他路径。

**这组数据证明的**：交付时无编码问题、无运行缓存、`evals.json` 可被标准解析器读取。

**这组数据不能证明的**：后续运行捆绑脚本不会生成 `__pycache__`。来源会话在跑完脚本后重新检查了一次，本流程把「跑完再查」写成固定步骤。

## 5. 捆绑脚本的退出码契约

该 Skill 内含 `scripts/merge_gate.py`，来源会话用真实样本与负向夹具实跑，记录到的退出码：

| 场景 | 退出码 |
|---|---|
| 预检全部通过 | 0 |
| 参数/用法错误 | 2 |
| 工作区脏且与上游路径相交 | 3 |
| 分歧度与授权基线不一致 | 4 |
| 存在 merge/rebase 中间态或索引锁 | 5 |
| 上游引用缺失或 fetch 失败 | 6 |

同时验证了两个容易误判的解析细节：传入重复路径参数时按双路径处理而非静默去重；路径前带空格时先裁剪再解析。

**这组数据证明的**：该脚本的退出码矩阵可被 CI 区分，失败不会伪装成成功。

**这组数据不能证明的**：`0/2/3/4/5/6` 适用于其他 Skill 的脚本。每个脚本的契约以它自己的 docstring 与 `argparse` 为准。

## 6. 并发登记面：只交付包体

写入前后对登记面取证，得到：

```text
 M .agents/capability-registry/02-skills.md
 M .agents/skills/CHANGELOG.md
 M .agents/skills/README.md
?? .meta/toml/.agents/skills/<other-skill>/
```

三条 `M` 是未暂存改动，`.meta/toml` 下另有其他会话创建的未跟踪目录。来源会话据此把交付范围收缩为「包体 + 验收证据」，没有写入任何登记面，也没有执行 `git add -A`。

**这组数据证明的**：登记面处于他人占用状态时，可以只交付包体并给出可复跑证据。

**这组数据不能证明的**：该 Skill 已完成入库登记。登记延后是明确结论，不是隐含完成。

## 7. 用户纠正：权威副本位置

首轮方案把目标目录写成了用户级 `~/.qoder/skills/<name>`。用户纠正：**仓库惯例权威副本通常放 `.agents/skills`**。方案随即改为在主权区创建，用户级路径只在获得明确授权后才用目录联接暴露，且不复制内容。

**这组数据证明的**：目标目录不能从推荐 JSON 直接继承，必须先按仓库惯例核对。

**这组数据不能证明的**：任何情况下都应创建用户级联接。联接是独立授权项，登记被延后时它同样可以延后。

## 8. 复跑清单

想复现上述结论，按顺序执行：

```bash
# 1) 包体与缓存
find .agents/skills/<name> -type f -printf '%P\n'
# 2) 质量门（真实退出码，不过管道）
python .agents/scripts/check-skill-quality.py --path .agents/skills/<name> --score --threshold 100
echo "QUALITY_EXIT=$?"
# 3) 链接门（必须显式扫 frontmatter）
python .agents/scripts/check-links.py --path .agents/skills/<name> --check-frontmatter-paths
echo "LINKS_EXIT=$?"
# 4) 登记面状态
git status --porcelain=v1 -- .agents/skills/README.md .agents/skills/CHANGELOG.md .agents/capability-registry/02-skills.md .meta/toml
```

复跑时若数字不同，以本次磁盘实测为准；本文件记录的是特定时点的证据，不是当前状态的保证。
