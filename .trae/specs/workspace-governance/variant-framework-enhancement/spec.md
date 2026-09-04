---
status: "draft"
id: variant-framework-enhancement
title: "Variant Framework 通用组件提取与增强"
source: "portable.Dockerfile 可复用组件提取 + 现有 variant-framework 增强"
date: 2026-08-17
---

# Spec: Variant Framework 通用组件提取与增强

## 1. 背景与目标

### 1.1 背景

现有 `devcontainer-base/variants/` 体系已拥有 `variant-framework.sh` 共享框架（10个模块），提供日志、计时、镜像源、分组安装等基础能力。

`external/chaos/ai/portable.Dockerfile` 实现了一套独立的多阶段构建，包含多个有价值的通用模式：

* 自定义用户创建/重命名（支持自定义 UID/GID）

* Shell 环境标准化配置（umask、bashrc、PATH持久化）

* Jupyter 自定义内核注册

* 文档容器内部署

* PIP\_USER 构建/运行时分离

这些模式在其他变体/项目中也可能需要，但目前硬编码在 portable.Dockerfile 中，无法复用。

### 1.2 目标

从 portable.Dockerfile 中提取可复用的通用组件，整合到 `variants/shared/lib/` 框架中：

1. **新增4个共享模块**：用户管理、Shell环境配置、Jupyter内核注册、文档部署
2. **增强2个现有模块**：安装辅助（PIP\_USER模式）、验证模块（sshd语法检查、自定义用户验证）
3. **保持100%向后兼容**：现有变体无需任何修改即可继续工作
4. **更新模板与文档**：`_template/Dockerfile` 展示新功能使用方法，编写共享库使用文档

### 1.3 非目标

* 不修改现有任何变体（conda-llvm/onnx-dev/onnx-pytorch/onnx-quantized/torch-dev/ai-dev）的Dockerfile

* 不改变现有框架模块的默认行为

* 不强制使用新功能（新模块函数需显式调用）

* 不处理 portable.Dockerfile 中 Chaos AI 特有的业务逻辑（NPU工具链、专有脚本等）

## 2. 需求规格

### 2.1 新增模块：user-management.sh（用户管理）

**职责**：提供可配置的目标用户管理能力，支持自定义用户名/UID/GID、用户重命名、sudo配置。

**环境变量**（所有变量有合理默认值）：

| 变量               | 默认值       | 说明                    |
| ---------------- | --------- | --------------------- |
| `DEVTARGET_USER` | `devuser` | 目标用户名                 |
| `DEVTARGET_UID`  | `1000`    | 目标用户 UID              |
| `DEVTARGET_GID`  | `1000`    | 目标用户 GID              |
| `GRANT_SUDO`     | `yes`     | 是否授予 sudo NOPASSWD 权限 |
| `USER_PASSWORD`  | （空）       | 用户密码（可选，默认不设置密码）      |

**API 函数**：

```bash
# 一键配置目标用户（创建/重命名 + sudo + 密码）
# 智能处理：存在同名用户→重命名；UID/GID冲突→自动选择下一个可用ID
variant_configure_target_user

# 原子函数（可独立调用）
variant_create_user <name> <uid> <gid> [additional_groups]
variant_rename_user <old_name> <new_name>
variant_configure_sudo <username> [yes|no]
variant_set_user_password <username> <password>  # ⚠️ 安全警告：密码会进入镜像层
variant_lock_user_password <username>  # 锁定密码，仅允许SSH密钥登录
variant_get_target_user_info  # 输出最终用户名/UID/GID到stdout
variant_get_target_user_group  # 输出最终用户组名
```

**关键行为**：

* 默认用户 `devuser` 与现有框架完全一致（向后兼容）

* UID/GID 已被占用时：自动递增查找可用 ID，输出 WARN 日志

* 重命名 devuser→ai 场景：正确处理主目录移动、组名修改

* 用户自动加入 `docker` 和 `sudo` 组

* sudoers 文件权限设置为 0440

**安全约束**：

* `variant_set_user_password` 文档必须明确警告：构建期设置密码会写入镜像层历史，推荐运行时设置或使用SSH密钥

