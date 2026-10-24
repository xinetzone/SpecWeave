---
name: skill-package-verification-gates
version: 1.0.0
description: "在 .agents/skills 写入或修改 Skill 包后执行可复跑的验收链：质量门冲到 100/100、链接门显式加 --check-frontmatter-paths、检查 UTF-8/BOM 与 __pycache__、解析 evals JSON，并在登记面被其他会话占用时只交付包体。当用户说「Skill 写完了可以交付吗」「质量门 95 分」「链接门过了吗」「登记延后」「验证 Skill 包」「验收这个 Skill」，或准备宣称已创建/已更新/已验证时，必须使用此技能。不用于四处登记本身（用 native-skill-surface-registration）、脚本夹具深度测试（用 skill-bundled-script-validation）或从零创建 Skill（用 skill-creator）。"
argument-hint: "<skill-dir> [--registration-pending]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/**"
source: "来源会话 767c40d5-6d6c-4bbe-9682-09774c17eaa2 的 Skill 包验收实测：质量门 95 到 100、链接门 0 断链、UTF-8 无 BOM、并发登记面已暂存时只交付包体"
title: "Skill 包验收门禁"
---

# Skill 包验收门禁

写进 `.agents/skills/` 的 Skill 包，只有在**包体完整、质量门满分、链接门显式扫过 frontmatter、脚本契约被实跑**之后才算可交付。登记面是否可写是另一个独立判断：它可能正被其他会话修改，此时正确动作是交付包体并标注登记延后，而不是把别人的暂存内容一起写进去。

## 1. Why：三种高代价失败

1. **链接门假绿**：不加 `--check-frontmatter-paths` 时，`broken_frontmatter` 恒为 0。`source`、`x-toml-ref`、`related_*` 已断链，报告仍显示“所有链接均有效”。
2. **退出码被管道吞掉**：`python check-skill-quality.py ... | tail` 返回的是 `tail` 的退出码。95 分也能显示成成功，验收结论因此失真。
3. **并发登记面混写**：README、CHANGELOG、registry 已被另一会话修改时继续写入，会把别人的行和计数混进本次交付，事后无法按路径区分归属。

> **为什么？** 验收门禁的价值不在“跑过命令”，而在“每条结论都有未被管道、默认值和并发写入篡改过的原始证据”。

> **为什么？** 登记面是共享索引，包体是本次会话的私有产物。两者写入风险不同，必须分开决策。

> **为什么？** 用户批准的是“交付这个 Skill 包”，不是“顺便修改所有索引文件”。前提变化时要回报，而不是扩大写入范围。

## 2. 适用边界

| 场景 | 使用本技能 | 交给谁 |
|---|---|---|
| Skill 包写完后按门验收 | 是 | — |
| 判断登记面被占用时是否只交付包体 | 是 | — |
| 核对捆绑脚本的退出码契约 | 是（编排与记录） | 深度夹具用 `skill-bundled-script-validation` |
| 四处登记、计数同步、Junction | 否 | `native-skill-surface-registration` |
| 质量门掉分后的实质修复 | 否 | `skill-quality-gate-remediation` |
| 从零设计 Skill | 否 | `skill-creator` |

## 3. G0：预览与确认（dry-run）

输入先写死，不要边跑边猜：

| 输入 | 取值 |
|---|---|
| `SKILL_DIR` | 被测 Skill 目录，必须明确 |
| 仓库根 | 默认当前工作区，命令相对仓库根执行 |
| 动作 | create / update |
| 登记授权 | 未授权 / 已授权 |

步骤1：确认目标目录与动作。`SKILL.md` 已存在时，只有用户明确要求 update 才继续；否则停止并报告已存在路径，不覆盖、不另建同名副本。

步骤2：检查登记面是否被占用。在写入任何登记文件前执行：

```bash
git status --porcelain=v1 -- .agents/skills/README.md .agents/skills/CHANGELOG.md .agents/capability-registry/02-skills.md .meta/toml
```

步骤3：输出预览并取得用户确认。预览至少包含：拟写入文件列表、是否新增脚本、是否触碰登记面、预计验收命令。未确认不写入。

> **为什么？** 这里的 dry-run 不是可选礼貌，而是把“写什么、写到哪里、是否碰共享面”提前变成可审阅的对象；一旦落盘后再解释，成本已经从预览变成回滚。

## 4. G1：包体完整性

步骤4：验证文件树、frontmatter 与引用。

```bash
find "$SKILL_DIR" -type f -printf '%P\n'
python .agents/scripts/check-links.py --path "$SKILL_DIR" --check-frontmatter-paths
```

逐项确认：

- `name` 与目录名完全一致，kebab-case，长度不超过 64。
- frontmatter 可解析，`description` 非空且包含触发场景。
- 正文引用的 `references/`、`scripts/`、`evals/` 文件真实存在。
- 无 `__pycache__`、`.pyc`、临时目录、`file:///` 或盘符绝对路径。
- 所有文本文件为 UTF-8 且无 BOM。
- `evals/*.json` 能被标准 JSON 解析器读取。

字节级卫生检查：

