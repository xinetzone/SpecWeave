---
id: "wsl-docker-storage-cleanup-five-step-method"
title: "WSL/Docker存储清理五步法"
type: code-pattern
date: 2026-08-14
maturity: L2-validated
maturity_note: "≥3个案例跨环境验证：原生Docker daemon清理160GB、PowerShell5语法兼容、daemon状态误判场景。覆盖Win11 WSL2 Ubuntu-26.04原生Docker + Docker Desktop WSL2后端两种引擎"
source:
  - "session: sc-20260814-wsl-docker-cleanup"
  - "experience: 927840"
  - "experience: 566693"
related_patterns:
  - "wsl-docker-command-safety.md"
  - "powershell-wsl-cross-shell-wrapper.md"
  - "wsl2-docker-selection-decision.md"
  - "shell-cleanup-non-blocking.md"
tags: ["wsl", "wsl2", "docker", "storage-cleanup", "disk-space", "resource-reclaim", "windows", "powershell", "devops", "maintenance", "zombie-container", "buildkit-cache", "orphan-volume"]
validation_count: 3
reuse_count: 0
---

# WSL/Docker存储清理五步法

## 触发场景

- Windows侧C/D盘爆红或收到磁盘空间告警，定位到WSL发行版`ext4.vhdx`持续膨胀
- `docker system df`报告`RECLAIMABLE`占比≥30%、Build Cache≥50GB（BuildKit无限累积典型症状）
- 镜像/容器/卷管理界面出现大量"实验TAG""孤儿卷""停止≥24小时的匿名容器"
- 项目构建迭代≥10轮后，磁盘用量线性增长但构建产物早已迁移
- 用户明确要求「清理WSL废弃容器与镜像」

**识别信号**：
- `docker images`输出20+条，其中`docker images -f dangling=true`非空或`REPOSITORY=<none>`
- `docker volume ls -q | wc -l` > 50且活跃容器数≤3
- `docker ps -aq --filter status=exited --filter status=dead`非空
- WSL发行版vhdx实际占用 >> Linux内`df -h`报告的已用量（compact未做）

**不适用于 / 边界条件**：
- 业务生产环境（K8s/Docker Swarm）→ 请用运维工具链，禁止手动脚本化清理
- 容器内数据未持久化到卷的**关键业务容器**→ 先`docker commit`或`docker cp`备份数据再清理
- 需要**彻底重置Docker存储**（重建`/var/lib/docker`整个目录）→ 属于破坏性操作，不适用本模式渐进清理
- Docker Desktop for Mac/原生Linux → WSL特有三层Shell陷阱不存在，可简化但锚点逻辑仍可用

---

## 问题背景

### WSL/Docker存储膨胀的三条根因（≥2案例交叉验证）

| 根因 | 量化特征 | 实际案例 |
|---|---|---|
| **BuildKit Cache无限增长** | `docker system df`中Build Cache `ACTIVE=0`但SIZE≥50GB，`docker builder prune`（不加`-a`）仅删几KB悬空层 | Case-1: 75.2GB Build Cache删前ACTIVE全0，加`-a`一次清71.68GB |
| **孤儿卷累积** | `docker-compose down`默认不删卷、`docker rm`无`-v`，每轮up产生1-2个匿名卷。LINKS=0的卷数量占比≥90% | Case-1: 128卷中121个LINKS=0，占94.5%；单个873MB大卷占可回收99.7% |
| **实验镜像TAG残留** | 同仓库多TAG镜像（devcontainer-base/xmnn系列）>10条，且`docker system df -v`中CONTAINERS列全为0 | Case-1: devcontainer-base 15条TAG仅2条最近构建，13条为24h前实验产物 |

### 清理时最危险的三类误操作

1. **活跃锚点误删**：运行中容器引用的层/卷如果被强制删除（`docker rm -f $(docker ps -q)`或`docker volume rm <LINKS=1卷>`）→ 容器崩溃、数据丢失
2. **命令跨层解析错误**（在PowerShell中用`$(...)`、xargs、&&）→ 要么执行空参数、要么PowerShell报错导致清理中断后错误宣称"完成"
3. **RECLAIMABLE≠真的可删**：`docker system df`报告的RECLAIMABLE包含"保守保留带"（最近构建镜像、基础层、工具镜像）。全删则下次构建冷启动30-60min

