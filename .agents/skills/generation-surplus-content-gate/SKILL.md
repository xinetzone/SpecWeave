---
name: generation-surplus-content-gate
version: 1.0.0
description: "生成型产物（位图海报/插画/封面、报告、幻灯片、代码、数据导出）交付前的「多了什么」验收门，中文名「查多了什么」。必须使用此技能：当用户要求生成图片/海报/KV/封面后需要验收，或提到「图上怎么多了字」「有水印」「AI 自己加了标题」「多了没要求的东西」「生成结果和我说的不一样」「交付前检查一遍」「负向约束怎么写」「显式挂的技能跟任务不匹配」时。封装五步链：冻结预期清单 → 生成前负向约束 → 挂载语义核验 → 生成后双向验收（少了什么/多了什么）→ 差异如实汇报并写可校验记录；附带零依赖验收记录校验器。不用于位图生成本身（归 solo-graphic-generation）、不用于派生产物与源文档的一致性核验（归 artifact-consistency-audit）、不用于像素级修图（归 solo-image-edit）、不用于 UI 视觉打分（归 ui-screenshot-review）。"
argument-hint: "<产物类型> [产物路径] [--record <验收记录.json>]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/generation-surplus-content-gate/**"
title: "查多了什么 — 生成型产物双向验收门"
source: "来源会话为复古未来主义海报生成与七概念里程碑复盘，结论沉淀于同日复盘报告与模式文档查多了什么"
---

# generation-surplus-content-gate — 查多了什么

> **Hello World（最小用法）**：生成一张海报 → 生成前在 prompt 末尾加 `no text, no watermark, no logo, no corner label` → 出图后问自己一句「除了我要求的，画面里还多了什么？」→ 把答案写进交付说明。三步做完，本技能的核心价值就用上了。

## 1. Skill ID 与边界

`generation-surplus-content-gate`（中文名：**查多了什么**）。L1 门面 + L2 模式文档，方法论抽象见 [查多了什么](../../../docs/retrospective/patterns/methodology-patterns/ai-collaboration/surplus-content-acceptance-gate.md)。

**边界（必遵守）**：

| 不做 | 归谁 |
|---|---|
| 位图生成、尺寸确认、`.design` 画布登记 | [solo-graphic-generation](../solo-graphic-generation/SKILL.md) |
| 派生产物 ↔ 源文档的一致性比对 | [artifact-consistency-audit](../artifact-consistency-audit/SKILL.md) |
| 像素级修图 / 以图生图 | `solo-image-edit` |
| UI 页面的视觉评分与迭代 | [ui-screenshot-review](../ui-screenshot-review/SKILL.md) |
| 代码功能测试、CI 门禁本身 | `ci-check-cmd` |

> **为什么第一条边界要写得这么死？** 本技能萃取自一次「绕过专用生成 Skill 直接调通用工具」的实战。如果本技能顺手把生图也接管了，就会变成第二个半成品生成门面，反而让下个会话多一个可选入口、继续绕过专用 Skill。本技能只占「生成之后到交付之前」这一段。

## 2. 功能描述

把「验收」从一次主观打量，变成一张可复算的双向清单：

| 方向 | 问什么 | 常见手段 |
|---|---|---|
| 少了什么 | 正向清单逐项是否命中 | 对照冻结的预期清单 |
| **多了什么** | **清单之外是否出现新元素** | **负向清单逐项扫描 + 目视审 / 全文扫** |

产出一句话结论 + 一条结构化验收记录，后者由 [check_acceptance_record.py](scripts/check_acceptance_record.py) 机械校验。

> **为什么「多了什么」必须单独列一栏？** 验收者的注意力会被正向清单吸走：主体对不对、色调对不对、尺寸对不对，问完认知上就"看完了"。计划外内容不在这张清单里，因此不会被顺带看见。把它变成独立的一问，漏检就从注意力问题降级为流程问题。

## 3. 何时使用（触发词分级）

