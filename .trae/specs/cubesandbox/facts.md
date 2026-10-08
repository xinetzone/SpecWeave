# CubeSandbox 源码事实登记表（R 阶段产出）

## 信源表

| 信源 ID | 内容 | 版本基准 | 本地路径 |
|---|---|---|---|
| S1 | TencentCloud/CubeSandbox 官方仓库（README、docs、deploy、configs、根 Makefile/openapi.yml） | release tag **v0.7.2**，commit `f1aaa737fb3862202b1731e0e0d844c28779f930`（2026-09-24），远程 `git@github.com:TencentCloud/CubeSandbox.git` | `external/dao/runtime/tencent/CubeSandbox` |
| S2 | hypervisor/、guest-init/（Rust） | 同 v0.7.2（block_util 为 post-release 新增，已排除） | 同上 |
| S3 | agent/、CubeShim/、cubecow/（Rust） | 同 v0.7.2 | 同上 |
| S4 | Cubelet/、CubeMaster/、CubeNet/（Go + eBPF C） | 同 v0.7.2 | 同上 |
| S5 | CubeAPI/、CubeEgress/、CubeProxy/、CubeOps/、cube-lifecycle-manager/、CubeTemplateCenter/、CubeS3lvol/、sdk/、pkgs/ | 同 v0.7.2（post-release 文件以 `git show v0.7.2:<path>` 读取） | 同上 |

> 锚点格式 `<相对路径>:<行号>`，相对路径自仓库根起算；所有事实均可按锚点回源验证。

## 主题面映射（10 面）

| 主题面 | F 编号区间 |
|---|---|
| ① 项目定位与核心指标 | F-001 ~ F-009 |
| ② 架构总览 | F-010 ~ F-013 |
| ③ 部署形态与环境要求 | F-014 ~ F-036 |
| ④ CubeAPI（E2B 兼容网关） | F-037 ~ F-059 |
| ⑤ CubeMaster（编排调度） | F-060 ~ F-068 |
| ⑥ Cubelet（节点管理） | F-069 ~ F-093 |
| ⑦ CubeHypervisor 与 guest-init | F-094 ~ F-140 |
| ⑧ CubeAgent 与 CubeShim | F-141 ~ F-165 |
| ⑨ CubeNet/eBPF 网络数据面 | F-166 ~ F-184 |
| ⑩ CubeEgress/CubeProxy 安全网关 | F-185 ~ F-196 |
| ⑪ CubeCoW 与 CubeS3lvol 存储体系 | F-197 ~ F-214 |
| ⑫ CubeOps/CLM/TemplateCenter | F-215 ~ F-225 |
| ⑬ SDK 三端与 pkgs | F-226 ~ F-233 |
| ⑭ 生命周期/模板/日志与版本演进 | F-234 ~ F-244 |

---

## ① 项目定位与核心指标

- F-001：README_zh 写明 Cube Sandbox 基于 RustVMM 与 KVM 构建，对外兼容 E2B SDK，可在 60ms 内创建硬件隔离沙箱，内存开销小于 5MB，支持单机部署与多机集群（README_zh.md:45）
- F-002：README_zh 性能注释列出单并发冷启动 60ms，50 并发场景下平均 67ms、P95 90ms、P99 137ms（README_zh.md:241）
- F-003：README_zh 写明运行环境要求为支持 KVM 的 x86_64 Linux（README_zh.md:280）
- F-004：简介页写明冷启动不到 60ms、额外内存不足 5MB，核心系统开源前在腾讯云生产环境规模化验证（docs/zh/guide/introduction.md:3）
- F-005：简介页对比表列出 Docker 容器启动 200ms、CubeSandbox 亚 60ms（docs/zh/guide/introduction.md:38）
- F-006：简介页列出"跨机暂停与恢复（Preview）"，配合 S3 快照后端（docs/zh/guide/introduction.md:19）
- F-007：Cube100 页写明项目开源 80 天内突破 10,000 GitHub Star、发布 11 个版本、近 70 位贡献者、超 560 个 commits（docs/zh/guide/cube100.md:9）
- F-008：README_zh 对比表列出 Docker 容器共享内核 Namespaces、传统 VM 独立内核、CubeSandbox 独立内核加 eBPF 网络隔离；启动速度分别为 200ms、秒级、毫秒级（<60ms）；部署密度分别为高、低、极高（单机数千实例）（README_zh.md:233-240）
- F-009：README_zh 写明启动速度项基于裸金属环境测试，内存开销项基于 ≤32GB 规格沙箱实测（README_zh.md:241）

## ② 架构总览

- F-010：架构概览页写明冷启动在 100ms 以内；控制面组件为 CubeAPI、CubeMaster、WebUI、Redis；数据面组件为 Cubelet、CubeShim、CubeHypervisor、CubeCoW、CubeVS、CubeEgress、CubeProxy（docs/zh/architecture/overview.md:11）
- F-011：README_zh 架构表列出 CubeAPI（Rust，兼容 E2B 的 REST API 网关）、CubeMaster、CubeProxy、Cubelet、CubeVS、CubeEgress、CubeHypervisor & CubeShim 七个组件条目（README_zh.md:388-397）
- F-012：架构概览页网络层表列出三个 eBPF 程序：`from_cube`（TAP TC ingress）、`from_world`（主机网卡 TC ingress）、`from_envoy`（cube-dev TC egress）（docs/zh/architecture/overview.md:166）
- F-013：README_zh 鸣谢条目列出 Cloud Hypervisor、Kata Containers、virtiofsd、containerd-shim-rs、ttrpc-rust（README_zh.md:449）

## ③ 部署形态与环境要求

- F-014：快速开始页写明部署流程共四步，无需本地构建（docs/zh/guide/quickstart.md:3）
- F-015：快速开始页写明二进制基于 Ubuntu 20.04（glibc 2.31）构建，系统 glibc 必须 ≥2.31（docs/zh/guide/quickstart.md:31）
- F-016：系统支持表列出 OpenCloudOS 9、TencentOS 4 为推荐系统，Ubuntu 20.04/22.04/24.04 已测试（docs/zh/guide/quickstart.md:35）
- F-017：快速开始页写明 `/data/cubelet` 至少需要 50GB，多模板场景建议 200GB 及以上（docs/zh/guide/quickstart.md:44）
- F-018：配置建议表列出功能体验 ≥4 核/≥8GB/≥50GB，推荐 32 核/64GB/≥200GB（docs/zh/guide/quickstart.md:57）
- F-019：在线安装命令为 `curl ... deploy/one-click/online-install.sh | CUBE_PVM_ENABLE=1 MIRROR=cn bash`（docs/zh/guide/quickstart.md:176）
- F-020：快速开始页写明跳过下载前检测的方式为环境变量 `ONE_CLICK_SKIP_PRECHECK=1` 或参数 `--skip-precheck`（docs/zh/guide/quickstart.md:181）
- F-021：安装组件清单列出 E2B 兼容 REST API 监听 3000 端口，CubeMaster/Cubelet/CubeShim 为宿主机进程，MySQL/Redis 走 Docker Compose（docs/zh/guide/quickstart.md:193）
- F-022：安装组件清单列出 CubeProxy 提供 mkcert TLS 与 CoreDNS 域名路由，域名为 `cube.app`（docs/zh/guide/quickstart.md:196）
- F-023：制作模板命令为 `cubemastercli tpl create-from-image --image ... --writable-layer-size 1G --expose-port 49999 --expose-port 49983 --probe 49999`（docs/zh/guide/quickstart.md:205）
- F-024：快速开始列出环境变量 `E2B_API_URL="http://127.0.0.1:3000"`、`E2B_API_KEY="e2b_000000"`、`SSL_CERT_FILE="/root/.local/share/mkcert/rootCA.pem"`（docs/zh/guide/quickstart.md:256）
- F-025：v0.7.2 tag 的 one-click README 列出 install.sh 为控制节点入口、install-compute.sh 为计算节点入口，安装路径固定 `/usr/local/services/cubetoolbox`（deploy/one-click/README.md:16）
- F-026：v0.7.2 tag 的 one-click README 列出 systemd 目标：控制节点 `cube-sandbox-control.target`、计算节点 `cube-sandbox-compute.target`（deploy/one-click/README.md:197）
- F-027：v0.7.2 tag 的 smoke.sh 共 18 行，主体加载 .env 后执行 `${INSTALL_PREFIX}/scripts/one-click/quickcheck.sh`（deploy/one-click/smoke.sh:17）
- F-028：release-assets.yaml pin 重资产：kernel_bm_amd64/kernel_bm_arm64/kernel_pvm 均为 `kernel-release-260921-1`，guest_image 为 `guest-image-260820-1`（deploy/release-assets.yaml:20）
- F-029：Helm Chart.yaml 写明 chart name `cube`，version 0.7.2，appVersion "0.7.2"（deploy/kubernetes/chart/Chart.yaml:5）
- F-030：根 Makefile 写明默认构建镜像 `cube-sandbox-builder:ubuntu2004`，Dockerfile 路径 docker/Dockerfile.builder（Makefile:4）
- F-031：根 Makefile 列出六个 Rust 工作区：CubeAPI、CubeShim、agent、guest-init、cubecow、hypervisor；BINARIES 列表含 agent、cube-init、cube-volume-s3、cubeapi、cubelet、cubemaster、cubeops、cubevsmapdump、shim（Makefile:50）
- F-032：下载页写明整包命名 `cube-sandbox-one-click-<版本>-<架构>.tar.gz`，架构取值 amd64/arm64，发布页在 cnb.cool/CubeSandbox/CubeSandbox/-/releases（docs/zh/guide/downloads.md:23）
- F-033：下载页列出 guest 内核 tag 示例 `kernel-release-260812-1`（vmlinux-amd64、vmlinux-pvm-amd64），guest 镜像 tag 示例 `guest-image-260820-1`（docs/zh/guide/downloads.md:54）
- F-034：deploy/pvm/pvm_setup.sh 头部列出三步：并行构建 PVM host 内核包与 guest vmlinux、确认后安装 host 包并接入 GRUB、放置 guest vmlinux 到 one-click assets 目录与运行时路径（deploy/pvm/pvm_setup.sh:6）
- F-035：一键部署后浏览器地址为 `http://<控制节点 IP>:12088`（README_zh.md:358）
- F-036：configs/ 目录含 kernel-oc9.x86_64.config、kernel-oc9.aarch64.config 与 single-node/{cubelet,cubemaster,templatecenter}.yaml（configs/single-node/cubemaster.yaml:1）

## ④ CubeAPI（E2B 兼容网关）

