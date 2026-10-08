# CubeSandbox 架构洞察与知识地图（I 阶段产出）

> 输入：[facts.md](facts.md) 中 244 条带锚点事实（F-001 ~ F-244）。
> G2 要求：每个洞察含「陈述 / 证据 / 反常识 / 行动」四元组，证据全部回引 F 编号。

---

## 一、核心洞察（5 个四元组）

### 洞察 I-1：60ms 冷启动不是"VMM 天生快"，而是"资源池化 + 快照克隆 + 跳过 guest 引导"的系统工程

- **陈述**：CubeSandbox 的亚 60ms 冷启动路径上，三类昂贵操作全部被移出请求同步路径：①宿主资源（TAP、cgroup、存储卷）预创建成池；②rootfs 以 reflink 元数据复制获得而非数据拷贝；③VM 从模板快照恢复而非冷引导内核，应用就绪由 guest 通过 IO 端口/MMIO 直接通知。
- **证据**：
  - 性能指标：单并发 60ms、50 并发均值 67/P95 90/P99 137ms（F-001、F-002、F-009）；对比 Docker 200ms、传统 VM 秒级（F-005、F-008）。
  - 池化配置：网络插件 `tap_init_num = 500`（F-074）；cgroup 插件 `pool_size = 3000`（F-073）；存储默认池 `defaultPoolSize = 500`、`defaultPoolWorkers = 8`（F-089）。
  - 快照克隆：hypervisor 侧 `VmSnapshot` 与 `Snapshottable`（snapshot/restore/dirty_log）（F-120）；CubeCoW reflink 引擎常量 `FICLONE = 0x40049409`，克隆走 ioctl（F-203、F-206）；文件命名模式 `tpl-<snapshotID>-rootfs`、`sb-<sandboxID>-rootfs-gen<N>`（F-085）。
  - 就绪通知：cube-agent 启动后 x86_64 向 IO 端口 `0x680` 写 `0x8`、aarch64 写 MMIO `0x09030000`（F-155），宿主 VMM 无需轮询 guest 用户态。
  - 预构建资产：guest 内核 `kernel-release-260921-1`、guest 镜像 `guest-image-260820-1` 由 release-assets.yaml pin（F-028）。
- **反常识**：直觉会把 60ms 归因于 cloud-hypervisor/firecracker 这类轻量 VMM 本身；但裸 KVM 引导一个带独立内核的通用 VM 通常需数百毫秒。CubeSandbox 的快来自"启动时不做引导"——模板快照点上 envd 已在运行，克隆与恢复都是元数据级操作，VMM 只是这条流水线的最后一环。
- **行动**：
  - 复用该模式时，把"启动耗时"拆成 **资源准备 / rootfs 克隆 / guest 引导** 三段，逐段移出同步路径；
  - 评估同类沙箱系统时问三个问题：资源有没有池？克隆是不是 reflink/快照级元数据操作？就绪信号是否绕过用户态 HTTP 轮询？
  - 引用性能数字时必须附带前提（裸金属、≤32GB 规格，F-009），不能把单并发 60ms 外推到任意并发与规格。

### 洞察 I-2：MicroVM 以 containerd Shim v2 契约"伪装"成普通容器，不自建节点生态而是嵌入 containerd/kubelet 语义

