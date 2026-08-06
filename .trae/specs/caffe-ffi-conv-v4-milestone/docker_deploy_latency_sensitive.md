# caffe-ffi 延迟敏感场景 Docker 部署启动命令

基于 [deployment_config_guide.md](deployment_config_guide.md) 的 **Profile A（延迟敏感型）** 部署配置，生成完整的 Docker 启动命令与参数配置。

## 适用场景

- 人脸识别、实时检测、在线推理服务
- P99 延迟有严格 SLA（目标 P50: 56-70ms，P99 < 1.5×P50，CV% < 5%）
- batch=1 实时推理

## 核心环境变量（Profile A）

```bash
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1
export OMP_WAIT_POLICY=PASSIVE
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_SCHEDULE=static
# 绝不设置 OMP_PROC_BIND（混合 P/E 核让 OS 调度更优）
# 绝不设置 OMP_WAIT_POLICY=ACTIVE
```

## Docker 启动命令

### 方案一：通过 `docker run` 环境变量注入（推荐）

```bash
docker run -d \
  --name caffe-ffi-prod \
  --restart=unless-stopped \
  -e OMP_NUM_THREADS=4 \
  -e OPENBLAS_NUM_THREADS=1 \
  -e OMP_WAIT_POLICY=PASSIVE \
  -e KMP_DUPLICATE_LIB_OK=TRUE \
  -e OMP_SCHEDULE=static \
  -e GLOG_minloglevel=2 \
  -e PYTHONUNBUFFERED=1 \
  --cpus=4 \
  --memory=4g \
  --pids-limit=512 \
  -p 8080:8080 \
  -v /path/to/models:/models:ro \
  -v /path/to/config:/config:ro \
  caffe-ffi:latest
```

**参数说明：**

| 参数 | 值 | 说明 |
|------|-----|------|
| `--cpus=4` | 4 | **关键**：限制 CPU 配额为 4 核，与 OMP_NUM_THREADS=4 匹配，防止线程扩展不足或过度订阅 |
| `--memory=4g` | 4G | 预留模型 + 中间 Blob 内存，fgvsirfeature 等模型约需 1-2G |
| `--pids-limit=512` | 512 | 限制进程数，防止进程失控 |
| `--restart=unless-stopped` | - | 崩溃自动重启，保证服务可用性 |
| 模型挂载 `:ro` | 只读 | 防止模型文件被意外修改 |

### 方案二：`docker run` + 环境文件（env file）

创建 `prod.env` 文件：

```bash
# prod.env — 延迟敏感场景环境配置文件
OMP_NUM_THREADS=4
OPENBLAS_NUM_THREADS=1
OMP_WAIT_POLICY=PASSIVE
KMP_DUPLICATE_LIB_OK=TRUE
OMP_SCHEDULE=static
GLOG_minloglevel=2
PYTHONUNBUFFERED=1

# 切勿设置以下项：
# OMP_PROC_BIND=true
# OMP_WAIT_POLICY=ACTIVE
# OPENBLAS_NUM_THREADS > 1
```

启动命令：

```bash
docker run -d \
  --name caffe-ffi-prod \
  --restart=unless-stopped \
  --env-file prod.env \
  --cpus=4 \
  --memory=4g \
  -p 8080:8080 \
  -v /path/to/models:/models:ro \
  caffe-ffi:latest
```

### 方案三：Dockerfile 固化（重建镜像时生效）

```dockerfile
FROM caffe-ffi:latest

# 延迟敏感场景环境变量（固化到镜像）
ENV OMP_NUM_THREADS=4
ENV OPENBLAS_NUM_THREADS=1
ENV OMP_WAIT_POLICY=PASSIVE
ENV KMP_DUPLICATE_LIB_OK=TRUE
ENV OMP_SCHEDULE=static
ENV GLOG_minloglevel=2

# 入口脚本（内部激活 caffe-ffi conda 环境）
CMD ["bash", "/app/entrypoint.sh"]
```

## 延迟敏感场景的额外优化参数

### 1. CPU 亲和性（可选，需实测）

默认**不设置** `OMP_PROC_BIND`，让 OS 在混合 P/E 核上自动调度。若 P99 抖动仍明显，可尝试绑定物理核心：

```bash
# 仅当测试确认改善后才启用（否则可能把线程钉在 E-core 上）
docker run -d \
  --name caffe-ffi-prod \
  --cpuset-cpus="0-3" \
  --cpus=4 \
  -e OMP_NUM_THREADS=4 \
  --platform linux/amd64 \
  caffe-ffi:latest
```

> ⚠️ **注意**：`--cpuset-cpus` 需根据 NUMA 拓扑和 P/E 核分布调整，强烈建议先跑 `jw_wait`/`hardware-taskset` 确认核映射，避免钉到 E-core 导致性能下降。

### 2. 模型特定配置

| 模型 | 推荐 OMP 线程 | 说明 |
|------|--------------|------|
| ResNet-50/101 | 4 | 标准配置 |
| InceptionV1 (batch=1) | 4 | 标准配置；batch>1 参考抖动缓解方案 |
| fgvsirfeature (120×120) | 2-4 | 先压测，加速<1.1x 则降为 2 |
| fgvsirfeature_ssd (32×32) | **1** | 极小模型，多线程负收益，强制单线程 |

### 3. 运行时内存预分配（Python 侧）

在推理服务启动时预热，减少首次延迟抖动：

```python
import os
import numpy as np
import caffe_ffi

def prewarm(net, batch=1, input_size=(3,224,224), iterations=50):
    """预热：用不同输入数据 touch 所有内存页，稳定后延迟抖动量级下降。"""
    input_blob = net.blob_by_name("data")
    for _ in range(iterations):
        data = np.random.rand(batch, *input_size).astype(np.float32)
        input_blob.data = data
        net.forward()
```

## 验证配置是否生效

```bash
# 进入容器检查环境变量
docker exec caffe-ffi-prod bash -c 'echo "OMP=$OMP_NUM_THREADS"; echo "BLAS=$OPENBLAS_NUM_THREADS"; echo "WAIT=$OMP_WAIT_POLICY"; echo "SCHED=$OMP_SCHEDULE"'

# Python 侧验证
docker exec caffe-ffi-prod python -c "import os; print(os.environ.get('OMP_NUM_THREADS'), os.environ.get('OPENBLAS_NUM_THREADS'))"
```

## 服务健康检查建议

针对延迟敏感场景，建议在服务内暴露 P50/P99 指标，并设置告警阈值：

```python
# 伪代码：延迟监控
percentile_99 = np.percentile(latencies, 99)
if percentile_99 > 1.5 * np.median(latencies):
    alert("P99 tail latency exceeded SLA")
```

## 常见问题排查

| 症状 | 排查方向 |
|------|---------|
| 实际 FPS 远低于预期 | 检查 `OPENBLAS_NUM_THREADS` 是否被覆盖为 >1 |
| P99 抖动明显 | 检查 `--cpus` 是否与 `OMP_NUM_THREADS` 匹配、是否 CPU 限流 |
| 低频抖动 | 检查是否开启了 turbo boost、是否被其他容器抢占 |
| 多线程无加速 | 小模型（<64×64）强制 OMP=1 |

---

> 完整对比数据与部署 Profile 详见 [deployment_config_guide.md](deployment_config_guide.md)。