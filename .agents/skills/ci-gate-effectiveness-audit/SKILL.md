---
name: ci-gate-effectiveness-audit
description: 审计 CI 工作流里存在但不生效的门禁步骤，按 continue-on-error、allow_failure、|| true、|| exit 0 枚举抑制面，先取基线再单点解除抑制，并把失败分为环境伪失败与真实缺陷。当用户提到门禁形同虚设、步骤存在却不阻断、要删 continue-on-error、linkcheck 超时算不算真断链时，必须使用此技能。不用于归因既有门禁债务、跑全量 CI 或修断链。
version: 1.1.0
argument-hint: "<仓库根或 workflow 文件> [--expect-zero <pattern>]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/ci-gate-effectiveness-audit/**"
title: "CI 门禁有效性审计 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/ci-gate-effectiveness-audit/SKILL.toml"
---

# CI Gate Effectiveness Audit

门禁「存在」≠「生效」。工作流里写着 `xs docs linkcheck`，不等于这道门会阻断流水线——`continue-on-error: true` 把失败降级成一行日志，作业照样绿。本技能审计这类**存在但不生效**的步骤，并在解除抑制时先取基线、区分环境伪失败与真实缺陷。

## 1. 三种高代价误判

| 误判 | 表现 | 代价 |
|---|---|---|
| 把「有这一步」当「这道门生效」 | pipeline 绿就宣称链接已校验 | 门禁声明与门检对象错位，断链长期静默 |
| 删掉抑制项就宣称完成 | 没取基线的单行删除 | 无法证明该命令*本可以*失败，改动可能是摆设 |
| 把 `[timeout]` 登记为断链 | 基线里 4 条超时被写成「4 条断链」 | 把本机出站受限上报成文档缺陷，误导修复方向 |

## 2. 适用边界

用本技能：

- 想知道某道 CI 门禁是否真的能失败（步骤存在但不阻断作业）。
- 要解除 `continue-on-error` / `allow_failure`，且不想盲改——需要基线、伪失败分类、机械验收。
- 基线里出现 `[timeout]` / 超时类失败，需要判定是环境问题还是真实缺陷。

不用本技能：

| 任务 | 交给 |
|---|---|
| 门禁红了但不是我改的（既有债务归因） | `gate-baseline-delta-triage` |
| 按标准顺序跑十项 CI 检查 | `ci-check-cmd` |
| 文档结构/质量门只读自检 | `docs-as-product-cmd` |
| 产出复盘与 ACT 行动项 | `retrospective-cmd` |
| 修断链、转相对路径 | `link-check-cmd` |

## 3. 六步法

### S0 枚举抑制面（用脚本，不靠肉眼看）

```bash
python scripts/scan_gate_suppressions.py <仓库根> --json
```

按作用域分类后才谈得上结论：

| 分类 | 含义 | 是否算「门禁失效」 |
|---|---|---|
| `step-level-blocker` | `continue-on-error: true` / `allow_failure: true` | 是，这是唯一让失败不阻断的直接成因 |
| `body-level-tolerated` | 步骤体内的 `\|\| true`、`\|\| exit 0` | 否，尽力而为步骤里合法存在 |
| `needs-review` | 表达式取值、`if: always()` | 需人工判读 |
| `step-level-declared-false` | 显式 `false` | 否，仅登记 |

`if: always()` **不由自身抑制失败**——它只让步骤在先前失败后仍运行，失败的步骤照样让作业红。把它计入抑制族会产出假阳性。

> **为什么？** 混淆「重排执行」与「放行失败」会把一批本来正常的步骤误报成待删项：`if: always()` 只是把执行时机挪到前置步骤失败之后，并不吞掉自身失败；一旦归入抑制族，S4 就会去动不该动的东西，而真正的抑制项反而被淹没在噪声里。

### S1 回溯退出码链

删除抑制的价值取决于**底层命令本可以非零退出**。读命令实现，把链路走到底。实测链路：

```text
xs docs linkcheck → docs_linkcheck() → docs_build(builder="linkcheck")
  → subprocess.run(..., check=False) → returncode != 0 → raise typer.Exit(1)
```

若命令永远不会非零退出（例如内部就 `|| true` 吞掉了），删工作流的抑制项只是仪式。链上至少有一环能自证失败，才进入 S2。

### S2 取基线（必须用 CI 同款解释器）

```bash
cd <CI 所在仓库>
python -c "import sys, sphinx; print(sys.version.split()[0], 'sphinx', sphinx.__version__)"
set -o pipefail
python -m sphinx -b linkcheck doc doc/_build/linkcheck > linkcheck.log 2>&1
echo "LINKCHECK_EXIT=$?"
```

两个硬约束：