- **陈述**：CubeSandbox 没有为 MicroVM 另造一套节点管理接口，而是实现 containerd-shim v2：CubeShim 把"创建一台独立内核 VM"翻译成 containerd 熟悉的 Create/Start/Exec 生命周期；Cubelet 自身则采用 kubelet 式节点代理形态（节点状态上报、gRPC、版本采集）。
- **证据**：
  - Shim 定位：CubeShim README 声明基于 containerd-shim-rs 实现 Shim v2，runtime_type `io.containerd.cube.v2`（F-158）；main 中 `shim_run::<Service>("io.containerd.cube.rs", ...)`，且 `no_reaper/no_setup_logger/no_sub_reaper = true`（F-159）。
  - 依赖版本：`containerd-shim = 0.9.0`、`containerd-shim-protos = 0.9.0`，shim 直接 path 依赖 cube-hypervisor 的 `lib_support` feature（F-161）。
  - Cubelet 侧接线：images 插件 runtime_type `io.containerd.cube.v2`、cubebox 默认 runtime `io.containerd.cube.rs`（F-076）；任务目录沿用 `io.containerd.runtime.v2.task`（F-078）；依赖 `containerd/v2 v2.2.2`（F-082）；stdout/stderr 落于 `io.containerd.runtime.v2.task/default/<id>/`（F-240）。
  - 节点代理形态：Cubelet 含 nodeStatus 上报机制（`nodeReadyGracePeriod = 120s`）与版本采集器（F-092）；鸣谢清单含 containerd-shim-rs（F-013）。
- **反常识**：直觉认为新虚拟化技术需要配套的新集群管理器与新操作模型；CubeSandbox 反其道而行——容器语义在宿主侧止于 shim，guest 内再由 cube-agent 经 ttrpc 提供第二层"容器"接口（CreateContainer/StartContainer/ExecProcess，F-156），但这层对 containerd 完全透明。
- **行动**：
  - 集成任何新运行时，优先实现 shim v2 适配，而不是改造 kubelet/上层编排；
  - 排障时须区分两层容器：宿主看到的是 shim 管理的 VM 任务，guest 内进程由 cube-agent 的 rustjail 管理，日志/exec 的链路跨两层；
  - fd 512 传 socket、coredump_filter=0x33 等 shim 约定（F-160）是契约的一部分，改动前先核对 containerd-shim 版本。

### 洞察 I-3：安全边界是三层正交结构——独立内核 + eBPF 状态网络面 + OpenResty L7 策略网关，出向流量在数据路径上被强制绕行

- **陈述**：沙箱安全不止于 VM 隔离。不可信代码的对外访问依次经过三层：①独立 guest 内核提供执行隔离；②eBPF TC 程序在宿主内核侧做端口映射、SNAT、L3/L4 策略与到网关的强制重定向；③CubeEgress（OpenResty）在 access 阶段做 L7（SNI/Host/Method/Path）裁决与审计。guest 内即使拿到 root 也无法绕过——绕过需要修改宿主 eBPF 与路由，已超出 VM 边界。
- **证据**：
  - 分层定位：对比表明确为"独立内核 + eBPF 网络隔离"（F-008）；架构页列出 `from_cube`/`from_world`/`from_envoy` 三个 eBPF 程序（F-012）。
  - eBPF 挂载点：Init 依次 attach from_envoy（cube-dev egress）、from_world（router egress / 节点网卡 ingress），AttachFilter 为 TAP 挂 from_cube ingress（F-179）；map 带 `LIBBPF_PIN_BY_NAME`  pin 到 /sys/fs/bpf（F-180、F-175）。
  - 固定网络拓扑：沙箱内地址恒为 169.254.68.6、网关 169.254.68.5（F-182、F-074），guest 默认路由唯一。
  - L7 网关：CubeEgress 以透明代理监听 192.168.0.1:8080/8443（F-185），请求经 `access_phase.decide()` 按策略裁决（F-187）；策略匹配元组 sni/host/method/path/scheme/port（F-188、F-051），审计事件落 access.jsonl（F-191）；L7 流量由 eBPF mark（0xCE010000/0xCE020000，F-178）识别。
  - 拒绝面：始终拒绝 10/8、127/8、169.254/16 等网段（F-184）；API 模型含 allowOut/denyOut/rules（F-050）。