- F-037：CubeAPI Cargo.toml 中 package name 为 `cube-api`、version 0.1.0、edition 2021，[[bin]] name 为 `cube-api`、path src/main.rs（CubeAPI/Cargo.toml:5-12）
- F-038：main.rs 声明模块 config、constants、cubemaster、error、handlers、logging、middleware、models、openapi、routes、services、state（CubeAPI/src/main.rs:5-16）
- F-039：struct Cli 含参数 --debug、--bind（默认 0.0.0.0:3000）、--cubemaster-url（默认 http://127.0.0.1:8089）、--auth-callback-url、--worker-threads、--log-level、--log-dir、--log-prefix（默认 cube-api）、--rate-limit-per-sec（默认 100）、--instance-type（默认 cubebox）、--sandbox-domain（默认 cube.app）、--export-openapi（CubeAPI/src/main.rs:39-120）
- F-040：routes.rs 常量 DEFAULT_ROUTE_TIMEOUT 为 30s、PAUSE_RESUME_ROUTE_TIMEOUT 为 120s、SNAPSHOT_LONG_ROUTE_TIMEOUT 为 240s（CubeAPI/src/routes.rs:26-36）
- F-041：路由 GET /health、GET/POST /sandboxes、GET /v2/sandboxes，分别指向 health::health、list_sandboxes、create_sandbox、list_sandboxes_v2（CubeAPI/src/routes.rs:72-90）
- F-042：路由 GET、DELETE /sandboxes/:sandboxID，及 GET /sandboxes/:sandboxID/logs、GET /v2/sandboxes/:sandboxID/logs（CubeAPI/src/routes.rs:91-100）
- F-043：路由 PUT /sandboxes/:sandboxID/network、POST /sandboxes/:sandboxID/timeout、POST /sandboxes/:sandboxID/refreshes、GET /snapshots（CubeAPI/src/routes.rs:101-113）
- F-044：路由 POST /sandboxes/:sandboxID/pause、/resume、/connect、/snapshots、/rollback（CubeAPI/src/routes.rs:122-148）
- F-045：模板路由含 GET/POST /templates、GET /templates/compat、POST /templates/compat/:templateID/adopt-baseline、GET /templates/aliases/:alias、GET/POST/PATCH /templates/:templateID、PUT /templates/:templateID/alias、POST /templates/:templateID/builds/:buildID 及 GET 其 status、logs（CubeAPI/src/routes.rs:155-184）
- F-046：路由 DELETE /templates/:templateID；卷路由 GET/POST /volumes、GET/DELETE /volumes/:volumeID（CubeAPI/src/routes.rs:191-205）
- F-047：struct AppState 字段为 rate_limiter、http_client、services、logger、config（CubeAPI/src/state.rs:16-31）
- F-048：struct ServerConfig 字段含 bind、log_level、worker_threads、rate_limit_per_sec、cubemaster_url、instance_type、sandbox_domain、log_dir、log_prefix、auth_callback_url、cube_api_key，默认值读取 CUBE_API_BIND、CUBE_MASTER_ADDR、CUBE_API_SANDBOX_DOMAIN、CUBE_API_KEY（CubeAPI/src/config/mod.rs:8-137）
- F-049：constants.rs 常量 ENVD_VERSION_FALLBACK 为 "0.2.0"、ENVD_VERSION_ANNOTATION 为 "cube.master.components.envd.version"（CubeAPI/src/constants.rs:10-14）
- F-050：models 中 enum SandboxState 变体为 Running/Paused/Pausing，struct SandboxNetworkConfig 字段为 allowPublicTraffic、allowOut、denyOut、maskRequestHost、rules（CubeAPI/src/models/mod.rs:36-52）
- F-051：models 定义 struct EgressRule、EgressRuleMatch（字段 sni/host/method/path/scheme/port）、EgressRuleAction（allow/audit/inject）、EgressRuleInject（header/secret/format），及 struct NewSandbox、Sandbox、SandboxDetail（CubeAPI/src/models/mod.rs:182-238）
- F-052：error 中 enum AppError 变体含 NotFound、Unauthorized、BadRequest、Internal、Conflict、ServiceUnavailable{message,retry_after}、TooManyRequests、NotImplemented，type AppResult<T>（CubeAPI/src/error/mod.rs:14-85）
- F-053：logging 中含 enum LogLevel、struct LogEvent、trait Logger、type ArcLogger，及 FileLogger、MultiLogger、FilteredLogger、HttpLogger、OtlpLogger、NoopLogger（CubeAPI/src/logging/mod.rs:42-140）
- F-054：struct CubeMasterClient 含 create_sandbox、delete_sandbox、list_sandboxes、get_sandbox、set_sandbox_timeout、update_sandbox_network、create_snapshot、rollback_sandbox、list_templates 等异步方法；中间件含 unified_auth、rate_limit（CubeAPI/src/cubemaster/mod.rs:43-551）
- F-055：struct AppServices 字段为 sandboxes/snapshots/templates/volumes，常量 DENY_ALL_IPV4_CIDR 为 "0.0.0.0/0"，函数 validate_allow_out_domains_require_deny_all；SandboxService 方法含 new、list、get_sandbox、create_sandbox、kill_sandbox、pause_sandbox、resume_sandbox、connect_sandbox、get_logs、get_logs_v2、set_timeout、update_network、refresh（CubeAPI/src/services/mod.rs:16-89）
- F-056：examples Python 注释含 `os.environ["E2B_API_URL"] = "http://localhost:3000"`；examples/go client.go 向 c.baseURL+"/sandboxes" POST（CubeAPI/examples/create.py:8；CubeAPI/examples/go/client.go:91）
- F-057：v0.7.2 tag 的 openapi.yml 标注 openapi 3.1.0，title CubeAPI，描述 "E2B-compatible sandbox API server."，server 前缀 `/cubeapi/v1`（openapi.yml:5）
- F-058：v0.7.2 tag 的 openapi.yml 共 2458 行，paths 含 /health、/sandboxes、/sandboxes/{sandboxID}/pause、/resume、/rollback、/snapshots、/templates、/volumes 等 **26 条路径**（V 阶段勘误：R 阶段误记 25）（openapi.yml）
- F-059：v0.7.2 tag 的 openapi.yml 中 info.version 仍为 0.1.0（openapi.yml:11）

## ⑤ CubeMaster（编排调度）

- F-060：conf.yaml `common` 键含 http_port 8089、http_readtimeout 120、http_writetimeout 360、http_idletimeout 360、cube_ops_addr "http://127.0.0.1:3010"、sync_meta_data_interval 1s、sync_metric_data_interval 1s、collect_metric_interval 1s、default_headless_service_nodes_num 1、enable_check_com_net_id_param false（CubeMaster/conf.yaml:1-18）
- F-061：conf.yaml `log` 键含 module "cubemaster"、path "/data/log/CubeMaster-dev"、file_size 100、file_num 10、level "info"（CubeMaster/conf.yaml:20-25）
- F-062：conf.yaml `cubelet_conf` 键含 grpc_port 9999、common_timeout_insec 30、create_image_timeout_insec 300、app_snapshot_timeout_insec 300、default_timeout_insec -1、create_timeout_insec 600、create_concurrent_limit 100、destroy_concurent_limit 100、enable_exposed_port true、exposed_port_list ["80"]、disable_redis_proxy_port true（CubeMaster/conf.yaml:27-42）
- F-063：conf.yaml 含 `auth: enable: false`；`req_template_conf` 含 whitelist_req_tag（键 WorkingDir、RLimit、DnsConfig、HostAliases、Poststop、Prestop）与 JSON 字符串 cube_box_req_template，其中含 network_type "tap"、TZ "Asia/Shanghai" 及 denyOut 四条 CIDR（CubeMaster/conf.yaml:44-56）
- F-064：conf.yaml `instance_db_config` 键含 addr "127.0.0.1:3306"、user "cube"、pwd "cube_pass"、db_name "cube_mvp"、conn_timeout 5、max_idle_conns 5、max_open_conns 20、max_conn_life_time_seconds 300（CubeMaster/conf.yaml:58-68）
- F-065：conf.yaml `redis` 键含 nodes "127.0.0.1:6379"、password "ceuhvu123"、db_no 0、max_idle 8、max_active 32、idle_timeout 30、max_retry 2、node_metric_ttl_sec 600、sandbox_proxy_ttl_sec 0（CubeMaster/conf.yaml:70-80）
- F-066：conf.yaml `scheduler` 键含 priority_select_num 1、metric_update_timeout 300s、local_metric_update_timeout 300s、ignore_redis_allocation false，filter.enable_filters 含 cpu、mem、template_locality、realtime_create_num（CubeMaster/conf.yaml:82-98）
- F-067：CubeMaster Makefile 含 APPS=cubemaster cubemastercli、PKG=github.com/tencentcloud/CubeSandbox/CubeMaster/pkg/base、ENVD_EMBED_ASSET 路径、ELF magic 校验 7f454c46、大小上限 16777216；go.mod（go 1.25.7）require 含 gomonkey/v2、gin、pgx/v5、goose/v3、gorm、urfave/cli、k8s.io/api（CubeMaster/Makefile:17-145；CubeMaster/go.mod:1-50）
- F-068：configs/single-node/cubemaster.yaml 写明 http_port 8089、grpc_port 9999、default_timeout_insec -1、create_timeout_insec 600、create_concurrent_limit 100、数据库 driver 默认 mysql（configs/single-node/cubemaster.yaml:48）

## ⑥ Cubelet（节点管理）

