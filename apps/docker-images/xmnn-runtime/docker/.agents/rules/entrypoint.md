---
id: "xmnn-runtime-entrypoint-rules"
title: "Entrypoint 启动脚本规范"
source: "docker/entrypoint.sh"
---
# Entrypoint 启动脚本规范（xmnn-runtime/docker）

## 基本职责

entrypoint.sh 是容器入口点，负责conda环境激活、TVM/VTA路径配置、UID/GID自适应调整和gosu用户切换。

## 关键差异（对比其他项目）

- **无tini**：本镜像不内置tini init，使用`docker run --init`或依赖基础镜像
- **无密码初始化**：无SSH服务，不需要设置密码
- **无服务启动**：不启动supervisord/sshd/jupyter，纯用户命令执行
- **UID/GID自适应**：从/workspace目录自动检测宿主机UID/GID，不是固定UID 1000
- **conda环境名可配置**：通过`CONDA_ENV_NAME`环境变量（默认tvm-build）

## 启动流程

1. **conda环境激活**：
   - source `${CONDA_DIR}/etc/profile.d/conda.sh`
   - `conda activate "${CONDA_ENV_NAME}"`
   - 设置CONDA_PREFIX、CONDA_DEFAULT_ENV
   - PATH prepend `${TARGET_HOME}/.local/bin`

2. **TVM/VTA路径配置**：
   - 检测`site-packages/tvm/_libs`，设置TVM_LIBRARY_PATH和LD_LIBRARY_PATH
   - 检测`site-packages/vta`，设置VTA_HW_PATH
   - 设置TVM_FFI=ctypes

3. **UID/GID自适应调整**（root运行时）：
   - 优先使用HOST_UID/HOST_GID环境变量
   - 否则从/workspace目录stat自动检测UID/GID
   - UID=0时回退到1000:1000
   - 处理UID/GID冲突（移动已有用户/组到9999+）
   - chown -R调整TARGET_HOME、site-packages、WORK_DIR权限

4. **用户切换与命令执行**：
   - 有gosu时：`exec gosu ai "$@"`
   - 无gosu时fallback：`exec su -s /bin/bash ai -c 'conda activate; exec "$@"'`
   - 非root时直接`exec "$@"`
   - 默认CMD：`/bin/bash -l`（登录shell）

## 日志规范

简单日志前缀`[entrypoint]`，输出到stderr：
```bash
log() { echo "[entrypoint] $*" >&2; }
```
无分级日志（INFO/ERROR等），与其他项目的结构化日志不同。

## 关键环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| CONDA_ENV_NAME | tvm-build | conda环境名 |
| TARGET_USER | ai | 非root用户名 |
| WORK_DIR | /workspace | 工作目录 |
| HOST_UID | 自动检测 | 宿主机UID（挂载卷权限匹配） |
| HOST_GID | 自动检测 | 宿主机GID |
| TVM_FFI | ctypes | TVM FFI模式 |

## UID/GID自适应逻辑

核心设计：容器内ai用户的UID/GID自动匹配/workspace挂载目录的宿主机UID/GID，避免权限问题。

```
if root:
  1. HOST_UID/HOST_GID from env, or stat /workspace, or default 1000:1000
  2. if UID=0 → 1000:1000
  3. if current UID/GID != target → 调整（冲突处理）
  4. chown -R home + site-packages + work_dir
  5. gosu ai "$@"
else:
  exec "$@"
```

冲突处理策略：
- 目标GID被其他组占用→移动该组到9999+
- 目标UID被其他用户占用→移动该用户到9999+
- 从9999开始递增找空闲ID

## 反模式

- ❌ 不要在entrypoint中启动任何后台服务（纯用户命令执行）
- ❌ 不要硬编码UID=1000（应自动适配/workspace权限）
- ❌ 不要省略conda activate（TVM/xmnn依赖conda环境）
- ❌ 不要用su - ai（会创建新login shell），使用gosu
