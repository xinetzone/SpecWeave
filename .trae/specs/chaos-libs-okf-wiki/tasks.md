# .chaos/libs 全量子项目 OKF Wiki 教程生成 - 实施计划

> **执行顺序原则**：按 bundle 复杂度从低到高排列，先在小型项目上验证工作流，再应用于大型项目。每个 bundle 独立完成 R→I→E→V 闭环。大型项目的 R 阶段按子系统拆分。所有任务通过子代理委派执行。

---

## 阶段一：小型 Bundle（建立工作流基线）

### [x] Task 1: okf-ecosystem bundle — R 阶段事实采集

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 阅读 `tests/okf-kit/okf_kit/` 全部 29 个 Python 文件和 `tests/okf-desktop/` 的 shell/app.py + ui/src/api.js
  - 提取编号事实清单：CLI 命令结构、核心模块（cli.py/mcp.py/okf.py）、MCP 服务接口、crawl/build/sync/validate 流程
  - 事实写入 `bundles/okf-ecosystem/references/facts-okf-kit.md` 和 `facts-okf-desktop.md`
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: 事实文件存在且每条事实包含源码文件路径
  - `human-judgement` TR-1.2: 事实中无"用于/目的是/设计为"等推断词
- **Notes**: 这是第一个 bundle，重点验证工作流可行性

### [x] Task 2: okf-ecosystem bundle — I 阶段架构洞察

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于事实清单提炼 3 个核心洞察（OKF bundle 数据模型、crawl→build→sync 流水线、MCP/chat 集成架构）
  - 设计知识地图：concepts/ 文档清单（00-okf-overview, 01-build-crawl, 02-sync-validate, 03-mcp-serve, 04-chat, 05-desktop-app）
  - 洞察写入 `bundles/okf-ecosystem/references/insights.md`
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `human-judgement` TR-2.1: 每条洞察含陈述/证据(F-xxx)/反常识/行动四元组

### [x] Task 3: okf-ecosystem bundle — E 阶段生成文档

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 步骤 1：生成 `references/` 信源文件（okf-kit-source.md, okf-desktop-source.md）
  - 步骤 2：分批生成 `concepts/` 6 个概念文档（每批 ≤7，一批完成）
  - 步骤 3：生成 `examples/` 示例文档（CLI 用法示例）
  - 步骤 4：最后生成根 index.md（含 okf_version）、concepts/index.md、examples/index.md、references/index.md、log.md
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-3.1: references/ 文件先于 concepts/ 创建（检查文件时间戳）
  - `programmatic` TR-3.2: 所有 .md 文件（非 index）含完整 frontmatter
  - `programmatic` TR-3.3: 所有交叉链接目标存在
  - `human-judgement` TR-3.4: 概念文档 500-5000 字，含"相关概念"章节

### [x] Task 4: okf-ecosystem bundle — V 阶段验证

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 结构检查、frontmatter 检查、链接检查
  - Grep 验证：文档中出现的每个类名/方法名/CLI 命令在 `tests/okf-kit/` 和 `tests/okf-desktop/` 源码中存在
  - 代码示例检查：CLI 命令与源码 argparse/click 定义一致
  - 输出验证报告，修复所有问题
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: Grep 验证零虚构 API
  - `programmatic` TR-4.2: 零断裂链接
  - `human-judgement` TR-4.3: 代码示例可执行/语法正确

### [x] Task 5: mobile-use bundle — R 阶段事实采集

- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 阅读 `mobile-use/` 全部 109 个 Python 文件，重点关注核心模块
  - 提取事实：Agent 架构、设备控制层、LLM 配置、UI 理解、数据抓取流程
  - 事实写入 `bundles/mobile-use/references/facts.md`
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 事实覆盖所有核心 Python 模块
  - `human-judgement` TR-5.2: 零推断表述

### [x] Task 6: mobile-use bundle — I→E→V 全流程

- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - I: 提炼洞察（自然语言→UI操作映射、设备抽象层、LLM可插拔架构），设计知识地图
  - E: 生成 references/ → concepts/（5-7个）→ examples/ → index.md
  - V: Grep 验证 API、链接检查、frontmatter 检查
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-6.1: 全部检查通过
  - `human-judgement` TR-6.2: 学习路径从入门到高级递进

