# Jupyter SSH Base - 标准化 Jupyter + SSH 基础镜像

> 基于 Ubuntu 26.04 的企业级 Docker 基础镜像，同时集成 OpenSSH Server 和 Jupyter Notebook/Lab，
> 通过 supervisord 进行进程管理，遵循 Docker 最佳实践，可作为其他项目的可靠基础层直接复用。

## ✨ 特性

- **基础镜像**：Ubuntu 26.04（固定标签，非 latest）
- **双服务管理**：Supervisord 管理 sshd + Jupyter，支持自动重启
- **企业级 SSH**：ED25519 优先密钥，非 root 用户，密码复杂度保障
- **安全增强 Jupyter**：密码/Token 认证，CORS 配置，非 root 运行
- **中文环境**：zh_CN.UTF-8 locale + Asia/Shanghai 时区
- **镜像优化**：多阶段包管理，apt 缓存清理，最小化攻击面
- **灵活配置**：环境变量驱动，支持运行时自定义
- **健康检查**：内置 HEALTHCHECK，可监控服务状态
- **可复用性**：清晰的扩展点，适合作为其他镜像的 base image

## 🏗️ 项目结构

```
jupyter-ssh-base/
├── Dockerfile                      # 主构建文件（7阶段构建）
├── entrypoint.sh                   # 容器启动脚本
├── requirements.txt                # Python 依赖版本固定
├── docker-compose.yml              # Compose 编排示例
├── .dockerignore                   # Docker 构建忽略文件
├── AGENTS.md                       # AI 协作者规范（SpecWeave）
├── config/
│   ├── supervisord.conf            # Supervisord 主配置
│   ├── sshd_config                 # SSH 服务完整配置
│   ├── jupyter_notebook_config.py  # Jupyter 基础配置
│   └── supervisor/
│       └── conf.d/
│           ├── sshd.conf           # SSH 进程配置
│           └── jupyter.conf        # Jupyter 进程配置
└── scripts/
    ├── build.sh                    # 一键构建脚本
    ├── healthcheck.sh              # 容器健康检查脚本
    └── test-ssh-noninteractive-path.sh  # SSH 非交互 PATH 集成测试
```

## 🚀 快速开始

### 构建镜像

```bash
# 方式1：直接 docker build
docker build -t jupyter-ssh-base:1.0 .

# 方式2：使用构建脚本
bash scripts/build.sh

# 自定义镜像名和标签
IMAGE_NAME=my-jupyter IMAGE_TAG=v2 bash scripts/build.sh
```

### 运行容器

```bash
# 基本运行（SSH + Jupyter）
docker run -d \
  --name jupyter-ssh \
  -p 2222:22 \
  -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -e USER_PASSWORD=your_secure_password \
  -e JUPYTER_TOKEN=your_jupyter_token \
  jupyter-ssh-base:1.0

# 查看日志（获取随机密码/token）
docker logs -f jupyter-ssh

# 调试模式（不启动服务，直接进入bash）
docker run -it --rm jupyter-ssh-base:1.0 bash
```

### 使用 Docker Compose

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

## 🔌 连接方式

### SSH 连接

```bash
# 使用密码登录
ssh jupyteruser@localhost -p 2222

# 使用公钥登录（启动时传入 SSH_PUBLIC_KEY 环境变量）
ssh jupyteruser@localhost -p 2222 -i ~/.ssh/id_ed25519
```

### Jupyter Notebook

打开浏览器访问：
```
http://localhost:8888/
```
使用启动时设置的 `JUPYTER_TOKEN` 或 `JUPYTER_PASSWORD` 登录。

## ⚙️ 环境变量配置

