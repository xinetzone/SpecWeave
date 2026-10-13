---
title: "为 okw 增加 openKylin AI 栈支持（OCR 已验证路径）"
status: "draft"
methodology: "seven-concepts-cmd: F→V→I→C"
content-sensitivity: "public"
source: "docs/knowledge/tech/openkylin-docs-wiki/concepts/05-ai-stack.md; docs/knowledge/tech/openkylin-docs-wiki/references/ai-sdk-ocr-poc.md; docs/knowledge/tech/openkylin-docs-wiki/references/ai-subsystem-source-architecture.md; apps/dev-tools/openkylin-wsl-devkit/"
---

# 为 okw 增加 openKylin AI 栈支持（OCR 已验证路径）

## Overview

- **Summary**：扩展现有 `apps/dev-tools/openkylin-wsl-devkit`（CLI `okw`），新增 `okw ai preflight|install|verify` 子命令组与 `okw ref ai-stack` 知识主题，对指定 openKylin 3.0 WSL2 发行版只读盘点 AI 栈、在显式确认后安装**唯一已落机验证的 Gen1 SDK / OCR 路径**，并验收本地 OCR 能力；不创建新的并列应用。
- **Purpose**：现有 `okw` 已覆盖发行版管理、环境验收、脚手架、rootless Podman 与下游引导，但不负责在发行版内准备 AI 能力。知识库已完成 OCR 落机 POC（2026-10-08），将这条**已验证**路径与 AI 栈分层盘点纳入同一入口，让开发者先看清各层现状，再显式安装、验收，避免把"成文未验证"的能力当作可用。
- **Target Users**：在 Windows + WSL2 中使用 openKylin 3.0、希望在该发行版内以确定性、离线方式获得本地 OCR（及了解其余 AI 层现状）的开发者。

## Goals

- G1：新增 `okw ai preflight <name>`、`okw ai install <name> --yes`、`okw ai verify <name>` 三个叶子命令，并在 `cli/main.py` 完成子组分发。
- G2：`preflight` 只读、单批 `apt-cache policy` 盘点分层 AI 组件（Gen1 SDK、OCR 引擎与语言包、模型管理工具、Gen2 客户端、引擎插件、本地 NLP 引擎、Triton、ollama），逐项报告 PASS/FAIL/UNKNOWN 与已装/候选版本。
- G3：`install --yes` 仅安装已验证的直接包 `libkylin-ai-base-dev`（APT 解析其依赖，含 `libkylin-ai-base2`、tesseract 5.3.4 与 chi_sim/eng 语言包），复用 POC 的 `--no-install-recommends` 安装口径。
- G4：`verify` 只读确认 OCR 路径真实可用：Gen1 运行库已装、`tesseract --version` 与 `--list-langs` 含 chi_sim/eng；可选 `--smoke-ocr <图片>` 对本地图片跑一次离线识别。
- G5：新增 `okw ref ai-stack` 主题，沉淀"用户使用/模型接入/开发者 SDK/贡献治理"四层心智模型与凭据红线。
- G6：复用现有 `okw.distro` WSL 封装与 `okw.podman` 的 APT 分类/超时资产，保持零第三方运行时依赖，不复制推理/模型管理能力。

## Non-Goals

- 不新建另一个 AI、模型或 SDK 管理应用；不改变 `okw` 包名与入口。
- 不配置、生成、读取或写入任何 API Key/Token/云端账号；不改动 dconf/gsettings 部署策略。
- 不下载任何 AI 模型（GGUF、modelscope 模型、ollama 模型），不组织 Triton 模型仓库。
- 不安装 ollama（其不在 openKylin 官方源）；不执行 `curl ... | sh` 类外部脚本，仅盘点并提示。
- 不安装 Gen2 全栈元包 `kylin-ai-subsystem`、`kylin-ai-engine-plugins`、`kylin-ondevice-nlp-engine`（端到端未验证、下载量大）；这些仅作只读盘点。
- 不默认安装 `kylin-ai-model-manager`（上游自述"功能非常不完善"）；仅盘点，用户可自行 apt 安装。
- 不启动/启用 Triton、`kylin-ai-runtime`、kytensor 等服务或 socket；不改变 WSL 默认发行版、默认用户、`wsl.conf` 与软件源。
- 不实现文本生成、语音、向量化、图像生成、图像分割等"成文未验证"能力的安装或调用。