---

## 阶段二：中型 Bundle

### [x] Task 7: veadk-python bundle — R 阶段事实采集

- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 阅读 `veadk-python/veadk/` 全部 438 个 Python 文件，按子系统分批：
    - agent.py, config.py, consts.py, runner.py, types.py（核心）
    - 各子模块目录（llm, tools, memory, workflow 等）
  - 提取事实：Agent 类、配置系统、LLM provider 抽象、工具注册、评估器
  - 事实写入 `bundles/veadk-python/references/facts.md`
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 事实覆盖 veadk/ 下所有子目录
  - `human-judgement` TR-7.2: 核心类/方法签名准确

### [x] Task 8: veadk-python bundle — I→E→V 全流程

- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - I: 洞察（Agent 生命周期、YAML 配置驱动、多 LLM provider 适配、evaluator 评估体系）
  - E: references/ → concepts/（8-12个，分2批，每批≤7）→ examples/ → index
  - V: Grep 验证、链接检查、frontmatter 检查
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-8.1: 分批生成（concepts 分2批）
  - `programmatic` TR-8.2: 全部验证通过
  - `human-judgement` TR-8.3: API 签名与源码一致

### [x] Task 9: ai-agent-skills bundle — R 阶段事实采集

- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 阅读 `agency-agents/` 的 divisions.json、tools.json、scripts/ 下的 shell/python 脚本，以及每个 division（engineering/marketing/design 等）的代表性 agent 文件
  - 阅读 `awesun-mcp/docs/mcp_tools.md`（MCP 工具规格）、`awesun-skill/`、`awesun-ui-locator/` 的 SKILL.md 和脚本
  - 阅读 `tests/jira-skill/` 的 skills/ 目录和 Python CLI 脚本
  - 阅读 `tests/retro-skill/` 的 skills/retro/ 目录和 scripts/
  - 事实写入 `bundles/ai-agent-skills/references/facts-*.md`（每个子项目一个文件）
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: 6 个子项目各有 facts 文件
  - `human-judgement` TR-9.2: agent 人格文件的结构模式被准确记录

### [x] Task 10: ai-agent-skills bundle — I→E→V 全流程

- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - I: 洞察（Agent Skills 开放标准、SKILL.md 渐进式披露模式、MCP vs Skill 两种集成范式、多工具兼容适配层）
  - E: references/ → concepts/（10-14个，分2批）→ examples/ → index
  - V: 验证脚本路径、SKILL.md 字段、工具名一致性
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-10.1: Grep 验证脚本文件名和路径
  - `programmatic` TR-10.2: 全部链接有效
  - `human-judgement` TR-10.3: agent 分类体系完整覆盖 12 个 division

---

## 阶段三：大型 Bundle

### [x] Task 11: apache-tvm bundle — R 阶段模块 1（IR 核心 + TIR）

- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 精读 `ffi/tvm/src/ir/`（attrs.cc, env_func.cc, expr.cc, function.cc, module.cc, op.cc, type.cc 等）
  - 精读 `ffi/tvm/src/tirx/ir/`（expr.cc, stmt.cc）和 `ffi/tvm/src/tirx/op/`（op.cc, tirx.cc）
  - 阅读 `ffi/tvm/include/tvm/ir/` 公共头文件
  - 提取事实：IRNode 体系、Expr/Stmt 继承关系、Op 注册机制、Module 容器
  - 事实写入 `bundles/apache-tvm/references/facts-ir.md`
- **Acceptance Criteria Addressed**: AC-6, AC-9
- **Test Requirements**:
  - `programmatic` TR-11.1: 事实覆盖 src/ir/ 和 src/tirx/ 全部 .cc 文件
  - `human-judgement` TR-11.2: 类继承关系准确

### [x] Task 12: apache-tvm bundle — R 阶段模块 2（Relax + TE + TOPI）

- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 精读 `ffi/tvm/src/relax/`（ir/expr.cc, ir/type.cc, op/op.cc, op/nn/nn.h, utils.cc）
  - 精读 `ffi/tvm/src/te/`（tensor.cc）
  - 精读 `ffi/tvm/src/topi/`（elemwise.cc, nn.cc, einsum.cc, vision.cc, utils.cc）
  - 提取事实：Relax 图级 IR、TE 张量表达式、TOPI 算子清单
  - 事实写入 `bundles/apache-tvm/references/facts-relax-te-topi.md`
- **Acceptance Criteria Addressed**: AC-6, AC-9
- **Test Requirements**:
  - `programmatic` TR-12.1: 事实覆盖上述全部源文件

### [x] Task 13: apache-tvm bundle — R 阶段模块 3（Runtime + Target + Arith + Support）

- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 精读 `ffi/tvm/src/runtime/`（timer.cc, vm/vm.cc）
  - 精读 `ffi/tvm/src/target/`（target.cc, tag.cc）
  - 精读 `ffi/tvm/src/arith/`（int_set.cc）
  - 精读 `ffi/tvm/src/support/`（arena.h, base64.h, env.h, limits.h, pipe.h, socket.h, ssize.h, utils.h）
  - 阅读 Python 绑定 `ffi/tvm/python/tvm/`（base.py, error.py, ir/op.py, te/tag.py）
  - 事实写入 `bundles/apache-tvm/references/facts-runtime-target.md`
- **Acceptance Criteria Addressed**: AC-6, AC-9
- **Test Requirements**:
  - `programmatic` TR-13.1: 事实覆盖上述全部文件

### [x] Task 14: apache-tvm bundle — R 阶段模块 4（TVM-FFI）

- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 精读 `ffi/tvm-ffi/src/ffi/`（dtype.cc, error.cc）
  - 阅读 `ffi/tvm-ffi/include/tvm/ffi/` 公共头文件
  - 阅读 `ffi/tvm-ffi/python/tvm_ffi/` Python 绑定（重点：base.py, error.py）
  - 阅读 `ffi/tvm-ffi/rust/` Rust crate 结构
  - 提取事实：Any/AnyView 类型擦除、Object/ObjectRef 引用计数、Function 打包调用约定、全局注册表
  - 事实写入 `bundles/apache-tvm/references/facts-tvm-ffi.md`
- **Acceptance Criteria Addressed**: AC-6, AC-9
- **Test Requirements**:
  - `programmatic` TR-14.1: 事实覆盖 tvm-ffi 的 C++/Python/Rust 三层核心 API

### [x] Task 15: apache-tvm bundle — I 阶段架构洞察

- **Priority**: high
- **Depends On**: Task 14
- **Description**:
  - 基于 4 个事实文件提炼 5 个核心洞察：
    1. 多层 IR 设计（TIR 张量级 → Relax 图级 → TE 表达式）
    2. Object/ObjectRef 智能指针体系（来自 TVM-FFI）
    3. PackedFunc 全局注册表跨语言调用机制
    4. TVM-FFI 的 C ABI 稳定性设计（Any/Object/Function 三元组）
    5. Python-first 转换流水线（Python 绑定驱动编译流程）
  - 设计知识地图：concepts/ 分 3 组（入门/核心/高级），约 15-18 个文档
  - 洞察写入 `bundles/apache-tvm/references/insights.md`
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `human-judgement` TR-15.1: 5 条洞察均含四元组，维度独立不重叠

### [x] Task 16: apache-tvm bundle — E 阶段 references + concepts 第一批

- **Priority**: high
- **Depends On**: Task 15
- **Description**:
  - 生成 references/ 信源文件（tvm-source.md, tvm-ffi-source.md）
  - 生成 concepts/ 第1批（入门组，00-06，7个文档）：00-overview, 01-install-build, 02-ir-basics, 03-object-system, 04-packed-func, 05-tensor-expressions, 06-python-bindings
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-8
- **Test Requirements**:
  - `programmatic` TR-16.1: references 先于 concepts 创建
  - `human-judgement` TR-16.2: 每篇文档 500-5000 字

### [x] Task 17: apache-tvm bundle — E 阶段 concepts 第2-4批 + examples + index

