---
id: "cross-platform-bash-preflight-checklist"
title: "跨平台 Bash 脚本发布前检查清单（WSL/Linux/macOS）"
type: checklist
date: 2026-08-27
maturity: "L2-validated"
maturity_note: "从 jpman 5 个叠加 bug 修复中萃取，经端到端验证"
source: "apps/containers/jupyter-podman-rootless/bin/jpman 修复过程中发现的5个叠加bug"
related_patterns:
  - "bash-safe-dotenv-loading.md"
  - "wsl-windows-path-autoconvert.md"
  - "multi-entrypoint-config-unification.md"
  - "cross-platform-encoding-enforcement.md"
  - "wsl-docker-command-safety.md"
  - "preflight-checks-script.md"
tags: ["bash", "wsl", "cross-platform", "checklist", "crlf", "podman", "docker", "shell-script", "release-gate", "eol"]
validation_count: 2
reuse_count: 0
---

# 跨平台 Bash 脚本发布前检查清单（WSL/Linux/macOS）

> **适用场景**：编写/修改/审查需要在 WSL、Linux、macOS 运行的 bash 脚本，特别是需要处理 Windows 互操作（路径、CRLF、wsl.exe 调用）的场景
> **触发时机**：脚本功能开发完成后、提交前、PR review 时、发布前
> **检查方式**：逐项打勾；不通过项必须修复后才能发布；标记 ⚠️ 的项为高危项，任何一项不通过都会导致脚本完全不可用
> **核心教训**：`bash -n` 语法检查只能发现 20% 的问题，叠加 bug 只能通过端到端运行测试暴露

---

## 一、文件格式与编码（高危：不通过则脚本无法执行）

### 1.1 行尾格式

- [ ] **⚠️ 脚本文件本身使用 LF 行结尾**（非 CRLF）
  - 验证：`file script.sh` 应显示 `with LF line terminators`，不能有 `with CRLF line terminators`
  - 修复：`sed -i 's/\r$//' script.sh` 或编辑器配置
  - 预防：项目 `.gitattributes` 加 `*.sh text eol=lf`
  - 症状：CRLF 脚本报 `syntax error near unexpected token $'{\r''`

### 1.2 执行权限与 Shebang

- [ ] **Shebang 正确**：`#!/usr/bin/env bash` 或 `#!/bin/bash`（第一行无 BOM、无空格）
- [ ] **执行权限已设置**：`chmod +x script.sh`
- [ ] **`set -euo pipefail` 已设置**（或明确知道为什么不设置）
  - `-e`：命令失败立即退出
  - `-u`：使用未定义变量时报错
  - `-o pipefail`：管道中任意命令失败则整个管道失败

---

## 二、外部文件加载（高危：Windows 互操作最容易出 bug）

### 2.1 .env/配置文件加载

- [ ] **⚠️ 不使用 `source`/`.` 加载 .env 文件**——使用逐行安全解析（见 [bash-safe-dotenv-loading.md](../code-patterns/bash-safe-dotenv-loading.md)）
  - 反模式：`set -a; source .env; set +a`
  - 症状：反斜杠路径被破坏（`D:\spaces` → `D:spaces`）、`$` 被展开、代码注入风险
- [ ] **⚠️ 加载外部文件时剥离 CR 字符**：`line="${line//$'\r'/}"`
  - 症状：端口解析 `8888\r` 报错、密码末尾多不可见字符
- [ ] **配置加载支持引号值**：`KEY="value with spaces"` 正确去除外层引号
- [ ] **路径类变量调用 Windows→WSL 转换**（见 [wsl-windows-path-autoconvert.md](../code-patterns/wsl-windows-path-autoconvert.md)）

### 2.2 数据文件读取

- [ ] 读取任何 Windows 可能生成的文件时，处理 CRLF（即使脚本本身是 LF）
- [ ] CSV/TSV 等分隔文件使用明确的 `IFS`，不依赖默认空白分割

---

## 三、路径处理（WSL 互操作核心）

### 3.1 Windows 路径支持

