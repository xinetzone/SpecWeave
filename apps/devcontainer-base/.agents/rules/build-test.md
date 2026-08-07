---
id: "devcontainer-build-test-rules"
title: "构建与测试规范"
source: "AGENTS.md#快速开始"
---
# 构建与测试规范（devcontainer-base）

## 构建方式

### 方式一：一键构建脚本（推荐）

```bash
# 标准构建
bash scripts/build.sh

# 使用国内镜像源构建（aliyun）
bash scripts/build.sh --cn

# 指定镜像源
bash scripts/build.sh --apt-mirror tuna --pip-mirror tuna

# 构建后自动验证
bash scripts/build.sh --verify

# 不使用缓存重新构建
bash scripts/build.sh --no-cache

# 指定镜像标签和名称
bash scripts/build.sh -t 2.0 -n my-devcontainer
```

构建脚本特性：
- 自动加载 `.env` 文件中的环境变量（set -a 自动导出）
- CLI 参数优先级高于 `.env` 文件中的配置
- BuildKit 缓存挂载自动启用
- 构建完成后可选 `--verify` 模式：临时启动容器，验证 SSH/Docker/Jupyter 三服务
- 统一日志格式（scripts/lib/logging.sh）

### 方式二：Docker Compose 一键启动（推荐日常使用）

```bash
# 一键启动（自动构建镜像+启动+健康验证）
bash scripts/start.sh

# 指定模式启动
bash scripts/start.sh --profile dood     # DooD 模式（挂载宿主机docker.sock）
bash scripts/start.sh --profile ssh-only # 仅 SSH 模式
bash scripts/start.sh -p ssh-only        # 简写

# 查看状态 / 停止 / 重启
bash scripts/start.sh status
bash scripts/start.sh stop
bash scripts/start.sh restart

# 跳过验证快速启动
bash scripts/start.sh --no-verify
```

start.sh 特性：
- 支持 dind/dood/ssh-only 三种 profile，默认 dind
- 自动加载 `.env` 文件，未设置 `USER_PASSWORD`/`JUPYTER_TOKEN` 时自动生成随机凭据
- 轮询 Docker healthcheck 等待服务就绪（超时 90s，间隔 3s）
- 分层验证：内部端口检测 + 宿主机 SSH 连接 + Jupyter HTTP + Docker DinD API
- 输出彩色连接信息面板（含 copy-paste 命令）

### 方式三：手动 docker build

```bash
# 标准构建
docker build -t devcontainer-base .

# 使用国内镜像源
docker build --build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun -t devcontainer-base .

# 不使用缓存
docker build --no-cache -t devcontainer-base .
```

## 环境配置

```bash
# 复制环境变量模板
cp .env.example .env
# 编辑 .env 文件，按需修改配置
```

`.env` 文件支持的关键配置项见 [.env.example](../../.env.example)。

## 运行容器

### 使用 Docker Compose（推荐）

```bash
# 使用 start.sh 启动（推荐）
bash scripts/start.sh

# 或直接使用 docker compose
docker compose --profile dind up -d
```

### 使用 docker run

```bash
# DinD 模式（需要 --privileged）
docker run -d --privileged \
  -p 2222:22 -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e JUPYTER_TOKEN=mysecret \
  -e GRANT_SUDO=yes \
  -v devcontainer-workspace:/workspace \
  -v devcontainer-docker:/var/lib/docker \
  --name devcontainer-test devcontainer-base

# DooD 模式（挂载宿主机 docker.sock，无需 --privileged）
docker run -d \
  -p 2222:22 -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e JUPYTER_TOKEN=mysecret \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v devcontainer-workspace:/workspace \
  --name devcontainer-test devcontainer-base

# 调试模式（不启动服务，直接进入 shell）
docker run -it --rm --privileged devcontainer-base bash
```

## 验证流程

### 构建后验证（build.sh --verify）

1. 临时启动容器（DinD 模式）
2. 等待健康检查通过（healthcheck.sh 返回 healthy）
3. 验证 SSH 端口监听
4. 验证 Docker daemon 可访问
5. 验证 Jupyter API 响应
6. 清理临时容器

### 运行后手动验证

```bash
# 1. 查看容器状态和健康
docker ps
docker inspect --format='{{.State.Health.Status}}' devcontainer-base-dind
# 期望：healthy

# 2. 查看服务日志
docker logs devcontainer-base-dind
docker exec devcontainer-base-dind supervisorctl status
# 期望：所有服务 RUNNING

# 3. 验证 SSH（使用 devuser，root 默认禁用）
ssh -p 2222 devuser@localhost
# 或使用 sshpass 自动化测试
sshpass -p <password> ssh -o StrictHostKeyChecking=no -p 2222 devuser@localhost echo "SSH OK"

# 4. 验证 Jupyter（浏览器访问）
# http://localhost:8888/?token=<token>
curl -s http://localhost:8888/api
# 期望：返回 JSON（需要 token）

# 5. 验证 Docker DinD
docker exec -it devcontainer-base-dind docker ps
docker exec -it devcontainer-base-dind docker run --rm hello-world

# 6. 验证 Podman rootless
docker exec -it devcontainer-base-dind su - devuser -c "podman ps"

# 7. 验证 sudo 权限（需设置 GRANT_SUDO=yes）
docker exec devcontainer-base-dind su - devuser -c "sudo -n whoami"
# 期望：root

# 8. 中文环境验证
docker exec devcontainer-base-dind locale | grep LANG
# 期望：LANG=zh_CN.UTF-8
docker exec devcontainer-base-dind date
# 期望：显示中国时区时间（CST）
```

## 常见问题排查

| 问题 | 排查命令 | 常见原因 |
|------|---------|---------|
| Docker DinD 启动失败 | `docker logs <name>` 查看 dockerd 日志 | 未使用 `--privileged`、daemon.json 与命令行参数冲突 |
| SSH 连接被拒 | `docker exec <name> pgrep -a sshd` | sshd 未启动、密码未设置、端口未映射 |
| Jupyter 无法访问 | `docker exec <name> curl -s http://localhost:8888/api` | jupyter 未启动、token 不匹配 |
| 环境变量不生效 | `docker exec <name> env \| grep -E "USER_PASSWORD\|JUPYTER"` | `.env` 文件未正确加载、变量名拼写错误 |
| 容器启动后立即退出 | `docker logs <name>` | entrypoint.sh 语法错误、Docker 启动失败、daemon.json 配置错误 |
| devuser 无法运行 docker | `docker exec <name> ls -la /var/run/docker.sock` | docker.sock 权限不对、用户不在 docker 组 |
| 构建时 apt/pip 下载慢 | 使用 `--cn` 参数或在 `.env` 中设置镜像源 | 网络问题，切换国内镜像源 |

## 清理

```bash
# 停止并移除容器
bash scripts/start.sh stop
# 或
docker compose --profile dind down

# 清理数据卷（注意：会丢失 Docker 数据）
docker volume rm devcontainer-base_docker-storage
docker volume rm devcontainer-base_workspace
```
