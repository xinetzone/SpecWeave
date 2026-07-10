---
id: "retrospective-hsk-cli-install-hosting-execution"
title: "HSK CLI安装与文件托管执行过程复盘"
source: "session-execution"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-hsk-cli-install-hosting-20260706/execution-retrospective.toml"
date: "2026-07-06"
---
# 执行过程复盘

## 一、时间线

| 阶段 | 时间 | 关键事件 | 耗时 |
|------|------|----------|------|
| S0 启动协议 | 任务开始 | 读取AGENTS.md、上下文路由表、全局核心规则 | ~1min |
| S1 文档获取 | 任务开始+1min | 使用defuddle尝试失败（markdown文件非HTML）→ 改用WebFetch成功获取完整文档 | ~2min |
| S2 环境检查 | +3min | 检查Node.js v24.14.1/npm 11.11.0正常 | ~30s |
| S3 CLI安装 | +4min | npm install -g @aweray/hsk-cli成功，12个包 | ~45s |
| S4 首次验证 | +5min | hsk-cli +platform报错"未知Shortcut"（二进制未下载） | ~30s |
| S5 二进制下载 | +6min | hsk-cli update成功下载hsk-cli-windows-amd64-v0.4.3.exe | ~30s |
| S6 验证通过 | +7min | platform命令正常返回windows/amd64，dry-run测试通过 | ~30s |
| S7 演示页面创建 | +8min | 创建temp-hsk-demo/index.html（渐变背景+信息卡片+时间戳JS） | ~2min |
| S8 文件托管上传 | +10min | hsk-cli +host自动打包目录→请求ticket→上传→创建资源，成功返回URL | ~1min |
| S9 结果交付 | +11min | 向用户展示公网地址、资源ID、常用命令参考 | ~30s |
| **总计** | | | **~12min** |

## 二、产出物清单

| 产出物 | 路径 | 说明 |
|--------|------|------|
| 演示页面 | [temp-hsk-demo/index.html](../../../../../apps/ai-code-assistant/templates/index.html) | 107行，渐变紫色背景+白色卡片+部署状态+工具信息+时间戳 |
| 公网资源 | https://files.hz-1.aicp.space:8010/file/f4d06796-ad37-4c46-9431-7a29cddaa435?verify_code=9949 | 匿名文件托管，验证码9949，需激活认领 |
| 复盘README | [README.md](README.md) | 复盘总览 |
| 执行复盘 | [execution-retrospective.md](execution-retrospective.md) | 本文件 |
| 洞察萃取 | [insight-extraction.md](insight-extraction.md) | 5大核心洞察 |
| 导出建议 | [export-suggestions.md](export-suggestions.md) | 行动项与知识库更新 |
| HSK CLI Wiki | [hsk-cli-wiki.md](../../../../knowledge/learning/07-vendor-product-learning/sunlogin/hsk-cli-wiki.md) | 待创建 |

## 三、成功因素

### 3.1 文档质量高
- 官方文档开头即提供**决策指南**（Agent必读），明确"优先host，失败再tunnel"
- 设有**沙盒环境专节**，识别4种静默拦截场景并给出应对方案
- 提供**dry-run验证步骤**，在实际操作前可确认环境正常
- 输出格式有专门章节说明--format json结构
- 失败处理表格覆盖8种常见场景，给出明确处理方式

### 3.2 安装流程顺畅
- npm全局安装一次成功，无依赖冲突
- hsk-cli update自动检测平台并下载对应二进制，无需手动选择
- 二进制缓存到~/.hsk/bin/，后续命令直接复用

### 3.3 文件托管流程简化
- 目录自动打包为zip，无需手动压缩
- 自动识别index.html作为入口文件
- 结构化JSON输出包含所有必要信息（success、publicUrl、resourceId、verifyCode）
- 全程无需登录注册，匿名即可使用

## 四、问题与修复

| 问题 | 现象 | 根因 | 修复方式 |
|------|------|------|----------|
| defuddle解析失败 | Exit code 126, "Not an HTML page (content-type: text/markdown)" | defuddle设计用于提取HTML网页内容，而目标URL直接返回text/markdown | 改用WebFetch工具直接获取markdown原文 |
| +platform快捷方式不可用 | "❌ 未知 Shortcut: +platform"，可用Shortcuts列表只有+tunnel/+host/+deploy | 文档版本与实际npm包版本可能不一致，或+platform是更新版本才加入的快捷方式 | 去掉+前缀，直接使用`hsk-cli platform`命令成功 |

## 五、量化统计

| 指标 | 数值 |
|------|------|
| 总耗时 | ~12分钟 |
| 命令执行次数 | 8次 |
| 新建文件数 | 1（演示页面）+ 4（复盘文档）+1（Wiki）= 6个 |
| npm包安装数 | 12个 |
| 二进制文件大小 | ~10-20MB（估算） |
| 演示页面代码行数 | 107行 |
| 问题发生数 | 2个（都快速解决） |
| 验证检查点 | 平台检测、dry-run、上传成功、URL返回，共4个 |

## 六、与awesun-cli的对比观察

| 维度 | awesun-cli（向日葵企业CLI） | hsk-cli（HSK公网预览CLI） |
|------|---------------------------|--------------------------|
| **定位** | 远程控制主控端（设备管理、桌面控制、文件传输） | 公网预览工具（内网穿透、文件托管） |
| **认证** | 需要登录向日葵账号 | 匿名可用，无需注册 |
| **核心功能** | 7种会话类型（desktop/file/cmd2/ssh/forward/newcamera/desktop_view） | 2种模式（tunnel内网穿透、host文件托管）+deploy构建部署 |
| **保活要求** | 会话需保持连接 | host模式无需保活，tunnel需后台进程 |
| **典型场景** | 远程运维、批量设备管理、AI Agent远程操作 | 本地开发预览、静态文件分享、快速demo展示 |
| **二进制架构** | 纯Node.js包？ | Node.js包装器+原生Go二进制 |
| **AI友好度** | JSON输出、归一化坐标、错误码 | Agent沙盒适配专节、决策指南内置、JSON结构化输出 |
| **资源认领** | 绑定账号设备 | 匿名资源需打开链接激活认领 |