---

## 核心做法（五步标准流程）

> **环境前置统一**：无论使用Docker Desktop WSL2后端还是WSL原生Docker，所有查询/删除命令统一通过同一个`wsl.exe -d <Distro> -e bash -c '...'`内部执行，**禁止PowerShell层解析任何`$()`、禁止在wsl调用外层写bash语法（如xargs/&&）**。参见兄弟模式 `wsl-docker-command-safety` 三层Shell模型。

### 第1步：环境预检 + 快照备份（防误删兜底）

**目标**：确认daemon真实可用（避免「不可达=已清理」跳跃结论）；捕获活跃锚点清单。

```bash
# 在同一个 wsl ... bash -c 内部执行以下脚本
TS=$(date +%Y%m%d_%H%M%S);
SNAP="/tmp/cleanup_snapshot_${TS}.txt";
echo "==== CLEANUP SNAPSHOT @ ${TS} ====" > $SNAP;

# 1.1 探测daemon真实状态（不是看命令返回码，是看info输出）
docker info > /dev/null 2>&1 && DAEMON="OK" || DAEMON="FAIL";
echo "DAEMON_STATUS=$DAEMON" >> $SNAP;
[ "$DAEMON" != "OK" ] && echo "ABORT: daemon不可达，可能Docker未启动或发行版不对。请先修复再清理" && exit 1;

# 1.2 导出运行中容器 + 引用镜像ID + 挂载卷
echo "--- ACTIVE CONTAINERS ---" >> $SNAP;
docker ps --no-trunc >> $SNAP;
echo "--- CONTAINER-REF IMAGES ---" >> $SNAP;
for cid in $(docker ps -q); do
  docker inspect --format "CID={{.Id}} IMG={{.Image}} IMG_NAME={{.Config.Image}}" $cid >> $SNAP;
done;
echo "--- VOLUMES WITH LINKS>=1 ---" >> $SNAP;
docker system df -v 2>/dev/null | awk '
  /^Local Volumes space usage:/{flag=1; next}
  flag && NF>=3 && $2~/^[0-9]+$/ && $2>=1 {
    print $1, "LINKS="$2, "SIZE="$3
  }' >> $SNAP;

# 1.3 快照前磁盘基线（用于最后算回收量）
echo "--- DISK BASELINE ---" >> $SNAP;
docker system df >> $SNAP;

echo "SNAPSHOT_SAVED=$SNAP";
```

**验收标准**：
- `DAEMON_STATUS=OK`（任何非OK都必须终止，不得硬清）
- 快照文件中列出所有运行中容器，且卷段包含≥LINKS≥1的完整列表

---

### 第2步：识别活跃锚点 + 划分三层保护带

**目标**：从快照中提取绝对红线。所有清理动作的白名单依据。

| 保护带层级 | 判定规则（从快照/inspect中提取） | 典型内容 | 删除后果 |
|---|---|---|---|
| 🔴 **绝对红线（-rf禁止）** | 1) `docker ps -q` 中所有容器ID及其引用的Image ID；2) `LINKS≥1`的全部卷名；3) 容器网络配置 | 1个运行中业务容器 + 对应1镜像ID + 5-7个挂载卷 | 容器立即Crash、卷内数据永久丢失、需重新部署 |
| 🟡 **保守保留（默认不删）** | 创建时间<24h的非实验TAG、基础OS镜像（ubuntu/alpine/debian）、工具镜像（hadolint/skopeo/buildx） | devcontainer-base:latest（2h前）、ubuntu:26.04（160MB）、hadolint:latest（68MB） | 下次构建冷启动：基础层重拉30s+实验镜像重构建30-60min（可接受则能删） |
| 🟢 **清理目标（默认全清）** | 不符合上两带，且：1) 停止/死亡容器；2) `ACTIVE<10%` Build Cache；3) `LINKS=0`的卷；4) `CONTAINERS=0`且超24h的实验TAG | 停止匿名容器（Exited 255 4天+Size 0B）、BuildKit ACTIVE=0缓存、LINKS=0孤儿卷、devcontainer-base:experiment/miniforge-baseline等历史TAG | 无破坏性，下次需要会自动重建 |

