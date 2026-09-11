# Toolbx 实现层架构洞察与知识地图（第二轮）

> 输入：facts.md（F-001~F-197，信源 vendor/toolbox @81401f64）。G2 门：每个洞察含陈述/证据/反常识/行动四元组。

## 洞察一：Toolbx 本体是"外部 CLI 的 argv 编排器"，不含任何容器运行时逻辑

- **陈述**：Toolbx 二进制自身不实现镜像拉取、容器创建、cgroup、namespace 等任何容器能力；它做的全部事情是构造 podman/skopeo/flatpak-spawn/p11-kit/mount/useradd/ldconfig 等外部命令的 argv 并执行，再用 JSON 解析返回结果。
- **证据**：F-070（pkg/shell 只是 exec.CommandContext 封装）；F-071~F-075（全部容器/镜像操作一一映射到 `podman ps/inspect/exists/pull/rm/start/logs/system migrate` 子命令）；F-081（镜像大小靠 `skopeo inspect docker://`）；F-029/F-060（容器内命令经 flatpak-spawn --host 回送主机）；F-136（CA 证书靠主机 p11-kit server）。GOALS.md 明确"Non-goals: 不支持多运行时、不在 Podman 之上堆功能"（F-196）。
- **反常识**：直觉以为"容器开发环境工具"必然深度耦合容器运行时（像 Docker CLI 之于 dockerd）；实际 Toolbx 与 Podman 之间**没有 API 依赖、没有库链接、没有守护进程**，唯一契约是 CLI argv + `--format json` 的输出模式。这解释了三件事：①Podman 版本差异要靠 CheckVersion 运行时探测（F-072、F-099/F-140）；②ps/inspect 两种 JSON 的 V1/V2 字段差异要写自定义 UnmarshalJSON 兼容（F-078）；③Toolbx 能在 CoreOS 上以极小依赖存在。
- **行动**：文档 04 专章讲清"命令映射全表 + JSON 适配 + 版本门控"；读者排查问题应直接看 `toolbox -vv ...` 打印的 podman argv（F-022），把 Toolbx 理解为"带领域知识的 podman 参数生成器"。

## 洞察二：单二进制跨发行版——入口程序在容器内动态链接主机 glibc

- **陈述**：同一个 toolbox 二进制要作为 entry point 跑在 Fedora/Ubuntu/RHEL/Arch 各种 glibc 版本的容器里；构建时通过外链选项把动态链接器与 rpath 指到 `/run/host/...`，即容器内执行的入口程序实际加载的是**主机的 glibc/ld**；配合 `-z lazy` 容忍 NVIDIA 库符号在启动时缺失。
- **证据**：F-008/F-009（go-build-wrapper 的 `-I /run/host<ld> -r /run/host<libc-dir>` 与 rpath 改写）；F-011（NVIDIA 栈 dlopen 延迟解析决定不能用 -z now 的完整注释）；F-095（主机根文件系统挂在 /run/host）；F-018/F-100（toolbox 二进制本身只读挂进容器 /usr/bin/toolbox，TOOLBOX_PATH 环境变量定位）。
- **反常识**：常规做法是为每个发行版/版本编译静态入口或逐镜像内置工具；Toolbx 反其道——容器内的 PID 1 程序不依赖容器内的 libc，而依赖被 bind mount 进来的主机 libc。这把"入口程序版本与容器内用户态版本匹配"问题彻底消解：工具版本随主机 RPM/DEB 升级，老容器下次启动就用上新 init-container 逻辑。
- **行动**：文档 08 讲清链接选项原理与故障表现（symbol lookup error）；自定义镜像文档需补充"镜像不需要预装 toolbox"的认知——主机二进制经 /usr/bin/toolbox 挂载注入。

## 洞察三：OCI 不可变性的反转——把容器配置从 create 时推迟到 entry point 运行时

- **陈述**：Toolbx 容器的用户账号、bind mount、关键系统配置都不在 `podman create` 参数里固化，而是由隐藏命令 `toolbox init-container` 在容器每次启动时于容器**内部**执行：用户 useradd/usermod、15 条 rbind、4 个配置文件符号链接、Kerberos/PKCS#11/RPM 配置写入、CDI 应用；主机侧用"初始化戳记文件 + fsnotify/轮询 + 日志跟随"协议等待引导完成。
- **证据**：F-101/F-110（entrypoint 即 init-container）；F-116（15 条 initContainerMounts）；F-119（用户同步 + passwd -d root）；F-120~F-123（krb5/p11-kit/rpm 宏配置）；F-138（25 秒超时、$XDG_RUNTIME_DIR/toolbox/container-initialized-<pid> 戳记、TOOLBX_RUN_USE_POLLING）；官方 man page 明确写出动机"OCI containers are inherently immutable... changes in newer Toolbx can't be applied to pre-existing containers"（F-192）。
- **反常识**：容器被宣传为"不可变基础设施"，Toolbx 却刻意把可变配置面移到运行时入口——容器还是那个容器，但每次启动都重新"成形"为当前主机用户与当前版本 Toolbx 期望的样子。连主机时区变化都靠 fsnotify 持续同步（F-125/F-114）。
- **行动**：文档 07 给出"create argv 静态面 vs init-container 动态面"的完整时序；戳记协议是排障钥匙（卡住 25 秒→看 `podman logs`，entry point 错误经 logfmt 转发）。

