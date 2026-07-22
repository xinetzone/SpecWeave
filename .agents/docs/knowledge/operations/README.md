---
id: "operations-index"
title: "运维操作指南库"
x-toml-ref: "../../../../.meta/toml/.agents/docs/knowledge/operations/README.toml"
category: "operations"
date: "2026-07-09"
---
# 运维操作指南库

## 🎯 什么是运维操作指南

> **运维操作指南**是从项目实战中提炼的可复用操作手册，覆盖工具集成、平台兼容、内容提取、设备对接等高频场景。每份指南包含：决策流程、可执行代码示例、常见陷阱、验证方法。
>
> 与「故障排查」的区别：操作指南侧重"怎么做"（正向流程），故障排查侧重"出问题怎么办"（反向修复）。

### 文档状态说明

| 状态 | 含义 |
|------|------|
| ✅ `stable` | 经过多次实战验证，可直接套用 |
| 🔍 `reviewed` | 已审核通过，在至少一个场景中验证过 |
| 📝 `draft` | 草稿阶段，内容可能不完整 |

---

## 📚 分类索引

共 13 篇操作指南，按主题分为 8 大类：

### 💬 Discourse / 论坛自动化

| 文档 | 一句话摘要 | 状态 |
|------|-----------|------|
| [forum-automation.md](forum-automation.md) | Discourse论坛（forum.trae.cn）自动化操作完整指南：5种技术方案对比（Playwright脚本/MCP/REST API等）、DOM选择器、Ember框架感知操作 | ✅ stable |
| [discourse-api-research.md](discourse-api-research.md) | Discourse REST API核心端点调研：发帖/编辑/回复等API参数与调用示例 | 🔍 reviewed |

### 🪟 Windows 平台兼容

| 文档 | 一句话摘要 | 状态 |
|------|-----------|------|
| [windows-platform-compatibility-guide.md](windows-platform-compatibility-guide.md) | Windows平台10类陷阱系统化手册：编码/URL解析/管道/heredoc/路径/命令链接/引号/脚本/行尾/环境变量 | ✅ stable |
| [windows-terminal-utf8-complete-guide.md](windows-terminal-utf8-complete-guide.md) | Windows终端UTF-8编码三层配置指南（系统级/用户级/项目级），解决中文乱码 | 🔍 reviewed |
| [windows-powershell-pipe-utf8.md](windows-powershell-pipe-utf8.md) | PowerShell管道转码污染问题：Python stdout通过管道写入中文文件乱码的根因与安全写回方案 | 🔍 reviewed |
| [windows-powershell-heredoc.md](windows-powershell-heredoc.md) | PowerShell heredoc语法替代方案：`<<'EOF'`不可用时的Here-String正确写法 | 🔍 reviewed |

### 📄 内容提取

| 文档 | 一句话摘要 | 状态 |
|------|-----------|------|
| [html-body-extraction.md](html-body-extraction.md) | HTML正文提取双方案：正则提取（首选）+ 边界标记索引截取法（兜底），含HTML清洗六步流程 | ✅ stable |
| [wechat-mp-content-extraction.md](wechat-mp-content-extraction.md) | 微信公众号文章提取双路径决策模型：defuddle CLI 与 PowerShell Invoke-WebRequest 互为兜底 | ✅ stable |

### 🛡️ 工具降级与可靠性

| 文档 | 一句话摘要 | 状态 |
|------|-----------|------|
| [tool-failure-degradation-matrix.md](tool-failure-degradation-matrix.md) | 关键路径工具三级降级矩阵：网页内容获取/文件搜索/命令执行/子代理委派四类场景的L1/L2/L3降级策略与触发条件 | ✅ stable |

### 🔗 文档链接修复

| 文档 | 一句话摘要 | 状态 |
|------|-----------|------|
| [frontmatter-link-batch-repair-guide.md](frontmatter-link-batch-repair-guide.md) | Frontmatter路径与Markdown链接批量修复8阶段流程：问题分类诊断→分层自动化修复→external标记约定→LF行尾保留→TOML同步，附8个脚本使用参考 | ✅ stable |

