---
type: Concept
title: 登录与鉴权：站点选择与两种登录方式
description: 登录前必须先确认 China 或 Global 站点；桌面环境用浏览器登录，远程/无头/CI 环境用 API Token，Token 具备账号级权限不可入库
tags: [edgeone, login, auth, token, china, global]
generated:
  by: agent-workbuddy
  at: "2026-09-29T14:47:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-29T14:47:00+08:00"
status: draft
stale_after: "2027-09-29"
sources:
  - id: S-001
    resource: /references/00-sources.md
    title: EdgeOne Pages Deploy 技能文档
  - id: S-003
    resource: /references/00-sources.md
    title: EdgeOne Pages 官方控制台
  - id: S-005
    resource: /references/00-sources.md
    title: EdgeOne Pages 国际站控制台
---

# 登录与鉴权：站点选择与两种登录方式

部署产物要上传到「你自己的账号下」，因此必须先完成鉴权。登录有两个决策点：**选哪个站点**、**用哪种登录方式**。两者都应在执行前与使用者确认，不代为假定。

## 决策点一：站点（China / Global）

| 站点 | 控制台 | 适用 |
|---|---|---|
| China | `console.cloud.tencent.com/edgeone/pages` | 中国大陆用户；便于绑定已备案域名 |
| Global | `console.intl.cloud.tencent.com/edgeone/pages` | 中国大陆以外用户 |

## 决策点二：登录方式

| 环境 | 方式 |
|---|---|
| 本地桌面 IDE（有浏览器） | 浏览器登录 |
| 远程 / SSH / 容器 / CI / 无头环境 | Token 登录 |
| 用户明确要求 | Token 登录 |

## 方式一：浏览器登录（桌面环境）

```bash
# 国内站
edgeone login --site china

# 国际站
edgeone login --site global
```

执行后 CLI 输出跳转链接并尝试自动打开浏览器：

```
[cli] Jumping to login page...
[cli] Please come back after login.
If the browser does not open automatically, please visit:
https://cloud.tencent.com/login?s_url=...&state=<uuid>
[cli][✔] .gitignore updated!
[cli][✔] Login successfully!
```

实测从执行命令到 `Login successfully` 约 11 秒。若浏览器未自动弹出，手动打开输出中的 URL 完成登录即可。

### 登录前的告知义务

触发登录会弹出浏览器窗口，属于外部动作。执行前应先说明：为什么需要登录（产物要挂到你账号下）、免费额度包含什么（CDN 加速、自动 HTTPS、自定义域名绑定）、接下来会发生什么（浏览器弹出腾讯云登录页）、卡住时怎么办（切换 Token 登录）。不要静默弹出浏览器。

### 浏览器 Session 复用陷阱

若此前在同一浏览器登录过**另一个站点**（如之前登过国际站、这次登国内站，或反之），浏览器可能静默复用旧 session，CLI 显示登录成功但实际绑定了错误账号，后续 `deploy` 才会报鉴权错误。

处理：在登录页点击「使用其他账户登录」切换；或先从所有腾讯云控制台退出后再重新登录。

## 方式二：Token 登录（远程 / CI）

Token 登录**不使用** `edgeone login`，而是在部署命令中用 `-t` 传入：

```bash
edgeone pages deploy -n <project-name> -t <token>
```

获取 Token：

1. 打开对应站点控制台的 `?tab=settings` 页面
2. 找到 **API Token** → **Create Token** → 复制

Token 已包含站点信息，部署时无需再加 `--site`。

> ⚠️ Token 具备**账号级权限**，不要提交进仓库。确需本地保存时写入 `.edgeone/.token` 并确保该文件已加入 `.gitignore`。

## 检查登录状态

```bash
edgeone whoami
```

未登录返回：

```
[cli][✘] You are not authenticated. Please run `edgeone login`, or set EDGEONE_PAGES_API_TOKEN.
```

也可设置环境变量 `EDGEONE_PAGES_API_TOKEN` 代替 `-t` 参数。

## 相关概念

- [EdgeOne Pages 平台概览](/concepts/00-overview.md)
- [CLI 安装与排错](/concepts/01-cli-install.md)
- [部署静态站点](/concepts/03-deploy-static.md)
