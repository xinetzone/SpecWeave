# caffe-ffi 生产环境部署最终操作手册

> 本手册为 caffe-ffi 延迟敏感场景（Conv v4 OpenMP 优化）生产部署的唯一操作依据。
> 所有命令均基于本机实测验证（环境：Ubuntu-24.04 / WSL / Docker 29.6.1 / 镜像 caffe-ffi-prod:latest 3.29GB）。
> 关联资产：`deploy/Dockerfile`、`deploy/build.sh`、`deploy/entrypoint.sh`、`deploy/docker-compose-latency.yml`。

---

## 1. 适用范围与目标

| 项 | 说明 |
|----|------|
| 适用场景 | 延迟敏感型实时推理（人脸识别、实时检测、在线推理服务） |
| 性能目标 | P50: 56-70ms，P99 < 1.5×P50，CV% < 5% |
| 部署方式 | Docker Compose 一键启动（`docker-compose-latency.yml`） |
| 底层技术 | OpenMP 双层并行隔离（外层 Conv OMP 多线程 + 内层 BLAS 单线程） |

**前提条件**
- Docker ≥ 20.10（实测 29.6.1），在 WSL2/Linux 环境执行
- 已构建镜像 `caffe-ffi-prod:latest`（见 §2）
- 模型文件（`.caffemodel` + `.prototxt`）与推理服务入口脚本（`.py`）

---

## 2. 镜像构建

在 **SpecWeave 根目录** 执行（Dockerfile 依赖根目录相对路径 COPY 源码）：

```bash
# 国内镜像源 + 延迟敏感 Profile（实测通过的组合）
bash .trae/specs/caffe-ffi-conv-v4-milestone/deploy/build.sh --cn --profile latency
```

其他常用变体：

```bash
bash deploy/build.sh                       # 通用 Profile（默认）
bash deploy/build.sh --cn                  # 国内镜像源 + 通用
bash deploy/build.sh --profile throughput   # 吞吐优先 Profile
bash deploy/build.sh --verify              # 构建后自动验证
```

**前置检查**（build.sh 自动执行）：`projects/xuanspace/vendor/tvm-ffi` 与 `projects/xuanspace/libs/caffe-ffi` 源码存在性。

---

## 3. 一键启动（延迟敏感端到端）

### 3.1 启动主服务

```bash
cd .trae/specs/caffe-ffi-conv-v4-milestone/deploy

# 准备挂载目录（compose 引用 ./models 与 ./config）
mkdir -p ./models ./config

# 一键启动
docker compose -f docker-compose-latency.yml up -d
```

**实测结果**：容器 `caffe-ffi-prod` 状态 `running`、`restarts=0`、`health=healthy`。

### 3.2 端到端一键验证（推荐）

```bash
docker compose -f docker-compose-latency.yml --profile verify run --rm caffe-ffi-verify
```

**实测输出摘要**：

```
python 3.14.6
caffe_ffi 0.1.0 available True
OMP_NUM_THREADS=4  OPENBLAS_NUM_THREADS=1  OMP_WAIT_POLICY=PASSIVE  OMP_PROC_BIND=unset
tvm_ffi 0.1.13
```

### 3.3 容器内深度验证

```bash
docker exec caffe-ffi-prod bash -lc 'echo OMP=$OMP_NUM_THREADS; echo BLAS=$OPENBLAS_NUM_THREADS; echo WAIT=$OMP_WAIT_POLICY; echo TZ=$TZ'
docker exec caffe-ffi-prod python -c 'import caffe_ffi; print(caffe_ffi.__version__, caffe_ffi.is_available())'
```

**实测资源限制生效**：`cpu.max=400000/100000`（4 核）、`memory.max=4294967296`（4GB）。

---

## 4. 配置参考（延迟敏感 Profile）

### 4.1 核心环境变量契约

| 变量 | 值 | 说明 |
|------|-----|------|
| `OMP_NUM_THREADS` | `4` | 外层 Conv 并行线程数，与 `--cpus=4` 对齐 |
| `OPENBLAS_NUM_THREADS` | `1` | **必须=1**，小 GEMM 场景 3-11x 退化 |
| `OMP_WAIT_POLICY` | `PASSIVE` | 延迟场景禁止 `ACTIVE`（空转浪费 CPU） |
| `OMP_SCHEDULE` | `static` | 固定调度，行为可预测 |
| `OMP_PROC_BIND` | **不设置** | 混合 P/E 核让 OS 调度 |
| `KMP_DUPLICATE_LIB_OK` | `TRUE` | Windows/多副本共存 |
| `TZ` | `Asia/Shanghai` | 时区三层保证 |

