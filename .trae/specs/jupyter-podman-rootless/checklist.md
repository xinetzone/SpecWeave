# Jupyter Podman Rootless - Verification Checklist

## 项目结构与规范
- [ ] 目录 `apps/containers/jupyter-podman-rootless/` 已创建
- [ ] 目录结构完整：Containerfile、entrypoint.sh、config/、scripts/、tasks/、conda-lock/、pyproject.toml
- [ ] AGENTS.md 存在且包含启动协议和正确路由
- [ ] .containerignore（或.dockerignore）存在，排除不必要文件
- [ ] apps/AGENTS.md 已更新，添加新应用路由条目

## 镜像构建
- [ ] Containerfile 语法正确，首行包含 `# syntax=docker/dockerfile:1.7-labs`
- [ ] `invoke build` 或 `podman build` 成功完成无错误
- [ ] 构建过程中所有语法验证检查点通过（sshd -t、bash -n等）
- [ ] 构建日志清晰，包含[INFO]/[OK]/[TIMER]结构化输出
- [ ] 支持国内镜像源构建参数（--build-arg APT_MIRROR=aliyun等）
- [ ] 镜像体积控制在合理范围（<2.5GB）

## Python/Conda环境
- [ ] 容器内 `python --version` 显示 Python 3.14.x
- [ ] 容器内 `python -c "import sys; print(sys.free_threaded)"` 返回 True（cp314t free-threading）
- [ ] `conda --version` 命令可用
- [ ] `which python` 指向 `/opt/conda/envs/main/bin/python`
- [ ] `jupyter lab --version` 和 `jupyter notebook --version` 可用
- [ ] conda配置使用conda-forge源和libmamba solver

## 非root用户与权限
- [ ] 容器内默认用户是devuser，非root
- [ ] `id` 显示UID为1000（或其他非0值）
- [ ] `/etc/subuid` 和 `/etc/subgid` 包含 `devuser:100000:65536`
- [ ] `/workspace` 目录所有者是devuser
- [ ] 家目录 `/home/devuser` 权限正确（700 for .ssh等）
- [ ] 默认禁用sudo（除非GRANT_SUDO=yes）

## SSH服务
- [ ] supervisord管理的sshd服务运行中
- [ ] sshd_config中PermitRootLogin设为no
- [ ] 端口映射后SSH可连接（ssh devuser@localhost -p 2222）
- [ ] 密码认证可工作（使用USER_PASSWORD）
- [ ] 公钥认证可工作（使用SSH_PUBLIC_KEY）
- [ ] root登录被拒绝

## Jupyter服务
- [ ] supervisord管理的jupyter服务运行中
- [ ] Jupyter监听0.0.0.0:8888
- [ ] 端口映射后可访问 http://localhost:8888
- [ ] Jupyter token认证工作（使用JUPYTER_TOKEN或自动生成）
- [ ] 默认工作目录是/workspace
- [ ] 不允许以root身份运行Jupyter（allow_root=False）
- [ ] Jupyter API健康检查返回200

## Podman rootless（容器内容器）
- [ ] 容器内 `podman --version` 可用
- [ ] 容器内 `crun --version` 可用
- [ ] `fuse-overlayfs` 二进制可用
- [ ] `slirp4netns` 可用
- [ ] Podman storage配置使用fuse-overlayfs驱动
- [ ] 以devuser身份执行 `podman info` 成功
- [ ] 以devuser身份执行 `podman run --rm alpine echo hello` 成功（不需要--privileged）

## Invoke任务
- [ ] `invoke --list` 列出所有任务：build、run、stop、shell、logs、clean、status
- [ ] `invoke build --help` 显示清晰的帮助信息
- [ ] `invoke run` 成功启动容器，映射端口2222和8888
- [ ] `invoke status` 正确显示容器运行状态
- [ ] `invoke logs` 显示容器日志
- [ ] `invoke shell` 进入容器交互式shell
- [ ] `invoke stop` 停止并删除容器
- [ ] `invoke clean` 清理无用镜像和容器

## 健康检查与运行时
- [ ] 容器健康检查（healthcheck）返回healthy
- [ ] healthcheck.sh同时检测sshd和jupyter
- [ ] entrypoint.sh支持命令模式（docker run ... bash 直接进入shell）
- [ ] 环境变量可配置：USER_PASSWORD、JUPYTER_TOKEN、GRANT_SUDO、SSH_PUBLIC_KEY
- [ ] 未设置密码/token时自动生成随机值并输出到日志
- [ ] 启动横幅清晰显示SSH和Jupyter访问信息

## 中文环境
- [ ] `locale` 显示 LANG=zh_CN.UTF-8
- [ ] `date` 显示Asia/Shanghai时区时间
- [ ] 中文字符可正常显示（无乱码）

## 卷挂载与权限（核心验证）
- [ ] 挂载本地目录到/workspace后，容器内创建的文件在宿主机上可见
- [ ] 宿主机用户对挂载目录中创建的文件有读写权限（无root-owned文件问题）
- [ ] 容器内可读写挂载目录中的文件