* 提供 `variant_lock_user_password` 函数禁用密码登录（更安全的默认）

### 2.2 新增模块：shell-profile.sh（Shell 环境配置）

**职责**：标准化 Shell 环境配置（umask、bashrc、PATH、SSH环境）。

**API 函数**：

```bash
# 配置全局 umask（写入4个位置：/etc/profile、/etc/bash.bashrc、用户.bashrc、root .bashrc）
# 幂等：使用标记注释包裹，重复调用不会重复追加
variant_configure_umask <umask_value>  # 默认 0022

# 追加内容到目标用户 bashrc（幂等）
variant_append_user_bashrc <content> [username]  # username 默认 DEVTARGET_USER

# 追加内容到 root bashrc（幂等）
variant_append_root_bashrc <content>

# 持久化 PATH 条目到 /etc/environment（幂等）
# position: prepend（默认，高优先级）或 append
variant_persist_path <path_entry> [position]

# 配置 SSH ~/.ssh/environment 文件（设置SSH登录后的环境变量）
variant_configure_ssh_env <username> [env_vars...]  # env_vars 格式: KEY=VALUE

# 一键配置标准 Shell 环境（推荐使用）
variant_configure_shell_profile [umask_value]  # 默认 umask 0022
```

**幂等性保证**：

* 所有追加操作使用标记注释 `# >>> variant-framework >>>` 和 `# <<< variant-framework <<<` 包裹

* 重复调用时先移除旧内容再追加，确保不重复

**默认行为**：

* 不自动调用任何函数（保持现有环境不变）

* 变体需要显式调用才会修改 Shell 配置

### 2.3 新增模块：jupyter-kernel.sh（Jupyter 内核注册）

**职责**：通用 Jupyter 自定义内核注册，支持多位置同步、自定义 Python 路径、自定义环境变量。

**API 函数**：

```bash
# 注册自定义 Jupyter 内核
# 参数：
#   kernel_name    - 内核目录名（如 npu、pytorch、ai-dev）
#   display_name   - Jupyter UI 显示名（如 "Python 3 (NPU Dev)"）
#   python_path    - 内核使用的 Python 解释器绝对路径
#   extra_env...   - 额外环境变量（0或多个，格式 KEY=VALUE）
#
# 自动检测并注册到所有存在的 Jupyter 路径：
#   - /opt/venv/share/jupyter/kernels/（venv 环境，优先）
#   - /opt/conda/share/jupyter/kernels/（conda base 环境）
#   - /opt/conda/envs/main/share/jupyter/kernels/（conda main 环境）
variant_register_jupyter_kernel <kernel_name> <display_name> <python_path> [extra_env...]

# 验证内核已注册
verify_jupyter_kernel <kernel_name> [jupyter_base_path]
```

**示例**：

```bash
variant_register_jupyter_kernel "npu" "Python 3 (NPU Dev)" "/opt/conda/bin/python" \
    "PYTHONPATH=/workspace/npu_tvm/python:/workspace/npuusertools" \
    "OMP_NUM_THREADS=4" \
    "KMP_DUPLICATE_LIB_OK=TRUE"
```

**关键行为**：

* 自动创建 kernel.json，包含正确的 argv 和 env

* 自动设置权限：内核目录和文件归 DEVTARGET\_USER 所有

* 自动检测存在的 Jupyter 数据路径，不存在则跳过（不报错）

* kernel.json 中默认 PATH 包含 /opt/conda/bin（可通过 extra\_env 覆盖）

### 2.4 新增模块：docs.sh（文档部署）

**职责**：将文档复制到容器内 `/opt/docs/` 目录并设置正确权限。

**API 函数**：

```bash
# 部署文档到容器内 /opt/docs/
# 参数：
#   src_path     - 源路径（文件或目录，相对于构建上下文）
#   dest_subdir  - 目标子目录（可选，默认放到 /opt/docs/ 根目录）
variant_deploy_docs <src_path> [dest_subdir]
```

**关键行为**：

* 自动创建目标目录