```bash
python - "$SKILL_DIR" <<'PY'
import pathlib, sys
root = pathlib.Path(sys.argv[1])
for p in sorted(root.rglob("*")):
    if not p.is_file():
        continue
    b = p.read_bytes()
    try:
        b.decode("utf-8")
    except UnicodeDecodeError as e:
        print("NOT_UTF8", p, e); continue
    if b.startswith(b"\xef\xbb\xbf"):
        print("BOM", p)
print("CACHE_DIRS", [str(p) for p in root.rglob("__pycache__")])
PY
```

> **为什么？** BOM 会让 frontmatter 的首个键带上不可见字节，解析器可能把 `name` 读成空值；`__pycache__` 则是运行夹具后最常见的残留，必须在交付前清掉。

## 5. G2：质量门

步骤5：验证质量门达到满分。

```bash
python .agents/scripts/check-skill-quality.py --path "$SKILL_DIR" --score --threshold 100
echo "QUALITY_EXIT=$?"
```

期望：分数 `100`、34 项全部通过、退出码 `0`。若必须经过管道，使用 `set -o pipefail` 并以 `${PIPESTATUS[0]}` 取真实退出码：

```bash
set -o pipefail
python .agents/scripts/check-skill-quality.py --path "$SKILL_DIR" --score --threshold 100 | tail -3
echo "REAL_EXIT=${PIPESTATUS[0]}"
```

低于 100 分时，先用 `--json` 或 `--verbose` 看失分项，再决定修复：

| 失分项 | 常见原因 | 处理 |
|---|---|---|
| `description.trigger_context` | description 缺“当用户/提到”等触发场景 | 补触发句后复跑 |
| `description.mandatory_phrase` | 缺“必须使用此技能”等强制措辞 | 补强制措辞后复跑 |
| `why.explanations` | 少于 2 个 `> **为什么` 解释 | 给关键决策补 Why |
| `safety.dry_run` | 检测到写操作但无预览 | 补 dry-run / 预览 / 预检 |
| `safety.checklist` | 无安全检查清单或少于 5 项 | 补逐项确认清单 |
| `open_standard.body.gotchas` | 无 `## N. Gotchas` 章节 | 补陷阱与反直觉行为 |
| `frontmatter.*` 推荐字段 | 缺 version/argument-hint/user-invocable/paths | 按仓库格式补齐 |

修复后回到步骤5复跑，不把 `--threshold 70` 的“通过”当成验收。

> **为什么？** 默认阈值是 70；不加 `--threshold 100` 时，95 分也会退出 0。验收口径必须写死在命令里，而不是依赖默认值。

## 6. G3：链接门

步骤6：验证本地链接与 frontmatter 路径字段。

```bash
python .agents/scripts/check-links.py --path "$SKILL_DIR" --check-frontmatter-paths
echo "LINKS_EXIT=$?"
```

期望：`broken_local=0`、`broken_frontmatter=0`、退出码 `0`。若同时改了登记面，扫描范围改为：

```bash
python .agents/scripts/check-links.py --paths .agents/skills .agents/capability-registry --check-frontmatter-paths
```

- 不加 `--check-frontmatter-paths` 时，frontmatter 字段根本不会进入检查，报告里的 0 不能作为证据。
- `source` 的路径型取值按文件所在目录解析。用户级 Skill 若写仓库相对路径，会指向不存在的位置；改成说明性文字或省略。
- 指向目录的 Markdown 链接会被判失败，应指向目录内的具体文件。

> **为什么？** `broken_local` 与 `broken_frontmatter` 是两套规则。只看前者，会把 `x-toml-ref` 指向空处这种失败漏掉。

## 7. G4：捆绑脚本（条件触发）

只有 `scripts/` 存在时才执行本节；不存在时在报告里写“不适用”。

步骤7：验证脚本契约与退出码。

```bash
python "$SKILL_DIR/scripts/<script>.py" --help
python "$SKILL_DIR/scripts/<script>.py" <只读样本>
echo "SCRIPT_EXIT=$?"
```

- 先读脚本 docstring 与 `argparse`，把调用方式、参数、退出码、副作用写成契约。
- 在临时夹具中逐类注入缺陷，断言**精确**退出码与报错数；不要只看“有输出”。
- 退出码矩阵以被测脚本自己的声明为准。例如 `merge_gate.py` 的 `0/2/3/4/5/6` 已在真实案例中验证，但不要把这个矩阵套到所有脚本。
- 正向样本至少三个（含一个 holdout），负向夹具保留相对路径与兄弟依赖；未注入缺陷的镜像必须先通过。
- 深度夹具方法、假失败识别与 `__pycache__` 清理，移交 `skill-bundled-script-validation`。
- 跑完脚本后重做 G1 的缓存检查。

> **为什么？** 脚本的“能看到输出”与“CI 能收到失败”是两件事。退出码不精确，门禁就只是打印日志。

## 8. G5：登记面并发判定

步骤8：确认登记面归属与交付范围。

