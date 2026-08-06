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

## 7. 故障排查

| 症状 | 排查方向 |
|------|---------|
| 容器 crash-loop | 检查 `command` 是否被替换为真实服务；`sleep infinity` 不应崩溃 |
| 实际 FPS 远低于预期 | 检查 `OPENBLAS_NUM_THREADS` 是否被覆盖为 >1 |
| P99 抖动明显 | 检查 `--cpus` 与 `OMP_NUM_THREADS` 是否匹配、CPU 是否限流 |
| 多线程无加速 | 小模型（<64×64）强制 `OMP=1`（如 fgvsirfeature_ssd） |
| `caffe_ffi` 导入失败 | 检查 conda 环境、`ldd` 共享库解析、`KMP_DUPLICATE_LIB_OK` |

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

> 完整性能数据与三 Profile 决策依据详见 [deployment_config_guide](deployment_config_guide.md) 与技术总结 `caffe-ffi-conv-v4-optimization-summary.md`。