| 层级 | 触发词 | 动作 |
|---|---|---|
| **T2 强·直接执行** | 「图上怎么多了字」「有水印」「AI 自己加了标题」「多了没要求的东西」「生成结果和我说的不一样」「验收一下这张生成图」 | 直接进入五步链 |
| **T1 中·确认后执行** | 「交付前检查一遍」「负向约束怎么写」「生成前要加什么限制」「帮我看看有没有多余内容」 | 确认产物类型与清单后执行 |
| **T0 弱·仅提示** | 「检查一下」「看看效果」 | 先问「重点核要求项还是计划外内容」，再决定是否进入 |

**隐式触发**：用户要求生成海报／封面／KV／宣传页且提示词含体裁词时，即使没说「验收」，也应在生成前执行第 2 步（负向约束）并在交付时给出「多了什么」段落。

> **为什么体裁词要算触发信号？** 「海报」这类词会诱发模型补全标题、副标、上映信息与落款。本次实战中用户从未提文字，成图仍带 5 处标题文字与 1 处平台水印。体裁词本身就是风险信号，不能等用户来问。

## 4. 方案选择决策树

```
本次要验收的产物是什么？
├─ 有确定性源文档 / 上游清单可逐条比对？
│    └─ → 不适用本技能，转 artifact-consistency-audit（双向集合比对更可靠）
├─ 位图 / 海报 / 插画 / 封面（视觉产物）？
│    └─ → 方案 A：负向清单 + 目视门（§7.1）
├─ 文本 / 报告 / 幻灯片 / 代码 / 数据导出？
│    └─ → 方案 B：负向清单 + 全文扫描门（§7.2）
└─ 结构化输出且可被程序断言完全覆盖（JSON 字段、行数）？
     └─ → 直接写断言，不需要本技能的目视门；仍建议留一条验收记录
```

默认推荐：方案 A 与 B 共用同一张负向清单和同一份记录格式，仅第 4 步的检查通道不同。

## 5. 输入参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `artifact_type` | string | 是 | — | `bitmap` / `text` / `code` / `data` |
| `artifact_path` | string | 否 | — | 产物相对路径，供记录留痕；不写绝对路径 |
| `expected` | list | 是 | — | 从用户提示词冻结的正向清单 |
| `negative_constraints` | list | 是 | — | 生成前写入 prompt 的 `no-X` 清单 |
| `record` | string | 否 | — | 验收记录 JSON 路径，交给校验器检查 |
| `dry_run` | boolean | 否 | false | 只展示负向清单与记录预览，不落盘、不重新生成 |

## 6. 依赖与前置准备

- **零第三方依赖**：校验器仅用 Python 标准库（≥3.9）。
- **读能力**：位图需要能查看图片；文本/代码需要能读全文。无法查看时如实标注「目视门未执行」，不要以文件存在代替检查。
- **专用 Skill 核对**：生成前先看本仓是否已有该产物类型的专用生成门面（位图见 `solo-graphic-generation`），有则沿用其负向约束模板，不另编一套。
- **挂载语义核验**：本轮若被显式 `@` 了某个技能，先读它的「何时使用」条款，与本轮产出物类型比对。

> **为什么把「挂载语义核验」放在依赖里？** 同一个技能挂载，在「用户要一张图」时应判为不触发，在「用户要里程碑复盘」时才进入完整链路。挂载只说明技能进入上下文，不构成执行义务；判据是技能描述里的触发条件，不是 `@` 符号。

## 7. 核心步骤（5 步）

### S1 冻结预期清单

把用户提示词里的显式要求逐项列出（主体／动作／构图／色调／尺寸／文字有无）。清单在生成前定稿，生成后不得追改。

### S2 生成前写负向清单

按产物类型套用下表，把短语**逐字写进 prompt**（不是只在心里记着）：

