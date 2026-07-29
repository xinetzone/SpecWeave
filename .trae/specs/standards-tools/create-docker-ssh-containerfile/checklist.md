# Docker-in-Docker SSH 验证清单

## 构建
- [x] Containerfile 使用 ubuntu:26.04 基础镜像
- [x] openssh-server 已安装配置（PermitEmptyPasswords=no）
- [x] Docker CE 官方仓库配置（GPG+HTTPS）
- [x] dockeruser(UID 1000) 已创建并加入 docker 组
- [x] entrypoint.sh 处理环境变量（ROOT_PASSWORD/SSH_PUBLIC_KEY/DOCKER_OPTS/ALLOW_ROOT_SSH）
- [x] tini 作为 init 进程，sshd 前台运行，dockerd 后台运行
- [x] VOLUME /var/lib/docker, EXPOSE 22
- [x] 无硬编码密码/密钥（主机密钥运行时生成）
- [ ] docker build 构建成功
- [ ] SSH 密码登录成功
- [ ] SSH 公钥免密登录成功
- [ ] docker version/info/run hello-world 正常
- [ ] dockeruser 可运行 docker 命令
- [ ] docker stop 优雅关闭
