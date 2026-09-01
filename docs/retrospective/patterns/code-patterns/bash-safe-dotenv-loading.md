---
id: "bash-safe-dotenv-loading"
title: "Bash 安全 .env 加载模式：逐行词法解析，禁止 source"
type: code-pattern
date: 2026-08-27
maturity: L2
maturity_note: "双案例验证（jpman 完整端到端 + test_env.sh 反斜杠根因复现）"
source: "apps/containers/jupyter-podman-rootless/bin/jpman load_env() 函数"
related_patterns:
  - "env-var-alias-backward-compat.md"
  - "env-var-five-layer-protection.md"
  - "wsl-windows-path-autoconvert.md"
  - "cross-platform-encoding-enforcement.md"
tags: ["bash", "dotenv", "env-file", "crlf", "windows-path", "wsl", "cross-platform", "security", "configuration"]
validation_count: 2
reuse_count: 0
---

# Bash 安全 .env 加载模式：逐行词法解析，禁止 source

## 触发场景

- bash 脚本需要加载 `.env` 文件读取配置
- `.env` 文件可能由 Windows 工具（Python invoke、PowerShell、记事本等）生成，含 CRLF 行结尾和 Windows 反斜杠路径
- `.env` 值可能包含引号、空格、特殊字符（`$`、`` ` ``、`\`）
- 脚本在 WSL/Linux/macOS 上运行，需跨平台兼容

**识别信号**：
- 代码中出现 `source .env`、`. .env`、`set -a; source .env; set +a`、`export $(cat .env | xargs)` 等写法
- 端口号/密码等值末尾出现不可见字符（`8888\r` 类报错）
- Windows 反斜杠路径加载后路径被破坏（`D:\spaces` → `D:spaces`）

**不适用场景**：
- `.env` 文件完全由 bash 脚本自身生成和控制（保证 LF + 无特殊字符），但即使如此仍推荐使用本模式

## 问题本质

bash 的 `source`（`.`）命令将文件内容作为 **shell 代码执行**，而非词法解析。这带来三类风险：

1. **反斜杠路径破坏**：bash 将 `\s`、`\S`、`\n`（非 `\n` 换行符，而是字面 `\n`）等反斜杠序列解释为转义，非标准转义的反斜杠被**静默丢弃**，导致 `D:\spaces\SpecWeave` → `D:spacesSpecWeave`
2. **CRLF 污染**：Windows 生成的 `.env` 带 `\r\n` 行结尾，`\r` 被当作值的一部分，导致端口解析 `8888\r` 失败、密码末尾多不可见字符
3. **代码注入**：`.env` 中若包含 `` `rm -rf /` `` 或 `$(malicious_cmd)`，`source` 会执行它们——dotenv 不应具有代码执行能力

Python/Node.js 的 dotenv 库做词法分析是安全的，但 bash 的 `source` 本质是 `eval`。**不能因为"其他语言安全"就假设 bash source 也安全**。

## 核心步骤

1. **逐行 `while IFS= read -r line` 读取**，绝不使用 `source`/`eval`/`export $(cat)`
2. **剥离 CR 字符**：`line="${line//$'\r'/}"`，处理 CRLF 行结尾
3. **去除首尾空白**，跳过空行和注释行（`#` 开头）
4. **正则解析 KEY=VALUE**：`^([A-Za-z_][A-Za-z0-9_]*)=(.*)$`，匹配合法标识符
5. **剥离引号**：值两端若有单引号或双引号，去除外层引号
6. **路径后处理**：对路径类变量调用平台路径转换函数（见 [wsl-windows-path-autoconvert.md](wsl-windows-path-autoconvert.md)）

## 代码

### ❌ 反模式：source 加载

```bash
# 反模式1：source 直接执行——反斜杠被转义、$ 和 ` 被执行、CR 污染
set -a; source .env; set +a

# 反模式2：export $(cat)——不处理空格/引号/特殊字符
export $(cat .env | xargs)

# 反模式3：逐行 export 但不处理 CRLF 和引号
while IFS='=' read -r key val; do
    export "$key=$val"  # $val 含 \r、引号未剥离