- **Priority**: high
- **Depends On**: Task 16
- **Description**:
  - 第2批（核心组，07-12）：07-tir, 08-relax, 09-topi-operators, 10-runtime-vm, 11-target-codegen, 12-tvm-ffi-any
  - 第3批（高级组，13-15）：13-tvm-ffi-object, 14-tvm-ffi-function, 15-cross-language
  - 生成 examples/（2-3个示例：简单算子编译、Relax 图构建、FFI 扩展）
  - 最后生成所有 index.md 和 log.md
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-17.1: 3批 concepts，每批≤7
  - `programmatic` TR-17.2: index 最后生成

### [x] Task 18: apache-tvm bundle — V 阶段验证

- **Priority**: high
- **Depends On**: Task 17
- **Description**:
  - 全量验证：结构、frontmatter、链接
  - Grep 验证：文档中每个 C++ 类名（如 `ObjectRef`, `PackedFunc`, `RelaxExpr`）在 ffi/tvm/include/ 或 ffi/tvm/src/ 中存在
  - Grep 验证：每个 Python import 和类名在 ffi/tvm/python/ 或 ffi/tvm-ffi/python/ 中存在
  - 代码示例检查：API 调用签名与源码一致
  - 修复所有问题
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-18.1: 零虚构 API（C++ 和 Python 分别验证）
  - `programmatic` TR-18.2: 零断裂链接
  - `human-judgement` TR-18.3: 跨语言示例（Python/C++/Rust）签名准确

### [x] Task 19: tuya-iot bundle — R 阶段模块 1（TuyaOpen 核心框架）

- **Priority**: high
- **Depends On**: Task 18
- **Description**:
  - 首先分析 `TuyaOpen/src/` 目录结构，区分核心框架/第三方库/平台适配
  - 精读核心框架子目录的 .c/.h 文件（基于目录分析结果确定范围）
  - 阅读 `TuyaOpen/CMakeLists.txt`、`tos.py`、`Kconfig` 文件理解构建系统
  - 提取事实：SDK 架构层次、构建系统（tos.py）、Kconfig 配置、核心抽象
  - 事实写入 `bundles/tuya-iot/references/facts-tuyaopen-core.md`
- **Acceptance Criteria Addressed**: AC-6, AC-9
- **Test Requirements**:
  - `programmatic` TR-19.1: 目录分析报告明确区分核心/第三方/适配
  - `human-judgement` TR-19.2: 核心模块全覆盖

### [x] Task 20: tuya-iot bundle — R 阶段模块2（TuyaOpen 技能 + 生态项目）

- **Priority**: high
- **Depends On**: Task 19
- **Description**:
  - 阅读 `TuyaOpen-dev-skills/skills/` 下全部 SKILL.md 和脚本（8个技能）
  - 阅读 `tuya-openclaw-skills/tuya-smart-control/` 的 SKILL.md、scripts/、references/
  - 阅读 `tuya-home-assistant/docs/` 和 `tuya-smart-life/docs/`（作为信源参考）
  - 提取事实：技能体系结构、AI 辅助开发工作流、Tuya Open API 能力、HA 集成架构
  - 事实写入 `bundles/tuya-iot/references/facts-skills.md` 和 `facts-ecosystem.md`
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-20.1: 8 个 TuyaOpen 技能全部有事实记录
  - `programmatic` TR-20.2: tuya-openclaw-skills 的 11 个 API 模块全覆盖

### [x] Task 21: tuya-iot bundle — I→E→V 全流程

- **Priority**: high
- **Depends On**: Task 20
- **Description**:
  - I: 洞察（跨平台 SDK 抽象层、AI 技能渐进式披露、云-端协同架构、TuyaOpen 构建系统设计）
  - E: references/ → concepts/（12-15个，分2-3批）→ examples/ → index
  - V: Grep 验证 C 函数名/Python 脚本/SKILL.md 字段
- **Acceptance Criteria Addressed**: AC-2 至 AC-8
- **Test Requirements**:
  - `programmatic` TR-21.1: C 函数名 Grep 验证
  - `programmatic` TR-21.2: 分批纪律
  - `human-judgement` TR-21.3: IoT 概念对新手友好

