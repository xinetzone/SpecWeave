---
name: ci-run-failure-triage
version: 1.0.0
title: "远程 CI 失败取证与转绿闭环"
description: "GitHub Actions 运行/作业失败（CI 红了、跑绿）的取证与闭环修复：从 run/job URL 或一句『CI 挂了』出发，用 gh 取失败 job 与失败日志、在落盘日志里 grep 出真实红项、本地复现同一门禁、区分真失败与本机环境伪失败、只修内容而不削弱门禁、推送后观察新 run 转绿才宣称解决。当用户给出 actions/runs/.../job/... 链接，或说『帮我把 CI 修好/跑绿』『这个 job 为什么失败』『流水线红了』『Actions 报错』『提交后 CI 挂了』『本地绿了远端还红』时，必须使用此技能。不要靠翻网页日志或读 run 标题猜测——本技能封装失败定位、伪失败甄别与转绿验收三段纪律。"
argument-hint: "<run 或 job URL | owner/repo + run_id> [--dry-run] [--no-push]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/ci-run-failure-triage/**"
source: "执行层投影：源自 2026-11-11 awesome-flexloop/awesome-okf run 42946656373（job 130280975401）失败闭环——新增 bundle 后 README/doc/index 规模数字漂移，由 check-asset-baseline.py 拦截并修复至转绿。计数同步的修复侧归 shared-index-atomic-extension 与 declared-consistency-fix；本技能只负责远程取证、伪失败甄别与转绿验收，不新增模式库条目。跨项目验证未完成"
x-toml-ref: "../../../.meta/toml/.agents/skills/ci-run-failure-triage/SKILL.toml"
---

# 远程 CI 失败取证与转绿闭环

> **边界声明（先读这段）**：本技能只负责「远端红 → 定位 → 复现 → 分诊 → 修 → 转绿」这条链路。
> 红项若是**内容接线类**（toctree 未登记、计数未同步、规模数字漂移），修复动作转
> [shared-index-atomic-extension](../shared-index-atomic-extension/SKILL.md)；
> 若是**跨文件声明漂移**（许可证/版本号/路径），转
> [declared-consistency-fix](../declared-consistency-fix/SKILL.md)；
> 若是**门禁被抑制**（`continue-on-error` / `|| true`），转
> [ci-gate-effectiveness-audit](../ci-gate-effectiveness-audit/SKILL.md)。

## 1. Skill ID

`ci-run-failure-triage`

## 2. 这个技能解决什么

CI 失败的处置成本几乎全部花在**定位**，不在修改。三类典型失效：

| 失效 | 症状 | 后果 |
|---|---|---|
| 只看 run 标题 | 读「failure」就猜是构建或依赖问题 | 改错地方，一轮返工后才回到真正的红项 |
| 把本地红当远端红 | 本地 `pytest` 全量红，据此改代码或依赖 | 修了 CI 根本不执行的测试，远端仍是红的 |
| 本地绿即宣称解决 | 复跑通过就回复「已修复」 | 远端未推送或推送后仍红，信任崩塌 |

> **为什么必须先把「红项的原文」取到手上？** 门禁输出通常是一句可机械判读的话（如 `✗ 校验失败：2 项` 加两条具名条目）。这句话决定了后面每一步：修什么文件、复跑哪个脚本、要不要改门禁。跳过取原文，等于用猜测替代判据。

> **为什么「本地绿」永远不能替代「远端绿」？** 远端有本地不存在的变量：检出方式（LF 而非 CRLF）、未安装的依赖、只跑子集的测试选择器、以及 workflow 的 `on.paths` 触发条件。本地通过只证明「本机这套命令通过」，不证明「这个 job 会通过」。

## 3. 何时使用本技能

当用户出现以下任一意图时必须使用：

- 给出 `https://github.com/<owner>/<repo>/actions/runs/<run_id>/job/<job_id>` 链接并要求解决；
- 说「CI 挂了」「流水线红了」「Actions 失败」「帮我把 CI 跑绿」「这个 job 为什么失败」；
- 说「提交后远端报错」「本地过了远端没过」「推送之后红的」；
- 需要判断某个失败是本次改动引入还是既有存量。

**不适用**：本地提交前自检（用 `ci-check-cmd`）；门禁被抑制的审计（用 `ci-gate-effectiveness-audit`）；纯内容接线修复（见上方边界声明）；没有远端 CI 的纯本地脚本调试。

## 4. 方案选择（决策树）

