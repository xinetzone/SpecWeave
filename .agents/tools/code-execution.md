---
id: "tools-code-execution"
title: "代码执行工具规范"
source: "AGENTS.md#工具规范"
x-toml-ref: "../../.meta/toml/.agents/tools/code-execution.toml"
---
# 代码执行工具规范

本规范定义了智能体在执行终端命令、运行测试套件以及构建项目时所使用的工具集合、参数格式、输出约定以及使用约束，确保代码执行过程可控、可追溯、可审计。

## 工具清单

| 工具名称 | 功能 | 输入参数 | 输出格式 |
|---|---|---|---|
| run_command | 执行终端命令 | command: string, cwd: string | stdout, stderr, exit_code |
| run_tests | 执行测试套件 | test_path: string, framework: string | 测试结果报告 |
| build_project | 构建项目 | build_command: string | 构建日志与状态 |

## 输入参数 Schema

### run_command

```json
{
  "command": {
    "type": "string",
    "description": "要执行的终端命令字符串，必须与当前操作系统兼容",
    "required": true
  },
  "cwd": {
    "type": "string",
    "description": "命令执行的工作目录绝对路径，未指定时使用当前工作目录",
    "required": false
  },
  "blocking": {
    "type": "boolean",
    "description": "是否阻塞等待命令完成，默认为 true；长运行进程应设为 false",
    "required": false,
    "default": true
  },
  "timeout": {
    "type": "integer",
    "description": "命令执行超时时间（毫秒），超时将自动终止",
    "required": false,
    "default": 60000
  }
}
```

### run_tests

```json
{
  "test_path": {
    "type": "string",
    "description": "测试文件或测试目录的绝对路径",
    "required": true
  },
  "framework": {
    "type": "string",
    "description": "测试框架名称，如 jest、pytest、go test、mocha 等",
    "required": false
  },
  "filter": {
    "type": "string",
    "description": "测试用例过滤表达式，用于运行指定子集测试",
    "required": false
  },
  "coverage": {
    "type": "boolean",
    "description": "是否生成覆盖率报告，默认为 false",
    "required": false,
    "default": false
  }
}
```

### build_project

```json
{
  "build_command": {
    "type": "string",
    "description": "构建命令，如 npm run build、go build、mvn package 等",
    "required": true
  },
  "cwd": {
    "type": "string",
    "description": "构建执行的工作目录绝对路径",
    "required": false
  },
  "env": {
    "type": "object",
    "description": "构建所需的环境变量键值对",
    "required": false
  }
}
```

## 输出格式

### run_command 输出示例

```json
{
  "status": "success",
  "data": {
    "command": "npm install",
    "cwd": "d:/AI",
    "stdout": "added 120 packages in 5s",
    "stderr": "",
    "exit_code": 0,
    "duration_ms": 5234
  },
  "error": null
}
```

### run_tests 输出示例

```json
{
  "status": "success",
  "data": {
    "framework": "jest",
    "test_path": "d:/AI/tests",
    "total": 50,
    "passed": 48,
    "failed": 2,
    "skipped": 0,
    "duration_ms": 12000,
    "coverage": {
      "lines": 85.5,
      "branches": 72.3,
      "functions": 90.0,
      "statements": 85.0
    },
    "failures": [
      {
        "test_name": "should handle edge case",
        "file": "tests/utils.test.js",
        "error": "Expected true, received false"
      }
    ]
  },
  "error": null
}
```

### build_project 输出示例

```json
{
  "status": "success",
  "data": {
    "build_command": "npm run build",
    "cwd": "d:/AI",
    "output": "Build completed successfully",
    "artifacts": ["dist/main.js", "dist/main.css"],
    "exit_code": 0,
    "duration_ms": 30000
  },
  "error": null
}
```

## 使用约束

1. **避免交互式命令**：禁止执行需要用户交互输入的命令（如 `npm install` 不带 `--yes`、`git rebase -i`、`ssh` 等），所有命令必须能在非交互模式下完成。
2. **设置超时**：所有命令必须设置合理的超时时间，默认 60 秒；长运行命令（如构建、安装依赖）应设置 300 秒或更长超时。
3. **工作目录明确**：所有命令应明确指定 `cwd` 参数为项目根目录或相应子目录的绝对路径，避免依赖当前工作目录。
4. **禁止危险命令**：禁止执行 `rm -rf /`、`git push --force`、`git reset --hard`、`git clean -f` 等破坏性命令，除非用户明确要求。
5. **环境隔离**：长运行进程（如开发服务器）应设置 `blocking: false`，并通过状态检查工具监控其运行状态。
6. **命令兼容性**：命令必须与当前操作系统兼容；Windows 环境下使用 PowerShell 兼容命令，禁止使用 `cmd.exe` 或 `command.exe`。
7. **避免使用 shell 搜索命令**：禁止使用 `find`、`grep`、`rg` 等 shell 搜索命令，应使用专用搜索工具（见 search.md）。
8. **避免使用 shell 读写命令**：禁止使用 `cat`、`head`、`tail`、`echo`、`sed`、`awk` 等命令执行文件操作，应使用文件操作工具（见 file-operations.md）。
9. **依赖安装前确认**：执行依赖安装命令（如 `npm install`、`pip install`）前，应确认 `package.json` 或 `requirements.txt` 存在。
10. **测试失败处理**：测试失败时不应自动重试相同命令，应分析失败原因并调整后再执行。
11. **并行命令限制**：单次响应中并行执行的命令数量不应超过 5 个，避免资源争用。

## 示例

### 示例 1：安装依赖并运行测试

```json
// 步骤 1：安装项目依赖
{
  "tool": "run_command",
  "parameters": {
    "command": "npm install",
    "cwd": "d:/AI",
    "blocking": true,
    "timeout": 300000
  }
}

// 步骤 2：运行测试套件
{
  "tool": "run_tests",
  "parameters": {
    "test_path": "d:/AI/tests",
    "framework": "jest",
    "coverage": true
  }
}
```

### 示例 2：构建项目并启动开发服务器

```json
// 步骤 1：构建项目
{
  "tool": "build_project",
  "parameters": {
    "build_command": "npm run build",
    "cwd": "d:/AI"
  }
}

// 步骤 2：启动开发服务器（非阻塞）
{
  "tool": "run_command",
  "parameters": {
    "command": "npm run dev",
    "cwd": "d:/AI",
    "blocking": false
  }
}
```