done < .env
```

### ✅ 推荐模式：安全逐行解析

```bash
load_env() {
    local env_files=("$PROJECT_ROOT/.env" "$PWD/.env")
    for f in "${env_files[@]}"; do
        [[ -f "$f" ]] || continue
        while IFS= read -r line || [[ -n "$line" ]]; do
            # 1. 剥离 CR（处理 CRLF）
            line="${line//$'\r'/}"
            # 2. 去除首尾空白
            line="${line#"${line%%[![:space:]]*}"}"
            line="${line%"${line##*[![:space:]]}"}"
            # 3. 跳过空行和注释
            [[ -z "$line" || "$line" == \#* ]] && continue
            # 4. 正则解析 KEY=VALUE
            if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
                local key="${BASH_REMATCH[1]}" val="${BASH_REMATCH[2]}"
                # 5. 剥离外层引号（单/双引号）
                if [[ "$val" =~ ^\"(.*)\"$ || "$val" =~ ^\'(.*)\'$ ]]; then
                    val="${BASH_REMATCH[1]}"
                fi
                export "$key"="$val"
            fi
        done < "$f"
    done
    # 6. 路径变量后处理：Windows → WSL 转换
    if [[ -n "${WORKSPACE:-}" ]]; then
        WORKSPACE="$(_win_to_wsl_path "$WORKSPACE")"
        export WORKSPACE
    fi
}
```

关键设计点：
- `|| [[ -n "$line" ]]`：处理文件末尾无换行时最后一行被跳过的问题
- `-r` 选项：禁止 read 将反斜杠解释为续行符
- `[[ -f "$f" ]] || continue`：多个候选 .env 路径，哪个存在用哪个
- 引号剥离支持单引号和双引号（但不处理转义引号——.env 规范不需要）

## 边界条件

- **空值**：`KEY=`（等号后为空）应导出为空字符串，而非跳过
- **无值**：`KEY`（无等号）应跳过（不是合法的 KEY=VALUE）
- **export 语法**：`export KEY=VALUE` 与 `export KEY="VALUE"` 在 bash 中均可，但推荐双引号包裹防止分词
- **多等号**：`KEY=val=ue` 应将第一个等号之后的全部作为值（正则中 `(.*)$` 已处理）
- **重复 KEY**：后加载的覆盖先加载的（$PWD/.env 覆盖 $PROJECT_ROOT/.env）

## 检验标准

- [ ] `WORKSPACE=D:\spaces\SpecWeave` 加载后值完整，反斜杠不丢失
- [ ] CRLF 文件加载后值末尾无 `\r` 字符
- [ ] 带引号的值 `KEY="value with spaces"` 正确去除引号
- [ ] 含 `$` 或 `` ` `` 的值不被执行（无代码注入）
- [ ] 文件末尾无换行时最后一行不丢失
- [ ] `bash -n` 语法检查通过
- [ ] 端到端测试：加载 .env 后容器/程序能正确使用所有值

## 迁移示例

- **Docker entrypoint 脚本**：用本模式替换 `source .env` 加载数据库密码等配置
- **CI/CD bash 脚本**：加载 `.env` 作为构建参数时避免 source 注入风险
- **开发工具 CLI**：jpman、devcontainer 辅助脚本等需要在 WSL 中读取 Windows 生成的 .env
- **通用 dotenv 替代**：在无法安装 Python/Node dotenv 的最小化环境中提供安全的 .env 解析

## 验证来源

- **验证1：jpman CLI 端到端测试**（2026-08-27）：[bin/jpman](file:///d:/spaces/SpecWeave/apps/containers/jupyter-podman-rootless/bin/jpman#L90-L126) 加载含 CRLF + Windows 反斜杠路径的 .env，WORKSPACE 正确转换为 `/mnt/d/spaces/SpecWeave`，CONTAINER_NAME/SSH_PORT 等值正确加载，容器成功启动并 healthy。✅
- **验证2：反斜杠根因复现测试**（2026-08-27）：测试脚本验证 bash source 将 `\s`、`\S` 解释为转义并丢弃反斜杠，安全解析模式无此问题。✅

## 关联模式

- [wsl-windows-path-autoconvert.md](wsl-windows-path-autoconvert.md)：Windows→WSL 路径自动转换（本模式的步骤6依赖此模式）
- [env-var-alias-backward-compat.md](env-var-alias-backward-compat.md)：环境变量别名向后兼容（.env 变量名统一后处理旧名兼容）
- [env-var-five-layer-protection.md](env-var-five-layer-protection.md)：环境变量五层防护（敏感变量的安全处理）
- [cross-platform-encoding-enforcement.md](cross-platform-encoding-enforcement.md)：跨平台编码强制（CRLF/LF 处理的系统级方案）
- [multi-entrypoint-config-unification.md](multi-entrypoint-config-unification.md)：多入口配置接口统一（.env 变量名作为权威来源）

## Changelog

- **2026-08-27** (v1.0.0): 初始版本，从 jupyter-podman-rootless jpman CLI 修复萃取，双案例验证（端到端容器启动 + 反斜杠根因复现），标记 L2。
