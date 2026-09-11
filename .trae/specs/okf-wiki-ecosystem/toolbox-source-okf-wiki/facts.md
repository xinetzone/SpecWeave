# Toolbx 源码深度学习事实清单（第二轮：实现层）

- 信源：`vendor/toolbox`（git submodule，remote git@github.com:containers/toolbox.git，pin commit `81401f64b3865129ea66f2a5e02a7eb40edd4fb8`，2026-08-05，`git describe` = 0.3-85-g81401f6，meson project version '0.3'）
- 轮次：toolbox 束多轮增量扩展第 2 轮。第 1 轮（v1.0.0, 2026-08-26）已基于 README.md + src/cmd/ 命令表层建束（4 概念/2 示例/2 信源）。本轮新信源：src/pkg/ 全部实现、initContainer、profile.d、data/、doc/ man、meson、images/、test/system、GOALS.md、NEWS。
- G1 纪律：每条事实仅陈述代码中存在的内容，附文件:行定位。

## A. 仓库与构建事实

- F-001：meson.build 顶层 project 名为 'toolbox'、version '0.3'、license 'ASL 2.0'、c_std=c99、meson_version>=0.58.0（meson.build:1-8）。
- F-002：构建期通过 cc.find_library('subid', has_headers: ['shadow/subid.h']) 查找 libsubid（meson.build:17）；find_program 探测 go、go-md2man、bats、codespell、htpasswd、openssl、p11-kit、podman、shellcheck、skopeo（meson.build:19-49）。
- F-003：meson_options.txt 定义 7 个选项：bash_completions、bash_completions_dir、fish_completions、fish_completions_dir、zsh_completions_dir、migration_path_for_coreos_toolbox（默认 false）、profile_dir（默认 /usr/share/profile.d）、tmpfiles_dir（meson_options.txt:1-49）。
- F-004：src/meson.build 用 custom_target 调 go-build-wrapper 编译 toolbox 二进制，参数 7 个：源目录、构建根、输出文件、project_version、C 编译器、动态链接器、migration 布尔（src/meson.build:74-90）。
- F-005：动态链接器路径按 7 种 CPU 架构枚举（aarch64/arm/loongarch64/ppc64le/s390x/x86/x86_64/riscv64），未匹配则 error()（src/meson.build:50-70）。
- F-006：补全脚本由 meson_generate_completions.py 对编译出的二进制执行生成 bash（toolbox.bash）、fish（toolbox.fish）、zsh（_toolbox）三种（src/meson.build:92-136）。
- F-007：meson test 注册 3 个 Go 检查：'go fmt'（meson_go_fmt.py）、'go vet'（go vet -c 3 ./...）、'go test'（go test -vet off ./...），另加 shellcheck 与 codespell（src/meson.build:138-144；meson.build:86-107）。
- F-008：go-build-wrapper 实际执行 `go build $tags -trimpath -ldflags "-extldflags '-Wl,--export-dynamic,--unresolved-symbols,ignore-in-object-files,-z,lazy' -I $dynamic_linker -linkmode external -r /run/host$libc_dir ... -X github.com/containers/toolbox/pkg/version.currentVersion=$VERSION"`（src/go-build-wrapper:116-120）。
- F-009：dynamic_linker 在传入 go build 前被改写为 `/run/host` 前缀（`/run/host$dynamic_linker_canonical_dirname/$basename`），rpath 同样加 `/run/host` 前缀（src/go-build-wrapper:71、119）。
- F-010：migration_path_for_coreos_toolbox 为真时加 `-tags migration_path_for_coreos_toolbox`（src/go-build-wrapper:36-39）。
- F-011：go-build-wrapper 注释记载不能用 `-z now`：nvidia-container-toolkit/go-nvml 靠 dlopen 延迟解析 libcuda/libnvidia-ml 符号，启动时立即解析会报 undefined symbol（src/go-build-wrapper:73-113）。
- F-012：Go module 路径 github.com/containers/toolbox，go 1.22.0；直接依赖 18 个，含 cobra v1.6.1、viper v1.20.1、logrus v1.9.3、godbus/dbus/v5 v5.0.6、go-nvlib v0.7.2、go-nvml v0.12.4-1、nvidia-container-toolkit v1.17.8、container-device-interface v0.8.1、fsnotify v1.8.0、renameio/v2 v2.0.0、spinner v1.23.2、go-units v0.5.0、logfmt v0.5.0、osrelease v0.1.0、go-version v1.0.1（src/go.mod:1-24）。
- F-013：版本号由构建期 -X 注入 pkg/version.currentVersion 字符串变量，GetVersion() 直接返回（src/pkg/version/version.go:20-27）。
- F-014：入口 src/toolbox.go 仅 20 行，main() 调 cmd.Execute()（src/toolbox.go:17-23）。
- F-015：源码树 src/cmd 14 个 .go 文件（含 root_test.go），src/pkg 下 8 个子包：nvidia、podman、shell、skopeo、term、utils、version（src/meson.build:7-45 与目录实测一致）。
- F-016：data/config/toolbox.conf 是示例配置，仅 [general] 段 3 个键：distro、release、image，全部注释（data/config/toolbox.conf:1-17）。
- F-017：data/tmpfiles.d/toolbox.conf 内容两行：`d /run/media 0755 root root - -` 与 `L /run/host - - - - - ../`（data/tmpfiles.d/toolbox.conf:1-2）。
- F-018：profile.d/toolbox.sh 由 meson 安装到 profile_dir（默认 /usr/share/profile.d），create.go 还会在宿主机 /etc/profile.d 或 /usr/share/profile.d 找到它并只读挂载进容器（profile.d/meson.build；src/cmd/create.go:59-65、381-393）。

