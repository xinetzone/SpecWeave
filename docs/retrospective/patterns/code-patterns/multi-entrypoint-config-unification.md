---
id: "multi-entrypoint-config-unification"
title: "多入口配置接口统一模式：命名权威+fallback链+优先级文档"
type: code-pattern
date: 2026-08-27
maturity: L2
maturity_note: "双案例验证（jpman CLI+compose.yaml+invoke Python 三入口对齐 + 环境变量名兼容）"
source: "apps/containers/jupyter-podman-rootless/ 三后端配置接口对齐修复"
related_patterns:
  - "config-source-priority-explicitness.md"
  - "env-var-alias-backward-compat.md"
  - "bash-safe-dotenv-loading.md"
  - "credential-multi-source-priority.md"
tags: ["configuration", "multi-entrypoint", "interface-alignment", "backward-compatibility", "naming", "cli", "env-var", "fallback-chain"]
validation_count: 2
reuse_count: 0
---

# 多入口配置接口统一模式：命名权威+fallback链+优先级文档

## 触发场景

- 一个项目有**多个使用入口**（CLI 工具、Python SDK、Docker Compose、Web UI、shell 脚本）
- 用户在 `.env` 或配置文件中设置的变量，通过某个入口启动时"配置了但没用"
- 不同入口使用不同的变量名前缀（如 `JUPYTER_WORKSPACE` vs `WORKSPACE`、`APP_PORT` vs `PORT`）
- 默认值硬编码为开发者自己的机器路径（如 `$HOME/MyProject`），其他用户开箱不可用
- 新增 CLI 工具后，与已有 compose/SDK 的配置接口不一致

**识别信号**：
- 代码中同时出现 `${JUPYTER_XXX:-default}` 和 `${XXX:-default}` 但没有统一
- 新工具定义了自己的 `TOOL_*` 前缀变量名，而 `.env` 用无前缀短名
- `grep -r "WORKSPACE\|JUPYTER_WORKSPACE\|CONTAINER_NAME\|JUPYTER_CONTAINER_NAME" .` 返回多种命名
- 用户反馈"我在 .env 配了 XXX 为什么不生效？"

**不适用场景**：
- 单一入口项目（只有一个 CLI 或只有一个 SDK）
- 各入口设计上独立配置、不需要共享配置的场景

## 问题本质

多入口项目的核心矛盾是「**配置命名谁说了算**」和「**用户从哪个入口配置最自然**」。后添加的入口（如"零依赖 CLI"）为了"独立性"自行定义一套变量名，但用户已经按最早入口的命名在 `.env` 中配置了，导致：

1. **命名分叉**：compose.yaml 用 `WORKSPACE`，invoke 用 `WORKSPACE`，但 CLI 用 `JUPYTER_WORKSPACE`——三个入口三套名字
2. **默认值耦合**：默认值硬编码为开发者个人目录（`$PROJECT_ROOT/../../..` 指向 SpecWeave 根），其他用户克隆后开箱即错
3. **优先级不透明**：CLI flag 和环境变量哪个生效？`.env` 和默认值谁优先？没有文档
4. **零依赖 ≠ 零对齐**："不依赖 Python/SDK"不等于"可以忽略已有配置体系"——用户关心的是"配一次到处能用"，而不是"每个工具配一遍"

这与 [配置源优先级显式化](config-source-priority-explicitness.md) 互补：该模式关注**合并语义与深度**（嵌套配置如何覆盖），本模式关注**跨入口命名对齐**（同一配置项在不同入口叫同一个名字）。

## 核心步骤

### 步骤 1：定义命名权威（Single Source of Truth for Naming）

以 `.env` 文件中的变量名作为**唯一权威命名**。因为：
- `.env` 是用户最常编辑的配置文件
- compose.yaml 和 invoke 都从 `.env` 读取变量
- CLI/SDK 应适应 `.env`，而非反过来

```bash
# .env 中的名字 = 权威名
WORKSPACE=./workspace          # 权威名：WORKSPACE
CONTAINER_NAME=jupyter-podman  # 权威名：CONTAINER_NAME
SSH_PORT=2222                  # 权威名：SSH_PORT
```

### 步骤 2：所有入口对齐权威名