### 4.2 三 Profile 对比（entrypoint.sh 按 `DEPLOY_PROFILE` 切换）

| Profile | OMP | BLAS | WAIT | SCHED | 适用 |
|---------|-----|------|------|-------|------|
| `latency` | 4 | 1 | PASSIVE | static | 延迟敏感（本手册） |
| `throughput` | 8 | 1 | ACTIVE | static | 批量吞吐 |
| `general` | 4 | 1 | PASSIVE | - | 通用均衡 |

> 用户可通过 `-e OMP_NUM_THREADS=2` 显式覆盖 Profile 默认值（优先级更高）。

### 4.3 资源限制（compose 定义）

```yaml
cpus: "4.0"         # 与 OMP_NUM_THREADS=4 对齐
mem_limit: 4g       # 预留模型 + 中间 Blob
pids_limit: 512     # 限制进程数
```

> ⚠️ **调整 OMP 线程数时必须同步调整 cpus，保持 1:1 对齐**，否则线程过度订阅或限流。

---

## 5. 生产替换（接入真实推理服务）

默认 `command: ["sleep", "infinity"]` 仅保持容器存活供调试。生产需替换为真实推理入口：

编辑 `deploy/docker-compose-latency.yml` 主服务：

```yaml
command: ["python", "/app/serve.py", "--model", "/app/models/model.caffemodel"]
```

将模型与配置放入 `./models`、`./config`（compose 已挂载到 `/app/models:ro`、`/app/config:ro`）。

---

## 6. 运维操作

| 操作 | 命令 |
|------|------|
| 查看日志 | `docker compose -f docker-compose-latency.yml logs -f caffe-ffi-prod` |
| 进入容器 | `docker compose -f docker-compose-latency.yml exec caffe-ffi-prod bash` |
| 查看健康状态 | `docker inspect -f '{{.State.Health.Status}}' caffe-ffi-prod` |
| 重启服务 | `docker compose -f docker-compose-latency.yml restart` |
| 停止并清理 | `docker compose -f docker-compose-latency.yml down` |
| 仅清理挂载目录 | `rmdir ./models ./config` |

---

## 7. 故障排查指南

> 采用「分层排查法」：先定层（L0 容器层 → L1 环境层 → L2 应用层），再逐层定位根因，避免在错误层浪费时间。

### 7.1 诊断工具速查

| 工具 | 用途 |
|------|------|
| `docker compose -f ... ps` | 查看容器运行状态 |
| `docker inspect -f '{{.State.Health.Status}}' caffe-ffi-prod` | 查看健康检查状态 |
| `docker compose -f ... logs -f caffe-ffi-prod` | 查看应用日志 |
| `docker inspect -f '{{.State.ExitCode}} {{.State.Error}}' caffe-ffi-prod` | 查看退出码与错误 |
| `docker exec caffe-ffi-prod bash /usr/local/bin/entrypoint.sh --healthcheck` | 手动触发健康检查 |
| `docker exec caffe-ffi-prod cat /sys/fs/cgroup/cpu.max` | 查看 CPU 配额（cgroup v2） |

### 7.2 容器启动失败

**排查流程**：

```
容器启动失败
├─ 无法启动（一直 Exited） → 看退出码
│   ├─ ExitCode=0 → command 执行完就退出（如 sleep infinity 被替换成一次性命令）
│   ├─ ExitCode=1/2 → 应用启动报错 → 看 logs
│   ├─ ExitCode=137(OOM kill) → 内存超限 → 调大 mem_limit 或降副本
│   └─ ExitCode=139(段错误) → C++ 扩展崩溃 → 查 ldd / KMP_DUPLICATE_LIB_OK
├─ crash-loop（反复重启） → 见下方「crash-loop 专项」
└─ 启动但 Unhealthy → 见下方「健康检查失败专项」
```

**crash-loop 专项**：

