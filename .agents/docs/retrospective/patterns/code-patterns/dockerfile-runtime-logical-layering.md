---
id: "dockerfile-runtime-logical-layering"
title: "Dockerfile Runtime 阶段六步逻辑分层模式"
type: "code-pattern"
maturity: "L1-draft"
maturity_note: "jupyter-ssh-base v1.0+ 实战验证；单案例，待更多项目验证后升级L2"
source:
  - "jupyter-ssh-base Dockerfile 6阶段分层构建实践"
related_patterns:
  - "docker-buildtime-vs-runtime-config.md"
  - "compiled-wheel-runtime-image-build.md"
  - "conda-docker-multistage-best-practices.md"
tags: ["docker", "dockerfile", "multi-stage-build", "layering", "cache-optimization", "build-verification"]
validation_count: 1
reuse_count: 1
---

# Dockerfile Runtime 阶段六步逻辑分层模式

## 触发场景

- 编写或审查多阶段 Dockerfile 的 runtime（最终镜像）阶段
- 遇到以下任一痛点：
  - Dockerfile 一个巨大 RUN 指令，改一处配置就要重新安装所有系统包
  - 构建缓存频繁失效，无法利用 Docker 层缓存加速
  - 错误发生时无法快速定位是哪个阶段出了问题
  - 镜像中残留了不需要的编译工具或缓存文件
  - 不知道"哪些配置应该在构建时做，哪些应该在运行时做"

**不适用于**：
- 单阶段 Dockerfile（FROM scratch 的极简镜像）
- 临时构建镜像（只用来编译不发布）
- 静态二进制 + scratch 的部署镜像

## 问题本质

多阶段构建中，很多人知道要做 `builder → runtime` 的物理分离，但 runtime 阶段内部仍是一个大杂烩 RUN 指令——安装包、复制文件、创建用户、配置服务、清理、验证全部塞在一起。这导致三个问题：

1. **缓存失效范围过大**：修改配置文件会导致"重新安装所有系统包"这一步重新执行
2. **错误定位困难**：构建失败时日志几百行，不知道是哪一步出错
3. **职责不清**：静态配置和动态初始化混在一起，容易把应该放在 ENTRYPOINT 的逻辑错放到 RUN 层

## 核心原则

物理两阶段（builder + runtime）只是基础，**runtime 阶段内部必须按单一职责拆分为 6 个逻辑层**，每层一个 RUN 指令，有清晰的注释边界和验证点。

## 标准方案（6 步逻辑分层）

