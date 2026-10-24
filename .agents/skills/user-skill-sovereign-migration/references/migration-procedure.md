# 迁移操作规程

本文件给出 `user-skill-sovereign-migration` 的可执行细节。所有命令以 `D:\spaces\SpecWeave` 为主权区根目录示例；实际执行时以 `git rev-parse --show-toplevel` 的结果为准。

## 1. 变量与前置

```bash
SKILL_NAME="<skill-name>"
SRC="$HOME/.qoder/skills/$SKILL_NAME"
REPO="$(git -C D:/spaces/SpecWeave rev-parse --show-toplevel)"
DST="$REPO/.agents/skills/$SKILL_NAME"
```

前置条件（任一不满足则停止）：

- 当前用户已批准迁移方案
- `$DST` 不存在
- 按 §1.1 判定轨道后，对应条件成立：
  - 有源迁移：`$SRC/SKILL.md` 存在，且源路径是实体目录
  - 零源改根：`$SRC` 不存在，且不是联接

## 1.1 源判定（先做，零写入）

```bash
test -e "$SRC" && echo OLD_EXISTS || echo OLD_NOT_FOUND
test -L "$SRC" && echo OLD_IS_LINK || echo OLD_NOT_LINK
find "$SRC" -mindepth 1 -maxdepth 2 2>/dev/null | head -20
```

| 结果 | 轨道 |
|---|---|
| 存在，非联接，有 `SKILL.md` | 有源迁移，继续 §2 |
| 不存在，非联接 | 零源改根，跳转 §10 |
| 是联接 | 停止，核实目标；不要重复迁移 |
| 存在但既非目录也非联接 | 停止，先定性（权限失败/特殊文件） |

> `ls` 输出为空不能作为「不存在」的证据；空目录、联接与权限失败都可能表现相似。

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

```bash
# 1) 比对正文与资源
python compare_skill_copy.py "$SRC" "$DST"

# 2) 绝对路径扫描
grep -rn "file:///" "$DST" || echo "OK: no file:///"

# 3) 引用资源存在性
grep -RnoE "\]\(([^)#]+)" "$DST" | head -50

# 4) 链接门（目录级，避免单文件假通过）
python "$REPO/.agents/scripts/check-links.py" \
  --path "$DST" --check-frontmatter-paths

# 5) 质量门基线：目标与源两侧同命令各一次
python "$REPO/.agents/scripts/check-skill-quality.py" \
  --path "$DST" --json
python "$REPO/.agents/scripts/check-skill-quality.py" \
  --path "$SRC" --json
```

先比两侧，再决定是否修复：

1. 目标分数下降或出现新增警告，才可能是迁入漂移；目标分差若只来自已批准的 frontmatter 变更（如新增 `paths` 带来的 +5），且残余警告在源侧逐条存在，则判定为零漂移。
2. 来源会话实测：源 65/100、7 warn → 目标 70/100、6 warn；+5 恰好是新增 `paths` 消掉的一条，残余 6 项均可在源侧找到。
3. 目标 <100 时按批准范围分流：
   - 允许改正文 → 转 `skill-quality-gate-remediation`，按 error → warn 顺序修复并复跑 `--score --threshold 100`。
   - 明确排除正文 → 不改正文凑分；把未达标项、残余警告与两侧分差写入交付报告和交接载荷，标注「修复待下一轮单独授权」。

## 7. 交接载荷

调用 `native-skill-surface-registration` 时，附上以下事实：

```text
skill-name: <name>
source: ~/.qoder/skills/<name>（实体目录/联接）
target: <repo>/.agents/skills/<name>
frontmatter changes: <字段列表>
body changes: none / <已批准章节列表>
file hash check: PASS（N 个文件）
body check: PASS（仅 frontmatter 变化）
quality gate baseline: <分数与失败项>
quality gate source: <score>/100，<n> warn（<清单>）
quality gate target: <score>/100，<n> warn（<清单>）
quality gate delta: <+x>，归因 <字段/正文变更>
quality gate remediation: 已完成 / 未达标，待下一轮单独授权（范围排除正文）
source kind: physical directory / junction
deletion authorized: yes / no
```

交接后由该技能负责：

