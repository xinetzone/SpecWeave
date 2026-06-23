# Scripts 脚本目录

`.agents/scripts/` 目录存放自动化验证与检查脚本。

## 脚本列表

| 脚本 | 用途 | 用法 |
|------|------|------|
| `check-gitignore.py` | 验证 `.gitignore` 规则覆盖所有临时依赖路径，检查 `git status` 合规性 | `python .agents/scripts/check-gitignore.py` |
| `check-links.py` | 扫描 Markdown 文件中的链接，校验本地文件引用与外部 URL 可达性 | `python .agents/scripts/check-links.py [--check-external] [--json] [--exclude DIR]` |
| `check-spec-consistency.py` | 检查 `spec.md`、`tasks.md`、`checklist.md` 之间的一致性 | `python .agents/scripts/check-spec-consistency.py [--spec-dir DIR] [--all] [--json]` |
| `generate-nav.py` | 扫描 `docs/` 目录，自动生成并更新 README.md 与 docs/README.md 的文档导航表 | `python .agents/scripts/generate-nav.py` |
| `check-move.py` | 文件移动时自动调整内部相对链接路径，可选更新外部引用 | `python .agents/scripts/check-move.py <源> <目标> [--dry-run] [--update-refs]` |

## 使用说明

### check-gitignore.py

验证 `.gitignore` 是否包含所有必需的忽略规则，并确认 `git status` 中不包含临时依赖文件。

```bash
python .agents/scripts/check-gitignore.py
```

### check-links.py

扫描项目中的所有 Markdown 文件，提取并校验链接有效性：

- **本地文件引用**：检查相对路径引用的目标文件是否存在（默认启用）
- **外部 URL 检查**：通过 HTTP HEAD 请求检查外部链接是否可达（需显式启用）
- **模板占位符过滤**：自动跳过 `<!-- ... -->` 格式的模板占位符
- **智能容错**：403（反爬虫）和 405（不支持 HEAD）视为链接可达

```bash
# 仅检查本地文件引用（默认）
python .agents/scripts/check-links.py

# 同时检查外部链接
python .agents/scripts/check-links.py --check-external

# 指定超时与并发数
python .agents/scripts/check-links.py --check-external --timeout 10 --workers 8

# 排除指定目录
python .agents/scripts/check-links.py --exclude docs/templates vendor

# JSON 格式输出（便于 CI 集成）
python .agents/scripts/check-links.py --json

# 检查指定目录
python .agents/scripts/check-links.py --path docs/
```

### check-spec-consistency.py

检查指定 spec 目录或全部 spec 目录中三份文档（spec.md、tasks.md、checklist.md）的一致性：

- 需求 → 任务覆盖检查
- 场景 → 检查点覆盖检查
- 关键数据引用一致性检查
- 交叉引用有效性检查

```bash
# 扫描所有 spec 目录
python .agents/scripts/check-spec-consistency.py

# 检查指定 spec 目录
python .agents/scripts/check-spec-consistency.py --spec-dir .trae/specs/create-agents-md-and-config

# JSON 格式输出
python .agents/scripts/check-spec-consistency.py --json
```

### generate-nav.py

扫描 `docs/` 目录下的所有 `.md` 文件，提取标题和描述，自动生成文档导航表，
并更新 `README.md` 和 `docs/README.md` 中 `<!-- NAV_TABLE_START -->` 与 `<!-- NAV_TABLE_END -->` 标记之间的内容。

```bash
# 自动生成并更新导航表
python .agents/scripts/generate-nav.py
```

### check-move.py

当 Markdown 文件需要移动到新目录时，自动调整文件内部的相对链接路径，
确保移动后所有链接仍然有效。支持 `--update-refs` 选项同时更新其他文件中对源文件的引用。

```bash
# 预览变更（不实际修改）
python .agents/scripts/check-move.py --dry-run docs/old.md docs/new/location.md

# 执行移动并调整链接
python .agents/scripts/check-move.py docs/old.md docs/new/location.md

# 执行移动并同步更新其他文件中的引用
python .agents/scripts/check-move.py --update-refs docs/old.md docs/new/location.md
```