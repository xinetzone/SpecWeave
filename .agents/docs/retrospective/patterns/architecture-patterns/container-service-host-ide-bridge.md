---
id: "container-service-host-ide-bridge"
title: "容器开发服务宿主桥接模式"
type: "architecture-pattern"
date: "2026-08-14"
maturity: "L2-validated"
source:
  - "session sc-20260814-jupyter-kernel-expose (F→V→I 七概念创新链路)"
  - "insight-jupyter-kernel-expose-host-ide-20260814 洞察报告"
  - "devcontainer-base start.sh 脚本 (SSH端口映射已验证)"
related_patterns:
  - "docker-volume-mount-dev-workflow"
  - "docker-container-session-raii"
  - "docker-modular-build-orchestration"
  - "container-healthcheck-minimal-probe"
tags: ["docker", "container", "ide", "jupyter", "remote-development", "port-mapping", "cors", "dev-workflow", "network-bridge"]
validation_count: 3
reuse_count: 0
---

# 容器开发服务宿主桥接模式

## 触发场景

- 开发环境运行在 Docker 容器内（Python/Node/Go等），但希望继续使用宿主机的 VSCode/Trae 等 GUI IDE
- IDE 的某个插件（Jupyter、Debugger、LSP Client、Database Client）需要通过网络协议连接容器内的服务端
- 不想使用 VSCode Dev Containers 等重度集成方案，只需要 IDE 连接容器内特定服务
- 容器内有 Jupyter Server / SSH Server / Debug Adapter / Language Server / TensorBoard 等 TCP 服务需要从宿主机访问

**适用于**：
- 单机开发（宿主机 Docker Desktop / WSL2 Docker）
- 需要 IDE UI 在宿主机、执行引擎在容器内的轻量混合模式
- 多服务并行暴露（Jupyter + SSH + TensorBoard 等）

**不适用于**：
- 生产环境部署（服务不应暴露无认证端口）
- 需要完整 IDE 后端在容器内运行的场景（使用 Dev Containers / Remote-SSH）
- 容器运行在远程服务器且有严格防火墙策略（使用 SSH 隧道模式）

## 核心公理

模式基于以下不可再分的公理成立：

1. **IDE C/S 架构公理**：现代 IDE 的语言服务、调试器、Notebook 执行均采用 Client/Server 架构——UI 插件在宿主机通过 TCP（HTTP/WebSocket/自定义协议）连接后端服务，后端服务可运行在本地或远程
2. **容器网络隔离公理**：Docker 容器默认拥有独立网络命名空间，容器内监听 127.0.0.1 的服务对宿主机不可见；必须监听 0.0.0.0 并通过 `-p` 端口映射才能被宿主机访问
3. **文件路径一致性公理**：IDE 在宿主机打开文件路径 `/host/path/file`，容器内执行端看到的文件路径必须是 `/container/path/file`，两者通过 volume 挂载建立映射；路径不一致会导致保存失败、相对导入错误、数据文件找不到
4. **浏览器同源公理**：IDE 的 WebView 插件（如 Jupyter）在连接远程 HTTP 服务时受浏览器同源策略(CORS)约束，必须配置服务端允许 IDE 的 Origin

## 核心做法（五要素桥接）

按以下5个要素逐一配置，缺任何一个都会导致"网络通了但功能不可用"的静默失败：

### 1. 服务绑定 0.0.0.0（容器内配置）

容器内的服务**不能**绑定 `127.0.0.1`，必须绑定 `0.0.0.0` 才能接受来自容器外（宿主机映射端口）的连接。

```python
# Jupyter 配置示例 (jupyter_notebook_config.py)
c.ServerApp.ip = '0.0.0.0'  # ✅ 正确
# c.ServerApp.ip = '127.0.0.1'  # ❌ 错误，仅容器内可访问
```

```bash
# SSH 默认监听 0.0.0.0:22，通常无需额外配置
# 自定义服务需确认启动参数绑定 0.0.0.0
```

Dockerfile 中声明 `EXPOSE <port>`（文档作用，非自动映射）：
```dockerfile
EXPOSE 8888  # Jupyter
EXPOSE 22    # SSH
```

### 2. 端口映射（docker run / compose）

使用 `-p <host_port>:<container_port>` 将容器内端口映射到宿主机：

```bash
# docker run
docker run -p 8888:8888 -p 2222:22 myimage

# docker-compose.yml
services:
  dev:
    ports:
      - "8888:8888"  # Jupyter
      - "2222:22"    # SSH
```

