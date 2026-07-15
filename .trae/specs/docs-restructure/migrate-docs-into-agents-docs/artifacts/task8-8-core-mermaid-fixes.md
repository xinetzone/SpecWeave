---
source:
  - "tasks.md#Task 8"
  - "artifacts/task8-7-mermaid-batches.md"
generated_at: "2026-07-15"
task: "SubTask 8.8"
type: "core-mermaid-fixes"
status: "completed"
---

# Task 8.8 第一批核心规范文档 Mermaid 修复摘要

## 处理范围

- 仅处理 `task8-7-mermaid-batches.md` 中 C1 第一批 5 个文件：
  - `README.md`
  - `.agents/commands/seven-concepts.md`
  - `.agents/checklists/risk-scoring-checklist.md`
  - `.agents/checklists/tech-doc-writing-precheck.md`
  - `.agents/checklists/meta-retrospective-checklist.md`
- 未修改 `AGENTS.md`、`project-governance/documentation-governance` 路径、`tasks.md`。
- 处理策略：只做 Mermaid 安全写法最小修复，不改动图表表达意图与正文结构。

## 修复结果

| 文件 | 修复动作 | 结果 |
|---|---|---|
| `README.md` | 将 3 个 `subgraph` 的中文 ID 改为英文 ID，并同步更新连线目标 | 根入口图改为安全 `subgraph EN_ID ["中文标题"]` 写法 |
| `.agents/commands/seven-concepts.md` | 将决策树中的裸中文节点、裸中文边标签补双引号；将 `\n` 换行改为 `<br/>`；去除代码块内空行 | 七概念决策树通过定向 Mermaid 校验 |
| `.agents/checklists/risk-scoring-checklist.md` | 将节点文本与边标签统一改为带双引号的安全写法 | 风险评分流程图通过定向 Mermaid 校验 |
| `.agents/checklists/tech-doc-writing-precheck.md` | 将节点文本与边标签统一改为带双引号的安全写法 | 文档编写流程图通过定向 Mermaid 校验 |
| `.agents/checklists/meta-retrospective-checklist.md` | 将节点文本与边标签统一改为带双引号的安全写法 | 元复盘流程图通过定向 Mermaid 校验 |

## 校验记录

### 1. 编辑器诊断

- 对上述 5 个已编辑文件运行诊断，结果均为 `0` 个新增问题。

### 2. Mermaid 定向校验

- 由于 `check-mermaid.py --path <file>` 当前只支持目录扫描、无法稳定覆盖单文件，采用检查器底层 `_process_file()` 对 5 个目标文件做定向复扫。
- 执行命令：

```bash
python -X utf8 -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.agents/scripts').resolve())); from lib.checks import mermaid; root = Path('.').resolve(); files = [Path('README.md'), Path('.agents/commands/seven-concepts.md'), Path('.agents/checklists/risk-scoring-checklist.md'), Path('.agents/checklists/tech-doc-writing-precheck.md'), Path('.agents/checklists/meta-retrospective-checklist.md')]; total_err = total_warn = 0; bad = 0; print('[检查] 定向 Mermaid 校验');\
for f in files:\
    issues, fixes, diffs = mermaid._process_file((root / f).resolve(), root, fix=False, dry_run=False);\
    errs = [i for i in issues if i[1] == 'error']; warns = [i for i in issues if i[1] == 'warning'];\
    if issues:\
        bad += 1;\
        print(f'[文件] {f.as_posix()}');\
        [print(f'  [{lvl}] L{ln}: {msg}') for ln, lvl, msg in issues];\
    total_err += len(errs); total_warn += len(warns);\
print(f'[结果] files={len(files)} bad={bad} errors={total_err} warnings={total_warn}');\
sys.exit(1 if total_err else 0)"
```

- 校验结果：`files=5 bad=0 errors=0 warnings=0`。

## 备注

- 本轮仅收敛 `SubTask 8.8` 第一批 C1 中用户指定的 5 个核心文件，不扩散到 `.agents/commands/` 其他文档。
- 后续若继续推进 `SubTask 8.8`，可按 `task8-7-mermaid-batches.md` 中建议顺序继续处理 C2、C3。