## Background & Context

- 知识库 `concepts/05-ai-stack.md` 将 AI 内容分为用户使用、模型接入配置、开发者 SDK 三层加贡献治理；明确 Gen1（`libkylin-ai-base2 2.0`，手册 8 能力域）与 Gen2（`libkysdk-* 1.1`，全 IPC 异步）两代 SDK 互不从属。
- OCR POC（`references/ai-sdk-ocr-poc.md`，状态 verified）已在 openKylin-3.0-desktop WSL 实测：
  `sudo apt-get install -y --no-install-recommends libkylin-ai-base-dev` 成功，直接包为 `libkylin-ai-base-dev`，APT 拉入 `libkylin-ai-base2`、`kylin-ai-runtime`、`libkylin-ai-document-qa-service`，并经 Depends 得到 tesseract 5.3.4（chi_sim/eng/osd）。
- OCR 三源钉死为**本地 tesseract CPU 离线**（ldd 直链 libtesseract、gsettings 权威 LOCAL 无云密钥、强制 LOCAL 识别成功），不依赖网络/GPU/大模型；识别精度中等、有形近误识。
- 源码架构核验（`references/ai-subsystem-source-architecture.md`）：Gen2 客户端库在 Desktop 镜像出厂已装但为 IPC 薄代理；引擎插件、本地 NLP 引擎与模型缺省；本地 NLP 完整链路终点为预装 kytensor(Triton)+llama.cpp，但需自备 GGUF。
- 与 Podman 扩展同构：okw 以标准库实现，WSL 调用经 `okw.distro` 统一封装；`okw.podman` 已沉淀 C locale APT argv、网络/哈希/缺包分类与写操作长超时常量，本变更复用而非重写。
- APT 输出随 locale 本地化，需解析的 apt 调用必须强制 C locale；dpkg-query 的 Status 字段不本地化，作为已装状态权威来源。

## Functional Requirements

### Requirement: 只读盘点 AI 栈分层组件

`okw ai preflight <name>` SHALL 对显式指定发行版执行只读盘点，SHALL NOT 更新 APT 索引、安装包、写文件、改配置或改变 WSL/默认发行版状态。盘点 SHALL 以单条 `apt-cache policy <全部组件>`（强制 C locale）获取候选与已装版本，并区分**OCR 必选组件**与**可选层组件**。

#### Scenario: 结构条件满足且 OCR 路径可安装

- **WHEN** 用户运行 `okw ai preflight <name>`
- **AND** 目标已注册、为 WSL2、`/etc/os-release` 可识别为 openKylin，且 dpkg/apt 可用
- **THEN** SHALL 输出结构项（发行版存在/WSL 版本/openKylin 身份/APT 能力）与每个组件的逐项 PASS/FAIL/UNKNOWN
- **THEN** OCR 必选组件（`libkylin-ai-base-dev`、`libkylin-ai-base2`、`tesseract-ocr`、`tesseract-ocr-chi-sim`、`tesseract-ocr-eng`）有候选时 SHALL 标 PASS 并附候选版本
- **THEN** 可选层（模型管理工具、Gen2 客户端、引擎插件、本地 NLP 引擎、kytensor、ollama）已装或有候选 SHALL 标 PASS，缺失 SHALL 标 UNKNOWN（不阻断）
- **THEN** 全程 SHALL NOT 发生任何写入或 apt update

#### Scenario: APT 索引过期或网络问题

- **WHEN** 安装目标 `libkylin-ai-base-dev` 无候选行（索引缺失/过期）
- **THEN** 该项 SHALL 标 UNKNOWN 并输出中文行动建议：`未知：发行版 APT 索引缺失或已过期，建议在发行版内先手动执行 sudo apt update 后重跑 preflight`
- **WHEN** policy 调用出现域名解析/不可达/连接失败等网络错误
- **THEN** 相关项 SHALL 标 FAIL 并给出网络排查方向；SHALL NOT 自动重试或改源

#### Scenario: 发行版或结构条件不符合

