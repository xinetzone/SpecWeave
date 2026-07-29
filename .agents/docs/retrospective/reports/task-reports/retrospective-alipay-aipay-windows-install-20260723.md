---
id: "retrospective-alipay-aipay-windows-install-20260723"
title: "支付宝 AI Pay Skill Windows 安装任务复盘"
date: "2026-07-23"
type: "task"
source: "用户会话：npx -y @alipay/alipay-aipay@latest install + alipay-cli version 验证"
tags: ["windows", "cli-install", "skill-setup", "sandbox", "cross-platform"]
maturity: "L1"
session: "sc-20260723-alipay-aipay-install"
---

# 支付宝 AI Pay Skill Windows 安装任务复盘

## 一、任务概述

| 项目 | 内容 |
|------|------|
| 任务目标 | 安装支付宝 AI Pay Skill（`@alipay/alipay-aipay` v1.3.8）并验证 alipay-cli 可用性 |
| 执行时间 | 2026-07-23 |
| 执行环境 | Windows / PowerShell / Trae Agent 沙箱 |
| 最终状态 | Skill 主组件安装成功，alipay-cli/jq 在 Windows 原生环境下未就绪，提供 Git Bash/WSL 替代方案 |

## 二、事实时间线（G1 质量门通过：无因果词）

| # | 时间 | 事实 | 证据来源 |
|---|------|------|---------|
| F01 | 07:18 | 执行 `npx -y @alipay/alipay-aipay@latest install` 命令 | Shell 执行记录 |
| F02 | 07:18 | 安装器版本为 v1.3.8 | 安装输出第一行 |
| F03 | 07:18 | 安装目标为 `.agents/skills/alipay-aipay/` | 安装输出"安装目标"行 |
| F04 | 07:18 | 环境检测输出：alipay-cli 未安装，GPG 未安装，jq 未安装 | 环境检查段 |
| F05 | 07:18 | 安装器提示 alipay-cli 后台尝试准备，不阻塞 Skill 安装 | 安装输出 |
| F06 | 07:18 | 安装器提示 Windows 下 jq 手动安装命令：`winget install jqlang.jq` | 安装总结 |
| F07 | 07:18 | Skill 文件安装完成，输出"✔ Skill 文件安装完成!" | 安装输出 |
| F08 | 07:18 | 后台日志路径：`C:\Users\xinzo\AppData\Local\Temp\alipay-aipay-tools-*.log` | 安装总结 |
| F09 | 07:18 | 后台 alipay-cli 安装失败，错误为 `spawn sh ENOENT` | 后台日志 |
| F10 | 07:18 | 后台日志中 alipay-cli 安装命令为 bash 脚本：`curl -fsSL https://opengw.alipay.com/alipaycli/install \| ... bash` | 后台日志 |
| F11 | 07:19 | 用户要求执行 `alipay-cli version` 验证 | 用户输入 |
| F12 | 07:19 | 读取 SKILL.md，文档说明 alipay-cli 用于登录授权、MCP 调用等联网操作 | SKILL.md 第29-31行 |
| F13 | 07:19 | 读取 alipay-cli-env.md，文档中安装命令均为 bash 语法，无 Windows PowerShell 安装说明 | alipay-cli-env.md |
| F14 | 07:19 | alipay-cli-env.md 中 PATH 配置示例为 `~/.zshrc`，无 Windows 环境变量配置说明 | alipay-cli-env.md 第138-140行 |
| F15 | 07:19 | 执行 `npx -y alipay-cli version` 失败，错误为 ENETUNREACH（网络不可达） | npx 输出 |
| F16 | 07:19 | 沙箱错误：`Not allow tcp network access: registry.npmmirror.com:443` | npx 输出 |
| F17 | 07:19 | 禁用沙箱后，PowerShell `Invoke-WebRequest` 下载安装脚本首次成功，脚本长度18602字节 | Shell 输出 |
| F18 | 07:19 | 第二次下载时 Invoke-WebRequest 出现 EOF 传输错误 | Shell 输出 |
| F19 | 07:19 | Skill 目录 VERSION 文件内容为 1.3.8，文件结构完整，包含 references/normal、references/integration、references/onboarding 三个子目录 | LS 输出 |
| F20 | 07:19 | Skill 包含 5 种语言代码示例：csharp、java、nodejs、php、python | LS 输出 |
| F21 | 07:19 | Skill 文档说明代码开发不需要 alipay-cli，签约流程才需要 | SKILL.md 功能描述 |

