---
id: "agent-skills-wiki-file-references"
source: "agent-skills-open-standard-wiki.md#十一文件引用规范"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/10-file-references.toml"
---
## 十一、文件引用规范

### 11.1 相对路径规则

在技能中引用其他文件时，使用相对于技能根目录的相对路径：

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script: scripts/extract.py
```

### 11.2 引用深度建议

保持文件引用距 `SKILL.md` 一层深度。避免深度嵌套的引用链。