## B. CLI 框架与全局行为事实

- F-020：rootCmd 定义 Use "toolbox"、Short "Tool for interactive command line environments on Linux"、PersistentPreRunE=preRun、RunE=rootRun、Version=version.GetVersion()（src/cmd/root.go:46-52）。
- F-021：4 个持久化全局选项：-y/--assumeyes（bool）、--log-level（默认 "error"，可选 trace/debug/info/warn/error/fatal/panic）、--log-podman（bool）、-v/--verbose（CountVar，可重复）（src/cmd/root.go:104-120）。
- F-022：-v 将 log-level 置 debug；-vv 额外打开 nvidia.SetLogLevel 与 logPodman（src/cmd/root.go:387-405）。
- F-023：8 个子命令注册：create、enter、help（help.go）、init-container（Hidden: true）、list、rm、rmi、run、completion（各文件 init() 中 rootCmd.AddCommand；initContainer.go:78-83 标记 Hidden）。
- F-024：preRun 流程：SilenceErrors/Usage→setUpLoggers→主机上 validateSubIDRanges→读取 TOOLBX_DELAY_ENTRY_POINT/TOOLBX_FAIL_ENTRY_POINT 调试变量→TOOLBOX_PATH 解析（容器内必须已设置，主机上自动设为自身绝对路径）→migrate()→utils.SetUpConfiguration()（src/cmd/root.go:135-186）。
- F-025：setUpGlobals 解析 cgroupsVersion（仅主机）、currentUser、可执行文件绝对路径（EvalSymlinks）、workingDirectory（src/cmd/root.go:346-379）。
- F-026：migrate() 在用户配置目录 toolbox/podman-system-migrate 记录上次 podman 版本；版本变化时执行 `podman system migrate`，用 $XDG_RUNTIME_DIR/toolbox/migrate.lock Flock 互斥；completion 命令跳过（src/cmd/root.go:222-334）。
- F-027：validateSubIDRanges：uid=0、容器内、completion 命令三种情况跳过；否则调 utils.ValidateSubIDRanges，失败报 "Missing subgid and/or subuid ranges"（src/cmd/root.go:410-434）。
- F-028：帮助在主机上通过 syscall.Exec 替换进程执行 `man toolbox[-<subcmd>]`；man 不存在时打印内置常用命令摘要（src/cmd/utils.go:547-581）。
- F-029：容器内调用任何命令（create/enter/run/list/rm/rmi/help）先判 IsInsideToolboxContainer，再 utils.ForwardToHost() 经 flatpak-spawn --host 转发到主机（各命令开头，如 enter.go:78-85；utils.go:267-295）。
- F-030：rootRunImpl 有两个构建标签版本：默认版打印 missing command 报错；migration_path_for_coreos_toolbox 版裸 `toolbox` 等价于进入默认容器（兼容 github.com/coreos/toolbox 老用户）（src/cmd/rootDefault.go:34-47；rootMigrationPath.go:45-76）。
- F-031：Execute 支持自定义 exitError.code 退出码，其余错误退出 1（src/cmd/root.go:64-94）。

## C. 名称解析与多发行版事实（pkg/utils）

