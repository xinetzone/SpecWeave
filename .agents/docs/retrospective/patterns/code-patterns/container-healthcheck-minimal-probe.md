---
id: "container-healthcheck-minimal-probe"
title: "容器健康检查最小探针设计模式"
type: "code-pattern"
maturity: "L1-draft"
maturity_note: "jupyter-ssh-base v1.1+ 实战验证；单案例，待更多项目验证后升级L2"
source:
  - "jupyter-ssh-base healthcheck.sh TCP探针设计 + v1.1 banner exchange告警修复"
related_patterns:
  - "docker-buildtime-vs-runtime-config.md"
  - "dockerfile-runtime-logical-layering.md"
tags: ["docker", "healthcheck", "supervisord", "tcp-probe", "logging", "observability", "noisereduction"]
validation_count: 1
reuse_count: 1
---

# 容器健康检查最小探针设计模式

## 触发场景

- 为 Docker 容器设计 HEALTHCHECK 脚本
- 多服务容器（如 SSH + Jupyter、Nginx + App 等通过 supervisord 管理）
- 遇到以下任一问题：
  - 健康检查导致服务日志充满噪音（如 SSH 的 banner exchange 错误）
  - 健康检查本身"太聪明"，发送完整应用层请求导致副作用
  - 健康检查偶发失败，因为依赖了第三方库版本兼容的响应格式
  - 不同健康检查方式（Docker HEALTHCHECK / k8s probe / 外部监控）行为不一致
  - 第三方依赖的已知兼容性警告污染容器 stdout/stderr

**不适用场景**：
- 需要深度功能验证（如登录后执行业务操作）的端到端探针——那应该是独立的集成测试，不是 HEALTHCHECK
- 业务逻辑健康检查（如数据库连接池状态）——本模式仅覆盖进程+端口层活性检测

## 问题本质

健康检查有一个常见的设计误区：**"越全面越好"**——试图在一个探针里验证完整功能可用性，这会带来三重副作用：

1. **协议噪音**：对非 HTTP 服务（SSH、数据库、Redis）发送 HTTP 请求会触发服务端协议解析错误，产生大量无意义告警日志
2. **脆弱性**：依赖应用层响应体格式做断言，第三方库版本升级后响应格式变化导致健康检查误报失败
3. **性能开销**：完整的应用层握手（如 SSH 密钥交换、TLS 握手）增加延迟和资源消耗，30 秒间隔的健康检查积累起来不可忽视

**核心反常识**：HEALTHCHECK 的目标是"进程活着且端口可连接"（liveness），不是"功能完全可用"（readiness 可由上层编排处理）。最小探针只检测到 TCP 连接能建立为止，不发送任何应用层数据。

## 标准方案：按协议分级的最小探针

### 探针设计分级原则

```
探针层级     检测内容              适用服务             实现方式
─────────────────────────────────────────────────────────────────
L0 进程存在  进程是否在运行        所有服务             pgrep/ps 检查 PID
L1 TCP 端口  端口是否可连接        SSH/数据库/Redis     exec 3<>/dev/tcp/host/port（不发数据）
L2 HTTP 极简  HTTP 状态码          Web/Jupyter/API      curl -s -o /dev/null -w "%{http_code}"
L3 响应体验证  响应体包含关键字      特殊场景（慎用）      curl + grep（不推荐作为默认HEALTHCHECK）
```

**默认建议**：所有服务做到 L1（TCP），HTTP 服务可做到 L2（状态码），**不要默认做到 L3**。

### 标准 healthcheck.sh 实现

```bash
#!/bin/bash
#
# 容器健康检查：最小探针设计
# - SSH/非HTTP服务：TCP空探针（不发送数据）
# - HTTP服务：curl -o /dev/null 只检查状态码（不解析响应体）
# - 任意一项失败则返回1（unhealthy）

SSH_PORT="${SSH_PORT:-22}"
JUPYTER_PORT="${JUPYTER_PORT:-8888}"
FAIL=0

# ── L1: SSH 服务检测（exec TCP 空探针，不发送数据）──
if ! pgrep -x sshd >/dev/null 2>&1; then
    echo "[HEALTHCHECK] sshd process not running"
    FAIL=1
else
    # 使用 exec 3<>/dev/tcp 建立 TCP 连接后立即关闭，不发送任何数据
    # 避免 echo >/dev/tcp/... 发送换行触发 SSH banner exchange 协议解析
    if timeout 2 bash -c "exec 3<>/dev/tcp/127.0.0.1/${SSH_PORT} && exec 3>&-"; then
        echo "[HEALTHCHECK] sshd port ${SSH_PORT}: OK"
    else
        echo "[HEALTHCHECK] sshd port ${SSH_PORT}: FAILED"
        FAIL=1
    fi
fi

# ── L2: Jupyter HTTP 检测（curl 极简模式，-o /dev/null 丢弃响应体）──
if pgrep -f "jupyter" >/dev/null 2>&1; then
    # 接受 200/302/401/403 作为"服务正常"：
    # - 200: 正常响应
    # - 302: 重定向到登录页
    # - 401/403: 需要认证（说明服务在运行）
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        "http://127.0.0.1:${JUPYTER_PORT}/api" 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] || \
       [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
        echo "[HEALTHCHECK] jupyter port ${JUPYTER_PORT}: OK (HTTP ${HTTP_CODE})"
    else
        echo "[HEALTHCHECK] jupyter port ${JUPYTER_PORT}: FAILED (HTTP ${HTTP_CODE})"
        FAIL=1
    fi
else
    echo "[HEALTHCHECK] jupyter process not running"
    FAIL=1
fi

if [ "$FAIL" -eq 1 ]; then
    echo "[HEALTHCHECK] STATUS: UNHEALTHY"
    exit 1
fi
echo "[HEALTHCHECK] STATUS: HEALTHY"
exit 0
```