| 检查结果 | 动作 |
|---|---|
| README / CHANGELOG / registry 有未暂存或已暂存改动 | 只交付包体，登记延后；报告列出被占用路径与 `git status` 原文 |
| 登记面干净，且用户明确要求登记 | 移交 `native-skill-surface-registration` 做四处登记与计数同步 |
| 登记面干净，但用户未要求登记 | 只交付包体，报告写明“未登记” |
| `.meta/toml` 有未跟踪目录 | 视为其他会话在建镜像，不删除、不覆盖、不顺手提交 |

禁止：`git add -A`、把其他会话的文件加入暂存、为“让状态变干净”而回滚别人的改动、在未获授权时创建 Junction 或改写登记面。

> **为什么？** 登记面的 `M` 可能包含另一会话尚未完成的工作。按路径写入自己的行看似安全，但计数与表体是一个整体，半个更新会让下一次登记基于错误基数。

## 9. G6：交付报告

步骤9：验证报告中的每项都有原始输出。

报告固定分三栏：

| 门 | 命令 | 实测 | 退出码 | 结论 |
|---|---|---|---|---|
| G1 包体 | `find ...` / UTF-8 检查 | 文件数、BOM、缓存 | — | PASS / FAIL |
| G2 质量门 | `check-skill-quality.py ...` | 分数、通过项数 | 0 / 非 0 | PASS / FAIL |
| G3 链接门 | `check-links.py ... --check-frontmatter-paths` | broken_local、broken_frontmatter | 0 / 非 0 | PASS / FAIL |
| G4 脚本 | `--help` / 夹具 | 各类退出码 | 按契约 | PASS / N/A |
| G5 登记 | `git status ...` | 被占用路径 | — | 已登记 / 延后 |

另外单列“未验证”与“延后”，并说明原因。文件存在但门未过，写“已写入、未验收”；门过了但登记未做，写“包体可交付、登记延后”。不得用“已创建/已更新/已验证”覆盖尚未发生的步骤。

> **为什么？** 交付报告是下一个 agent 的复跑脚本。没有命令与退出码的结论，只能被相信，不能被验证。

## 10. Gotchas（陷阱与反直觉行为）

1. **管道会换掉退出码**：`... | tail`、`... | tee` 返回最后一个命令的状态。用 `${PIPESTATUS[0]}` 或先直接执行再取 `$?`。
2. **`--score` 不显示失分项**：只打印分数。诊断要加 `--json` 或 `--verbose`。
3. **链接门默认不查 frontmatter**：不加 `--check-frontmatter-paths` 时 `broken_frontmatter` 恒为 0，这不是通过。
4. **默认阈值是 70**：不写 `--threshold 100`，95 分也会退出 0。
5. **用户级 Skill 在仓库质量门下可能只有 45 分**：英文/开放标准写法常缺强制触发措辞、Why、Gotchas、安全检查清单与 dry-run；仓库内验收要按五要素结构补齐。
6. **BOM 是隐性破坏**：肉眼看不见，但会让 frontmatter 首个字段解析异常；检查字节，不只看能否解码。
7. **跑脚本会生成 `__pycache__`**：验收通过后仍可能留下缓存，交付前必须复查。
8. **`--path` 指向仓库外时，JSON 的 `skills_dir` 仍显示仓库默认目录**：读 `skills[].path`，不要用 `skills_dir` 判断实际扫描对象。
9. **用户级 Skill 的 `source` 不要写仓库相对路径**：它按 Skill 文件所在目录解析，会制造断链；用说明性文字或省略。
10. **并发会话的登记面改动可能未暂存**：只看 `git diff --cached` 会漏掉 ` M`；同时看 `git status --porcelain`。
11. **`evals.json` 不容忍注释与尾逗号**：标准 JSON 解析失败会让“已解析”结论作废。
12. **目录链接会被判断链**：Markdown 链接必须指向具体文件。

## 11. 安全检查清单（逐项确认）

- [ ] 已确认目标目录与动作，已存在时未擅自覆盖（已确认）
- [ ] 已在写入前输出预览并取得用户确认（已确认）
- [ ] 已检查登记面占用状态，未把其他会话的改动带入本次交付（已检查）
- [ ] `name` 与目录名一致，frontmatter 可解析（已验证）
- [ ] 所有文本文件为 UTF-8 无 BOM，无 `__pycache__`/`.pyc` 残留（已验证）
- [ ] `evals/*.json` 可被标准 JSON 解析器读取（已验证）
- [ ] 质量门 100/100、34 项全过、真实退出码 0（已验证）
- [ ] 链接门显式加 `--check-frontmatter-paths`，broken_local 与 broken_frontmatter 均为 0（无断链）
- [ ] 捆绑脚本已按契约实跑，退出码有原始记录（已检查）
- [ ] 交付报告区分“已验证 / 未验证 / 登记延后”，未夸大结论（已明确）
- [ ] 未使用 `git add -A`，未提交或推送（已确认）
- [ ] 未修改其他 Skill 或其他会话的未提交内容（无残留）

## 12. 参考

- 来源会话证据、命令原文与失败输出：[references/verified-case.md](references/verified-case.md)
- 测试场景：[evals/evals.json](evals/evals.json)
- 相关技能：`native-skill-surface-registration`、`skill-bundled-script-validation`、`skill-quality-gate-remediation`