- F-069：Cubelet go.mod 声明 module `github.com/tencentcloud/CubeSandbox/Cubelet`，版本指令 go 1.25.7（Cubelet/go.mod:1-3）
- F-070：config.toml 顶层键含 oom_score 0、root "/data/cubelet/root"、state "/data/cubelet/state"、version 3、pid_file "/run/cube-let.pid"、dynamic_config_path "/usr/local/services/cubetoolbox/Cubelet/dynamicconf/conf.yaml"（Cubelet/config/config.toml:1-8）
- F-071：config.toml 含 [http] address ":9998"、[grpc] address "/data/cubelet/cubelet.sock"、tcp_address ":9999"、max_recv_message_size 16777216、[cubetap] address "/data/cubelet/cubetap.sock"、[operation_server] disable true、[debug] address ":9966"、[cubelog] path "/data/log/Cubelet"、file_size "500m"（Cubelet/config/config.toml:10-40）
- F-072：config.toml 含插件 ID `io.cubelet.controller.config.v1.cubelet`，其键含 node_status_update_frequency "1s"、cubeops_addr ""、cubeops_timeout "10m"（Cubelet/config/config.toml:42-47）
- F-073：config.toml 含插件 ID `io.cubelet.internal.v1.cgroup`，其键含 pool_size 3000、pool_workers 1、vm_memory_overhead_base "42Mi"、vm_memory_overhead_coefficient 64、host_cpu_overhead "0.3"（Cubelet/config/config.toml:58-65）
- F-074：config.toml 含插件 ID `io.cubelet.internal.v1.network`，其键含 eth_name "eth0"、tap_init_num 500、cidr "192.168.0.0/18"、mvm_inner_ip "169.254.68.6"、mvm_mac_addr "20:90:6f:fc:fc:fc"、mvm_gw_mac_addr "20:90:6f:cf:cf:cf"、mvm_gw_dest_ip "169.254.68.5"、mvm_mtu 1500、cube_router_enable false、stream_name_prefix "gw_route:update:"、stream_key "gw_key"（Cubelet/config/config.toml:78-101）
- F-075：config.toml 含插件 ID `io.cubelet.internal.v1.storage`，其键含 storage_backend "cubecow"、data_path "/data/cubelet/storage"、volume_plugin_base_dir "/data/cube-shared/volume"，volume_plugins 含 name s3、name cos（两者 type "binary"），[cow.s3] 段含 enable false、socket_path "/var/run/s3lvol.sock"（Cubelet/config/config.toml:102-135）
- F-076：config.toml 含插件 ID `io.cubelet.internal.v1.images`（runtime_type "io.containerd.cube.v2"）与 `io.cubelet.internal.v1.cubebox`（default_runtime_name "cube"，runtimes.cube runtime_type "io.containerd.cube.rs"，runtimes.runc runtime_type "io.containerd.runc.v2"）（Cubelet/config/config.toml:148-157）
- F-077：config.toml 含插件 ID `io.cubelet.workflow.v1.workflow`，flows 含 init、create、destroy、cleanup，create 与 destroy 含 concurrent 100，actions 名含 cubebox、images、storage、cgroup、network、volume、netfile、cube-sandbox-store、cleanup、createid、appsnapshot（Cubelet/config/config.toml:172-183）
- F-078：config.toml 含 `io.containerd.runtime.v2.task` 的 platforms ["linux/amd64","linux/arm64"]、`io.cubelet.chi.v1.vsocket-manager` 的 proxyPort 1032、`io.containerd.cri.v1.images` 下 docker.io mirror endpoint "https://mirror.ccs.tencentyun.com"（Cubelet/config/config.toml:207-218）
- F-079：plugin.conf 含 [meta] name "Cubelet"、type 2，start_cmd 字符串含 `-c /usr/local/services/cubetoolbox/Cubelet/config/config.toml --dynamic-conf-path`，另有 plugin_health_check "@cubelet"、is_fork true、pid_file "/run/cube-let.pid"、start_secs 180、run_start "yes"（Cubelet/config/plugin.conf:1-28）
- F-080：Cubelet Makefile 含 APPS=cubelet cubecli、PROTO=services/cubehost services/multimetadb services/nbi services/version、CONF_VERSION 1.1.7、PKG=github.com/tencentcloud/CubeSandbox/Cubelet/pkg，BUILD_FLAGS 经 -ldflags -X 注入 Version/Commit/BuildTime（Cubelet/Makefile:1-62）
- F-081：Cubelet Dockerfile builder 阶段 ARG CUBE_BUILDER_IMAGE=ghcr.io/tencentcloud/cubesandbox-builder:ubuntu2004，`cargo build --release -p cubecow` 产出 libcubecow.a 并安装至 third_party/cubecow/lib/；运行时阶段 FROM ubuntu:22.04，ENV 含 IMAGE_ROOT=/opt/cube-image、TOOLBOX_ROOT=/usr/local/services/cubetoolbox，EXPOSE 9999 9998 9966（Cubelet/Dockerfile:17-157）
- F-082：Cubelet go.mod require 含 cilium/ebpf v0.17.3、containerd/v2 v2.2.2、cgroups/v3 v3.1.2、redis/go-redis/v9 v9.7.0、vishvananda/netlink v1.3.1、k8s.io/kubernetes v1.34.1、urfave/cli/v2 v2.27.7（Cubelet/go.mod:5-207）
- F-083：Cubelet go.mod replace 含 grpc => v1.67.1、k8s.io/cri-api => v0.25.16、CubeNet/cubevs => ../CubeNet/cubevs、pkgs/CubeLog => ../pkgs/CubeLog、pkgs/proto => ../pkgs/proto（Cubelet/go.mod:209-219）
- F-084：pkg/cdp/types.go 含 type DeleteOption（字段 ID、ResourceType、ResourceOrigin、SkipDeleteFlagCheck）与 type DeleteProtectionHook interface（方法 Name、PreDelete、PostDelete）（Cubelet/pkg/cdp/types.go:11-25）
- F-085：pkg/cubecow/doc.go 包注释含标识符 cubecow_last_error()、Init、InitWithoutLogging、InitFromJSON、CowError（字段 SemanticCode、Action）与字符串模式 `tpl-<snapshotID>-rootfs`、`sb-<sandboxID>-rootfs-gen<N>`（Cubelet/pkg/cubecow/doc.go:5-44）
- F-086：pkg/numa/local.go 含 type NumaInfo、type NumaNode（字段 NodeId、Cpulist、CpulistOrigin、Cores），函数 GetNumaInfo、GetMaxNumaNodeId、GetNumaNodeCount、GetAllNumaNodes，读取路径 /sys/devices/system/node/ 及文件 cpulist（Cubelet/pkg/numa/local.go:24-130）
- F-087：services/gc/gc.go 含 type GCConfig（toml 键 root_path）、bucketName "sandbox/v1"、DbName "gcservice"，init 注册 ID constants.GCID.ID；Init 方法含 mount 类型 tmpfs、source none、选项 size=100m，数据库文件名 meta.db（Cubelet/services/gc/gc.go:35-138）
- F-088：storage/plugin.go 含常量 StorageBackendCow "cubecow"、cowBackendReflink "reflink"、cowBackendS3 "s3"、defaultVolumePluginBaseDir、defaultS3SocketPath，变量 reflinkExt4InitCommands（mkfs.ext4、mount、umount、losetup），函数 BuildCowInitJSON、BuildS3CowInitJSON、PrepareCowInlineConfig、initCowEngineWithConfig、initS3CowEngineWithConfig、initVolumePlugins（Cubelet/storage/plugin.go:39-593）
- F-089：storage/local.go 含 type local（字段 cowEngine、s3CowEngine、cowManager、rcDB *bolt.DB、rcStore、poolFormat），变量 defaultPoolSize 500、defaultPoolWorkers 8、defaultFormatSize "1Gi"、defaultDiskUUID "ef5c2893-ddbd-4d6e-bef6-3853c31d5b94"、bucketName "emptydir/v1"、nfsBucketName "nfs/v1"、baseFileName "base.raw"（Cubelet/storage/local.go:52-148）
- F-090：storage hostdir.go 含 hostDirBasePath "/data/cubelet/hostdir"、type HostDirBackendInfo（json 标签 volume_name、share_dir、bind_path、read_only）；s3_init.go 含 s3InitRetryInterval 5s、ErrS3NotReady；pool.go 含 poolType、cp_type "copy"、cp_reflink_type "copy_reflink"（Cubelet/storage/hostdir.go:25-41；Cubelet/storage/s3_init.go:18-26；Cubelet/storage/pool.go:30-34）
- F-091：network/plugin.go 含 type delegateNetworkManager（字段 tapPlugin、db、allocationStore）、常量 DBBucketNetwork "network/v1"，init 注册 ID constants.NetworkID.ID()（Cubelet/network/plugin.go:34-88）
- F-092：pkg/cubelet/cubelet.go 含常量 nodeReadyGracePeriod 120s、nodeStatusUpdateRetry 5、type KubeletConfig、type Cubelet（字段 masterClient、SetNodeStatusFuncs、controllerMap、versionCollector）；versioninfo/collector.go 含 Source 常量 SourceManifest/SourceBinary/SourceFile/SourceComponentJSON，组件常量 ComponentCubelet/ComponentCubeAgent/ComponentGuestImage/ComponentKernel/ComponentCubeEgress，文件名字符串 release-manifest.json、version.json、cube-image/version、cube-agent/version、cube-kernel-scf/vmlinux（Cubelet/pkg/cubelet/cubelet.go:35-121；Cubelet/pkg/cubelet/versioninfo/collector.go:35-62）
- F-093：pkg/utils/cloud.go 含常量 localInstanceType "cubebox"、type HostIdentity、环境变量名 CUBE_SANDBOX_NODE_ID/CUBE_SANDBOX_NODE_IP/CUBE_SANDBOX_ENDPOINT_IP、路径 /proc/net/route；bdf.go 含正则与函数 ValidateBDF（Cubelet/pkg/utils/cloud.go:18-200；Cubelet/pkg/utils/bdf.go:10-14）

## ⑦ CubeHypervisor 与 guest-init