```
用户给了什么输入？
├─ 完整的 run/job URL → 直接用 §5 步1（省一次列表查询）
├─ 只有 owner/repo + 「最近 CI 红了」 → gh run list --limit 5 找最近 failure
├─ 只有仓库路径 → 先读 .github/workflows/*.yml 认清「哪些 job 会跑、跑哪些脚本」
└─ 只有一句「本地红」 → 不走远程取证，直接本地复现（§5 步3）
红项的性质是什么？
├─ 内容/声明类（计数、链接、编码、标题层级、frontmatter） → 修内容，不动门禁
├─ 门禁误判（正则漏写法、平台差异） → 按 TDD 改门禁：先加自检探针证明能命中，再放行
├─ 门禁被抑制（continue-on-error / || true） → 转 ci-gate-effectiveness-audit
└─ 环境/依赖缺失（本机缺包、缺工具） → 判定为伪失败，不改仓库
```

**推送是独立授权**：`--no-push` 表示只修到本地全绿并交付 diff；默认在取得用户明确同意后才推送。

> **为什么推送要单独取得同意？** 推送到共享分支会改变他人可见的历史并触发新一轮 CI。修复和推送是两次不同的决定：前者影响本机工作树，后者影响远端所有人。

## 5. 六步工作流

| 步 | 动作 | 完成判据 |
|---|---|---|
| 1 | **取失败 job**：列出本 run 全部 job 的 conclusion | 知道哪个 job 红、哪些是 skipped |
| 2 | **取红项原文**：取失败日志 → 落盘 → grep 出 `✗`/`::error`/`exit code` | 拿到具体条目文字，不是「有个错」 |
| 3 | **本地复现**：在仓库根单独跑同一个门禁脚本 | 本地退出码与报错条目与远端一致 |
| 4 | **分诊**：按 §7 判定真失败 / 伪失败 / 门禁缺陷 | 判定有证据（命令 + 输出），不靠印象 |
| 5 | **修复并复跑全部门禁**：修内容；若门禁缺陷则先补自检探针 | 本地全部 gate 退出码 0，含各自 `--self-test` |
| 6 | **推送并按新 run 验收**：观察新 run 的同一 job 变 success | 记录新 run id 与 job conclusion |

**步骤 6：转绿验收**——推送后不得直接宣称解决，必须轮询新 run 直到失败 job 的 conclusion 变为 `success`；若新 run 仍红，回到步骤 2 重取日志，而不是在旧日志上继续猜测。

**dry-run 语义**：步骤 1-2 与步骤 4 全程只读；步骤 5 的写盘前先给出「要改的文件 + 旧值 → 新值」清单预览；步骤 6 的推送需显式同意。

> **为什么第 3 步的判据是「退出码与条目一致」而不是「也都失败了」？** 同一个脚本在不同环境可能因不同原因失败（本机 CRLF 让字节基线残差非零，CI 是 LF 所以为 0）。条目文字一致才证明是同一个缺陷。

## 6. 取证命令

完整命令表（含 Windows PowerShell 与 bash 差异、超限落盘后的切片方式）见
[取证命令手册](references/triage-recipes.md)。

最小集：

```bash
# 1. 本 run 的 job 结论
gh run view <run_id> --repo <owner>/<repo> --json status,conclusion,jobs \
  --jq '{status,conclusion,jobs:[.jobs[]|{name,conclusion}]}'

# 2. 失败日志（输出可能很大，会落盘）
gh run view --repo <owner>/<repo> --job <job_id> --log-failed
#    → 落盘路径出现在 "<persisted-output>" 提示中，用 Grep 定点读，不要全文读

# 3. 在落盘日志里定位红项
#    pattern: (✗|::error|exit code|FAIL|Traceback)

# 4. 本地复现同一门禁（在仓库根）
python scripts/<gate>.py

# 5. 推送后验收
gh run list --repo <owner>/<repo> --limit 2 --json databaseId,headSha,status,conclusion
```

## 7. 分诊表

| 类别 | 判据 | 处置 |
|---|---|---|
| **真失败·内容类** | 本地复现同一条目，且文件内容确实与声明不符 | 修内容；门禁不动 |
| **真失败·门禁缺陷** | 门禁把合法写法判错（正则漏写法、跨平台路径） | 先加 `--self-test` 探针证明能命中，再放行；规则与夹具同批改 |
| **伪失败·环境差异** | 本机缺依赖/工具导致红，且该脚本不在失败 job 的 steps 里 | 记录「非本次范围」，不改仓库 |
| **伪失败·测试选择器** | 本地跑了全量测试，CI 只跑其中单个文件 | 以 workflow 的 `run:` 行与 `on.paths` 为准 |
| **存量红** | 该条目在本次改动前的提交里同样存在 | 如实记录「未恶化」，不宣称「已修复」 |
| **抑制型门禁** | 步骤存在但被 `continue-on-error` 等吞掉 | 转 `ci-gate-effectiveness-audit` |

> **为什么「存量红」必须单列？** 把存量红写成「已修复」，会让下一次同类失败失去可信基线；把存量红当成本次引入去改，则会污染一个本无问题的提交。

## 8. 安全检查清单（逐项确认）

