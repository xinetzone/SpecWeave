# 案例：declared-consistency-fix 从 65 分到 100 分

来源会话 `0b5028ae-4c67-46da-8e99-0c2b68ae9c3a`。本案例只记录已核实的事实，用于说明分诊顺序与首败记录，不作为逐字模板。

## 背景

会话中先创建了 `declared-consistency-fix` Skill，用于修复仓库中「声明与事实不一致」的问题。初版放在用户级目录。用户随后提出两个纠正：

- 「为何没有放在 .agents/skills?」
- 「移入 .agents/skills 目录」

Skill 被移入项目级目录 `D:\spaces\SpecWeave\.agents\skills\declared-consistency-fix\` 后，再运行质量门，暴露出版本级元数据与正文结构不符合项目契约的问题。

## 首次基线

命令：

```bash
python .agents/scripts/check-skill-quality.py --path ".agents/skills/declared-consistency-fix" --verbose
```

结果：65 分，29 项通过、4 项 warn、1 项 error。

| 检查名 | 严重度 | 扣分 | 失败原因 |
|---|---|---|---|
| `safety.dry_run` | error | −15 | 有写操作，但没有预览/确认机制 |
| `why.explanations` | warn | −5 | 只有 `## Why` 标题，不是 `> **为什么？**` 引用块，且数量不足 |
| `safety.idempotent` | warn | −5 | 没有重复执行检查或收尾验证 |
| `safety.checklist` | warn | −5 | 缺少结构化安全检查清单 |
| `open_standard.body.gotchas` | warn | −5 | Gotchas 标题未编号 |

算式：100 − 15 − 5×4 = 65。这与实际输出一致。

## 分诊判断

1. 先修唯一的 error：`safety.dry_run` 是最大单项扣分，且写操作 Skill 的确认门本身有实际价值。
2. 再修四个结构性 warn：Why、幂等、清单、Gotchas 都属于「章节存在但形式不合格」，可以在同一轮补齐。
3. frontmatter 的推荐字段当时已经存在，因此没有出现额外的 5 分扣减；如果先入为主地补 frontmatter，会做无效功。

> 这一点可以推广：同样叫「65 分」，失败组合可能不同。必须以 `--verbose` 的实际失败项为准，不能从分数反推。

## 实际修复

- 把 `## Why` 标题改成引用块 `> **为什么？**`，并为关键规则补充设计意图，使 Why 数量达到 2 处以上。
- 在工作流中加入「先列出将要修改的声明 → 用户确认 → 执行」的预览步骤。
- 加入重复执行判断与收尾验证：目标已是期望状态时跳过，执行后重新检查声明与事实是否一致。
- 新增「安全检查清单（逐项确认）」，使用 `- [ ]` 列出真实风险项，数量不少于 5。
- 把 Gotchas 改成带编号的章节标题，并记录容易误判的规则细节。
- 保留原有有效内容，没有重写整个 Skill。

## 过程故障：Edit 零匹配

修复过程中有一次 Edit 失败：`old_string` 在文件中出现 0 次。原因是编辑前没有重新读取文件，待替换文本与磁盘内容已经不一致。

处理方式：

1. 重新 Read 目标文件，确认当前真实内容。
2. 用新的上下文重新构造 `old_string`。
3. 重试 Edit，成功后再继续。

这不是质量门规则问题，而是编辑流程问题。它被记录为 Gotchas 中的一条：编辑前先读文件，失败后重读，不要连续盲试。

## 最终结果

复跑命令：

```bash
python .agents/scripts/check-skill-quality.py --path ".agents/skills/declared-consistency-fix" --verbose
```

结果：

- 100 分。
- 34 项全部通过。
- 无 FAIL 项。
- 平均质量分 100/100。

最终通过项既包含修复后的 `safety.dry_run`、`why.explanations`、`safety.idempotent`、`safety.checklist`、`open_standard.body.gotchas`，也包含原有的 frontmatter、description、命名、开放标准结构与路径检查。

## 可复用结论

1. 65 分不是固定组合，先看失败项再排优先级。
2. error 优先于 warn；但四个结构性 warn 可以合并为一次修改。
3. 用户纠正「放在哪个目录」不是格式小事：用户级与项目级的元数据契约不同，位置错了，后续评分和加载行为都会变。
4. Edit 零匹配时重读文件，不要用更长的猜测字符串反复试。
5. 修复完成后必须复跑并记录首败原因；只报「已修好」无法让下一位维护者判断是否复发。

返回上级：[../SKILL.md](../SKILL.md)