- F-094：hypervisor Cargo.toml [package] name "cube-hypervisor"、version 28.0.0、authors ["The Cloud Hypervisor Authors"]、edition 2021（hypervisor/Cargo.toml:2-5）
- F-095：同文件含 default-run "cube-hypervisor"、build "build.rs"、rust-version 1.77.0、description "Open source Virtual Machine Monitor (VMM) that runs on top of KVM"、homepage 指向 cloud-hypervisor GitHub；[profile.release] 含 codegen-units 1、lto true、opt-level "s"（hypervisor/Cargo.toml:6-18）
- F-096：hypervisor Cargo.toml [dependencies] 含 anyhow 1.0.86、clap 4.4.7、epoll 4.3.1、libc 0.2.137、rlimit 0.9.1、seccompiler 0.3.0、slog、thiserror、vmm-sys-util 0.12.1（hypervisor/Cargo.toml:20-47）
- F-097：hypervisor Cargo.toml [features] 含 default ["kvm"]、guest_debug ["vmm/guest_debug"]、kvm ["vmm/kvm"]、lib_support、mshv、tdx ["vmm/tdx"]、tracing（hypervisor/Cargo.toml:62-70）
- F-098：hypervisor Cargo.toml [workspace] members 枚举 29 个成员（v0.7.2 tag blob；V 阶段勘误：R 阶段曾误记 28、名单漏 block_util）：api_client、arch、block_util、devices、event_monitor、event_notifier、hypervisor、logging、net_gen、net_util、option_parser、pci、performance-metrics、qcow、serial_buffer、test_infra、tracer、vfio_user、vhdx、vhost_user_block、vhost_user_net、virtio-devices、vm-allocator、vm-device、vm-migration、vm-virtio、vmm、rate_limiter、virtiofsd（v0.7.2 tag hypervisor/Cargo.toml）
- F-099：hypervisor Cargo.toml [workspace.dependencies] 含 linux-loader 0.13.0、seccompiler 0.3.0、serde 1.0.208、virtio-bindings 0.1.0、virtio-queue 0.14.0、vm-memory 0.16.1、vmm-sys-util 0.12.1；vfio-ioctls 取 git rust-vmm/vfio rev 64171f3，vhost-user-backend 取 rev d983ae0（hypervisor/Cargo.toml:105-117）
- F-100：hypervisor src/lib.rs 声明 mod common、pub mod vmm_config，pub use vmm::api::*、vmm::config、vmm::seccomp_filters::*、vmm::vm_config、vmm::{SnapshotConfig,SnapshotType}；含 #[derive(Debug,Error)] pub enum Error，变体含 ReviverChannel、StartVmm、CreateHypervisor、VmmThread 等（hypervisor/src/lib.rs:1-64）
- F-101：pub struct VmmInstance 字段 vmm_thread；impl 含 new(vmm_config: VmmConfig)、send_request(request: ApiRequest)、join、join_timeout；impl Drop 调 ApiRequest::VmmShutdown，失败分支 thread.kill(SIGTERM)（hypervisor/src/lib.rs:69-349）
- F-102：main.rs fn create_app -> Command：Command::new("cube-hypervisor")、about "Launch a cloud-hypervisor VMM."，含 ArgGroup "vm-config"、"vmm-config"、"logging"（hypervisor/src/main.rs:104-113）
- F-103：create_app 注册 vm-config 参数 --cpus、--platform、--memory、--memory-zone、--firmware、--kernel、--initramfs、--cmdline、--disk、--net、--rng、--balloon、--fs、--pmem、--serial（默认 null）、--console（默认 tty）、--device、--user-device、--vdpa、--vsock、--numa、--watchdog、--sys-ctrl（hypervisor/src/main.rs:114-337）
- F-104：create_app 注册 logging 参数 -v（ArgAction::Count）、--log-file、--sandbox-id、--log-stderr；-v 计数 0/1/2/_ 分支对应 Warn/Info/Debug/Trace（hypervisor/src/main.rs:301-452）
- F-105：create_app 另注册 --api-socket、--event-monitor、--restore、--tpm、--coredump、--pvpanic、--ivshmem；x86_64 下注册 --sgx-epc；guest_debug feature 下注册 --gdb；-D/--snapshot-version 为 exclusive SetTrue（hypervisor/src/main.rs:339-422）
- F-106：--seccomp num_args 1、value_parser ["true","false","log","process"]、默认 process；匹配分支构造 SeccompAction::Trap/Allow/Log/KillProcess（hypervisor/src/main.rs:359-644）
- F-107：start_vmm 开头创建 AF_UNIX socket 并 dup2 到 512；变量 payload_present 判定含 kernel 或 firmware，该分支依次执行 VmConfig::parse、vm_create、vm_boot；--restore 分支执行 vm_restore（hypervisor/src/main.rs:439-734）
- F-108：src/common.rs 含常量 DEFAULT_LOG_FILE "/data/log/CubeVmm/vmm.log"、DEFAULT_LOG_JSON_FILE、DEFAULT_LOGGER_BUFFER_SIZE 100；函数 default_coredump_filter 返回 "0x33"、default_coredump_limit 返回 2*1024^3（hypervisor/src/common.rs:15-29）
- F-109：common.rs pub struct Logger 字段含 output、sandbox_id、buffer、vcpu_started；impl log::Log 的 log 格式串为 "{} --- {:?} --- {} --- <{}> {}:{} -- {}\n"（hypervisor/src/common.rs:36-252）
- F-110：vmm crate name "vmm" version 0.1.0；[features] 含 guest_debug、kvm、tdx；[dependencies] 含 gdbstub 0.6.3、micro_http（git firecracker-microvm/micro-http）、tokio 1.40.0（features full）、virtio-queue 0.11.0、linux-loader（features elf/bzimage/pe）、zerocopy 0.6.1（hypervisor/vmm/Cargo.toml:1-65）
- F-111：vmm/src/lib.rs 声明模块 acpi、api、clone3、config、coredump、cpu、device_manager、device_tree、gdb、interrupt、memory_manager、migration、seccomp_filters、serial_manager、vm、vm_config；pub enum EpollDispatch 含 Exit、Reset、Api、ActivateVirtioDevices、Debug、LogReopen；常量 LOG_REOPEN_INTERVAL 60 分钟（hypervisor/vmm/src/lib.rs:69-228）
- F-112：vmm/src/lib.rs pub fn start_vmm_thread 参数含 vmm_version、http_path、http_fd、api_event、api_receiver、res_sender、seccomp_action、hypervisor: Arc<dyn hypervisor::Hypervisor>、sandbox_id、vcpu_started（hypervisor/vmm/src/lib.rs:340-355）
- F-113：start_vmm_thread 内先 get_seccomp_filter（Thread::All）并 apply_filter，再 spawn 名为 "vmm" 的线程，闭包内 apply Thread::Vmm filter、构造 Vmm::new 并进入 control_loop；HTTP 分支启动 start_http_path_thread 或 start_http_fd_thread（hypervisor/vmm/src/lib.rs:367-422）
- F-114：pub struct Vmm 字段含 epoll、exit_evt/reset_evt/api_evt、version、vm: Option<Vm>、vm_config、seccomp_action、hypervisor、signals、threads、sandbox_id、vcpu_started；HANDLED_SIGNALS 为 [SIGTERM,SIGINT]；方法含 vm_create/vm_boot/vm_pause/vm_snapshot/vm_restore/vm_shutdown/vm_reboot/vm_info/vm_resize/vm_add_device/vm_add_disk（hypervisor/vmm/src/lib.rs:449-1094）
- F-115：vmm/src/vm.rs pub enum VmState { Created,Running,Shutdown,Paused,BreakPoint }；impl valid_transition 匹配五状态合法转移分支（hypervisor/vmm/src/vm.rs:324-368）
- F-116：struct VmOpsHandler 字段含 memory: GuestMemoryAtomic、io_bus、mmio_bus、pci_config_io；impl VmOps 方法含 guest_mem_write、guest_mem_read、mmio_read、mmio_write、pio_read、pio_write（hypervisor/vmm/src/vm.rs:370-461）
- F-117：pub fn physical_bits(max_phys_bits, hypervisor_type) 中 KvmPvm 分支 guest_phys_bits 取 min(max_phys_bits, 43)，末尾 min(host_phys_bits, guest_phys_bits)（hypervisor/vmm/src/vm.rs:463-478）
- F-118：pub struct Vm 字段含 initramfs: Option<File>、threads、device_manager、config: Arc<Mutex<VmConfig>>、state: RwLock<VmState>、cpu_manager、memory_manager、vm: Arc<dyn hypervisor::Vm>、numa_nodes、seccomp_action、exit_evt、hypervisor、load_payload_handle（hypervisor/vmm/src/vm.rs:480-503）
- F-119：impl Vm 方法含 boot、shutdown、resize、resize_zone、add_device、add_user_device、remove_device、add_disk、add_fs、add_pmem、add_net、add_vdpa、add_vsock、counters、balloon_size、power_button、debug_request；HANDLED_SIGNALS 为 [SIGWINCH]（hypervisor/vmm/src/vm.rs:506-2488）
- F-120：#[derive(Serialize,Deserialize)] pub struct VmSnapshot 字段含 clock: Option<ClockData>、common_cpuid: Vec<CpuIdEntry>；常量 VM_SNAPSHOT_ID "vm"；impl Snapshottable 含 snapshot/restore/start_dirty_log/dirty_log/start_migration/complete_migration（hypervisor/vmm/src/vm.rs:2648-2926）
- F-121：vmm/src/cpu.rs 常量 CPU_MANAGER_ACPI_SIZE 0xc；结构体含 LocalApic、Ioapic、GicC、GicD、GicR、ProcessorHierarchyNode、InterruptSourceOverride（hypervisor/vmm/src/cpu.rs:102-303）
- F-122：pub struct Vcpu 字段含 vcpu: Arc<dyn hypervisor::Vcpu>、id、saved_state、tsc_msrs；impl 含 new(id, vm, vm_ops)、configure、run -> Result<VmExit>；impl Snapshottable 含 snapshot/restore（hypervisor/vmm/src/cpu.rs:324-518）
- F-123：aarch64 pub fn init 中 kvi.features 依次置 KVM_ARM_VCPU_PSCI_0_2、id>0 时 KVM_ARM_VCPU_POWER_OFF、KVM_ARM_VCPU_PMU_V3，报错分支 should_retry_without_pmu 重试时去掉 PMU_V3（hypervisor/vmm/src/cpu.rs:419-452）
- F-124：pub struct CpuManager 字段含 hypervisor_type、config: CpusConfig、interrupt_controller、vm_memory、cpuid、vm、vcpus_kill_signalled、vcpus、seccomp_action、vm_ops；常量 CPU_ENABLE_FLAG 0、CPU_INSERTING_FLAG 1、CPU_REMOVING_FLAG 2、CPU_EJECT_FLAG 3；方法含 new、create_boot_vcpus、start_boot_vcpus、resize(desired_vcpus)、shutdown、create_madt、create_pptt（hypervisor/vmm/src/cpu.rs:520-1475）
- F-125：vmm/src/gdb.rs pub enum DebuggableError；pub trait Debuggable: Pausable 含 set_guest_debug、debug_pause、read_regs、write_regs、read_mem、write_mem、active_vcpus；含 GdbRequest/GdbRequestPayload/GdbResponsePayload 类型（hypervisor/vmm/src/gdb.rs:42-122）
- F-126：pub struct GdbStub 字段含 gdb_sender、gdb_event、vm_event、hw_breakpoints、single_step；impl Target（Arch=GdbArch）、MultiThreadBase、Breakpoints、HwBreakpoint；含 pub fn gdb_thread(gdbstub, path)（hypervisor/vmm/src/gdb.rs:124-495）
- F-127：arch crate name "arch"，authors ["The Chromium OS Authors"]；pub enum RegionType { Ram,SubRegion,Reserved }；lib.rs 导出 arch_memory_regions、configure_system、configure_vcpu、get_host_cpu_phys_bits、initramfs_load_addr、layout、EntryPoint，x86_64 另含 generate_common_cpuid、CpuidFeatureEntry，aarch64 另含 fdt::DeviceInfoForFdt（hypervisor/arch/src/lib.rs:54-91）
- F-128：arch lib.rs pub struct NumaNode 字段含 memory_regions、hotplug_regions、cpus、distances、memory_zones、sgx_epc_sections；pub type NumaNodes=BTreeMap<u32,NumaNode>；pub struct InitramfsConfig { address, size }；pub enum DeviceType { Virtio(u32),Serial,Rtc,Gpio }；pub const PAGE_SIZE 4096（hypervisor/arch/src/lib.rs:101-139）
- F-129：pci crate name "pci"，features kvm=["vfio-ioctls/kvm"]；deps 含 vfio-ioctls rev 64171f3、vfio-bindings 0.3.1、vm-allocator、vm-migration；lib.rs 模块含 bus/configuration/device/msi/msix/vfio/vfio_user；pub enum PciInterruptPin { IntA,IntB,IntC,IntD }；x86_64 常量 PCI_CONFIG_IO_PORT 0xcf8；pub struct PciBdf(u32)（hypervisor/pci/Cargo.toml:1-30；hypervisor/pci/src/lib.rs:9-177）
- F-130：pci/bus.rs 常量 VENDOR_ID_INTEL 0x8086、DEVICE_ID_INTEL_VIRT_PCIE_HOST 0x0d57、NUM_DEVICE_IDS 32；含 PciRoot、PciBus（字段 devices、device_ids）、PciConfigIo、PciConfigMmio 类型（hypervisor/pci/src/bus.rs:17-470）
- F-131：pci/msi.rs 常量 MSI_CTL_ENABLE 0x1、MSI_CTL_64_BITS 0x80；含 MsiCap、MsiConfig 类型；msix.rs 常量 MAX_MSIX_VECTORS_PER_DEVICE 2048、MSIX_TABLE_ENTRY_SIZE 16、FUNCTION_MASK_BIT 14、MSIX_ENABLE_BIT 15；含 MsixTableEntry、MsixConfig 类型（hypervisor/pci/src/msi.rs:18-178；hypervisor/pci/src/msix.rs:19-101）
- F-132：pci/vfio.rs 含 struct UserMemoryRegion { slot,start,size,host_addr }、struct MmioRegion、enum VfioError、trait Vfio、struct VfioPciDevice（字段 id、vm、device、container、iommu_attached、memory_slot）（hypervisor/pci/src/vfio.rs:37-1217）
- F-133：qcow crate name "qcow" license BSD-3-Clause，[lib] path src/qcow.rs；常量 QCOW_MAGIC 0x5146_49fb、DEFAULT_CLUSTER_BITS 16、MAX_QCOW_FILE_SIZE 1<<44；pub struct QcowHeader 含 magic/version/backing_file_offset/cluster_bits/size/l1_size/refcount_table_offset/nb_snapshots/header_size 等 19 字段；含 QcowFile、convert、detect_image_type、ImageType { Raw,Qcow2 }（hypervisor/qcow/Cargo.toml:1-16；hypervisor/qcow/src/qcow.rs:32-1702）
- F-134：vhdx/src/lib.rs 含 pub mod vhdx 及模块 vhdx_bat/vhdx_header/vhdx_io/vhdx_metadata；vhdx.rs enum VhdxError { NotVhdx,ParseVhdxHeader,ReadFailed,WriteFailed }；pub struct Vhdx 含 new(file)、virtual_disk_size() 并 impl Read（hypervisor/vhdx/src/lib.rs:8-30；hypervisor/vhdx/src/vhdx.rs:17-88）
- F-135：tpm/src/lib.rs 声明 pub mod emulator、pub mod socket；常量 TPM_CRB_BUFFER_MAX 3968；pub enum Commands 含 CmdGetCapability/CmdInit/CmdShutdown/CmdGetStateBlob/CmdSetStateBlob 等 17 变体；pub trait Ptm 含 ptm_to_request/update_ptm_with_response（hypervisor/tpm/src/lib.rs:9-315）
- F-136：hypervisor docs 中 api.md 写默认 socket 路径 "/run/user/{user ID}/cloud-hypervisor.{pid}"，endpoints 含 /vmm.ping、/vmm.shutdown；vsock.md 写 virtio-vsock based on the Firecracker implementation，CID 表 -1 Random/0 Hypervisor/1 Loopback/2 Host；README.md 含 "Differences with Firecracker and crosvm" 章节（hypervisor/docs/api.md；hypervisor/docs/vsock.md:5；hypervisor/README.md:29-312）
- F-137：guest-init Cargo.toml crate name "cube-init" version 0.1.0，bin cube-init path src/main.rs；deps anyhow、lazy_static 1.4、libc 0.2、nix 0.26（guest-init/Cargo.toml:1-17）
- F-138：guest-init main.rs 常量 PMEM_DEV "/dev/pmem1"、CUBE_AGENT "/run/support/cube-agent"；fn main 依次校验 process::id()==1、调用 init_env::init、mount_pmem()、start_agent()；mount_pmem 挂载参数含 fstype ext4、flags MS_RDONLY、options "dax"（guest-init/src/main.rs:28-70）
- F-139：guest-init init_env.rs struct InitMount 字段 fstype/src/dest/flags/options；CGROUPS HashMap 登记 cpu/cpuacct/blkio/cpuset/memory/devices/freezer/net_cls/perf_event/net_prio/hugetlb/pids/rdma 共 13 条 v1 挂载路径；INIT_ROOTFS_MOUNTS 含 proc→/proc、sysfs→/sys、tmpfs→/dev/shm、devpts→/dev/pts、tmpfs→/run（guest-init/src/init_env.rs:23-304）
- F-140：init_env.rs pub fn init 依次调用 mount_sys、read_unified_cgroup_hierarchy("/proc/cmdline")、mount_cgroup、enable_rc_local、init_env；unified 分支 get_cgroup_mounts 返回 fstype "cgroup2" 单条 InitMount；mount_sys 末尾 env::set_var("wrapper_mode","on")（guest-init/src/init_env.rs:23-304）

