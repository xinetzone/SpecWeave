# Home Assistant 知识包

本知识包（bundle）系统梳理 Home Assistant 开源智能家居平台的核心架构与集成开发体系，涵盖三层架构（核心-集成-平台）、运行时内核（HomeAssistant 对象、事件总线、状态机、服务注册表、实体模型）、配置系统、认证权限、helpers/util 工具库、集成开发模式（manifest、ConfigFlow、平台实体基类）、hassfest 质量工具链（29 个验证器、四级 quality_scale）和 pytest 测试基础设施。内容基于 Home Assistant Core 源码提取，遵循 OKF v0.2 规范，零虚构。

## 知识地图

### 基础组：平台认知与启动（00-06）

建立对 Home Assistant 的整体认知，理解其架构设计与启动机制：

* [00 — 概览](/concepts/00-overview.md) — 平台定位、核心能力与架构一览
* [01 — 三层架构](/concepts/01-architecture.md) — 核心层、集成层、平台层的职责划分
* [02 — 安装与启动](/concepts/02-installation-runner.md) — runner.py 入口、命令行参数、事件循环策略
* [03 — 核心对象](/concepts/03-core-object.md) — HomeAssistant 根对象与 CoreState 状态机
* [04 — 启动流程](/concepts/04-bootstrap-lifecycle.md) — bootstrap 阶段、组件加载顺序与依赖解析
* [05 — 配置系统](/concepts/05-configuration.md) — configuration.yaml、Config 类、secrets 管理
* [06 — 事件总线](/concepts/06-event-bus.md) — EventBus 发布订阅与内置事件类型

### 核心组：运行时与工具库（07-13）

深入 HA 运行时内核与辅助工具，掌握二次开发的基础设施：

* [07 — 状态机](/concepts/07-state-machine.md) — State 对象、async_set/async_remove、状态恢复
* [08 — 服务注册表](/concepts/08-service-registry.md) — ServiceRegistry、实体服务装饰器、服务描述
* [09 — 实体模型](/concepts/09-entity-model.md) — Entity 基类、EntityDescription、cached_properties
* [10 — 注册表](/concepts/10-registries.md) — Device/Entity/Area Registry 与 DeviceInfo
* [11 — 认证与权限](/concepts/11-auth-permissions.md) — AuthManager、JWT 令牌、权限策略与角色
* [12 — Helpers 工具库](/concepts/12-helpers-library.md) — Template、Debouncer、Storage、Selector
* [13 — Util 工具集](/concepts/13-utilities.md) — dt/json/yaml/async/color/ulid/network 工具

### 高级/开发组：集成开发（14-18）

面向集成开发者，掌握从 manifest 声明到测试验证的完整开发工作流：

* [14 — 集成架构](/concepts/14-component-architecture.md) — manifest.json、生命周期三函数、依赖解析
* [15 — 配置流](/concepts/15-config-flow.md) — ConfigFlow 状态机、OptionsFlow、配置迁移
* [16 — 平台开发模式](/concepts/16-platform-pattern.md) — Light/Sensor/Switch 基类、EntityDescription、服务注册
* [17 — hassfest 工具链](/concepts/17-hassfest-tooling.md) — 29 个验证器、quality_scale 四级标准、scaffold
* [18 — 测试模式](/concepts/18-testing-patterns.md) — pytest fixtures、syrupy 快照、MockConfigEntry、禁网策略

## 快速链接

* [概念文档索引](/concepts/index.md) — 全部 19 篇概念文档，按三组分类
* [示例索引](/examples/index.md) — 完整自定义集成示例
* [信源登记簿](/references/index.md) — 4 个信源文件、4 个事实文件与洞察文件
* [变更日志](/log.md) — 文档生成与验证记录

```{toctree}
:maxdepth: 2

concepts/index
examples/index
references/index
log
verification-report
```