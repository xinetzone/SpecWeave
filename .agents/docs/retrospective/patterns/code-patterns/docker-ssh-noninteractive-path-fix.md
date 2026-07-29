---
id: "docker-ssh-noninteractive-path-fix"
source: "jupyter-ssh-base Dockerfile /etc/environment PATH 修复"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/docker-ssh-noninteractive-path-fix.toml"
---
# Docker+SSH 非交互会话 PATH 修复模式

## 问题

在 Docker 容器中设置了自定义 PATH（如 Python 虚拟环境 `/opt/venv/bin`），`docker exec` 和交互式 SSH 登录均可正常访问，但 `ssh user@host 'which <cmd>'` 等非交互 SSH 会话找不到命令。症状表现为：

- `docker exec <container> which jupyter` → `/opt/venv/bin/jupyter` ✓
- 交互式 SSH 登录后 `which jupyter` → `/opt/venv/bin/jupyter` ✓
- `ssh user@host 'which jupyter'` → 空输出或 `command not found` ✗

## 解决方案

SSH 非交互会话通过 PAM 读取 `/etc/environment` 获取 PATH，而非继承 Dockerfile `ENV` 层。需同时配置三个层面：

1. **Dockerfile ENV**：供交互式会话和 `docker exec` 使用
2. **/etc/environment**：供 SSH 非交互会话（PAM 读取）使用
3. **/etc/profile.d/venv.sh**：供登录 shell 使用

## 代码

### ❌ 反模式：仅依赖 Dockerfile ENV

```dockerfile
ENV PATH=/opt/venv/bin:$PATH
# 问题：SSH 非交互会话不继承此 PATH
```

### ✅ 推荐模式：三层 PATH 配置

```dockerfile
# 1. Dockerfile ENV（交互式 + docker exec）
ENV PATH=/opt/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# 2. /etc/environment（SSH 非交互 PAM 读取）
RUN echo "PATH=/opt/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /etc/environment

# 3. profile.d（登录 shell）
RUN echo 'export PATH=/opt/venv/bin:$PATH' > /etc/profile.d/venv.sh && \
    chmod 644 /etc/profile.d/venv.sh
```

### 验证方法

```bash
# 非交互 SSH 命令测试
sshpass -p 'password' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -p <port> user@host 'which target_cmd && target_cmd --version'
```

## 适用场景

- 任何包含 SSH 服务的 Docker 镜像（如开发容器、远程工作站）
- 镜像中使用了 virtualenv/conda 等需要自定义 PATH 的 Python 环境
- 需要使用 `ssh user@host 'command'` 远程执行命令的自动化场景

## 根因分析

SSH 非交互会话的 PATH 来源链：
```
Dockerfile ENV → 容器运行时环境变量（仅交互式继承）
PAM → /etc/environment → PATH（非交互式 SSH 会话唯一来源）
/etc/profile.d/*.sh → PATH（登录 shell，非交互式不触发）
```

关键差异：Dockerfile `ENV` 设置的环境变量存在于容器进程的环境变量表中，但 SSH 非交互会话 fork 新进程时，PAM 模块从 `/etc/environment` 重新读取环境变量，覆盖了父进程的 ENV 设置。

## 成熟度

L2 已验证 — jupyter-ssh-base 项目中通过 sshpass 非交互 SSH 测试验证 `which jupyter` 返回 `/opt/venv/bin/jupyter`。

## 交叉引用

- 来源：jupyter-ssh-base 项目完工复盘 [retrospective-jupyter-ssh-base-20260724](../../reports/project-reports/retrospective-jupyter-ssh-base-20260724/README.md#L56-L64)
- 关联模式：env-var-alias-backward-compat（同项目 Docker 最佳实践系列）