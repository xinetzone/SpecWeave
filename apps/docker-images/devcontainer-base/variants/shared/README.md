# DevContainer Variant Framework — Shared Library

> **版本**: 1.1.0
>
> devcontainer-base 变体构建共享 Shell 函数库，提供标准化的日志、计时、镜像源配置、包分组安装、用户管理、权限设置、环境验证等能力。

---

## 快速开始

在 Dockerfile 的 RUN heredoc 开头 source 框架：

```dockerfile
RUN <<'S1'
source /usr/local/share/variant-framework/variant-framework.sh
# ... 你的构建步骤 ...
S1
```

---

## 模块列表

框架按依赖顺序加载 13 个模块：

| 模块 | 职责 | 是否新增 |
|------|------|---------|
| `logging` | 结构化日志（INFO/OK/WARN/ERROR + JSON格式） | 原有 |
| `timer` | 构建阶段计时与汇总 | 原有 |
| `user-management` | 目标用户管理（自定义用户名/UID/GID/重命名/sudo） | **v1.1.0新增** |
| `mirror` | conda/pip/APT 镜像源配置 | 原有 |
| `shell-profile` | Shell环境配置（umask/bashrc/PATH持久化/SSH） | **v1.1.0新增** |
| `install-helpers` | apt/conda/pip 分组安装 + PIP_USER模式切换 | 原有+增强 |
| `jupyter-kernel` | Jupyter 自定义内核注册 | **v1.1.0新增** |
| `docs` | 文档部署到 /opt/docs/ | **v1.1.0新增** |
| `ft-guards` | free-threading (no-GIL) 完整性守卫 | 原有 |
| `cleanup` | 统一清理（保留计时器目录） | 原有 |
| `build-info` | 构建元数据写入 /etc/ | 原有+增强 |
| `verify` | 基础验证（服务/conda/用户/sshd/语法检查） | 原有+增强 |
| `permissions` | 权限设置（conda/可执行文件/bashrc） | 原有+增强 |

---

## 环境变量

所有变量均有合理默认值，保持与 v1.0.0 完全向后兼容。

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEVTARGET_USER` | `devuser` | 目标用户名（v1.1.0起生效） |
| `DEVTARGET_UID` | `1000` | 目标用户 UID（v1.1.0起生效） |
| `DEVTARGET_GID` | `1000` | 目标用户 GID（v1.1.0起生效） |
| `GRANT_SUDO` | `yes` | 是否授予目标用户 sudo NOPASSWD |
| `USER_PASSWORD` | *(空)* | 用户密码（可选，见安全警告） |
| `CONDA_MIRROR` | `tuna` | conda 镜像源：official/tuna/aliyun/bfsu |
| `PIP_MIRROR` | `aliyun` | pip 镜像源：official/tuna/aliyun/bfsu |
| `APT_MIRROR` | `official` | APT 镜像源：official/tuna/aliyun |
| `CONDA_DIR` | `/opt/conda` | conda 安装目录 |
| `VARIANT_DEBUG` | `0` | 设为 1 启用 set -x 调试 |
| `PIP_USER` | *(动态)* | pip 用户模式标志 |

---

## API 参考

### logging — 结构化日志

```bash
variant_log_info "message"
variant_log_ok "message"
variant_log_warn "message"
variant_log_error "message"
variant_stage_header "Stage Title"
```

### timer — 构建计时

```bash
variant_timer_start <variant_name>
variant_timer_stage <stage_num> <description>
variant_timer_summary <title>
```

### user-management — 用户管理（v1.1.0新增）

**主入口**：一键配置目标用户（推荐）

```bash
# 使用环境变量 DEVTARGET_USER/DEVTARGET_UID/DEVTARGET_GID 配置
variant_configure_target_user
```

**原子函数**：

```bash
variant_create_user <name> <uid> <gid> [additional_groups...]
variant_rename_user <old_name> <new_name>
variant_configure_sudo <username> [yes|no]
variant_set_user_password <username> <password>
variant_lock_user_password <username>
variant_get_target_user_info  # 输出 user:uid:gid
variant_get_target_user_group # 输出组名
```

> ⚠️ **安全警告**：`variant_set_user_password` 在构建期设置密码会将明文密码写入镜像层历史！
> 推荐做法：
> - 运行时通过 `docker exec` 设置密码
> - 使用 SSH 密钥登录（调用 `variant_lock_user_password` 禁用密码）
> - 仅在受控内网环境下使用构建期密码

**示例**：自定义非root用户

```dockerfile
ARG DEVTARGET_USER=ai
ARG DEVTARGET_UID=1001
ARG DEVTARGET_GID=1001
RUN <<'S1_USER'
source /usr/local/share/variant-framework/variant-framework.sh
variant_configure_target_user  # 自动创建/重命名用户
variant_configure_shell_profile 0022
S1_USER
```

### mirror — 镜像源配置

```bash
variant_configure_mirrors  # 一键配置所有镜像源（读取环境变量）
```

### shell-profile — Shell环境（v1.1.0新增）

```bash
variant_configure_umask <umask_value>         # 默认 0022
variant_append_user_bashrc <content> [username]
variant_append_root_bashrc <content>
variant_persist_path <path_entry> [prepend|append]
variant_configure_ssh_env <username> [KEY=VALUE...]
variant_configure_shell_profile [umask_value] # 一键配置（推荐）
```

**幂等性保证**：所有追加操作使用 `# >>> variant-framework >>>` / `# <<< variant-framework <<<` 标记包裹，重复调用不会重复追加内容。