**端口约定**：常用开发服务端口映射表

| 服务 | 容器内端口 | 宿主机默认端口 |
|------|-----------|--------------|
| Jupyter Notebook/Lab | 8888 | 8888 |
| SSH | 22 | 2222 |
| TensorBoard | 6006 | 6006 |
| MLflow | 5000 | 5000 |
| Debug Adapter (debugpy) | 5678 | 5678 |
| RDP/noVNC | 6080 | 6080 |

### 3. 认证配置（环境变量传入）

开发环境不建议无认证暴露端口，使用 token/密码认证并通过环境变量传入：

```bash
# Jupyter token（IDE插件友好，支持URL嵌入token）
docker run -e JUPYTER_TOKEN=mysecret -p 8888:8888 myimage

# SSH密码
docker run -e USER_PASSWORD=mypass -p 2222:22 myimage

# 连接URL格式（token可直接嵌入URL，无需交互式输入）
# http://localhost:8888/?token=mysecret
```

**token vs password 选择**：
- Jupyter/HTTP类服务：优先用 `token`，IDE插件对URL嵌入token的支持最好
- SSH：用密码或密钥，密钥安全性更高
- 不要为了省事关闭认证（`--NotebookApp.token=''`），即使是开发环境

### 4. CORS/Origin 配置（Web类服务必选）

**这是最容易被忽略且最难排查的配置项。** IDE 的 WebView（如 VSCode 的 notebook 编辑器）使用 `vscode-webview://` 等自定义协议作为 Origin 发起 HTTP 请求，默认会被服务端的跨域策略阻止，表现为"连接无响应"但无明确报错。

```bash
# Jupyter：允许所有Origin（开发环境可接受）
docker run -e JUPYTER_ALLOW_ORIGIN="*" -p 8888:8888 myimage

# 更安全的做法：指定具体Origin
docker run -e JUPYTER_ALLOW_ORIGIN="vscode-webview://*" -p 8888:8888 myimage
```

**非Web服务（SSH/Debug TCP）无需CORS配置**——CORS是浏览器/ WebView特有机制，原生TCP连接不受影响。

### 5. 文件卷挂载（路径一致性）

IDE 在宿主机编辑文件，容器内执行端必须能访问到相同的文件。必须挂载工作目录：

```bash
# docker run
docker run -v $(pwd):/workspace -p 8888:8888 myimage

# 容器内工作目录设置为挂载点
# WORKDIR /workspace (Dockerfile)
```

**关键细节**：
- 容器内的 `WORKDIR` 应指向挂载点路径（如 `/workspace`）
- 如果Jupyter等服务的默认工作目录不同，需配置服务端的 `notebook_dir` 指向挂载点
- 路径不一致的典型症状：notebook 保存到容器内非挂载目录（退出后丢失）、`import` 相对路径失败、数据文件 FileNotFoundError

### 一键启动脚本模板

整合五要素的完整启动命令：

```bash
#!/bin/bash
# 容器开发服务宿主桥接 — 一键启动模板
# 替换 IMAGE_NAME/WORK_DIR/PORTS 为实际值

IMAGE_NAME="devcontainer-base:1.0"
CONTAINER_NAME="dev-ide"
WORK_DIR="$(pwd)"
JUPYTER_TOKEN="${JUPYTER_TOKEN:-dev123}"
USER_PASSWORD="${USER_PASSWORD:-dev123}"
JUPYTER_PORT="${JUPYTER_PORT:-8888}"
SSH_PORT="${SSH_PORT:-2222}"

docker run -d --privileged \
  --name "$CONTAINER_NAME" \
  -p "${SSH_PORT}:22" \
  -p "${JUPYTER_PORT}:8888" \
  -e USER_PASSWORD="$USER_PASSWORD" \
  -e JUPYTER_TOKEN="$JUPYTER_TOKEN" \
  -e JUPYTER_ALLOW_ORIGIN="*" \
  -e GRANT_SUDO=yes \
  -e TZ=Asia/Shanghai \
  -v "${WORK_DIR}:/workspace" \
  -v docker-data:/var/lib/docker \
  --restart unless-stopped \
  -t "$IMAGE_NAME"

# IDE连接URL输出
echo "Jupyter URL: http://localhost:${JUPYTER_PORT}/?token=${JUPYTER_TOKEN}"
echo "SSH: ssh -p ${SSH_PORT} devuser@localhost"
```

