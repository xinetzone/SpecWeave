# 迁移操作规程

本文件给出 `user-skill-sovereign-migration` 的可执行细节。所有命令以 `D:\spaces\SpecWeave` 为主权区根目录示例；实际执行时以 `git rev-parse --show-toplevel` 的结果为准。

## 1. 变量与前置

```bash
SKILL_NAME="<skill-name>"
SRC="$HOME/.qoder/skills/$SKILL_NAME"
REPO="$(git -C D:/spaces/SpecWeave rev-parse --show-toplevel)"
DST="$REPO/.agents/skills/$SKILL_NAME"
```

先只读预检，再取得本轮对应轨道与文件范围的批准；未获批不执行写入：

- 推荐目标若与项目主权区约定冲突，先说明差异并确认最终目标，不默认采纳推荐或静默改根；用户后续明确选择优先
- 同时检查 `$SRC` 与 `$DST`，不得只凭旧根缺失创建目标
- 有源迁移：源是包含 `SKILL.md` 的实体目录，目标不存在
- 无源交接：两根均不存在且非联接，转 §10；只携带已有设计与当前批准，不执行 §2–§5
- 任一目标已存在：先查权威副本与差异，转显式 Update 或冲突裁决，不以 Create 覆盖

## 1.1 双根判定（先做，零写入）

用可区分 `ENOENT` 与权限错误的只读探测；`lstat` 保留悬空联接信息。传入 Node 的路径使用 `C:/...`、`D:/...` 等原生路径，不用 Bash 的 `/c/...`：

```bash
node - "$SRC" "$DST" <<'JS'
const fs = require('node:fs');
for (const path of process.argv.slice(2)) {
  try {
    const item = fs.lstatSync(path);
    console.log(JSON.stringify({path, exists: true,
      isDirectory: item.isDirectory(), isSymbolicLink: item.isSymbolicLink()}));
  } catch (error) {
    console.log(JSON.stringify({path, error: error.code}));
    if (error.code !== 'ENOENT') process.exitCode = 1;
  }
}
JS
```

| 双根结果（联接或错误优先处理） | 轨道 |
|---|---|
| 任一根为联接，含悬空联接 | 停止，核实目标；不要重复迁移或创建 |
| 权限错误、特殊文件、空目录或缺 `SKILL.md` 的半套副本 | 停止并分类，不当作不存在 |
| 目标已存在 | 只读取证；显式 Update 或冲突裁决，不覆盖、不更新两根 |
| 源为含 `SKILL.md` 的实体，目标缺失 | 有源迁移，继续 §2 |
| 两根均返回 `ENOENT`，且非联接 | 无源交接，跳转 §10 |

> `ENOENT` 是有效的缺失预检结果，不是失败的迁移命令；权限错误不得吞成缺失。当前不存在也不证明「从未写入」，后者需要会话历史证据；`ls` 空输出不能证明任一结论。

## 2. 预检命令

```bash
# 源清单
find "$SRC" -type f | sort
find "$SRC" -type d -name __pycache__ -prune -print

# 仓库状态
git -C "$REPO" rev-parse --show-toplevel
git -C "$REPO" rev-parse --show-superproject-working-tree 2>/dev/null || true
git -C "$REPO" status --short

# 目标与登记面
test -e "$DST" && echo "TARGET_EXISTS" || echo "TARGET_ABSENT"
test -e "$REPO/.meta/toml/.agents/skills/$SKILL_NAME/SKILL.toml" \
  && echo "TOML_EXISTS" || echo "TOML_ABSENT"
grep -n "$SKILL_NAME" \
  "$REPO/.agents/skills/README.md" \
  "$REPO/.agents/capability-registry/02-skills.md" \
  "$REPO/.agents/skills/CHANGELOG.md"
```

Windows 下判断源路径类型：

```powershell
Get-Item "$HOME\.qoder\skills\$env:SKILL_NAME" |
  Select-Object FullName, LinkType, Target
```

`LinkType` 非空表示已是联接；此时不要迁移，先核实它指向的目标是否就是权威副本。

## 3. 原生化 frontmatter 模板

```yaml
---
name: <skill-name>
version: 1.0.0
description: "..."
argument-hint: "<...>"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/<skill-name>/**"
title: "<Skill 标题>"
# 仅当 .meta/toml 镜像已创建时写：
x-toml-ref: "../../../.meta/toml/.agents/skills/<skill-name>/SKILL.toml"
---
```