### install-helpers — 包安装

```bash
apt_install_group <description> <packages...>
conda_install_group <group_name> <description> <packages...>
pip_install_group [--verbose] [--index-url <url>] <group_name> <description> <packages...>

variant_activate_main_env   # 激活 conda main 环境
variant_activate_base_env   # 激活 conda base 环境（自动设置PIP_USER=0）

# v1.1.0新增
variant_pip_build_mode     # PIP_USER=0，安装到全局位置
variant_pip_runtime_mode   # PIP_USER=1，用户可 pip install --user
```

**--verbose 模式**（源码编译场景）：安装前输出环境诊断（Python ABI/编译器/Rust版本），安装后逐个验证包import。

### jupyter-kernel — Jupyter内核（v1.1.0新增）

```bash
variant_register_jupyter_kernel <kernel_name> <display_name> <python_path> [extra_env...]
verify_jupyter_kernel <kernel_name> [jupyter_base_path]
```

自动检测并注册到所有存在的 Jupyter 路径：
- `/opt/venv/share/jupyter/kernels/`（优先）
- `/opt/conda/share/jupyter/kernels/`（base环境）
- `/opt/conda/envs/main/share/jupyter/kernels/`（main环境）

**示例**：

```bash
variant_register_jupyter_kernel "npu" "Python 3 (NPU Dev)" "/opt/conda/bin/python" \
    "PYTHONPATH=/workspace/npu_tvm/python" \
    "OMP_NUM_THREADS=4"
```

### docs — 文档部署（v1.1.0新增）

```bash
variant_deploy_docs <src_path> [dest_subdir]
```

将文件/目录复制到 `/opt/docs/` 并设置 `a+rX` 权限。

**Dockerfile 示例**：

```dockerfile
COPY README.md docs/ /tmp/_docs/
RUN <<'S_DOCS'
source /usr/local/share/variant-framework/variant-framework.sh
variant_deploy_docs "/tmp/_docs" "my-variant"
rm -rf /tmp/_docs
S_DOCS
```

### ft-guards — free-threading守卫

```bash
ft_guard_checkpoint <stage_name>
```

### cleanup — 清理

```bash
cleanup_all  # apt缓存/conda缓存/tmp，保留.variant-timers目录
```

