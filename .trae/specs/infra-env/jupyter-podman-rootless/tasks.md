# Jupyter Podman Rootless - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 项目目录结构初始化与基础配置
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `apps/containers/jupyter-podman-rootless/` 下创建完整目录结构
  - 创建 AGENTS.md 作为应用入口（遵循apps/区域规范）
  - 创建 pyproject.toml 声明invoke依赖
  - 创建 .containerignore（兼容.containerignore和.dockerignore）
  - 创建 README.md 基础框架
- **Acceptance Criteria Addressed**: AC-12
- **Status**: ✅ 完成 — 目录结构、4个基础文件已创建；AGENTS.md在Task 8中修正了sudo默认值问题

## [x] Task 2: Conda环境定义（conda-lock/environment.yml）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 conda-lock/environment.yml 定义conda环境
  - 指定Python 3.14=*_cp314t（free-threading）
  - 包含jupyterlab、notebook、ipykernel、nbconvert、ipywidgets等核心Jupyter包
  - conda-forge频道优先（strict priority），libmamba solver
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Status**: ✅ 完成 — environment.yml已创建，最小核心包集合

## [x] Task 3: 系统配置文件（config/目录）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 config/sshd_config（SSH配置：禁用root登录、ED25519优先）
  - 创建 config/supervisord.conf（supervisord主配置）
  - 创建 config/supervisor/conf.d/sshd.conf（sshd以root运行绑定22端口）
  - 创建 config/supervisor/conf.d/jupyter.conf（jupyter以devuser运行，conda main环境PATH）
  - 创建 config/jupyter_notebook_config.py（Jupyter配置：0.0.0.0绑定、/workspace目录）
  - 创建 config/containers/storage.conf（Podman存储配置：fuse-overlayfs驱动）
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-7, AC-11
- **Status**: ✅ 完成 — 6个配置文件已创建；Task 8修正了jupyter.conf中的conda路径（原为venv路径）

## [x] Task 4: Containerfile（原Dockerfile）编写
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 编写Containerfile（7层单镜像架构）
  - BuildKit语法，缓存挂载（apt/pip/conda pkgs）
  - 构建参数支持（APT_MIRROR/CONDA_MIRROR/PIP_MIRROR/PYTHON_VERSION）
  - Podman rootless配置（subuid/subgid: devuser:100000:65536）
  - 结构化日志和构建计时器
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-7, AC-11, AC-14, AC-15
- **Status**: ✅ 完成 — Containerfile已创建，占位entrypoint.sh/healthcheck.sh也已生成

## [x] Task 5: entrypoint.sh启动脚本
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 7步启动流程（密码→host keys→sshd→podman初始化→ssh keys→jupyter→访问信息）
  - 命令模式支持（exec用户命令，通过gosu/su切换到devuser）
  - setup_podman()新增函数（初始化rootless Podman环境，/dev/fuse权限、XDG_RUNTIME_DIR）
  - 显式conda路径（/opt/conda/envs/main/bin/python）
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6, AC-10
- **Status**: ✅ 完成 — 完整entrypoint.sh已重写

## [x] Task 6: 辅助脚本（scripts/目录）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - scripts/healthcheck.sh：sshd进程+端口检查 + jupyter HTTP API检查 + podman可选检测
  - scripts/lib/logging.sh：带颜色的共享日志函数库
- **Acceptance Criteria Addressed**: AC-10
- **Status**: ✅ 完成 — 两个脚本已创建，bash -n语法通过

## [x] Task 7: Invoke任务实现（tasks/目录）
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - tasks/__init__.py：Collection命名空间入口
  - tasks/container.py：8个核心任务（build/run/stop/status/shell/logs/exec/clean）+ container子集合
  - 自动检测podman/docker运行时
  - Windows路径转换支持
  - 构建参数（镜像源、端口、密码/token/公钥/sudo等）
  - 卷挂载:Z,U标志（Podman rootless chown）
- **Acceptance Criteria Addressed**: AC-8, AC-9
- **Status**: ✅ 完成 — invoke --list列出16个任务

## [x] Task 8: 静态验证与结构检查
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 验证目录结构完整性（17个文件）
  - 修正发现的问题（AGENTS.md sudo默认值、jupyter.conf venv路径）
  - 代码一致性检查
- **Acceptance Criteria Addressed**: AC-1到AC-11（静态部分）
- **Status**: ✅ 完成 — 目录结构验证通过，3处问题已修正

## [x] Task 9: apps/AGENTS.md路由表更新
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 新增containers/分组描述
  - 添加jupyter-podman-rootless路由条目
  - 更新嵌套优先级树状图
  - 更新边界声明表
- **Acceptance Criteria Addressed**: AC-12
- **Status**: ✅ 完成 — 三处更新均已完成

---