### 📦 Vendor 集成

| 文档 | 一句话摘要 | 状态 |
|------|-----------|------|
| [vendor-flexloop-integration-guide.md](vendor-flexloop-integration-guide.md) | vendor/flexloop功能集成决策指南：三区域边界模型+四不原则+5种合规集成路径（萃取/参考/更新/PR/接口扩展） | 🔍 reviewed |

### 🔌 IoT 设备集成

| 文档 | 一句话摘要 | 状态 |
|------|-----------|------|
| [tuya-ipc-minimal-closed-loop.md](tuya-ipc-minimal-closed-loop.md) | Tuya IPC（网络摄像机）端-云-手机最小闭环跑通路径：配网/音视频/事件上报全流程，含验收标准与排查方法 | 📝 draft |

### 🐳 Docker / 容器构建

| 文档 | 一句话摘要 | 状态 |
|------|-----------|------|
| [caffe-docker-sop.md](caffe-docker-sop.md) | Caffe Docker 容器构建与运行完整 SOP：构建→验证→运行→导出→故障排查，含 5 阶段 Dockerfile、6 项验证清单、8 项故障排查 | ✅ stable |

---

## ⚡ 快速参考

### 常见任务速查

| 任务场景 | 推荐文档 | 快速提示 |
|---------|---------|---------|
| 🔗 在 forum.trae.cn 发帖/回帖 | [forum-automation.md](forum-automation.md) | IDE内首选 integrated_browser MCP，本地/CI首选 forum-bot.py |
| 🪟 Windows 下中文乱码 | [windows-platform-compatibility-guide.md](windows-platform-compatibility-guide.md) | 先看分类总览表定位陷阱类型，再跳转对应专文 |
| 📝 提取网页正文 | [html-body-extraction.md](html-body-extraction.md) | 先试正则，失败用边界标记索引截取法 |
| 💬 提取微信公众号文章 | [wechat-mp-content-extraction.md](wechat-mp-content-extraction.md) | WebFetch通常失败，按环境选defuddle或Invoke-WebRequest |
| 🔧 工具调用失败怎么办 | [tool-failure-degradation-matrix.md](tool-failure-degradation-matrix.md) | L1首选→L2降级→L3兜底，按矩阵查表 |
| 🔗 frontmatter路径/链接批量修复 | [frontmatter-link-batch-repair-guide.md](frontmatter-link-batch-repair-guide.md) | 先诊断分类，再按8阶段分层修复，每层验证后进入下一层 |
| 📦 想使用flexloop功能 | [vendor-flexloop-integration-guide.md](vendor-flexloop-integration-guide.md) | 严禁直接修改vendor/flexloop/，按决策树选合规路径 |
| 📋 PowerShell多行字符串 | [windows-powershell-heredoc.md](windows-powershell-heredoc.md) | 用 `@'...'@` Here-String 替代 `<<'EOF'` |
| 🐳 构建 Caffe Docker 镜像 | [caffe-docker-sop.md](caffe-docker-sop.md) | 一键构建：`./build/build-multistage.sh --target runtime --verify` |

### 跨文档导航

| 问题类型 | 应去 |
|---------|------|
| 操作过程中遇到Bug | [📁 故障排查指南](../troubleshooting/README.md) |
| 架构决策背景与理由 | [📁 架构决策记录](../decisions/README.md) |
| 方法论/最佳实践 | [📁 团队最佳实践库](../best-practices/README.md) |

---

## 🔗 相关资源

- [🏠 知识库首页](../README.md) - 返回知识库总入口
- [📁 故障排查指南](../troubleshooting/README.md) - 操作过程中遇到问题时查阅
- [📁 架构决策记录](../decisions/README.md) - 理解操作背后的决策依据
- [📁 团队最佳实践库](../best-practices/README.md) - 通用方法论与Checklist
- [🔧 check-links.py](../../../scripts/check-links.py) - 文档链接有效性验证工具