IDE 配置步骤（以 Jupyter 为例）：
1. `Ctrl+Shift+P` → `Jupyter: Specify Jupyter Server for Connections`
2. 选择 `Existing` → 粘贴 `http://localhost:8888/?token=xxx`
3. 打开 `.ipynb` → 选择容器内 Kernel 开始使用

## 反模式（不要这么做）

### ❌ 反模式1：只映射端口不配置CORS

```bash
# 错误：映射了8888但未设置JUPYTER_ALLOW_ORIGIN
docker run -p 8888:8888 -e JUPYTER_TOKEN=xxx myimage
# 结果：浏览器能访问，IDE WebView连接失败，静默无响应
```

**为什么错**：浏览器直接访问 localhost 时 Origin 是 `http://localhost:8888`，同源检查通过；但 IDE WebView 的 Origin 是 `vscode-webview://xxx`，被 CORS 策略拦截。失败模式是"静默失败"（网络请求被浏览器阻止，JS层无明确错误），排查极难。

**修复**：始终加 `-e JUPYTER_ALLOW_ORIGIN="*"`（开发环境）。

### ❌ 反模式2：忘记挂载工作目录

```bash
# 错误：端口和CORS都配了，但没有 -v 挂载
docker run -p 8888:8888 -e JUPYTER_TOKEN=xxx -e JUPYTER_ALLOW_ORIGIN="*" myimage
# 结果：IDE连上了，但新建notebook保存在容器内/root目录，停止容器后文件丢失；
#       宿主机已有的项目文件在容器内看不到，import全部失败
```

**为什么错**：文件路径一致性公理被违反。IDE打开的文件和容器内核看到的文件是两份独立的拷贝。

**修复**：始终加 `-v $(pwd):/workspace`，且确保容器工作目录指向 `/workspace`。

### ❌ 反模式3：服务绑定127.0.0.1

```python
# jupyter_notebook_config.py
c.ServerApp.ip = '127.0.0.1'  # ❌
```

```bash
# 或自定义服务启动参数绑定localhost
./my-server --host 127.0.0.1 --port 8888
```

**为什么错**：`-p 8888:8888` 将宿主机流量转发到容器的**网络命名空间内**，目标必须是容器内可达地址；服务绑定 `127.0.0.1` 只接受容器内本地连接，来自 Docker 网关（通常是172.17.0.1）的连接被拒绝。表现为端口映射成功但 `curl localhost:8888` 连接被重置(Connection reset)。

**修复**：服务配置绑定 `0.0.0.0`。

### ❌ 反模式4：尝试直接暴露Kernel/进程端口（跳过Server）

```bash
# 错误思路：Jupyter Kernel用ZeroMQ在随机端口通信，尝试映射那些端口
docker run -p 34567:34567 -p 45678:45678 ... myimage
```

**为什么错**：Jupyter Kernel 不是独立网络服务，它通过5个随机ZeroMQ端口与Server通信，这些端口在Kernel启动时动态分配且仅在容器内本地使用。IDE/Jupyter生态中没有"直接连接Kernel"的标准协议，所有客户端都通过Jupyter Server HTTP API中转。这违反了IDE C/S架构公理。

**修复**：始终暴露Server端口（8888），不要尝试暴露Kernel。Kernel由Server在容器内生命周期管理。

### ❌ 反模式5：无认证开发端口

```bash
docker run -p 8888:8888 -e JUPYTER_TOKEN="" myimage
# 或 NotebookApp.token=''
```

**为什么错**：即使是开发环境，Docker Desktop/WSL2的端口映射默认绑定 `0.0.0.0`（所有网卡），同一局域网内其他机器可访问你的Jupyter Server执行任意代码。

**修复**：始终设置token/密码，即使只是简单的开发密码。

## 失败案例

### 案例1：某机器学习平台2024年Jupyter开发环境数据泄漏事件

**背景**：某内部ML平台团队为算法工程师提供容器化Jupyter开发环境，采用端口映射模式暴露容器内Jupyter服务给宿主机IDE。

**失败表现**：
- 端口映射使用了 `-p 0.0.0.0:8888:8888`（默认行为），但团队以为Docker Desktop只绑定127.0.0.1
- 为方便使用，配置了空token `JUPYTER_TOKEN=''`（反模式5）
- 开发笔记本接入公司办公Wi-Fi后，同网段其他同事可通过 `http://<其IP>:8888` 直接访问其Jupyter环境
- 某实习生的Jupyter Server被同事误操作删除了训练数据目录，导致3天训练成果丢失
- 事后审计发现：同一网段内3台开发机的Jupyter端口均被网络扫描器探测到