- README、capability-registry/02-skills、CHANGELOG、`.meta/toml` 四处登记与计数校正
- 质量门与链接门双验收
- 用户级 Junction 创建与回读验证
- 实体源目录为空时的 `rmdir` 清理；非空时先报告

## 8. 重入与失败处理

| 现象 | 处理 |
|---|---|
| 目标已存在且哈希一致 | 视为已迁入，跳过复制，继续验证与交接 |
| 目标已存在但内容不同 | 停止；报告差异，等待覆盖/改名/放弃的裁决 |
| 源路径是联接 | 不迁移；核实联接目标，直接进入验证或登记 |
| 哈希不一致 | 重新复制，不在目标上手工修补 |
| 正文差异未在提案中 | 恢复目标正文，重新比对 |
| 质量门低于 100，批准范围允许改正文 | 转 `skill-quality-gate-remediation`，修完复跑 |
| 质量门低于 100，批准范围排除正文 | 不改正文；上报未达标项与残余警告，修复留待下一轮授权 |
| 目标与源分差无法归因 | 停止交接；先查是否有未列明的正文或资源变更 |
| 链接门报错 | 修正链接或补齐目标文件；不要忽略或用 `--exclude` 掩盖 |
| Junction 创建失败 | 确认用户级路径为空；空目录用 `rmdir` 清理后重试，非空则报告 |
| 源目录已删除但联接缺失 | 先验证主权区目标完整，再重建联接；不要重建源实体副本 |
| 旧根不存在且非联接 | 无源可迁；转 §10 零源改根，不要复制或比对哈希 |
| 旧根存在但既非目录也非联接 | 先定性（权限失败/特殊文件），停止 |
| 无源却执行了复制/哈希 | 停止并报告假失败原因；本轮误建的空目录经确认后再用 `rmdir` 清理 |

## 9. 安全边界

- 不在未获批准时写入任何目标文件
- 不覆盖已存在的目标目录
- 不删除实体源目录，除非用户单独授权
- 不使用 `git add -A`、`git stash`、`git reset --hard`、`git clean`
- 不提交、不推送，除非用户明确要求
- 不在用户级与主权区同时保留两份实体内容作为最终状态

## 10. 零源改根分支（无源可迁）

触发：用户说「迁入 .agents/skills」，但方案批准后只改了目标根，旧根从未写入。

```bash
# 1) 旧根取证
test -e "$SRC" && echo OLD_EXISTS || echo OLD_NOT_FOUND
test -L "$SRC" && echo OLD_IS_LINK || echo OLD_NOT_LINK
find "$SRC" -mindepth 1 -maxdepth 2 2>/dev/null | head -20

# 2) 新根跨根查重
for root in "$HOME/.qoder/skills" "$HOME/.agents/skills" "$REPO/.agents/skills"; do
  test -e "$root/$SKILL_NAME" && echo "EXISTS: $root/$SKILL_NAME"
  test -L "$root/$SKILL_NAME" && echo "LINK:   $root/$SKILL_NAME"
done
git -C "$REPO" grep -n "$SKILL_NAME" -- . || echo "NO_TRACKED_HIT"
test -e "$REPO/.meta/toml/.agents/skills/$SKILL_NAME/SKILL.toml" \
  && echo "TOML_EXISTS" || echo "TOML_ABSENT"

# 3) 并发登记面
git -C "$REPO" status --short -- \
  .agents/skills/README.md .agents/skills/CHANGELOG.md \
  .agents/capability-registry/02-skills.md
```

处置：

| 旧根状态 | 动作 |
|---|---|
| 不存在且非联接 | 直接在新根创建；报告写「旧根未写入」 |
| 空目录 | 报告；经单独授权后 `rmdir` |
| 实体或半套副本 | 先比对文件清单与哈希，报告哪份是权威；删除需单独授权 |
| 联接 | 先读 `LinkType`/`Target`；不得直接复制或删除 |

该分支**不执行** §4–§5 的复制与哈希步骤。frontmatter 仍按新根原生约定写；新根没有 TOML 镜像时不要写 `x-toml-ref`。验收按 §6 在新根执行，报告中把哈希/正文比对写「不适用」，不要写 PASS。