- [ ] **Windows 路径输入有自动转换**：`D:\foo\bar` → `/mnt/d/foo/bar`
- [ ] **路径转换幂等**：对已是 POSIX 路径（`/`、`./`、`~/` 开头）不做二次转换
- [ ] **不硬编码依赖 `wslpath` 命令**（最小化 WSL 环境可能没有 wslpath）
- [ ] **CLI 参数中的路径也经过转换**（不仅仅是 .env 中的路径）

### 3.2 路径解析

- [ ] **相对路径使用前解析为绝对路径**：`cd "$dir" && pwd`
- [ ] **不存在的目录自动创建**：`mkdir -p "$dir"` 且在 `cd` 之前
- [ ] **`~` 展开正确**：不放在引号内时 bash 会展开，但赋值给变量后需手动处理
- [ ] **所有路径变量引用使用双引号**：`"$WORKSPACE"` 而非 `$WORKSPACE`（防止空格分词）

---

## 四、Docker/Podman CLI 使用

### 4.1 create vs run 语义

- [ ] **⚠️ `podman create`/`docker create` 不带 `-d` 标志**
  - `-d`（detach）是 `run` 的选项，`create` 本身就是"只创建不启动"
  - 症状：`Error: unknown shorthand flag: 'd' in -d`
- [ ] **`podman run`/`docker run` 需要后台运行时带 `-d`**
- [ ] **create 之后有对应的 `podman start` 调用**（两步模式），或直接用 `run -d`（一步模式），不混用

### 4.2 容器操作安全

- [ ] **容器名/镜像名不硬编码为固定值**：支持通过变量/参数覆盖
- [ ] **端口映射前检查端口是否被占用**（或让 podman/docker 报错并友好提示）
- [ ] **volume 挂载的宿主机路径在容器创建前确保存在**
- [ ] **容器停止/删除操作有幂等保护**：存在才操作，不报错

---

## 五、参数解析与子命令

### 5.1 参数解析

- [ ] **`while [[ $# -gt 0 ]]; do case "$1" in ... esac; done` 正确 shift**
- [ ] **带值参数（`-w VALUE`）正确 `shift 2`**，无值参数 `shift`
- [ ] **未知参数报错并打印 usage**，而非静默忽略
- [ ] **长选项（`--workspace`）和短选项（`-w`）均支持**

### 5.2 子命令透传

- [ ] **⚠️ 子命令（restart/stop 等）正确透传 `"$@"` 参数**
  - 反模式：`cmd_restart() { cmd_stop; cmd_start; }`（丢失 `-w` 等参数）
  - 正确：`cmd_restart() { cmd_stop; cmd_start "$@"; }`
- [ ] **help/usage 子命令不调用 check_podman 等前置检查**（用户没装 podman 也应能看帮助）

---

## 六、配置接口一致性

- [ ] **环境变量名与 `.env` 文件/Compose/SDK 对齐**（见 [multi-entrypoint-config-unification.md](../code-patterns/multi-entrypoint-config-unification.md)）
- [ ] **默认值开箱即用**：不硬编码开发者个人目录（如 `/home/user/project`）
- [ ] **历史/遗留变量名作为 fallback 兼容**：`${NEW:-${OLD:-default}}`
- [ ] **优先级文档化**：CLI flag > env var > .env > default
- [ ] **help 输出中列出所有环境变量**及其默认值

---

## 七、运行时测试（发布前必做，静态检查无法替代）

### 7.1 语法检查（必要不充分）

- [ ] **`bash -n script.sh` 通过**（零错误零警告）
- [ ] **shellcheck 通过**（如有安装）：`shellcheck script.sh`

### 7.2 端到端运行测试（关键！）

- [ ] **⚠️ `script help` 正常运行**（不依赖容器/服务也能执行）
- [ ] **⚠️ `script start`（默认配置）能成功启动**
- [ ] **`script start -w <testdir>`（CLI 参数）能正确挂载/使用指定路径**
- [ ] **配置 .env 后 `script start` 使用 .env 中的配置**（验证非默认值生效）
- [ ] **`script status` 正确显示状态**
- [ ] **`script stop` 能干净停止**
- [ ] **`script restart` 透传参数正常**（restart 后 -w 指定的路径仍然有效）
- [ ] **容器/服务健康检查通过**（healthy/running，端口可访问）

