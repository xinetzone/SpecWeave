---
id: "gitignore-validation"
source: "docs/retrospective/knowledge-extraction.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/gitignore-validation.toml"
---
> **来源**：从 `docs/retrospective/knowledge-extraction.md` 一、可复用代码模式 拆分

# Git 忽略规则验证

## 来源
`check-gitignore.py`

## 代码
```python
REQUIRED_RULES = [
    "vendor/",
    ".temp/",
    "__pycache__/",
    "*.pyc",
    ".venv/",
    "node_modules/",
    ".env",
    "*.log",
    ".DS_Store",
    "Thumbs.db",
]

def check_gitignore_rules(gitignore_path: Path) -> list[str]:
    """检查 .gitignore 是否包含所有必需规则。"""
    content = gitignore_path.read_text(encoding="utf-8")
    missing = []
    for rule in REQUIRED_RULES:
        if rule not in content:
            missing.append(rule)
    return missing
```

## 复用场景
任何需要验证 `.gitignore` 规则完整性的项目。替换 `REQUIRED_RULES` 即可。

> **关联模块**：
> - `frameworks/dependency-management-matrix.md`