- **compose.yaml**：直接使用权威名（`${WORKSPACE:-./workspace}`）
- **CLI（bash）**：`load_env` 后直接读取权威名
- **CLI（PowerShell）**：`Import-EnvFile` 后直接读取权威名
- **SDK/invoke（Python）**：`os.getenv("WORKSPACE")` 读取权威名

### 步骤 3：历史变量名 fallback 兼容

旧名不直接删除，而是通过 fallback 链兼容：

```bash
# bash: 新名 > 旧名 > 默认值
CONTAINER_NAME="${JUPYTER_CONTAINER_NAME:-${CONTAINER_NAME:-jupyter-default}}"
SSH_PORT="${JUPYTER_SSH_PORT:-${SSH_PORT:-2222}}"
JUPYTER_PORT="${JUPYTER_PORT:-${JUPYTER_PORT:-8888}}"
WORKSPACE="${WORKSPACE:-${JUPYTER_WORKSPACE:-$PROJECT_ROOT/workspace}}"
```

注意 fallback 顺序：**新名（权威名）> 旧名（兼容）> 默认值**。这样用户显式设置新名时旧名被忽略，旧用户设置旧名仍能工作。

### 步骤 4：默认值开箱即用

默认值使用 `$PROJECT_ROOT/subdir` 等相对路径，**绝不硬编码开发者个人目录**：

```bash
# ❌ 错误：硬编码开发者路径
WORKSPACE="${WORKSPACE:-$PROJECT_ROOT/../../..}"

# ✅ 正确：项目内自包含默认值
WORKSPACE="${WORKSPACE:-$PROJECT_ROOT/workspace}"
```

### 步骤 5：优先级文档化

在帮助信息和文档中明确优先级链：

```
Priority: -w/--workspace CLI flag > WORKSPACE env var > JUPYTER_WORKSPACE env var (compat)
          > .env file WORKSPACE > $PROJECT_ROOT/workspace default
```

```bash
# jpman help 输出
echo -e "${C_BOLD}Workspace:${C_RESET}    $WORKSPACE"
echo "  (override: -w PATH, env WORKSPACE, or .env WORKSPACE)"
```

### 步骤 6：跨入口验证

用"干净环境"测试：
1. 只设置 `.env`，通过 CLI 启动 → 配置生效
2. 只设置环境变量，通过 CLI 启动 → 配置生效
3. 只使用 CLI flag，不设环境变量 → flag 生效
4. 什么都不设 → 默认值开箱可用
5. 同时设置 `.env` 和环境变量 → 环境变量优先
6. 通过 compose 启动 → `.env` 中配置生效（compose 本身支持）

## 代码

### ❌ 反模式

```bash
# 反模式1：每个入口自创变量名，与 .env 不对齐
# jpman 中（自创 JUPYTER_* 前缀，与 .env 中的短名不一致）
CONTAINER_NAME="${JUPYTER_CONTAINER_NAME:-jupyter-default}"  # 永远读不到 .env 中的 CONTAINER_NAME
WORKSPACE="${JUPYTER_WORKSPACE:-$PROJECT_ROOT/../../..}"      # 默认值硬编码开发者目录

# 反模式2：默认值硬编码开发者个人路径
WORKSPACE="${WORKSPACE:-/home/xinzo/specweave}"  # 其他用户直接报错

# 反模式3：有 fallback 但顺序错误（旧名优先于新名，导致新名无法覆盖）
WORKSPACE="${JUPYTER_WORKSPACE:-${WORKSPACE:-./workspace}}"  # 旧名优先，新名被忽略

# 反模式4：CLI help 不列出环境变量配置方式，用户只能读源码
```

### ✅ 推荐模式：权威名+fallback链+文档化优先级

