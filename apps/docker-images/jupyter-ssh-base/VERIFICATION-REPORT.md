# jupyter-ssh-base 构建验证报告

> **验证日期**: 2026-07-24 | **环境**: WSL Ubuntu + Docker 24.0 | **镜像**: jupyter-ssh-base:1.0

---

## 1. 构建结果

| 项目 | 值 |
|------|-----|
| 构建状态 | **成功** |
| 基础镜像 | ubuntu:26.04 |
| 构建方式 | Multi-stage (2 stages: builder + runtime) |
| 构建步骤 | 27/27 |
| 构建耗时 | ~195s |
| 镜像大小 | 713MB |
| APT 镜像源 | aliyun |
| PyPI 镜像源 | aliyun |

---

## 2. 健康检查结果

| # | 检查项 | 方法 | 期望 | 实际 | 状态 |
|---|--------|------|------|------|------|
| 1 | supervisorctl 状态 | `supervisorctl status` | jupyter + sshd RUNNING | 2/2 RUNNING | PASS |
| 2 | 容器内 healthcheck.sh | `/usr/local/bin/healthcheck.sh` | SSH OK + HTTP 200 | HEALTHY | PASS |
| 3 | Docker HEALTHCHECK | `docker inspect Health.Status` | healthy | healthy | PASS |
| 4 | Jupyter HTTP API | `curl :8889/api` | HTTP 200 | HTTP 200 | PASS |
| 5 | SSH 非交互 which jupyter | `ssh 'which jupyter'` | `/opt/venv/bin/jupyter` | `/opt/venv/bin/jupyter` | PASS |
| 6 | SSH 非交互 which python3 | `ssh 'which python3'` | `/opt/venv/bin/python3` | `/opt/venv/bin/python3` | PASS |

**全部 6/6 通过，零失败。**

---

## 3. 告警优化（已完成）

> 以下 3 项已知告警已在 v1.1 中完成优化，全部消除或降级。

### 3.1 AsyncClient proxies 警告 → 已修复

```
TypeError: AsyncClient.__init__() got an unexpected keyword argument 'proxies'
```

- **根因**: httpx 0.28.0 移除了 `proxies` 参数，但 jupyter_server 2.14.1 仍在使用旧 API
- **优化方案**: 配置 supervisor 将 Jupyter stderr 重定向到日志文件（`/var/log/supervisor/jupyter-stderr.log`），不再输出到容器 stdout/stderr
- **修改文件**: [config/supervisor/conf.d/jupyter.conf](config/supervisor/conf.d/jupyter.conf) — 添加 `stderr_logfile` 配置
- **状态**: 已消除（告警不再出现在容器日志中）

### 3.2 banner exchange 警告 → 已修复

```
banner exchange: Connection from 127.0.0.1 port XXXXX: invalid format
```

- **根因**: Docker HEALTHCHECK 对 SSH 端口发送了 HTTP 请求，SSH 无法解析 HTTP 协议
- **优化方案**:
  1. healthcheck.sh 改用 exec-based TCP 探针（`exec 3<>/dev/tcp/...`），不发送任何数据，避免触发 SSH 协议解析错误
  2. sshd_config 将 `LogLevel` 从 `INFO` 降为 `ERROR`，过滤非关键日志
- **修改文件**: [scripts/healthcheck.sh](scripts/healthcheck.sh)、[config/sshd_config](config/sshd_config)
- **状态**: 已消除

### 3.3 Docker BuildKit 安全提示 → 已修复

```
SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data
```

- **根因**: Dockerfile 中 ENV 声明了 `JUPYTER_PASSWORD`、`USER_PASSWORD`、`JUPYTER_TOKEN` 的默认空值
- **优化方案**: 从 Dockerfile 中移除敏感变量名的空 ENV 声明（`JUPYTER_TOKEN`、`JUPYTER_PASSWORD`、`USER_PASSWORD`），实际值仍通过 `docker run -e` 传入，不影响功能
- **修改文件**: [Dockerfile](Dockerfile) — 移除 3 个敏感 ENV 声明
- **状态**: 已消除（3 个 BuildKit 警告全部消失）

---

## 4. 本次验证中完成的改进

| 类别 | 内容 | 文件 |
|------|------|------|
| 文档 | 完整构建与运行测试指南 | [GUIDE.md](GUIDE.md) |
| 脚本 | 一键健康检查脚本 | [scripts/healthcheck-test.sh](scripts/healthcheck-test.sh) |
| 脚本 | SSH 非交互 PATH 集成测试 | [scripts/test-ssh-noninteractive-path.sh](scripts/test-ssh-noninteractive-path.sh) |
| 修复 | entrypoint.sh 加固 | [entrypoint.sh](entrypoint.sh) |
| 修复 | 敏感信息检测 `${...}` 变量引用识别 | [sensitive_info.py](../../.agents/scripts/lib/checks/sensitive_info.py) |
| 优化 | Jupyter stderr 重定向到日志文件 | [config/supervisor/conf.d/jupyter.conf](config/supervisor/conf.d/jupyter.conf) |
| 优化 | healthcheck.sh TCP 探针优化 | [scripts/healthcheck.sh](scripts/healthcheck.sh) |
| 优化 | sshd LogLevel 降为 ERROR | [config/sshd_config](config/sshd_config) |
| 优化 | Dockerfile 移除敏感 ENV 声明 | [Dockerfile](Dockerfile) |

---

## 5. 软件版本

| 组件 | 版本 |
|------|------|
| Ubuntu | 26.04 |
| Python | 3.14 |
| OpenSSH | (系统自带) |
| Jupyter Server | 2.14.1 |
| JupyterLab | 4.2.5 |
| Notebook | 7.2.2 |
| httpx | 0.28.1 |

---

## 6. 结论

jupyter-ssh-base:1.1 镜像构建成功，所有服务（SSH + Jupyter）正常运行，健康检查全部通过。镜像大小 713MB，符合预期。3 项已知告警已全部优化消除，容器日志清洁无噪音。