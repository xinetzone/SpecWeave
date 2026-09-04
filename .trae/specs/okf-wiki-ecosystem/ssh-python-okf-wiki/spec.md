# SSH/远程控制 Python 包 OKF Wiki 教程 - 产品需求文档

## Overview
- **Summary**: 在 awesome-okf-xs 文档库中新建 `networking/` 分组，为 6 个 SSH/远程控制相关的 Python 包（paramiko、fabric、asyncssh、pexpect、netmiko、scrapli）逐一生成符合 OKF v0.2 规范的系统化中文 Wiki 教程。每个知识束包含 concepts/（概念文档）、examples/（实战示例）、references/（信源登记）三层结构，通过 source-code-to-okf-wiki 的 R→I→E→V→C 五阶段工作流生成，确保零虚构 API、事实可溯源。
- **Purpose**: Python SSH/远程控制生态缺乏系统化的中文源码级教程。现有资料多为 API 速查或碎片化博客，读者难以理解各库的架构设计取舍（同步 vs 异步、底层协议 vs 高层封装、通用 SSH vs 网络设备专用）。本项目通过深度源码阅读生成可溯源的 OKF 知识束，帮助开发者从架构层面理解 SSH 协议实现、远程执行模型、交互式终端控制、多厂商设备抽象等核心主题。
- **Target Users**: Python 后端/运维开发工程师、网络自动化工程师、DevOps 工程师、需要学习 SSH 协议实现的进阶开发者、OKF 知识生态贡献者。

## Goals
- 为 paramiko（SSHv2 纯 Python 协议实现）生成完整知识束，覆盖 Transport/Channel/SSHClient/SFTPClient/认证体系/密钥管理/端口转发/服务端
- 为 fabric（基于 paramiko+invoke 的高层远程执行框架）生成知识束，覆盖 Connection/Config/Group/Remote Runner/Transfer/Tunnel/Executor
- 为 asyncssh（asyncio 异步 SSHv2 实现）生成知识束，覆盖 SSHClientConnection/SSHChannel/SSHStream/SSHProcess/SFTP/SCP/端口转发/认证框架
- 为 pexpect（纯 Python Expect 式交互式进程控制）生成知识束，覆盖 spawn/pxssh/PopenSpawn/fdspawn/expect 模式匹配/REPL wrap
- 为 netmiko（多厂商网络设备 SSH 库，基于 paramiko）生成知识束，覆盖 ConnectHandler/BaseConnection/ssh_dispatcher/SSHDetect/驱动继承体系/文件传输
- 为 scrapli（现代网络设备 CLI/NETCONF 自动化库）生成知识束，覆盖 Transport/Channel/Driver 三层架构、核心平台驱动、同步/异步双模式
- 新建 `bundles/networking/` 分组索引，建立 6 个知识束之间的交叉引用和学习路径
- 更新 `bundles/index.md` 总索引，注册 networking 分组
- 所有文档通过 Grep 级 API 真实性验证，零虚构类名/方法名

## Non-Goals (Out of Scope)
- 不覆盖 SSH 协议本身的 RFC 规范教学（聚焦 Python 库源码实现，非协议标准解读）
- 不生成非 Python 的 SSH 库教程（如 Go 的 golang.org/x/crypto/ssh、Rust 的 thrussh）
- 不覆盖 Ansible/SaltStack/Nornir 等大型自动化框架（它们构建于这些库之上，属于上层应用）
- 不为 scrapli 的 Zig 核心（libscrapli）生成深度文档（聚焦 Python API 层和架构关系）
- 不生成视频、交互式 Notebook 或可运行代码仓库（纯 Markdown 文档）
- 不修改 awesome-okf-xs 子项目的 .agents/ 规范文件
- 不覆盖 parallel-ssh/ssh2-python/spur 等次要库（6 个核心包已覆盖主流范式）

## Background & Context
- awesome-okf-xs 是玄境项目的 OKF（开源知识格式）文档库，已有 23 个分组、236 个知识束
- 现有分组包括 tooling/（含 pyinvoke）、python/、conda/、jupyter/ 等，但**无 networking/ 分组**
- source-code-to-okf-wiki Skill 已从 PyInvoke v3.0.3 实践中萃取，封装了 R→I→E→V→C 五阶段工作流和 7 个反模式防护
- seven-concepts-cmd Skill 提供方法论编排和 G1-G4 质量门，本项目属于"场景4：知识沉淀（R→I→E）"
- pyinvoke 知识束（bundles/tooling/pyinvoke/）是本项目的直接参考范例，包含 12 概念 + 5 示例 + 1 信源，共 23 文件
- 6 个包的依赖关系形成清晰的生态层次：paramiko 是基础层 → fabric/netmiko 是高层封装 → asyncssh 是异步替代 → pexpect 是交互控制（互补）→ scrapli 是现代网络自动化（多 transport 可插拔）
- 源码将通过 git clone 获取到 `external/libs/` 目录，与现有 pyinvoke、ninja 等源码存放方式一致

