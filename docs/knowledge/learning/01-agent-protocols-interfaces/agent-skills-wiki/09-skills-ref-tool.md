---
source: "agent-skills-open-standard-wiki.md#十验证工具skills-ref"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/09-skills-ref-tool.toml"
id: "agent-skills-wiki-skills-ref-tool"
title: "验证一个技能目录"
---
## 十、验证工具：skills-ref

### 10.1 安装

项目中已包含本地副本：[external/agentskills/skills-ref](../../../../../external/agentskills/skills-ref/)

使用 uv 安装（推荐）：

```bash
cd d:\spaces\SpecWeave\external\agentskills\skills-ref
uv sync
.venv\Scripts\Activate.ps1
```

或使用 pip：

```powershell
cd d:\spaces\SpecWeave\external\agentskills\skills-ref
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

### 10.2 CLI 命令

```bash
# 验证一个技能目录
skills-ref validate path/to/skill

# 读取技能属性（输出 JSON）
skills-ref read-properties path/to/skill

# 为智能体提示生成 &lt;available_skills&gt; XML
skills-ref to-prompt path/to/skill-a path/to/skill-b
```

> **源码锚点**：CLI 实现见 [cli.py](../../../../../.agents/scripts/lib/cli.py)

#### validate 命令

检查技能是否有有效的 SKILL.md，包括正确的 frontmatter、命名约定和必填字段。

**退出码**：
- `0`：有效技能
- `1`：发现验证错误

```bash
$ skills-ref validate .agents/skills/roll-dice
Valid skill: .agents/skills/roll-dice
```

#### read-properties 命令

解析 SKILL.md 的 YAML frontmatter 并将属性输出为 JSON：

```bash
$ skills-ref read-properties .agents/skills/roll-dice
{
  "name": "roll-dice",
  "description": "Roll dice using a random number generator..."
}
```

#### to-prompt 命令

生成 `<available_skills>` XML 块用于智能体系统提示。这是 Anthropic 为 Claude 模型推荐的格式：

```xml
<available_skills>
<skill>
<name>my-skill</name>
<description>What this skill does and when to use it</description>
<location>/path/to/my-skill/SKILL.md</location>
</skill>
</available_skills>
```

`<location>` 元素告诉智能体在哪里找到完整的技能指令。

### 10.3 Python API

```python
from pathlib import Path
from skills_ref import validate, read_properties, to_prompt

# 验证技能目录
problems = validate(Path("my-skill"))
if problems:
    print("Validation errors:", problems)

# 读取技能属性
props = read_properties(Path("my-skill"))
print(f"Skill: {props.name} - {props.description}")

# 生成可用技能的提示
prompt = to_prompt([Path("skill-a"), Path("skill-b")])
print(prompt)
```

> **源码锚点**：公共 API 见 [__init__.py](../../../../../prompt_extraction/__init__.py)；提示生成见 [prompt.py](../../../../../external/agentskills/skills-ref/src/skills_ref/prompt.py)

### 10.4 验证检查清单

运行 `skills-ref validate` 将检查：

| 检查项 | 错误条件 |
|--------|---------|
| 路径存在 | 目录不存在 |
| 是目录 | 路径不是目录 |
| SKILL.md 存在 | 缺少 SKILL.md 或 skill.md |
| Frontmatter 格式 | 不以 `---` 开头或没有正确闭合 |
| YAML 有效性 | 无效的 YAML 语法 |
| 必填字段存在 | 缺少 `name` 或 `description` |
| Name 格式 | 非字符串、为空、超过 64 字符、含大写、开头/结尾连字符、连续连字符、无效字符 |
| 目录名匹配 | 目录名与 name 不匹配（NFKC 规范化后） |
| Description 格式 | 非字符串、为空、超过 1024 字符 |
| Compatibility 格式 | 非字符串、超过 500 字符 |
| 允许字段 | frontmatter 包含未知字段 |

### 10.5 运行测试

```bash
cd d:\spaces\SpecWeave\external\agentskills\skills-ref
uv run pytest
```

测试覆盖：
- 有效技能验证
- 各种名称格式错误（大写、过长、连字符问题、无效字符、目录不匹配）
- 描述长度限制
- 兼容性字段验证
- 所有可选字段接受
- 国际化名称（中文、俄文）
- NFKC Unicode 规范化

> **测试文件**：[test_validator.py](../../../../../external/agentskills/skills-ref/tests/test_validator.py)