* 复制后设置 `chmod -R a+rX /opt/docs/`（所有用户可读，目录可遍历）

* 文件保留在构建层，不清理

### 2.5 增强模块：install-helpers.sh

**新增函数**（不修改现有函数）：

```bash
# 切换到构建模式：PIP_USER=0
# 包会安装到 /opt/conda 全局位置（root:root，所有用户可读）
variant_pip_build_mode

# 切换到运行时模式：PIP_USER=1
# 用户可通过 pip install --user 安装到 ~/.local
variant_pip_runtime_mode
```

\*\*现有 `variant_activate_base_env` 已包含 `PIP_USER=0` 设置，保持不变。

### 2.6 增强模块：verify.sh

**新增函数**：

```bash
# 验证 sshd 配置文件语法正确（sshd -t）
verify_ssh_config

# 验证指定用户存在且可访问 conda 环境（通用版本）
verify_user_access [username]  # username 默认 DEVTARGET_USER

# 验证 Jupyter 内核已注册
verify_jupyter_kernel <kernel_name> [jupyter_base_path]
```

**向后兼容**：

* 保留现有 `verify_devuser_access` 函数，作为 wrapper 调用 `verify_user_access devuser`

* 现有 `verify_base_services` 保持不变，不自动调用 sshd 语法检查（变体可显式调用）

### 2.7 增强现有模块的硬编码问题

更新以下现有模块使用 `DEVTARGET_USER` 变量替代硬编码 `devuser`，同时保留旧函数作为 wrapper：

| 模块               | 更新内容                                                                                                       |
| ---------------- | ---------------------------------------------------------------------------------------------------------- |
| `permissions.sh` | `ensure_devuser_bashrc` → wrapper 调用 `ensure_user_bashrc $DEVTARGET_USER`；新增通用 `ensure_user_bashrc <user>` |
| `mirror.sh`      | pip 镜像配置使用 DEVTARGET\_USER，同时保留 devuser 兼容逻辑                                                               |
| `build-info.sh`  | 元数据中记录实际用户名而非硬编码                                                                                           |

**wrapper 模式保证向后兼容**：

```bash
# 旧函数保留，内部调用新通用函数
ensure_devuser_bashrc() {
    ensure_user_bashrc "devuser"
}

verify_devuser_access() {
    verify_user_access "devuser"
}
```

### 2.8 框架版本与加载顺序更新

* 框架版本升级：1.0.0 → **1.1.0**

* `variant-framework.sh` 模块加载顺序更新：

```bash
_VARIANT_MODULES=(
    "logging"           # 已有：结构化日志
    "timer"             # 已有：构建阶段计时
    "user-management"   # 🆕 新增：用户管理（需在mirror/permissions前）
    "mirror"            # 已有：镜像源配置
    "shell-profile"     # 🆕 新增：Shell环境配置
    "install-helpers"   # 已有：包安装辅助（增强PIP_USER模式）
    "jupyter-kernel"   # 🆕 新增：Jupyter内核注册
    "docs"              # 🆕 新增：文档部署
    "ft-guards"         # 已有：free-threading守卫
    "cleanup"           # 已有：统一清理
    "build-info"        # 已有：构建元数据
    "verify"            # 已有：基础验证（增强ssh/用户检查）
    "permissions"       # 已有：权限设置（更新支持自定义用户）
)
```

### 2.9 模板更新

更新 `_template/Dockerfile`，在注释中展示新功能的可选使用方法（不启用，保持现有模板行为）：

```dockerfile
# ── Optional: Custom user configuration (uncomment to use) ──
# ARG DEVTARGET_USER=ai
# ARG DEVTARGET_UID=1001
# ARG DEVTARGET_GID=1001
# ARG GRANT_SUDO=yes
# RUN <<'S1_USER'
# source /usr/local/share/variant-framework/variant-framework.sh
# variant_configure_target_user
# S1_USER

# ── Optional: Custom Jupyter kernel (uncomment to use) ──
# RUN <<'S_KERNEL'
# source /usr/local/share/variant-framework/variant-framework.sh
# variant_register_jupyter_kernel "custom" "Python 3 (Custom)" "/opt/conda/bin/python"
# S_KERNEL
```

