---
id: "docker-ssh-noninteractive-path-fix"
title: "Docker+SSH 非交互会话 PATH 四重保障模式"
type: "code-pattern"
maturity: "L2-validated"
maturity_note: "jupyter-ssh-base v1.2 全链路验证：docker exec + SSH交互 + SSH非交互 + supervisord启动 四种场景均覆盖"
source:
  - "jupyter-ssh-base Dockerfile /etc/environment PATH 修复 + supervisor environment 配置"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/docker-ssh-noninteractive-path-fix.toml"
related_patterns:
  - "docker-buildtime-vs-runtime-config.md"
  - "docker-timezone-configuration.md"
tags: ["docker", "ssh", "path", "environment-variable", "pam", "supervisord", "venv", "non-interactive-shell"]
validation_count: 2
reuse_count: 2
---

# Docker+SSH 非交互会话 PATH 四重保障模式

## 触发场景

- 设计包含 SSH 服务的 Docker 开发镜像（Jupyter、远程工作站、CI runner 等）
- 镜像中使用 virtualenv/conda 等需要自定义 PATH 的 Python/Node/Rust 环境
- 遇到以下任一症状：
  - `docker exec <container> which cmd` 正常，但 `ssh user@host 'which cmd'` 返回空
  - `supervisorctl start <service>` 启动的进程找不到自定义路径下的二进制
  - 交互式 SSH 登录正常，但 `ssh user@host 'remote-command'` 报 `command not found`
  - 不同入口（exec/SSH/服务进程）下 `which python` 指向不同路径

## 问题本质

Docker 容器中存在 **四种进程启动入口**，每种入口有独立的环境变量加载链路：

```
进程启动入口              PATH 来源                          典型场景
─────────────────────────────────────────────────────────────────────
docker exec / ENTRYPOINT   Dockerfile ENV → 进程环境表        PID 1、docker exec 命令
SSH 交互式登录             PAM → /etc/environment → profile.d  ssh 后进入 shell
SSH 非交互式远程命令       PAM → /etc/environment (仅)       ssh host 'cmd'
supervisord 启动的子进程   supervisord environment= 配置      supervisorctl start xxx
```

**核心反常识**：Dockerfile 的 `ENV PATH=...` 并非全局生效——SSH 非交互会话通过 PAM 从 `/etc/environment` 独立加载 PATH，supervisord 子进程使用显式 `environment=` 配置或继承被裁剪的环境，不读取 Docker ENV。只配置单层会导致某些入口失效。

## 标准方案（四重保障）

必须同时配置四个层面，缺一不可：

### 第 1 层：Dockerfile ENV（ENTRYPOINT 进程 + docker exec）

```dockerfile
ENV PATH="/opt/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

覆盖：`docker run` 启动的 PID 1 进程（entrypoint）、`docker exec` 进入的进程。

### 第 2 层：/etc/environment（SSH 非交互会话 PAM 读取）

```dockerfile
RUN echo "PATH=/opt/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /etc/environment
```

覆盖：`ssh user@host 'which jupyter'` 这类非交互远程命令执行。**这是最容易被遗漏的一层**。

### 第 3 层：/etc/profile.d/*.sh（登录 shell）

```dockerfile
RUN echo 'export PATH=/opt/venv/bin:$PATH' > /etc/profile.d/venv.sh && \
    echo 'export VIRTUAL_ENV=/opt/venv' >> /etc/profile.d/venv.sh && \
    chmod +x /etc/profile.d/venv.sh
```

覆盖：交互式 SSH 登录后的 shell 会话（虽然交互式登录也会继承 Docker ENV，但 profile.d 是标准的 shell 初始化位置，可作为冗余保障）。

同时写入用户 `~/.bashrc`，确保 su/sudo 切换用户后也能找到路径：

```dockerfile
RUN echo 'export PATH=/opt/venv/bin:$PATH' >> /home/jupyteruser/.bashrc && \
    echo 'export VIRTUAL_ENV=/opt/venv' >> /home/jupyteruser/.bashrc