- **WHEN** 指定发行版不存在、非 WSL2、非 openKylin，或 APT/dpkg 不可用
- **THEN** SHALL 输出失败项与可执行修复指引、以非零状态结束，SHALL NOT 继续组件盘点的安装性结论

### Requirement: 显式确认后安装已验证的 OCR 路径

`okw ai install <name>` SHALL 仅在 `--yes` 时，以 root 身份经发行版当前软件源安装直接包 `libkylin-ai-base-dev`（`apt install -y --no-install-recommends`），由 APT 解析 OCR 运行库、tesseract 与语言包等依赖。SHALL NOT 添加/改写软件源，SHALL NOT 安装可选层或模型。

#### Scenario: 缺少确认时零写入

- **WHEN** 用户运行 `okw ai install <name>` 而未提供 `--yes`
- **THEN** SHALL 仅打印编号副作用清单（apt update、安装 libkylin-ai-base-dev 及其依赖、事后 OCR 只读验收）与凭据红线提示
- **THEN** SHALL 以退出码 2 结束且不发生任何写入、apt update 或子进程写操作

#### Scenario: 确认后安装并验收

- **WHEN** 用户运行 `okw ai install <name> --yes`
- **AND** 结构预检通过
- **THEN** SHALL 以 root 执行 apt update、复查直接包候选存在，再一次安装直接包与 APT 解析的依赖
- **THEN** 安装后 SHALL 以默认用户执行 OCR 只读子集验收（tesseract 版本、语言列表含 chi_sim/eng）并逐项报告
- **THEN** SHALL NOT 对其他发行版执行命令、改变默认发行版/默认用户/软件源/wsl.conf，或安装任何模型

#### Scenario: 候选缺失、网络/哈希错误或中途失败

- **WHEN** apt update 命中网络错误、源哈希校验失败，或直接包在刷新后仍无候选
- **THEN** SHALL 在写入前停止，区分"包不在源/网络错误/哈希失败"给出中文方向（禁止添加第三方源）
- **WHEN** apt install 或后续验收任一步失败
- **THEN** SHALL 返回非零、指出失败阶段并报告可能已部分完成的变更；SHALL NOT 宣称成功或自动卸载，不保证事务回滚

### Requirement: 只读验收本地 OCR 能力

`okw ai verify <name>` SHALL 只读确认 OCR 必选路径已装且功能可用，并盘点可选层现状；默认不执行识别写入。

#### Scenario: OCR 路径验收通过

- **WHEN** 用户运行 `okw ai verify <name>`
- **AND** `libkylin-ai-base2` 已装、`tesseract --version` 可执行、`tesseract --list-langs` 同时含 chi_sim 与 eng
- **THEN** SHALL 逐项输出 PASS（附 tesseract 版本）并以 0 结束
- **WHEN** 必选运行库缺失、tesseract 不可执行或语言缺失
- **THEN** 对应项 SHALL 标 FAIL 并提示先执行 `okw ai install <name> --yes`，以非零结束

#### Scenario: 可选层盘点不阻断

- **WHEN** 模型管理工具、Gen2 客户端/引擎插件、本地 NLP 引擎、kytensor 或 ollama 未安装
- **THEN** SHALL 标 UNKNOWN 并简述其角色与"okw 不自动安装/不下载模型"；这些 SHALL NOT 阻断 OCR 验收结论

#### Scenario: 可选的本地图片 OCR 冒烟

- **WHEN** 用户显式加 `--smoke-ocr <发行版内可访问图片路径>`
- **AND** 前置无 FAIL
- **THEN** SHALL 仅对该本地图片执行一次 `tesseract <图片> stdout -l chi_sim+eng`，返回非空文本且退出 0 时标 PASS
- **THEN** 图片不存在或识别失败 SHALL 标 FAIL；全程离线、SHALL NOT 访问网络或拉取任何内容

### Requirement: 提供 ai-stack 知识参考并保持应用边界

SHALL 新增 `okw ref ai-stack` 主题，概述 AI 四层成文、两代 SDK、OCR 已验证事实与凭据/模型红线，并列出知识库来源。AI 能力 SHALL 作为现有 `okw` 子命令实现，复用统一 WSL 结果处理与中文错误提示，更新用户文档与 apps 索引中的既有应用说明。

#### Scenario: 知识主题与既有命令不回归