- F-040：supportedDistros 注册表 4 项：arch/fedora/rhel/ubuntu，每个 Distro 结构含 ContainerNamePrefix、ImageBasename、ReleaseRequired、GetDefaultRelease、GetFullyQualifiedImage、GetP11KitClientPaths、ParseRelease 七个字段（src/pkg/utils/utils.go:46-54、132-169）。
- F-041：四发行版参数：arch（arch-toolbox/arch-toolbox，ReleaseRequired=false）、fedora（fedora-toolbox/fedora-toolbox，true）、rhel（rhel-toolbox/toolbox，true）、ubuntu（ubuntu-toolbox/ubuntu-toolbox，true）（utils.go:132-169）。
- F-042：fallback 常量：distroFallback="fedora"、releaseFallback="44"、containerNamePrefixFallback="fedora-toolbox"、idTruncLength=12（utils.go:64-69）。
- F-043：init() 读 os-release ID + 默认 release，识别成功则覆盖默认值；ContainerNameDefault=前缀+"-"+release（utils.go:190-208）。
- F-044：Fedora 全限定镜像 `registry.fedoraproject.org/<image>`；默认 release 取主机 VERSION_ID；parseRelease 接受 36 或 f36/F36，必须正整数（fedora.go:26-61）。
- F-045：RHEL 全限定镜像 `registry.access.redhat.com/ubi<major>/<image>`（major 从 '8.5' 取点前），release 必须 '<major>.<minor>' 正数（rhel.go:36-69）。
- F-046：Ubuntu 全限定镜像 `quay.io/toolbx/<image>`；release 必须 YY.MM：年 ≥4、最多两位且个位数不能前导零、月 01-12 且两位（ubuntu.go:36-91）。
- F-047：Arch 全限定镜像 `quay.io/toolbx/<image>`；release 仅接受 latest/rolling/空，归一化为 "latest"（arch.go:19-39）。
- F-048：ResolveContainerAndImageNames 优先级：CLI > 配置文件（viper general.distro/release/image）> 默认值；非默认发行版且 ReleaseRequired 时必须给 release（CLI 或配置）（utils.go:777-836）。
- F-049：默认镜像名=<ImageBasename>:<release>；指定 image 时 release 取其 tag，无 tag 回落默认 release；容器名默认=镜像 basename 对应前缀+"-"+tag（冒号换连字符）（utils.go:843-886）。
- F-050：容器名校验正则 ContainerNameRegexp = `[a-zA-Z0-9][a-zA-Z0-9_.-]*`（utils.go:71-75、751-761）。
- F-051：镜像引用工具函数：ImageReferenceCanBeID（^[a-f0-9]{6,64}$）、HasDomain（首段含 . 或 : 或为 localhost）、GetBasename/GetDomain/GetTag（utils.go:564-632）。
- F-052：配置文件两处，按 /etc/containers/toolbox.conf → $XDG_CONFIG_HOME/containers/toolbox.conf 顺序 viper MergeInConfig，TOML 格式；解析后重算 ContainerNameDefault（utils.go:667-716）。
- F-053：GetGroupForSudo 依次查 "sudo"、"wheel" 组（utils.go:429-442）。
- F-054：preservedEnvironmentVariables 白名单 43 个（COLORTERM、CONTAINERS_STORAGE_CONF、DBUS_*2、DESKTOP_SESSION、DISPLAY、HIST*6、HOME、KDE_*2、KONSOLE_*4、LANG、SHELL、SSH_AUTH_SOCK、TERM、TOOLBOX_PATH、USER、VTE_VERSION、WAYLAND_DISPLAY、XAUTHORITY、XDG_*15、XTERM_VERSION）（utils.go:82-126；脚本实测 43）。
- F-055：GetEnvOptionsForPreservedVariables 只转发主机上实际存在（LookupEnv found）的白名单变量，输出 `--env=NAME=VALUE`（utils.go:366-383）。
- F-056：IsInsideContainer = /run/.containerenv 存在；IsInsideToolboxContainer = /run/.toolbxenv 或旧名 /run/.toolboxenv 存在（utils.go:763-769）。
- F-057：GetRuntimeDirectory：uid=0 用 /run，否则用 $XDG_RUNTIME_DIR，下面建 toolbox 子目录（0700，chown 给目标用户）；初始化戳记路径 `$RUNTIME/toolbox/container-initialized-<entryPointPID>`；p11-kit socket `$RUNTIME/toolbox/pkcs11`，锁 pkcs11.lock（utils.go:470-544）。
- F-058：ValidateSubIDRanges 通过 cgo dlopen libsubid→subid_init→subid_get_gid_ranges/subid_get_uid_ranges，先按用户名查、nRanges<=0 再按 UID 查（utils_cgo.go:38-104；wrapper 头 libsubid-wrappers.h/.c）。
- F-059：GetCgroupsVersion statfs /sys/fs/cgroup，CGROUP2_SUPER_MAGIC 为 v2 否则 v1（utils.go:301-313）。
- F-060：ForwardToHost 用 flatpak-spawn 携带全部保留变量 `--host $TOOLBOX_PATH <原参数>`（utils.go:267-295）。
- F-061：错误类型体系：ContainerError/DistroError/FlockError/ImageError/ParseReleaseError 均在 pkg/utils/errors.go 定义并实现 Unwrap（errors.go:23-97）；podman 包另有 ImageError（podman/errors.go:23-35）。
- F-062：p11-kit 客户端路径按发行版：Fedora/RHEL /usr/lib64/pkcs11/p11-kit-client.so；Ubuntu 两条多架构路径；Arch /usr/lib/pkcs11/p11-kit-client.so（fedora.go:40-43；rhel.go:48-51；ubuntu.go:41-48；arch.go:28-31）。

## D. Podman/Skopeo 调用层事实（pkg/podman、pkg/skopeo、pkg/shell）

