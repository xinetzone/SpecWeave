# Scripts 脚本目录

`.agents/scripts/` 目录存放自动化验证与检查脚本。

## 脚本列表

| 脚本 | 用途 | 用法 |
|------|------|------|
| `check-gitignore.py` | 验证 `.gitignore` 规则覆盖所有临时依赖路径，检查 `git status` 合规性 | `python .agents/scripts/check-gitignore.py` |
| `check-spec-consistency.py` | 检查 `spec.md`、`tasks.md`、`checklist.md` 之间的一致性 | `python .agents/scripts/check-spec-consistency.py [--spec-dir DIR] [--all] [--json]` |

## 使用说明

### check-gitignore.py

验证 `.gitignore` 是否包含所有必需的忽略规则，并确认 `git status` 中不包含临时依赖文件。

```bash
python .agents/scripts/check-gitignore.py
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