- **WHEN** 运行 `okw ref`（列表）、`okw ref ai-stack`，以及既有发行版/验收/脚手架/podman/compose/image 命令
- **THEN** `ref` 列表 SHALL 含 ai-stack，主题内容与来源可读；既有命令参数、默认星标保护、退出码与行为 SHALL 保持兼容
- **THEN** `okw ai --help` 与 README SHALL 一致展示子命令、`--yes` 确认、只读与"不碰密钥/不下载模型"边界

## Non-Functional Requirements

- **NFR-1（运行时依赖）**：仅用 Python 标准库与现有 scikit-build-core 构建，不增加第三方运行时依赖。
- **NFR-2（WSL 调用）**：发行版命令 SHALL 复用 `okw.distro` 的 wsl 定位、`WSL_UTF8=1`、超时与错误归一；需 root 时显式 `-u root`；apt 写操作复用 `okw.podman` 的长超时与 C locale/错误分类资产。
- **NFR-3（测试）**：单测不得真实安装/写系统/触网；policy、dpkg-query、tesseract 与安装流程须可注入/隔离。整体覆盖率 ≥80%，新增关键 ai 模块 ≥90%。
- **NFR-4（输出）**：错误 SHALL 以中文说明失败阶段与后续动作；不将密钥、模型或无关发行版数据写入文件。
- **NFR-5（兼容）**：宿主 Windows + WSL2，目标 openKylin 3.0 WSL2；包/语言包可用性作为运行时探测结果，不作静态假设。

## Constraints

- **Technical**：OCR 直接包经 APT 解析依赖；候选可用性取决于现有源与索引状态，安装前探测、刷新后复查。
- **Security**：preflight 与默认 verify 只读；install 必须 `--yes`；不触碰任何凭据、模型与外部脚本，变更限定于指定发行版。
- **Compatibility**：不把容器组 OCI 契约或 Gen2 全栈用于本路径；不要求 GPU、大模型、systemd 服务或网络作为 OCR 基础条件。
- **Dependencies**：Windows WSL2、已导入 openKylin 3.0 WSL2 发行版及其现有 APT 源；真实安装验收还依赖直接包有候选。

## Assumptions

- 面向知识库记录的 openKylin 3.0（huanghe）WSL2，Desktop 与最小镜像不增加独立适配逻辑。
- `libkylin-ai-base-dev` 由目标发行版当前官方源提供；探测不到则安全停止，不引入外部源。
- OCR 功能验收以 tesseract 本地 CPU、chi_sim+eng 为准；精度中等属已知，不承诺商用准确率。
- `--smoke-ocr` 图片由用户在发行版内提供；默认验收离线、不下载模型。

## Acceptance Criteria

### AC-1：preflight 只读且分层清晰

- **Type**：`rule`
- **Given**：模拟发行版不存在、WSL1、非 openKylin、APT 缺失、索引过期、网络错误、OCR 候选齐全、可选层缺失等情形
- **When**：执行 `okw ai preflight <name>`
- **Then**：每种情形输出可区分的逐项结果与正确退出码；单批 policy 调用；不发生安装、apt update、写入或默认发行版变更
- **Pass Condition**：隔离测试断言 WSL 调用序列、退出码与文件系统前后快照全部通过
- **Evidence**：ai preflight 单元测试与副作用哨兵断言

### AC-2：install 有显式确认与发行版边界

- **Type**：`rule`
- **Given**：符合条件的 openKylin WSL2 发行版
- **When**：无 `--yes` 或有 `--yes` 执行安装
- **Then**：无确认时仅打印副作用清单、零写入（退出码 2）；确认后仅在指定发行版执行 apt update 与 `apt install -y --no-install-recommends libkylin-ai-base-dev`；不改源、其他发行版、默认发行版/用户、wsl.conf，不安装模型或可选层
- **Pass Condition**：mock WSL 序列与快照断言通过
- **Evidence**：安装流程单元测试与 CLI 集成测试

### AC-3：安装失败分类与停止安全

- **Type**：`rule`
- **Given**：apt update 网络错误、哈希失败、直接包刷新后无候选、apt install 失败等输出
- **When**：执行 `okw ai install <name> --yes`
- **Then**：在写入前/失败时区分包缺失/网络/哈希给出中文方向且禁止第三方源；非零退出，不宣称成功、不自动卸载
- **Pass Condition**：分类 mock 矩阵覆盖每类，且无越界写入
- **Evidence**：安装分类单元测试