| 环境变量 | 默认值 | 说明 |
|---------|-------|------|
| `USER_PASSWORD` | *(随机生成)* | jupyteruser 用户密码，未设置时自动生成16位随机密码并打印到日志 |
| `ROOT_PASSWORD` | *(不设置)* | root 用户密码，需同时设置 ALLOW_ROOT_SSH=yes |
| `JUPYTER_TOKEN` | *(随机生成)* | Jupyter Notebook 访问令牌 |
| `JUPYTER_PASSWORD` | *(空)* | Jupyter Notebook 密码（与 Token 二选一） |
| `ALLOW_ROOT_SSH` | `no` | 是否允许 root 通过 SSH 登录 |
| `GRANT_SUDO` | `no` | 是否允许 jupyteruser 无密码 sudo |
| `SSH_PUBLIC_KEY` | *(空)* | SSH 公钥，设置后自动注入 authorized_keys |
| `TZ` | `Asia/Shanghai` | 时区设置 |
| `DEBUG` | `0` | 调试模式（1 启用 set -x） |

## 🔒 安全特性

1. **非 root 默认用户**：jupyteruser（UID 1000），所有服务以非 root 运行
2. **SSH 安全配置**：
   - 禁用 root 登录（默认）
   - ED25519 密钥优先
   - 禁用空密码
   - 严格模式（StrictModes yes）
3. **Jupyter 安全配置**：
   - Token/Password 认证
   - 绑定 0.0.0.0 但受端口映射控制
   - 跨域策略默认同源限制
4. **运行时密钥生成**：SSH host keys 在容器启动时生成，避免密钥复用
5. **最小化安装**：使用 --no-install-recommends，清理 apt 缓存和临时文件

## 🏗️ 作为基础镜像使用

本镜像设计为可复用基础层，在你的项目 Dockerfile 中：

```dockerfile
FROM jupyter-ssh-base:1.0

# 切换到 root 安装系统依赖（如需）
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    your-package \
    && rm -rf /var/lib/apt/lists/*

# 安装额外 Python 包
RUN pip install --no-cache-dir your-package

# 复制额外配置
# COPY your-config /etc/

# 切换回 jupyteruser
USER jupyteruser

# 保留原 ENTRYPOINT，服务会自动启动
```

## 📋 服务管理

容器内使用 supervisord 管理服务：

```bash
# 查看服务状态
supervisorctl status

# 重启服务
supervisorctl restart sshd
supervisorctl restart jupyter

# 查看日志
supervisorctl tail -f sshd
supervisorctl tail -f jupyter
```

## 🔧 构建优化说明

- **7阶段构建**：逻辑分层，便于维护和缓存利用
- **层合并**：相关 RUN 指令合并，减少镜像层数
- **no-install-recommends**：最小化安装包数量
- **缓存清理**：每个 apt 阶段后立即清理
- **pip --no-cache-dir**：不缓存 pip 安装文件
- **特定版本标签**：ubuntu:26.04，避免 latest 的不确定性

## 📝 版本信息

- **版本**：1.0
- **基础镜像**：ubuntu:26.04
- **Python**：系统 Python 3 (Ubuntu 26.04 默认)
- **Jupyter Notebook**：7.2.2
- **OpenSSH**：Ubuntu 26.04 官方包
- **Supervisor**：Ubuntu 26.04 官方包

## 📄 许可证

遵循 SpecWeave 项目规范。

## 🤝 扩展建议

如需更多功能（如 GPU 支持、特定 ML 框架、额外服务），建议：
1. 基于此镜像创建子镜像（FROM jupyter-ssh-base）
2. 参考 config/supervisor/conf.d/ 添加新的服务配置
3. 在 entrypoint 扩展逻辑（调用原始 entrypoint 后添加自定义步骤）

## 📖 更多文档

- [GUIDE.md](GUIDE.md) — 完整的 Docker 构建与运行测试指南（含环境变量参考、常见问题排查、docker-compose 部署）
- [scripts/test-ssh-noninteractive-path.sh](scripts/test-ssh-noninteractive-path.sh) — SSH 非交互 PATH 自动化测试脚本（8 项测试覆盖）