```dockerfile
# ─────────────────────────────────────────────────────────────────────
# Stage 2: Runtime - Minimal production image
# ─────────────────────────────────────────────────────────────────────
FROM ubuntu:26.04

ARG APT_MIRROR

# 环境变量声明集中放在这里（层 0，元数据，不执行命令）
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai
ENV PATH="/opt/venv/bin:${PATH}"
# ...

# ═══════════════════════════════════════════════════════════════════
# Stage 2.1/6: 系统包安装 + 基础环境配置（locale/timezone）
# 变化频率：最低（基础镜像确定后很少改）
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 1/6: Install base system packages + locale ===" && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates curl locales openssh-server \
        python3 python3-venv sudo supervisor tini tzdata vim wget \
        # ... 仅运行时依赖，不含 build-essential/python3-dev
    && sed -i 's/^# *zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen zh_CN.UTF-8 && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# ═══════════════════════════════════════════════════════════════════
# Stage 2.2/6: 语言运行时 / 编译产物复制（从 builder 阶段 COPY）
# 变化频率：低（依赖版本升级时改）
# ═══════════════════════════════════════════════════════════════════
COPY --from=builder /opt/venv /opt/venv
# 或 COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
RUN echo "=== Stage 2/6: Copy language runtime from builder ===" && \
    python3 --version && pip --version && jupyter --version && \
    echo "export PATH=/opt/venv/bin:\$PATH" > /etc/profile.d/venv.sh && \
    chmod +x /etc/profile.d/venv.sh

# ═══════════════════════════════════════════════════════════════════
# Stage 2.3/6: 用户/组/目录创建 + 权限设置
# 变化频率：中（新增用户或目录时改）
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 3/6: Create non-root user ===" && \
    if ! getent passwd 1000 >/dev/null 2>&1; then \
        useradd -m -s /bin/bash -u 1000 -G sudo appuser; \
    else \
        useradd -m -s /bin/bash -G sudo appuser; \
    fi && \
    mkdir -p /workspace /home/appuser/.ssh && \
    chmod 700 /home/appuser/.ssh && \
    chown -R appuser:appuser /workspace /home/appuser

# ═══════════════════════════════════════════════════════════════════
# Stage 2.4/6: 运行时目录准备 + 基础配置框架
# 变化频率：中（新增服务需要新目录时改）
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 4/6: Prepare runtime directories ===" && \
    mkdir -p /run/sshd /var/log/supervisor /etc/supervisor/conf.d

# ═══════════════════════════════════════════════════════════════════
# Stage 2.5/6: 配置文件复制 + 脚本安装 + 语法验证
# 变化频率：高（配置调整时改，缓存不会让前面的层失效）
# ═══════════════════════════════════════════════════════════════════
COPY config/sshd_config /etc/ssh/sshd_config
COPY config/supervisord.conf /etc/supervisor/supervisord.conf
COPY config/supervisor/conf.d/ /etc/supervisor/conf.d/
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY scripts/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN echo "=== Stage 5/6: Install configs and validate ===" && \
    chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/healthcheck.sh && \
    sshd -t && echo "[OK] sshd config valid" && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] entrypoint syntax" && \
    bash -n /usr/local/bin/healthcheck.sh && echo "[OK] healthcheck syntax"

# ═══════════════════════════════════════════════════════════════════
# Stage 2.6/6: 构建元数据 + 最终清理 + 构建内验证
# 变化频率：最低（版本发布时改）
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== Stage 6/6: Final verification ===" && \
    echo "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /etc/build-info && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    # 最终验证：关键命令都可用
    supervisord --version && python --version && pip --version

# 元数据声明（不产生层）
WORKDIR /workspace
VOLUME ["/workspace"]
EXPOSE 22 8888
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD []
```

## 各层设计要点

| 层 | 名称 | 变化频率 | 关键原则 | 验证点 |
|----|------|---------|---------|--------|
| 2.1 | 系统包安装 | 低 | `--no-install-recommends`，同层内配置 locale/timezone | `locale -a` 检查 zh_CN |
| 2.2 | 运行时复制 | 低 | COPY --from=builder 后立即验证二进制可用 | `<cmd> --version` |
| 2.3 | 用户/目录 | 中 | UID 优先固定值，被占用时自动 fallback；chown 在同层 | `id <user>` 检查 |
| 2.4 | 目录准备 | 中 | mkdir -p 所有 runtime 需要的空目录 | 目录存在性检查 |
| 2.5 | 配置复制 | **高** | COPY 所有配置文件，同层内做语法验证（`sshd -t`/`bash -n`） | 配置语法校验 |
| 2.6 | 清理+验证 | 最低 | 清理缓存，写入构建元数据，做最终可用性验证 | 关键命令存在检查 |

**缓存优化关键**：最易变的层（配置文件 COPY）放在后面，最稳定的层（系统包安装）放在前面，最大化 Docker 构建缓存命中。

## 反模式（至少 3 个）

### ❌ 反模式 1：整个 runtime 一个 RUN 指令

```dockerfile
# 错误：所有事情塞在一起，改一行配置要重新安装所有包
FROM ubuntu:26.04
RUN apt-get update && apt-get install -y ... && \
    useradd -m appuser && \
    mkdir -p /workspace && \
    COPY . /app && ...
```

后果：改一句配置注释，Docker 缓存全部失效，每次构建都要等几分钟装包。

### ❌ 反模式 2：COPY 放在 RUN 之前（缓存投毒）

```dockerfile
# 错误：先复制代码再装包，代码每次变导致装包每次重跑
COPY . /app
RUN apt-get update && apt-get install -y python3-dev ...
```

后果：即使是 README 改了一个字，apt-get install 也要重新执行。正确顺序：先装包（稳定层）→ 再复制源码（易变层）。

### ❌ 反模式 3：runtime 阶段残留编译工具链

```dockerfile
# 错误：runtime 阶段也安装了 build-essential/gcc/python3-dev
FROM ubuntu:26.04
RUN apt-get install -y build-essential python3-dev gcc ...
```

后果：镜像体积膨胀数百 MB，攻击面增大。正确做法：编译工具只在 builder 阶段安装，runtime 阶段 COPY 编译产物。