## 待用户在Linux/Podman环境验证
- [x] invoke build 构建镜像 — ✅ WSL/Podman rootless 构建成功（7层 542s，TUNA 镜像源）
- [x] invoke run 启动容器 — ✅ 容器启动成功（supervisord 管理 sshd+jupyter）
- [x] SSH登录（2222端口）— ✅ devuser 登录成功（uid=1001, groups=sudo,docker）
- [~] Jupyter访问（8888端口）— ⚠️ Jupyter Server 2.20.0 成功启动并监听 0.0.0.0:8888（日志确认），但 WSL2 环境下容器会定期收到 SIGTERM 导致 HTTP 外部验证时序受限；容器内 supervisor 确认 jupyter RUNNING
- [~] 容器内 `podman run alpine echo hello` — ⚠️ Podman-in-Podman 受 WSL2 namespace 限制（newuidmap: write to uid_map failed: Operation not permitted）；需 privileged 模式或宿主机 subuid/subgid 配置
- [x] 卷挂载权限验证（workspace目录）— ✅ 读写测试通过（/workspace drwxrwxrwx）
- [x] Python 3.14t free-threading验证 — ✅ Python 3.14.6 free-threading build（Py_GIL_DISABLED=1, GIL enabled=False, Free-threading=True）
- [x] healthcheck正常工作 — ✅ 容器健康状态为 healthy

### 构建过程中修复的问题（2026-08-26）
1. **Containerfile Layer 3 & Layer 6**: `sys.free_threaded` 属性不存在 → 改用 `sysconfig.get_config_var('Py_GIL_DISABLED') == 1` + `not sys._is_gil_enabled()`
2. **Containerfile Layer 4**: shell heredoc (`<<'EOF'`) 在 buildah 中解析失败 → 改用 `printf '%s\n'` 命令
3. **sshd.conf**: `&&` 被错误编码为 HTML 实体 `&amp;&amp;` → 修复为 `&&`
4. **entrypoint.sh**: `sys.free_threaded` 检查 → 修复为正确的 `sysconfig + sys._is_gil_enabled()` 检查
5. **entrypoint.sh setup_podman()**: `chown` 目标从 `${podman_storage_dir}` 改为 `${NON_ROOT_HOME}/.local`，修复 Jupyter 无法创建 `.local/share/jupyter` 的权限问题

### WSL2 环境限制
- 容器会在约 74 秒后收到 SIGTERM 信号退出（WSL2 的进程清理机制）
- Podman-in-Podman 的 newuidmap 在容器内无权限（需要宿主机配置或 privileged 模式）
- Jupyter 8888 端口外部 HTTP 验证受 WSL2 端口转发时序影响（容器内 supervisor 确认 jupyter RUNNING，监听 0.0.0.0:8888）

### 二次验证补充（2026-08-26）
- `invoke container.run --detach` 启动成功：自动生成密码/token，输出 SSH（2222）与 Jupyter（8888）访问信息
- 容器内 `supervisorctl status` 确认：jupyter RUNNING、sshd RUNNING（pid 249/248）
- 通过 `--entrypoint /opt/conda/envs/main/bin/python` 覆盖入口直接运行验证脚本，Python free-threading 三项指标全部通过：
  - `Py_GIL_DISABLED: 1`
  - `GIL enabled: False`
  - `Free-threading: True`
  - 版本字符串：`Python 3.14.6 free-threading build | packaged by conda-forge | (main, Jul 24 2026, 16:09:35) [GCC 14.3.0]`

### 已知非阻断问题
- entrypoint.sh 在接收带空格的 CMD（如 `python /workspace/verify_ft.py`）时，会被当作 shell 命令解析（`import: command not found`）。不影响正常启动流程（supervisord 模式不依赖 CMD 传参），仅影响 `podman run image <cmd>` 形式的临时调用，建议后续通过 `--entrypoint` 覆盖或在 entrypoint.sh 中增强 CMD 分发逻辑。

### 卷挂载权限修复（2026-08-26）
**问题**：挂载卷使用 `:Z,U` 标志 + entrypoint.sh 中 `chown -R devuser:devuser /workspace` 导致宿主机文件被递归 chown 到 subuid 101000（无名UID），宿主机用户无法访问。

**根因**（七概念 I→F 分析）：
- `:U` 标志将卷递归 chown 给容器主UID（root=0→宿主机1000），但容器内 devuser(1001) 映射到宿主机 subuid 101000
- entrypoint.sh `chown -R devuser:devuser /workspace` 将所有文件 chown 到容器 UID 1001 → 宿主机 UID 101000，在原生 Linux fs 上生效（9p 上 chown 被静默忽略）

**修复方案**（Jupyter 以 root 运行——rootless 容器中 root=宿主机普通用户）：
1. **entrypoint.sh**: 移除 `chown -R devuser:devuser /workspace` 和 `chmod 755 /workspace`；改为 `chmod 777 /workspace`（仅目录，非递归）；Jupyter 配置目录改为 `/root/.jupyter`；`c.ServerApp.allow_root = True`
2. **config/supervisor/conf.d/jupyter.conf**: `user=root`，config 路径 `/root/.jupyter/jupyter_notebook_config.py`
3. **config/jupyter_notebook_config.py**: `allow_root = True`
4. **Containerfile**: 移除 `/workspace` 的 devuser chown，改为 777；COPY jupyter_notebook_config.py 到 `/root/.jupyter` 和 `/home/devuser/.jupyter`
5. **tasks/container.py**: 移除卷挂载的 `:Z,U` 标志，改为无标志挂载（`--security-opt label=disable` 已禁用 SELinux）

**验证结果**（原生 Linux fs `/tmp/`）：
- 挂载前已有文件：`xinzo(1000):xinzo(1000) perms=644` → 启动后仍为 `xinzo(1000):xinzo(1000) perms=644` ✅
- Jupyter(root) 创建的新文件：`xinzo(1000):xinzo(1000) perms=644`（容器 root(0)→宿主机1000）✅
- supervisord: jupyter RUNNING + sshd RUNNING ✅
- Python free-threading: True ✅
