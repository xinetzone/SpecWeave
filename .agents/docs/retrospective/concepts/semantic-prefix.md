> **来源**：从 `docs/retrospective/knowledge-extraction.md` 六、可复用知识概念 拆分

# 语义前缀（Semantic Prefix）

## 定义
路径中隐含的、指示解析基准的前缀。如 `.agents/` 暗示"这是项目根目录下的规范目录"，应以根目录为基准解析。

## 当前项目语义前缀
`.agents/`、`vendor/`、`.trae/`、`docs/`

## 推广
任何文档间交叉引用都可通过语义前缀判断解析基准。

> **关联模块**：
> - `patterns/code-patterns/context-aware-path-resolution.md`