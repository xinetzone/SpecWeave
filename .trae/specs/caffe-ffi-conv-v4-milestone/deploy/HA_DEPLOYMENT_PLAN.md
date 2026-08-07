# caffe-ffi 生产环境高可用（HA）部署方案

> 基于 caffe-ffi 延迟敏感场景（Conv v4 OpenMP 优化）现有单机部署的无状态服务特性，设计多副本 + 负载均衡 HA 方案。
> 关联资产：`deploy/docker-compose-ha.yml`（阶段1）、`deploy/haproxy.cfg`（阶段1 LB）、`deploy/PRODUCTION_DEPLOYMENT_MANUAL.md`（单机操作手册）。
> 适用前提：镜像 `caffe-ffi-prod:latest` 已构建（见操作手册 §2）。

---

## 1. 设计原则（第一性原理）

| 原则 | 推导 | 落地 |
|------|------|------|
| 无状态性 | caffe-ffi 推理为纯内存计算，模型经只读挂载加载，无共享可变状态 | **多副本水平扩展可行**，无跨副本一致性问题 |
| 故障容忍 | 消除单点故障（SPOF），每个组件均可复制 | 副本 ≥ 2、LB 自身可复制 |
| 负载分发 | 请求均匀分布到多个副本 | 负载均衡器（HAProxy / K8s Service） |
| 故障检测与恢复 | 及时感知副本不可用并摘除/重建 | Docker 健康检查 + 编排自动恢复 |
| 故障隔离 | 副本间资源独立，单副本故障不影响整体 | 每副本独立 CPU/内存配额 |

---

## 2. 两阶段演进

| 阶段 | 方案 | 消除的故障 | 短板 |
|------|------|-----------|------|
| **阶段1** | Docker Compose + `--scale N` + HAProxy 负载均衡 | 进程/容器级故障（崩溃、OOM、死锁） | 单主机的确权仍是 SPOF |
| **阶段2** | Kubernetes Deployment + Service + HPA + Ingress | 主机级故障（宕机、重启、硬件故障） | 运维复杂度高，需 K8s 集群 |

> **决策条件**：仅需提升单机可用性（进程崩溃自动恢复）→ 阶段1；需要跨节点容灾/自动扩缩容 → 阶段2。

---

## 3. 阶段1：单机多副本 + HAProxy 负载均衡

### 3.1 架构

```
                 ┌──────────────┐
  client :8080 ─▶│  HAProxy LB  │  (主动健康检查, round-robin)
                 └──────┬───────┘
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   caffe-ffi-prod-1  prod-2      prod-3    (deploy --scale 3)
   8080 健康检查    8080         8080
          └──────── shared read-only mounts ──┘
```

- **副本**：`caffe-ffi-prod` 无状态，通过 `--scale 3` 拉出多副本
- **负载均衡**：HAProxy 主动健康检查（`option httpchk GET /health`），故障副本自动摘除
- **健康检查契约**：真实推理服务必须暴露 HTTP `/health` 端点（返回 2xx 视为健康）

### 3.2 启动命令

```bash
cd .trae/specs/caffe-ffi-conv-v4-milestone/deploy
mkdir -p ./models ./config

# 启动 3 副本 + HAProxy（前端 8080, 统计页 8404）
docker compose -f docker-compose-ha.yml up -d --scale caffe-ffi-prod=3
```

### 3.3 验证

```bash
# LB 统计页（查看后端健康状态）
open http://localhost:8404/stats          # admin:admin

# 健康后端应全部为 UP
docker compose -f docker-compose-ha.yml ps

# 故障注入验证（停止一个副本，观察 HAProxy 摘除）
docker compose -f docker-compose-ha.yml stop caffe-ffi-prod
# → 其余副本继续服务，无请求中断
```

### 3.4 关键配置

**HAProxy 主动健康检查**（`option httpchk` + `check inter`）：每 3s 探测，`fall 3`次失败摘除、`rise 2`次成功恢复。相比 Nginx OSS 的被动检查，HAProxy 能主动感知下游故障，更实时。

**容量规划（关键）**：副本数 × `cpus` ≤ 物理核数，否则 CPU 配额超订导致限流、性能异常。

| 物理核数 | 每副本 cpus | 最大副本数 | 建议副本数 |
|---------|------------|-----------|-----------|
| 8 | 4 | 2 | 2 |
| 16 | 4 | 4 | 3 |
| 32 | 4 | 8 | 4-6 |

---

## 4. 阶段2：Kubernetes 跨节点 HA

### 4.1 架构

