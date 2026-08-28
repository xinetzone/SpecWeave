# scrapli2 源码事实清单（第二批：全子文件夹覆盖扩展）

> 基于 `external/libs/scrapli/` 未覆盖子文件夹（examples/、tests/、docs/、scrapli/definitions/、scrapli/lib/、.github/）阅读提取。
> 与 `ssh-python-okf-wiki/scrapli-facts.md`（F-001~F-133）独立编号。零推测，仅记录客观存在内容。

## 示例体系总览（examples/README.md）

- F-001: examples/README.md 说明所有示例（除非特定示例另有说明）目标为 "scrapli_clab" containerlab testbed 拓扑中的 srlinux 设备，具体为该拓扑的 "ci" 变体，可在任意 linux 或 darwin 设备上运行且仅使用公开可用镜像（examples/README.md:1-5）。
- F-002: examples/README.md 记录在仓库根目录运行 `make run-clab-ci` make 目标启动测试拓扑，需要 docker（examples/README.md:7-9）。
- F-003: examples/README.md 说明拓扑会启动一个绑定 docker sock 的 launcher pod，使 containerlab 在 darwin 主机上也可原生运行（examples/README.md:11-12）。
- F-004: examples/README.md 说明 "ci" 变体拓扑包含一个 srlinux 设备、一个 netopeer netconf server，以及一个可测试 proxy-jump ssh 行为的 dummy linux container（examples/README.md:14-15）。
- F-005: examples/README.md 记录 srlinux 设备暴露 SSH/Telnet/Netconf 端口 22/23/830，darwin 用户的 NAT 端口为 21022/21023/21830，凭据为 `admin` / `NokiaSrl1!`（examples/README.md:24-26）。
- F-006: examples/README.md 说明每个示例按运行系统选择端口（检测 darwin 则 SSH 连 21022）（examples/README.md:28-29）。
- F-007: examples/README.md 说明示例支持通过环境变量覆盖 platform（srlinux）、host、port、username、password（examples/README.md:31-33）。

## examples/cli/（12 个示例目录）

