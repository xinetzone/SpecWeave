# Docker 默认 pip install 用户级安装 - 实施计划

## [x] Task 1: 在 docker-compose.yml 中添加 PIP_USER=1 环境变量
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 dev 服务的 `environment` 段添加 `PIP_USER=1`
  - 此变量仅影响运行时容器，不影响 Dockerfile 构建阶段（构建阶段不读取 compose environment）
  - Jupyter kernel 和 SSH 会话继承此变量，使 `pip install` 默认走 `--user`
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `programmatic` TR-1.1: `docker exec chaos-ai-dev bash -c 'echo $PIP_USER'` 输出 `1`
  - `programmatic` TR-1.2: `docker exec -u devuser chaos-ai-dev pip install --dry-run six` 不报错，路径指向 `/home/devuser/.local/`
  - `programmatic` TR-1.3: `docker exec -u devuser chaos-ai-dev sudo pip install --dry-run six` 路径指向 `/opt/conda/`（sudo 默认重置环境变量）
- **Notes**: PIP_USER=1 设置在 docker-compose.yml 而非 Dockerfile ENV，因为：1) 不需要重建镜像；2) 不影响 Dockerfile 构建阶段的 pip install（Stage 2）

## [x] Task 2: 在 container-bootstrap.sh 中显式设置 PIP_USER=0
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - bootstrap 脚本以 root 身份运行，需要将包装入系统 /opt/conda 而非 /root/.local/
  - 在 pip install 命令前显式导出 `PIP_USER=0`，确保系统级安装
  - 这是防御性措施：即使未来有人在 Dockerfile 中设置了 PIP_USER=1，bootstrap 仍正确工作
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 容器重启后，bootstrap 安装的包（如 pandas）位于 `/opt/conda/lib/python3.14/site-packages/`
  - `programmatic` TR-2.2: devuser 能直接 import bootstrap 安装的包（无需 --user）
- **Notes**: 在 pip install 命令前加 `PIP_USER=0` 前缀即可，无需全局 export（避免影响后续命令）

## [x] Task 3: 端到端验证
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 重启容器使配置生效
  - 验证四种场景：devuser pip install、root pip install、sudo pip install、bootstrap 安装
  - 确认 TVM/VTA 导入和 caffe_demo 编译仍正常
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-3.1: devuser 执行 `pip install --dry-run tabulate` 显示安装路径为 `/home/devuser/.local/`
  - `programmatic` TR-3.2: root 执行 `PIP_USER=0 pip install --dry-run tabulate` 显示安装路径为 `/opt/conda/`
  - `programmatic` TR-3.3: devuser 执行 `sudo pip install --dry-run tabulate` 显示安装路径为 `/opt/conda/`
  - `programmatic` TR-3.4: TVM/VTA Python 导入成功
  - `programmatic` TR-3.5: caffe_demo 模型编译成功