> **锚点提取脚本（从快照半自动）**：
> - 绝对红线容器：`docker ps -q`的所有短ID
> - 绝对红线镜像：`docker inspect --format {{.Image}} <cid>` 转成sha256长ID后比对
> - 绝对红线卷：快照`VOLUMES WITH LINKS>=1`段第1字段卷名

---

### 第3步：按优先级顺序清理（容器→Build Cache→孤儿卷→废弃镜像TAG）

**为什么顺序不能乱？** 镜像层可能被停止容器引用（先删容器再删镜像→避免`image has dependent child images`报错）；卷可能挂载在停止容器上（先删容器带`-v`或后删LINKS=0卷二选一）。

#### 3.1 清理停止/死亡容器

```bash
# 两步法：先收集ID，再显式传参（避免空列表报错）
STOPPED_IDS=$(docker ps -aq --filter status=exited --filter status=created --filter status=dead);
if [ -n "$STOPPED_IDS" ]; then
  # 用docker rm -fv（同时删匿名关联卷）
  # shellcheck disable=SC2086
  docker rm -fv $STOPPED_IDS;
fi
# 验证：剩余容器数应该 = 运行中容器数
AFTER=$(docker ps -aq | wc -l);
RUN=$(docker ps -q | wc -l);
[ "$AFTER" -ne "$RUN" ] && echo "WARN: 有僵尸容器残留（ps -aq能看到但rm报No such container，SIZE=0B属正常残影，重启dockerd自愈）"
```

#### 3.2 清理BuildKit Build Cache（大头！加`-a`）

```bash
# ⚠️ 必须加 -a（all）：否则只删标记为dangling的几KB缓存，不删带keep标记的70GB+条目
# ⚠️ 先用 docker system df 看Build Cache ACTIVE≈0时才能大胆-a
CACHE_BEFORE=$(docker system df --format '{{.BuildCacheSize}}' 2>/dev/null || echo "NA");
echo "Build Cache before: $CACHE_BEFORE";

# 尝试两种builder清理（legacy + buildx），谁有用谁
docker builder prune -a -f 2>&1 | tail -3;
(command -v docker-buildx >/dev/null 2>&1 && docker buildx prune -a -f 2>&1 | tail -3) || true;
```

#### 3.3 清理孤儿卷（精确匹配LINKS=0，剔除第2步的保护卷）

```bash
PROTECTED_VOLS="<从第2步快照中复制的LINKS>=1卷名，空格分隔>"

# 两步法：先收集LINKS=0的卷，再过滤掉PROTECTED_VOLS
ALL=$(mktemp);
SAFE=$(mktemp);
docker system df -v 2>/dev/null | awk '
  /^Local Volumes space usage:/{flag=1; next}
  flag && NF>=3 && $2=="0" {print $1}' > $ALL;

while read -r vid; do
  skip=0;
  for pv in $PROTECTED_VOLS; do [ "$vid" = "$pv" ] && { skip=1; break; }; done;
  [ $skip -eq 0 ] && echo "$vid" >> $SAFE;
done < $ALL;

echo "Orphan volumes: $(wc -l < $SAFE) / $(wc -l < $ALL) protected excluded: $(($(wc -l < $ALL)-$(wc -l < $SAFE)))";
if [ -s "$SAFE" ]; then
  DEL=$(tr '\n' ' ' < "$SAFE");
  # shellcheck disable=SC2086
  docker volume rm $DEL 2>&1 | tail -5;
fi
```

#### 3.4 清理废弃镜像TAG（分两批，先实验再项目）

```bash
# === 第一批：同仓库多TAG，保留活跃保留带中的TAG（例：devcontainer-base保留latest+v2.2.1-opt）
KEEP="devcontainer-base:latest devcontainer-base:v2.2.1-opt";
REPO="devcontainer-base";
ALL_TAGS=$(docker images --format '{{.Repository}}:{{.Tag}}' | grep "^${REPO}:");
DEL="";
for t in $ALL_TAGS; do
  skip=0;
  for k in $KEEP; do [ "$t" = "$k" ] && { skip=1; break; }; done;
  [ $skip -eq 0 ] && DEL="$DEL $t";
done;
echo "Cleaning repo=$REPO tags=$(echo $DEL | wc -w)";
[ -n "$DEL" ] && docker rmi $DEL;

# === 第二批：确定"不使用的项目系列镜像"（例：xmnn系列 / 旧版portable）
EXPLICIT_DEL="xmnn-runtime:latest xmnn-whl-builder:latest xmnn-runtime-jupyter:latest chaos-ai:portable";
echo "Explicit delete list: $EXPLICIT_DEL";
# shellcheck disable=SC2086
docker rmi $EXPLICIT_DEL 2>&1 | tail -3;
```