## ⑧ CubeAgent 与 CubeShim

- F-141：agent Cargo.toml package name `cube-agent` version 0.1.0，bin cube-agent 对应 src/main.rs；依赖含 ttrpc 0.8.4（features async）、tokio 1.45.1（full）、tokio-vsock 0.7.2（agent/Cargo.toml:2-34；agent/Cargo.toml:97-99）
- F-142：agent Cargo.toml workspace members 为 ["rustjail","cube"]，features 含 seccomp、standard-oci-runtime（agent/Cargo.toml:86-95）
- F-143：agent Makefile 含 PROJECT_COMPONENT cube-agent、SECCOMP yes、MUSL yes（agent/Makefile:8-53）
- F-144：main.rs 常量 NAME "cube-agent"、ENV_WRAPPER_MODE_K "wrapper_mode"；enum SubCommand 含 Init{}、Exec{} 两个变体（agent/src/main.rs:84-113）
- F-145：Init 分支调用 rustjail::container::init_child()，Exec 分支调用 cube::rootfs::do_exec_mount()（agent/src/main.rs:300-305）
- F-146：start_sandbox 内依次调用 rpc::start、start_passfd_listener、rpc::notify_vsock_server_ready，结束处调用 libc::reboot(LINUX_REBOOT_CMD_POWER_OFF)（agent/src/main.rs:397-412）
- F-147：config.rs 常量 VSOCK_ADDR "vsock://-1"、VSOCK_PORT 1024；struct AgentConfig 字段含 debug_console、dev_mode、log_level、server_addr、unified_cgroup_hierarchy、tracing、endpoints、supports_seccomp（agent/src/config.rs:31-81）
- F-148：AgentConfig Default impl 中 server_addr 为 vsock://-1:1024，supports_seccomp 调用 rpc::have_seccomp()（agent/src/config.rs:145-162）
- F-149：sandbox.rs struct Sandbox 字段含 containers: HashMap<String,LinuxContainer>、network、shared_utsns: Namespace、shared_ipcns、pcimap；方法含 setup_shared_namespaces、add_container、update_shared_pidns、online_cpu_memory（agent/src/sandbox.rs:36-257）
- F-150：namespace.rs 常量 PERSISTENT_NS_DIR "/var/run/sandbox-ns"，enum NamespaceType 变体 Ipc、Uts、Pid（agent/src/namespace.rs:19-159）
- F-151：mount.rs 常量 TYPE_ROOTFS "rootfs"、MOUNT_GUEST_TAG "cubeShared"、CUBE_BIND_SHARE_DIR "/run/cube-bind-share/"；CGROUPS map 含 cpu/cpuacct/memory/pids/rdma 键；STORAGE_HANDLER_LIST 含 blk、virtio-fs、ephemeral、overlayfs、mmioblk、local、scsi、nvdimm、watchable-bind 共 9 项（agent/src/mount.rs:37-143）
- F-152：device.rs 驱动常量含 DRIVER_VIRTIOFS_TYPE "virtio-fs"、DRIVER_BLK_TYPE "blk"、DRIVER_BLK_CUBE_TYPE "blk-cube"、DRIVER_MMIO_BLK_TYPE "mmioblk"、DRIVER_SCSI_TYPE "scsi"、DRIVER_NVDIMM_TYPE "nvdimm"、DRIVER_OVERLAYFS_TYPE "overlayfs"（agent/src/device.rs:37-53）
- F-153：passfd_io.rs 常量 PASSFD_LISTENER_PORT 1027、PASSFD_STREAM_TIMEOUT 5s、MAX_PENDING_STREAMS 256（agent/src/passfd_io.rs:13-15）
- F-154：rpc.rs start 中注册 protocols::agent_ttrpc::create_agent_service 与 protocols::health_ttrpc::create_health 两个 service（agent/src/rpc.rs:1938-1945）
- F-155：notify_vsock_server_ready x86_64 分支向端口 0x680 写 0x8，aarch64 分支写 MMIO 地址 0x0903_0000；常量 SYS_VSOCK_SERVER 为 1<<3（agent/src/rpc.rs:1957-1978）
- F-156：agent.proto 中 service AgentService 声明 CreateContainer、StartContainer、RemoveContainer、ExecProcess、SignalProcess、WaitProcess rpc，另含 GetVolumeStats、ResizeVolume（agent/libs/protocols/protos/agent.proto:21-73）
- F-157：cube/src/rootfs.rs 常量 ANNOTATION_K_ROOTFS_INFO "cube.rootfs.info"、ENV_CONTAINER_PID "container.pid"；struct RootfsInfo 字段 rootfs、pmem_file、overlay_info、mounts、ero_image 均为 Option；do_exec_mount 对 /proc/{pid}/ns/mnt 执行 setns(CLONE_NEWNS)，随后执行 MS_BIND|MS_REC 挂载与 umount2(MNT_DETACH)（agent/cube/src/rootfs.rs:14-209）
- F-158：CubeShim README 声明基于 containerd-shim-rs 实现 Shim v2，containerd runtime_type 为 `io.containerd.cube.v2`（CubeShim/README.md:3-86）
- F-159：CubeShim shim main.rs 中 Config 字段 no_reaper、no_setup_logger、no_sub_reaper 均为 true；main 调用 shim_run::<Service>("io.containerd.cube.rs", Some(c))（CubeShim/shim/src/main.rs:17-54）
- F-160：set_process 写 /proc/self/coredump_filter 为 0x33，设 RLIMIT_CORE 为 2*1024^3，并把 dummy AF_UNIX socket dup2 到 fd 512（CubeShim/shim/src/main.rs:93-138）
- F-161：shim Cargo.toml 依赖 containerd-shim =0.9.0、containerd-shim-protos =0.9.0、ttrpc =0.5.8，并 path 依赖 cube-hypervisor（features lib_support）（CubeShim/shim/Cargo.toml:17-32）
- F-162：shim lib.rs 声明模块 common、container、cube、hypervisor、log、sandbox、service、snapshot（CubeShim/shim/src/lib.rs:5-12）
- F-163：common/mod.rs 常量 SHIM_VERSION/SHIM_COMMIT/SHIM_BUILD_TIME 取 env CUBE_VERSION/CUBE_COMMIT/CUBE_BUILD_TIME；注解常量含 ANNO_ROOTFS_WLAYER_PATH "cube.rootfs.wlayer.path"、ANNO_PROPAGATION_MNTS "cube.propagation.mounts"、ANNO_CONTAINER_LOG_FORWARDING "cube.container.log_forwarding"（CubeShim/shim/src/common/mod.rs:17-37）
- F-164：common/mod.rs 常量 PAUSE_VM_SNAPSHOT_BASE "/data/cubelet/root/pausevm"、GUEST_PROPAGATION_DIR "/run/propagation"、GUEST_VIRTIOFS_MNT_PATH "/run/virtiofs"（CubeShim/shim/src/common/mod.rs:27-41）
- F-165：protoc crate 模块含 agent、agent_ttrpc、csi、empty、health、health_ttrpc、oci、types；csi.rs enum VolumeUsage_Unit 变体 UNKNOWN=0/BYTES=1/INODES=2，struct VolumeUsage 字段 available/total/used（CubeShim/protoc/src/lib.rs:7-14；CubeShim/protoc/src/csi.rs:258-518）