## Functional Requirements

- **FR-1**: 新建 `bundles/networking/` 分组目录，包含 `index.md`（分组导航，含生态关系图和学习路径）
- **FR-2**: 为 paramiko 生成 OKF 知识束（concepts/ + examples/ + references/ + index.md + log.md），概念文档不少于 10 篇
- **FR-3**: 为 fabric 生成 OKF 知识束，概念文档不少于 8 篇
- **FR-4**: 为 asyncssh 生成 OKF 知识束，概念文档不少于 10 篇
- **FR-5**: 为 pexpect 生成 OKF 知识束，概念文档不少于 8 篇
- **FR-6**: 为 netmiko 生成 OKF 知识束，概念文档不少于 8 篇
- **FR-7**: 为 scrapli 生成 OKF 知识束，概念文档不少于 8 篇
- **FR-8**: 每个知识束包含 references/ 信源登记文件，记录源码路径、版本、核心模块清单、公开 API
- **FR-9**: 每个知识束包含 examples/ 实战示例文档（每束 4-6 篇），代码示例基于真实源码 API
- **FR-10**: 所有文档使用 OKF v0.2 YAML frontmatter（type/title/description/tags/generated/verified/status/stale_after/sources）
- **FR-11**: 交叉引用使用 `/` 开头的 bundle-relative 路径，文档结尾有"相关概念"章节
- **FR-12**: 更新 `bundles/index.md` 总索引，注册 networking 分组及 6 个知识束条目
- **FR-13**: R 阶段为每个包提取编号事实清单（F-xxx），覆盖核心类定义、方法签名、参数、继承关系、数据流
- **FR-14**: I 阶段为每个包提炼 3-5 个核心架构洞察（陈述+证据+反常识+行动四元组）
- **FR-15**: V 阶段对文档中引用的每个关键类名/方法名执行 Grep 源码验证，修复所有虚构 API

## Non-Functional Requirements
- **NFR-1**: 所有文档正文使用中文，文件名使用 kebab-case 纯英文
- **NFR-2**: 每个概念文档 300-1500 字，代码块标注语言
- **NFR-3**: facts.md 中无推断性表述（"用于"/"目的是"/"设计为"等因果词），纯客观事实
- **NFR-4**: V 阶段 Grep 验证覆盖文档中出现的所有公开类名和主要方法名（≥95%）
- **NFR-5**: 分批生成，每批 ≤7 个文档，防止上下文过载
- **NFR-6**: references/ 信源文件先于 concepts/examples 生成
- **NFR-7**: 各级 index.md 在所有内容文档定稿后最后生成
- **NFR-8**: 所有文档 `status: stable`，`stale_after` 设置为合理的未来日期（API 稳定的包设 2027-12-31，快速迭代的包设 2027-06-30）

## Constraints
- **Technical**: 源码通过 git clone 获取到 `external/libs/` 下；Windows 环境使用 PowerShell；pexpect 的 PTY 功能仅 Unix 可用但源码可读；scrapli 新版可能含 Zig 核心
- **Business**: 遵循 awesome-okf-xs 子项目 AGENTS.md 规范；不修改子项目 .agents/ 目录；产出物存放于 projects/awesome-okf-xs/bundles/networking/
- **Dependencies**: git（clone 源码）、网络访问 GitHub、source-code-to-okf-wiki Skill、seven-concepts-cmd Skill
- **Format**: Markdown + OKF v0.2 YAML frontmatter；遵循现有 pyinvoke 知识束的格式范例

## Assumptions
- 6 个包的 GitHub 仓库可公开访问且 clone 成功
- scrapli 当前主分支可能已迁移至 Zig 核心 + Python ctypes 绑定，R 阶段将根据实际源码调整文档重点
- paramiko/fabric/asyncssh/pexpect/netmiko 均为纯 Python（或主要为 Python），源码可读性好
- fabric v3.x 基于 invoke + paramiko，invoke 已有知识束（bundles/tooling/pyinvoke/），可交叉引用
- netmiko 基于 paramiko，scrapli 支持 paramiko/asyncssh/ssh2 等多种 transport，存在跨束引用机会
- 每个包的 R 阶段可在子代理中独立执行，6 个包的 R 阶段可并行委派

## Acceptance Criteria

### AC-1: networking 分组结构完整
- **Given**: 规划文档已批准
- **When**: 检查 bundles/networking/ 目录
- **Then**: 存在 index.md 分组导航，6 个子目录（paramiko/fabric/asyncssh/pexpect/netmiko/scrapli），每个含 concepts/examples/references 三层结构
- **Verification**: `programmatic`
- **Notes**: 通过 LS/Glob 验证目录结构