- F-070：shell 包 4 个函数 Run/RunContext/RunContextWithExitCode/RunWithExitCode，基于 exec.CommandContext；exec.ErrNotFound 返回 "name(1) not found"，ExitError 透传退出码且 err=nil（pkg/shell/shell.go:30-88）。
- F-071：所有 podman 子进程调用统一带 `--log-level <LogLevel>` 前缀，LogLevel 默认 logrus.ErrorLevel，由 --log-podman 打开（podman.go:45、SetLogLevel:408-410）。
- F-072：CheckVersion 用 HarryMichal/go-version Normalize+CompareSimple，当前版本 ≥ 要求版本返回 true（podman.go:53-60）。
- F-073：容器操作封装：ContainerExists（`podman container exists`）、InspectContainer（`podman inspect --format json --type container`）、Start、RemoveContainer（`podman rm [--force]`，退出码 1=not found、2=is running）、SystemMigrate（`podman system migrate [--new-runtime]`）、Logs/LogsContext（`podman logs [--follow] --since <unix>`）（podman.go:65-79、246-263、412-434、342-373、293-319、423-435）。
- F-074：镜像操作封装：ImageExists（`podman image exists`）、InspectImage、Pull（`podman pull [--authfile]`）、RemoveImage（退出码 1=not found、2=has dependent children）、GetFullyQualifiedImageFromRepoTags（跳过 latest tag 选第一个 RepoTag）（podman.go:229-243、266-283、325-340、375-406、186-224）。
- F-075：GetContainers 执行 `podman ps --all --format json --sort names`，按标签过滤 Toolbx 容器；GetImages 执行 `podman images --format json`，按 ID 去重、flattenNames 展平多标签、按名排序（podman.go:86-153）。
- F-076：isToolbx 同时认两个标签：com.github.containers.toolbox=true 与旧名 com.github.debarshiray.toolbox=true（podman.go:285-291）。
- F-077：Container 接口 12 个方法（Created/EntryPoint/EntryPointPID/ID/Image/IsToolbx/Labels/Mounts/Name/Names/Status）；containerInspect 与 containerPS 各自 UnmarshalJSON 适配 podman inspect 与 ps 两种 JSON 形态（container.go:26-62、117-277）。
- F-078：containerPS.UnmarshalJSON 兼容 Podman V1/V2 字段差异：Created（string→Unix 秒）、Names（string→array）、State/Status（container.go:236-277，注释引 podman issue 6594）。
- F-079：Containers/Images 集合提供 Next/Get/Len/Reset 游标式迭代器（container.go:279-307；image.go:58-98）。
- F-080：GetVersion 解析 `podman version --format json`，兼容有/无 Client 对象两种结构并缓存（podman.go:156-184）。
- F-081：skopeo.Inspect 执行 `skopeo inspect --format json docker://<target>`，只解析 LayersData[].Size（json.Number）（skopeo.go:27-51）。

## E. create 命令构造 podman argv 的事实

- F-090：create 5 个选项：--authfile、-c/--container、-d/--distro、-i/--image、-r/--release；--distro 与 --image 互斥、--image 与 --release 互斥（create.go:78-105、132-148）。
- F-091：create 主流程：容器内转发主机→互斥校验→authfile PathExists→resolveContainerAndImageNames→createContainer（create.go:122-188）。
- F-092：createContainer 先 ContainerExists 查重，再 pullImage，再 GetFullyQualifiedImageFromRepoTags，空 RepoTags 回退原名（create.go:190-242）。
- F-093：podman create argv 固定段：`--cgroupns host --dns none --hostname toolbx --ipc host --label com.github.containers.toolbox=true --name <c> --network host --no-hosts --pid host --privileged --security-opt label=disable --ulimit host --userns <host|keep-id> --user root:root`（create.go:427-460）。
- F-094：userns：uid=0 用 host，非 root 用 keep-id（create.go:289-294）。
- F-095：固定挂载：`/:/run/host:rslave`、`/dev:/dev:rslave`、D-Bus system socket 同路径挂载、home（EvalSymlinks 后同路径 :rslave）、TOOLBOX_PATH:/usr/bin/toolbox:ro、runtimeDirectory 同路径挂载（create.go:461-467）。
- F-096：条件挂载：Avahi（avahi-daemon.socket）、KCM（sssd-kcm.socket）、pcsc（pcscd.socket）经 D-Bus systemd 单元 Listen 属性解析 socket 路径后挂载（create.go:312-343、611-666）。
- F-097：/media 是 /run/media 符号链接则给 entry point 传 --media-link，否则 bind /media:/media:rslave；/mnt 同理（/var/mnt、--mnt-link）；/run/media 存在则直接 bind（create.go:345-379）。
- F-098：/home 是 /var/home 符号链接时传 --home-link（create.go:395-404）。
- F-099：podman ≥2.1.0 时追加 `--mount type=devpts,destination=/dev/pts`（create.go:280-287）。
- F-100：toolbox.sh 从宿主机 /etc/profile.d 或 /usr/share/profile.d 找到后只读挂到容器 /etc/profile.d/toolbox.sh（create.go:59-65、381-393）。
- F-101：容器 entrypoint argv：`toolbox --log-level debug init-container --gid <gid> --home <home> --shell <shell> --uid <uid> --user <name>` 加 home/media/mnt link 标志（create.go:413-425）。
- F-102：TOOLBX_DELAY_ENTRY_POINT/TOOLBX_FAIL_ENTRY_POINT 通过 --env 透传进容器（测试用）（create.go:244-256）。
- F-103：非 root 用户 XDG_RUNTIME_DIR 通过 --env 传入并挂载同路径；root 用户在容器侧 GetRuntimeDirectory（/run）（create.go:262-278）。
- F-104：pullImage 查找顺序：镜像 ID→本地原名→localhost/<name>→全限定名；无域名镜像经 GetFullyQualifiedImageFromDistros 解析 registry（create.go:668-702）。
- F-105：下载确认：assumeyes 或 localhost 域名免确认；非 TTY 直接报错要求 --assumeyes；交互式 showPromptForDownload 两阶段：并发 skopeo inspect 取镜像总大小（HumanSize）与 y/N 提示竞速（create.go:710-756、570-609）。
- F-106：创建/拉取时 briandowns/spinner 显示进度（debug 级别下关闭）（create.go:489-494、738-743）。
- F-107：D-Bus system socket 路径取 DBUS_SYSTEM_BUS_ADDRESS，缺省 unix:path=/var/run/dbus/system_bus_socket，EvalSymlinks 后挂载（create.go:532-555）。