- [ ] 已确认失败 job 名称与 conclusion，且区分了 skipped 的 job
- [ ] 已取到红项的具体条目文字（不是「有个错」这类转述）
- [ ] 已确认本地复现的退出码与条目与远端一致
- [ ] 已读过对应 workflow 的 `on:` 与 `run:`，确认该脚本确实在失败 job 中执行
- [ ] 本地出现的其他红项已判定为伪失败或存量红，并写明证据
- [ ] 修复范围只覆盖红项，未顺手重构无关文件
- [ ] 写盘前已给出「文件 + 旧值 → 新值」清单预览
- [ ] 复跑全部 gate 及各自 `--self-test`，并记录精确退出码
- [ ] 未通过放宽/删除门禁规则来换取转绿
- [ ] 推送已取得明确同意，且推送后已记录新 run id
- [ ] 新 run 的失败 job 已变为 success，或如实记录仍红的原因

## 9. Gotchas（陷阱与反直觉行为）

1. **`--log-failed` 输出会超限落盘**：本次 91.0 KB / 534 行即触发落盘。落盘后必须用 Grep 定点读，不要对落盘文件再发一次全文 Read。
2. **step 名可能是 `UNKNOWN STEP`**：日志前缀里的步骤名不可靠，定位靠正文的 `✗` / `::error` / `Process completed with exit code`。
3. **本地全量测试红 ≠ CI 红**：本次 `pytest tests/unit` 因本机缺 `sphinx_tippy` 有 1 项失败，而失败 job 只执行 `test_no_future_annotations.py`。先读 workflow 再下结论。
4. **`on.paths` 会让某些 workflow 根本不触发**：本次 `gates-selftest.yml` 只在 `scripts/**` 等路径变更时跑，文档改动不会触发它的 self-test。别把「没跑」当「跑了且通过」。
5. **Windows PowerShell 没有 `head -c`**：`gh ... | head -c 3000` 会直接报「未识别 cmdlet」并使整条命令失败，后续管道一并中止。
6. **多行提交信息要独占行的 here-string**：PowerShell 的 `@'` 与 `'@` 必须各自独占一行；写成 `-m "@'` 会静默失败，且同一批次里的 `git add` 可能根本没执行。
7. **失败命令之后的命令可能没跑**：一旦某条命令以非零退出，后续 `git add` / `git commit` 未必执行。提交前用 `git status --short` 复核暂存态，别假设已暂存。
8. **管道拿到的不是脚本退出码**：`python gate.py | tail` 的退出码是 `tail` 的。要判定门禁真实结果，单独设取退出码。
9. **CRLF 工作区会让字节类基线残差非零**：本次本地残差在归一后为 `+0` 才成立；若见到非零残差，先确认归一维度，而不是直接改字节数字。
10. **门禁已存在时不要新增门禁**：预防措施应写「已有门禁覆盖」，并指出是哪一条检查拦下的；重复加一层只会增加维护面。

## 10. 验证命令与预期结果

```bash
cd <subproject 或仓库根>
# 逐个跑失败 job 中出现的每一个门禁，而不是只跑红的那一个
python scripts/<gate-1>.py
python scripts/<gate-2>.py
python scripts/<gate-1>.py --self-test        # 其余门禁同参
python -m pytest <失败 job 实际选择的测试文件> -q

cd d:\spaces\SpecWeave
python .agents/scripts/check-skill-quality.py --path .agents/skills/ci-run-failure-triage --score --threshold 100
python .agents/scripts/check-links.py --path .agents/skills/ci-run-failure-triage --check-frontmatter-paths
```

预期：所有门禁退出码 0；`--self-test` 退出码 0；失败 job 选择的测试全绿；质量门 100 分且退出码 0；链接门 0 断链。
**已知限制**：无人值守轮询新 run 的时长上限由 CI 排队时间决定，排队过久时如实记录「已推送、待观察」，不写成「已修复」。

## 11. 真实案例

2026-11-11，`awesome-flexloop/awesome-okf` 的 run `42946656373`（job `130280975401`）在
`Quality gates (utf8 / toctrees / bundles / assetbaseline / redline / actionlint)` 失败。
完整证据链、六处数字漂移与最终转绿记录见
[案例记录](references/case-20261111.md)。

## 12. 参考

- [取证命令手册](references/triage-recipes.md)
- [案例记录](references/case-20261111.md)
- [共享索引下的原子化增量拓展](../shared-index-atomic-extension/SKILL.md)
- [声明一致性修复](../declared-consistency-fix/SKILL.md)
- [CI 综合检查](../ci-check-cmd/SKILL.md)
- [超限工具输出切片取证](../oversized-tool-output-slicing/SKILL.md)

## 13. Changelog

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-11-11 | 首次萃取：六步工作流、六类分诊表、取证命令手册、10 条 Gotchas、2026-11-11 awesome-okf 转绿案例 |