### AC-2: paramiko 知识束内容完整且准确
- **Given**: paramiko 源码已 clone 到 external/libs/paramiko/
- **When**: 审查 paramiko 知识束
- **Then**: ≥10 篇概念文档覆盖 SSHClient/Transport/Channel/SFTPClient/认证/密钥/端口转发/服务端等主题；≥4 篇示例；1 篇信源登记；所有引用的类名/方法名在源码中存在
- **Verification**: `programmatic`
- **Notes**: Grep 验证关键 API

### AC-3: fabric 知识束内容完整且准确
- **Given**: fabric 源码已 clone
- **When**: 审查 fabric 知识束
- **Then**: ≥8 篇概念文档覆盖 Connection/Config/Group/Remote/Transfer/Tunnel/Executor 等；≥4 篇示例；与 paramiko 和 pyinvoke 知识束有交叉引用
- **Verification**: `programmatic`

### AC-4: asyncssh 知识束内容完整且准确
- **Given**: asyncssh 源码已 clone
- **When**: 审查 asyncssh 知识束
- **Then**: ≥10 篇概念文档覆盖异步连接/通道/流/进程/SFTP/SCP/转发/认证/密钥等；≥4 篇示例；所有 async/await API 签名准确
- **Verification**: `programmatic`

### AC-5: pexpect 知识束内容完整且准确
- **Given**: pexpect 源码已 clone
- **When**: 审查 pexpect 知识束
- **Then**: ≥8 篇概念文档覆盖 spawn/pxssh/PopenSpawn/fdspawn/expect/send/interact/replwrap 等；≥4 篇示例；正确标注 Unix/Windows 平台差异
- **Verification**: `programmatic`

### AC-6: netmiko 知识束内容完整且准确
- **Given**: netmiko 源码已 clone
- **When**: 审查 netmiko 知识束
- **Then**: ≥8 篇概念文档覆盖 ConnectHandler/BaseConnection/ssh_dispatcher/SSHDetect/驱动体系/命令执行/配置模式/文件传输等；≥4 篇示例；与 paramiko 知识束交叉引用
- **Verification**: `programmatic`

### AC-7: scrapli 知识束内容完整且准确
- **Given**: scrapli 源码已 clone
- **When**: 审查 scrapli 知识束
- **Then**: ≥8 篇概念文档覆盖 Transport/Channel/Driver 三层/核心平台驱动/同步异步双模式/Response 对象等；≥4 篇示例；准确描述与 paramiko/asyncssh 的 transport 插件关系
- **Verification**: `programmatic`

### AC-8: OKF v0.2 规范符合性
- **Given**: 所有文档生成完成
- **When**: 检查每个 .md 文件的 frontmatter
- **Then**: 每个非 index/log 文件有 type 字段（Concept/Example/Reference）；根 index.md 有 okf_version: "0.2"；子目录 index.md 无 frontmatter；sources 字段指向有效信源
- **Verification**: `programmatic`

### AC-9: 零虚构 API
- **Given**: V 阶段验证
- **When**: 对每个知识束中引用的公开类名和方法名执行 Grep
- **Then**: 文档中出现的所有类名（SSHClient、Connection、SSHClientConnection、spawn、ConnectHandler、Scrapli 等）和主要方法名在对应源码中可匹配到；虚构 API 数量为 0
- **Verification**: `programmatic`
- **Notes**: 这是 source-code-to-okf-wiki 的核心质量门

### AC-10: 交叉引用无断裂
- **Given**: 所有文档和 index 生成完成
- **When**: 检查所有 `/` 开头的 bundle-relative 链接
- **Then**: 所有链接目标文件存在；index.md 中列出的文档均实际存在
- **Verification**: `programmatic`

### AC-11: 分组索引和总索引更新
- **Given**: 6 个知识束全部完成
- **When**: 查看 bundles/networking/index.md 和 bundles/index.md
- **Then**: networking/index.md 包含 6 个知识束导航和生态关系图；bundles/index.md 新增 networking 分组条目，total_bundles 和 groups 计数更新
- **Verification**: `programmatic`

### AC-12: 知识地图学习路径合理
- **Given**: networking/index.md 生成完成
- **When**: 人类审查者阅读分组索引
- **Then**: 学习路径从 paramiko（基础）→ fabric/netmiko（高层封装）→ asyncssh（异步范式）→ pexpect（交互控制）→ scrapli（现代网络自动化），逻辑递进清晰，包之间的架构对比有说明
- **Verification**: `human-judgment`

## Open Questions
- [ ] scrapli 当前主分支是否已完全迁移至 Zig 核心？若是，Python 绑定层的源码量是否足以支撑 8 篇概念文档？R 阶段确认后可能调整文档数量。
- [ ] 是否需要为每个包生成 examples/ 中的可独立运行脚本文件（.py），还是仅在 Markdown 中内嵌代码块？（参考 pyinvoke 范例仅用 Markdown 内嵌代码）
- [ ] 6 个包的 facts.md 和 insights.md 是放在各自知识束目录内（如 pyinvoke 范例未包含），还是放在 .trae/specs/ 下作为过程产物？
