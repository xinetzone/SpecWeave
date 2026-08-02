# 敏感信息脱敏规范与误报防控指南

**版本**：v1.0  
**更新日期**：2026-06-02  
**适用范围**：SpecWeave 项目内所有文档、脚本、配置文件  
**关联工具**：[`check-sensitive-info.py`](../../scripts/check-sensitive-info.py)

---

## 1. 概述

`check-sensitive-info.py` 脚本用于扫描代码仓库中的敏感信息（个人路径、手机号、邮箱、API Key、密码、内网IP等），并对个人路径提供自动修复能力。为平衡安全检测与开发效率，本规范定义了：

- 真实敏感路径的修复标准
- 误报分类与白名单机制
- Shell命令语法保护规则
- Dockerfile容器路径保护规则
- 测试验证标准

---

## 2. 真实敏感路径修复（5处）

本次修复的5处真实个人路径位于文档示例中，均已替换为标准化占位符：

| 文件 | 修复前（个人路径） | 修复后（标准占位符） | 风险等级 |
|------|--------|--------|----------|
| `powershell-nativebuild-faq.md` | `<个人主目录>\` | `<USER_HOME>\` | MEDIUM |
| `powershell-nativebuild-faq.md` | `<个人主目录>\.conda\envs\builder` | `%USERPROFILE%\.conda\envs\builder` | MEDIUM |
| `powershell-nativebuild-faq.md` | `<个人主目录>\anaconda3\envs\vsbuild\python.exe` | `%USERPROFILE%\anaconda3\envs\vsbuild\python.exe` | MEDIUM |
| `multi-strategy-auto-discovery.md` | `<个人主目录>\.trae-cn\memory` | `<memory_folder>` | MEDIUM |
| `...`（其他历史文档） | 个人路径 | `<USER_HOME>` / `~/` / `%USERPROFILE%` | MEDIUM |

**修复标准**：
- Windows路径：使用 `%USERPROFILE%` 或 `<USER_HOME>\`
- Unix/Linux/macOS路径：使用 `~/` 或 `$HOME/`
- 项目内部路径：使用项目相对路径
- 文档示例中说明性路径：使用通用占位符（如 `<memory_folder>`）

---

## 3. 误报分类与防控规则（16类）

### 3.1 Shell命令语法误报（4类）

正则贪婪匹配导致 Shell 命令中的 `/home/` 目录列举被误判为个人路径。

| 误报模式 | 示例 | 防控机制 |
|----------|------|----------|
| 命令链式调用 | `ls -la /home/ && echo '---'` | `_is_shell_command_context()` 检测 `&&`/`\|\|`/`;`/`\|` |
| 目录列举通配符 | `for d in /home/*/; do ...` | 检测路径后紧跟 `*` 通配符 |
| 多路径参数 | `ls /home/ /etc/passwd` | 检测路径后空格+另一根路径 |
| WSL命令封装 | `wsl -d distro -- bash -c "ls /home/"` | shell上下文模式匹配 |

**保护逻辑**：路径匹配结束后，检查后续文本是否为 shell 操作符（`&&`/`||`/`;`/`|`）、通配符（`*`）或其他命令关键字（`ls`/`cd`/`echo`/`cat`/`rm`/`cp`/`mv`），若是则跳过此匹配。

### 3.2 Dockerfile容器路径误报（3类）

Dockerfile 中的容器内固定用户路径不应被脱敏（这些路径在构建时创建，不泄露宿主机信息）。

| 误报模式 | 示例 | 防控机制 |
|----------|------|----------|
| ENTRYPOINT入口点 | `ENTRYPOINT ["/home/ai/entrypoint.sh"]` | `_is_dockerfile_context()` 检测Dockerfile指令 |
| ENV环境变量 | `ENV PATH="/home/conda_user/miniconda3/bin:$PATH"` | 仅在Dockerfile文件中生效 |
| RUN安装命令 | `RUN bash install.sh -b -p /home/conda_user/` | 支持所有Dockerfile指令（FROM/RUN/CMD/COPY等） |

**保护逻辑**：文件名为 `Dockerfile` 或 `*.dockerfile` 时，检测行首是否为Dockerfile指令（FROM/RUN/CMD/ENTRYPOINT/ENV/ARG/WORKDIR/COPY/ADD/USER/VOLUME/EXPOSE/LABEL/MAINTAINER/ONBUILD/STOPSIGNAL/HEALTHCHECK/SHELL），若是则跳过路径检测。

### 3.3 文档占位符用户名误报（7类）

教程/示例文档中使用的通用示例用户名不是真实个人路径。

| 误报模式 | 示例 | 防控机制 |
|----------|------|----------|
| 通用第二人称 | `/home/you/`, `C:\Users\you\` | 白名单: `you`, `yourname`, `your_name` |
| 英文占位名 | `/home/john/`, `C:\Users\John Doe\` | 白名单: `john`, `jane`, `john doe`, `jane doe` |
| 中文占位名 | `C:\Users\用户名\Documents` | 白名单: `用户名`, `你的用户名`, `用户名目录` |
| 示例用户 | `/home/dev/`, `/home/otheruser/` | 白名单: `dev`, `otheruser` |
| 拼音示例名 | `/home/zhangsan/`, `/home/lisi/` | 白名单: `zhangsan`, `lisi`, `wangwu`, `zhaoliu` |
| 容器固定用户 | `/home/ai/`, `/home/conda_user/` | 白名单: `ai`, `conda_user`, `conda` |
| 模板变量 | `${user}`, `<user>`, `{username}` | 正则模式: `^[<${].*[>}]$` |

### 3.4 系统目录误报（2类）

操作系统内置的系统账户目录不属于个人信息。

| 误报模式 | 示例 | 防控机制 |
|----------|------|----------|
| Windows系统账户 | `C:\Users\Public\`, `C:\Users\Default\` | Windows白名单: `public`, `default`, `default user`, `defaultuser0`, `all users` |
| Unix/Linux系统账户 | `/root/.bashrc`, `/home/admin/` | Unix白名单: `root`, `admin`, `shared`, `guest`, `user` |

---

## 4. 白名单用户名清单

### 4.1 Windows 系统/占位符用户名白名单

```python
SYSTEM_WIN_USERS = {
    # Windows 内置系统账户
    "public", "default", "all users", "default user", "defaultuser0",
    # 通用示例账户
    "user", "admin", "xxx", "test", "demo", "shared", "guest",
    "wdagutilityaccount",
    # 模板变量
    "$user", "{username}", "<user>",
    # 文档占位符（教程/示例通用用户名）
    "you", "yourname", "your_name", "otheruser", "john doe", "john",
    "jane", "jane doe", "用户名", "你的用户名", "用户名目录",
}
```

### 4.2 Unix/Linux/macOS 系统/占位符用户名白名单

```python
SYSTEM_UNIX_USERS = {
    # Unix/Linux 内置系统账户
    "user", "admin", "xxx", "test", "demo", "shared", "root",
    # 模板变量
    "$user", "{username}", "<user>",
    # 文档占位符（教程/示例通用用户名）
    "you", "yourname", "your_name", "otheruser", "dev", "zhangsan",
    "lisi", "wangwu", "zhaoliu", "john", "jane", "john doe",
    # Docker/CI 容器内固定用户
    "ai", "conda_user", "conda",
}
```

---

## 5. 正则防护机制详解

### 5.1 用户名有效性验证（`_is_valid_path_username`）

路径正则匹配到用户名后，需通过以下验证才会被判定为真实个人路径：

1. **非空检查**：用户名不能为空
2. **点号过滤**：纯点号（`.`/`..`/`...`）或全点号用户无效
3. **模板变量过滤**：以`<`/`${`/`{`开头并以`>`/`}`结尾的模板变量无效
4. **特殊字符过滤**：包含以下Shell/文件名非法字符的用户名无效：
   - Windows非法文件名字符：`` \ ` / < > : " | ? * ``
   - Shell特殊字符：`{ } ( ) $ ; & | # ' "`
5. **边界检查**：
   - 不能以空格开头或结尾
   - 不能以`-`/`'`/`"`开头

### 5.2 Shell命令上下文检测（`_is_shell_command_context`）

在路径匹配结束位置检查后续文本：

```python
_SHELL_CMD_AFTER_PATH_RE = re.compile(
    r'^\s*(?:&&|\|\||;|\||\)|&\s*echo|\s+ls\s|\s+cd\s|\s+echo\s|\s+cat\s|\s+rm\s|\s+cp\s|\s+mv\s)',
)
```

检测场景：
- `&&`/`||`/`;`/`|` 命令连接符
- `& echo` 后台执行+回显
- 空格后跟常见命令名（ls/cd/echo/cat/rm/cp/mv）
- 路径后紧跟 `*` 通配符
- 路径后空格+另一根路径（多参数）

### 5.3 Dockerfile上下文检测（`_is_dockerfile_context`）

仅对 `Dockerfile` 和 `*.dockerfile` 文件生效，检测行首是否为标准Dockerfile指令（不区分大小写）。

---

## 6. 编写文档时的脱敏规范

### 6.1 路径引用规范

| 场景 | Windows | Unix/macOS | 错误示例 |
|------|---------|------------|----------|
| 用户主目录 | `%USERPROFILE%` | `~/` 或 `$HOME/` | `C:\Users\<真实用户名>\` |
| 项目目录 | 相对路径 `./` 或 `<repo_root>/` | 相对路径 `./` | 硬编码绝对路径 |
| 文档示例 | `<USER_HOME>\` 或 `C:\Users\<用户名>\` | `/home/<用户名>/` | 使用真实用户名 |
| 配置文件 | `%APPDATA%\`、`%LOCALAPPDATA%\` | `~/.config/`、`~/.local/` | 硬编码个人路径 |

### 6.2 例外处理（nosec标记）

确需在文档中保留真实路径格式（如测试用例、错误日志示例）时，在行尾添加nosec标记：

```python
path = "C:\\Users\\xinzo\\anaconda3"  # nosec: 测试用例真实路径样本
```

支持的nosec标记格式：
- Python/Shell: `# nosec` 或 `# sensitive-ignore`
- C/Java/JS: `// nosec`
- HTML/XML: `<!-- nosec -->`
- SQL/Lua: `-- nosec`
- Mermaid: `%% nosec`

### 6.3 新增占位符用户名流程

若文档中频繁使用某个示例用户名导致误报，按以下流程添加到白名单：

1. 确认该用户名是**通用示例**而非真实个人用户名
2. 确认该用户名在**多个文档/场景**中出现（非一次性使用）
3. 在 `SYSTEM_WIN_USERS` 或 `SYSTEM_UNIX_USERS` 中添加
4. 在测试文件 `tests/test_sensitive_info_shell.Tests.py` 中添加对应测试用例
5. 运行测试验证（`python tests/test_sensitive_info_shell.Tests.py`）

---

## 7. 测试验证标准

### 7.1 测试套件位置

- **新增误报测试**：[`tests/test_sensitive_info_shell.Tests.py`](../../scripts/tests/test_sensitive_info_shell.Tests.py)
- **原有综合测试**：`tests/test_sensitive_info.py`

### 7.2 测试覆盖要求

每次修改正则表达式或白名单后，必须运行以下测试：

```bash
cd .agents/scripts
python tests/test_sensitive_info_shell.Tests.py
python tests/test_sensitive_info.py
```

### 7.3 核心测试用例清单（46项）

| 测试组 | 用例数 | 验证目标 |
|--------|--------|----------|
| Shell命令上下文检测 | 8 | `&&`/`\|\|`/`;`/`\|`/`*`/多路径参数/正常子路径 |
| 用户名有效性验证 | 12 | 正常用户名+shell特殊字符过滤 |
| Dockerfile上下文检测 | 6 | Dockerfile指令识别+非Dockerfile文件排除 |
| 端到端扫描误报修复 | 20 | Shell命令/Dockerfile/占位符/真实路径/系统路径 |

**验收标准**：所有测试用例100%通过，且全量扫描（`python check-sensitive-info.py --path .agents`）无新增MEDIUM及以上级别个人路径误报。

---

## 8. 常见问题排查

### Q1: 我的合法路径被误报了怎么办？

1. 检查用户名是否包含Shell特殊字符（`&|;$`等）——正常用户名不应包含这些字符
2. 如果是文档示例用户名，参考6.3节流程添加到白名单
3. 如果是单行特例，添加 `# nosec` 标记
4. 如果是Shell命令中的目录操作，检查是否应该用上下文保护机制

### Q2: 真实个人路径没有被检测到？

1. 检查路径格式是否为标准的 `C:\Users\<用户名>\` 或 `/home/<用户名>/` 格式
2. 检查用户名是否被错误加入白名单
3. 检查该行是否包含nosec标记
4. 检查是否在代码块内（```...```代码块内的路径默认跳过）

### Q3: Dockerfile中自己的路径被检测了？

Dockerfile上下文检测仅对文件名为 `Dockerfile` 或 `*.dockerfile` 的文件生效。如果是 `.sh` 脚本中的容器路径，属于脚本内容，需通过白名单或nosec处理。

---

## 9. 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-06-02 | 初始版本：定义5处修复标准、16类误报防控规则、白名单清单、测试标准 |