- **解释器与 CI 对齐**。实测：默认 shell 是 anaconda py3.13.9 + sphinx 8.2.3，而该仓库 CI 用 py314 + sphinx 9.1.0——先在默认环境跑出的结论不可比。
- **原始退出码来自重定向或 `pipefail`**。禁止 `... | tail` 之后再读 `$?`，那读到的是管道末端命令的退出码。

> **为什么？** 解释器不对齐就取不到可比基线：本机默认环境是 py3.13.9 + sphinx 8.2.3，而被审仓库 CI 用 py314 + sphinx 9.1.0，版本差异会改变 linkcheck 的判定与超时行为。在错误解释器上得到的「绿」或「红」都不代表 CI 里的真实门禁状态，据此删抑制项等于把结论建在错误前提上。

### S3 把失败分成环境伪失败与真实缺陷

Sphinx linkcheck 的两个产物语义不同：

| 产物 | 内容 | 用法 |
|---|---|---|
| `output.txt` | **只写非 working 项**（实测 4 行全是 `[timeout]`） | 按状态列统计，见下 |
| `output.json` | **JSONL**，每次检查一条记录（实测 12 条，含 `working`） | 逐行 `json.loads`；`json.load()` 会报 `Extra data` |

```bash
awk '{print $2}' doc/_build/linkcheck/output.txt | sort | uniq -c
```

`output.txt` 的行格式是 `文件:行号: [状态] URL: 详情`，所以第 2 列就是状态。对每条失败的 URL **独立探针连通性**，才敢判定它是不是断链：

```bash
curl -o /dev/null -w '%{http_code} %{time_total}s\n' --max-time 15 https://github.com/
# 000 15.0s → 本机出站受限，属环境伪失败
```

判定规则：探针返回 `000` 或超时 ⇒ 该失败是**本机出站受限**，不是断链；只有探针能连上而目标返回 4xx/5xx，才是真实缺陷。实测算例中 4 条 `[timeout]` 全部指向 github.com 且探针返回 `000` ⇒ 未发现真实断链。

### S4 单点解除

只删抑制项本身。**不要顺手**加 `linkcheck_timeout` / `linkcheck_retries`、不要把该检查从矩阵里搬走、不要清理同文件里的无关行——那些是另一项行动。改动面越大，验收越说不清。

> **为什么？** 多删一行配置、多搬一个矩阵项，都会让 S5 的「一文件一行」断言失效，也让「门禁现在会阻断」的因果链混入无关变量。残余风险应当在 S6 如实报告，而不是顺手扩大改动去兜底——报告风险与消除风险是两件事，混在一起会让本次改动无法归因。

### S5 机械验收（四重，缺一不可）

1. **模式限定计数**——只对「刚删掉的那个模式」计 0，**不要**对抑制族整体计 0：

```bash
python scripts/scan_gate_suppressions.py <仓库根> --expect-zero 'continue-on-error: true'
```

> **为什么？** 计数范围必须与删除范围一一对应：对抑制族整体计 0 会永不达标——`ci.yml` 里尽力而为的步骤合法保留着 `|| true`，一并计入就会让「验收永不过」与「改动永远不够」互相强化。把计数限定到刚删掉的那个模式，0 才等价于「该抑制项已不存在」。

2. **YAML 重解析断言**——确认结构未受损，而不只是「文件还能打开」：

```bash
python -c "
import yaml
d = yaml.safe_load(open('.github/workflows/ci.yml', encoding='utf-8'))
print('jobs:', list(d['jobs']))
print('steps:', len(d['jobs']['test']['steps']))
print('last:', d['jobs']['test']['steps'][-1])
"
```

断言目标步骤的 keys 只剩 `name` / `run`，且步骤总数与改前一致（实测：4 个 job、`test` 23 个步骤、末步 keys `['name','run']`）。

3. **改动作用域**：`git diff --stat` 必须是一文件一行。`1 file changed, 1 deletion(-)` 是正确形状。

4. **子模块分叉快照**：动子模块前先取，避免把别人的提交卷进来：

```bash
git -C <submodule> rev-list --left-right --count HEAD...origin/main
```

### S5.1 幂等与重入

整套流程可重复执行，无需标记文件：`scan_gate_suppressions.py` 只读，重复扫描不改动磁盘；抑制项已删除时 `--expect-zero` 命中 0 即返回 0，这个返回值本身就是「已完成」的判据。重入按探针决定起点——S0 无声明级抑制则跳过 S4，`--expect-zero` 已为 0 则不复跑 S5，仅在重新编辑工作流后才重跑四重验收。幂等性由「脚本只读 + 期望值为 0」共同保证，不依赖任何可变状态。

### S6 报告残余风险（但不扩大改动范围）

- 门禁现在会真实阻断，但默认 `linkcheck_timeout=30` + `linkcheck_retries=1`，runner 上一次瞬时网络抖动会让矩阵里 9 个组合同时变红。
- 同一检查在 matrix 的每个组合里重复执行（3 OS × 3 包管理器 = 9 次），单点失败被放大成 9 个红点。
- 未装 `actionlint` 就不算做过工作流静态校验——如实写「未做」，不要用 YAML 解析冒充 lint。