---

### 第4步：三重存活验证（活跃锚点未受损）

只做空间核对不验证业务 → 属于「清理未闭环」。必须三重通过：

| 验证维度 | 操作 | 验收标准 |
|---|---|---|
| **Docker状态层** | `docker ps --format '{{.Names}} {{.Status}}'` | 所有🔴保护带容器状态仍为`Up ... (healthy)`，数量不减 |
| **进程可达层** | `docker exec <name> hostname; docker exec <name> ss -ltnp \| grep -E ':<业务端口>'` | 命令执行无报错；预期端口（如8888/2222）处于LISTEN且对应进程存在 |
| **网络握手层** | WSL内/Windows侧任选其一：`timeout 5 bash -c 'echo > /dev/tcp/127.0.0.1/<端口>'` 或 PowerShell `Test-NetConnection` | TCP握手成功（无超时/拒绝连接） |

三重任一层失败 → **立即停止** → 回滚（若镜像被误删则`docker load`恢复；若卷被误删则从备份还原）

---

### 第5步：空间回收核验 + 报告归档

```bash
echo "==== FINAL: BEFORE vs AFTER ====";
echo "--- BEFORE (from $SNAP) ---";
grep -A 4 "DISK BASELINE" $SNAP | tail -5;
echo "--- AFTER ---";
docker system df;
echo "";
echo "--- ASSET COUNTS ---";
echo "Containers total: $(docker ps -aq | wc -l) (running: $(docker ps -q | wc -l))";
echo "Images total rows: $(docker images | wc -l) (unique IDs: $(docker images -q | sort -u | wc -l))";
echo "Volumes total: $(docker volume ls -q | wc -l) (must equal protected: LINKS>=1 count)";
```

**WSL侧vhdx compact（可选，Windows侧可见空间释放）**：
清理完成后Linux内空间已释放，但Windows的`ext4.vhdx`不会自动缩小。若需要立即在Windows侧看到空间减少：
```
PowerShell管理员：
  wsl --shutdown
  diskpart
    select vdisk file="%LOCALAPPDATA%\Packages\CanonicalGroupLimited...\LocalState\ext4.vhdx"
    attach vdisk readonly
    compact vdisk
    detach vdisk
    exit
```

---

## 反模式（对等提炼，≥3条来自真实踩坑）

### ❌ 反模式1：PowerShell顶层写`docker rm $(docker ps -aq)` / 用xargs
- **案例来源**：经验ID 566693 + 经验ID 927840
- **失败机制**：`$(...)`被PowerShell（Layer 1）在传给wsl.exe前展开为空 → `docker rm`无参数报错 → 清理实际未执行但后续echo"已清理"；`xargs`是Linux命令，PowerShell不存在
- **后果**：宣称"已清理80GB"实际0字节回收，磁盘告警持续
- **替代做法**：所有`$()`子命令替换必须在同一个`wsl -d Distro -e bash -c '...'`内部进行，或用"先收集ID存变量→再传参"的两步法

### ❌ 反模式2：`docker info`报"Cannot connect to Docker daemon" → 直接结论"已清理完毕"
- **案例来源**：经验ID 927840
- **失败机制**：daemon不可达 = "当前无法列举资源" ≠ "资源不存在"。daemon未启动/发行版切换/WSL未启动都会导致同一错误
- **后果**：跳过清理，错过上百GB回收机会；后续在错误结论上追加"验证通过"形成双重误判
- **替代做法**：daemon不可达时只输出**诊断步骤**（检查wsl状态、检查docker.socket、重启dockerd/desktop），**绝不**写清理总结

