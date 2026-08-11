---
id: "jupyter-ssh-build-test-rules"
title: "构建与测试流程"
source: "AGENTS.md#快速开始"
---
# 构建与测试流程（jupyter-ssh-base）

## 快速开始

### 构建镜像

```bash
# 标准构建
docker build -t jupyter-ssh-base .

# 使用构建脚本
bash scripts/build.sh

# 使用国内镜像源构建
docker build --build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=tuna -t jupyter-ssh-base .
```

### 运行容器

```bash
# 基本运行（映射SSH 2222和Jupyter 8888端口）
docker run -d -p 2222:22 -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e JUPYTER_TOKEN=mysecret \
  -v jupyter-workspace:/workspace \
  --name jupyter-test jupyter-ssh-base

# 启用sudo权限
docker run -d -p 2222:22 -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e GRANT_SUDO=yes \
  -v jupyter-workspace:/workspace \
  --name jupyter-test jupyter-ssh-base

# 启用root SSH登录（不推荐，仅用于特殊场景）
docker run -d -p 2222:22 -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e ALLOW_ROOT_SSH=yes \
  -v jupyter-workspace:/workspace \
  --name jupyter-test jupyter-ssh-base

# 挂载SSH公钥免密登录
docker run -d -p 2222:22 -p 8888:8888 \
  -v ~/.ssh/authorized_keys:/home/jupyteruser/.ssh/authorized_keys:ro \
  -e JUPYTER_TOKEN=mysecret \
  -v jupyter-workspace:/workspace \
  --name jupyter-test jupyter-ssh-base
```

### 验证服务

```bash
# 查看服务状态
docker exec -it jupyter-test supervisorctl status

# 验证SSH（使用jupyteruser，root默认禁用）
ssh -p 2222 jupyteruser@localhost

# 验证Jupyter（浏览器访问）
# http://localhost:8888/?token=mysecret

# 调试模式（不启动服务，直接进入shell）
docker run -it --rm jupyter-ssh-base bash

# 以root身份进入运行中的容器
docker exec -it -u root jupyter-test bash
```

### 使用 docker-compose

参考 `docker-compose.yml` 示例：
```bash
docker-compose up -d
```

## 构建验证清单

每次修改 Dockerfile 后必须验证：

```bash
# 1. 语法检查（使用项目根目录的自动化测试脚本）
powershell -ExecutionPolicy Bypass -File ../../.agents/scripts/test-dockerfiles.ps1 -File Dockerfile

# 2. 实际构建
docker build -t jupyter-ssh-base:test .

# 3. 运行容器
docker run -d --name jupyter-test -p 2222:22 -p 8888:8888 \
  -e USER_PASSWORD=test123 -e JUPYTER_TOKEN=testtoken jupyter-ssh-base:test

# 4. 等待服务启动
sleep 10

# 5. 验证supervisord
docker exec jupyter-test supervisorctl status
# 期望输出：sshd RUNNING, jupyter RUNNING

# 6. 验证SSH端口
docker exec jupyter-test bash -c "ss -tlnp | grep :22"

# 7. 验证Jupyter HTTP
docker exec jupyter-test bash -c "curl -s -o /dev/null -w '%{http_code}' http://localhost:8888/api"
# 期望输出：200 或 302

# 8. 验证中文环境
docker exec jupyter-test locale
# 期望：LANG=zh_CN.UTF-8

# 9. 验证时区
docker exec jupyter-test date
# 期望：CST 时区（Asia/Shanghai）

# 10. 验证非root用户
docker exec jupyter-test id jupyteruser
# 期望：uid=1000(jupyteruser) gid=1000(jupyteruser)

# 11. 验证Python虚拟环境
docker exec jupyter-test /opt/venv/bin/python --version
docker exec jupyter-test /opt/venv/bin/jupyter --version

# 12. 清理测试容器
docker rm -f jupyter-test
```

## 构建脚本（scripts/build.sh）

构建脚本应支持：
- 彩色输出（INFO/OK/ERROR）
- 构建计时
- 自动标签（latest + 日期戳）
- 可选的 BuildKit 启用/禁用
- 构建失败时输出最后50行日志供排查

## Python 依赖管理

依赖列表在 `requirements.txt`，必须固定版本号（避免构建不确定性）：
```
jupyter==1.0.0
notebook==6.5.5
# ... 其他依赖
```

Builder 阶段安装依赖时使用：
```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt
```

## .dockerignore

必须排除以下非构建文件：
- `.git/`、`.trae/`、`.agents/`（版本控制和AI工作目录）
- `__pycache__/`、`*.pyc`（Python缓存）
- `workspace/`、`notebooks/`（用户数据目录）
- `*.md`（文档，README除外）
- `docker-compose.yml`（编排文件，非构建必需）
