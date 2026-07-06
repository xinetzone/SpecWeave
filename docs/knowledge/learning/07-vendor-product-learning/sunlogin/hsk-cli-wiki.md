---
title: "HSK CLI（@aweray/hsk-cli）完整学习教程：AI时代零配置公网预览工具"
source: "https://hsk.oray.com/doc/cli-setup.md"
date: "2026-07-06"
tags: ["向日葵", "HSK", "hsk-cli", "CLI", "内网穿透", "文件托管", "公网预览", "零配置", "AI Agent", "匿名分享"]
---

# HSK CLI（@aweray/hsk-cli）完整学习教程：AI时代零配置公网预览工具

> **官方文档**: https://hsk.oray.com/doc/cli-setup.md
> **更新日期**: 2026-07-06
> **当前版本**: v0.4.3

---

## 📋 目录导航

- [一、概述与产品定位 🎯](#一概述与产品定位)
- [二、核心概念 📚](#二核心概念)
- [三、安装与环境配置 ⚙️](#三安装与环境配置)
- [四、快速上手 🚀](#四快速上手)
- [五、文件托管（host/deploy）📦](#五文件托管hostdeploy)
- [六、内网穿透（tunnel）🔌](#六内网穿透tunnel)
- [七、常用命令速查 📖](#七常用命令速查)
- [八、AI Agent沙盒适配与实战场景 🤖](#八ai-agent沙盒适配与实战场景)
- [九、专业洞察、常见问题与资源链接 💡](#九专业洞察常见问题与资源链接)

---

## 一、概述与产品定位 🎯

### 1.1 产品定位

**HSK CLI** 是贝锐（Oray）推出的零配置公网预览工具，提供两种核心能力：**文件托管**（静态资源一键上传分享）和**内网穿透**（本地端口暴露到公网）。与向日葵企业CLI（awesun-cli）定位远程控制主控端不同，HSK CLI专注于"本地资源快速公网化"场景。

### 1.2 核心价值与适用场景

| 场景类型 | 价值说明 | 推荐模式 |
|---|---|---|
| **静态文件分享** | 快速分享HTML页面、PDF、图片、构建产物等静态资源，无需配置服务器 | host |
| **本地开发预览** | 将本地开发的Web项目临时分享给他人访问、演示、测试 | deploy / host |
| **Webhook调试** | 接收第三方服务的Webhook回调，无需部署公网服务器 | tunnel |
| **AI Agent演示** | AI Agent创建的页面、报表、demo一键发布到公网供用户查看 | host / deploy |
| **临时API暴露** | 将本地运行的API服务临时暴露给前端或第三方调试 | tunnel |
| **CI/CD预览** | 构建产物自动上传，生成预览链接用于PR评审 | deploy |

### 1.3 与awesun-cli的定位互补

HSK CLI与向日葵企业CLI（awesun-cli）是互补关系而非替代关系：

| 维度 | awesun-cli（向日葵企业CLI） | hsk-cli（HSK公网预览CLI） |
|---|---|---|
| **核心定位** | 远程控制主控端 | 公网预览/文件分享工具 |
| **认证要求** | 需要登录向日葵账号 | 匿名可用，无需注册 |
| **核心功能** | 设备管理、桌面控制、文件传输、端口转发、SSH | 文件托管、内网穿透、构建部署 |
| **保活要求** | 会话需保持连接 | host无需保活；tunnel需后台进程 |
| **典型场景** | 远程运维、批量设备管理、AI Agent远程操作 | 本地预览、静态分享、demo展示、Webhook调试 |
| **资源绑定** | 绑定账号下的设备 | 匿名资源需打开链接激活认领 |

---

## 二、核心概念 📚

### 2.1 双模式架构

HSK CLI采用"静态优先"的双模式设计：

| 模式 | 说明 | 保活要求 | 推荐度 | 适用场景 |
|---|---|---|---|---|
| **host（文件托管）** | 上传文件或目录到贝锐云存储，自动生成公网URL | ❌ 无需保活，一次上传永久可用（待认领） | ✅ 优先 | 静态HTML、图片、PDF、构建产物 |
| **deploy（构建部署）** | 一键执行构建 → 上传产物到文件托管 | ❌ 无需保活 | ✅ 优先 | npm项目、前端应用静态构建 |
| **tunnel（内网穿透）** | 将本地端口暴露到公网，建立TCP隧道 | ✅ 需要前台/后台进程维持连接 | ⚠️ 降级使用 | WebSocket、动态API、SSR、本地服务调试 |

> **⚠️ AI Agent决策指南**：优先使用host/deploy发布静态资源。只有以下情况才使用tunnel：WebSocket、动态API、SSR等无法静态托管的内容；用户明确要求"暴露端口""内网穿透"。不确定时，先尝试host/deploy，失败再退回到tunnel。

### 2.2 匿名资源机制

HSK采用"匿名先行、认领后置"的资源创建流程：

1. **匿名创建**：无需注册登录，直接执行命令即可上传文件/创建隧道，获得公网URL
2. **验证码保护**：URL中包含verify_code参数，防止随意遍历访问
3. **激活认领**：用户打开链接后，按页面提示激活并认领资源
4. **控制台管理**：认领后可在HSK控制台查看、管理、续期资源

### 2.3 资源ID与更新机制

- **resource_id**：每个资源创建后返回唯一资源ID（如1783317437166602000）
- **资源更新**：使用`--resource-id`参数可更新已有资源内容，URL保持不变
- **目录自动打包**：host/deploy传入目录时，自动打包为zip上传，并自动识别index.html作为入口文件

---

## 三、安装与环境配置 ⚙️

### 3.1 环境要求

| 要求项 | 具体说明 |
|---|---|
| **操作系统** | Windows 7+ / macOS 10.12+ / 主流Linux发行版 |
| **Node.js环境** | 需预装Node.js和npm包管理器（建议Node.js ≥ 16） |
| **网络连接** | 设备可正常访问互联网，用于下载二进制和上传资源 |

### 3.2 npm安装命令

全局安装npm包：

```bash
npm install -g @aweray/hsk-cli
```

### 3.3 下载二进制文件

npm包是Node.js包装器，首次使用需下载对应平台的原生二进制：

```bash
hsk-cli update
```

该命令会自动：
- 检测当前操作系统和架构（Windows/macOS/Linux × amd64/arm64）
- 从贝锐CDN下载对应版本的原生二进制文件
- 缓存到 `~/.hsk/bin/` 目录，后续命令直接复用

二进制文件命名格式：
| 平台 | 架构 | 文件名 |
|---|---|---|
| Windows | amd64 | hsk-cli-windows-amd64-v{version}.exe |
| macOS Intel | amd64 | hsk-cli-darwin-amd64-v{version} |
| macOS Apple Silicon | arm64 | hsk-cli-darwin-arm64-v{version} |
| Linux | amd64 | hsk-cli-linux-amd64-v{version} |

### 3.4 验证安装

安装完成后执行以下命令验证环境：

```bash
# 检测平台信息
hsk-cli platform --format json

# 干运行测试（不实际创建隧道）
hsk-cli +tunnel --ip 127.0.0.1 --port 8080 --dry-run
```

验证通过的标准输出示例：
```json
{
  "platform": "windows",
  "arch": "amd64",
  "nodePlatform": "win32",
  "nodeArch": "x64",
  "isWindows": true,
  "platformKey": "windows-amd64"
}
```

```
[DRY-RUN] 将执行: hsk-cli-windows-amd64-v0.4.3.exe -ip 127.0.0.1 -port 8080
  目标IP: 127.0.0.1
  目标端口: 8080
  ...
```

---

## 四、快速上手 🚀

### 4.1 文件托管快速体验

创建一个简单的HTML页面并上传：

```bash
# 1. 创建演示目录和页面
mkdir demo && cd demo
echo '<h1>Hello HSK!</h1>' > index.html

# 2. 上传目录（自动打包为zip，识别index.html为入口）
hsk-cli +host . --format json
```

成功后返回：
```json
{
  "success": true,
  "mode": "create",
  "publicUrl": "https://files.hz-1.aicp.space:8010/file/xxx?verify_code=xxx",
  "verifyCode": "xxxx",
  "resourceId": "1783317437166602000"
}
```

### 4.2 构建部署快速体验

在npm项目根目录执行：

```bash
hsk-cli +deploy --format json
```

默认执行`npm run build`，然后上传dist目录。

### 4.3 内网穿透快速体验

确保本地有服务在目标端口监听（如本地8080端口运行了Web服务）：

```bash
# 前台运行（可看到实时日志）
hsk-cli +tunnel --ip 127.0.0.1 --port 8080 --format json

# 或后台运行（CLI立即退出，隧道持续运行）
hsk-cli +tunnel --ip 127.0.0.1 --port 8080 --detach --format json
```

---

## 五、文件托管（host/deploy）📦

### 5.1 host命令 - 上传文件或目录

**用途**：上传单个文件或整个目录到公网托管，生成可访问的URL。

**语法**：
```bash
hsk-cli +host <路径> [选项]
```

**参数**：
| 参数 | 说明 |
|---|---|
| `<路径>` | 要上传的文件或目录路径。传入目录时自动打包为zip上传 |

**常用选项**：
| 选项 | 说明 |
|---|---|
| `--format json` | 输出JSON格式（推荐AI Agent使用） |
| `--format pretty` | 人类可读格式（默认） |
| `--open` | 上传成功后自动打开浏览器（沙盒环境可能无效） |
| `--resource-id <id>` | 更新指定资源ID的内容，URL不变 |

**典型示例**：

```bash
# 上传单个文件
hsk-cli +host ./report.pdf --format json

# 上传整个目录（自动打包）
hsk-cli +host ./dist --format json

# 更新已有资源
hsk-cli +host ./new-dist --resource-id 1783317437166602000 --format json
```

### 5.2 deploy命令 - 构建并部署

**用途**：一键执行构建命令 → 上传构建产物到文件托管。适合前端项目快速发布预览。

**语法**：
```bash
hsk-cli +deploy [选项]
```

**常用选项**：
| 选项 | 说明 | 默认值 |
|---|---|---|
| `--build-cmd <cmd>` | 自定义构建命令 | `npm run build` |
| `--build-dir <dir>` | 构建产物目录 | `dist` |
| `--no-build` | 跳过构建，直接上传build-dir | - |
| `--resource-id <id>` | 更新指定资源 | - |
| `--format json` | 输出JSON格式 | - |

**项目配置**（package.json）：
```json
{
  "hsk": {
    "deploy": {
      "buildCmd": "npm run build",
      "buildDir": "dist"
    }
  }
}
```

**典型示例**：

```bash
# 默认构建并部署
hsk-cli +deploy --format json

# 跳过构建直接上传现有dist目录
hsk-cli +deploy --no-build --format json

# 自定义构建命令和目录
hsk-cli +deploy --build-cmd "pnpm build" --build-dir "output" --format json

# 更新已有部署
hsk-cli +deploy --resource-id 1783317437166602000 --format json
```

---

## 六、内网穿透（tunnel）🔌

### 6.1 tunnel命令 - 暴露本地端口

**用途**：将本地IP:端口暴露到公网，建立TCP隧道。仅当host/deploy无法满足需求时使用。

**语法**：
```bash
hsk-cli +tunnel --ip <IP> --port <PORT> [选项]
```

**参数说明**：
| 参数 | 说明 |
|---|---|
| `--ip <IP>` | 本地服务监听的IP地址（通常为127.0.0.1） |
| `--port <PORT>` | 本地服务监听的端口号 |

**常用选项**：
| 选项 | 说明 |
|---|---|
| `--detach` | 后台模式：CLI立即退出，隧道在后台持续运行 |
| `--reuse` | 复用已有隧道：检测已有隧道是否有效，有效则直接返回旧链接，失效则重建 |
| `--format json` | 输出JSON格式 |
| `--dry-run` | 仅预览，不实际创建隧道 |

**典型示例**：

```bash
# 前台模式（可看到日志，Ctrl+C停止）
hsk-cli +tunnel --ip 127.0.0.1 --port 3000 --format json

# 后台模式
hsk-cli +tunnel --ip 127.0.0.1 --port 8080 --detach --format json

# 复用已有隧道（避免重复创建）
hsk-cli +tunnel --ip 127.0.0.1 --port 5173 --reuse --format json
```

### 6.2 tunnel管理命令

```bash
# 列出所有后台隧道
hsk-cli tunnel list

# 停止全部后台隧道
hsk-cli tunnel stop --all

# 检查隧道状态（进程存活 + HTTP可访问）
hsk-cli status --format json
```

### 6.3 隧道排错指南

如果隧道启动后立即退出（无错误输出），按以下步骤排查：

1. **前台模式观察日志**：去掉`--detach`，运行前台模式看完整输出
2. **确认本地服务**：检查本地服务是否真实在监听：
   ```bash
   # Windows PowerShell
   curl http://127.0.0.1:<PORT>
   netstat -ano | findstr :<PORT>
   ```
3. **检查端口冲突**：确保端口未被其他进程占用
4. **检查权限**：macOS/Linux下端口<1024需要root权限；macOS需在系统设置→隐私与安全性→本地网络中允许终端访问
5. **检查防火墙**：确保系统防火墙未阻止该端口
6. **查看日志**：`cat ~/.hsk/logs/tunnel-*.log`（macOS/Linux）或`%USERPROFILE%\.hsk\logs\`（Windows）

---

## 七、常用命令速查 📖

### 7.1 完整命令列表

| 命令 | 说明 |
|------|------|
| `hsk-cli platform` | 检测操作系统和架构信息 |
| `hsk-cli update` | 下载/更新对应平台的原生二进制 |
| `hsk-cli download` | 预下载穿透客户端 |
| `hsk-cli +host <path>` | 上传文件或目录进行文件托管 |
| `hsk-cli +deploy` | 构建项目并部署到文件托管 |
| `hsk-cli deploy --no-build` | 跳过构建直接上传现有目录 |
| `hsk-cli +tunnel --ip <IP> --port <PORT>` | 创建内网穿透（前台运行） |
| `hsk-cli +tunnel --ip <IP> --port <PORT> --detach` | 创建内网穿透（后台运行） |
| `hsk-cli tunnel list` | 列出所有后台隧道 |
| `hsk-cli tunnel stop --all` | 停止全部后台隧道 |
| `hsk-cli status` | 检查隧道资源状态（进程+HTTP） |

### 7.2 Shortcuts快捷方式

`+`前缀是快捷方式，等效于原生命令：

| Shortcut | 等效原生命令 |
|----------|-------------|
| `+tunnel` | `tunnel` |
| `+host` | `host` |
| `+deploy` | `deploy` |

> **注意**：`+platform`在v0.4.3版本中不可用，请使用原生命令`hsk-cli platform`。

### 7.3 输出格式

```bash
--format json      # 结构化JSON，推荐AI Agent解析
--format pretty    # 人类可读格式（默认）
--dry-run          # 仅预览操作，不实际执行
```

---

## 八、AI Agent沙盒适配与实战场景 🤖

### 8.1 沙盒环境静默拦截识别

AI Agent在沙盒/容器（Docker、CI、某些IDE环境）中运行时，某些操作可能被**静默拦截**（不报错但也不执行）。HSK文档专门列出了识别与应对方案：

| 沙盒特征 | 识别方式 | 应对策略 |
|----------|----------|----------|
| `--open`无响应 | 不报错也不打开浏览器 | 跳过`--open`参数，告诉用户手动复制链接 |
| `--detach`进程消失 | `tunnel list`找不到隧道 | 去掉`--detach`，以前台模式运行tunnel |
| 网络请求挂起 | 无响应无输出也不报错 | 换用`host`模式代替`tunnel` |
| 文件写入丢失 | 写入后读取不到文件 | 使用`/tmp`或系统临时目录 |

**关键原则**：没有明确错误 = 可能被静默拦截。被拦截后**换方式**，不要无限重试。

### 8.2 AI Agent标准执行流程

**文件托管标准流程（推荐）**：
```
1. 准备文件/目录 → 2. hsk-cli +host <path> --format json → 3. 解析JSON获取publicUrl → 4. 向用户展示URL和激活提示
```

**内网穿透标准流程（降级）**：
```
1. 确认本地服务已在IP:PORT监听 → 2. hsk-cli +tunnel --ip <IP> --port <PORT> --format json（后台模式加--detach）→ 3. 持续读取stdout直到捕获publicUrl → 4. 向用户展示URL和激活提示 → 5. 保持隧道进程运行
```

**内容更新后标准协议**：
当用户说"更新内容后继续访问"时，先检测状态：
```bash
hsk-cli status --format json
```
- 返回`valid: true` → 告诉用户"链接仍然有效，刷新即可"
- 返回`valid: false` → 重新执行创建命令（加`--reuse`或新`--resource-id`），告诉用户新链接

### 8.3 实战场景一：AI Agent快速发布演示页面

AI Agent创建了一个数据分析HTML报表，一键发布到公网：

```bash
# 1. Agent生成报表页面report.html
# 2. 上传托管
hsk-cli +host ./report.html --format json
# 3. 解析publicUrl返回给用户
```

### 8.4 实战场景二：前端开发预览分享

本地开发的React/Vue项目，临时分享给同事或客户查看效果：

```bash
# 方式1：先构建再上传（推荐，稳定无需保活）
npm run build
hsk-cli +host ./dist --format json

# 方式2：一键构建部署
hsk-cli +deploy --format json

# 方式3：如果需要热更新，用tunnel暴露开发服务器
npm run dev  # 假设启动在5173端口
hsk-cli +tunnel --ip 127.0.0.1 --port 5173 --detach --format json
```

### 8.5 实战场景三：Webhook接收调试

开发微信/支付宝/Stripe等支付回调，需要公网HTTPS地址接收Webhook：

```bash
# 本地启动后端服务在3000端口
hsk-cli +tunnel --ip 127.0.0.1 --port 3000 --format json
# 将返回的publicUrl + /webhook路径配置到第三方平台后台
```

---

## 九、专业洞察、常见问题与资源链接 💡

### 9.1 专业洞察

#### AI原生工具文档的"沙盒前置"设计

HSK CLI文档是AI原生工具设计的典范，在最开头就设置了：
1. **决策指南**：明确告诉Agent"优先host，仅特定场景用tunnel"
2. **沙盒环境专节**：列出4种静默拦截场景及应对方案，赋予Agent自我诊断能力
3. **失败处理表格**：覆盖8种常见错误场景，给出明确处理方式

这种设计大幅降低了AI Agent的决策成本和错误率，是CLI工具面向AI时代的重要演进方向。

#### "Node包装器+原生二进制"分发架构

HSK采用分层架构：npm包作为轻量入口负责平台检测、参数解析、二进制下载，核心功能由Go/Rust原生二进制实现。这种架构结合了Node.js生态的安装便利性和原生代码的跨平台一致性、高性能优势。

#### 匿名先行的增长漏斗

HSK采用"先体验价值，再建立账户"的PLG（Product-Led Growth）策略：匿名即可创建资源获得价值，用户需要长期管理时再引导注册认领，大幅降低了使用门槛，尤其适合AI Agent的自动化场景。

#### AI原生CLI工具的5个成熟度标志

| 标志 | HSK实现 |
|------|---------|
| 结构化JSON输出 | ✅ --format json输出稳定字段 |
| 全参数命令行传递 | ✅ 匿名模式无需交互输入 |
| 沙盒适配文档 | ✅ 专门章节说明静默拦截 |
| 内置决策指南 | ✅ 开头即给功能选择决策树 |
| dry-run预览 | ✅ 支持--dry-run预验证 |

### 9.2 常见问题

#### Q: 创建的资源有效期多久？
匿名资源在未认领前有一定有效期，建议打开链接完成激活认领，认领后可在控制台管理续期。

#### Q: 支持自定义域名吗？
匿名托管资源使用贝锐提供的默认域名，企业版可能支持自定义域名绑定，请参考官方文档或控制台。

#### Q: 文件大小有限制吗？
具体限制请参考官方最新说明，一般静态页面、图片、PDF等常规文件都可以正常上传。

#### Q: 隧道支持UDP吗？
当前版本主要支持TCP隧道（HTTP/HTTPS/WebSocket等基于TCP的协议）。

#### Q: 可以同时创建多个隧道吗？
可以，多次执行tunnel命令即可创建多个隧道，使用`tunnel list`查看所有后台隧道。

#### Q: +platform命令为什么报错"未知Shortcut"？
v0.4.3版本中`+platform`快捷方式不可用，请使用原生命令`hsk-cli platform`。原生命令在所有版本都可用，遇到快捷方式失败时可尝试去掉+前缀使用原生命令。

### 9.3 与其他工具对比

| 工具 | 核心定位 | 匿名使用 | 静态托管 | 内网穿透 | AI友好度 |
|------|---------|---------|---------|---------|---------|
| **hsk-cli** | 零配置公网预览 | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| ngrok | 内网穿透 | ✅ | ❌ | ✅ | ⭐⭐⭐ |
| serveo | 内网穿透 | ✅ | ❌ | ✅ | ⭐⭐ |
| Vercel/Netlify CLI | 前端部署 | ❌（需登录） | ✅ | ❌ | ⭐⭐⭐ |
| awesun-cli | 远程控制 | ❌（需登录） | ❌ | ✅（端口转发） | ⭐⭐⭐⭐ |

HSK的差异化优势：同时支持静态托管和内网穿透、匿名免登、AI Agent沙盒适配、文档决策指南内置。

### 9.4 相关资源链接

| 资源 | 链接 |
|---|---|
| HSK官方文档 | https://hsk.oray.com/doc/cli-setup.md |
| HSK控制台 | https://console-hsk-ng.oray.com/ |
| npm包地址 | https://www.npmjs.com/package/@aweray/hsk-cli |
| 向日葵企业CLI（awesun-cli）教程 | [sunlogin-cli-wiki.md](sunlogin-cli-wiki.md) |
| 向日葵产品全面解析 | [sunlogin-comprehensive-analysis-wiki.md](sunlogin-comprehensive-analysis-wiki.md) |
| 向日葵产品系列索引 | [sunlogin-product-series-index.md](sunlogin-product-series-index.md) |
| 向日葵AI开发者生态 | [sunlogin-ai-developer-ecosystem-wiki.md](sunlogin-ai-developer-ecosystem-wiki.md) |