## F. init-container 容器内引导事实

- F-110：init-container 仅允许容器内执行；选项 --gid（缺省取 uid）、--home（必填）、--home-link、--media-link、--mnt-link、--monitor-host（已废弃 no-op）、--shell（必填）、--uid（必填）、--user（必填）（initContainer.go:78-148、150-162）。
- F-111：引导按序创建标记文件 /run/.toolboxenv（旧名 legacy）与 /run/.toolbxenv（新名）（initContainer.go:166-182）。
- F-112：TOOLBX_DELAY_ENTRY_POINT（秒）sleep 延时；TOOLBX_FAIL_ENTRY_POINT 置正值直接报错退出（initContainer.go:184-200、891-916）。
- F-113：主机 /run/host/etc 存在时，将容器内 /etc/host.conf、/etc/hosts、/etc/localtime、/etc/resolv.conf 以符号链接重定向到 /run/host 对应文件（非链接才操作）（initContainer.go:202-242）。
- F-114：updateTimeZoneFromLocalTime 从 localtime 解析时区（搜索根 /run/host/usr/share/zoneinfo 与 /usr/share/zoneinfo）写 /etc/timezone；localtime 不存在写 UTC（initContainer.go:1176-1240）。
- F-115：--media-link/--mnt-link 在容器内造 /media→/run/media、/mnt→/var/mnt 符号链接（initContainer.go:244-258）。
- F-116：initContainerMounts 15 条 rbind 清单：/etc/machine-id、/run/libvirt、/run/systemd/journal、/run/systemd/resolve、/run/systemd/sessions、/run/systemd/system、/run/systemd/users、/run/udev/data、/run/udev/tags、/tmp（rslave）、/var/lib/flatpak、/var/lib/libvirt、/var/lib/systemd/coredump、/var/log/journal、/var/mnt（rslave）（initContainer.go:55-76、260-264）。
- F-117：/sys/fs/selinux 存在时 bind 到 /usr/share/empty 清空容器内 selinuxfs（initContainer.go:266-270）。
- F-118：mountBind 对源 stat：不存在静默跳过；目录 MkdirAll 后 `mount --rbind [-o flags] source target`；普通文件/socket 先创建占位文件再挂（initContainer.go:1004-1054）。
- F-119：configureUsers：用户不存在执行 useradd（--groups <sudo|wheel> --home-dir --no-create-home --password "" --shell --uid），存在执行 usermod（--append --groups ... --home ...）；随后 `passwd --delete root`（initContainer.go:800-866）。
- F-120：configureKerberos 在 /etc/krb5.conf.d/kcm_default_ccache 写入 `[libdefaults] default_ccache_name = KCM:`（目录/文件已存在则跳过）（initContainer.go:552-584）。
- F-121：configurePKCS11：存在 /etc/pkcs11/modules 且 p11-kit-client.so 与主机 server socket 均在时，写 /etc/pkcs11/modules/p11-kit-trust.module（module: p11-kit-client.so + server-address）（initContainer.go:586-649）。
- F-122：PKCS#11 三处环境保持：sshd_config.d/90-toolbx.conf（SetEnv P11_KIT_SERVER_ADDRESS）、profile.d/toolbx-pkcs11.sh（export，供 su）、sudoers.d/90-toolbx-pkcs11（Defaults env_keep，0440）（initContainer.go:651-776）。
- F-123：configureRPM 写 /usr/lib/rpm/macros.d/macros.toolbox：`%_netsharedpath /dev:/media:/mnt:/proc:/sys:/tmp:/var/lib/flatpak:/var/lib/libvirt`，让 RPM 把这些 bind mount 路径视为网络共享路径不归属任何包（initContainer.go:778-798）。
- F-124：NVIDIA CDI 引导：从 $RUNTIME/toolbox/cdi-nvidia.json 读 spec（不存在跳过）；Mounts 校验后 bind（HostPath 自动加 /run/host 前缀，默认 bind 类型）；仅处理 createContainer hook，识别 `nvidia-cdi-hook create-symlinks`（解析 --link target::link 建符号链接）与 `nvidia-cdi-hook update-ldcache`（--folder 写 /etc/ld.so.conf.d/toolbx-nvidia.conf 后 ldconfig）（initContainer.go:286-308、417-550、936-985）。
- F-125：引导完成后写初始化戳记文件（chown 给容器用户），随后进入永久事件循环：fsnotify watch /run/host/etc（localtime 变化同步 /etc/timezone）+ 24h ticker（触发 updatedb）+ goroutine runUpdateDb（initContainer.go:322-394、918-933、1122-1126）。
- F-126：fsnotify/EMFILE/ENFILE/ENOMEM、ENOSPC 等资源耗尽降级为不监视而非失败（initContainer.go:332-355）。
- F-127：redirectPath 删除原路径（EBUSY 报 mount point 错误）后 Symlink；sanitizeRedirectionTarget 对主机侧绝对死链自动补 /run/host 前缀（initContainer.go:1056-1174）。