### 2.10 文档

创建 `shared/README.md`（共享库使用文档），包含：

* 模块列表与职责

* 每个模块的API函数说明

* 使用示例

* 环境变量配置表

* 安全注意事项（密码设置警告）

* 向后兼容说明

## 3. 验收标准

### 3.1 功能验收

* [ ] 4个新模块文件创建完成：user-management.sh、shell-profile.sh、jupyter-kernel.sh、docs.sh

* [ ] 2个现有模块增强完成：install-helpers.sh（新增2个函数）、verify.sh（新增3个函数）

* [ ] permissions.sh、mirror.sh 硬编码 devuser 问题修复，同时保留旧函数wrapper

* [ ] variant-framework.sh 更新模块加载列表，版本号升级到1.1.0

* [ ] \_template/Dockerfile 更新，注释展示新功能可选用法

* [ ] shared/README.md 文档编写完成

### 3.2 向后兼容验收

* [ ] 所有现有变体（conda-llvm/onnx-dev/onnx-pytorch/onnx-quantized/torch-dev/ai-dev）的Dockerfile无需修改

* [ ] 现有函数（verify\_devuser\_access、ensure\_devuser\_bashrc等）仍然存在且行为不变

* [ ] 默认环境变量值（DEVTARGET\_USER=devuser, DEVTARGET\_UID=1000, DEVTARGET\_GID=1000）与现有行为一致

* [ ] 不自动调用任何新模块函数，现有变体构建过程中不会执行新逻辑

### 3.3 质量验收

* [ ] 所有新函数有注释说明用途、参数、返回值

* [ ] 幂等性：shell-profile.sh 的追加函数重复调用不会重复内容

* [ ] 错误处理：关键操作有错误检查和明确错误信息

* [ ] 安全警告：variant\_set\_user\_password 文档和函数注释明确说明密码进入镜像层的风险

* [ ] bash -n 语法检查通过：所有新脚本无语法错误

* [ ] 遵循现有代码风格（函数命名、日志格式、框线头等）

### 3.4 可移植性验收

* [ ] jupyter-kernel.sh 自动检测 Jupyter 路径存在性，/opt/venv 不存在时不报错

* [ ] user-management.sh UID/GID 冲突时优雅降级（自动找下一个可用ID）

* [ ] shell-profile.sh 在文件不存在时自动创建（如用户 .bashrc）

* [ ] docs.sh 支持文件和目录两种源路径

## 4. 约束与假设

### 4.1 技术约束

* 基础镜像假设：基于 devcontainer-base（Ubuntu 26.04 + /opt/conda Miniforge3 + /opt/venv）

* Shell：bash，遵循现有框架的 `set -e -o pipefail` 模式

* 日志格式：使用现有 logging.sh 的 `variant_log_info/variant_log_ok/variant_log_error` 函数

* 框线头：使用现有框架的 ┌─┐ 格式

### 4.2 假设

* 现有变体不需要迁移到新功能（保持现状即可）

* 新变体会选择是否使用新功能（按需调用）

* 外部项目如果复用此框架，会遵循相同的目录约定（/opt/conda, /opt/venv）

## 5. 风险与缓解

| 风险                    | 影响 | 缓解措施                                                |
| --------------------- | -- | --------------------------------------------------- |
| 新模块引入语法错误导致所有变体构建失败   | 高  | bash -n 语法检查；不自动调用新函数；现有wrapper保持原行为                |
| 权限设置错误导致用户无法访问conda   | 中  | 默认值与现有一致；自定义用户场景需显式启用；permissions.sh wrapper保持兼容    |
| Jupyter路径检测错误导致内核注册失败 | 低  | 路径不存在时跳过而非报错；verify函数可验证注册结果                        |
| bashrc追加幂等性标记被用户手动修改  | 低  | 文档说明标记用途；幂等失效时只会重复追加，不影响功能                          |
| 密码函数被误用导致安全问题         | 中  | 函数注释和文档用⚠️明确警告；提供更安全的`variant_lock_user_password`选项 |