### AC-4：verify 确认真实 OCR 上下文

- **Type**：`rule`
- **Given**：运行库缺失、tesseract 缺失/版本读取失败、语言缺 chi_sim 或 eng、全部通过等输出
- **When**：执行 `okw ai verify <name>`
- **Then**：结果准确反映各项，缺失必选项提示先 install 并非零退出，全部通过退出 0；可选层缺失仅 UNKNOWN 不阻断
- **Pass Condition**：dpkg-query/tesseract mock 输出矩阵覆盖每项；目标 WSL 可用时以默认用户只读执行
- **Evidence**：verify 单元测试；目标 WSL 可用时的只读执行记录

### AC-5：OCR 冒烟离线且不触网

- **Type**：`rule`
- **Given**：未请求冒烟、本地图片存在/不存在、识别返回非空/失败
- **When**：执行默认 verify 或 `verify --smoke-ocr <图片>`
- **Then**：默认不执行识别；冒烟仅对本地图片跑 tesseract（chi_sim+eng），失败清晰报错且无任何网络调用
- **Pass Condition**：冒烟命令参数与无网络守卫断言通过
- **Evidence**：冒烟参数构造测试与无网络测试守卫

### AC-6：ref ai-stack 与既有能力无回归

- **Type**：`rule`
- **Given**：现有 okw 测试与包配置
- **When**：运行 `okw ref`/`okw ref ai-stack`、全量测试与 wheel 构建
- **Then**：ref 列表含 ai-stack 且来源正确；既有子命令全部通过，新增 ai 三叶子可由入口调用，运行时依赖未增加，wheel 构建成功
- **Pass Condition**：全量测试通过、总体覆盖率 ≥80%、ai 模块 ≥90%、wheel 构建成功
- **Evidence**：pytest/coverage 与 wheel 构建记录

### AC-7：命令面守卫与快照一致

- **Type**：`rule`
- **Given**：parser、注册表、CLI 快照与架构守卫
- **When**：对照注册表键集、parser 叶子集、空组帮助与快照
- **Then**：新增 `ai preflight/install/verify` 三键在注册表、parser 与快照中逐字一致；`okw ai` 空组回打帮助并退出 2；快照重新生成且字节稳定
- **Pass Condition**：更新后的命令注册表/架构/快照测试全部通过
- **Evidence**：守卫测试与再生成的 cli_surface.json

### AC-8：文档与区域索引一致

- **Type**：`rule`
- **Given**：CLI help、README、命令参考/新增 AI 指南、apps 索引
- **When**：核对各入口
- **Then**：命令名、`--yes`、只读/离线、"不碰密钥/不下载模型/不装 ollama"边界一致；新增 07 AI 指南入 toctree；apps/AGENTS.md 更新既有 okw 描述而非新增应用
- **Pass Condition**：文档命令与 `okw ai --help` 逐项对应、链接有效
- **Evidence**：文档核对与链接检查记录

### AC-9：首次使用与副作用说明完备

- **Type**：`rubric`
- **Given**：首次接触 okw ai 的开发者
- **When**：阅读 `okw ai --help`、`okw ai install --help`、README/AI 指南入门段
- **Then**：各入口一致且无矛盾地说明：① AI 四层与两代 SDK 的区别、本期只装"已验证 OCR 路径"；② install 副作用清单（apt update、安装 libkylin-ai-base-dev 及依赖、事后 OCR 只读验收）；③ 如何查发行版名；④ 为何不配置密钥/不下载模型/不装 ollama，以及 `--smoke-ocr` 前置（图片须在发行版内、全程离线）
- **Pass Condition**：任一缺失或多入口不一致即不通过
- **Evidence**：多入口逐字段对照表

## Open Questions

- 产品范围无待决项。目标发行版当前源是否提供直接包，是安装前/安装时的运行时门禁；若本机无可用 openKylin 3.0 发行版，真实安装与 OCR 验收如实记为 `blocked`，不得用 mock 替代。
- Gen2 全栈、文本生成与模型下载属后续独立 POC，不在本变更范围。