```bash
# 1. 安全加载 .env（见 bash-safe-dotenv-loading.md）
load_env

# 2. fallback 链：权威名 > 旧兼容名 > 开箱即用默认值
CONTAINER_NAME="${JUPYTER_CONTAINER_NAME:-${CONTAINER_NAME:-jupyter-default}}"
IMAGE="${JUPYTER_IMAGE:-${IMAGE_TAG:-localhost/jupyter-podman-rootless:latest}}"
SSH_PORT="${JUPYTER_SSH_PORT:-${SSH_PORT:-2222}}"
JUPYTER_PORT="${JUPYTER_PORT:-${JUPYTER_PORT:-8888}}"
PASSWORD="${JUPYTER_PASSWORD:-${USER_PASSWORD:-devpass123}}"
WORKSPACE="${WORKSPACE:-${JUPYTER_WORKSPACE:-$PROJECT_ROOT/workspace}}"

# 3. CLI 参数覆盖环境变量
while [[ $# -gt 0 ]]; do
    case "$1" in
        -w|--workspace) WORKSPACE="$2"; shift 2 ;;
    esac
done

# 4. 路径转换和解析（见 wsl-windows-path-autoconvert.md）
WORKSPACE="$(_win_to_wsl_path "$WORKSPACE")"

# 5. help 文档中列出所有配置方式
echo "Environment variables:"
echo "  WORKSPACE            Host directory to mount (default: ./workspace)"
echo "  CONTAINER_NAME       Container name (default: jupyter-podman)"
echo "  SSH_PORT             SSH port (default: 2222)"
```

## 边界条件

- **新增配置项**：直接使用权威名（无前缀），不要为新入口再发明新前缀
- **废弃旧名**：在 release notes 中标注 deprecated，至少保留一个版本的兼容，再移除
- **机密变量**（密码、Token）：fallback 链同样适用，但不应在 help 中打印默认值（见 [env-var-five-layer-protection.md](env-var-five-layer-protection.md)）
- **布尔变量**：统一处理 `yes/no/true/false/1/0` 多种写法
- **跨语言对齐**：Python/Node.js/Go SDK 也应读取相同的环境变量名，不要各搞一套

## 检验标准

- [ ] `.env` 中设置的变量通过所有入口启动都能生效
- [ ] 旧变量名（如有）仍然可用，但权威名优先
- [ ] 默认值不依赖开发者个人目录，`git clone` 后开箱即用
- [ ] help/文档中明确列出所有环境变量和优先级
- [ ] CLI flag 优先级高于环境变量（且文档说明）
- [ ] 新入口（CLI/SDK）不发明新的变量名前缀
- [ ] 至少一次端到端验证：从 `.env` 配置→启动→验证配置生效

## 迁移示例

- **容器工具**：docker/podman CLI、compose.yaml、Python SDK 三入口变量名统一
- **开发工具**：CLI、VS Code 扩展、Web UI 共享同一套配置变量名
- **微服务**：API 服务同时支持 CLI 启动、Docker Compose、K8s ConfigMap/环境变量，变量名一致
- **CI/CD 工具**：命令行参数、环境变量、配置文件三个配置源统一命名

## 验证来源

- **验证1：jpman+compose+invoke 三入口对齐**（2026-08-27）：修复前 jpman 用 `JUPYTER_*` 前缀读不到 `.env` 中的 `CONTAINER_NAME`/`SSH_PORT`/`WORKSPACE`；修复后三入口统一使用 `.env` 短名，`JUPYTER_*` 作为 fallback 兼容。容器使用 `.env` 配置成功启动。✅
- **验证2：默认值开箱即用验证**（2026-08-27）：修复前默认 WORKSPACE 指向 SpecWeave 根目录（硬编码 `../../..`），修复后指向 `$PROJECT_ROOT/workspace`，不依赖特定目录结构。✅

## 关联模式

- [config-source-priority-explicitness.md](config-source-priority-explicitness.md)：配置源优先级显式化（嵌套配置合并语义，本模式的互补模式）
- [env-var-alias-backward-compat.md](env-var-alias-backward-compat.md)：环境变量别名向后兼容（单变量重命名场景的特化方案）
- [bash-safe-dotenv-loading.md](bash-safe-dotenv-loading.md)：Bash 安全 .env 加载（本模式步骤1的实现基础）
- [credential-multi-source-priority.md](credential-multi-source-priority.md)：凭证多源优先级（敏感配置的多源优先级特化）

## Changelog

- **2026-08-27** (v1.0.0): 初始版本，从 jupyter-podman-rootless 三入口配置对齐修复萃取，双案例验证（三入口对齐+默认值开箱即用），标记 L2。