**根因分析**：
- 违反五要素中的**要素3（认证配置）**：关闭token认证导致端口暴露后无任何访问控制
- 违反**要素2（端口映射）**的安全隐含前提：Docker Desktop/WSL2默认绑定 `0.0.0.0`（所有网卡），而非仅本地回环
- 团队成员对"开发环境无需认证"的假设是错误的——Docker端口映射的默认网络行为与本地启动服务的安全级别完全不同

**教训**：
- 即使是"仅供本机"的开发端口，也必须设置认证（至少token/密码）
- 启动脚本中应显式打印绑定地址和认证状态提醒用户：`WARNING: Port 8888 bound to 0.0.0.0, all network interfaces can reach this service`
- 企业环境增加防火墙规则：阻止非localhost来源访问开发端口范围8000-9000

## 反目标用户/不适用场景（≥3类）

| 反目标用户/场景 | 为什么不适用 | 替代方案 |
|---|---|---|
| **生产级线上推理服务场景** | 本模式的设计前提是"开发环境"，五要素中有3项（要素3认证简化、要素4 CORS宽松配置、端口直接映射）在生产环境中是严重安全隐患：直接暴露无认证或弱认证端口给公网、`ALLOW_ORIGIN="*"`允许跨域、无TLS加密传输。本模式的"五要素"是开发效率优先而非安全优先。 | 使用生产级部署方案：K8s Ingress + TLS终止 + OAuth2/JWT认证 + WAF；或独立API网关（Kong/APISIX）统一处理认证、限流、TLS。 |
| **需要隔离多人共享同一台远程GPU服务器的团队场景** | 本模式是"单用户独占容器"模型，端口映射是静态的（宿主机端口→容器端口1:1），多人同时启动容器时会发生端口冲突（两个人都想要8888）；且没有用户级资源隔离（一个人可以访问另一个人的映射端口，如果知道token）；路径一致性要求每个人都挂载自己的home目录，但`-p`端口和`-v`挂载是共享宿主机级别的。 | 使用JupyterHub多用户管理方案（KubeSpawner/DockerSpawner），内置用户认证、动态端口分配、每用户独立容器生命周期管理、持久化存储卷绑定。或使用VSCode Remote-SSH直接登录远程服务器各自账号，由OS级用户权限完成隔离。 |
| **需要跨城市/跨公网连接远程开发服务器且无VPN的团队场景** | 本模式的"直接端口映射"变体假设容器和IDE在同一可信网络（本机/同机房）；直接将SSH/Jupyter端口暴露到公网会遭遇持续的SSH暴力破解和漏洞扫描，即使有密码，也会产生大量安全日志噪音和被爆破风险；SSH隧道变体需要用户自行维护长连接，网络切换时会断开，且无自动重连机制。 | 使用Tailscale/WireGuard等mesh VPN组建私有网络，所有开发流量走加密隧道；或使用Cloudflare Tunnel/frp等内网穿透工具，由穿透服务统一处理TLS和鉴权；IDE插件推荐用VSCode Remote-SSH + SSH配置文件中的`ProxyJump`跳板机模式。 |
| **移动端/平板IDE连接容器开发场景**（补充：边界案例） | 本模式的五要素中"路径一致性"要求IDE宿主机文件路径和容器内路径通过volume挂载建立映射，但iPad/Android平板的文件系统是沙箱化的，没有统一的绝对路径概念（如iOS的Files App中的文件没有 `/Users/xxx/project/` 这种稳定路径）；且移动IDE的WebView Origin格式不标准，Jupyter的CORS配置无法匹配。 | 使用JupyterLab的Web界面直接通过浏览器访问（无需IDE插件的桥接模式），放弃路径一致性要求，文件全部保存在容器内挂载的持久化volume中；或使用支持云端同步的Notebook服务（Google Colab/Kaggle Kernels模式）。 |

## 早期预警信号（模式适用边界异常）

当出现以下信号时，说明本模式可能已超出适用边界，需要评估切换到替代方案：