- **反常识**：直觉认为"沙箱=VM 隔离"即安全终点，网络策略可以像普通应用一样在 guest 内配代理；CubeSandbox 的策略执行点全部放在 guest 控制不了的宿主侧，guest 内没有任何可信组件，也不依赖用户代码配合。
- **行动**：
  - 设计多租户代码执行平台，L3/L4/L7 策略必须落在 guest 之外，并保证默认路由除网关外无路可走；
  - 排查"沙箱无法访问外网"按固定顺序：eBPF map（allow_out/deny_out、port_mapping）→ CubeEgress 策略与证书 → 后端 SNAT 出口；
  - 新增协议支持时需同时改 eBPF mark/识别与 L7 策略元组，单层改动会造成语义断裂。

### 洞察 I-4：控制面与运维面分离 + Redis Stream 选主，使"自动暂停/恢复"成为平台内置原语而非用户手工操作

- **陈述**：v0.7 把生命周期管理从请求路径中抽离为独立控制器 cube-lifecycle-manager（CLM）：生命周期事件经 Redis Stream 汇聚、单实例选主消费，按 last-active 轮询自动暂停，访问到来时由 CubeProxy 经内部接口自动唤醒；同时运维能力（集群、登录、节点、仓库）从 CubeMaster 拆到独立的 CubeOps，两平面端口、权限、演进节奏全部分离。
- **证据**：
  - 运维分离：CubeMaster 配置 `cube_ops_addr = http://127.0.0.1:3010`（F-060）；CubeOps 监听 :3010，API 组含 /auth、/cluster、/agenthub、/store、/warehouse（F-216、F-217、F-219）。
  - CLM 机制：事件总线以 `cube:v1:shared:` 为前缀（EventStreamKey/LeaderLeaseKey），Stream 上限 100000（F-223）；main 中并行运行选主、消费流、last-active 轮询、清扫器（F-221）。
  - 自动唤醒：CLM 暴露 `POST /internal/resume`（25s context，F-222）；CubeProxy 配置 internal location `/_sidecar_resume` 转发该口（F-194）。
  - 状态与超时模型：五状态 running/pausing/paused/resuming/terminated（F-234）；`on_timeout` 支持 kill（默认）/pause，NEVER_TIMEOUT=-1（F-235）；集群默认 `default_timeout_insec = -1`（F-062、F-237）。
  - 跨机暂停/恢复随 S3 快照后端处于 Preview（F-006）。
- **反常识**：直觉认为"暂停省资源"只是 hypervisor 快照命令的包装；工程难点其实在控制循环——并发去重（Stream + 选主）、唤醒延迟不能进同步路径（sidecar internal resume）、暂停态资源在节点上的释放比例（F-237）都需要独立 reconciler，塞进 CubeMaster 同步链路会造成请求抖动与脑内状态不一致。
- **行动**：
  - 构建 serverless 式沙箱服务，自动暂停/恢复须备齐 **事件总线 + 选主 reconciler + 旁路唤醒入口** 三件套；
  - 运维 API 与租户 API 物理分离，缩小高权限凭据的暴露面；
  - 评估恢复失败时沿 130409（Cubelet 容量）→ 409（CubeAPI）→ WebUI 容量诊断链路定位（F-238）。

### 洞察 I-5：CubeCoW 以文件系统 reflink 为唯一克隆原语，本地后端"免账本"——索引可从文件名扫描重建；跨机才切 S3/SPDK 后端

