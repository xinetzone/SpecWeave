---
id: "tools-search"
title: "搜索工具规范"
source: "AGENTS.md#工具规范"
x-toml-ref: "../../.meta/toml/.agents/tools/search.toml"
---
# 搜索工具规范

本规范定义了智能体在代码库中进行内容搜索、文件查找以及语义搜索时所使用的工具集合、参数格式、输出约定以及使用约束，确保搜索行为高效、准确且符合最佳实践。

## 工具清单

| 工具名称 | 功能 | 输入参数 | 输出格式 |
|---|---|---|---|
| grep_search | 正则搜索文件内容 | pattern: string, path: string, glob: string | 匹配文件列表或内容 |
| glob_find | 文件名模式匹配 | pattern: string, path: string | 文件路径列表 |
| semantic_search | 语义搜索 | query: string, target_directories: string[] | 相关代码片段 |

## 输入参数 Schema

### grep_search

```json
{
  "pattern": {
    "type": "string",
    "description": "正则表达式模式，遵循 ripgrep 语法",
    "required": true
  },
  "path": {
    "type": "string",
    "description": "搜索的目标目录或文件绝对路径，未指定时搜索当前工作目录",
    "required": false
  },
  "glob": {
    "type": "string",
    "description": "文件名过滤模式，如 *.js、*.{ts,tsx}，用于限定搜索文件类型",
    "required": false
  },
  "output_mode": {
    "type": "string",
    "enum": ["content", "files_with_matches", "count"],
    "description": "输出模式：content 显示匹配行，files_with_matches 仅显示文件名，count 显示匹配数",
    "required": false,
    "default": "files_with_matches"
  },
  "case_insensitive": {
    "type": "boolean",
    "description": "是否忽略大小写，默认为 false",
    "required": false,
    "default": false
  },
  "multiline": {
    "type": "boolean",
    "description": "是否启用多行模式，允许跨行匹配",
    "required": false,
    "default": false
  }
}
```

### glob_find

```json
{
  "pattern": {
    "type": "string",
    "description": "文件名 glob 模式，如 **/*.ts、src/**/*.js",
    "required": true
  },
  "path": {
    "type": "string",
    "description": "搜索的根目录绝对路径，未指定时使用当前工作目录",
    "required": false
  }
}
```

### semantic_search

```json
{
  "query": {
    "type": "string",
    "description": "自然语言查询，描述要查找的代码意图或行为，而非关键词",
    "required": true
  },
  "target_directories": {
    "type": "array",
    "items": {"type": "string"},
    "description": "搜索的目标目录绝对路径列表，未指定时搜索整个项目",
    "required": false
  }
}
```

## 输出格式

### grep_search 输出示例（content 模式）

```json
{
  "status": "success",
  "data": {
    "pattern": "function\\s+\\w+",
    "matches": [
      {
        "file": "d:/AI/src/index.js",
        "line_number": 12,
        "line": "function main() {",
        "match": "function main"
      },
      {
        "file": "d:/AI/src/utils.js",
        "line_number": 5,
        "line": "function helper() {",
        "match": "function helper"
      }
    ],
    "total_matches": 2,
    "files_matched": 2
  },
  "error": null
}
```

### glob_find 输出示例

```json
{
  "status": "success",
  "data": {
    "pattern": "**/*.ts",
    "files": [
      "d:/AI/src/index.ts",
      "d:/AI/src/utils/helper.ts",
      "d:/AI/tests/main.test.ts"
    ],
    "total": 3
  },
  "error": null
}
```

### semantic_search 输出示例

```json
{
  "status": "success",
  "data": {
    "query": "用户密码加密逻辑在哪里实现",
    "results": [
      {
        "file": "d:/AI/src/auth/password.ts",
        "lines": "15-32",
        "score": 0.95,
        "snippet": "export function hashPassword(password: string): string {\n  return bcrypt.hashSync(password, 10);\n}",
        "reason": "实现密码哈希加密的核心函数"
      },
      {
        "file": "d:/AI/src/middleware/auth.ts",
        "lines": "8-20",
        "score": 0.78,
        "snippet": "import { hashPassword } from '../auth/password';",
        "reason": "在认证中间件中引用密码加密函数"
      }
    ]
  },
  "error": null
}
```

## 使用约束

1. **优先使用专用工具而非 shell 命令**：禁止使用 `grep`、`rg`、`find` 等 shell 命令执行搜索，必须使用本规范定义的 `grep_search`、`glob_find` 工具。
2. **精确匹配优先使用 grep**：当需要精确文本或符号匹配时，应使用 `grep_search` 而非 `semantic_search`，后者适用于意图或行为查询。
3. **语义搜索查询规范**：`semantic_search` 的 `query` 参数应使用完整的自然语言问题（如 "用户密码在哪里加密"），而非单个关键词（如 "password"）。
4. **单一问题原则**：每次 `semantic_search` 调用只查询一个问题，复合问题应拆分为多次调用。
5. **路径必须为绝对路径**：所有 `path` 与 `target_directories` 参数必须使用绝对路径。
6. **正则语法遵循 ripgrep**：`grep_search` 的 `pattern` 参数遵循 ripgrep 正则语法，字面括号需转义（如 `interface\{\}`）。
7. **搜索范围限定**：当已知相关代码所在目录时，应通过 `path` 或 `target_directories` 限定搜索范围，避免全项目扫描。
8. **避免重复读取**：当搜索结果已返回完整代码片段时，不应再次使用 `read_file` 读取相同内容。
9. **glob 模式规范**：`glob_find` 的 `pattern` 支持 `*`、`**`、`?` 等通配符，如 `src/**/*.js` 匹配 src 目录下所有 js 文件。
10. **结果数量限制**：搜索结果默认限制 100 条，如需更多结果应通过更精确的模式或路径限定。

## 示例

### 示例 1：查找所有 TypeScript 文件并搜索特定函数

```json
// 步骤 1：查找所有 TypeScript 文件
{
  "tool": "glob_find",
  "parameters": {
    "pattern": "**/*.ts",
    "path": "d:/AI/src"
  }
}

// 步骤 2：在文件中搜索特定函数定义
{
  "tool": "grep_search",
  "parameters": {
    "pattern": "function\\s+authenticate",
    "path": "d:/AI/src",
    "glob": "*.ts",
    "output_mode": "content"
  }
}
```

### 示例 2：语义搜索查找认证逻辑实现

```json
{
  "tool": "semantic_search",
  "parameters": {
    "query": "用户登录认证流程是如何实现的",
    "target_directories": ["d:/AI/src"]
  }
}
```
