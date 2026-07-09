---
id: "analyze-omniroute-ai-gateway-06"
title: "工具集成与部署方式"
theme: "retrospectives-insights"
source: "article-content.md"
chapter: 6
created: "2026-07-09"
---

# 工具集成与部署方式

## 工具一键接入

OmniRoute支持24+工具一键接入，包括Claude Code、Codex、Cursor、Cline、Copilot等主流AI开发工具。

## setup命令

提供一行setup命令自动生成配置文件，用户无需手动修改JSON或环境变量，大幅降低接入门槛。

## 部署方式

### npm安装

```bash
npm install -g omniroute
omniroute
```

### Docker部署

```bash
docker run -d \
  -p 20128:20128 \
  -v omniroute-data:/app/data \
  --restart unless-stopped \
  omniroute/omniroute
```

包含完整端口映射、数据卷挂载、重启策略。

### 其他部署方式

- PWA应用
- Electron桌面版（支持Windows/macOS/Linux）

## Remote模式

支持VPS远程部署，本地使用 `omniroute connect` 命令远程控制，实现云端运行本地使用。

## 三级权限token

提供三级权限体系：read、write、admin，满足不同场景的权限控制需求。

## 兼容地址方案

支持带token的URL方案，例如 `http://localhost:20128/vscode/YOUR_KEY/chat/completions`，解决部分客户端无法发送自定义header的兼容性问题。

## 环境要求

- Node版本要求：>=22.0.0 <23
- 本地编译慢可设置环境变量 `OMNIROUTE_SKIP_POSTINSTALL=1` 跳过构建

## 验证命令

服务启动后可使用以下命令验证：

```bash
curl http://localhost:20128/v1/models -H "Authorization: Bearer YOUR_KEY"
```