- F-008: async_usage 示例 README 主题：连接目标设备并异步执行 `show version`，同时运行后台任务以体现 async/await 交错（examples/cli/async_usage/README.md:1-6）。
- F-009: async_usage/main.py 使用 `async with cli as c` 上下文管理器，调用 `await c.send_input_async(input_="show version")`（examples/cli/async_usage/main.py:25-39）。
- F-010: async_usage/main.py 创建 5 个 `Cli` 实例（`AuthOptions(username/password)`），通过 `asyncio.as_completed` 并发执行，入口为 `asyncio.run(main())`（examples/cli/async_usage/main.py:42-75）。
- F-011: custom_definition 示例 README 主题：说明 platform definitions 的概念，以及如何通过自定义 YAML 定义文件接入未内置平台（examples/cli/custom_definition/README.md:1-13）。
- F-012: custom_definition/main.py 通过 `Cli(definition_file_or_name=...)` 加载本地 `foo_bar.yaml` 定义文件，随后调用 `c.send_input(input_="show version")`（examples/cli/custom_definition/main.py:16-35）。
- F-013: handling_interactions 示例 README 主题：处理设备上的半交互式提示（如配置写入确认、删除文件确认），复杂场景建议使用 `read_with_callbacks`（examples/cli/handling_interactions/README.md:1-7）。
- F-014: handling_interactions/main.py 使用 `c.send_prompted_input(...)`，参数包含 `input_`、`prompt`、`prompt_pattern`、`response`、`requested_mode="bash"`（examples/cli/handling_interactions/main.py:28-39）。
- F-015: input_modes 示例 README 主题：设备可能存在不同 mode/权限级别，示例展示如何按定义中的 mode 发送输入（examples/cli/input_modes/README.md:1-5）。
- F-016: input_modes/main.py 先调用 `c.enter_mode(requested_mode="configuration")`，再调用 `c.send_input(input_="show version", retain_trailing_prompt=True)`（examples/cli/input_modes/main.py:28-47）。
- F-017: logging_setup 示例 README 主题：使用标准 Python logging 进行日志配置（examples/cli/logging_setup/README.md:1-3）。
- F-018: logging_setup/main.py 调用 `logging.basicConfig(level=logging.DEBUG, ...)` 后创建 `Cli` 并调用 `c.send_input(..., retain_trailing_prompt=True)`（examples/cli/logging_setup/main.py:17-40）。
- F-019: misc_options 示例 README 主题：覆盖 `send_input` 的多种选项，包括是否保留输入/尾随 prompt、`input_handling` 参数、operation timeout（examples/cli/misc_options/README.md:1-6）。
- F-020: misc_options/main.py 展示 `send_input(..., retain_trailing_prompt=True/False)`、`retain_input=True`、`operation_timeout_ns=...`、`input_handling=InputHandling.EXACT` 的用法（examples/cli/misc_options/main.py:31-99）。
- F-021: output_parsing 示例 README 主题：使用 textfsm / ntc-templates 将设备非结构化输出解析为结构化对象（examples/cli/output_parsing/README.md:1-6）。
- F-022: output_parsing/main.py 调用 `result.textfsm_parse(...)` 解析单条结果，调用 `results.textfsm_parse(..., index=1, to_dict=False)` 解析多条结果（examples/cli/output_parsing/main.py:29-62）。
- F-023: proxy_jump_cli 示例 README 主题：使用 libssh2 和 bin transport 实现 proxy jump——先连接 bastion host，再跳连目标设备（examples/cli/proxy_jump_cli/README.md:1-11）。
- F-024: proxy_jump_cli/main.py 中 bin transport 通过 `TransportBinOptions(ssh_config_path=...)` 配置代理跳转；ssh2 transport 通过 `TransportSsh2Options(proxy_jump_host/username/password/...)` 参数跳转（examples/cli/proxy_jump_cli/main.py:42-85）。
- F-025: read_callbacks 示例 README 主题：`read_with_callbacks` 适用于终端服务器、设备 console、零接触 provisioning、tail 日志或长输出触发回调场景（examples/cli/read_callbacks/README.md:1-8）。
- F-026: read_callbacks/main.py 调用 `c.read_with_callbacks(initial_input="tail -f /var/log/messages", callbacks=[...])`，回调对象为 `ReadCallback(name/contains/callback/once/completes)`（examples/cli/read_callbacks/main.py:51-82）。
- F-027: sending_configs 示例 README 主题：向设备发送配置；配置本质上是发送到设备的输入（examples/cli/sending_configs/README.md:1-4）。
- F-028: sending_configs/main.py 使用 `send_input(..., requested_mode="configuration", retain_trailing_prompt=True)` 发送配置模式输入，使用 `send_inputs(inputs=[...], requested_mode="configuration")` 批量发送配置/提交命令（examples/cli/sending_configs/main.py:35-76）。
- F-029: sending_inputs 示例 README 主题：`Cli` 的三种输入发送方法：`send_input`、`send_inputs`、`send_inputs_from_file`（examples/cli/sending_inputs/README.md:1-10）。
- F-030: sending_inputs/main.py 分别调用 `c.send_input(input_="show version")`、`c.send_inputs(inputs=[...])`、`c.send_inputs_from_file(f=...)`（examples/cli/sending_inputs/main.py:29-53）。
- F-031: session_recorder 示例 README 主题：配置 Scrapli 将底层 session 的所有读取记录到文件（examples/cli/session_recorder/README.md:1-4）。
- F-032: session_recorder/main.py 通过 `Cli(..., session_options=SessionOptions(recorder_path=...))` 配置会话记录路径，随后发送 `show version`（examples/cli/session_recorder/main.py:17-45）。

## examples/netconf/（4 个示例目录）

