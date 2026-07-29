---
id: docker-commit-config-reset
title: docker commit 入口配置显式重置
type: code-pattern
date: 2026-07-18
maturity: L1
source: retrospective-docker-commit-entrypoint-fix-20260718
related_patterns: [docker-container-session-raii.md, compiled-wheel-runtime-image-build.md]
tags: [Docker, docker-commit, ENTRYPOINT, CMD, 镜像构建, 容器化, Dockerfile, declarative]
validation_count: 2
reuse_count: 1
---

# docker commit 入口配置显式重置

## 触发场景
- 当使用 `docker run → docker exec → docker commit` 工作流做镜像增量更新时
- 临时容器使用了保活入口（bash/sleep/tail -f /dev/null/sleep infinity等），需要commit为正式镜像
- 适用于：wheel包更新、热修复补丁、快速原型迭代
- 不适用于：可重复构建场景（应使用Dockerfile声明式构建）

## 核心做法
1. 在 `docker run` 启动临时容器时，使用保活命令保持容器运行（如 `--entrypoint /bin/bash -c "while true; do sleep 3600; done"`）
2. 通过 `docker exec` 在容器内执行修改操作（安装包、修改配置等）
3. **关键步骤**：在 `docker commit` 命令中使用 `--change='ENTRYPOINT []'` 清空入口点
4. 使用 `--change='CMD ["/bin/bash"]'`（或对应业务的默认命令）设置合理的默认命令
5. commit后使用 `docker inspect IMAGE --format '{{.Config.Entrypoint}} {{.Config.Cmd}}'` 验证配置
6. 使用 `docker run --rm IMAGE <测试命令>` 验证镜像可用性

## 反模式（不要这么做）
- ❌ 直接 `docker commit $CONTAINER $IMAGE` 不做任何配置重置，导致保活配置（sleep/tail等）泄漏为永久入口
- ❌ 在docker run时用 `--entrypoint ''` 绕过问题而不从镜像层面修复（治标不治本，每个使用者都要知道这个workaround）
- ❌ 使用 `docker commit --change='ENTRYPOINT ["/bin/bash"]'` 但不清空CMD（会保留sleep infinity等保活命令，容器启动后假死）
- ❌ 用 docker commit 替代 Dockerfile 做正式发布镜像构建（commit是命令式快照，不可复现、不可审计）

## 检验标准
做完之后怎么知道做对了？
- `docker inspect IMAGE --format '{{.Config.Entrypoint}}'` 输出为 `[]` 或正确的入口脚本路径（非bash保活入口）
- `docker inspect IMAGE --format '{{.Config.Cmd}}'` 输出为合理的默认命令（如 `["/bin/bash"]` 或 `["python"]`），而非sleep/tail等保活命令
- `docker run --rm IMAGE bash -c "echo ok"` 能正常输出 "ok" 并退出
- `docker run --rm IMAGE python3 -c "print('ok')"` （如果镜像含Python）能正常执行
- `docker run -it --rm IMAGE`（无额外参数）能进入交互式shell或启动预期服务，而非进入sleep假死

## 迁移示例
这个模式还能用在什么其他场景？
- 场景1（跨领域-虚拟机快照）：VirtualBox/VMware快照类似docker commit——快照会保存当前运行状态。做"黄金镜像"前必须重置临时状态（卸载临时工具、清理日志、重置网络配置），否则快照中会残留临时配置
- 场景2（跨领域-数据库备份）：类似docker commit的"快照陷阱"——在数据库运行中做备份时如果不先quiesce（停写/flush），备份中可能包含未完成的事务。对应docker commit中的 `--change` 重置，数据库备份需要 `FLUSH TABLES WITH READ LOCK` 确保一致性
- 场景3（CI/CD镜像更新）：CI流水线中构建镜像后通过docker commit保存测试结果/覆盖率数据时，同样需要重置ENTRYPOINT/CMD确保后续部署正常

## 边界条件
- 如果镜像确实需要自定义ENTRYPOINT（如客户端镜像的entrypoint.sh做UID/GID适配），应使用 `--change='ENTRYPOINT ["/path/to/entrypoint.sh"]'` 设置正确的入口脚本，而非清空
- 多阶段构建（multi-stage build）是比docker commit更好的增量更新方案，支持可复现构建
- docker commit适合快速原型和临时验证，正式发布应使用Dockerfile

## 实际案例

### 案例1：xmnn-client ENTRYPOINT 泄漏（首次验证，源案例）

**项目**：xmnn-client Docker 镜像增量更新
**问题**：使用 `docker run --entrypoint tail -f /dev/null` 启动保活容器 → `docker exec` 安装依赖 → `docker commit` 保存镜像，结果 `tail -f /dev/null` 泄漏为永久 ENTRYPOINT
**修复**：`docker commit --change='ENTRYPOINT []' --change='CMD ["/bin/bash"]'`
**验证**：`docker inspect` 确认 ENTRYPOINT 为空，CMD 为 bash

### 案例2：xmnn-client PyTorch 集成中的 Dockerfile 替代方案（本次复盘验证）

**项目**：xmnn-client:1.2.2-alpha PyTorch 2.13.0 集成
**问题**：使用 `docker commit` 更新镜像后，ENTRYPOINT 被覆盖为 `tail`，导致容器启动后假死。即使通过 `--change` 修复 ENTRYPOINT，仍存在以下问题：
1. docker commit 继承的运行时状态不透明，难以审计
2. 每次更新都需要手动指定 `--change` 参数，容易遗漏
3. 镜像不可重复构建，无法追溯构建过程

**修复方案**：放弃 docker commit，改用 Dockerfile 声明式构建

```dockerfile
FROM nuitka-gcc-llvm:latest

# 安装 PyTorch 和依赖
RUN pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install onnx2pytorch tabulate

# 安装 xmnn wheel
COPY xmnn-1.2.2-cp314-cp314-linux_x86_64.whl /tmp/
RUN pip install /tmp/xmnn-1.2.2-cp314-cp314-linux_x86_64.whl

# 创建 sitecustomize.py（Python 3.14 multiprocessing fork 兼容）
RUN mkdir -p $(python -c "import site; print(site.getusersitepackages())") && \
    echo 'import multiprocessing; multiprocessing.set_start_method("fork", force=True)' \
    > $(python -c "import site; print(site.getusersitepackages())")/sitecustomize.py

# 显式声明入口（避免继承问题）
ENTRYPOINT []
CMD ["bash"]
```

**验证结果**：
- ✅ 镜像可重复构建
- ✅ ENTRYPOINT/CMD 配置正确
- ✅ 构建过程可审计（Dockerfile 即文档）
- ✅ 无临时配置泄漏

**教训**：Docker 镜像更新应优先使用 Dockerfile 声明式构建，docker commit 仅用于快速原型验证。详见归档文档 [docker-declarative-first-principle.md](../../../../knowledge/best-practices/docker-declarative-first-principle.md)

## Changelog

- **2026-07-18** (v1.0.0): 初始版本，从 xmnn-client ENTRYPOINT 泄漏修复萃取，单案例验证，标记 L1-draft
- **2026-07-23** (v1.1.0): 补充 Dockerfile 替代方案案例（案例2），强调声明式优先原则，验证计数 1→2，maturity 升级为 L1。来源：retrospective-xmnn-pytorch-integration-20260723