## 洞察四：透传是"两张清单 + 双向同步 + 白名单环境变量"的确定性工程

- **陈述**：所谓"无缝主机集成"在代码里是三组确定机制：①主机侧 create argv 的固定挂载 6 条 + 条件挂载（Avahi/KCM/pcsc socket 经 D-Bus systemd 实时查询）+ namespace 共享 8 项；②容器侧 init-container 的 15 条 rbind 与 /etc 关键文件链接；③43 个环境变量白名单按"主机存在才转发"注入 exec。另有运行后持续同步（localtime/timezone fsnotify）。
- **证据**：F-093~F-100（create 侧清单与 namespace 参数）；F-096/F-107（socket 不是硬编码路径而是查 systemd 单元 Listen 属性）；F-113~F-117（容器侧链接与 selinuxfs 置空）；F-054/F-055（43 个白名单变量实测计数）；F-039/F-156（OSC 777、VTE、terminfo 等终端集成）。
- **反常识**：文档常把透传描述为"神奇的集成"，实际每一项资源都对应一个显式 argv 条目或一次 mount 系统调用，且大量精力花在**边界情况**：/media 是否符号链接到 /run/media、/home 是否链接到 /var/home（影响传 --media-link 还是 bind）、主机绝对死链要补 /run/host 前缀（F-127）。这是"特性看起来简单、实现全是 case 分析"的典型。
- **行动**：文档 06 以 argv 解剖表逐项对照第一轮 01-pass-through.md 的用户视角描述（不重复，讲实现位置）；自定义镜像文档读者可据此判断自己缺哪一项透传。

## 洞察五：GPU 支持是"主机生成 spec→运行目录传递→容器内应用"的 CDI 三段式，且无硬件全程静默降级

- **陈述**：NVIDIA GPU 透传不依赖 `--device` 也不在 create 时固化：主机侧用 go-nvlib 探测 NVML/Tegra 生成 CNCF CDI spec（JSON），写入 $XDG_RUNTIME_DIR/toolbox/cdi-nvidia.json；容器启动时 init-container 读取并用官方 CDI 库应用 mounts（HostPath 自动映射 /run/host）与 hooks（create-symlinks、update-ldcache→ldconfig）。
- **证据**：F-150/F-151（GenerateCDISpec 探测矩阵与 ErrPlatformUnsupported/驱动不匹配分流）；F-135（run 时每次重新生成，env 注入）；F-124（init-container 端 mount/hook 处理细节）；F-184（BATS 40+ JSON 夹具证明行为分支的丰富度）。
- **反常识**：GPU 特性被设计成"可选插件"而非基础路径——没有 NVIDIA 硬件、驱动未加载、Windows(DXCore)、Tegra 之外平台全部走 ErrPlatformUnsupported 静默分支，普通用户零感知；CDI spec 在主机与容器间用文件而非参数传递，绕开了 create 时不可变的限制（与洞察三同一架构思想）。
- **行动**：文档 09 讲清三段式与失败矩阵；示例 04 给出从驱动版本不匹配报错到 nvidia-smi 验证的完整路径。

## 知识地图与本轮文档规划（续编号，不重排既有文档）

学习路径（第二轮续接第一轮"入门→工作流→自定义镜像"，进入"实现层→工程体系"）：

| 序号 | 文档 | 覆盖事实 | 依赖前置 |
|---|---|---|---|
| concepts/04 | Podman/Skopeo 调用层：CLI 编排器架构 | F-070~F-081, F-022 | 02 |
| concepts/05 | 镜像与发行版名称解析机制 | F-040~F-062, F-193 | 03 |
| concepts/06 | `podman create` argv 全景解剖 | F-090~F-107, F-093~F-100 | 01, 04 |
| concepts/07 | init-container 运行时引导与戳记协议 | F-101, F-110~F-127, F-137~F-139 | 06 |
| concepts/08 | 单二进制跨发行版：链接策略与构建标签 | F-001~F-018, F-030, F-058 | 07 |
| concepts/09 | NVIDIA CDI GPU 透传三段式 | F-124, F-135, F-150~F-151 | 07 |
| concepts/10 | Meson 构建、BATS 测试与发行体系 | F-001~F-007, F-170~F-197 | 08 |
| examples/03 | 多发行版容器实战（Ubuntu/RHEL/Arch） | F-040~F-052, F-191 | 05 |
| examples/04 | NVIDIA GPU 容器实战 | F-150, F-124, F-184 | 09 |
| examples/05 | BATS 系统测试运行与扩展 | F-180~F-187 | 10 |
| references/source-code-map | 实现层信源登记（src/pkg、cmd、构建脚本、profile.d、data） | 全部 A-H | — |
| references/docs-man-source | man 页/GOALS/NEWS 信源登记 | F-190~F-197 | — |

G2 自检：5 个洞察均含陈述/证据（F 编号）/反常识/行动；每篇新文档有独立新主题，与第一轮 4 概念无重复（06 是 01 的实现视角、05 是 02 的解析器内部，均交叉引用不复述）。
