---
id: "docker-buildtime-vs-runtime-config"
title: "多阶段Dockerfile构建时与运行时配置分离原则"
type: code-pattern
date: 2026-07-27
maturity: L2-validated
maturity_note: "本次caffe-cpu:jupyter的SSH密钥案例验证；结合Docker官方最佳实践提炼"
source:
  - "../../reports/build-engineering/retrospective-caffe-jupyter-docker-build-export-20260727/README.md#模式-p3多阶段dockerfile的运行时配置vs构建时配置分离原则"
related_patterns:
  - "docker-image-offline-export-distribution.md"
  - "compiled-wheel-runtime-image-build.md"
  - "dockerfile-python-code-safe-embedding.md"
  - "../architecture-patterns/docker-modular-build-orchestration.md"
  - "../methodology-patterns/governance-strategy/dev-env-dockerfile-optimization.md"
tags: ["docker", "dockerfile", "multi-stage-build", "entrypoint", "runtime-config", "buildtime-config", "ssh-keys", "container-lifecycle", "security-best-practice"]
validation_count: 1
reuse_count: 0
---

# 多阶段Dockerfile构建时与运行时配置分离原则

## 触发场景

- 设计或审查多阶段Dockerfile
- 遇到"构建时正常、运行时报错"或"直接docker run command验证失败但完整启动正常"的问题
- 配置SSH密钥、数据库密码、TLS证书等敏感或实例唯一数据
- Dockerfile中的RUN指令和ENTRYPOINT/CMD职责划分不清
- 验证容器服务时，绕过entrypoint执行命令得到意外结果

**识别信号**：
- "Dockerfile里RUN ssh-keygen -A了，为什么sshd还说no hostkeys available？"
- "docker run --rm img cmd能工作，但docker run -d img启动服务失败"（或反过来）
- 镜像在本机构建后验证正常，放到另一台机器启动就出错
- 所有容器实例共享了相同的密钥/密码/会话ID
- CMD被docker run的命令参数覆盖后初始化逻辑丢失

**不适用场景**：
- 单阶段Dockerfile、FROM scratch的极简镜像
- 无状态纯计算镜像（无服务、无持久化配置）
- 构建产物就是最终运行时不需要任何初始化（如静态二进制+scratch）

## 问题背景

### 容器生命周期的三个阶段

理解Dockerfile指令在容器生命周期中的执行时机是核心：

```
┌─────────────────────────────────────────────────────────────────────┐
│ Phase 1: 构建时（docker build）                                     │
│                                                                     │
│  指令：FROM, RUN, COPY, ADD, ENV, ARG, WORKDIR, USER,              │
│        EXPOSE, LABEL, VOLUME, HEALTHCHECK, ENTRYPOINT, CMD          │
│  特征：                                                              │
│  - 每一条RUN在新的临时容器中执行，结果commit为新镜像层               │
│  - 每一层是只读的，持久化到最终镜像中                                │
│  - ENV/EXPOSE/LABEL等是元数据声明，不执行命令                        │
│  - 没有运行中的服务、没有外部数据卷、没有网络连接（默认）            │
│  - ARG仅在构建时可用，容器运行时不可见                               │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ Phase 2: 镜像分发（docker save / docker push / docker load / pull）│
│                                                                     │
│  - 镜像层和元数据被序列化传输/存储                                   │
│  - 不执行任何命令，只做数据搬运                                      │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ Phase 3: 运行时（docker run）                                       │
│                                                                     │
│  执行顺序：                                                          │
│  1. 创建容器（分配读写层、namespace、cgroup、网络）                  │
│  2. 应用docker run参数（覆盖ENV、挂载Volume、暴露端口等）           │
│  3. 设置USER、WORKDIR                                                │
│  4. 执行ENTRYPOINT（入口点，不可被docker run命令参数覆盖）           │
│  5. 将CMD或docker run命令参数作为参数传给ENTRYPOINT                  │
│                                                                     │
│  特征：                                                              │
│  - ENTRYPOINT每次容器启动都执行                                      │
│  - 可以访问环境变量、挂载卷、网络、容器内进程                         │
│  - 可以修改文件系统（在读写层中）                                    │
│  - CMD可以被docker run的命令行参数覆盖                               │
└─────────────────────────────────────────────────────────────────────┘
```