### build-info — 构建元数据

```bash
variant_write_build_info <variant_name> <base_image> [key=value...]
```

写入 `/etc/devcontainer-variant-<name>-build-info`，包含：
- BUILD_DATE / VARIANT / BASE_IMAGE
- CONDA_VERSION / PYTHON_VERSION / PYTHON_BUILD
- 镜像源配置
- **TARGET_USER / TARGET_UID**（v1.1.0新增）
- 服务可用性、构建耗时

### verify — 验证检查

```bash
verify_validation_header [title]
verify_base_services           # docker/supervisord/sshd命令检查
verify_conda_main_env          # conda main环境验证
verify_user_access [username]  # 通用用户验证（v1.1.0新增）
verify_devuser_access()        # devuser验证（wrapper，向后兼容）
verify_ssh_config              # sshd -t配置语法检查（v1.1.0新增）
verify_bash_syntax <paths...>  # bash -n语法检查
verify_all_basic               # 一键执行基础验证
```

### permissions — 权限设置

```bash
ensure_conda_permissions [conda_dir]       # chown root:root + a+rX
ensure_executable_permissions <paths...>    # 可执行位设置
ensure_user_bashrc [username]              # 通用用户bashrc权限（v1.1.0新增）
ensure_devuser_bashrc()                    # devuser bashrc（wrapper，向后兼容）
ensure_profile_d_executable [profile_dir]  # /etc/profile.d/脚本+x
ensure_all_permissions                     # 一键执行所有权限修复
```

---

## 使用示例

### 示例1：标准变体（使用默认devuser）

```dockerfile
RUN <<'S3'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 3 "Core installation"
variant_activate_main_env
pip_install_group "G1: ML tools" "Machine learning" scikit-learn pandas
S3
```

### 示例2：自定义用户+Jupyter内核+Shell配置

```dockerfile
ARG DEVTARGET_USER=data-scientist
ARG DEVTARGET_UID=1001

RUN <<'S_CUSTOM'
source /usr/local/share/variant-framework/variant-framework.sh
variant_configure_target_user
variant_configure_shell_profile 0022
variant_persist_path "/opt/my-tools/bin" prepend
variant_register_jupyter_kernel "datasci" "Python 3 (Data Science)" "/opt/conda/envs/main/bin/python"
S_CUSTOM
```

### 示例3：带verbose模式的源码编译

```dockerfile
RUN <<'S_BUILD'
source /usr/local/share/variant-framework/variant-framework.sh
variant_pip_build_mode
pip_install_group --verbose "G4: Source builds" "Compiled packages" \
    opencv-python-headless
S_BUILD
```

---

## 向后兼容性

v1.1.0 保持 100% 向后兼容：

| 旧函数 | 兼容方式 |
|--------|---------|
| `verify_devuser_access()` | wrapper，内部调用 `verify_user_access "devuser"` |
| `ensure_devuser_bashrc()` | wrapper，内部调用 `ensure_user_bashrc "devuser"` |
| `ensure_all_permissions` | 调用 `ensure_user_bashrc`（默认DEVTARGET_USER=devuser） |
| 默认 `DEVTARGET_USER=devuser` | 与v1.0.0行为一致 |
| 默认UID/GID=1000 | 与v1.0.0行为一致 |

**现有变体（conda-llvm/onnx-dev/onnx-pytorch/onnx-quantized/torch-dev/ai-dev）无需任何修改即可使用v1.1.0框架。**

---

## 设计原则

1. **默认安全**：密码设置有明确警告，不自动调用危险操作
2. **幂等性**：配置类函数重复调用不会产生副作用
3. **防御性编程**：路径不存在时优雅处理而非报错退出
4. **向后兼容**：默认值保持与旧版本一致，旧函数保留wrapper
5. **可选使用**：新功能需显式调用，不自动改变构建行为
6. **结构化日志**：所有关键操作通过 `variant_log_*` 输出，便于排查问题