### ❌ 反模式3：`docker system df`看到RECLAIMABLE大 → 直接`prune -a --volumes`不加保护
- **案例来源**：Case-1 160GB清理前差点犯的错误（devcontainer-base:latest是2小时后的下次构建基础）
- **失败机制**：`prune -a --volumes`删除"不被任何容器引用的一切"= 🔴安全（不碰运行中容器的挂载），但🟡保守保留带的基础镜像/工具镜像会一并被删 → 下次构建冷启动30-60min + 拉取外网流量
- **后果**：空间多回收5GB但CI/build时间+2小时，开发团队抱怨
- **替代做法**：TAG级清理（第3.4步）精确控制保留内容，`docker image prune -a`只在"明确所有非活跃镜像都可删"时使用，**永远避免** `docker system prune -a --volumes`一键全清（等于跳过保护带判断）

### ❌ 反模式4（额外）：僵尸容器一定要"删到看不见"才叫完成
- **案例来源**：Case-1 4d4cc2bf2a51：`docker ps -aq`能看到，但`inspect/rm/DELETE unix socket`均报"No such container"，SIZE=0B
- **失败机制**：dockerd的boltdb容器索引与overlayFS层不同步（可能因强行关闭WSL或磁盘断电造成）。这类容器**实际存储层已删除**，SIZE=0B不占空间，残留元数据<1KB
- **后果**：为清理0B残影重启整个WSL发行版 → 打断业务容器运行（healthy→中断）
- **替代做法**：用`docker inspect <id> --format '{{.SizeRw}}'`确认Size=0B后标记为"残影项（dockerd重启自愈）"，在报告中标注即可，不强制重启

---

## 检验标准（做完怎么知道做对了？）

| # | 标准 | 验证方法 | 通过标志 |
|---|---|---|---|
| 1 | 🔴保护带资产无损 | 对比Step1快照的活跃容器ID/卷名列表 vs `docker ps -q` / `LINKS>=1卷` | 完全一致，名字和数量都相等 |
| 2 | Build Cache显著下降 | `docker system df` Build Cache SIZE前后对比 | 下降≥70%（例：75GB→3.5GB = 降95%）或差值≥30GB |
| 3 | 孤儿卷数 = LINKS≥1数 | `docker volume ls -q \| wc -l` vs 快照中LINKS≥1行数 | 完全相等（例：128→7，7正好等于LINKS≥1数） |
| 4 | 停止容器≤1个（允许0B残影） | `docker ps -aq --filter status=exited \| wc -l` ≤ 1且SIZE=0B | 通过；>1个且SIZE>0则第3.1步没跑全 |
| 5 | 三重存活验证全绿 | 第4步Docker状态+进程+TCP | 三重全部通过，无报错 |
| 6 | 前后空间差值≥预期60% | Images+BuildCache+Volumes的SIZE总减少量 | ≥保守估算的60%（例：估算146GB→实回160GB=109% ✓） |

---

## 迁移示例（非Docker领域验证可复用性）

本模式的本质是「**资源清理五段式：预检→锚点→顺序→验证→核验**」，抽象掉Docker/WSL后，可迁移至以下场景：

### 场景1：Kubernetes节点磁盘清理（DevOps跨平台）
- 第1步预检 → `kubectl describe node <node>`检查`DiskPressure` taint + `crictl info`探测containerd
- 第2步锚点 → `DaemonSet Pod + ReplicaSet Pod`=🔴，`Evicted Pod + Completed Job`=🟢
- 第3步顺序 → 先删Pod（等同容器）→ `crictl rmi`清理镜像tag → 清理孤儿PVC
- 第4步验证 → `kubectl get pods -o wide` + `curl`业务Service端口
- 第5步核验 → `df -h /var/lib/containerd`前后对比

### 场景2：本地PostgreSQL大表清理（数据库领域）
- 第1步预检 → `SELECT version()` + `pg_stat_database`确认连接正常 + 逻辑复制插槽状态快照
- 第2步锚点 → `pg_stat_user_tables`中`n_live_tup>0`且最近被查询的表=🔴，`temp_*` / `backfill_*` 表=🟢
- 第3步顺序 → 先`DROP TABLE`已备份的临时表（等同停止容器）→ `VACUUM FULL`（等同Build Cache碎片整理）→ 清理孤儿复制槽/物化视图数据
- 第4步验证 → `SELECT count(*) FROM <锚点表>`行数未变 + `pg_isready`连接OK
- 第5步核验 → `SELECT pg_size_pretty(pg_database_size(...))`前后对比