- F-033: edit_config 示例 README 主题：展示 `edit-config` RPC，以及锁定、提交、解锁配置数据 store 的流程（examples/netconf/edit_config/README.md:1-4）。
- F-034: edit_config/main.py 创建 `Netconf` 连接后依次调用 `lock()`、`edit_config()`、`commit()`、`unlock()`，最后恢复设备名配置（examples/netconf/edit_config/main.py:16-69）。
- F-035: get_operations 示例 README 主题：覆盖 Netconf 的 `get`、`get-config`、`get-schema`、`get-data` RPC（examples/netconf/get_operations/README.md:1-3）。
- F-036: get_operations/main.py 展示 `get_config()`、`get()`、`get_schema()` 调用，并连接 Netopeer 服务器调用 `get_data()`（examples/netconf/get_operations/main.py:20-67）。
- F-037: proxy_jump_netconf 示例 README 主题：与 CLI 版本类似，展示 Netconf 连接同样支持 ProxyJump（examples/netconf/proxy_jump_netconf/README.md:1-4）。
- F-038: proxy_jump_netconf/main.py 分别展示基于 `TransportBinOptions` 的 SSH config 代理跳转，以及基于 `TransportSsh2Options` 的 `proxy_jump_*` 参数跳转（examples/netconf/proxy_jump_netconf/main.py:22-77）。
- F-039: subscriptions 示例 README 主题：Netconf subscriptions 较复杂，Scrapli 未封装多种 RFC 创建订阅方式；示例通过 `raw_rpc` 创建订阅，分别用 `get_next_notification` 与 `get_next_subscription` 获取消息（examples/netconf/subscriptions/README.md:1-9）。
- F-040: subscriptions/main.py 展示 `create-subscription`（raw_rpc）+ `get_next_notification()` 流程，以及 `establish-subscription`（raw_rpc）+ `get_subscription_id()` + `get_next_subscription()` 流程（examples/netconf/subscriptions/main.py:22-107）。

## docs/