| 产物类型 | 建议负向短语 |
|---|---|
| 位图 | `no text, no Chinese or English lettering, no title, no subtitle, no watermark, no logo, no creator tag, no corner label, no platform UI, no border` |
| 报告 / 幻灯片 | 无占位符、无示例数据、无模板页脚版本说明、无「待填写」 |
| 代码 | 无调试输出、无 TODO 注释、无示例密钥、无未使用导入、无被注释掉的旧实现 |
| 数据导出 | 无测试行、无内部标识列、无水印列、无导出工具说明行 |

若宿主工具提供显式开关（如 `--no-watermark` / `watermark: false`），同时打开，不把开关与提示词视为可互相替代。

### S3 挂载语义核验（第 0 步）

```
本轮显式挂载的技能 → 读其「何时使用」→ 与 artifact_type / 用户动词比对
├─ 匹配 → 按该技能完整流程执行，本技能作为其验收段
└─ 不匹配 → 书面声明「已读取 X，其触发条件不含本轮的 Y，按真实意图路由」，继续 S4
```

### S4 生成后双向验收

1. 先核「少了什么」：S1 清单逐项打勾。
2. **再单独问一次**：「产物里有没有清单之外的东西？」
   - 方案 A（位图）：目视审，按 S2 清单逐项扫描四角、边缘、中央、落款区。
   - 方案 B（文本/代码/数据）：全文扫描占位符、示例值、调试语句、页脚、附加列。
3. 逐条记录命中项：内容 + 位置 + 证据来源（目视审／全文扫／工具输出）。

> **为什么生成成功后还要再看一遍？** `status=completed`、退出码 0、尺寸与配色正确，都只覆盖「生成动作完成」。本次实战三项全部通过，图里仍带 5 处计划外文字。成功状态与内容合规是两个独立命题。

### S5 差异如实汇报并留痕

交付说明固定含「**多了什么**」段落：有命中项逐条列出；无命中项写「未发现计划外内容」并说明检查方式。同时写一条验收记录 JSON，跑校验器。

## 8. 验收记录格式与校验器

记录示例（字段含义见 [references/record-schema.md](references/record-schema.md)）：

```json
{
  "record_id": "gsg-20261106-001",
  "artifact": "generated-images/poster.png",
  "artifact_type": "bitmap",
  "expected": ["主体：古代中国仙女", "低角度仰拍", "橙色主调"],
  "negative_constraints": ["no text", "no watermark", "no logo"],
  "negative_constraints_applied_before_generation": true,
  "missing_items": [],
  "surplus_items": [
    {"item": "英文标题 SHENYI 等 5 处文字", "location": "左上及下方", "evidence": "目视审"}
  ],
  "check_method": "目视审 + 负向清单逐项",
  "conclusion": "surplus_found"
}
```

```bash
# 校验单条记录
python .agents/skills/generation-surplus-content-gate/scripts/check_acceptance_record.py <record.json>

# 内建正负样本自检（不读写外部文件）
python .agents/skills/generation-surplus-content-gate/scripts/check_acceptance_record.py --selftest
```

退出码契约：`0` 通过；`2` = `[CHECK-FAILED]` 契约检出；`3` = `[IO-ERROR]` 文件/JSON 解析失败。

> **为什么检出码不用 1？** Python 未捕获异常固定返回 1，恰是校验脚本最爱用的检出码。用 2/3 并配语义标记，才能把「确实检出了问题」与「脚本自己崩了」分开；只看退出码 1 会把 Traceback 当成正常检出。

## 9. 安全检查清单（逐项确认）

- [ ] 预期清单已在生成前冻结，生成后未追改
- [ ] 负向清单已逐字写入 prompt，或已引用专用 Skill 的模板
- [ ] 宿主侧的水印/文字开关（若有）已单独确认
- [ ] 已做挂载语义核验，不匹配时已书面声明跳过理由
- [ ] 已先核「少了什么」，再**单独**核「多了什么」
- [ ] 命中项逐条含内容、位置、证据来源
- [ ] 交付说明含「多了什么」段落（无发现也写明检查方式）
- [ ] 验收记录已通过 `check_acceptance_record.py`，退出码 0
- [ ] **dry-run／预览**：记录落盘前已在对话中展示预览；`dry_run=true` 时不写文件、不重新生成
- [ ] **幂等**：重复验收同一产物时复用同一 `record_id`，不产生第二份相互矛盾的记录
- [ ] 记录中不含绝对路径、凭据或会话原文
- [ ] 目视门无法执行时已如实标注「未执行」，未以文件存在代替检查