### 配套：日志降噪三重措施

光有最小探针不够，还需要从服务端配置层面减少噪音日志：

1. **SSH 服务：降低 LogLevel**
   ```ini
   # /etc/ssh/sshd_config
   LogLevel ERROR  # 默认 INFO 会记录所有连接探测，改为 ERROR 只记真正错误
   ```

2. **Jupyter/第三方服务：stderr 分流到独立日志文件**
   ```ini
   # /etc/supervisor/conf.d/jupyter.conf
   [program:jupyter]
   stdout_logfile=/dev/stdout        # stdout（正常访问日志）直连容器日志
   stdout_logfile_maxbytes=0
   stderr_logfile=/var/log/supervisor/jupyter-stderr.log  # stderr 重定向到文件
   stderr_logfile_maxbytes=1048576  # 1MB 轮转，避免磁盘占满
   redirect_stderr=false
   ```
   为什么这样做？第三方库版本兼容的警告（如 httpx 版本不匹配的 TypeError）属于 stderr，但不影响服务可用性，不应该污染容器 stdout 日志流。

3. **Dockerfile 中不声明敏感变量默认值**
   ```dockerfile
   # ❌ 错误：ENV 空声明触发 BuildKit SecretsUsedInArgOrEnv 警告
   # ENV JUPYTER_TOKEN=
   # ENV USER_PASSWORD=

   # ✅ 正确：只在 entrypoint 中处理，Dockerfile 不写空 ENV
   ENV JUPYTER_PORT=8888  # 非敏感默认值可以声明
   ```

## 反模式（至少 3 个，来自实际踩坑）

### ❌ 反模式 1：对 SSH 端口使用 echo >/dev/tcp 做探针

```bash
# 错误：echo 发送换行符到 SSH 端口，触发 SSH 协议 banner exchange
(echo > /dev/tcp/127.0.0.1/22) 2>/dev/null
```

后果：sshd 日志每秒都打印 `banner exchange: Connection from 127.0.0.1: Connection closed by remote host`，日志被刷爆，真正的攻击/错误日志被淹没。正确做法是 `exec 3<>/dev/tcp/... && exec 3>&-`，建立连接后立即关闭，不发送任何字节。

### ❌ 反模式 2：HTTP 探针解析并验证响应体内容

```bash
# 错误：依赖响应体包含特定字符串，第三方库升级后格式变化导致误报
curl -s http://localhost:8888/api | grep -q '"version"'
```

后果：jupyter_server 版本升级后 API 响应格式变化，健康检查开始失败，但服务实际上完全正常。正确做法是只检查 HTTP 状态码，接受 2xx/3xx/401/403 为正常。

### ❌ 反模式 3：健康检查里做完整业务逻辑验证

```bash
# 错误：在 HEALTHCHECK 中登录、查询数据库、执行业务操作
curl -s -X POST http://localhost/api/login -d '{"user":"health","pass":"check"}' | grep -q '"success"'
```

后果：①健康检查耗时过长容易 timeout；②写操作可能产生脏数据；③依赖的依赖（数据库、缓存）故障时主服务被误判为不健康；④健康检查本身变成攻击面。正确做法：业务深度验证交给独立的监控系统或集成测试，HEALTHCHECK 只做活性检测。

### ❌ 反模式 4：所有服务日志都输出到 stdout/stderr

```ini
# 错误：stderr 直连容器日志，第三方警告污染日志流
[program:jupyter]
stderr_logfile=/dev/stderr
redirect_stderr=true
```

