# 质量门工具契约与实测样例

本文件给出 `skill-quality-baseline-check` 的可复跑细节。命令以 `D:\spaces\SpecWeave` 为主权区根示例；其他机器以 `git rev-parse --show-toplevel` 的结果替换 `REPO`。

## 1. 变量与路径

```bash
REPO="$(git -C D:/spaces/SpecWeave rev-parse --show-toplevel)"
CHECKER="$REPO/.agents/scripts/check-skill-quality.py"
LINKS="$REPO/.agents/scripts/check-links.py"
SKILL_DIR="<目标 Skill 目录>"
```

要求 Python 3.10+：检查器入口会调用共享版本校验，低于 3.10 直接失败。

## 2. 两个验证器的契约差异

`skill-creator/scripts/quick_validate.py` 的允许字段（读源码确认，非运行结论）：

```text
name, description, license, allowed-tools, metadata, compatibility
```

它会把 `version`、`argument-hint`、`user-invocable`、`paths`、`title`、`source` 判为 unexpected key 并返回失败。仓库原生 Skill 默认带这些字段，因此：

- 通用客户端加载性检查：可以跑 `quick_validate.py`，但需预期上述字段会被拒绝
- 仓库质量分与失分项：只用 `check-skill-quality.py`

`check-skill-quality.py` 的字段契约：

| 类别 | 字段 | 未通过时的严重度 |
|---|---|---|
| 必需 | `name`、`description` | error（各 −15） |
| 推荐 | `version`、`argument-hint`、`user-invocable`、`paths` | warn（各 −5） |
| 其他 | `title`、`source`、`disable-model-invocation`、`metadata` | info（开放标准扩展字段提示，不扣分） |

## 3. 基线命令

```bash
python "$CHECKER" --path "$SKILL_DIR" --verbose
python "$CHECKER" --path "$SKILL_DIR" --score --threshold 100
```

- `--verbose`：逐项输出 PASS / WARN / FAIL、检查名与原始提示
- `--score`：只输出 `Skill名: 分数` 与 `平均: 分数`；任一 Skill 低于阈值时退出码 1
- `--threshold` 默认 70；验收统一显式传 100

只读基线不写文件，可在提案前直接对用户级目录执行。

## 4. 评分与对账

评分源码：`.agents/scripts/lib/check_skill_quality/scoring.py`

```text
score = 100
每个未通过 error：-15
每个未通过 warn：-5
每个未通过 info：-1
下限 0，上限 100
```

对账步骤：

1. 从 `--verbose` 抄出所有未通过项及 severity
2. 按权重求和，得到推算分数
3. 与 `--score` 的数字比较；不等则重读输出，找漏项
4. 只有「未通过」扣分，passed 的 warn 不扣

## 5. 常见失分项与修正映射

| 检查名 | 触发原因 | 最小修正 |
|---|---|---|
| `frontmatter.user-invocable` | 缺字段 | 补 `user-invocable: true` |
| `frontmatter.paths` | 缺字段 | 补 `paths` 列表 |
| `open_standard.body.gotchas` | 标题未编号 | 改为 `## N. Gotchas（陷阱与反直觉行为）` |
| `why.explanations` | `> **为什么` 引用块少于 2 处 | 补实质解释，不要用 `## Why` 标题充数 |
| `safety.dry_run` | 检测到写操作关键词但没有预览/预检/质量门等词 | 在工作流加入预览与确认门 |
| `safety.checklist` | 无安全检查清单或 `- [ ]` 少于 5 项 | 补结构化清单 |
| `description.mandatory_phrase` | 描述缺少强制触发措辞 | 补「必须使用」等措辞 |
| `description.trigger_context` | 描述缺少触发场景 | 补「当用户……」句式 |
| `file.length` | 正文超过 500 行 | 拆到 `references/` |
| `paths.no_file_url` | 正文出现 file URL 形式的绝对路径 | 改为相对路径或行内代码 |

Gotchas 的通过正则（源码 `checks_open_standard.py`）：

```text
^##\s+\d+\.\s*Gotchas|^##\s+\d+\.\s*(陷阱|反直觉|Gotchas)
```

即标题以 `## 数字. ` 开头，后接 Gotchas、陷阱或反直觉之一。

## 6. 链接门

```bash
python "$LINKS" --path "$SKILL_DIR" --check-frontmatter-paths
```

默认检查的 frontmatter 字段：`source`、`x-toml-ref`，并自动扩展以 `related_` 开头的字段。`paths` 不在默认列表内。

由此得到两条结论：

- 新增 `paths` 不会制造 frontmatter 路径假断链
- `paths` 的值是否正确，未经这道门验证

正文内联链接仍会被检查。指向不存在文件的链接会失败；指向目录且目录内无 README 也会失败。

## 7. 来源会话实测（`0f8d24ae-195c-407b-af91-6a8b26227212`）

对象：用户级 `~/.qoder/skills/user-skill-sovereign-migration`，更新前基线。

`--score` 输出（转录）：

```text
user-skill-sovereign-migration: 85
平均: 85
EXIT=0
```

`--verbose` 中的 3 个 WARN（转录）：

```text
[WARN]     [WARN] frontmatter.user-invocable: 建议字段 'user-invocable' 缺失（推荐添加以提高可用性）
[WARN]     [WARN] frontmatter.paths: 建议字段 'paths' 缺失（推荐添加以提高可用性）
[WARN]     [WARN] open_standard.body.gotchas: 建议包含Gotchas章节，列出容易踩的坑和反直觉行为（与"常见错误处理"不同，记录无错误码的隐性陷阱）
```

对账：100 − 5 × 3 = 85，构成与分数一致。

同一会话中，用户在方案批准后把目标根改为 `.agents/skills`；迁移后复验：

```text
user-skill-sovereign-migration: 100
平均: 100
QUALITY_EXIT=0
```

链接门结果：4 个 Markdown 文件、3 个本地引用全部存在、frontmatter 路径字段全部有效、0 断链、退出码 0。

注意：该会话的 85 与 100 分别对应不同根下的文件状态，不能当作同一次改动的前后对照；本技能只复用「失分构成可对账」「同命令复验」两条方法。

## 8. 报告模板

```text
目标：<skill-dir>
基线：<分数>（<n> 个 warn / <m> 个 error）
失分项：<检查名列表>
对账：100 − <扣分> = <分数>（一致 / 不一致）
预测：<拟改动> → <预期分数>（预期，未实测）
写入后：<实际分数>，退出码 <code>；链接门 <断链数> 断链，退出码 <code>
差异：<无 / 与预测不一致的原因>
```

## 9. 边界

- 本文件不替代 `skill-quality-gate-remediation` 的修复映射，也不替代 `skill-package-verification-gates` 的整包验收
- 检查器与评分公式只读；发现规则疑似误报时，先记录检查名与输入，不要改源码
- 基线输出只作取证，不据此自动改写 Skill