> **为什么写操作要有 dry-run？** 验收记录一旦落盘就成为后续复算与成熟度升级的依据，写错比不写更难纠正。先在对话里展示预览，是成本最低的纠错点。

## 10. 常见错误处理

| 标记 | 场景 | 处理 |
|---|---|---|
| `GSG_001` | `negative_constraints` 为空或未在生成前应用 | 退回 S2 补齐并重生成；只补记录不改做法视作未通过 |
| `GSG_002` | `conclusion=clean` 但 `surplus_items`/`missing_items` 非空 | 修正结论与列表一致，重跑校验器 |
| `GSG_003` | 记录含盘符绝对路径或本地文件协议前缀 | 改相对路径；路径只用于留痕，不用于访问 |
| `GSG_004` | 无法查看图片/读全文 | 保留记录但标注「目视门未执行」，交付说明中明示该限制 |
| `GSG_005` | 有确定性源文档可比 | 转 `artifact-consistency-audit`，本技能降级为辅助清单 |

完整字段说明见 [references/record-schema.md](references/record-schema.md)。

## 11. Gotchas（陷阱与反直觉行为）

1. **「成功」不等于「干净」**：`status=completed`、退出码 0、尺寸正确，三项全绿仍可能带 5 处计划外文字。
2. **没写文字 ≠ 禁止文字**：概率模型会按体裁补全。负向短语必须显式出现，不能靠「用户没要求」推断。
3. **转发提示词会丢约束**：把用户原话原样传给生图工具时，负向清单不会自动出现；转发不等于补齐。
4. **开关与提示词不能互相替代**：`--no-watermark` 管平台水印，`no text` 管画面文字，两者覆盖面不同。
5. **目视审的「有什么」不等于「多了什么」**：描述构图与配色的检查报告，可以完全不提左上角的标题组。
6. **自由文本备忘不构成留痕**：日志里写「模型会加字」无法被下一个会话机械复用，要写结构化记录。
7. **不要顺手接管生成**：见 §1 边界；接管会制造第二个绕过专用 Skill 的入口。
8. **中文标题不进 prompt**：`海报` 这类体裁词在中英提示词里都算体裁信号，风险不因语言切换而消失。
9. **锚点层级**：本 Skill 位于 `.agents/skills/<name>/`，指向 `docs/` 需 5 层 `..`；写浅一层会跳出仓库。
10. **验收记录不写绝对用户路径**：跨机器即失效，且可能把本机目录结构带进公开资产。

## 12. 关键参考速查

| 目标 | 入口 |
|---|---|
| 方法论抽象与成熟度 | [查多了什么（模式文档）](../../../docs/retrospective/patterns/methodology-patterns/ai-collaboration/surplus-content-acceptance-gate.md) |
| 来源复盘 | [AI 海报生成里程碑复盘](../../../docs/retrospective/reports/concepts/milestone/ai-poster-generation-retrospective-20261106.md) |
| 位图生成专用门面 | [solo-graphic-generation](../solo-graphic-generation/SKILL.md) |
| 验收记录字段 | [references/record-schema.md](references/record-schema.md) |
| 评测用例 | [evals/evals.json](evals/evals.json) |

## 13. Changelog

- **v1.0.0** (2026-11-06): 初始版本。萃取自复古未来主义海报生成里程碑复盘（模式「查多了什么」L1-draft）；含五步链、零依赖校验器、3 个真实评测用例。官方 benchmark 未运行，见复盘报告 §8。

---

> **验证状态**：质量门 `check-skill-quality.py --threshold 100`、校验器 `--selftest`、链接门实跑结果见复盘报告交付记录；评测循环（eval-viewer / aggregate_benchmark）本机不可用，未运行。