## 4. Gotchas（已实测陷阱与反直觉行为）

| 陷阱 | 现象 | 处理 |
|---|---|---|
| 验收 grep 计 0 却卡住 | `grep -c` 零匹配退出码为 1，`&&` 链被截断 | 用 `--expect-zero`，或 `n=$(grep -c ... \|\| true)` |
| 验收范围放太宽 | 对抑制族整体计 0 永不达标，合法 `\|\| true` 被误当待删项 | 计数限定到被删模式 |
| 取基线用错解释器 | 默认 py3.13.9 + sphinx 8.2.3 ≠ CI 的 py314 + sphinx 9.1.0 | 跑之前先打印版本 |
| `[timeout]` 记成断链 | 超时被当作断链上报 | 逐域名 `curl` 探针，`000` 即环境受限 |
| `output.json` 不是 JSON 文档 | `json.load()` 报 `Extra data: line 2 column 1` | 按 JSONL 逐行解析，或读 `output.txt` |
| Bash 工具工作目录跨调用持久 | `cd projects/xuanspace` 报 `No such file or directory` | 用绝对路径，或 `git -C <dir>` |
| 管道吞退出码 | `... \| head` 后 `$?` 是末端命令的 | `set -o pipefail`，或先重定向 |
| `if: always()` 被误判为抑制 | 它不阻断失败传播 | 归 `needs-review`，人工判读 |

## 5. 安全检查清单（交付前逐项确认）

- [ ] 每个抑制项都区分了作用域，`body-level-tolerated` 没有被当作待删对象？
- [ ] 删除前证明过底层命令*本可以*非零退出（退出码链走到底）？
- [ ] 基线跑在 CI 同款解释器上，原始退出码来自重定向或 `pipefail`？
- [ ] 每条失败都做过独立连通性探针，环境伪失败与真实缺陷已分开陈述？
- [ ] 验收计数限定到被删模式，且没有使用会截断 `&&` 链的 `grep -c` 写法？
- [ ] YAML 重解析断言了目标步骤的 keys 与步骤总数？
- [ ] `git diff --stat` 只有一文件一行？子模块分叉快照已取？
- [ ] 残余风险已如实报告，且没有为「兜住风险」而扩大本次改动范围？

## 6. 脚本契约

`scripts/scan_gate_suppressions.py`：仅标准库，Python 3.10+，只读。

```bash
python scripts/scan_gate_suppressions.py <root> [--paths FILE ...] [--expect-zero PATTERN] [--json]
```

- `<root>`：扫描根；默认递归发现 `**/.github/workflows/*.yml|yaml`（跳过 `.git`、`node_modules`、`.venv`、`build`、`_build`、`dist` 等）。
- `--paths`：显式指定工作流文件，覆盖自动发现。
- `--expect-zero`：统计含该**子串**的行数（区分大小写，`grep -F` 语义）；命中 0 退 0、非 0 退 1。用于替换会截断 `&&` 链的 `grep -c`。它**不跳过注释行**——与扫描模式相反，这是刻意对齐 `grep -c` 的语义，因为验收标准本来就是按 grep 写的；实测夹具里被注释掉的同类行会被计入。
- `--json`：输出机器可读结果。

退出码：`0` 无声明级抑制（或 `--expect-zero` 命中 0）；`1` 存在声明级抑制（或 `--expect-zero` 命中非 0）；`2` 参数错误、找不到工作流文件或文件不可读——**不猜**。

脚本是逐行扫描（跳过注释行），`step` 字段取最近的上方 `- name:`，属启发式；改动前以 YAML 重解析结果为准。

真实取证样例、可复跑命令与实测值见 [references/verified-case-act-001.md](references/verified-case-act-001.md)。

## 7. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.1.0 | 2026-10-24 | 质量门补救。首败 70/100、6 项 warn，根因全是结构/措辞缺失而非内容错误：补 description 强制措辞与触发场景、在 S0/S2/S4/S5 各补 1 处 `> **为什么？**`、新增 `S5.1 幂等与重入`、§4 改为带编号 Gotchas、§5 改为安全检查清单标题。复跑 `--score --threshold 100` → 100/100、34 项全过、退出码 0；链接门 0 断链。 |
| 1.0.0 | 2026-10-24 | 初始版本：S0 枚举抑制面 → S1 回溯退出码链 → S2 CI 同款解释器取基线 → S3 伪失败/真实缺陷分类 → S4 单点解除 → S5 四重机械验收 → S6 残余风险；配套 `scripts/scan_gate_suppressions.py`（只读扫描器）与 `references/verified-case-act-001.md`。 |