### [x] Task 22: home-assistant bundle — R 阶段模块1（核心架构）

- **Priority**: high
- **Depends On**: Task 21
- **Description**:
  - 精读 `home-assistant/core/homeassistant/` 根目录核心文件：__init__.py, bootstrap.py, config.py, core.py, loader.py, runner.py, setup.py, const.py, exceptions.py
  - 精读 `homeassistant/auth/` 模块
  - 提取事实：HomeAssistant 核心对象、启动流程（bootstrap）、配置加载、组件加载器（loader）、认证体系
  - 事实写入 `bundles/home-assistant/references/facts-core.md`
- **Acceptance Criteria Addressed**: AC-6, AC-9
- **Test Requirements**:
  - `programmatic` TR-22.1: 事实覆盖根目录全部 .py 文件和 auth/ 模块
  - `human-judgement` TR-22.2: 启动流程顺序准确

### [x] Task 23: home-assistant bundle — R 阶段模块2（helpers + util）

- **Priority**: high
- **Depends On**: Task 22
- **Description**:
  - 精读 `homeassistant/helpers/` 关键文件（entity.py, device_registry.py, entity_registry.py, config_validation.py, service.py, template.py 等）
  - 阅读 `homeassistant/util/` 全部文件（color.py, dt.py, json.py, ssl.py, uuid.py 等）
  - 提取事实：实体基类层次、设备/实体注册表、配置验证、服务注册、模板引擎、工具函数
  - 事实写入 `bundles/home-assistant/references/facts-helpers.md`
- **Acceptance Criteria Addressed**: AC-6, AC-9
- **Test Requirements**:
  - `programmatic` TR-23.1: 事实覆盖 helpers/ 和 util/ 核心文件

### [x] Task 24: home-assistant bundle — R 阶段模块3（components 集成模式）

- **Priority**: high
- **Depends On**: Task 23
- **Description**:
  - 分析 `homeassistant/components/` 目录结构（数千个集成）
  - 选取代表性集成精读：一个 light 平台、一个 sensor 平台、一个 switch 平台、一个复杂集成（如 tuya、mqtt）
  - 阅读 `homeassistant/components/__init__.py`（集成基类/manifest 处理）
  - 提取事实：集成 manifest.json 结构、platform 模式、config_flow、entity 生命周期、集成设置流程
  - 事实写入 `bundles/home-assistant/references/facts-components.md`
- **Acceptance Criteria Addressed**: AC-6, AC-9
- **Test Requirements**:
  - `human-judgement` TR-24.1: 准确总结集成开发共性模式
  - `programmatic` TR-24.2: 至少精读 5 个代表性集成的关键文件

### [x] Task 25: home-assistant bundle — R 阶段模块4（script 工具 + 测试模式）

- **Priority**: medium
- **Depends On**: Task 24
- **Description**:
  - 阅读 `home-assistant/core/script/` 关键工具（hassfest/、scaffold/、translations/）
  - 阅读 `homeassistant/tests/` 测试模式（conftest.py, common.py, 代表性测试文件）
  - 提取事实：hassfest 验证工具、集成脚手架、测试 fixture 模式、snapshot 测试
  - 事实写入 `bundles/home-assistant/references/facts-tooling.md`
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-25.1: 事实覆盖 hassfest 各验证器和 scaffold 生成器

### [x] Task 26: home-assistant bundle — I 阶段架构洞察

- **Priority**: high
- **Depends On**: Task 25
- **Description**:
  - 提炼 5 个核心洞察：
    1. 核心-组件-平台三层架构（core → component → platform）
    2. 异步事件驱动模型（EventBus + StateMachine + ServiceRegistry）
    3. 配置流（config_entries）与声明式 manifest
    4. Entity 抽象与设备注册表（设备-实体-服务关系）
    5. 集成质量规模化保障（hassfest + scaffold + 严格测试）
  - 设计知识地图：约 15-20 个概念文档，分入门/核心/高级/开发指南 4 组
  - 洞察写入 `bundles/home-assistant/references/insights.md`
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `human-judgement` TR-26.1: 洞察四元组完整