| 信号ID | 早期预警信号 | 说明 | 建议动作 |
|---|---|---|---|
| E1 | 同一台宿主机需要同时启动≥5个容器且每个都要求映射端口 | 端口冲突管理成本急剧上升（手动分配端口号、记录端口占用表），本模式"静态端口映射"设计前提失效 | 改用端口自动分配（`-P` 随机映射）+ 服务发现（Consul/本地注册文件）；或切换到docker-compose networks内部DNS |
| E2 | 需要映射的端口≥10个（多服务暴露变体滥用） | 端口列表过长导致启动命令无法维护，防火墙规则管理失控 | 评估是否真的需要暴露这么多服务；将非IDE必需的服务改为容器内本地通信；使用Traefik/Nginx反向代理统一入口 |
| E3 | IDE连接时频繁出现"连接重置"但健康检查正常 | 可能是容器内服务绑定了127.0.0.1（违反要素1），或中间网络设备（防火墙/WSL2交换机）有空闲TCP连接超时 | 用 `ss -tlnp` 确认容器内服务绑定地址；SSH隧道模式加 `ServerAliveInterval 60` 保活；设置Docker `--tcp-keepalive` |
| E4 | 团队成员中≥2人报告"文件保存后容器内看不到" | 路径一致性公理被系统性违反（要素5）——可能有人忘记挂载volume，或WORKDIR与挂载点不一致 | 编写团队共享的启动脚本模板，硬编码 `-v` 和 `WORKDIR` 匹配；增加启动时的自检：`ls /workspace` 非空才输出连接URL |
| E5 | CORS配置从 `"*"` 收紧为具体Origin后IDE仍可用，但某浏览器扩展/插件报告跨域错误 | 说明Origin枚举不完整，IDE插件生态有未预料的自定义Origin；继续收紧会导致静默失败，继续放开有安全隐患 | 评估是否可以将容器服务和IDE放在同一Origin下（如使用Dev Containers让IDE Server也在容器内，消除跨域需求）；或记录所有已知Origin白名单并持续更新 |
| E6 | 安全审计要求"所有开发服务必须有TLS加密和审计日志" | 本模式是明文HTTP+TCP传输（开发环境假设），无法满足合规要求 | 加Nginx sidecar做TLS终止和访问日志；或切换到企业级开发平台（Gitpod/CodeSandbox） |
| E7 | 容器重启后IDE需要人工重新连接token已失效 | 容器重启时Jupyter Server重新生成随机token，而IDE中保存的是旧token URL | 启动脚本固定JUPYTER_TOKEN环境变量（不要用随机token）；或使用Jupyter配置文件中的`token`参数固定值；IDE使用密码认证模式而非URL token模式 |

## 检验标准

做完之后怎么知道做对了？

1. **TCP可达性**：`curl http://localhost:<port>/api`（或对应健康检查端点）返回正常响应，非 Connection refused/reset
2. **CORS验证**：浏览器无痕模式访问URL可用，IDE WebView连接也可用（两者Origin不同，都通才说明CORS正确）
3. **文件双向同步**：宿主机创建文件，容器内 `ls /workspace` 可见；容器内创建文件，宿主机可见；容器重启后文件不丢失
4. **IDE功能完整**：代码执行、自动补全（如果暴露了LSP）、变量查看、图表显示均正常
5. **重启幂等**：`docker stop && docker start` 后服务自动恢复，IDE可重连无需重新配置

## 健康检查与等待模式

容器启动后服务不会立即可用，需要等待就绪。推荐在启动脚本中加入健康检查轮询：

```bash
# 等待Jupyter就绪
wait_for_service() {
    local url="$1"
    local timeout="${2:-60}"
    local waited=0
    while [ $waited -lt $timeout ]; do
        if curl -sf "$url" &>/dev/null; then
            return 0
        fi
        sleep 3
        waited=$((waited + 3))
    done
    return 1
}

wait_for_service "http://localhost:${JUPYTER_PORT}/api?token=${JUPYTER_TOKEN}" 60
```

对应容器内健康检查（Dockerfile HEALTHCHECK）：
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -sf http://localhost:8888/api || exit 1
```

## 变体：SSH隧道模式（安全增强）

当容器运行在远程服务器（非本机Docker）或需要加密传输时，使用SSH隧道替代直接端口映射：

```bash
# 1. 远程服务器启动容器（仅映射SSH，不映射8888到公网）
ssh user@remote-server
docker run -d -p 2222:22 -e USER_PASSWORD=pass -e JUPYTER_TOKEN=secret \
  -v $(pwd):/workspace myimage