### 核心矛盾：固定配置 vs 动态配置

| 配置类型 | 特征 | 应放在 | 错误放置的后果 |
|---------|------|--------|--------------|
| 软件安装 | 不变、大、慢 | RUN层（构建时） | 每次启动都装软件 → 启动极慢 |
| 文件权限（镜像内） | 静态、相对固定 | RUN层chmod/chown | 运行时修改增加启动时间 |
| 源码编译 | 耗时长、不变 | RUN层make/cmake | 每次启动重新编译 → 不可行 |
| 环境变量默认值 | 可被docker run覆盖 | ENV（元数据） | 硬编码到代码中无法覆盖 |
| 端口声明 | 元数据、文档性质 | EXPOSE | 不声明不影响功能但影响文档 |
| SSH主机密钥 | 每个容器实例唯一 | ENTRYPOINT（运行时） | 所有容器共享同一密钥 → 安全风险 |
| 数据库初始化 | 依赖外部卷/环境变量 | ENTRYPOINT（运行时） | 构建时数据库不可用，初始化失败 |
| 密码/Secret | 敏感、运行时注入 | ENTRYPOINT读取（或不放入镜像） | RUN中写入密码 → 密码留在层历史中 |
| 权限修复（运行时用户） | 依赖挂载卷属主 | ENTRYPOINT | 构建时挂载点不存在 |

### SSH主机密钥案例（本次实践）

caffe-cpu:jupyter的Dockerfile在RUN层执行了`ssh-keygen -A`（第338行），生成SSH主机密钥到镜像层。但：

1. **安全最佳实践**：每个容器实例应该有唯一的主机密钥，而非所有容器共享镜像中预生成的密钥。如果密钥固定在镜像中，攻击者可以从公开镜像提取私钥进行MITM攻击。
2. **entrypoint处理**：[entrypoint-jupyter.sh](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/docker/origin/entrypoint-jupyter.sh)在容器启动时重新生成密钥（或修复权限），覆盖RUN层生成的密钥。
3. **验证陷阱**：`docker run --rm caffe-cpu:jupyter sshd -t`绕过了entrypoint，直接执行sshd。此时如果entrypoint负责生成密钥，绕过entrypoint后密钥不存在，报"no hostkeys available"——但这不是bug，是验证方式错误。

## 核心原则

### 原则1：构建时负责"静态"，运行时负责"动态"

**构建时（RUN层）应该做的事情**：
- 安装系统依赖（apt-get install、pip install）
- 编译源码（make、cmake、gcc）
- 复制静态文件（COPY配置文件、脚本、代码）
- 创建用户和组（groupadd、useradd）
- 设置固定不变的文件权限（chmod、chown）
- 下载/缓存不依赖运行时环境的数据
- 清理构建缓存（apt-get clean、rm -rf /var/lib/apt/lists）

**运行时（ENTRYPOINT脚本）应该做的事情**：
- 生成实例唯一数据（SSH密钥、TLS证书、session secret）
- 根据环境变量修改配置文件（sed/template渲染）
- 初始化依赖外部存储的数据（数据库首次启动、数据迁移）
- 修复挂载卷的权限（chown挂载点到运行用户）
- 处理docker secret/配置（从/run/secrets读取）
- 执行需要网络访问的初始化（注册服务、发现节点）
- 启动进程管理（supervisord、tini等）

### 原则2：ENTRYPOINT负责初始化，CMD负责默认命令

```dockerfile
# 正确模式
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]  # 初始化+exec到最终进程
CMD ["jupyter", "lab", "--ip=0.0.0.0"]      # 默认启动命令（可被覆盖）
```

entrypoint.sh的典型结构：
```bash
#!/bin/bash
set -e

# 1. 初始化逻辑（运行时执行）
if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
    ssh-keygen -A  # 仅在密钥不存在时生成
fi

# 2. 处理环境变量
if [ -n "$JUPYTER_PASSWORD" ]; then
    # 设置密码...
fi

# 3. 权限修复
chown -R caffe-origin:caffe-origin /workspace 2>/dev/null || true

# 4. exec到CMD（或传入的命令），替换当前进程（PID 1）
exec "$@"
```

**关键点**：使用`exec "$@"`将PID 1交给CMD进程，确保信号（SIGTERM）正确传递。

### 原则3：不要在RUN中放入敏感或实例唯一数据