## G. enter/run 执行期事实

- F-130：enter 把 `$SHELL -l`（SHELL 缺失时 getent passwd <uid> 解析）作为命令调 runCommand（emitEscapeSequence=true、fallbackToBash=true、pedantic=false）（enter.go:117-127；cmd/utils.go:387-423）。
- F-131：run 选项 -c/--container、-d/--distro、--preserve-fds、-r/--release；SetInterspersed(false)；必须带命令参数（run.go:72-140）。
- F-132：runCommand 容器缺失三分支：0 容器→提示/自动 createContainer；仅 1 个容器且查的是默认容器→改用该容器；多容器→报错要求 --container（run.go:188-249）。
- F-133：Inspect 后检查 entry point 必须为 "toolbox"，否则报 "too old ... Recreate with Toolbx version 0.0.97 or newer"（run.go:257-268）。
- F-134：旧容器挂载 /run/host/monitor 时警告 deprecated 并调 org.freedesktop.Flatpak.SessionHelper.RequestSession（run.go:518-545；utils.go:210-237）。
- F-135：每次 run/enter 主机侧 nvidia.GenerateCDISpec()：探测失败分 ErrNVMLDriverLibraryVersionMismatch（报错内核/用户态驱动不匹配）与 ErrPlatformUnsupported（静默跳过）；成功则 Env 注入并在容器首次启动时把 spec 写到 cdi-nvidia.json（run.go:274-309）。
- F-136：startP11KitServer 对 $RUNTIME/toolbox/pkcs11.lock 加锁，socket 不存在时执行 `p11-kit server --name <socket> --provider p11-kit-trust.so pkcs11:model=p11-kit-trust?write-protected=yes`，注入 P11_KIT_SERVER_ADDRESS（run.go:1051-1111）。
- F-137：容器未运行（EntryPointPID<=0）时 startContainer；start 失败且 stderr 含 "use system migrate to mitigate" 时按 cgroups 版本选 runc(v1)/crun(v2) 做 system migrate 再重试（run.go:299-338、1012-1049）。
- F-138：ensureContainerIsInitialized 等待戳记：fsnotify watch runtime 目录为主、1 秒轮询降级、25 秒超时；TOOLBX_RUN_USE_POLLING 可强制轮询；同时 `podman logs --follow` 流式转发 entry point 日志（logfmt 解析 level/msg，"Error: " 前缀行收集为致命错误）（run.go:609-758、886-897、929-1010）。
- F-139：exec argv：`podman [--log-level] exec [--detach-keys ""] <保留变量 --env=> --interactive --preserve-fds N [--tty] --user <用户名> --workdir <cwd> <container> capsh --caps= -- [--login] -c 'exec "$@"' bash <命令...>`（run.go:547-607）。
- F-140：TTY 仅在 stdin+stdout 均为终端时分配；--detach-keys "" 需要 podman ≥1.8.1（run.go:367-395）。
- F-141：进入/退出时输出 OSC 777 转义序列（`\033]777;container;push;<name>;toolbox;<uid>\033\\` 与 pop），供终端（GNOME Console/VTE）标记容器会话（run.go:411-425）。
- F-142：退出码处理：0 成功；125 podman exec 自身失败；126 命令不可执行；127 时区分：工作目录不存在→回落 $HOME（仅一次）、命令不存在且允许回落→/bin/bash -l（仅一次）、toolbox 自身缺失→透传 127（run.go:427-492、61-62）。
- F-143：isCommandPresent/isPathPresent 通过 `podman exec --user <u> <c> sh -c 'command -v/test -d "$1"'` 探测（run.go:848-884）。