- F-041: docs/index.md 说明 Scrapli 是 CLI 与 Netconf 交互库，包含 Zig 核心 `libscrapli`、Python bindings、Go bindings，并列出 CLI/Netconf 主要能力（docs/index.md:6-18）。
- F-042: docs/details.md 描述 `telnet`、`bin`、`ssh2` 三种 transport 的特点与适用场景，`bin` transport 支持 ProxyJump 等 SSH 特性（docs/details.md:8-17）。
- F-043: docs/details.md 说明 CLI 设备交互通过 YAML platform definition 配置，包括 prompt、mode、连接打开/关闭指令等（docs/details.md:19-27）。
- F-044: docs/details.md 逐条解释 YAML 顶层字段：`prompt_pattern`、`prompt_excludes`、`default_mode`、`modes`、`failure_indicators`、`on_open_instructions`、`on_close_instructions`（docs/details.md:80-94）。
- F-045: docs/installation.md 记录 PyPI 上存在 `scrapli` 与 `scrapli2` 两个项目，为同一代码库，唯一差异是版本方案（`scrapli` 用 calendar versioning，`scrapli2` 用 semantic versioning）（docs/installation.md:8）。
- F-046: docs/installation.md 记录安装命令 `pip install scrapli` / `pip install scrapli2`，以及 `pip install git+https://github.com/carlmontanari/scrapli`、指定 commit hash/branch、`#egg=scrapli2` 的安装方式（docs/installation.md:10-35）。
- F-047: docs/installation.md 记录从源码安装：`git clone` 后 `pip install .`（docs/installation.md:37-43）。
- F-048: docs/installation.md 记录可选 extras：`pip install scrapli[textfsm]`、`pip install scrapli[genie]`、`pip install scrapli[full]`（两者兼得）（docs/installation.md:45-58）。
- F-049: docs/installation.md Go 部分：`go get github.com/scrapli/scrapligo/v2`；libscrapli 首次运行时自动获取并缓存，缓存路径由 `LIBSCRAPLI_CACHE_PATH` 环境变量设定，默认 `XDG_CACHE_HOME`（若设置）、linux 为 `$HOME/.cache/scrapli`、darwin 为 `$HOME/Library/Caches/scrapli`（docs/installation.md:61-84）。
- F-050: docs/installation.md 记录 Go 手动获取 libscrapli 的方式：`go run build/write_libscrapli_to_cache/main.go`，或从 libscrapli releases 下载对应平台构建（docs/installation.md:86-97）。
- F-051: docs/installation.md Zig 部分：`zig fetch --save=libscrapli https://github.com/scrapli/libscrapli/archive/refs/tags/v0.0.1-rc.1.tar.gz`，build.zig 中通过 `b.dependency("libscrapli", ...)` 与 `libscrapli.module("scrapli")` 集成（docs/installation.md:101-163）。
- F-052: docs/installation.md 记录静态链接的 libscrapli 共享对象在 libscrapli release 页面构建发布（docs/installation.md:165-168）。
- F-053: docs/migration.md "General Changes"：所有核心逻辑位于 Zig（libscrapli）；Python 和 Go 包是围绕 libscrapli 的薄、惯用封装（docs/migration.md:8）。
- F-054: docs/migration.md：scrapli/scrapligo 离开 libscrapli 无法工作（docs/migration.md:9）。
- F-055: docs/migration.md：libscrapli 取消了发送 "configurations" 的概念，只有 inputs，可在任意 "mode"（包括 "configuration" mode）发送；generic 与 network driver 的划分不复存在（docs/migration.md:10）。
- F-056: docs/migration.md：scrapli community 已被 scrapli definitions 取代（自 scrapligo 起 definitions 严格为 YAML），更可移植但灵活性降低（docs/migration.md:11）。
- F-057: docs/migration.md：使用 Cli 连接不再必须指定 platform——未提供时自动选择一个非常通用的默认平台；文档建议仍提供 platform 以匹配目标设备（如正确禁用分页）（docs/migration.md:12）。
- F-058: docs/migration.md：privilege levels 被 "modes" 取代，主要是语义变化——仍可在给定 mode/privilege level 发送输入，多数 definitions 会在连接时尝试进入合理的默认/初始 mode（docs/migration.md:13）。
- F-059: docs/migration.md：NETCONF 支持总体增强——未支持全部 RFC RPC，但提供 "raw" RPC 方法（`raw_rpc`）可发送任意内容到 NETCONF 服务器（docs/migration.md:14）。
- F-060: docs/migration.md：默认 `bin` transport 默认禁用 strict key checking；默认不再以 `-F /dev/null` 跳过默认 ssh config 文件——即默认自动遵循用户 ssh config 文件设置（docs/migration.md:15-16）。
- F-061: docs/migration.md：`auth_secondary`（历史上作为 enable 密码）已移除，替换为 *lookups*（lookup 键与其值的数组），definition 中以 `__lookup::enable` 形式引用 key 为 "enable" 的 lookup（docs/migration.md:17）。
- F-062: docs/migration.md "Python Changes"：不再支持 paramiko、asyncssh、ssh2-python——所有 transport 逻辑在 libscrapli/C 依赖中实现（docs/migration.md:22）。
- F-063: docs/migration.md：TTP 支持已移除（docs/migration.md:23）。
- F-064: docs/migration.md：除必选参数外全部强制为关键字参数（通过 `*`）（docs/migration.md:24）。
- F-065: docs/migration.md：NETCONF 不再是独立包（scrapli-netconf），全部 NETCONF 功能位于 libscrapli，scrapli 包将其与 CLI 功能一同暴露（docs/migration.md:25）。
- F-066: docs/migration.md：仅支持 Python 3.10+；文档称经少量修改最低可回溯至约 3.7（类型注解是需要 3.10 的主因）（docs/migration.md:26）。
- F-067: docs/migration.md：不再有 mixin——同一 `Cli`/`Netconf` 类同时提供同步与异步风格方法，如 `get_config_async` 与 `get_config`（docs/migration.md:27）。
- F-068: docs/migration.md：scrapli community 弃用对少数平台（文档点名 FortiOS）的 "extra" 定制有影响，此类定制需社区/个人自行维护（docs/migration.md:28）。
- F-069: docs/migration.md：Python 现支持处理 NETCONF subscriptions——旧版因 channel 数据处理方式无法实现（docs/migration.md:29）。
- F-070: docs/migration.md "Go Changes"：Go 包不再有 timeout options，超时由 contexts 管理；当前无 "bring your own" transport 选项；Go 不再直接支持 NETCONF subscription 建立，但支持获取 subscription/notification 消息（docs/migration.md:32-37）。
- F-071: docs/examples/python.md 展示 `Netconf` 连接创建、上下文管理器、调用 `get_config()` 并打印 `Result.result`（docs/examples/python.md:38-56）。