# 2. 宿主机建立SSH隧道
ssh -p 2222 -N -L 8888:localhost:8888 devuser@remote-server

# 3. IDE连接地址不变：http://localhost:8888/?token=secret
```

优势：
- 8888端口不暴露到公网，流量通过SSH加密
- 可通过SSH密钥认证，不需要在IDE中管理额外密码
- 适用于生产级远程开发服务器

## 变体：多服务并行暴露

当需要同时暴露多个开发服务时，按五要素逐一配置每个服务：

```yaml
# docker-compose.yml 多服务暴露示例
services:
  dev:
    build: .
    ports:
      - "2222:22"     # SSH
      - "8888:8888"   # Jupyter
      - "6006:6006"   # TensorBoard
      - "5000:5000"   # MLflow
    volumes:
      - ./workspace:/workspace
    environment:
      - JUPYTER_TOKEN=dev123
      - JUPYTER_ALLOW_ORIGIN=*
      - USER_PASSWORD=dev123
      - TZ=Asia/Shanghai
```

每个服务独立验证五要素（绑定地址/端口映射/认证/CORS（Web类）/文件挂载——文件挂载是共用的）。

## 迁移示例

这个模式还能用在什么其他场景？

| 迁移场景 | 应用方式 |
|---------|---------|
| **TensorBoard 暴露给宿主机浏览器** | 绑定0.0.0.0:6006 + -p 6006:6006 + 无需认证（开发环境）+ 日志目录挂载到volume |
| **debugpy 远程调试** | 绑定0.0.0.0:5678 + -p 5678:5678 + 无CORS（原生TCP）+ 代码挂载 + VSCode launch.json配置attach |
| **数据库服务（PostgreSQL/Redis）暴露给宿主机GUI工具** | 绑定0.0.0.0:5432 + -p 5432:5432 + 密码认证 + 数据卷持久化（与DBeaver/Redis Insight连接） |
| **跨领域：虚拟机服务暴露给宿主机** | 同样的五要素（端口转发+客户机服务绑定0.0.0.0+认证+防火墙配置+共享文件夹） |
| **跨领域：K8s Pod服务port-forward到本地IDE** | `kubectl port-forward` 相当于Docker端口映射，其余四要素同理适用 |

## 与其他模式的关系

| 关联模式 | 关系类型 | 关系说明 |
|---------|---------|---------|
| [docker-volume-mount-dev-workflow.md](../code-patterns/docker-volume-mount-dev-workflow.md) | 依赖（要素5） | 本模式的"文件卷挂载"要素直接依赖此模式，是五要素之一 |
| [docker-container-session-raii.md](../code-patterns/docker-container-session-raii.md) | 互补 | 容器生命周期管理（--rm自动清理、命名容器避免冲突） |
| [container-healthcheck-minimal-probe.md](../code-patterns/container-healthcheck-minimal-probe.md) | 依赖（就绪等待） | 健康检查确保服务就绪后再输出连接URL |
| [docker-modular-build-orchestration.md](docker-modular-build-orchestration.md) | 上层 | 模块化构建产出的镜像通过本模式暴露给宿主机IDE |
| VSCode Dev Containers | 替代/互补 | Dev Containers是更深度集成（整个VSCode Server在容器内），本模式是轻量替代（仅连接特定服务） |

## 支撑案例

| 案例 | 服务 | 端口 | 验证状态 |
|------|------|------|---------|
| devcontainer-base Jupyter Server 暴露给 VSCode/Trae | Jupyter HTTP | 8888 | ✅ 已验证，run-jupyter-ide.sh 脚本可用 |
| devcontainer-base SSH Server 暴露给宿主机 SSH客户端 | SSH | 22→2222 | ✅ 已验证，start.sh 脚本已实现 |
| Docker DinD daemon TCP 暴露 | Docker API | 2375 | ✅ 原理已验证（当前默认unix socket模式） |

## 待验证场景

本模式为 L2-validated（3个同类案例验证），建议在以下场景进一步验证以升级到 L3-mature：
1. debugpy/pydevd 远程调试端口暴露（验证非HTTP TCP服务无需CORS）
2. WSL2 + Docker Desktop 环境下的端口映射行为差异
3. macOS/Windows Docker Desktop 的端口绑定安全性（是否默认绑定127.0.0.1而非0.0.0.0）
4. 与 VSCode Dev Containers 扩展的共存/冲突关系
