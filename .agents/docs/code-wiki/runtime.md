# 运行与验证指南

## 环境要求

本仓库包含文档规范体系和 Python 子项目两类内容。不同任务所需环境不同。

| 场景 | 必需工具 | 说明 |
|---|---|---|
| 阅读和使用规范体系 | AI 编码工具、Git | 将仓库根目录作为工作目录，AI 工具读取 `AGENTS.md` |
| 运行治理脚本 | Python、Git | 执行 `.agents/scripts/` 下的检查脚本 |
| 运行提示词萃取系统 | Python、pip | 安装 `apps/prompt_extraction/requirements.txt` |
| 运行 Web UI | Python、pip、Streamlit | 使用 Streamlit 启动 `apps/prompt_extraction/ui/app.py` |
| 运行测试 | Python、pip、pytest | 执行 `apps/prompt_extraction/tests/` 测试套件 |

## 安装提示词萃取系统依赖

在仓库根目录执行：

```powershell
python -m pip install -r apps\prompt_extraction\requirements.txt
```

依赖包括：

- `streamlit`
- `pandas`
- `pytest`
- `plotly`

## 运行 Streamlit UI

在仓库根目录执行：

```powershell
python -m streamlit run apps\prompt_extraction\ui\app.py
```

启动后可以在浏览器中使用可视化界面，支持：

- 上传 CSV、JSON、TXT、Markdown 文件。
- 手动输入单条提示词。
- 查看质量评分、等级、雷达图、优化建议和优化 diff。
- 导出处理结果。

## 以 Python 代码调用流水线

可在仓库根目录下通过 Python 调用：

```python
from apps.prompt_extraction.pipeline import Pipeline

pipeline = Pipeline()
record = pipeline.run_single("请生成一份结构化项目总结，包含背景、问题、方案和结论。")
print(record.quality.overall)
print(record.quality.grade)
print(record.optimization.triggered)
```

批量处理文件：

```python
from apps.prompt_extraction.pipeline import Pipeline

pipeline = Pipeline()
records = pipeline.run_batch("prompts.csv")
pipeline.export_results(records, "results.csv")
```

## 运行 Python 测试

在仓库根目录执行：

```powershell
python -m pytest apps\prompt_extraction\tests
```

测试覆盖模块包括：

| 测试文件 | 覆盖范围 |
|---|---|
| `test_input.py` | 输入解析与输入处理 |
| `test_preprocessing.py` | 清洗与标准化 |
| `test_extraction.py` | 指令、约束、输出格式提取 |
| `test_assessment.py` | 清晰度、完整性、可执行性评分 |
| `test_optimization.py` | 优化触发、补缺、消歧、重组、diff |
| `test_pipeline.py` | 单条、批量、导出等流水线能力 |
| `test_integration.py` | 端到端场景 |

## 运行规范体系验证脚本

### 检查 Git 忽略规则

```powershell
python .agents\scripts\check-gitignore.py
```

用途：验证临时依赖路径是否被 `.gitignore` 覆盖，并检查 Git 状态中是否存在不应提交的临时产物。

### 检查 Markdown 链接

```powershell
python .agents\scripts\check-links.py
```

如需检查外部 URL：

```powershell
python .agents\scripts\check-links.py --check-external
```

### 检查规格文档一致性

```powershell
python .agents\scripts\check-spec-consistency.py
```

也可以检查指定 spec 目录：

```powershell
python .agents\scripts\check-spec-consistency.py --spec-dir .trae\specs\create-agents-md-and-config
```

### 生成文档导航

```powershell
python .agents\scripts\generate-nav.py
```

用途：扫描 `docs/` 目录并更新 README 导航表。

### 检查源文档溯源关系

```powershell
python .agents\scripts\check-source-traceability.py
```

查询某个源文件变更会影响哪些派生产物：

```powershell
python .agents\scripts\check-source-traceability.py --affected README.md
```

### 检查角色权限声明

```powershell
python .agents\scripts\check-role-permissions.py
```

用途：校验角色文件 TOML frontmatter 中 tier 字段与权限声明完整性。

## 运行 CI 综合检查

PowerShell 环境：

```powershell
.\.agents\scripts\ci-check.ps1
```

Shell 环境：

```bash
./.agents/scripts/ci-check.sh
```

注意：当前 PowerShell 脚本中包含文件名规范检查步骤，若对应脚本缺失或仓库版本未同步，可能需要先确认 `.agents/scripts/` 下实际脚本清单。

## 常见开发任务命令

| 任务 | 命令 |
|---|---|
| 安装提示词萃取依赖 | `python -m pip install -r apps\prompt_extraction\requirements.txt` |
| 启动 Web UI | `python -m streamlit run apps\prompt_extraction\ui\app.py` |
| 运行全部提示词萃取测试 | `python -m pytest apps\prompt_extraction\tests` |
| 检查 Git 忽略规则 | `python .agents\scripts\check-gitignore.py` |
| 检查本地 Markdown 链接 | `python .agents\scripts\check-links.py` |
| 检查规格一致性 | `python .agents\scripts\check-spec-consistency.py` |
| 更新文档导航 | `python .agents\scripts\generate-nav.py` |
| 运行 PowerShell CI 检查 | `.\.agents\scripts\ci-check.ps1` |

## 输入文件格式说明

### CSV

CSV 文件应包含提示词列，列名可以是 `prompt`、`text`、`content` 等可被关键词匹配的名称。若无法匹配，解析器会回退使用第一列。

```csv
prompt
请生成项目总结
请分析销售数据
```

### JSON

JSON 顶层应为对象数组。解析器会自动识别提示词字段。

```json
[
  {"prompt": "请生成项目总结"},
  {"prompt": "请分析销售数据"}
]
```

### TXT

每个非空行视为一条提示词。

```text
请生成项目总结
请分析销售数据
```

### Markdown

Markdown 文件优先按一级或二级标题拆分区块；若无标题，则整个文件作为一条提示词。

```markdown
# 任务一
请生成项目总结。

## 任务二
请分析销售数据。
```

## 结果导出说明

`Pipeline.export_results` 默认导出 CSV，字段包括：

- `id`
- `original_text`
- `cleaned_text`
- `instructions`
- `constraints`
- `expected_output`
- `clarity`
- `completeness`
- `executability`
- `overall`
- `grade`
- `optimized_text`
- `improvements`
- `error`

导出文件使用 `utf-8-sig` 编码，便于 Excel 正确识别中文。

## 验证建议

修改不同区域后建议运行不同验证：

| 修改区域 | 建议验证 |
|---|---|
| `apps/prompt_extraction/` 源码 | `python -m pytest apps\prompt_extraction\tests` |
| `docs/` 文档 | `python .agents\scripts\check-links.py` |
| `.agents/roles/` | `python .agents\scripts\check-role-permissions.py` |
| `.trae/specs/` | `python .agents\scripts\check-spec-consistency.py` |
| `.gitignore` 或临时目录规则 | `python .agents\scripts\check-gitignore.py` |
| README 导航相关文档 | `python .agents\scripts\generate-nav.py` 后检查 diff |