## scrapli/lib/

- F-072: scrapli/lib/README.md 说明该包存放各平台的 libscrapli 共享对象；版本控制中无内容，wheel 或 sdist 安装后填充；ffi loader 在未设置 override 路径时从此处加载 libscrapli 共享对象（scrapli/lib/README.md:1-7）。
- F-073: scrapli/lib/README.md 记录源码开发方式：克隆仓库后 `pip install .` 或 `pip install -e .` 会构建当前平台的共享对象并放入该目录（scrapli/lib/README.md:7）。

## tests/（functional + unit + golden 体系）

- F-074: tests/functional/conftest.py 的 `cli` fixture 按 `platform`/`transport` 参数构造 `Cli`：`transport == "bin"` 时注入 `TransportBinOptions()`，否则注入 `TransportSsh2Options()`（tests/functional/conftest.py:72-112）。
- F-075: tests/functional/conftest.py 的 CLI golden 比对 fixture 根据测试名生成 `tests/functional/golden/cli/{filename}` 路径；支持 `--update` 命令行参数写入 golden，否则读取 golden 并对清洗后的输出断言（tests/functional/conftest.py:115-148）。
- F-076: tests/functional/conftest.py 的 `netconf` fixture 按 `platform`/`transport` 构造 `Netconf`，bin/ssh2 分别注入 `TransportBinOptions`/`TransportSsh2Options`；Netconf golden 比对支持相似度阈值（非精确匹配场景）（tests/functional/conftest.py:151-240）。
- F-077: tests/functional/test_cli.py 的 `test_get_prompt` 使用 `@pytest.mark.parametrize` 覆盖 `platform`/`transport`，调用 `cli_assert_result` 与 golden 文件比对（tests/functional/test_cli.py:48-55）。
- F-078: tests/functional/test_cli.py 定义 `ENTER_MODE_ARGNAMES`/`ARGVALUES`/`IDS` 参数矩阵，覆盖 arista_eos/nokia_srl 平台与 bin/ssh2/telnet transport 组合（tests/functional/test_cli.py:71-210）。
- F-079: tests/functional/test_transport_bin.py 的 `test_proxy_jump_bin` 直接构造 `Cli` 并注入 `TransportBinOptions(ssh_config_path=...)`，验证 bin transport 的 proxy jump 行为（tests/functional/test_transport_bin.py:32-80）。
- F-080: tests/functional/ 目录含测试文件：conftest.py、test_cli.py、test_examples.py、test_netconf.py、test_transport_bin.py、test_transport_ssh2.py（tests/functional/ 目录清单）。
- F-081: tests/functional/golden/cli/ 下 golden 目录命名模式为 `<操作>[-async]-<平台>-<transport>[-变体]`，例：`enter-mode-arista-eos-bin-escalate-with-password`、`send-input-async-nokia-srl-bin-big-output`、`send-input-arista-eos-bin-same-mode-pagination-retain-input-and-trailing-prompt`（tests/functional/golden/cli/ 目录清单）。
- F-082: tests/functional/golden/netconf/ 下 golden 目录命名模式为 `<rpc 操作>[-async]-<服务器>-<transport>[-变体]`，例：`edit-config-netopeer-bin-simple`、`raw-rpc-create-subscription-async-netopeer-ssh2-simple`、`get-async-netopeer-bin-filtered-xpath`（tests/functional/golden/netconf/ 目录清单）。
- F-083: tests/functional/golden/netconf/ 中 `kill-session` 系列 golden 对应 nokia-srl 服务器（如 `kill-session-async-nokia-srl-bin-simple`），其余 netconf golden 主要对应 netopeer 服务器（目录清单）。
- F-084: tests/functional/fixtures/ 含 SSH 测试密钥与配置：`libscrapli_test_ssh_key(.pub)`、`libscrapli_test_ssh_key_passphrase(.pub)`、`scrapli-jumper-key`、`ssh_config_darwin`、`ssh_config_linux`（tests/functional/fixtures/ 目录清单）。
- F-085: tests/unit/dummy_ssh_server/main.go 创建 SSH server：仅接受 `admin/password` 凭据，添加 ed25519 host key，监听 `0.0.0.0:2222`（tests/unit/dummy_ssh_server/main.go:91-128）。
- F-086: tests/unit/dummy_ssh_server/main.go 的连接处理只接受 `session` channel（忽略其他请求），连接后写入 `router> ` prompt（tests/unit/dummy_ssh_server/main.go:159-199）。
- F-087: tests/unit/dummy_ssh_server/main.go 对输入的处理：识别 `show version` 返回模拟版本输出，识别 `exit` 断开连接，否则回显输入并重新显示 prompt（tests/unit/dummy_ssh_server/main.go:222-244）。
- F-088: tests/unit/ 目录结构：dummy_ssh_server/（go.mod、go.sum、main.go）、fixtures/、golden/、conftest.py；fixtures/ 与 golden/ 均按 cli/、netconf/ 分目录组织（tests/unit/ 目录清单）。
- F-089: tests/unit/fixtures/ 与 tests/unit/golden/ 的目录名一一对应（如 `send-input-simple-requires-pagination` 同时存在于两处），fixtures 存放 TEST Transport 的会话数据，golden 存放期望输出（tests/unit/ 目录清单）。
- F-090: tests/unit/fixtures/cli/ 覆盖的操作包括：send-input（simple/retain-*/input-handling-*/requires-pagination/acquire-non-default-mode 等变体）、send-inputs、send-inputs-from-file、send-prompted-input、enter-mode（escalate/deescalate/multi-stage-change/no-change 及 async 变体）、get-prompt、read（simple/user-sized）、read-with-callbacks（tests/unit/fixtures/cli/ 目录清单）。
- F-091: tests/unit/golden/netconf/ 含 `get-next-notification`、`get-next-subscription` golden 目录，与 examples/netconf/subscriptions 示例调用的 `get_next_notification()`/`get_next_subscription()` 方法对应（tests/unit/golden/netconf/ 目录清单）。
- F-092: tests/unit/golden/netconf/ 还含 `session-id` golden 目录（tests/unit/golden/netconf/ 目录清单）。

