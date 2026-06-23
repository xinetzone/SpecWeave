# 文件操作工具规范

本规范定义了智能体在执行文件操作任务时所使用的工具集合、参数格式、输出约定以及使用约束，确保所有智能体在文件读写、编辑、删除和目录列举等操作上保持一致行为。

## 工具清单

| 工具名称 | 功能 | 输入参数 | 输出格式 |
|---|---|---|---|
| read_file | 读取文件内容 | file_path: string | 文件内容字符串 |
| write_file | 写入文件 | file_path: string, content: string | 成功/失败状态 |
| edit_file | 编辑文件指定部分 | file_path: string, old_string: string, new_string: string | 成功/失败状态 |
| delete_file | 删除文件 | file_path: string | 成功/失败状态 |
| list_directory | 列出目录内容 | path: string | 文件/目录列表 |

## 输入参数 Schema

### read_file

```json
{
  "file_path": {
    "type": "string",
    "description": "目标文件的绝对路径，必须为完整路径而非相对路径",
    "required": true
  }
}
```

### write_file

```json
{
  "file_path": {
    "type": "string",
    "description": "目标文件的绝对路径，若目录不存在将自动创建",
    "required": true
  },
  "content": {
    "type": "string",
    "description": "要写入文件的完整内容，将覆盖原有内容",
    "required": true
  }
}
```

### edit_file

```json
{
  "file_path": {
    "type": "string",
    "description": "目标文件的绝对路径",
    "required": true
  },
  "old_string": {
    "type": "string",
    "description": "需要被替换的原文本，必须在文件中唯一存在",
    "required": true
  },
  "new_string": {
    "type": "string",
    "description": "替换后的新文本",
    "required": true
  }
}
```

### delete_file

```json
{
  "file_path": {
    "type": "string",
    "description": "待删除文件的绝对路径，支持批量删除时传入数组",
    "required": true
  }
}
```

### list_directory

```json
{
  "path": {
    "type": "string",
    "description": "目标目录的绝对路径",
    "required": true
  }
}
```

## 输出格式

所有文件操作工具统一返回 JSON 格式结果，包含 `status`、`data`、`error` 三个字段。

### 成功响应示例

```json
{
  "status": "success",
  "data": {
    "file_path": "d:/AI/src/index.js",
    "operation": "read_file",
    "content": "文件内容字符串...",
    "size": 1024
  },
  "error": null
}
```

### 失败响应示例

```json
{
  "status": "failure",
  "data": null,
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "指定路径的文件不存在",
    "path": "d:/AI/src/missing.js"
  }
}
```

### list_directory 输出示例

```json
{
  "status": "success",
  "data": {
    "path": "d:/AI/src",
    "entries": [
      {"name": "index.js", "type": "file", "size": 1024},
      {"name": "utils", "type": "directory", "size": 0},
      {"name": "config.json", "type": "file", "size": 256}
    ]
  },
  "error": null
}
```

## 使用约束

1. **路径必须为绝对路径**：所有 `file_path` 与 `path` 参数必须使用完整绝对路径（如 `d:/AI/src/index.js`），禁止使用相对路径（如 `./src/index.js`）或包含 `~` 的路径。
2. **编辑前必须先读取文件**：调用 `edit_file` 前，必须先调用 `read_file` 读取目标文件内容，确保 `old_string` 与文件实际内容精确匹配。
3. **old_string 唯一性要求**：`edit_file` 的 `old_string` 必须在文件中唯一存在；若存在多处匹配，应提供更多上下文使其唯一，或使用 `replace_all` 选项。
4. **写入前必须读取**：对已存在文件调用 `write_file` 前，必须先调用 `read_file` 读取原内容，避免误覆盖。
5. **删除前必须确认存在**：调用 `delete_file` 前应确认文件确实存在，避免对不存在的文件执行删除操作。
6. **禁止使用 shell 命令替代**：禁止使用 `cat`、`head`、`tail`、`sed`、`awk`、`echo` 等 shell 命令执行文件操作，必须使用本规范定义的工具。
7. **敏感文件保护**：禁止读取、写入或删除 `.env`、`credentials.json`、密钥文件等敏感文件，除非任务明确要求。
8. **编码约定**：所有文件操作默认使用 UTF-8 编码，换行符遵循项目既有约定（LF 或 CRLF）。
9. **大文件处理**：对于超过 1MB 的大文件，`read_file` 应配合 `offset` 与 `limit` 参数分批读取，避免一次性加载导致内存溢出。

## 示例

### 示例 1：读取并编辑配置文件

```json
// 步骤 1：读取文件
{
  "tool": "read_file",
  "parameters": {
    "file_path": "d:/AI/config/settings.json"
  }
}

// 步骤 2：基于读取内容执行编辑
{
  "tool": "edit_file",
  "parameters": {
    "file_path": "d:/AI/config/settings.json",
    "old_string": "\"debug\": false",
    "new_string": "\"debug\": true"
  }
}
```

### 示例 2：列举目录并创建新文件

```json
// 步骤 1：列出目录内容
{
  "tool": "list_directory",
  "parameters": {
    "path": "d:/AI/src/modules"
  }
}

// 步骤 2：在目录中创建新文件
{
  "tool": "write_file",
  "parameters": {
    "file_path": "d:/AI/src/modules/new_module.js",
    "content": "export default function newModule() {\n  return {};\n}\n"
  }
}
```