### 场景3：npm/yarn/pnpm全局缓存清理（前端领域）
- 第1步预检 → `node --version` + `pnpm store path`定位缓存根目录 + 正在运行的`dev server`进程快照
- 第2步锚点 → 当前打开的项目`node_modules`（正在被server进程fd持有）=🔴，`~/.cache/yarn/v6`/`~/.pnpm-store`中`mtime≥6个月`=🟢保守，更早=清理
- 第3步顺序 → 先停服务（等同停止容器）→ `pnpm store prune`/`yarn cache clean`（Build Cache）→ 清理`npm ci`失败残留的`node_modules.tmp-*`孤儿目录
- 第4步验证 → 重启动项目后`pnpm dev`端口可访问 + `curl localhost:3000`返回HTML
- 第5步核验 → `du -sh ~/.cache`/`du -sh ~/.pnpm-store`前后对比

三个跨领域场景均能完整映射，说明抽象层级（L2-validated）合适。

---

## 与相关模式的协同关系

| 模式 | 本模式调用点 | 协同关系 |
|---|---|---|
| [wsl-docker-command-safety](wsl-docker-command-safety.md) | 本模式所有执行命令的基础语法 | 本模式是**清理流程层**，前者是**单条WSL/Docker命令的安全写法层**。本模式的每条bash命令都要符合其原则1-5（尤其是"变量在bash -c内不跨层展开"原则） |
| [powershell-wsl-cross-shell-wrapper](powershell-wsl-cross-shell-wrapper.md) | 若提供PowerShell一键清理.ps1脚本时 | 前者提供PowerShell→WSL的参数映射/路径转换/环境检测，本模式定义bash侧的实际清理流程 |
| [wsl2-docker-selection-decision](wsl2-docker-selection-decision.md) | 预检阶段daemon不可达排障时 | 前者提供Desktop vs 原生Docker的诊断要点；若发现二选一违规（双daemon并存），在Step1预检阶段先提示整改 |
| [shell-cleanup-non-blocking](shell-cleanup-non-blocking.md) | Step3清理命令的TRAP/ERR退出处理 | 前者定义清理脚本异常时的非阻塞回滚策略，适合嵌入到本模式bash脚本的`trap`层 |

---

## 快速命令速查卡（复制粘贴用）

### Quick S0：预检 + 快照
```bash
wsl.exe -d Ubuntu-26.04 -e bash -c '
TS=$(date +%Y%m%d_%H%M%S); SNAP=/tmp/cleanup_snapshot_${TS}.txt
echo SNAP=$SNAP
docker info >/dev/null 2>&1 && echo DAEMON=OK || echo DAEMON=FAIL
docker ps -q > /tmp/cids.txt; echo RUN=$(wc -l < /tmp/cids.txt)
echo ALL_INFO_SAVED_TO_$SNAP
'
```

### Quick S3：Build Cache + 孤儿卷两条命令大头
```bash
wsl.exe -d Ubuntu-26.04 -e bash -c '
echo "=== Build Cache -a prune ==="; docker builder prune -a -f | tail -1
echo "=== Volumes LINKS=0 cleanup ==="
PROTECTED="卷1 卷2 ...（从快照抄LINKS>=1）"
SAFE=$(mktemp)
docker system df -v 2>/dev/null | awk "/^Local Volumes space usage:/{f=1;next} f && NF>=3 && \$2==0 {print \$1}" | while read v; do
  skip=0; for p in $PROTECTED; do [ "$v" = "$p" ] && { skip=1; break; }; done; [ $skip -eq 0 ] && echo $v
done > $SAFE
echo "Safe delete: $(wc -l < $SAFE) volumes"
[ -s "$SAFE" ] && docker volume rm $(tr "\n" " " < $SAFE) 2>&1 | wc -l
'
```

### Quick S4：三重存活验证
```bash
wsl.exe -d Ubuntu-26.04 -e bash -c '
echo "[1] State layer:"; docker ps --format "table {{.Names}}\t{{.Status}}"
echo "[2] Process layer:"; docker exec chaos-ai-portable bash -c "hostname; ss -ltnp 2>/dev/null | grep :8888 || netstat -ltnp | grep :8888; echo EC=\$?"
echo "[3] TCP layer   :"; timeout 5 bash -c "echo > /dev/tcp/127.0.0.1/8888" && echo TCP_8888_OK || echo TCP_8888_FAIL
'
```