## scrapli/definitions/（44 个平台 YAML）

- F-093: scrapli/definitions/ 目录含 44 个平台 YAML 文件与 `__init__.py`（目录清单）。
- F-094: 44 个 YAML 完整清单：aethra_atosnt、alcatel_aos、arista_eos、aruba_aoscx、aruba_wlc、cisco_aireos、cisco_asa、cisco_cbs、cisco_ftd、cisco_iosxe、cisco_iosxr、cisco_nxos、cumulus_linux、cumulus_vtysh、datacom_dmos、datacom_dmswitch、default、dell_emc、dell_enterprisesonic、dlink_os、edgecore_ecs、eltex_esr、fortinet_fortios、fortinet_wlc、hp_comware、huawei_smartax、huawei_vrp、ipinfusion_ocnos、juniper_junos、mikrotik_routeros、nokia_srlinux、nokia_sros、nokia_sros_classic、nokia_sros_classic_aram、paloalto_panos、raisecom_ros、ruckus_fastiron、ruckus_unleashed、ruijie_rgos、siemens_roxii、ubiquiti_edgeswitch、versa_flexvnf、vyos_vyos、zyxel_dslam（scrapli/definitions/ 目录清单）。
- F-095: 按厂商归类：Cisco 系 7 个（aireos/asa/cbs/ftd/iosxe/iosxr/nxos）、Nokia 系 4 个（srlinux/sros/sros_classic/sros_classic_aram）、Aruba 2 个（aoscx/wlc）、Fortinet 2 个（fortios/wlc）、Cumulus 2 个（linux/vtysh）、Datacom 2 个（dmos/dmswitch）、Dell 2 个（emc/enterprisesonic）、Ruckus 2 个（fastiron/unleashed）、Huawei 2 个（smartax/vrp），其余厂商各 1 个（F-094 清单归纳）。
- F-096: cisco_nxos.yaml 顶层字段：`prompt_pattern`、`default_mode`、`modes`、`failure_indicators`、`on_open_instructions`、`on_close_instructions`、`ntc_templates_platform`、`genie_platform`（scrapli/definitions/cisco_nxos.yaml:1-67）。
- F-097: arista_eos.yaml 定义 exec/privileged_exec/configuration/bash 模式、密码输入指令、`failure_indicators`、`on_open_instructions`、`on_close_instructions`（scrapli/definitions/arista_eos.yaml:1-65）。
- F-098: nokia_srlinux.yaml 含全局 prompt、bash/exec/configuration 模式、`prompt_excludes` 字段（scrapli/definitions/nokia_srlinux.yaml:1-50）。
- F-099: huawei_vrp.yaml 含 privileged_exec/configuration 模式、复杂 prompt 正则、`failure_indicators`、on_open 时的 `screen-width` 指令（scrapli/definitions/huawei_vrp.yaml:1-56）。
- F-100: mikrotik_routeros.yaml 全文仅 9 行，只定义 `prompt_pattern`、`default_mode`、单模式 `cli` 与关闭指令（scrapli/definitions/mikrotik_routeros.yaml:1-9）。
- F-101: juniper_junos.yaml 含多模式定义、`failure_indicators`、`on_open_instructions`/`on_close_instructions`、`ntc_templates_platform`（scrapli/definitions/juniper_junos.yaml:1-88）。
- F-102: fortinet_fortios.yaml 含 exec 模式、on_open 时的 `config system console` 设置、关闭指令（scrapli/definitions/fortinet_fortios.yaml:1-20）。
- F-103: vyos_vyos.yaml 含 privileged_exec/configuration 模式、prompt 正则、`failure_indicators`、打开指令（scrapli/definitions/vyos_vyos.yaml:1-26）。
- F-104: scrapli/cli.py 默认从 `scrapli.definitions` 包加载 `{platform}.yaml` 定义文件；存在 `CLI_DEFINITIONS_PATH_OVERRIDE` 环境变量时从覆盖目录加载（scrapli/cli.py:500-515）。
- F-105: scrapli/cli.py 支持向 `definition_file_or_name` 传入 `LoadedDefinition` 对象或平台名/文件名；平台名赋给 `_platform_name` 并触发 `_load_definition()`（scrapli/cli.py:491-498）。
- F-106: scrapli/definition_options/ 目录含平台专属 Python 扩展模块（如 `mikrotik_routeros.py`），`Cli` 初始化时动态加载 `scrapli.definition_options.{platform}`（scrapli/definition_options/mikrotik_routeros.py:1-21；scrapli/cli.py:323-347）。