- **陈述**：CubeCoW 本地后端不维护血缘数据库：卷/快照的身份与关系编码进文件名与目录结构，启动时扫描文件系统即可重建索引；克隆就是一次 `FICLONE` ioctl。跨机与云后端则完全换轨——cubecow S3 引擎经 UDS JSON-RPC 共封装 11 个 rcow_* 方法调用 CubeS3lvol（SPDK/DPDK NVMe/TCP target），而 C 侧实际注册 30 个不同名 rcow_* RPC（R 阶段登记的 9 个核心卷管理 RPC 为其子集，V 阶段勘误），并落 index.json。
- **证据**：
  - reflink 原语：常量 `FICLONE = 0x40049409`、`REFLINK_BLOCK_SIZE = 512`（F-203）；克隆函数直接 `ioctl(dst, FICLONE, src)`（F-206）。
  - 免账本：初始化 `probe_reflink_support` 后调 `scan_and_rebuild_index`（F-204）；命名模式 `tpl-<snapshotID>-rootfs`、`sb-<sandboxID>-rootfs-gen<N>` 携带血缘（F-085）；卷创建 `create_new(true) + set_len`（F-205）。
  - 引擎抽象：`trait Engine` 统一卷/快照方法（F-201），`BackendKind` 仅 reflink（default）/s3 两态（F-202）；库以 lib/cdylib/staticlib 三种 crate-type 同时供 Rust 与 Go/CGo 调用（F-197、F-207、F-081）。
  - S3 轨道：S3 引擎经 `/var/run/s3lvol.sock` 调 11 个 rcow_*（F-208、F-075）；C 侧注册 30 个 rcow_* RPC，其中核心卷管理 9 个（rcow_create_lvstore/lvol/snapshot/clone、resize/delete、attach/get/active_bdev，F-212，V 阶段勘误）；产物 s3lvol_tgt 为 NVMe/TCP target（F-209）。
  - S3 卷生态：支持 AWS S3/COS/R2/MinIO（F-213），s3fs 挂载引用计数、数据保留与卷前缀删除分离（F-214）。
- **反常识**：直觉认为 CoW 卷系统必然要有一个元数据库防崩溃丢血缘；reflink 后端把文件系统本身当作唯一事实源，数据库反而会引入"账本与真相不一致"的故障类别。代价是 reflink 不跨机、依赖文件系统能力，因此跨机场景必须接受另一套（SPDK + 对象存储）更重的语义。
- **行动**：
  - 需要秒级克隆大量 rootfs 时，先确认底层文件系统支持 reflink（XFS reflink/btrfs/OCFS），把元数据当账本；
  - 文档必须显式标注两后端边界：本地免账本 vs S3 外接 target，快照不跨后端通用；
  - Go 侧统一经 CGo 调 libcubecow，存储初始化 JSON 由 `BuildCowInitJSON/BuildS3CowInitJSON` 构造（F-088），禁止在应用层另造克隆路径。

---

## 二、知识地图

### 2.1 目标束结构（`jishu/containers/cubesandbox/`）

```
cubesandbox/
├── index.md                  # 束入口（frontmatter + 总 toctree，最后写）
├── log.md                    # 生成/验证日志
├── concepts/                 # 12 篇概念文档（学习主干）
│   └── index.md              # 无 frontmatter，含 toctree
├── examples/                 # 4 篇源码锚点对照式实操
│   └── index.md
└── references/               # 3 篇信源与术语（信源先行，最先写）
    └── index.md
```

### 2.2 文档分组与学习路径