## 三、核心洞察（G2 质量门通过：四元组完整）

### 洞察 1：CLI 工具跨平台兼容性断裂

- **陈述**：alipay-aipay Skill 安装器的 alipay-cli 自动安装链路仅面向 Unix-like 环境（bash/curl/zshrc），Windows 原生 PowerShell 环境无对应实现，导致 `spawn sh ENOENT` 错误。
- **证据**：F09（spawn sh ENOENT）、F10（bash 安装脚本）、F13（文档仅提供 bash 命令）、F14（PATH 配置仅 ~/.zshrc）
- **反常识**：官方提供了 `winget install jqlang.jq` 的 Windows 安装提示（F06），说明意识到 Windows 存在，但核心 CLI 安装链路未做 Windows 适配，是"半适配"状态而非"完全不支持"。
- **下次行动**：遇到提供 bash 安装脚本的 CLI 工具，在 Windows 上第一时间检查是否有 Git Bash/WSL 环境，而非直接执行自动安装。

### 洞察 2：Agent 沙箱网络限制是特有的执行约束

- **陈述**：Trae Agent 默认沙箱禁止外网 TCP 连接，而 alipay-cli 的安装、登录、MCP 调用均需联网，形成"Skill 文档假设联网→沙箱默认断网→命令失败"的三层错配。
- **证据**：F16（Not allow tcp network access）、F12（Skill 文档说明 CLI 需联网）、F15（ENETUNREACH）
- **反常识**：npx 首次安装 @alipay/alipay-aipay 时能联网下载包（F01 执行成功），但后续 npx alipay-cli 却被沙箱拦截——说明沙箱对 npx 的临时包下载和包内命令执行有不同的网络策略，不是简单的"全断网"。
- **下次行动**：执行涉及 CLI 登录、API 调用、远程脚本下载的命令时，首次执行即申请 `dangerouslyDisableSandbox: true`，不要先在受限沙箱试跑。

### 洞察 3："安装成功"的判定标准需分层

- **陈述**：安装器输出"✔ Skill 文件安装完成!"，但 alipay-cli 和 jq 均未就绪，"Skill 安装成功"≠"全功能可用"。
- **证据**：F07（Skill 安装完成）、F04（三个组件均未安装）、F21（代码开发可用/签约流程不可用）
- **反常识**：安装器的总结表格里把 Skill 文件、alipay-cli、jq、GPG 四项分开标注状态（F08 总结表），但用户视觉焦点容易被"✔ Skill 文件安装完成!"的大对勾吸引，忽略其他组件的 ⏳/✗ 状态，形成"装好了"的错误认知。
- **下次行动**：安装类工具验证时，必须逐项检查所有组件状态，不能仅凭主组件的成功标识下结论。

## 四、可复用模式（G3 质量门通过：跨场景可迁移）

### 模式 E1：Windows 环境下 Unix-only CLI 工具安装处理模式

**触发场景**：
- 在 Windows PowerShell 中执行 npm/npx 安装 CLI 工具后，验证命令出现 `spawn sh ENOENT`、`command not found`、`bash: not found` 类错误
- 安装文档/脚本使用 `curl ... | bash`、`~/.zshrc`、`brew install`、`apt-get` 等 Unix 专属语法
- 官方安装器提供 winget 提示但核心安装链路仍为 bash

**核心步骤**：
1. **识别阶段**：读取安装日志，确认错误为 shell 缺失（ENOENT on sh/bash）而非网络或权限问题
2. **环境检测**：检查本机是否有 Git Bash、WSL、Cygwin 等 Unix 兼容层
3. **分流处理**：
   - 有 Git Bash/WSL → 在兼容层终端中执行官方 bash 安装命令
   - 无兼容层 → 尝试查找是否有 npm 全局包、Windows 可执行文件下载、或 Scoop/Chocolatey/Winget 包
   - 都不可用 → 明确告知用户该 CLI 在 Windows 原生环境受限，给出兼容层安装方案
4. **能力分层告知**：区分"哪些功能不需要 CLI 即可用"vs"哪些功能必须 CLI 才能用"，避免用户认为全部不可用

**反模式**：
- ❌ 在 PowerShell 中直接重试 bash 脚本命令（必然失败）
- ❌ 仅凭主组件安装成功的大对勾就判定"安装成功"
- ❌ 不区分功能层级，笼统说"安装失败"
- ❌ 给出 `chmod +x`、`source ~/.bashrc` 等在 PowerShell 中无意义的建议