## H. NVIDIA/终端/Shell 集成事实

- F-150：nvidia.GenerateCDISpec 用 go-nvlib info 探测：HasDXCore（Windows 不支持）、HasNvml + nvml.Init（ERROR_DRIVER_NOT_LOADED→跳过，ERROR_LIB_RM_VERSION_MISMATCH→驱动不匹配错误）、IsTegraSystem；两者皆无→ErrPlatformUnsupported（nvidia.go:47-100）。
- F-151：用 nvcdi.New 禁用 HookEnableCudaCompat，GetCommonEdits 后 nvspec.New 生成 CNCF CDI spec（nvidia.go:102-127）。
- F-152：pkg/term 封装 unix termios：GetState（TCGETS）、SetState（TCSETS）、IsTerminal、NewStateFrom + WithVMIN/WithVTIME/WithoutECHO/WithoutICANON 选项（term.go:25-80）。
- F-153：下载提示二段交互用 termios 切 raw 模式（VMIN=1/VTIME=0/关 ECHO/关 ICANON）配合 eventfd+poll 实现可取消的确认输入与输入丢弃（create.go:836-946；cmd/utils.go:76-262、435-484）。
- F-154：profile.d/toolbox.sh 仅在 bash/zsh 且交互式（$PS1 非空）加载；主机 Silverblue 变体（workstation/silverblue/kinoite/sericea，存在 /run/ostree-booted）首次打印主机欢迎语（profile.d/toolbox.sh:4-47）。
- F-155：容器内（/run/.containerenv + /run/.toolbxenv）bash/zsh 提示符前缀洋红色 ⬢（PS1 重写），首次打印 Toolbx 欢迎语（stub 文件去重）（toolbox.sh:49-76）。
- F-156：容器内 VTE 终端版本 ≥3405 且无 vte.sh 时置 PROMPT_COMMAND=" "；并对 $TERM 做 terminfo 存在性检查输出告警（toolbox.sh:78-101）。
- F-157：list 命令输出两张 tabwriter 表（IMAGE ID/NAME/CREATED；CONTAINER ID/NAME/CREATED/STATUS/IMAGE NAME），运行中容器在终端下亮绿色；仅认 toolbox 标签的对象（list.go:133-220）。
- F-158：rm -a/--all 删全部 Toolbx 容器、-f/--force 强删运行/暂停容器；rmi 同构 -a/-f（rm.go:32-54；rmi.go:48-54）。
- F-159：completion.go 提供 7 个补全函数：completionEmpty、completionCommands、completionContainerNames(Filtered)、completionDistroNames、completionImageNames(Filtered)（completion.go:59-163）。

## I. 镜像资产事实

- F-170：images/ 下四族：fedora f28-f39（12 个版本目录）、rhel 8.5-9.3（8 个）、ubuntu 16.04-26.04（8 个，含 25.10）、arch 1 个，另 images/test/busybox（目录实测）。
- F-171：fedora f39 Containerfile：FROM registry.fedoraproject.org/fedora:39；LABEL com.github.containers.toolbox="true" 等 6 个标签；去 nodocs、coreutils/glibc 换全包、reinstall missing-docs、装 extra-packages、ensure-files 校验、断裂包检测、dnf clean all（images/fedora/f39/Containerfile:1-54）。
- F-172：ubuntu 24.04 Containerfile：FROM docker.io/library/ubuntu:24.04；同样打 toolbox 标签；unminimize、装 ubuntu-minimal/standard、libnss-myhostname、flatpak-xdg-utils；建 /etc/pkcs11/modules 与 /usr/share/empty；flatpak-spawn 软链到 /usr/bin；删除 ubuntu 用户；去 APT ESM hook（images/ubuntu/24.04/Containerfile:1-50）。
- F-173：data/config 与 data/tmpfiles.d 各有 meson.build 安装配置（data/ 目录结构）。

## J. 测试体系事实