## ⑨ CubeNet/eBPF 网络数据面

- F-166：cubevs.go 含三条 //go:generate 指令，bpf2go 目标名 localgw、mvmtap、nodenic，源文件 ../src/localgw.bpf.c、../src/mvmtap.bpf.c、../src/nodenic.bpf.c，参数含 -I../vmlinux/$GOARCH（CubeNet/cubevs/cubevs.go:12-14）
- F-167：cubevs.go type Params 字段含 MVMInnerIP、MVMMacAddr、MVMGatewayIP、Cubegw0Ifindex、Cubegw0IP、EgressSrcMacAddr、EgressDstMacAddr、EgressRedirectFlags、CubeRouterIfindex、NodeIfindex、NodeIPMask、NodeGatewayMacAddr、L7MarkHTTP、L7MarkHTTPS、L7MarkMask（CubeNet/cubevs/cubevs.go:17-47）
- F-168：cubevs.go type TAPDevice（字段 IP、ID、Ifindex）、type mvmMetadata（字段 Version、IP、UUID [64]byte、DNSPolicyFlags、PolicyVersion）（CubeNet/cubevs/cubevs.go:49-71）
- F-169：cubevs.go type TCDirection、常量 TCIngress/TCEgress、BPFRedirectFlagIngress 1、type MVMPort（字段 Ifindex、ListenPort）（CubeNet/cubevs/cubevs.go:73-91）
- F-170：cubevs.go BPF 镜像结构体含 lpmKey、l7PortEntry、netPolicyValueV2、lpmKeyV3（字段 Prefixlen、IP、Port、Pad）、netPolicyValueV3（字段 ExpiresAtNS、Flags、Scheme、KeyPrefixlen）、dnsAllowKey、dnsAllowValue、dnsQueryTrackKey、dnsQueryTrackValue（CubeNet/cubevs/cubevs.go:93-177）
- F-171：cubevs.go 常量含 maxIDLength 64、maxDNSAllowEntries 1024、maxDNSNameLen 256、dnsPolicyFlagLearningEnabled 1、netPolicyFlagL7Required 1、netPolicyFlagL3Allowed 2、L7SchemeNone 0/L7SchemeHTTP 1/L7SchemeHTTPS 2、maxL7PortsPerHost 8、netPolicyValueStatic 1（CubeNet/cubevs/cubevs.go:179-202）
- F-172：cubevs.go 程序名常量 programNameFromEnvoy "from_envoy"、programNameFromCube "from_cube"、programNameFromWorld "from_world"，DNS 程序名 dns_parse_chunk/dns_rev_chunk/dns_finish/dns_handle_response_prog/dns_response_finish_prog，slot 常量 dnsTailCallParse 0 至 dnsTailCallResponseFinish 4，mapNameDNSTailCalls "dns_tail_calls"（CubeNet/cubevs/cubevs.go:203-219）
- F-173：cubevs.go map 名常量含 MapNameIfindexToMVMMetadata "ifindex_to_mvmmeta"、MapNameMVMIPToIfindex "mvmip_to_ifindex"、MapNameRemotePortMapping "remote_port_mapping"、MapNameLocalPortMapping "local_port_mapping"、MapNameAllowOut "allow_out"/V2/V3、MapNameDenyOut "deny_out"、MapNameDNSAllow "dns_allow"/V2、MapNameDNSQueryTrack "dns_query_track"、MapNameDirectNeigh "direct_neigh"（CubeNet/cubevs/cubevs.go:221-234）
- F-174：cubevs.go 全局变量名常量含 mvm_inner_ip、mvm_macaddr_p1/p2、mvm_gateway_ip、cubegw0_ip、cubegw0_ifindex、egress_smacaddr_p1、nodenic_ip、nodegw_macaddr_p1、cube_l7_mark_http/https/mask；TC 常量含 tcFlagDirectAction 1、tcFilterHandle 1、tcFilterPriority 1、tcAttrKindBPF "bpf"、tcAttrKindClsact "clsact"（CubeNet/cubevs/cubevs.go:235-274）
- F-175：map.go 变量 bpfFSPath "/sys/fs/bpf"，函数 pinPath、loadPinnedMap；port.go 函数 AddPortMapping、DelPortMapping、ListPortMapping、GetPortMapping、DeletePortMappingsByIfindex（CubeNet/cubevs/map.go:13-29；CubeNet/cubevs/port.go:17-359）
- F-176：snat.go 常量 mapSNATIPList "snat_iplist"、maxPortStart 30000、maxSNATIPs 4；含 type SNATIP、type snatIP（字段 Lock、Ifindex、IP、MaxPort）、函数 SetSNATIPs（CubeNet/cubevs/snat.go:11-49）
- F-177：reaper.go 常量 MapNameIngressSessions "ingress_sessions"、MapNameEgressSessions "egress_sessions"、reapSessionsInterval 5s、maxSessions 1048576、maxSessionPercentage 0.8；tcpConntrackState 常量含 tcpCTSynSent/tcpCTEstablished/tcpCTTimeWait/tcpCTInvalid；tcpTimeouts 中 ESTABLISHED 3 小时；udpTimeouts 30s/180s；icmpTimeout 30s（CubeNet/cubevs/reaper.go:14-141）
- F-178：miscs.go 常量 defaultL7MarkHTTP 0xCE010000、defaultL7MarkHTTPS 0xCE020000、defaultL7MarkMask 0xFFFF0000；函数 rewriteConstants、pinProgs、populateDNSTailCalls（CubeNet/cubevs/miscs.go:38-40）
- F-179：miscs.go Init(params) 依次调用 loadLocalgw、loadMvmtap、loadNodenic，含 attachTCFilter(programNameFromEnvoy, Cubegw0Ifindex, TCEgress)、attachTCFilter(programNameFromWorld, CubeRouterIfindex, TCEgress)、attachTCFilter(programNameFromWorld, NodeIfindex, TCIngress)；AttachFilter(ifindex) 加载 programNameFromCube（TCIngress）（CubeNet/cubevs/miscs.go:311-405）
- F-180：src/map.h 中 map 均带 SEC(".maps") 与 pinning LIBBPF_PIN_BY_NAME，map 名含 mvmip_to_ifindex（HASH）、ifindex_to_mvmmeta、remote_port_mapping、local_port_mapping、egress_sessions、ingress_sessions、snat_iplist（ARRAY）、direct_neigh（LRU_HASH）、allow_out_v3（HASH_OF_MAPS，内层 LPM_TRIE）、deny_out、dns_allow_v2、dns_query_track、dns_tail_calls（PROG_ARRAY，max 16）（CubeNet/src/map.h:13-238）
- F-181：BPF C 文件含 SEC("tc") 程序：localgw.bpf.c 的 from_envoy（含 dnat、snat、bpf_redirect 调用）；mvmtap.bpf.c 的 dns_parse_chunk、dns_rev_chunk、dns_finish、from_cube；nodenic.bpf.c 的 from_world、dns_handle_response_prog、dns_response_finish_prog（CubeNet/src/localgw.bpf.c:67-117；CubeNet/src/mvmtap.bpf.c:848-955；CubeNet/src/nodenic.bpf.c:479-567）
- F-182：网络模型页写明沙箱固定内部地址 169.254.68.6，沙箱网关 169.254.68.5（docs/zh/architecture/network.md:75）
- F-183：网络模型页会话超时表列出 SYN_SENT 1 分钟、ESTABLISHED 3 小时、FIN_WAIT 2 分钟、TIME_WAIT 2 分钟（沙箱主动关闭时 10 秒）、UDP 30/180 秒、ICMP 30 秒；会话回收 goroutine 每 5 秒执行一次，Map 占用率超 80% 告警（docs/zh/architecture/network.md:140-144）
- F-184：网络模型页写明 SNAT 池最多四个 IP，沙箱分配公式 index=jhash(sandbox_ip)%4，SNAT 源端口从 30000 开始；始终拒绝的地址段含 10.0.0.0/8、127.0.0.0/8、169.254.0.0/16、172.16.0.0/12、192.168.0.0/16；节点端口三段为 10000–19999、20000–29999、30000–65535，port mapping 仅从 20000–29999 分配（docs/zh/architecture/network.md:162-267）