```

### 第 4 层：supervisord [program] environment=（supervisor 管理的服务）

```ini
# /etc/supervisor/conf.d/jupyter.conf
[program:jupyter]
user=jupyteruser
command=jupyter notebook --config=...
environment=HOME="/home/jupyteruser",USER="jupyteruser",VIRTUAL_ENV="/opt/venv",PATH="/opt/venv/bin:/usr/local/bin:/usr/bin:/bin"
```

覆盖：通过 `supervisorctl start jupyter` 启动的服务进程。supervisord 启动子进程时环境变量可能被裁剪，必须显式声明关键变量。

## 反模式（至少 3 个，来自实际踩坑）

### ❌ 反模式 1：仅依赖 Dockerfile ENV（最常见）

```dockerfile
# 错误：只设了 ENV PATH，SSH 非交互和 supervisord 进程仍然找不到命令
ENV PATH=/opt/venv/bin:$PATH
```

后果：`ssh user@host 'jupyter --version'` 报 `command not found`，但 `docker exec` 正常。调试时容易混淆"为什么同一个镜像有时好用有时不好用"。

### ❌ 反模式 2：只改 ~/.bashrc 不碰 /etc/environment

```dockerfile
# 错误：.bashrc 仅在交互式 bash 启动时读取，SSH 非交互不读取
RUN echo 'export PATH=/opt/venv/bin:$PATH' >> /home/user/.bashrc
```

后果：`ssh user@host 'echo $PATH'` 仍然是系统默认 PATH，不包含 /opt/venv/bin。

### ❌ 反模式 3：supervisor 中依赖继承 PATH 不写 environment=

```ini
# 错误：依赖 supervisord 继承父进程 PATH，不同版本/发行版行为不一致
[program:myservice]
command=/opt/venv/bin/jupyter notebook
```

后果：在某些宿主机/发行版上正常，在另一些上启动失败，难以复现。正确做法是显式写 `environment=PATH="..."`。

### ❌ 反模式 4：用 login shell 包装命令（`bash -l -c 'cmd'`）

```bash
# 看似解决问题但有副作用：启动慢、加载不必要的profile、可能改变LANG/CWD等
ssh user@host 'bash -l -c "which jupyter"'
```

这是 workaround 而非根本修复，会导致每个远程命令都启动 login shell，增加延迟且可能改变工作目录和语言环境。

## 检验标准

构建后启动容器，依次执行以下四条验证命令，**全部返回正确路径才算合格**：

```bash
# 1. docker exec 入口（第 1 层）
docker exec <container> which jupyter
# 期望：/opt/venv/bin/jupyter

# 2. SSH 非交互远程命令（第 2 层）
ssh -p <port> user@host 'which jupyter'
# 期望：/opt/venv/bin/jupyter

# 3. SSH 交互式登录后执行（第 3 层）
ssh -p <port> user@host
# 登录后执行 which jupyter
# 期望：/opt/venv/bin/jupyter

# 4. supervisor 管理的服务进程（第 4 层）
docker exec <container> supervisorctl status
docker exec <container> bash -c 'cat /proc/$(pgrep -f jupyter)/environ | tr "\0" "\n" | grep PATH'
# 期望：PATH 包含 /opt/venv/bin
```

## 迁移示例（跨领域）

不仅适用于 Python venv，同样适用于任何需要自定义 PATH 的场景：

**Node.js nvm 环境**：
```dockerfile
ENV PATH="/root/.nvm/versions/node/v20/bin:$PATH"
RUN echo "PATH=/root/.nvm/versions/node/v20/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /etc/environment
# ... 其他三层同理
```

**Rust cargo bin**：
```dockerfile
ENV PATH="/root/.cargo/bin:$PATH"
RUN echo "PATH=/root/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /etc/environment
```

**自定义编译工具路径**（如 /opt/llvm/bin）：
```dockerfile
ENV PATH="/opt/llvm/bin:$PATH"
RUN echo "PATH=/opt/llvm/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /etc/environment
```

## 边界条件与常见疑问（来自对抗审查）

**Q: 为什么不直接用绝对路径（如 /opt/venv/bin/jupyter）？是不是过度设计？**

绝对路径只能解决 supervisord 启动服务这单点问题。用户 SSH 登录后手动执行 `jupyter notebook`、`ssh host 'jupyter nbconvert'` 远程命令等场景都依赖 PATH 查找。四层保障解决**所有入口**的一致性，不是单点修补——每层配置仅1-3行，维护成本极低，换来全场景一致体验。

**不适用场景**：
- 单进程容器（无 SSH、无 supervisord，只有 ENTRYPOINT 一个进程）：只需第1层 Dockerfile ENV 即可
- 不需要远程命令执行的一次性任务容器：可省略第2/4层

## 成熟度

L2-validated — jupyter-ssh-base v1.1/v1.2 项目中通过 sshpass 非交互 SSH 测试 + supervisor 进程环境验证，四种入口的 which jupyter 均返回 `/opt/venv/bin/jupyter`。caffe-ffi-jupyter 继承自 jupyter-ssh-base 复用此模式，验证通过。V阶段对抗审查（怀疑者/实践者/运维/SRE/维护者五视角）全部通过。

## 交叉引用

- 来源：jupyter-ssh-base 项目七概念方法论复盘（2026-08-07）
- 关联模式：
  - docker-buildtime-vs-runtime-config.md（ENTRYPOINT 运行时配置原则）
  - docker-timezone-configuration.md（同样是多入口配置一致性问题）
  - env-var-alias-backward-compat.md（环境变量向后兼容别名设计）
- 验证脚本：scripts/test-ssh-noninteractive-path.sh（8 项测试覆盖）