**迁移验证**：
- ✅ 可迁移到：nvm-windows 安装、husky Git hooks 配置、各种 Cloud CLI（awscli/gcloud）在 Windows 上的安装
- ✅ 可迁移到：WSL2 环境下的 Windows interop 场景

---

### 模式 E2：Agent 沙箱联网命令预授权模式

**触发场景**：
- Agent 环境有默认网络沙箱（如 Trae Sandbox）
- 命令涉及：CLI 登录认证、远程安装脚本下载、MCP/API 调用、文件上传到外部服务
- 命令在首次执行时出现 ENETUNREACH、EAI_AGAIN、"Not allow tcp network access" 等网络错误

**核心步骤**：
1. **预判断**：执行前先阅读工具文档/Skill 说明，识别哪些命令需要联网
2. **首次即授权**：已知需要联网的命令，首次执行即设置 `dangerouslyDisableSandbox: true`
3. **错误分类**：网络错误发生时，区分是沙箱阻断还是目标服务真的不可达
4. **复用授权**：同一脚本/工具的后续命令尽量复用已授权的命令前缀，减少重复授权

**反模式**：
- ❌ 先在受限沙箱里试跑，失败了再申请联网权限（浪费交互轮次）
- ❌ 把沙箱阻断误判为"用户网络故障"或"服务不可用"
- ❌ 每个子命令都单独触发授权申请（应复用脚本前缀）

**迁移验证**：
- ✅ 可迁移到：所有需要外部 API 调用的 Skill（alipay-payment-integration、notion-cli、gh-cli、home-assistant 等）
- ✅ 可迁移到：npm/pip 包安装时的原生二进制下载场景（如 electron、puppeteer、node-sass 的 postinstall）

---

### 模式 E3：多组件安装状态分层验证模式

**触发场景**：
- 安装器包含主组件+可选依赖+工具链的多组件组合
- 安装输出中有彩色对勾/叉号状态表格
- 验证命令由用户手动触发，而非安装器自动执行

**核心步骤**：
1. **组件枚举**：安装完成后，列出安装器声明的所有组件（不要只看主组件）
2. **逐项验证**：对每个 ⏳（后台进行中）和 ✗（未就绪）的组件，单独验证状态
3. **读取日志**：后台任务的日志路径要及时读取，确认是进行中还是已失败
4. **能力矩阵输出**：以表格形式说明"组件 A✓→可用功能 X；组件 B✗→功能 Y 暂不可用，替代方案 Z"
5. **时间窗口判断**：后台任务给予合理等待时间（如 30 秒）后再验证，避免刚启动就判定失败

**反模式**：
- ❌ 看到主组件的 ✔ 就输出"安装成功，请使用"
- ❌ 不读取后台日志，直接告诉用户"正在后台安装请等待"然后不再跟进
- ❌ 把"未安装 jq"升级为"整个工具不可用"的级联失败判断
- ❌ 不提供功能分层说明，用户试了才知道哪些能用哪些不能用

**迁移验证**：
- ✅ 可迁移到：所有带可选依赖的 npm/pip 包安装、IDE 插件安装、开发环境搭建（Node+npm+npx+nvm 组合）
- ✅ 可迁移到：Scoop/Chocolatey/Winget 等包管理器的安装后验证

## 五、质量门记录

| 质量门 | 阶段 | 状态 | 说明 |
|--------|------|------|------|
| G1 | R（复盘） | ✅ 通过 | 22 条事实无因果词，纯客观描述 |
| G2 | I（洞察） | ✅ 通过 | 3 条洞察均包含陈述/证据/反常识/下次行动四元组 |
| G3 | E（萃取） | ✅ 通过 | 3 个模式均有触发场景/核心步骤/反模式/迁移验证 |

## 六、相关文件

| 文件 | 说明 |
|------|------|
| [SKILL.md](../../../../skills/alipay-aipay/SKILL.md) | Skill 主文件 |
| [VERSION](../../../../skills/alipay-aipay/VERSION) | 版本文件（v1.3.8） |
| [alipay-cli-env.md](../../../../skills/alipay-aipay/references/normal/alipay-cli-env.md) | CLI 环境准备文档 |

<!-- changelog -->
- 2026-07-23 | task | 支付宝 AI Pay Skill Windows 安装任务复盘完成，3条核心洞察+3个可复用模式（E1 Windows跨平台CLI安装处理/E2沙箱联网预授权/E3多组件分层验证），G1-G3质量门全部通过