## ⑩ CubeEgress/CubeProxy 安全网关

- F-185：CubeEgress nginx.conf 中 server 监听 192.168.0.1:8080（transparent reuseport）与 192.168.0.1:8443（ssl transparent reuseport）（CubeEgress/nginx.conf:109-141）
- F-186：nginx.conf lua_shared_dict 声明 cert_cache 64m、cert_locks 8m、policy_store 128m、meta_store 1m（CubeEgress/nginx.conf:24-28）
- F-187：nginx.conf init_by_lua_block 调 cert_signer.bootstrap（ca_cert_path /etc/cube/ca/cube-root-ca.crt、leaf_ttl_sec 7 天）与 audit.bootstrap（file_path /data/log/cube-egress/access.jsonl）；HTTP/HTTPS location 内调 require("access_phase").decide()（CubeEgress/nginx.conf:32-116）
- F-188：lua/policy.lua 常量 STORE "policy_store"、INDEX_KEY "__index__"、MAX_L7_PORTS_PER_HOST 8；局部函数含 is_valid_sandbox_ip、parse_ipv4_cidr、normalize_identity、validate_match_tuples、validate_policy（CubeEgress/lua/policy.lua:26-220）
- F-189：policy.lua 导出方法 list_ips、get、put、delete、patch、dump_all、count、bulk_load；compute_fingerprint 返回 "fp-" 加 sha256 前 8 位 hex，put 时写 inj.secret_ref_synthetic（CubeEgress/lua/policy.lua:249-447）
- F-190：nginx.conf 管理 server 监听 127.0.0.1:9091；admin.lua routes 注册 GET /admin/v1/health、/dump、/policies 及 GET/PUT/PATCH/DELETE /admin/v1/policies/([%d%.]+)（CubeEgress/nginx.conf:212-223；CubeEgress/lua/admin.lua:187-195）
- F-191：admin.lua redact_policy 把 inject[].secret 替换为 "***REDACTED***" 并删除 secret_ref_synthetic；audit.lua bootstrap 默认文件 /data/log/cube-egress/access.jsonl，函数 write_one、write_security_event、write_tls_handshake_event，事件名 http_request、security_event、tls_handshake（CubeEgress/lua/admin.lua:45-63；CubeEgress/lua/audit.lua:34-359）
- F-192：CubeProxy lua/utils.lua GRPC_STATUS 表映射 400→3、403→7、404→5、410→9、503→14；方法含 is_grpc_request、respond_with、respond_bad_request、respond_forbidden、respond_not_found、respond_unavailable、respond_gone（CubeProxy/lua/utils.lua:13-102）
- F-193：CubeProxy nginx.conf 监听 8081（reuseport）、8080（ssl reuseport）、9090（http2 reuseport）；upstream backend、grpc_backend 配 balancer_by_lua_file lua/balancer_phase.lua（CubeProxy/nginx.conf:104-396）
- F-194：CubeProxy nginx.conf location 正则匹配 ^/sandbox/[^/]+/\d+/(?:process\.Process/(?:Start|Connect)|filesystem\.Filesystem/WatchDir)$ 与 location /sandbox/（rewrite_by_lua_file path_rewrite_phase.lua）；internal location /_sidecar_resume proxy_pass http://$cube_sidecar_addr/internal/resume；lua_shared_dict cube_sandbox_meta 16m、cube_sandbox_state 4m、cube_sandbox_last_active 8m（CubeProxy/nginx.conf:130-196）
- F-195：CubeEgress start.sh 变量 CUBE_SANDBOX_NETWORK_CIDR 默认 192.168.0.0/18、CUBE_EGRESS_ADMIN_PORT 默认 9091；gen-ca.sh CURVE 默认 prime256v1、DAYS 3650（CubeEgress/start.sh:66-257；CubeEgress/gen-ca.sh:4-32）
- F-196：CubeEgress Dockerfile FROM cube-sandbox-cn.tencentcloudcr.com/cube-sandbox/openresty-tproxy:1.29.2.5，EXPOSE 8080 8443 9091；CubeProxy Dockerfile FROM openresty:1.21.4.1-6-alpine-fat，EXPOSE 8080 8081 9090（CubeEgress/Dockerfile:1-39；CubeProxy/Dockerfile:5-25）

## ⑪ CubeCoW 与 CubeS3lvol 存储体系

- F-197：cubecow Cargo.toml 包名 cubecow version 0.1.0，crate-type ["lib","cdylib","staticlib"]，bin cubecow-cli 对应 src/bin/cubecow_cli.rs（cubecow/Cargo.toml:2-23）
- F-198：cubecow src/lib.rs struct Volume 字段含 name、size_bytes、device_path、snapshot_count: i32、created_at、export_uuid、export_status、deletable: Option<bool>（cubecow/src/lib.rs:52-80）
- F-199：struct Snapshot 字段含 name、size_bytes、device_path、origin_volume、created_at、export_uuid、export_status、deletable（cubecow/src/lib.rs:83-136）
- F-200：lib.rs initialize 按 BackendKind::Reflink、BackendKind::S3 分支构造（cubecow/src/lib.rs:158）
- F-201：engine/mod.rs trait Engine: Send+Sync 方法含 create_volume、delete_volume、resize_volume、create_snapshot_from_volume、create_volume_from_snapshot、list_volumes、list_snapshots、activate_volume、deactivate_volume、reset_node_storage、metrics（cubecow/src/engine/mod.rs:36-140）
- F-202：config/mod.rs enum BackendKind 变体 Reflink（default）与 S3，serde rename_all lowercase；S3Config 字段 socket_path 默认 "/var/run/s3lvol.sock"；ReflinkConfig 含 root_dir: PathBuf（cubecow/src/config/mod.rs:55-151）
- F-203：engine/reflink.rs 常量 REFLINK_BLOCK_SIZE 512、FICLONE 0x40049409；struct ReflinkEngine 字段 volumes_dir、name_index: RwLock<HashMap<String,NameKind>>、metrics（cubecow/src/engine/reflink.rs:78-128）
- F-204：reflink.rs initialize_with_config 创建 <root_dir>/volumes，调用 probe_reflink_support 与 scan_and_rebuild_index（cubecow/src/engine/reflink.rs:150-185）
- F-205：reflink.rs create_volume 以 create_new(true) 创建主文件并调 set_len(size_bytes)；resize_volume 中 new_size<old_size 时返回 InvalidArg；create_snapshot_from_volume 调自由函数 ficlone（cubecow/src/engine/reflink.rs:386-715）
- F-206：自由函数 ficlone 对目标 fd 执行 ioctl(dst, FICLONE, src)（cubecow/src/engine/reflink.rs:1083-1092）
- F-207：ffi.rs 错误码常量 COW_OK 0、COW_ERR_NOT_FOUND -1、COW_ERR_ALREADY_EXISTS -2、COW_ERR_PANIC -99；含 pub extern "C" fn cubecow_init、cubecow_create_volume、cubecow_create_snapshot_from_volume、cubecow_get_metrics（cubecow/src/ffi.rs:47-1173）
- F-208：engine/s3.rs 经 UDS /var/run/s3lvol.sock JSON-RPC 调用 11 个 rcow_* 方法，index.json 落盘（cubecow/src/engine/s3.rs）
- F-209：CubeS3lvol README 记录发布包含 bin/s3lvol_tgt（NVMe/TCP target）；make_release.sh 参数含 --version、--outdir、--no-tar、--skip-build、--skip-smoke（CubeS3lvol/README.md:3-16）
- F-210：CubeS3lvol Makefile 目标含 all、shared、static、app、clean、check、check-offline、check-rules、check-env（CubeS3lvol/Makefile:51-100）
- F-211：CubeS3lvol scripts/rpc.py 定义函数 _existing、find_upstream_rpc_py，注释记录环境变量 S3LVOL_RPC_DISABLE_FALLBACKS（CubeS3lvol/scripts/rpc.py:14-39）
- F-212：v0.7.2 tag blob 的 `vbdev_s3lvol_rpc.c` 经 `SPDK_RPC_REGISTER` 注册 **30 个不同名 `rcow_*` RPC**（V 阶段勘误：R 阶段按 :485-3516 行段登记的 9 个——`rcow_create_lvstore`、`rcow_attach_lvstore`、`rcow_create_lvol`、`rcow_create_snapshot`、`rcow_create_clone`、`rcow_resize_lvol`、`rcow_delete_lvol`、`rcow_get_lvstores`、`rcow_active_bdev`——仅为核心卷管理子集，非注册总数；其余含 lvstore 删除/卸载/flush/checkpoint、import_lvol/export_snapshot/materialise_export/release_export/get_exports/get_imports、decouple_lvol/get_decouple、get_bdev/deactive_bdev/active_bdev_batch、pending delete、buildinfo 等）（CubeS3lvol/module/bdev/s3lvol/vbdev_s3lvol_rpc.c）
- F-213：S3 卷页列出后端可接 AWS S3、腾讯云 COS、Cloudflare R2、MinIO，默认安装自带 MinIO；Python SDK 安装命令 pip install 'cubesandbox>=0.6.0'，创建写法 Volume.create("my-data", driver="s3")（docs/zh/guide/s3-volume.md:3-28）
- F-214：S3 卷页写明挂载/卸载走引用计数：首次挂载 s3fs 挂到宿主机，refCount→0 时 fusermount -u 卸载且后端数据保留，Volume.destroy 删除 volumes/<id>/ 前缀（docs/zh/guide/s3-volume.md:174）

## ⑫ CubeOps / CLM / TemplateCenter