### [x] Task 27: home-assistant bundle — E 阶段 references + concepts 第1批

- **Priority**: high
- **Depends On**: Task 26
- **Description**:
  - 生成 references/ 信源文件
  - 第1批（入门组，00-06）：00-overview, 01-architecture, 02-installation, 03-core-object, 04-bootstrap-lifecycle, 05-configuration, 06-event-bus
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-8
- **Test Requirements**:
  - `programmatic` TR-27.1: references 先于 concepts
  - `human-judgement` TR-27.2: 入门文档对新手友好

### [x] Task 28: home-assistant bundle — E 阶段 concepts 第2批

- **Priority**: high
- **Depends On**: Task 27
- **Description**:
  - 第2批（核心组，07-13）：07-state-machine, 08-service-registry, 09-entity-model, 10-device-registry, 11-auth-system, 12-helpers, 13-utilities
- **Acceptance Criteria Addressed**: AC-3, AC-8
- **Test Requirements**:
  - `programmatic` TR-28.1: 每篇文档 frontmatter 完整

### [x] Task 29: home-assistant bundle — E 阶段 concepts 第3批 + examples + index

- **Priority**: high
- **Depends On**: Task 28
- **Description**:
  - 第3批（高级/开发组，14-18）：14-component-architecture, 15-config-flow, 16-platform-pattern, 17-hassfest-tooling, 18-testing-patterns
  - 生成 examples/（自定义集成示例、实体平台示例）
  - 最后生成所有 index.md 和 log.md
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-29.1: 全部文档生成
  - `programmatic` TR-29.2: index 完整列出所有文件

### [x] Task 30: home-assistant bundle — V 阶段验证

- **Priority**: high
- **Depends On**: Task 29
- **Description**:
  - 全量验证：结构、frontmatter、链接
  - Grep 验证：文档中每个 Python 类名/方法名在 homeassistant/ 源码中存在
  - 重点验证：Entity 基类方法、HomeAssistant 类方法、callback 签名、manifest.json 字段
  - 代码示例检查：自定义集成代码与 scaffold 模板一致
  - 修复所有问题
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-30.1: 零虚构 API
  - `programmatic` TR-30.2: 零断裂链接
  - `human-judgement` TR-30.3: 集成开发指南可操作

---

## 阶段四：跨 Bundle 收尾

### [x] Task 31: 全部 Bundle 交叉链接与一致性审查

- **Priority**: medium
- **Depends On**: Task 30
- **Description**:
  - 检查 7 个 bundle 之间的潜在关联（如 veadk-python 与 mobile-use 都涉及 LLM agent 架构；tuya-iot 与 home-assistant 有 tuya 集成关联）
  - 在相关概念文档中补充跨 bundle 引用说明
  - 统一 frontmatter 风格（generated.at 时间格式、verified.by 标识、stale_after 日期）
  - 确认所有 bundle 的根 index.md 都有 okf_version frontmatter
- **Acceptance Criteria Addressed**: AC-3, AC-5, NFR-5
- **Test Requirements**:
  - `programmatic` TR-31.1: 7 个 bundle 根 index 均含 okf_version
  - `human-judgement` TR-31.2: 跨 bundle 关联准确

### [x] Task 32: C 阶段模式沉淀

- **Priority**: medium
- **Depends On**: Task 31
- **Description**:
  - 回顾 7 个 bundle 的 R→I→E→V→C 执行过程
  - 记录遇到的问题（如 Windows 路径陷阱、大型项目分批策略、C++ 项目事实采集方法）
  - 如有新反模式或改进点，更新 source-code-to-okf-wiki 模式文档
  - 记录跨场景迁移验证（C/C++ 嵌入式项目、Python 大型框架、Markdown 技能集合等不同类型项目的适用性）
- **Acceptance Criteria Addressed**: FR-9
- **Test Requirements**:
  - `human-judgement` TR-32.1: 至少记录 3 个本次实践的经验教训
  - `human-judgement` TR-32.2: 如更新模式文档，反模式总数 ≥5
