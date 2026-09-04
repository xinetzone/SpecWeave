# devcontainer-base - Verification Checklist

## 目录结构与基础文件
- [ ] apps/devcontainer-base/ 目录已创建
- [ ] config/、config/supervisor/、config/supervisor/conf.d/、scripts/、scripts/lib/ 子目录存在
- [ ] .dockerignore 文件存在且包含合理的排除规则（.git、.trae、.agents、workspace等）
- [ ] requirements.txt 包含 notebook、jupyterlab、ipykernel、nbconvert、jupyter_server，版本固定
- [ ] AGENTS.md 包含"启动协议"关键词，正确引用父级 ../../AGENTS.md，包含项目概述和约束
- [ ] AGENTS.md 包含上下文路由表、核心规范入口、项目特有约束、快速开始章节

## Dockerfile 多阶段构建
- [ ] Dockerfile 使用两阶段构建（jupyter-builder AS builder + runtime）
- [ ] builder 阶段安装 build-essential、python3-dev、python3-pip、python3-venv
- [ ] builder 阶段创建 /opt/venv 并安装 requirements.txt 中Python包，支持 PIP_MIRROR build-arg
- [ ] builder 阶段支持 APT_MIRROR build-arg（aliyun/tuna/official）
- [ ] runtime 阶段基于 ubuntu:26.04，安装所有必要系统包（ca-certificates到fuse-overlayfs等）
- [ ] runtime 阶段配置中文 locale（zh_CN.UTF-8）和时区（Asia/Shanghai），三层保证（tzdata + ln -sf + ENV TZ）
- [ ] Docker CE 安装正确：添加GPG key、添加apt源、安装docker-ce/docker-ce-cli/containerd.io/docker-buildx-plugin
- [ ] Podman 安装正确：从Ubuntu 26.04官方源安装podman和相关依赖（crun/conmon/slirp4netns/fuse-overlayfs/uidmap）
- [ ] 从builder复制/opt/venv，配置PATH和VIRTUAL_ENV环境变量，profile.d/venv.sh系统级配置
- [ ] devuser创建逻辑正确：UID 1000优先，加入docker和sudo组，home目录权限正确
- [ ] /etc/subuid 和 /etc/subgid 为devuser配置rootless映射
- [ ] daemon.json 配置正确（storage-driver=overlay2, iptables=false, log-driver=json-file, userland-proxy=false）
- [ ] 所有配置文件和脚本（sshd_config、supervisord.conf、entrypoint.sh、healthcheck.sh等）正确COPY
- [ ] sshd -t 在构建时验证通过
- [ ] 关键命令可用性验证（sshd、supervisord、python、pip、jupyter、bash -n 检查脚本语法）
- [ ] /etc/devcontainer-build-info 构建元数据文件存在且内容完整
- [ ] 每个RUN指令后清理apt缓存（rm -rf /var/lib/apt/lists/*），pip使用--no-cache-dir
- [ ] 构建日志包含"[BUILD]"标记，最终有"BUILD COMPLETE"
- [ ] WORKDIR=/workspace，VOLUME ["/workspace", "/var/lib/docker"]，EXPOSE 22 8888
- [ ] HEALTHCHECK 配置合理（interval=30s, timeout=10s, start-period=60s, retries=3）
- [ ] ENTRYPOINT 使用 tini -- /usr/local/bin/entrypoint.sh，CMD为空支持命令模式

## supervisord 与服务配置
- [ ] config/supervisord.conf 主配置正确（nodaemon=true, unix_http_server, include conf.d/*.conf）
- [ ] config/supervisor/conf.d/sshd.conf 存在，sshd以前台模式运行
- [ ] config/supervisor/conf.d/jupyter.conf 存在，jupyter以devuser身份启动
- [ ] config/supervisor/conf.d/dockerd.conf 存在，dockerd以前台模式运行（--iptables=false等参数）
- [ ] config/sshd_config 配置正确（ED25519优先，PermitRootLogin可配置，PasswordAuthentication yes，PubkeyAuthentication yes）
- [ ] config/jupyter_notebook_config.py 基础配置正确（0.0.0.0绑定，/workspace目录）
- [ ] 所有supervisor配置包含autorestart=true和合理的startsecs/startretries

## entrypoint.sh 启动脚本
- [ ] 脚本开头 set -euo pipefail，支持 DEBUG=1 set -x
- [ ] 包含环境变量兼容处理（ENABLE_SUDO_NOPASSWD→GRANT_SUDO，JUPYTER_CORS_ORIGIN→JUPYTER_ALLOW_ORIGIN）
- [ ] log_info/log_warn/log_error 日志函数正确，带时间戳
- [ ] print_banner 启动横幅函数存在
- [ ] diagnose_system 系统诊断函数：输出OS/Kernel/Arch/Timezone/Locale/User/Build info
- [ ] setup_passwords 密码设置：支持ROOT_PASSWORD/USER_PASSWORD环境变量，未设置时用pwgen生成随机密码并打印，支持GRANT_SUDO=yes配置NOPASSWD sudo
- [ ] generate_host_keys：启动时删除旧host keys并重新生成（ssh-keygen -A）
- [ ] configure_sshd：根据ALLOW_ROOT_SSH配置PermitRootLogin，运行sshd -t验证
- [ ] setup_ssh_keys：支持SSH_PUBLIC_KEY环境变量注入authorized_keys
- [ ] setup_jupyter：动态生成jupyter_server_config.d/runtime.py，支持JUPYTER_PASSWORD/JUPYTER_TOKEN，未设置时生成随机token
- [ ] setup_docker：根据ENABLE_DOCKER决定是否启用dockerd，支持DOCKER_HOST（DooD模式）
- [ ] setup_podman：根据ENABLE_PODMAN配置subuid/subgid和fuse-overlayfs
- [ ] 服务条件启用逻辑：根据ENABLE_SSH/ENABLE_DOCKER/ENABLE_PODMAN/ENABLE_JUPYTER环境变量控制哪些服务由supervisord启动
- [ ] print_access_info：打印SSH/Jupyter/Docker访问信息（密码/token等）
- [ ] 命令模式支持：$# -gt 0时跳过服务启动，exec "$@"直接执行用户命令
- [ ] 默认执行流程：print_banner → diagnose_system → setup_passwords → generate_host_keys → configure_sshd → setup_ssh_keys → setup_jupyter → setup_docker → setup_podman → print_access_info → exec supervisord
- [ ] bash -n entrypoint.sh 语法检查通过

## healthcheck.sh 健康检查
- [ ] 脚本检查sshd：进程存在且22端口监听（仅当SSH启用）
- [ ] 脚本检查docker：docker info成功（仅当Docker启用）
- [ ] 脚本检查jupyter：curl访问127.0.0.1:8888返回200（仅当Jupyter启用）
- [ ] 脚本检查podman：podman info成功（仅当Podman启用）
- [ ] 所有启用服务检查通过返回0，否则返回1并输出诊断信息
- [ ] 合理处理服务未就绪状态（启动期不直接判定失败）
- [ ] bash -n healthcheck.sh 语法检查通过

## 辅助脚本
- [ ] scripts/build.sh 存在，支持默认构建和--cn国内源构建
- [ ] scripts/build.ps1 存在（Windows PowerShell版本）
- [ ] scripts/lib/logging.sh 日志库存在
- [ ] docker-compose.yml 存在，包含DinD和DooD两种使用示例
- [ ] build.sh可执行权限正确

## 镜像构建验证
- [ ] docker build -t devcontainer-base . 构建成功，无错误
- [ ] docker build --build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun -t devcontainer-base-cn . 国内源构建成功
- [ ] 构建日志清晰，各阶段有明确标记
- [ ] 镜像中关键命令可用：python3、pip、jupyter、docker、podman、sshd、supervisord、supervisorctl

## 功能验证（容器运行时）
- [ ] 默认启动：docker run -d --privileged -p 2222:22 -p 8888:8888 -e USER_PASSWORD=test123 -e JUPYTER_TOKEN=test --name dc-test devcontainer-base 启动成功
- [ ] 等待60秒后，docker exec dc-test supervisorctl status 显示sshd、dockerd、jupyter均为RUNNING状态，podman未在supervisord中
- [ ] SSH登录验证：ssh -p 2222 devuser@localhost（密码test123）登录成功
- [ ] devuser登录后docker ps可直接执行（docker组权限，无需sudo）
- [ ] Jupyter访问：curl http://localhost:8888/?token=test 返回200
- [ ] Docker DinD验证：docker exec dc-test docker run --rm hello-world 输出Hello from Docker!
- [ ] Podman单独启用：docker run -d --privileged -e ENABLE_DOCKER=no -e ENABLE_PODMAN=yes -p 2223:22 -e USER_PASSWORD=test --name dc-podman devcontainer-base 启动后，podman info成功，podman run --rm alpine echo hello可执行
- [ ] 服务禁用验证：docker run -d -p 8889:8888 -e ENABLE_SSH=no -e ENABLE_DOCKER=no -e ENABLE_PODMAN=no -e JUPYTER_TOKEN=test --name dc-jupyteronly devcontainer-base 启动后，22端口未监听，仅Jupyter运行
- [ ] 命令模式验证：docker run -it --rm devcontainer-base bash 直接进入shell，supervisord未启动，exit后容器停止
- [ ] 健康检查：等待启动期后，docker inspect --format='{{.State.Health.Status}}' dc-test 显示healthy
- [ ] sudo权限验证：以-e GRANT_SUDO=yes启动后，devuser执行sudo -n whoami返回root，无需密码
- [ ] 公钥认证：传入-e SSH_PUBLIC_KEY="..."启动后，对应私钥可无密码登录
- [ ] 中文环境：docker exec dc-test locale 显示LANG=zh_CN.UTF-8，date显示CST时区
- [ ] 可复用性：创建简单Dockerfile（FROM devcontainer-base + 简单RUN命令），构建并运行成功，继承服务正常工作

## 文档与规范
- [ ] README.md 存在且内容完整
- [ ] README包含快速开始、环境变量表、使用模式说明、端口/卷说明、基础镜像使用示例
- [ ] apps/AGENTS.md 已更新，应用路由表添加devcontainer-base条目
- [ ] 环境变量命名与现有镜像兼容（USER_PASSWORD、JUPYTER_TOKEN、GRANT_SUDO、ALLOW_ROOT_SSH等沿用jupyter-ssh-base命名）
- [ ] 镜像中无硬编码密码/密钥，所有敏感信息在entrypoint运行时生成或环境变量注入
