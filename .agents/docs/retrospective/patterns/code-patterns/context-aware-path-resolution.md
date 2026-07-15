---
id: "context-aware-path-resolution"
source: "external: 不存在-docs/retrospective/knowledge-extraction.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/code-patterns/context-aware-path-resolution.toml"
---
> **来源**：从 `docs/retrospective/knowledge-extraction.md` 一、可复用代码模式 拆分

# 上下文感知路径解析

## 来源
`check-spec-consistency.py` — `resolve_path()`

## 代码
```python
# 以项目根目录为基准解析的路径前缀
PROJECT_ROOT_PREFIXES = [".agents/", "vendor/", ".trae/", "docs/"]

def resolve_path(ref: str, spec_dir: Path, project_root: Path) -> Path:
    """根据引用路径前缀选择基准目录进行解析。
    
    以 PROJECT_ROOT_PREFIXES 中列出的前缀开头的路径，以项目根目录为基准；
    其他相对路径以 spec 所在目录为基准。
    """
    for prefix in PROJECT_ROOT_PREFIXES:
        if ref.startswith(prefix):
            return project_root / ref
    return spec_dir / ref
```

## 复用场景
任何需要解析文档间交叉引用的工具。替换 `PROJECT_ROOT_PREFIXES` 即可适配不同项目。

> **关联模块**：
> - `patterns/code-patterns/three-tier-check-tool.md`
> - `concepts/semantic-prefix.md`