| 分组 | 文档 | 覆盖 F 编号 | 学习路径位置 |
|---|---|---|---|
| **入门** | concepts/01-overview.md（定位、指标、对比） | F-001 ~ F-009 | 第 1 步 |
| **入门** | concepts/02-architecture.md（组件全景、语言栈、端口、鸣谢） | F-010 ~ F-013 | 第 2 步 |
| **入门** | concepts/03-deployment.md（环境、一键安装、systemd、Helm、PVM、资产） | F-014 ~ F-036 | 第 3 步 |
| **控制面** | concepts/04-cubeapi.md（E2B 兼容网关、路由族、模型、中间件、OpenAPI） | F-037 ~ F-059 | 第 4 步 |
| **控制面** | concepts/05-cubemaster.md（conf 全键、调度器、MySQL/Redis、CLI） | F-060 ~ F-068 | 第 5 步 |
| **控制面** | concepts/06-cubelet.md（config.toml 插件体系、工作流、存储/网络接线） | F-069 ~ F-093 | 第 6 步 |
| **数据面** | concepts/07-hypervisor.md（cube-hypervisor fork、VmmInstance/vmm、guest-init） | F-094 ~ F-140 | 第 7 步 |
| **数据面** | concepts/08-agent-shim.md（cube-agent、ttrpc 服务、rustjail、CubeShim） | F-141 ~ F-165 | 第 8 步 |
| **数据面** | concepts/09-network.md（CubeNet eBPF、map/程序、会话回收、SNAT、拓扑） | F-166 ~ F-184 | 第 9 步 |
| **数据面** | concepts/10-gateways.md（CubeEgress L7 策略、CubeProxy 路由/唤醒） | F-185 ~ F-196 | 第 10 步 |
| **数据面** | concepts/11-storage.md（CubeCoW 双后端、CubeS3lvol/SPDK、S3 卷） | F-197 ~ F-214 | 第 11 步 |
| **进阶** | concepts/12-ops-lifecycle.md（CubeOps、CLM、TemplateCenter、五状态与超时） | F-215 ~ F-225、F-234 ~ F-238、F-241 ~ F-244 | 第 12 步 |
| **进阶** | concepts/13-sdk-ecosystem.md（三端 SDK、模板、日志、版本演进） | F-226 ~ F-233、F-239 ~ F-240 | 与 12 并列 |
| **references** | references/01-source-map.md（源码地图 + v0.7.2 pin + 信源瑕疵） | 信源表 S1 ~ S5 | 随时回查 |
| **references** | references/02-anchor-index.md（244 事实按组件分组的锚点索引） | 全部锚点 | 随时回查 |
| **references** | references/03-glossary.md（术语表） | — | 随时回查 |
| **examples** | examples/01-sdk-workflow.md（Python/Go/Node 创建-执行-文件-快照） | F-226 ~ F-232、F-056 | 入门后动手 |
| **examples** | examples/02-cluster-deploy.md（单机一键 / 多节点 / K8s / 离线） | F-014 ~ F-036 | 部署时 |
| **examples** | examples/03-template-build.md（从 OCI 镜像与运行中沙箱制模板） | F-023、F-239、F-049 | 制模板时 |
| **examples** | examples/04-pause-resume-policy.md（自动暂停恢复 + 网络策略配置） | F-050 ~ F-051、F-234 ~ F-238 | 运维进阶 |

学习路径：
1. **主干（半天）**：01 → 02 → 04 → 06 → 07 → 09，建立"请求进 API、Cubelet 调度、shim 拉起 VM、eBPF 接管网络"的端到端心智模型。
2. **控制面深入**：04 → 05 → 06，对照配置文件逐键理解。
3. **数据面深入**：07 → 08 → 11，对照 Rust crate 与 Go 包结构。
4. **运维/二开**：12 → 13 → examples/04。

### 2.3 洞察与文档的交叉矩阵

| 洞察 | 主要承载文档 |
|---|---|
| I-1 池化 + 快照克隆 | 07、11、06、01 |
| I-2 Shim v2 生态嵌入 | 08、06 |
| I-3 三层安全边界 | 09、10、04 |
| I-4 运维分离与自动暂停恢复 | 12、10、13 |
| I-5 reflink 免账本 / 双后端 | 11、06 |

---

## 三、G2 自检记录

- 5 个洞察均含「陈述 / 证据 / 反常识 / 行动」四要素；证据全部回引 F 编号（F-001 ~ F-244），无新增未经登记事实。
- 知识地图覆盖全部 244 条事实：F-001~244 均在 2.2 表中至少出现一次；编号区间无断点。
- 洞察为"解释性"产出，其中因果与动因表述不回写 facts.md；R 阶段事实表保持零推测原貌。
- 待 E 阶段执行：references/ 先行（3 篇）→ concepts/ 分两批（01~07、08~13）→ examples/ 分两批（01~02、03~04）→ 各级 index.md 最后写。