```dockerfile
# ❌ 错误：密码留在镜像层历史中，所有人可见
RUN echo "root:mySecretPassword" | chpasswd

# ❌ 错误：所有容器使用同一SSH密钥
RUN ssh-keygen -A

# ✅ 正确：运行时通过环境变量/secret设置
# Dockerfile中：
# ENV DB_PASSWORD=""  # 默认空，运行时传入
# entrypoint中：
if [ -n "$DB_PASSWORD" ]; then
    echo "Setting DB password..."
fi
```

检查Docker镜像层中是否泄漏密钥：
```bash
# 查看镜像历史
docker history --no-trunc <image>:<tag>

# 更彻底：检查每一层的文件内容
docker save <image>:<tag> -o image.tar
mkdir inspect && tar xf image.tar -C inspect
# 检查各层tar中是否包含敏感文件
```

### 原则4：验证服务必须经过ENTRYPOINT

当验证容器内的服务是否配置正确时，**不要绕过ENTRYPOINT**：

```bash
# ❌ 错误：绕过entrypoint，缺少运行时初始化（密钥、配置、权限）
docker run --rm caffe-cpu:jupyter sshd -t
docker run --rm myapp:latest python -c "import config; print(config.db_url)"

# ✅ 正确1：启动完整容器，通过exec检查
docker run -d --name test-container -p 8888:8888 caffe-cpu:jupyter
sleep 5
docker exec test-container sshd -t
docker exec test-container python -c "import caffe; print('OK')"
# 验证后清理
docker stop test-container && docker rm test-container

# ✅ 正确2：使用--entrypoint覆盖为空来验证纯静态内容（仅检查文件存在/静态配置）
docker run --rm --entrypoint="" caffe-cpu:jupyter ls -la /workspace/caffex/install/
# 注意：此时没有运行时初始化，只适合验证构建时产物
```

**什么时候可以绕过ENTRYPOINT**：
- 验证文件是否存在（ls、test -f）
- 验证二进制是否可执行（--version、--help）
- 验证构建时静态生成的配置（不依赖运行时变量）
- 调试构建时问题（构建失败的排查）

**什么时候必须经过ENTRYPOINT**：
- 验证服务能否正常启动
- 验证SSH/HTTPS等需要密钥/证书的服务
- 验证依赖环境变量的配置
- 验证需要权限修复的挂载卷访问
- 验证数据库连接/初始化
- 健康检查（HEALTHCHECK指令在容器内部执行，经过entrypoint）

### 原则5：使用HEALTHCHECK做运行时健康验证

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh || exit 1
```

HEALTHCHECK在容器运行时执行（经过ENTRYPOINT初始化后），是验证服务是否真正可用的标准方式。healthcheck.sh应该检查服务是否真正响应（如HTTP请求、端口监听、CLI查询），而不仅仅是进程存在。

## 多阶段构建中的配置复用

多阶段构建（multi-stage build）中，通常分为builder阶段和runtime阶段：

```dockerfile
# 阶段1: 构建环境（包含编译器、开发库、头文件）
FROM ubuntu:22.04 AS builder
RUN apt-get update && apt-get install -y build-essential cmake libxxx-dev
COPY . /src
RUN cd /src && make && make install DESTDIR=/output