```
client ─▶ Ingress ─▶ Service(ClusterIP) ─▶ Deployment(Replicas=N, 分布多节点)
                                              ├─ HPA(CPU 自动扩缩)
                                              ├─ RollingUpdate(滚动升级)
                                              └─ liveness/readiness 探针
```

### 4.2 核心资源（示意 YAML）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: caffe-ffi-prod
spec:
  replicas: 3
  selector:
    matchLabels: { app: caffe-ffi-prod }
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }   # 零停机升级
  template:
    metadata:
      labels: { app: caffe-ffi-prod }
    spec:
      nodeSelector: { cpu: "p-core" }                    # 亲和 P-core 节点
      containers:
      - name: caffe-ffi-prod
        image: caffe-ffi-prod:latest
        envFrom: [{ configMapRef: { name: caffe-ffi-env } }]  # OMP/BLAS 环境变量
        resources:
          requests: { cpu: "4", memory: "4Gi" }
          limits:   { cpu: "4", memory: "4Gi" }          # limits=requests 防节流
        readinessProbe:
          httpGet: { path: /health, port: 8080 }
          initialDelaySeconds: 10
        livenessProbe:
          httpGet: { path: /health, port: 8080 }
---
apiVersion: v1
kind: Service
metadata: { name: caffe-ffi-prod }
spec:
  selector: { app: caffe-ffi-prod }
  ports: [{ port: 8080, targetPort: 8080 }]
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: caffe-ffi-prod }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: caffe-ffi-prod }
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
```

### 4.3 K8s 特有注意点

- **CPU 节流**：`limits.cpu = requests.cpu`（避免 K8s quota 节流导致 OpenMP 线程调度异常）
- **环境变量**：通过 ConfigMap 注入 `OMP_NUM_THREADS`/`OPENBLAS_NUM_THREADS` 等，禁止在 Python 内 `os.environ` 覆盖
- **节点亲和**：`nodeSelector` 绑定 P-core 节点，避免调度到 E-core 节点引发性能倒退
- **多副本 OMP 线程总需求**：`副本数 × OMP_NUM_THREADS` 需 ≤ 节点 P-core 数，否则线程过订阅

---

## 5. 性能与容量规划

| 项 | 阶段1（单机） | 阶段2（K8s） |
|----|--------------|--------------|
| 单副本资源 | 4 核 / 4GB | 4 核 / 4GB |
| 单副本吞吐 | ~14-18 FPS（batch=1） | 同左 |
| 总吞吐可扩展 | 受限于单机核数 | 线性扩展至多节点 |
| 可用性 | 进程级 HA | 主机级 HA + 自动扩缩 |
| 运维复杂度 | 低（compose） | 中高（K8s） |

---

## 6. 已知限制与反模式（对抗审查结论）

| 反模式 / 风险 | 说明 | 规避 |
|--------------|------|------|
| ❌ 静态 server 条目硬编码 | 阶段1 HAProxy 显式 `server prod-1/-2/-3`，扩缩容需手改 | 固定副本数；升级阶段2用服务发现 |
| ❌ 服务未暴露 `/health` | 默认 `sleep infinity` 无监听端口，HAProxy 无法主动检查 | 真实服务必须实现 `/health` |
| ❌ CPU 配额超订 | 副本数×cpus > 物理核数 → 限流性能异常 | 按 §3.4 容量规划表 |
| ❌ 共享模型目录更新 | 多副本加载不一致窗口 | 镜像固化模型或用版本化目录原子切换 |
| ❌ 忽略 K8s CPU 节流 | `limits.cpu > requests.cpu` 触发节流 | 设 `limits=requests` |
| ❌ 线程过订阅 | 多副本 OMP 线程总和超 P-core 数 | 副本数×OMP ≤ 节点P-core数 |

---

## 7. 上线验证清单（HA）

- [ ] 阶段1：`--scale 3` 后 HAProxy 统计页 3 后端全部 UP
- [ ] 阶段1：停止一个副本，请求无中断，其余副本接管
- [ ] 阶段1：恢复副本后自动回到负载均衡（`rise 2`）
- [ ] 阶段1：容量规划满足 副本数×cpus ≤ 物理核数
- [ ] 阶段2（如启用）：Deployment 滚动升级零停机、HPA 在 CPU>70% 自动扩容
- [ ] 阶段2：`limits.cpu = requests.cpu`，ConfigMap 注入环境变量

---

> 单机单副本部署与延迟敏感配置详见 [PRODUCTION_DEPLOYMENT_MANUAL.md](PRODUCTION_DEPLOYMENT_MANUAL.md)；性能决策依据见 [deployment_config_guide.md](../deployment_config_guide.md)。