### 7.3 边界测试

- [ ] **不存在的目录自动创建**（`-w /tmp/nonexistent-test`）
- [ ] **含空格的路径**（`-w "/tmp/test workspace"`）
- [ ] **Windows 路径**（从 WSL 中：`-w "D:\spaces\test"`，如果支持）
- [ ] **重复启动**（已运行时给出提示而非报错崩溃）

---

## 八、可移植性

- [ ] **不使用 GNU 扩展选项**（如 `sed -i` 在 macOS 上需要 `sed -i ''`，或用 `perl -pi -e` 替代）
- [ ] **不硬编码 `/bin/bash` 路径**（用 `/usr/bin/env bash`）
- [ ] **`echo -e` 可能不兼容**（用 `printf` 替代彩色输出）
- [ ] **数组语法 `arr=()` 需要 bash 4+**（macOS 默认 bash 3.2，需注明最低版本要求或避免使用）
- [ ] **`${var,}` 首字母小写需要 bash 4+**（bash 3.x 用 `tr` 替代）

---

## 快速自检命令

```bash
# 1. 检查行尾
file bin/jpman
# 应显示: Bourne-Again shell script, ASCII text executable（不能有 "with CRLF"）

# 2. 语法检查
bash -n bin/jpman && echo "Syntax OK"

# 3. help 测试（不需要运行容器）
bash bin/jpman help

# 4. 检查 source 反模式
grep -n 'source.*\.env\|\. .*\.env' bin/jpman
# 不应有结果

# 5. 检查 CRLF
grep -P '\r' bin/jpman | head -5
# 不应有结果

# 6. 检查 podman create -d
grep -n 'podman create.*-d\|docker create.*-d' bin/jpman
# 不应有结果

# 7. 检查子命令参数透传
grep -A2 'cmd_restart' bin/jpman | grep '"$@"'
# cmd_restart 中应包含 "$@"
```

## 验证来源

- **验证1：jpman CLI 5-bug 修复**（2026-08-27）：脚本修复过程中连续发现 5 个叠加 bug（CRLF脚本→podman create -d→CRLF数据→变量名不一致→反斜杠路径），全部命中本清单的 ⚠️ 高危项。修复后通过所有端到端测试。✅
- **验证2：bash -n 的局限性验证**（2026-08-27）：5 个 bug 中只有 CRLF 脚本问题能被 `bash -n` 发现，其余 4 个（podman -d、变量名、反斜杠、子命令透传）全部是语义错误，语法检查无法发现。✅

## 关联模式

- [bash-safe-dotenv-loading.md](../code-patterns/bash-safe-dotenv-loading.md)：Bash 安全 .env 加载（本清单第二节的实现模式）
- [wsl-windows-path-autoconvert.md](../code-patterns/wsl-windows-path-autoconvert.md)：Windows→WSL 路径转换（本清单第三节的实现模式）
- [multi-entrypoint-config-unification.md](../code-patterns/multi-entrypoint-config-unification.md)：多入口配置统一（本清单第六节的实现模式）
- [cross-platform-encoding-enforcement.md](../code-patterns/cross-platform-encoding-enforcement.md)：跨平台编码强制（CRLF/LF 系统级治理）
- [wsl-docker-command-safety.md](../code-patterns/wsl-docker-command-safety.md)：WSL Docker 命令安全（Docker/Podman CLI 安全使用）
- [preflight-checks-script.md](../code-patterns/preflight-checks-script.md)：预检脚本模式（将本清单自动化为 CI 检查）

## Changelog

- **2026-08-27** (v1.0.0): 初始版本，从 jupyter-podman-rootless jpman CLI 修复过程中萃取，8大类33项检查，双案例验证，标记 L2。
