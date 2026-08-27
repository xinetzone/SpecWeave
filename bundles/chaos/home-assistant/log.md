---
type: Changelog
title: 变更日志
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
---

# 变更日志

## 2026-08-23

- 初始生成 Home Assistant OKF v0.2 文档 bundle
- 基于 R 阶段事实清单（facts-core、facts-components、facts-helpers、facts-tooling）与 I 阶段架构洞察生成
- 分三批生成 19 篇概念文档：
  - 第一批（基础组，00-06）：概览、三层架构、安装与启动、核心对象、启动流程、配置系统、事件总线
  - 第二批（核心组，07-13）：状态机、服务注册表、实体模型、注册表、认证与权限、Helpers 工具库、Util 工具集
  - 第三批（高级/开发组，14-18）：集成架构、配置流、平台开发模式、hassfest 工具链、测试模式
- 创建 1 篇示例文档：完整自定义集成示例（manifest.json + __init__.py + light + config_flow + strings.json）
- 创建 4 篇信源登记文件：核心框架源码、Components 集成源码、Helpers 与 Util 源码、工具链与测试源码
- 创建 4 篇事实文件：Core、Components、Helpers、Tooling 事实清单
- 创建所有索引文件（根 index.md、concepts/index.md、references/index.md、examples/index.md）
- 关键 API/类名/方法名均经源码 Grep 验证（ConfigFlow、async_setup_entry、LightEntity、EntityDescription、hassfest 验证插件、pytest fixtures 等）
- 高级组侧重"如何开发集成"，代码示例完整可运行