字段规则：

| 字段 | 规则 |
|---|---|
| `name` | kebab-case，且与目录名完全一致 |
| `version` | 迁入原生轨时统一从 `1.0.0` 起 |
| `description` | 保留原有有效描述，补足触发词与强制使用措辞 |
| `paths` | 指向主权区技能目录，不写用户级绝对路径 |
| `x-toml-ref` | 条件字段：仅当 `.meta/toml` 镜像已创建时写入；按 SKILL.md 实际所在层级推算，`.agents/skills/<name>/` 下是 `../../../` |
| `source` | 若原 Skill 有来源说明则保留；不写入本机绝对路径。它是 `check-links.py` 默认校验的路径字段，溯源改用会话 ID 等非路径文本 |

> 层数校验：从 `.agents/skills/<name>/SKILL.md` 出发，`..` 到 `.agents/skills/`，`../..` 到 `.agents/`，`../../..` 到仓库根；再进入 `.meta/toml/...`。共三级。

> `x-toml-ref` 与 `source` 都是 `check-links.py --check-frontmatter-paths` 的默认校验字段（`check-links.py:477`）。镜像未建或来源不是文件路径时，写入路径值会被判为断链；本轮登记延后时两个字段一并延后。

## 4. 复制命令

PowerShell：

```powershell
$src = "$HOME\.qoder\skills\<name>"
$dst = "<repo>\.agents\skills\<name>"

if (Test-Path -LiteralPath $dst) { throw "目标已存在：$dst" }
Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force

Get-ChildItem -LiteralPath $dst -Recurse -Directory -Filter __pycache__ |
  Remove-Item -Recurse -Force
Get-ChildItem -LiteralPath $dst -Recurse -File -Include *.pyc, *.pyo |
  Remove-Item -Force
```

Bash：

```bash
test -e "$DST" && { echo "目标已存在"; exit 1; }
cp -a "$SRC/." "$DST/"
find "$DST" -type d -name __pycache__ -prune -exec rm -rf {} +
```

复制后先在目标目录内补 frontmatter，再运行比对。正文修改必须已在提案中列明；未列明的正文差异视为复制事故。

## 5. 哈希与正文比对脚本

将以下脚本保存为临时文件（不要写入仓库），或直接在支持 Python 3.10+ 的环境中执行：

```python
import hashlib
import sys
from pathlib import Path

IGNORED_DIRS = {"__pycache__", ".git"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}
IGNORED_FILES = {".DS_Store", "Thumbs.db"}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    return text[: end + 4], text[end + 4 :]


def inventory(root: Path) -> dict[str, Path]:
    files = {}
    for path in root.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix in IGNORED_SUFFIXES or path.name in IGNORED_FILES:
            continue
        files[path.relative_to(root).as_posix()] = path
    return files


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: python compare_skill_copy.py <source-dir> <target-dir>")
        return 2

    source = Path(sys.argv[1]).resolve()
    target = Path(sys.argv[2]).resolve()
    failures = []

    source_files = inventory(source)
    target_files = inventory(target)

    missing = sorted(set(source_files) - set(target_files))
    extra = sorted(set(target_files) - set(source_files))
    if missing:
        failures.append(f"target missing files: {missing}")
    if extra:
        failures.append(f"target extra files: {extra}")

    for relative in sorted(set(source_files) & set(target_files)):
        if relative == "SKILL.md":
            source_text = source_files[relative].read_text(encoding="utf-8")
            target_text = target_files[relative].read_text(encoding="utf-8")
            source_body = split_frontmatter(source_text)[1].strip()
            target_body = split_frontmatter(target_text)[1].strip()
            if source_body != target_body:
                failures.append("SKILL.md body differs; only frontmatter changes are allowed")
        elif digest(source_files[relative]) != digest(target_files[relative]):
            failures.append(f"content differs: {relative}")

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"PASS: {len(target_files)} files checked; SKILL.md body identical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

运行：

```bash
python compare_skill_copy.py "$SRC" "$DST"
```

若提案明确包含正文修改，脚本会失败。此时逐条 diff 并人工确认每处差异都在批准清单内，再记录到交接载荷；不要为通过脚本而回退已批准的修改。

## 6. 内容级验证

**有源轨才运行** §5 比较脚本与源侧质量门。无源轨由 `skill-creator` 验证新建目标；读取源、复制、源目标 SHA256、正文保真、源侧质量门及质量分差全部记「不适用（无源）」，不能填写 PASS、0 分或零漂移。

```bash
# 仅有源迁移执行
python compare_skill_copy.py "$SRC" "$DST"
```

两轨均验证实际目标：

```bash
# 2) 绝对路径扫描
grep -rn "file:///" "$DST" || echo "OK: no file:///"

