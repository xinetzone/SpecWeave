# 信源登记簿

## 信源文件（Source Registration）

* [Home Assistant Components 集成源码](/references/components-source.md) — 组件集成层源码登记，包含 manifest.json 规范、实体平台、ConfigFlow、服务发现与代表性集成
* [Home Assistant 核心框架源码](/references/core-source.md) — Core 运行时内核源码登记，包含核心对象、事件总线、状态机、服务注册、启动流程、认证体系与异常层次
* [Home Assistant Helpers 与 Util 源码](/references/helpers-util-source.md) — 辅助工具库源码登记，包含实体基类、设备注册表、模板引擎、存储系统、事件辅助、配置验证、选择器与通用工具
* [Home Assistant 工具链与测试源码](/references/tooling-source.md) — 开发工具链源码登记，包含 hassfest 验证器、scaffold 脚手架、翻译工具、pytest 测试基础设施与 CI 配置

## 事实文件（Facts）

* [Home Assistant Components 集成模式事实清单](/references/facts-components.md) — R 阶段采集的集成层源码事实
* [Home Assistant Core 核心架构事实清单](/references/facts-core.md) — R 阶段采集的核心运行时源码事实
* [Home Assistant Helpers 与 Util 事实清单](/references/facts-helpers.md) — R 阶段采集的辅助工具库源码事实
* [Home Assistant 工具链与测试模式事实清单](/references/facts-tooling.md) — R 阶段采集的工具链与测试基础设施源码事实

## 洞察文件（Insights）

* [Home Assistant 架构洞察](/references/insights.md) — I 阶段分析的核心架构洞察与概念文档知识地图

```{toctree}
:maxdepth: 2

components-source
core-source
facts-components
facts-core
facts-helpers
facts-tooling
helpers-util-source
insights
tooling-source
```