## .github/workflows/（7 个 CI 工作流）

- F-107: .github/workflows/ 含 7 个工作流文件：cicd.yaml、test.yaml、lint.yaml、docs.yaml、publish.yaml、release.yaml、validate.yaml（目录清单）。
- F-108: cicd.yaml 在 push（main 分支）、pull_request、workflow_dispatch 触发，包含 `lint` 与 `test` 两个 job，分别复用 `./.github/workflows/lint.yaml` 与 `./.github/workflows/test.yaml`（.github/workflows/cicd.yaml:1-15）。
- F-109: test.yaml 含 `os`/Python `version` 运行矩阵、checkout、setup-python、install、run 等步骤（.github/workflows/test.yaml:19-69）。

## G1 质量门自检

- 全部 109 条事实为代码/文档/目录清单中客观存在内容的记录，无"用于/目的是/设计为"式因果推断（F-095 为清单归纳计数，非行为推断）。
- 每条事实含源码相对路径（及行号或目录清单标注）。
- 覆盖检查：examples/cli（12 目录 ✅ F-008~F-032）、examples/netconf（4 目录 ✅ F-033~F-040）、examples/README.md（✅ F-001~F-007）、tests/functional+unit+golden（✅ F-074~F-092）、scrapli/definitions（44 全集清单 + 8 个采样 ✅ F-093~F-106）、docs/（✅ F-041~F-071）、scrapli/lib/（✅ F-072~F-073）、.github/workflows（✅ F-107~F-109）。