后果：已知的第三方兼容性警告（如 `AsyncClient.__init__() got an unexpected keyword argument 'proxies'`）每 30 秒刷一次，真正的错误被淹没。正确做法：stdout 输出到容器日志，stderr 分流到轮转日志文件。

## 检验标准

健康检查方案完成后，验证以下项：

- [ ] 连续运行 1 小时，容器日志中无健康检查导致的噪音告警（banner exchange 等）
- [ ] 手动 kill 服务进程后，3 次健康检查内（~90秒）状态变为 unhealthy
- [ ] 服务重启后，1 次健康检查内恢复 healthy
- [ ] 健康检查脚本执行时间 < 3 秒（timeout 2秒防卡死）
- [ ] 不依赖响应体特定格式，只检查状态码/端口连通性
- [ ] sshd_config 的 LogLevel 设置为 ERROR 或更高
- [ ] supervisord 中第三方服务的 stderr 已分流到日志文件
- [ ] Dockerfile 中无敏感变量名的空 ENV 声明

## 迁移示例（跨领域）

不仅适用于 Jupyter+SSH 双服务容器，任何多服务容器都适用：

**Nginx + uWSGI 容器**：
```bash
# Nginx 端口 80：HTTP 状态码探针
# uWSGI 端口 8000：TCP 空探针（不发 HTTP）
if timeout 2 bash -c "exec 3<>/dev/tcp/127.0.0.1/8000 && exec 3>&-"; then OK; fi
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/healthz)
```

**PostgreSQL + 应用容器**：
```bash
# PostgreSQL 5432：TCP 空探针（不发 PostgreSQL 启动报文）
if timeout 2 bash -c "exec 3<>/dev/tcp/127.0.0.1/5432 && exec 3>&-"; then OK; fi
# 不要用 psql -c 'SELECT 1' 作为 HEALTHCHECK——那是 readiness 探针不是 liveness
```

**Redis 容器**：
```bash
# Redis 6379：TCP 空探针即可
# 不要用 redis-cli PING 作为默认 HEALTHCHECK
```

## 边界条件与常见疑问（来自对抗审查）

**Q: 最小探针是不是太弱了？服务进程存在但死锁怎么办？**

TCP端口能连接只能说明进程在accept，不能说明服务能正常处理请求。但需要严格区分职责边界：
- **liveness（活性）**：进程是否在运行，端口是否能连接 → 这是 Docker HEALTHCHECK 的职责
- **readiness（就绪）**：服务是否能正常处理请求 → 这是 k8s readinessProbe、负载均衡健康检查或独立监控系统的职责

进程死锁属于 readiness 问题，不是 liveness 问题。本项目中 supervisord 本身有 `autorestart=true` 机制，进程崩溃退出会自动重启。HEALTHCHECK 只负责覆盖 supervisord 管不到的情况（如OOM kill导致整个容器僵死）。两者职责清晰，不应混在一起。如果确实需要死锁检测，应在独立监控系统中实现，不应塞进 Docker HEALTHCHECK。

**不适用场景**（已在触发场景中列出）：
- 需要深度功能验证（登录后执行业务操作）的端到端探针 → 独立集成测试
- 业务逻辑健康检查（数据库连接池状态等） → 上层监控系统
- 需要完整业务链路验证的场景 → k8s readinessProbe + livenessProbe 分层设计

## 成熟度

L1-draft — jupyter-ssh-base 项目中验证可行（healthcheck.sh 重写后，banner exchange 告警从每秒一条降为零，AsyncClient 警告不再出现在 stdout），但尚未在第二个不同类型项目中验证。V阶段对抗审查（怀疑者/实践者/运维/SRE/维护者五视角）全部通过。

## 交叉引用

- 来源：jupyter-ssh-base 项目七概念方法论复盘（2026-08-07）+ v1.1 告警优化
- 关联模式：
  - docker-buildtime-vs-runtime-config.md（HEALTHCHECK 是运行时机制，相关脚本在 ENTRYPOINT/COPY 层安装）
  - dockerfile-runtime-logical-layering.md（healthcheck.sh 在 Stage 2.5 COPY 并做 bash -n 验证）
  - dual-channel-tiered-logging.md（双通道日志：stdout 关键日志、文件日志噪音日志）
- 参考实现：
  - [scripts/healthcheck.sh](../../../../../apps/docker-images/jupyter-ssh-base/scripts/healthcheck.sh)
  - [config/sshd_config](file:///d:/spaces/SpecWeave/apps/docker-images/jupyter-ssh-base/config/sshd_config)（LogLevel=ERROR）
  - [config/supervisor/conf.d/jupyter.conf](../../../../../apps/docker-images/jupyter-ssh-base/config/supervisor/conf.d/jupyter.conf)（stderr 分流）
