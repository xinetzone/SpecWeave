---
id: "dind-containerfile-rules"
title: "Containerfile 编写规范"
---
# Containerfile 编写规范（docker-ssh-dind）

## 基础约定

- 文件名为 `Containerfile`（非Dockerfile）
- 基础镜像：`ubuntu:26.04`（固定版本，不使用`latest`）
- 构建注释/日志使用**英文**（避免PowerShell/Shell编码问题）
- 每个Stage/关键步骤输出构建日志：`echo "[BUILD] ..."`

## 结构规范

按以下7个Stage组织，每个Stage用分隔线注释分隔：

1. **Environment**：ENV声明（DEBIAN_FRONTEND、TZ、LANG、LC_ALL、NON_ROOT_USER等）
2. **Base packages**：系统依赖 + 中文locale生成 + 时区设置
3. **Docker Engine**：Docker CE仓库配置 + docker-ce/containerd.io/buildx安装
4. **Non-root user**：创建ai用户(UID 1000) + docker组 + sudoers配置
5. **SSH config**：sshd_config配置 + 主机密钥清理（启动时再生）
6. **Docker daemon**：daemon.json配置（overlay2、json-file日志轮转、iptables=false）
7. **Finalization**：entrypoint安装 + 构建信息写入 + VOLUME/EXPOSE/ENTRYPOINT

## 层缓存优化

- 先安装不常变化的系统包，再复制/配置经常变化的文件
- 多个RUN指令合并为一个（用`&& \`连接），减少镜像层数
- apt-get update和install在同一个RUN中，避免缓存过期
- COPY指令放在最后阶段，优先复制不常变化的文件

## 安全规范

- 禁止在Containerfile中硬编码密码、密钥、token
- 敏感信息通过环境变量（-e）或build-arg传入
- SSH主机密钥在容器启动时生成，不打包到镜像中
- 创建用户后不使用USER指令切换（保持root运行dockerd，通过su切换用户）

## 中文环境配置

```dockerfile
ENV TZ=Asia/Shanghai
ENV LANG=zh_CN.UTF-8
ENV LANGUAGE=zh_CN:zh
ENV LC_ALL=zh_CN.UTF-8

# 安装locales包后执行：
RUN sed -i 's/^# *zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen zh_CN.UTF-8 && \
    update-locale LANG=zh_CN.UTF-8 && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone
```

## 体积优化

- 每个apt-get install后立即执行`rm -rf /var/lib/apt/lists/*`
- 使用`--no-install-recommends`减少不必要的依赖
- 多阶段构建仅在需要分离构建时/运行时使用（本项目为单阶段）

## 验证清单

- [ ] `docker build`无错误，构建日志有清晰的Stage标记
- [ ] 镜像中`locale -a`显示zh_CN.UTF-8
- [ ] 镜像中`date`显示Asia/Shanghai时区
- [ ] `id ai`显示uid=1000，groups包含docker和sudo
- [ ] `visudo -cf /etc/sudoers.d/ai`语法正确
- [ ] docker.sock权限666，ai用户可访问