# 3) 引用资源存在性
grep -RnoE "\]\(([^)#]+)" "$DST" | head -50

# 4) 链接门（目录级，避免单文件假通过）
python "$REPO/.agents/scripts/check-links.py" \
  --path "$DST" --check-frontmatter-paths

python -B "$REPO/.agents/scripts/check-skill-quality.py" \
  --path "$DST" --json
python -B "$REPO/.agents/scripts/check-skill-quality.py" \
  --path "$DST" --score --threshold 100
```

仅有源轨再用同一检查器取源侧基线：

```bash
python -B "$REPO/.agents/scripts/check-skill-quality.py" \
  --path "$SRC" --json
```

逐条记录实际退出码；`--verbose` 退出 0 不代替 `--score --threshold 100` 满分验收。无源时只报告目标分数、失败项与退出码，单产物 SHA256 也不能证明迁移保真。

有源轨先比两侧，再决定是否修复；无源轨仅按第 3 项和新建批准范围处理目标失败：

1. 目标分数下降或出现新增警告，才可能是迁入漂移；目标分差若只来自已批准的 frontmatter 变更（如新增 `paths` 带来的 +5），且残余警告在源侧逐条存在，则判定为零漂移。
2. 来源会话实测：源 65/100、7 warn → 目标 70/100、6 warn；+5 恰好是新增 `paths` 消掉的一条，残余 6 项均可在源侧找到。
3. 目标 <100 时按批准范围分流：
   - 允许改正文 → 转 `skill-quality-gate-remediation`，按 error → warn 顺序修复并复跑 `--score --threshold 100`。
   - 明确排除正文 → 不改正文凑分；把未达标项、残余警告与两侧分差写入交付报告和交接载荷，标注「修复待下一轮单独授权」。

## 7. 验收与登记交接载荷

目标验证通过且本轮批准登记后，才交接 `native-skill-surface-registration`；未批准则只报告内容交付与待授权事项。无源创建前给 `skill-creator` 的载荷见 §10，不用登记交接代替创建交接。

```text
skill-name: <name>
operation: migrate / create
source: <实体源路径> / 不适用（两根缺失，无源）
target: <本轮确认的主权区路径>
frontmatter changes: <字段列表>
body changes: none / <已批准章节列表>
copy: <实测状态> / 不适用（无源）
file hash check: <实测结果与文件数> / 不适用（无源）
body check: <实测结果与批准差异> / 不适用（无源）
quality gate source: <分数、失败项、退出码> / 不适用（无源）
quality gate target: <分数、失败项、退出码>
quality gate delta: <分差与逐项归因> / 不适用（无源）
quality gate remediation: 无需修复 / 已完成 / 未达标，待单独授权
source kind: physical directory / junction / absent
registration authorized: yes / no
junction authorized: yes / no
delete or move source authorized: yes / no
stage authorized: yes / no
commit authorized: yes / no
push authorized: yes / no
```

按各项当前授权执行，不因内容获批或移交另一技能而扩大权限：

- 登记获批才修改 README、capability-registry/02-skills、CHANGELOG、`.meta/toml`；无新增条目不增加计数
- 复跑质量门与链接门，并发登记面脏时延后该面，不覆盖他人改动
- Junction 创建与回读单独授权；替换实体源还需源移动或删除授权
- 暂存、提交、推送分别确认；历史会话中的批准不计入本轮权限

## 8. 重入与失败处理

| 现象 | 处理 |
|---|---|
| 目标已存在且两侧保真比对通过 | 只报告内容一致，不据此推断历史迁移动作；跳过复制，验证后仅按当前授权交接 |
| 目标已存在但内容不同，或无源可比 | 停止；报告权威副本与差异，取得显式 Update 或冲突裁决，不用 Create 覆盖 |
| 源路径是联接 | 不迁移；核实目标，可只读验证；登记仍需当前授权 |
| 哈希不一致 | 仅重做本轮获批且由本轮创建的目标复制；既有或并发改动先停止并报告 |
| 正文差异未在提案中 | 先归因，不覆盖既有或并发改动；仅修复本轮引入的未批准差异再比对 |
| 质量门低于 100，批准范围允许改正文 | 转 `skill-quality-gate-remediation`，修完复跑 |
| 质量门低于 100，批准范围排除正文 | 不改正文；上报未达标项与残余警告，修复留待下一轮授权 |
| 目标与源分差无法归因 | 停止交接；先查是否有未列明的正文或资源变更 |
| 链接门报错 | 修正链接或补齐目标文件；不要忽略或用 `--exclude` 掩盖 |
| Junction 创建失败 | 在联接授权内排查；删除空目录也须确认源清理授权，非空则报告 |
| 源目录已删除但联接缺失 | 先验证主权区目标完整，获准后再重建联接；不要重建源实体副本 |
| 两根均不存在且非联接 | 无源可迁；转 §10 交接 `skill-creator`，不复制、不做迁移比较 |
| 任一根存在但既非目录也非联接 | 先定性（权限失败/特殊文件），停止 |
| 无源却执行了复制/哈希 | 停止并报告误走有源轨；缺失预检本身不是迁移失败，本轮误建空目录经确认后再清理 |

## 9. 安全边界

- 不在未获批准时写入任何目标文件；推荐 JSON 和历史授权不能代替本轮批准
- 不覆盖已存在的目标目录，不因另一根缺失而重建已有目标
- 登记、Junction、源移动或删除分别授权，保留未获清理授权的实体副本并如实报告
- 不使用 `git add -A`、`git stash`、`git reset --hard`、`git clean`
- 不暂存、不提交、不推送，除非用户对各项明确授权
- 不同时更新用户级与主权区两份实体；一个权威副本加联接是目标状态，不是擅自清理现有副本的理由

## 10. 零源改根分支（无源可迁）

触发：用户说「迁入 .agents/skills」，但 §1.1 确认两根均不存在、非联接；操作定性为 create，而非 migrate。只有会话证据支持时才写「从未写入」。

1. 复述推荐根与拟用根的差异，确认最终路径；若批准后改根，交由 `skill-target-root-switch-replan` 做重规划，不重复设计已批准内容。
2. 用 §1.1 同样的只读探测补查 `~/.agents/skills/<name>`，并查仓库同名登记与 TOML 镜像；出现副本、空壳、联接或探测错误则停止分流，不造源、不清理。
3. 检查仓库根、submodule 与并发登记面状态，重读新根 frontmatter、质量门与链接门约定；搜索无命中与命令错误分开报告。
4. 把以下载荷交给 `skill-creator` 的 Create 流程。已有批准完整覆盖新根、操作和内容时直接承接；只批准旧根、内容仍为提案或范围不清时先补确认。来源会话中的历史批准不能移作本轮授权。

```text
operation: create（不是 migrate）
skill-name: <name>
root decision: <推荐根 → 本轮确认根；冲突如何解决>
source probe: <路径、ENOENT、非联接证据>
target probe: <路径、ENOENT、非联接证据>
duplicate check: <第三根、登记与镜像结果>
existing design: <已有正文设计、资源清单、有效约束及当前设计批准状态>
current authorization: <本轮批准消息及其覆盖的目标、操作、文件和内容范围>
excluded actions: <未授权的登记、Junction、源清理、暂存、提交、推送>
target contract: <新根原生 frontmatter 与验证命令；TOML 是否存在>
migration comparisons: 不适用（复制、源目标哈希、正文保真、源侧质量门、质量分差）
```

`skill-creator` 写入前须复查目标仍不存在；若已出现，停止 Create 并走 Update 或冲突裁决。它负责创建及目标验收，本技能不另设一套创建算法。

该分支**不执行**读源全文、§4–§5 复制与比较脚本或 §6 源侧评分；不为迁移造空源。新根无 TOML 镜像时不写 `x-toml-ref`。只执行 §6 的目标检查，记录分数、失败项和真实退出码；源侧与分差写「不适用」，不得声称零漂移或已 move。通过后如实报告「已在主权区新建，无源可迁」；登记和联接仅按 §7 的独立授权交接，并发占用则说明延后。