- F-180：系统测试 BATS，位于 test/system，18 个 .bats 文件：001-version、002-help、101-create、102-list、103-container、104-run、105-enter、106-rm、107-rmi、108-completion、201-ipc、203-network、206-user、210-ulimit、211-dbus、220-environment-variables、230-cdi、250-kerberos、270-rpm、501-create、504-run、505-enter（目录实测 22 个）。
- F-181：依赖 awk/bats/coreutils/httpd-tools/openssl/podman/skopeo/toolbox；内嵌 bats-support+bats-assert 两个 git submodule（test/system/README.md:11-26）。
- F-182：运行方式 `bats ./test/system/`，非标准安装路径用 TOOLBX 环境变量；建议 TMPDIR=/var/tmp（README.md:28-55）。
- F-183：测试自带 OCI registry localhost:50000（需认证 user/user），默认镜像 fedora-toolbox:34（README.md:82-95）。
- F-184：230-cdi.bats 用 data/ 下 29 个 CDI JSON 夹具（实测枚举：cdi-empty 1 个；cdi-hooks 8 个 00/01/02/10/11/12/14/15；cdi-hooks-create-symlinks 17 个 00..08+30..37；cdi-mounts 3 个 10/11/12）（test/system/data 目录实测）。
- F-185：playbooks/ 11 个 Ansible playbook：build、dependencies-*（centos-9-stream/common/fedora-coreos/fedora-restricted/fedora）、setup-env、system-test-commands-options、system-test-runtime-environment-arch-fedora/ubuntu、unit-test（playbooks/ 目录实测 11）。
- F-186：CI：.github/workflows 3 个（arch-images、ubuntu-images、ubuntu-tests），另有 .zuul.yaml（Zuul CI）（目录实测）。
- F-187：测试命名规范 `[command]: <描述>`，失败用例以 "Try to..." 开头；setup/teardown 隔离（README.md:56-80）。

## K. 文档与演进事实

- F-190：doc/ 10 个 man 页源：9 个 section 1（toolbox、toolbox-create、toolbox-enter、toolbox-help、toolbox-init-container、toolbox-list、toolbox-rm、toolbox-rmi、toolbox-run）+ 1 个 section 5（toolbox.conf.5），go-md2man 构建（目录实测 10）。
- F-191：toolbox(1) 记载支持主机发行版：Arch、Fedora、RHEL ≥8.5、Ubuntu；不支持的主机回落 Fedora；发行版/版本组合表 arch:latest|rolling、fedora:<n>|f<n>、rhel:M.m、ubuntu:YY.MM（doc/toolbox.1.md:51-74）。
- F-192：toolbox-create(1) 明确 entry point 为 `toolbox init-container`，解释 OCI 容器不可变、运行时配置以向旧容器应用新版 Toolbx 改进的动机（doc/toolbox-create.1.md:25-89）。
- F-193：toolbox.conf(5)：TOML，仅 [general] 段 distro/image/release；查找顺序 /etc/containers/toolbox.conf → $XDG_CONFIG_HOME/containers/toolbox.conf（doc/toolbox.conf.5.md:6-48）。
- F-194：NEWS 0.3：mapstructure 升至 2.4.0（GHSA-2464-8j7c-4cjm）；Flatpak SessionHelper 路径废弃；p11-kit ≥0.25.6 用 socket 配置文件；修复 su/sudo CA 证书回归（NEWS:1-26）。
- F-195：NEWS 0.2：nvidia-container-toolkit ≥1.17.8（CVE-2025-23266/23267）；Go ≥1.22；Ubuntu 25.04 镜像；0.1.2 引入主机 CA 证书访问（p11-kit server，RHEL UBI 镜像当时未启用）（NEWS:28-80）。
- F-196：GOALS.md 非目标：不支持多运行时（仅 Podman）、不在 Podman 之上堆大功能（应推上游）、不做与主机松耦合的强沙箱容器（GOALS.md:14-20）。
- F-197：GOALS.md 用例：开发者（多数 rootless、少数需 root）、桌面（D-Bus/显示转发）、无头环境、GDB/strace；调试（bpftrace/strace 主机进程、systemctl、rpm-ostree）；Silverblue/CoreOS/RHEL CoreOS（对齐 oc debug node）（GOALS.md:22-66）。

## L. 计数断言（V 阶段独立复核口径）

- C-01：src/cmd 下非测试 .go 文件数（实测）：completion/create/enter/help/initContainer/list/rm/rmi/root/rootDefault/rootMigrationPath/run/utils = 13 个 + root_test.go = 14。
- C-02：src/pkg 子包数：nvidia/podman/shell/skopeo/term/utils/version = 7（cmd-source 旧文称 8 个包含根 pkg 计数口径，本轮以子目录 7 为准）。
- C-03：initContainerMounts 条目数 = 15（initContainer.go:55-76，逐条数）。
- C-04：podman create 固定 namespace/安全相关 flag 数：--cgroupns/--dns/--hostname/--ipc/--label/--name/--network/--no-hosts/--pid/--privileged/--security-opt/--ulimit/--userns/--user = 14 个参数项（不含 volume）。
- C-05：保留环境变量白名单 = 43 个（utils.go:82-126；脚本实测）。
- C-06：支持发行版 = 4（arch/fedora/rhel/ubuntu）。
- C-07：man 页 = 10（9 个 .1 + 1 个 .5；目录实测）。
- C-08：test/system .bats 文件 = 22（含 101-108、201/203/206/210/211/220/230/250/270、501/504/505、001/002）。
- C-09：Go 直接依赖 = 18（go.mod require 第一段）。
- C-10：images 族 = 4（arch/fedora/rhel/ubuntu）+ test/busybox。