### ❌ 反模式 4：COPY 后不做语法验证

```dockerfile
# 错误：复制了 entrypoint.sh 和配置文件，但构建时不检查语法
COPY entrypoint.sh /usr/local/bin/
# 没做 bash -n，直到运行时才发现语法错误
```

后果：构建"成功"但启动失败，问题留到运行时才发现。正确做法：COPY 后立即在 RUN 层做语法校验（`bash -n`、`sshd -t`、`nginx -t` 等），构建即测试。

## 检验标准

审查 Dockerfile 时逐项检查：

- [ ] runtime 阶段是否分为 6 个逻辑层，每层有清晰注释？
- [ ] 系统包安装是否在最靠前的稳定层？配置 COPY 是否在靠后的易变层？
- [ ] runtime 阶段是否不包含 build-essential/gcc/python3-dev 等编译工具？
- [ ] 每个 apt-get install 是否带 `--no-install-recommends` 并在同层清理 lists？
- [ ] COPY 配置/脚本后是否执行了语法验证命令？
- [ ] 是否有最终验证步骤确认关键命令可用？
- [ ] pip install 是否带 `--no-cache-dir`？
- [ ] ENTRYPOINT 是否使用 exec 形式（JSON 数组）？

## 迁移示例（跨领域）

不仅适用于 Python/Jupyter 镜像，任何多阶段构建的 runtime 阶段都适用：

**Go 应用镜像**：
- Stage 2.1：安装 ca-certificates、tzdata、系统库
- Stage 2.2：COPY --from=builder /app/mybinary /usr/local/bin/
- Stage 2.3：创建非 root 用户
- Stage 2.4：准备配置目录/数据目录
- Stage 2.5：COPY 配置文件，验证二进制 `--version`
- Stage 2.6：清理 + HEALTHCHECK

**Node.js 前端镜像（Nginx 托管）**：
- Stage 2.1：安装 nginx
- Stage 2.2：（无语言运行时，静态文件直接 COPY）
- Stage 2.3：创建 www-data 用户目录
- Stage 2.4：准备 /var/log/nginx
- Stage 2.5：COPY nginx.conf + 静态构建产物，`nginx -t` 验证
- Stage 2.6：清理 + HEALTHCHECK

## 边界条件与常见疑问（来自对抗审查）

**Q: 6个RUN增加镜像层数，会不会影响拉取性能？**

每个Docker镜像层元数据约100字节，6层共约600字节，对拉取性能影响完全可忽略。换来的收益：修改配置文件（最频繁操作）时，Docker不需要重新执行"安装系统包"（通常30秒到几分钟），构建时间从几分钟降到几秒钟。且每层RUN末尾都执行apt-get clean和rm -rf缓存，不增加实际文件体积。构建缓存收益远大于600字节元数据成本。

**Q: 分隔符注释是不是太形式化？增加工作量？**

分隔符和阶段注释可直接复制粘贴模板，几乎零成本。反而降低维护认知负担——改SSH端口配置时不用读完整个100行RUN，直接跳转到Stage 2.5/6；构建失败时日志清晰显示`=== Stage 2/6: ...`后面跟着错误，不需要从上千行日志找是哪一步出错。形式化收益（可定位、可维护、缓存命中）远大于成本。

**不适用场景**（已在触发场景中列出）：
- 单阶段 FROM scratch 极简镜像
- 临时构建镜像（只编译不发布）
- 静态二进制 + scratch 部署镜像

## 成熟度

L1-draft — jupyter-ssh-base 项目中验证可行（镜像从单阶段 1.2GB 减到 713MB，配置修改不触发重装包），但尚未在第二个不同类型项目中验证。V阶段对抗审查（怀疑者/实践者/运维/SRE/维护者五视角）全部通过。

## 交叉引用

- 来源：jupyter-ssh-base 项目七概念方法论复盘（2026-08-07）
- 关联模式：
  - docker-buildtime-vs-runtime-config.md（构建时 vs 运行时职责分离是本模式的前提）
  - compiled-wheel-runtime-image-build.md（Python wheel 运行时镜像的具体分层实践）
  - conda-docker-multistage-best-practices.md（Conda 环境的多阶段构建）
- 参考实例：
  - [Dockerfile](file:///d:/spaces/SpecWeave/apps/jupyter-ssh-base/Dockerfile)（本模式的参考实现）
