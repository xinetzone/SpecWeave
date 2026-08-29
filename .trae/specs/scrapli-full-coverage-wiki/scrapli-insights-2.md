# scrapli2 架构洞察（第二批：全子文件夹覆盖扩展）

> 基于 `scrapli-facts-2.md`（F-001~F-109）提炼。每条洞察为四元组：陈述 + 证据 + 反常识 + 行动。

## 洞察 1：golden 文件测试法将"API 行为快照"固化为可审查的目录树，测试矩阵即文档

- **陈述**：scrapli2 的测试体系以"操作 × 平台 × transport × 变体"的笛卡尔积命名 golden 目录，目录名本身就是 API 行为的完整规格说明——读者不看测试代码，仅浏览 golden 目录树即可得知每个方法支持的参数组合与场景。
- **证据**：F-081（`send-input-arista-eos-bin-same-mode-pagination-retain-input-and-trailing-prompt` 等命名模式）、F-078（`ENTER_MODE_ARGNAMES/ARGVALUES/IDS` 参数矩阵覆盖 arista_eos/nokia_srl × bin/ssh2/telnet）、F-075（`--update` 参数支持 golden 重写）、F-089（unit fixtures 与 golden 目录名一一对应，fixtures 喂给 TEST Transport，golden 存期望输出）。
- **反常识**：多数网络库的测试用例藏在 pytest 函数体内，需要读代码才能理解覆盖范围；scrapli2 反其道而行——把覆盖矩阵外化为文件系统结构，`ls tests/functional/golden/cli/` 就是一份现成的 API 特性清单（含 async 变体、分页、retain 选项的每种组合）。
- **行动**：生成 `concepts/09-testing-system.md` 时以 golden 目录命名模式为主线讲解测试体系；写其他概念文档需要列举某方法支持的选项组合时，直接引用 golden 目录名作为权威证据，避免凭空列举参数组合。

## 洞察 2：44 个平台 YAML 的复杂度谱系跨越两个数量级，"最小可用定义"只需 3 个字段

- **陈述**：definitions 目录中平台定义的复杂度呈极端分布——最简的 mikrotik_routeros.yaml 仅 9 行（prompt_pattern + default_mode + 单模式 + 关闭指令），最复杂的 juniper_junos.yaml 达 88 行（多模式 + 升降级密码指令 + lookup 引用），且存在 default.yaml 作为不指定平台时的通用兜底；YAML 表达力边界之外的部分由 definition_options/ 下的 Python 模块补齐。
- **证据**：F-100（mikrotik_routeros.yaml 9 行）、F-101（juniper_junos.yaml 88 行）、F-094（清单含 default.yaml）、F-096~F-103（8 个采样平台的字段谱系）、F-106（definition_options/mikrotik_routeros.py Python 扩展 + Cli 初始化动态加载）、F-056/F-057（migration.md 记录 scrapli community→definitions YAML 化及默认平台自动选择）。
- **反常识**：直觉上会认为 44 个平台需要 44 套定制逻辑；实际上核心结构高度同构（prompt/modes/on_open/on_close/failure_indicators），差异只在 prompt 正则的复杂度和升降级指令的数量——纯 YAML 覆盖绝大多数平台，仅个别平台（如 FortiOS，见 F-068）需要超出 YAML 表达力的定制。为自定义平台写定义文件的门槛因此极低。
- **行动**：生成 `concepts/10-platform-catalog.md` 时按"字段共性 → 复杂度谱系（9 行到 88 行）→ default.yaml 兜底 → definition_options Python 钩子边界"四层递进组织；生成 `examples/` 相关文档时引用 custom_definition 示例证明 3 字段即可接入新平台。

## 洞察 3：官方示例体系是"containerlab 一键拓扑 + 环境变量覆盖"的可复现教学装置，而非孤立代码片段

- **陈述**：examples/ 的 16 个示例不是各自为政的脚本，而是共享同一运行时契约——全部目标指向 scrapli_clab containerlab "ci" 变体拓扑（srlinux + netopeer + proxy-jump dummy 容器），端口按宿主系统自适应（darwin 用 NAT 端口），且 platform/host/port/username/password 五个维度均可被环境变量覆盖，`make run-clab-ci` 一条命令即可拉起全部示例所需的后端环境。
- **证据**：F-001~F-007（examples/README.md 的拓扑说明、端口 NAT 映射 21022/21023/21830、凭据 admin/NokiaSrl1!、环境变量覆盖、make 目标）、F-004（ci 拓扑三容器构成与 proxy-jump/netconf/netopeer 一一对应示例需求）、F-036/F-040（get_operations 连接 Netopeer 服务器，subscriptions 示例依赖 netopeer）。
- **反常识**：常见开源库的 examples 假设用户"手头有台设备"或"自己搭环境"，导致示例不可复现；scrapli2 把示例的后端依赖整体容器化并版本化到独立仓库 scrapli_clab，让每个示例（包括 proxy-jump 这种需要 bastion host 的复杂场景）都可以在任意 linux/darwin 机器上真实跑通——示例使用的拓扑与 CI functional 测试面向相同类型的设备（F-004 与 F-083）。
- **行动**：生成 `concepts/12-repository-examples.md` 时以"共享拓扑契约"为纲组织 16 个示例的主题矩阵；3 篇新示例文档（proxy-jump、output-parsing、session-recorder）开篇说明运行前提（clab 拓扑或环境变量覆盖），代码基于官方示例改写。
