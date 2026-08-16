---
id: deepseek-harness-wiki-02
title: DeepSeek Harness Wiki - 环境准备与安装
source:
  - .temp/deepseek-harness-sources/02-tonybai.md
  - .temp/deepseek-harness-sources/09-deepseekagent-io.md
date: 2026-08-16
tags:
  - deepseek
  - agent
  - harness
  - installation
category: learning
maturity: L1
---

# 02 环境准备与安装

本章介绍 DeepSeek Harness 的环境要求、安装方式与初始配置。

## Node.js 版本要求

DeepSeek Harness 对 Node.js 版本有严格要求：

> **支持版本**：`^22.19 || >=24`
>
> **不支持**：奇数版本（如 Node 23）会直接启动失败

### 版本检查

安装前先确认当前 Node.js 版本：

```bash
node -v
```

输出示例（符合要求）：

```
v24.0.0
```

或：

```
v22.19.0
```

如果版本不符合要求，请根据操作系统选择对应方式安装或升级。

### 各平台安装方式

**macOS / Linux（使用 Homebrew）**

安装 Node.js 24：

```bash
brew install node@24
brew link --overwrite --force node@24
```

**Windows**

推荐使用以下任一方式：
- 从 [Node.js 官网](https://nodejs.org/) 下载 LTS 版本（24.x）
- 使用 [nvm-windows](https://github.com/coreybutler/nvm-windows) 管理多版本
- 使用 [fnm](https://github.com/Schniz/fnm) 或 [Volta](https://volta.sh/) 等版本管理工具

**Linux（使用 nvm）**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
nvm install 24
nvm use 24
```

## DeepSeek API Key 获取

dsh 不绑定特定模型厂商，但默认以 DeepSeek 模型为第一优先。使用前需要准备 API Key：

1. 打开 [DeepSeek 开放平台](https://platform.deepseek.com/api_keys)
2. 登录账号（若无账号需先注册）
3. 点击「创建 API Key」，填写名称后确认
4. **立即复制并妥善保存 Key**——Key 仅在创建时显示一次，关闭后无法再次查看完整内容
5. 确保账户有可用余额或免费额度

> 提示：dsh 也支持 Anthropic、OpenAI、Bedrock、Azure、Vertex 等其他厂商模型，以及自定义 OpenAI 兼容网关，详见后续模型配置章节。

## 一键启动（推荐）

最简单的体验方式是使用 npx 直接启动，无需提前安装：

```bash
cd 你的项目工作目录
npx @deepseek-ai/dsh web
```

首次运行时 npx 会自动下载最新版本的 `@deepseek-ai/dsh` 包。终端启动成功后会打印访问地址：

```
dsh web: http://127.0.0.1:3080
```

在浏览器中打开该地址即可进入 Web UI。

> 建议：在你希望 Agent 操作的项目根目录下执行启动命令，这样默认工作区就是当前目录。

## 源码构建

如果你希望参与开发、使用最新未发布特性，或需要自定义修改，可以从源码构建：

```bash
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build
pnpm dsh web
```

> 注意：源码构建需要 [pnpm](https://pnpm.io/) 包管理器。如果未安装 pnpm，可以先执行 `npm install -g pnpm`。

## ~/.dsh/ 配置目录

首次运行时，dsh 会在用户主目录下自动创建 `~/.dsh/` 目录，所有配置、凭证、会话数据均存储于此：

| 路径 | 用途 |
|------|------|
| `~/.dsh/profiles/` | Profile 配置档案目录，内置 `web` 和 `headless` 两套模板 |
| `~/.dsh/.credentials.yaml` | **API 密钥存储文件**（加密/脱敏存储，真实密钥不进入 settings.yaml） |
| `~/.dsh/settings.yaml` | 全局设置文件，包含模型配置、界面偏好等 |
| `~/.dsh/cordis.patch.yml` | 用户级 Cordis 补丁层，可覆盖任意插件配置 |
| `~/.dsh/sessions/` | 会话日志存储目录（后续版本可能变更格式） |

> 备份配置时，主要备份 `~/.dsh/` 目录即可。注意 `.credentials.yaml` 包含敏感信息，请勿提交到版本控制。

## 端口自定义

默认情况下，Web UI 监听 `127.0.0.1:3080`。如果 3080 端口被占用，可以通过 `--port` 参数自定义端口：

```bash
npx @deepseek-ai/dsh web --port 8080
```

此时访问地址变为 `http://127.0.0.1:8080`。

## 本地服务限制

dsh 被设计为**仅本地服务**，不支持对外暴露：

- CLI 会**主动拒绝** `--host 0.0.0.0` 参数并直接退出，报用法错误
- 无法通过此方式共享给局域网同事使用
- 会话、日志、数据全部保留在本地，不上传云端

这一设计与官方定位一致：dsh 是本地开发者工具，而非托管服务。如果需要团队内部共享 Agent 平台，需要基于 dsh 的 SDK 和插件能力自行构建。

## Windows 兼容性说明

dsh 可以在 Windows 上运行 Web UI，但存在以下功能限制：

| 功能 | Windows 支持情况 |
|------|------------------|
| Web UI 基本功能 | ✅ 完全支持 |
| 文件读写 | ✅ 完全支持 |
| 基础 Shell 执行 | ⚠️ 部分支持 |
| 持久终端（PTY） | ❌ 受限，依赖 POSIX 环境（建议使用 WSL2） |
| 官方自带运行时 | ❌ 仅发布 Linux 和 macOS 版本 |

如果在 Windows 上使用，推荐通过 WSL2（Windows Subsystem for Linux 2）安装 Node.js 并运行 dsh，以获得完整体验。

## 验证安装成功

启动成功后，在浏览器中打开 `http://127.0.0.1:3080`（或自定义端口），你应该能看到：

1. DeepSeek Harness 的 Web UI 界面
2. 顶部显示「预览版」角标
3. 左侧提示「Choose workspace」（选择工作区）
4. 输入框当前为灰色不可用状态（因为尚未选择工作区）

如果能看到以上界面，说明安装成功，可以进入下一章快速上手。

---

← [01 介绍](01-introduction-background.md) | → [03 快速上手](03-quickstart-first-task.md)