# 阶段2: 运行时环境（仅包含运行时依赖，不含编译器）
FROM ubuntu:22.04 AS runtime
RUN apt-get update && apt-get install -y libxxx1  # 仅运行时库
COPY --from=builder /output/ /  # 从builder复制编译产物
COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["myapp"]
```

在这种结构中：
- builder阶段的RUN负责编译，runtime阶段不需要编译器
- runtime阶段的ENTRYPOINT负责运行时初始化
- 不要将builder阶段的ENTRYPOINT/CMD带入runtime（多阶段构建中每个FROM是全新的）
- COPY --from=只复制文件，不复制ENV/EXPOSE/ENTRYPOINT等元数据

## 反模式

| 反模式 | 风险 | 正确做法 |
|--------|------|---------|
| RUN中生成密钥/密码/证书 | 安全漏洞：所有镜像用户共享密钥，密钥保存在层历史中 | ENTRYPOINT在运行时生成，或从secret挂载 |
| CMD中执行初始化逻辑 | CMD可被docker run <cmd>覆盖，初始化被跳过 | ENTRYPOINT做初始化，exec "$@" |
| 所有配置都在ENTRYPOINT中处理 | 启动时间过长，ENTRYPOINT脚本臃肿复杂 | 静态配置在RUN中，动态配置在ENTRYPOINT中 |
| 绕过ENTRYPOINT直接`docker run img cmd`验证服务 | 缺少运行时初始化导致"验证失败"误判 | 启动完整容器后docker exec验证 |
| ENTRYPOINT不使用exec | PID 1不是服务进程，信号不转发，容器无法优雅停止 | entrypoint末尾exec "$@" |
| 在RUN中启动服务并测试 | 构建时无网络/无完整环境，测试不可靠；增加构建时间 | 构建后单独运行容器验证 |
| 在RUN中chown -R递归大目录 | 每一次chown创建新层，镜像大小急剧增加 | 合理组织目录结构，使用COPY --chown |
| ARG当作运行时环境变量使用 | ARG仅在docker build时可用，容器运行时不可见 | 运行时需要的变量用ENV，或ENTRYPOINT处理 |

## Dockerfile指令生命周期速查

| 指令 | 阶段 | 持久化到镜像 | 可被docker run覆盖 | 每次启动执行 |
|------|------|------------|-------------------|------------|
| FROM | 构建 | - | ❌ | ❌ |
| RUN | 构建 | ✅（新层） | ❌ | ❌ |
| COPY/ADD | 构建 | ✅（新层） | ❌（卷挂载可遮蔽） | ❌ |
| ENV | 构建 | ✅（元数据） | ✅（-e/--env） | - |
| ARG | 构建 | ❌ | ❌ | ❌ |
| WORKDIR | 构建 | ✅（元数据） | ✅（-w/--workdir） | - |
| USER | 构建 | ✅（元数据） | ✅（--user） | - |
| EXPOSE | 构建 | ✅（元数据） | ✅（-p/--publish） | - |
| VOLUME | 构建 | ✅（元数据） | ✅（-v/--mount） | - |
| LABEL | 构建 | ✅（元数据） | ❌ | - |
| HEALTHCHECK | 构建 | ✅（元数据） | ❌ | ✅（按间隔执行） |
| ENTRYPOINT | 构建+运行 | ✅（元数据） | ⚠️（--entrypoint可覆盖） | ✅（每次容器启动） |
| CMD | 构建+运行 | ✅（元数据） | ✅（docker run命令参数） | ✅（作为ENTRYPOINT参数） |

## 验证检查清单

设计Dockerfile后，逐项检查：

- [ ] 软件安装、编译是否都在RUN层？
- [ ] 是否有密钥/密码/证书等敏感数据被写入RUN层？（用docker history检查）
- [ ] 实例唯一数据（密钥、session ID等）是否在ENTRYPOINT中生成？
- [ ] 是否有需要环境变量或挂载卷的初始化逻辑错误地放在了RUN层？
- [ ] ENTRYPOINT末尾是否使用exec "$@"？
- [ ] 是否配置了HEALTHCHECK？
- [ ] 验证服务时是通过docker run -d + docker exec，而非绕过ENTRYPOINT？
- [ ] 多阶段构建中runtime阶段是否只复制了必要的产物，没有带入编译器？
- [ ] ENTRYPOINT和CMD是否使用exec形式（JSON数组）而非shell形式？
- [ ] CMD是否作为ENTRYPOINT的默认参数，能被docker run命令参数合理覆盖？

## 相关模式

- [docker-image-offline-export-distribution.md](docker-image-offline-export-distribution.md) — 镜像导出六步流程（步骤3验证环节遵循本模式）
- [compiled-wheel-runtime-image-build.md](compiled-wheel-runtime-image-build.md) — 编译型Wheel运行时镜像构建（多阶段构建的具体应用）
- [dockerfile-python-code-safe-embedding.md](dockerfile-python-code-safe-embedding.md) — Dockerfile中Python代码安全嵌入
- [../architecture-patterns/docker-modular-build-orchestration.md](../architecture-patterns/docker-modular-build-orchestration.md) — Docker模块化构建编排
- [../methodology-patterns/governance-strategy/dev-env-dockerfile-optimization.md](../methodology-patterns/governance-strategy/dev-env-dockerfile-optimization.md) — 开发环境Dockerfile优化