- F-215：CubeOps go.mod module github.com/tencentcloud/CubeSandbox/CubeOps，go 1.25.7，require gin、gorm、pgx/v5、redigo、google/go-containerregistry、urfave/cli，replace CubeLog/blobstore/cubedb 指向 ../pkgs/（CubeOps/go.mod:1-25）
- F-216：CubeOps README 声明服务监听 :3010，API 组含 /api/v1/auth、/cluster、/agenthub、/store、/config、/warehouse、/api/v1/sdk/* 与 /internal/warehouse/*（CubeOps/README.md:12-30）
- F-217：CubeOps 路由 POST /auth/login、/auth/refresh、GET /auth/session、POST /auth/change-password；GET /cluster/overview、/cluster/versions、/nodes、/nodes/:nodeID，PATCH /nodes/:nodeID/labels，PUT /nodes/:nodeID/isolation（CubeOps/internal/auth/handler.go:35-44；CubeOps/internal/handler/cluster.go:41-49）
- F-218：CubeOps 路由 GET/POST/DELETE /agenthub/instances[/:agentID]、POST /agenthub/instances/:agentID/restart；nodemanagement 路由 GET /readyz、POST /nodes/register、POST /nodes/:nodeID/status，internal 组 GET /nodes、DELETE /nodes/:nodeID（CubeOps/internal/handler/agenthub.go:90-95；CubeOps/internal/nodemanagement/handler/agent.go:26-34）
- F-219：CubeOps server.go 注册 GET /health，sdkV2 组 GET /sandboxes、GET /sandboxes/:id/logs；Dockerfile 运行时 FROM alpine:3.20，EXPOSE 3010，ENTRYPOINT cubeops（CubeOps/internal/server/server.go:138-198；CubeOps/Dockerfile:10-45）
- F-220：cube-lifecycle-manager go.mod module github.com/tencentcloud/CubeSandbox/cube-lifecycle-manager，go 1.25.7，require redis/go-redis/v9 v9.20.0、zap v1.28.0、cenkalti/backoff/v7、miniredis（cube-lifecycle-manager/go.mod:1-12）
- F-221：CLM cmd main.go 构造 redisclient、redisstream、cubemasterclient、registry、leader.Lease、resumer.Resumer、sweeper、httpapi.Server，后台 goroutine 运行 consumeStream、pollLastActive、sweep.Run、apiSrv.Run、lease.Run、reconcileOnLeadership、discovery（cube-lifecycle-manager/cmd/cube-lifecycle-manager/main.go:67-255）
- F-222：CLM httpapi server 注册 POST /internal/resume、GET /healthz、GET /readyz，WriteTimeout 35s，handleResume 内 25s context 调 resumer.Resume（cube-lifecycle-manager/internal/httpapi/server.go:66-120）
- F-223：CLM eventbus Bus 方法 Publish(sandboxID)、Wait(sandboxID)；schema 常量 MetaKey、EventStreamKey、EventChannel、LeaderLeaseKey 以 "cube:v1:shared:" 开头，EventStreamMaxLen 100000；操作码 OpCreate/OpDelete/OpUpdate/OpState，状态字符串 StatePaused/StateRunning/StateKilled（cube-lifecycle-manager/internal/eventbus/bus.go:29-47；cube-lifecycle-manager/internal/lifecycle/schema.go:24-107）
- F-224：CubeTemplateCenter go.mod module github.com/tencentcloud/CubeSandbox/CubeTemplateCenter，go 1.25.7，replace CubeMaster => ../CubeMaster、cubedb => ../pkgs/cubedb、Cubelet => ../Cubelet（CubeTemplateCenter/go.mod:1-144）
- F-225：CubeTemplateCenter gin 路由 root.GET("/metrics")、root.GET("/health")；internal 组 POST /build、/artifact/delete、/artifact/upload；测试请求前缀 /tc/api/v1/（CubeTemplateCenter/pkg/httpservice/server.go:130-131；CubeTemplateCenter/pkg/api/internal.go:338-340）

## ⑬ SDK 三端与 pkgs

- F-226：sdk/go go.mod module github.com/tencentcloud/CubeSandbox/sdk/go，go 1.22；client.go type Client，函数 NewClient，方法 Create、Connect、List、ListV2、Health、Close；type ClientOption 与 WithHTTPClient（sdk/go/go.mod:1-3；sdk/go/client.go:22-108）
- F-227：sdk/go sandbox.go Sandbox 方法 GetHost、GetInfo、Pause、Resume、SetTimeout、UpdateNetwork、Kill、Close、RunCode、Commands、Files（sdk/go/sandbox.go:25-257）
- F-228：sdk/go commands.go type Commands 与方法 Run；files.go type Files 与方法 ForUser、Read、Write、WriteFiles、List、Stat、Exists、Remove、Rename、MakeDir、WatchDir（sdk/go/commands.go:15-19；sdk/go/files.go:61-154）
- F-229：sdk/go snapshot.go 方法 CreateSnapshot、ListSnapshots、DeleteSnapshot、Rollback、Clone；template.go 方法 ListTemplates、GetTemplate、BuildTemplate、RebuildTemplate、DeleteTemplate、SetTemplateAlias、GetTemplateBuildStatus；volume.go 方法 CreateVolume、ListVolumes、GetVolume、DeleteVolume（sdk/go/snapshot.go:88-175；sdk/go/template.go:94-166；sdk/go/volume.go:69-113）
- F-230：sdk/go policy.go type Match、Inject（方法 Render）、Action、Rule；connect.go 函数 encodeConnectEnvelope、readConnectEnvelope；transport.go 函数 newControlHTTPClient、newDataHTTPClient；envd.go 常量 defaultEnvdUser "root"，方法 startProcess、filesystemRPC、watchDir，type Watcher（sdk/go/policy.go:29-102；sdk/go/connect.go:23-64；sdk/go/transport.go:14-19；sdk/go/envd.go:24-506）
- F-231：sdk/node package.json name "@cubesandbox/sdk" version 0.3.0、type module、engines node >=18，依赖 undici ^6.19.8；src 含 index.ts、sandbox.ts、commands.ts、filesystem.ts、pty.ts、policy.ts、template.ts、volume.ts 等 13 个 ts 文件（sdk/node/package.json:2-51）
- F-232：sdk/python pyproject.toml name cubesandbox version 0.7.0；包 cubesandbox 含 __init__.py、sandbox.py、_commands.py、_config.py、_exceptions.py、_filesystem.py、_models.py、_policy.py、_pty.py、_stream.py、_template.py、_transport.py、_volume.py；__init__.py 导出 Sandbox、NEVER_TIMEOUT、Config、Execution、Pty、Template、Volume（sdk/python/pyproject.toml:1-3；sdk/python/cubesandbox/__init__.py:5-16）
- F-233：pkgs/CubeLog module github.com/tencentcloud/CubeSandbox/pkgs/CubeLog，源文件含 common.go、log.go、logger.go、logwriter.go；pkgs/blobstore 文件 announce.go、blob.go、config.go、keys.go、open.go，依赖 minio-go/v7 v7.3.0；pkgs/cubedb 文件 dao/dao.go、dao/driver.go，依赖 goose v3.27.1、gorm；pkgs/proto 含 doc/api.md（pkgs/CubeLog/go.mod:1；pkgs/blobstore/go.mod:1-5；pkgs/cubedb/go.mod:1-13；pkgs/proto/go.mod:1）

## ⑭ 生命周期/模板/日志与版本演进

- F-234：生命周期页列出五种状态 running、pausing、paused、resuming、terminated（docs/zh/guide/lifecycle.md:13）
- F-235：生命周期页写明 timeout 单位为秒（e2b 的 timeoutMs 为毫秒），SDK 不带默认值；on_timeout 取值 "kill"（默认）与 "pause"；NEVER_TIMEOUT 数值 -1，0 为立刻超时，正整数 N 为空闲 N 秒（docs/zh/guide/lifecycle.md:21-29）
- F-236：删除持锁中的沙箱返回 503 Service Unavailable 并携带 Retry-After: 2（docs/zh/guide/lifecycle.md:129）
- F-237：集群默认空闲超时读取 CubeMaster/conf.yaml 中 cubelet_conf.default_timeout_insec，仓库默认为 -1，修改后重启 cube-sandbox-cubemaster.service；节点配置项 host.quota.paused_resource_release_ratio 位于 Cubelet/config/config.toml，值域 [0,1]，默认 0（docs/zh/guide/lifecycle.md:237-257）
- F-238：恢复被拒链路为 Cubelet（130409 Conflict）→ CubeAPI（HTTP 409）→ WebUI 容量诊断（docs/zh/guide/lifecycle.md:281）
- F-239：模板页写明模板快照在 HTTP 探针返回 2xx 后制作；必填参数含 --expose-port、--probe、--probe-path；envd 默认监听 49983，/health 接口返回 204；两种制作方式为从 OCI 镜像制作、从运行中的沙箱制作；cubemastercli tpl merge 处理历史 artifact 存储收敛，tpl redo 处理节点侧重新分发/重建（docs/zh/guide/templates.md:15-61）
- F-240：沙箱日志页列出沙箱 stdout/stderr 路径 /data/cubelet/state/io.containerd.runtime.v2.task/default/<sandbox-id>/stdout|stderr；模板构建日志路径 /data/log/template/<templateID>_0/stdout|stderr；日志无 --follow 标志，日志转发要求 CubeShim v0.4.0 及以上（docs/zh/guide/sandbox-logs.md:59-86）
- F-241：各 changelog 标注：v0.1.0 2026-04-20；v0.2.0 2026-05-07；v0.3.0 2026-06-02（82 commits/22 人）；v0.4.0 2026-06-14（58/15）；v0.5.0 2026-07-03（116/26）；v0.6.0 2026-07-24（92/31）；v0.7.0 2026-08-28（239/57）；v0.7.1 2026-09-11（70/24）；v0.7.2 标题写 2026-09-23（56/29）（docs/zh/changelog/v0.7.2.md:2）
- F-242：v0.2.2 changelog 写明默认沙箱暴露端口由 8080/32000 改为 49999/49983（docs/zh/changelog/v0.2.2.md:21）
- F-243：v0.4.0 changelog 写明构建基础镜像降到 ubuntu:20.04，最低 glibc 从 2.34 降到 2.31（docs/zh/changelog/v0.4.0.md:7）
- F-244：WebUI（React + TSX）`web/src/pages/` 下共 **19 个 .tsx 页面组件**，`main.tsx` 注册 **18 条路由**（/login 及 AuthGuard+AppShell 内 17 条，另有 `*` 通配重定向），其中主导航页面 15 个——Overview、Sandboxes、SandboxNew、SandboxDetail、Templates、TemplateStore、TemplateDetail、Nodes、NodeDetail、Network、Versions、AgentHub、Observability、Settings、Warehouse；其余为 Login 与 Warehouse 子页 WarehouseJobs/WarehouseComponent；Placeholder 未挂路由（V 阶段勘误：R 阶段误记"共 15 个页面"）（web/src/main.tsx、web/src/pages/）

---

## G1 自检记录

- 事实总数：244 条（F-001 ~ F-244），全部为"文件中有什么"的客观陈述。
- 因果词扫描：正文无"因为/所以/导致/失误"；"配合/强制/默认"均出现在对代码或文档字面的转述中（如 conf 键值、函数分支、默认参数）。
- 每条事实附文件锚点；post-release 变更文件（CubeS3lvol C 源、CubeAPI handlers/services、sdk/go/envd.go、openapi.yml、deploy/one-click）均以 v0.7.2 tag blob 为基准。
- 待 I 阶段处理的推断事项：组件间调用时序、设计动因、性能数字的成立条件。