| 根因 | 判断方法 | 解决 |
|------|---------|------|
| `command` 被替换为不常驻进程 | 日志显示启动后立即退出，ExitCode=0 | 恢复 `sleep infinity` 或改为常驻服务 |
| 环境变量未生效（Python 内 os.environ 覆盖失败） | 容器内 `echo $OMP_NUM_THREADS` 为空 | 在 Dockerfile/entrypoint 设置，勿在 Python 内设置 |
| 共享库缺失 | `docker exec ... ldd <caffe_ffi._caffe_ffi.so> | grep 'not found'` | 检查 `LD_LIBRARY_PATH`、`ldconfig` |

**健康检查失败专项**：

```
docker inspect -f '{{.State.Health.Status}}' caffe-ffi-prod   # 若为 unhealthy
docker inspect -f '{{.State.Health.Log}}' caffe-ffi-prod       # 看失败原因
docker exec caffe-ffi-prod bash /usr/local/bin/entrypoint.sh --healthcheck  # 手动复现
```

常见原因：`caffe_ffi` 导入失败（conda 环境/共享库）、`protobuf` ABI 不匹配（串行化 roundtrip 崩溃）。

### 7.3 性能异常

**排查流程**：

```
性能异常
├─ FPS 远低于预期 →
│   ├─ OPENBLAS_NUM_THREADS>1？ → 小 GEMM 3-11x 退化 → 强制 =1
│   ├─ CPU 被限流？ → cpu.max 是否 < 设置值 → 副本数×cpus≤物理核数
│   └─ 小模型(<64×64)多线程？ → fgvsirfeature_ssd 应 OMP=1
├─ P99 抖动大(CV%>10%) →
│   ├─ OMP_WAIT_POLICY=ACTIVE？ → 延迟场景应 PASSIVE
│   ├─ CPU 限流/同机争抢？ → 检查配额与同机负载
│   └─ Inception 大 batch？ → 参考抖动缓解方案
└─ 多线程无加速 →
    ├─ 层输出通道<32？ → 自适应线程数自动单线程（正常）
    └─ 物理核不足？ → OMP 不超物理核数
```

**环境变量验证命令**：

```bash
docker exec caffe-ffi-prod bash -lc 'echo OMP=$OMP_NUM_THREADS; echo BLAS=$OPENBLAS_NUM_THREADS; echo WAIT=$OMP_WAIT_POLICY'
```

**关键检查项（按优先级）**：

| 优先级 | 检查 | 通过标准 |
|--------|------|---------|
| P0 | `OPENBLAS_NUM_THREADS` | 必须=1 |
| P0 | CPU 配额 | `cpu.max` 与 `--cpus` 一致，未限流 |
| P1 | `OMP_WAIT_POLICY`（延迟场景） | PASSIVE |
| P1 | `OMP_PROC_BIND` | 未设置 |
| P2 | 线程数与物理核对齐 | `OMP_NUM_THREADS` ≤ 物理核数 |
| P2 | 同机资源争抢 | 无其他高 CPU 容器 |

### 7.4 禁用项清单（性能退化根因）

| 禁用项 | 现象 |
|--------|------|
| ❌ `OPENBLAS_NUM_THREADS>1` | FPS 3-11x 退化 |
| ❌ `OMP_WAIT_POLICY=ACTIVE`（延迟场景） | CPU 空转、抖动 |
| ❌ `OMP_PROC_BIND=CLOSE/SPREAD` | P/E 核负载不均 |
| ❌ `OMP_SCHEDULE=runtime` | 行为不可预测 |
| ❌ `KMP_AFFINITY=compact...` | 兼容性问题，可能崩溃 |

---

## 8. 验证清单（上线前逐项勾选）

- [ ] 镜像构建成功（`build.sh --cn --profile latency`）
- [ ] `docker compose up -d` 后容器 `running` / `restarts=0` / `health=healthy`
- [ ] `--profile verify run` 4 项检查全部通过
- [ ] 环境变量：OMP=4, BLAS=1, WAIT=PASSIVE, BIND=unset
- [ ] 资源限制：cpu.max=400000/100000, memory.max=4294967296
- [ ] 真实推理服务已替换 `command` 并通过一次推理验证
- [ ] 延迟指标满足 P50/P99/CV% 目标

---

> 完整性能数据与三 Profile 决策依据详见 [deployment_config_guide](../deployment_config_guide.md) 与技术总结 `caffe-ffi-conv-v4-optimization-summary.md`。
> 多副本 + 负载均衡的高可用部署详见 [HA_DEPLOYMENT_PLAN.md](HA_DEPLOYMENT_PLAN.md)（含 `docker-compose-ha.yml` 与 `haproxy.cfg`）。