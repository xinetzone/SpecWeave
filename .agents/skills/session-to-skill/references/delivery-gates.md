# 交付门与验证矩阵

本文件把「Skill 包写成什么样」和「凭什么说它可用」固化成可复跑的检查，避免用形容词代替证据。

## 目录

1. [包契约](#1-包契约)
2. [跨根查重与动作判定](#2-跨根查重与动作判定)
3. [优先复用](#3-优先复用)
4. [验证矩阵](#4-验证矩阵)
5. [evals.json 结构](#5-evalsjson-结构)
6. [交付报告模板](#6-交付报告模板)
7. [未验证项处理](#7-未验证项处理)
8. [检查清单](#8-检查清单)

## 1. 包契约

```text
<skill-dir>/
├── SKILL.md               # 必需：frontmatter + 触发与工作流
├── references/            # 可选：按需加载的长文档
├── scripts/               # 可选：仅放现有能力未覆盖的确定性逻辑
├── assets/                # 可选：输出用模板
└── evals/
    └── evals.json         # 建议：真实场景 + 可判定断言
```

### frontmatter

```yaml
---
name: <kebab-case，且与目录名一致>
description: "<做什么 + 何时触发 + 何时不用>"
metadata:
  version: "1.0.0"
  source: "<来源会话 ID 或可追溯出处>"
compatibility: "<运行时依赖，可选>"
---
```

约束：

- `description` 不超过 1024 字符，不含尖括号；把「何时用」全部放在这里，正文不承担触发。
- `name` 只用小写字母、数字和连字符，且与目录名完全一致。
- `source` 可放在顶层或 `metadata`，但必须存在，便于以后判断内容是否过期。
- 不要写绝对用户路径、凭据、会话原文或业务数据。

### 正文

- 控制在 500 行以内；超过 300 行的 reference 加目录。
- 参考文件用 Markdown 相对链接指向真实文件，链接检查器才能验证；只写内联代码路径会漏检。
- 命令块中的路径用占位符（`<skill-dir>`、`<spill-file>`），不写本机绝对路径。
- 先解释「为什么」，再给规则；只在真正需要硬约束时使用全大写。

### 文件卫生

- 不含 `__pycache__`、`.pyc`、临时夹具、测试输出。
- 不复制其他 Skill 的脚本；需要时链接到其真实位置或写明依赖。
- 不提交 `.temp/`、落盘会话原文或第三方私有材料。

## 2. 跨根查重与动作判定

每次 create 前至少查三个根，再在仓库内查登记面：

```bash
ls -d ~/.qoder/skills/<name> 2>/dev/null
ls -d ~/.agents/skills/<name> 2>/dev/null
ls -d <workspace>/.agents/skills/<name> 2>/dev/null
git grep -l "<name>" -- . ':!docs' 2>/dev/null
```

| 磁盘实况 | 真实缺口 | 动作 |
|---|---|---|
| 三个根都没有，登记面零命中 | 内容不存在 | 真 create，走本技能 |
| 主权区有权威副本，用户级没有 | 缺可见性或登记 | 补登记 + 目录联接，不复制内容 |
| 某根有实体副本 | 可能出现两份真相 | 先报告，再决定改联接或保留 |
| 权威副本存在但内容过时 | 内容需更新 | update：先读现状，保留有效规则 |
| 权威副本已完整且门禁通过 | 无缺口 | 不操作，报告现状 |

同名目录、目录联接、实体副本都算「存在」。`create` 遇到任何一种都必须停下，不允许先写再问。

## 3. 优先复用

写包前先确认这些能力是否已存在，避免制造重复实现：

| 能力 | 复用对象 | 用法 |
|---|---|---|
| 会话取证与证据矩阵 | `chat-session-evidence-audit` | 读用户轮次、失败、复跑；产出证据表 |
| 超限落盘切片 | `oversized-tool-output-slicing` | `extract_tool_result.js` 的 overview/messages/tool/grep |
| 推荐动作分诊 | `skill-recommendation-disk-triage` | 三根查重、create/update/补登记判定 |
| 包卫生与脚本验证 | `skill-bundled-script-validation` | `audit_skill_assets.py`；脚本正负向回归 |
| 登记与联接 | `native-skill-surface-registration` | 仅在用户明确要求入库时使用 |

判断标准：如果新脚本做的是上面任一能力的子集，就不写；只补真正的覆盖缺口，并在 SKILL.md 说明依赖。

## 4. 验证矩阵

按顺序执行，每条都记录命令与退出码。

### 4.1 包卫生门

```bash
AUDIT="$HOME/.qoder/skills/skill-bundled-script-validation/scripts/audit_skill_assets.py"
python "$AUDIT" "<skill-dir>" --strict; echo "exit=$?"
```

期望 `exit=0`。覆盖：

- SKILL.md 存在且 frontmatter 可解析；
- `name` 与目录一致且为 kebab-case；
- `description` 存在、长度合规、无尖括号；
- 文本 UTF-8 可解码；
- Markdown 相对链接可达；
- Python 文件内存编译通过；
- 无缓存产物；
- 敏感绝对路径告警。

不覆盖：

- `evals.json` 的结构与 id 唯一性；
- 内联代码中提到的资源路径是否存在。

后两项单独查。

### 4.2 frontmatter

```bash
python -c "import sys,yaml,pathlib; t=pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'); fm=yaml.safe_load(t.split('---',2)[1]); src=fm.get('source') or fm.get('metadata',{}).get('source'); print('name=',fm.get('name'),'desc_len=',len(fm.get('description','')),'source=',bool(src))" "<skill-dir>/SKILL.md"
```

期望输出 `name= <name>`、`desc_len` 不超过 1024、`source= True`。

### 4.3 evals.json

```bash
python -c "import sys,json; d=json.load(open(sys.argv[1],encoding='utf-8')); ids=[e['id'] for e in d['evals']]; assert d.get('skill_name'); assert len(ids)==len(set(ids)); assert all(e.get('prompt') and e.get('expected_output') for e in d['evals']); print('evals ok:',len(ids))" "<skill-dir>/evals/evals.json"
```

期望 `evals ok: N`。断言项可以为空，但场景提示与预期输出必须存在。

### 4.4 文档命令试跑

把 SKILL.md 和 references 中出现的命令逐条执行。至少覆盖：

- 一次抽取脚本调用（overview 或 messages）；
- 一次取证脚本调用（summary 或 failures）；
- 一次包卫生门；
- 一次真实 Skill 正样本对照。

无法执行的（缺工具、缺样本、需要联网）单列「未验证」，写明原因，不改文档假装能跑。

### 4.5 真实正样本对照

```bash
python "$AUDIT" "$HOME/.qoder/skills/<一个已存在的真实 Skill>" --strict; echo "exit=$?"
```

期望 `exit=0`。若真实样本失败，先判断是样本问题还是门禁误报；不要为了通过而修改别人的 Skill。

### 4.6 脚本类 Skill 的附加门

只有本次新增了 `scripts/` 时才执行：

```bash
python -m py_compile "<skill-dir>/scripts/"*.py
python -m unittest discover -s "<skill-dir>/scripts" -p "test_*.py" -v
ruff check "<skill-dir>/scripts"
```

并用 `skill-bundled-script-validation` 的负向夹具方法，断言精确错误数与退出码。没有脚本就明确写「不适用」，不要空跑。

### 4.7 回读

最后重新读取实际文件，核对：

- frontmatter 与目录名；
- 链接目标真实存在；
- 命令与参数和脚本契约一致；
- 没有 `__pycache__`、临时文件、绝对用户路径、会话原文。

## 5. evals.json 结构

```json
{
  "skill_name": "<name>",
  "evals": [
    {
      "id": 1,
      "prompt": "用户会真实说出的一段话",
      "expected_output": "可观察的预期结果",
      "files": [],
      "assertions": [
        "一条可机械判定的检查"
      ]
    }
  ]
}
```

写法要求：

- 场景来自真实会话或真实工作流，不写「请演示这个技能」。
- 至少 3 条，覆盖：正常创建、超限或失败回退、同名已存在的 update 路径。
- 断言使用可观察行为，例如「首个回复未写入目标目录」「报告了三根查重结果」「未提交」。
- 不把主观文风写成断言；主观部分留给人工评审。
- 本机若缺少 `eval-viewer` 与 `aggregate_benchmark`，只能做结构校验与人工试跑，报告里标注 benchmark 未运行。

## 6. 交付报告模板

```markdown
## Skill: <name>

- 动作: create / update / 补登记
- 来源: <session-id>
  - 工具证实: <条目>
  - 用户原话: <条目>
  - 助手自述（未独立证实）: <条目>
  - 未验证/矛盾: <条目>
- 产出: <文件与行数>
- 验证:
  - `<command>` → exit=<n> → <结果>
- 未验证: <项目与原因>
- 未执行: commit / push / 登记
```

要求：

- 每条「验证」都有命令和退出码，不能只写「已通过」。
- 「未验证」独立成段，不用「基本可用」掩盖。
- 报告与磁盘一致；报告说写了几个文件，就实际存在几个。

## 7. 未验证项处理

| 情况 | 处理 |
|---|---|
| 宿主缺少评测脚本 | 明说缺失，标注 benchmark 未运行；改用真实样本与命令验证 |
| 需要联网或外部账号 | 不执行，标注依赖与未覆盖范围 |
| 样本不足三个 | 说明样本数，不用夹具冒充真实样本 |
| 命令只在某个 shell 可用 | 记录 shell 与平台，标注其他平台未验证 |
| 结果依赖时间或环境 | 记录时间点、版本、平台 |

「未验证」不是失败，隐瞒未验证才是。

## 8. 检查清单

- [ ] `name` 与目录名一致，`description` 含触发与边界且不超过 1024 字符。
- [ ] `source` 存在且能追溯到会话或出处。
- [ ] 正文不超过 500 行；长 reference 有目录。
- [ ] references 用 Markdown 相对链接且全部可达。
- [ ] 三根查重已执行，同名存在时未覆盖。
- [ ] `audit_skill_assets.py --strict` 退出 0。
- [ ] `evals.json` 结构、id 唯一性、必填字段通过。
- [ ] 文档中的命令实际执行过，或有未验证说明。
- [ ] 至少一个真实 Skill 正样本通过同一门。
- [ ] 无 `__pycache__`、临时夹具、绝对用户路径、会话原文。
- [ ] 未提交、未推送、未做未授权登记。
