# 源码转 OKF Wiki 实践 — C 阶段经验沉淀

> **沉淀日期**：2026-08-22
> **实践范围**：7 个开源项目源码 → OKF v0.2 知识包
> **方法论**：source-code-to-okf-wiki（R-I-E-V-C 五阶段）+ seven-concepts-cmd（方法论编排）
> **沉淀性质**：跨项目类型、跨语言栈的经验教训与反模式提炼

---

## A. 执行概况

### A.1 量化统计

| 指标 | 数值 | 说明 |
|------|------|------|
| Bundle 总数 | 7 | 覆盖 4 种项目类型 |
| 概念文档总数 | 93 篇 | 不含 index/log/report |
| 示例文档总数 | 7 篇 | 每 bundle 至少 1 篇 |
| 事实总数 | 1598+ 条 | R 阶段采集，全部指向源码路径 |
| 信源登记文件 | 25 篇 | references/ 下的源码登记 |
| V 阶段验证修复 | 61+ 处 | 含虚构 API、签名错误、路径修正等 |
| 验证报告 | 7 份 | 每 bundle 均有完整 V 阶段报告 |
| 内部链接总数 | 300+ 条 | 全部以 `/` 开头，零断链 |
| Grep API 验证 | 300+ 个 | 类名/函数名/常量在源码中验证存在 |

### A.2 各 Bundle 明细

| Bundle | 语言/类型 | 事实数 | 概念数 | 修复数 | 分批数 |
|--------|----------|--------|--------|--------|--------|
| okf-ecosystem | Python CLI + 桌面 | 311 | 6 | 10 | 1 批 |
| mobile-use | Python Agent SDK | 265 | 7 | 1 | 1 批 |
| veadk-python | Python Agent 框架 | 131 | 12 | 3 | 2 组 |
| ai-agent-skills | Markdown/技能集合 | 292 | 12 | 1 | 2 批 |
| apache-tvm | C/C++ 编译器 | 4 事实文件 | 22 | 23 | 4 批 |
| tuya-iot | C/C++ 嵌入式 IoT | 599 | 15 | 11 | 2 批 |
| home-assistant | Python 大型框架 | 4 事实文件 | 19 | 16 | 3 批 |

### A.3 使用的技能与方法论

1. **source-code-to-okf-wiki**（L1 模式）：提供 R→I→E→V→C 五阶段工作流框架，包括事实采集模板、frontmatter 模板、V 阶段检查清单、反模式库
2. **seven-concepts-cmd**：方法论编排工具，协调七概念方法论各阶段的执行顺序与产出物管理
3. **Grep/Glob 工具**：V 阶段 API 真实性验证的核心手段，所有类名/函数名/路径均经源码级验证
4. **分批委派策略**：通过独立上下文分批生成概念文档，每批 5-7 个，避免上下文溢出

---

## B. 跨项目类型适用性

### B.1 C/C++ 嵌入式项目（TuyaOpen、Apache TVM）

#### 经验教训 1：头文件优先策略

**现象**：C/C++ 项目中，`.h` 头文件比 `.c`/`.cc` 实现文件更能反映 API 设计。

**实践**：
- TuyaOpen 的 R 阶段以 `tal_*/include/tal_*.h` 头文件为主要事实来源，API 函数签名、枚举类型、宏定义全部从头文件提取
- TVM 的 FFI 层分析以 `include/tvm/ffi/` 头文件为入口，`ffi::Object`、`ffi::Function` 等核心类型的定义均在 `.h` 中
- 实现文件（`.c`/`.cc`）仅用于验证函数存在性和理解内部数据流，不作为 API 声明的权威来源

**原理**：C/C++ 的头文件是接口契约，实现文件可能包含静态函数、内部宏等不应暴露的细节。从头文件提取事实天然过滤了内部实现。

**适用边界**：此策略对有清晰 public/private 分离的项目有效；对于 header-only 库（如部分 C++ 模板库），头文件即全部源码，策略仍适用但需注意模板实现细节。

#### 经验教训 2：构建系统是架构理解的入口

**现象**：嵌入式项目的 Kconfig/CMake 构建系统不仅是编译配置，更是模块依赖关系和能力裁剪的架构文档。

**实践**：
- TuyaOpen 的 `Kconfig` 文件揭示了 19 个 TAL 模块的依赖关系和可选组件
- `CMakeLists.txt` 的组件自动发现机制（`components/*`）反映了插件式架构
- `tos.py` 构建工具的子命令（new/build/flash/monitor/config）定义了开发者工作流
- TVM 的 CMake 构建配置揭示了可选后端（LLVM/CUDA/Metal/Vulkan）和编译选项

**建议**：R 阶段应将构建系统文件（Kconfig/CMakeLists.txt/Makefile）作为核心模块阅读，而非仅关注源码。

#### 经验教训 3：大型 C++ 项目的分批模块策略

**现象**：Apache TVM 是本次最大的 C++ 项目（22 篇概念文档），单次 R 阶段无法覆盖全部模块。

**实践**：
- 按架构分层将 TVM 拆分为 4 个事实文件：
  1. `facts-tvm-ffi.md`：FFI 跨语言基座
  2. `facts-ir-tir.md`：IR 核心与 TIRx
  3. `facts-relax-te-topi.md`：Relax/TE/TOPI（244 条事实，最大的一批）
  4. `facts-runtime-target-arith.md`：Runtime/Target/Arith
- 概念文档分 4 批生成，每批对应一个架构层次
- 每批生成前重新确认该层的事实清单和洞察

**教训**：大型 C++ 项目必须按架构边界拆分，不能按文件数量机械分批。分层分批使每批内部概念内聚，跨批概念有清晰的依赖方向。

#### 经验教训 4：C++ API 虚构风险最高

**现象**：TVM 是本次发现虚构 API 最多的项目（8 类虚构/过时 API），包括 `PackedFunc`、`TVMArgs`、`TVM_REGISTER_GLOBAL` 等。

**根因**：
1. TVM 正在从旧版运行时 API（PackedFunc/TVMArgs）迁移到新版 TVM-FFI API（`ffi::Function`/`ffi::PackedArgs`/`refl::GlobalDef()`）
2. AI 训练数据中旧版 API 的文档和示例远多于新版，导致"统计惯性"虚构
3. C++ 宏和模板使 API 真实形式难以从表面推断

**对策**：V 阶段对 C++ 项目必须执行最严格的 Grep 验证，包括：
- 每个类名在 `include/` 中 Grep
- 每个宏在源码中 Grep 定义
- 命名空间前缀完整验证（`ffi::` vs 无命名空间）
- 注意版本迁移导致的 API 废弃

---

### B.2 Python 大型框架（Home Assistant）

#### 经验教训 5：9647 文件的分批策略

**现象**：Home Assistant Core 是本次最大的 Python 项目（9647 个文件），全量阅读不可能。

**实践**：
- 按架构层次分 4 个事实文件：
  1. `facts-core.md`：核心运行时（core.py、bootstrap、config、auth）
  2. `facts-components.md`：集成架构（manifest、config_entries、平台基类）
  3. `facts-helpers.md`：辅助工具库（entity、device_registry、storage、debounce）
  4. `facts-tooling.md`：测试与工具链（hassfest、pytest fixtures、syrupy）
- 概念文档分 3 批生成：基础组（00-06）、核心组（07-13）、高级/开发组（14-18）
- 每批聚焦架构的一个层次，不跨层

**核心原则**：大型框架的分批依据是**架构分层**而非**文件数量**。核心→helpers→components→tooling 的阅读顺序也是新开发者的学习路径。

#### 经验教训 6：插件式架构的集成模式提取

**现象**：HA 有 2000+ 集成（integration），无法逐一分析，但所有集成遵循相同的模式。

**实践**：
- 不分析具体集成实现，而是提取集成开发的**通用模式**：
  - `manifest.json` 声明元数据
  - `async_setup`/`async_setup_entry` 生命周期
  - ConfigFlow 状态机
  - 平台实体基类（LightEntity/SensorEntity/SwitchEntity）
  - `EntityDescription` 声明式配置
- 通过阅读 `components/light/__init__.py`、`components/sensor/__init__.py` 等平台基类提取模式
- hassfest 验证器（29 个）是理解集成规范的最佳入口——它们编码了"什么是合规集成"

**迁移**：此策略适用于所有插件式架构（VS Code 扩展、WordPress 插件、ESLint 规则等）：不分析插件，分析插件 API 和验证规则。

#### 经验教训 7：测试基础设施作为架构理解入口

**现象**：HA 的 `tests/` 目录和 pytest fixtures 揭示了架构的"使用方式"。

**实践**：
- `MockConfigEntry`、`enable_custom_integrations` fixture 展示了集成如何被测试
- `snapshot` fixture（syrupy）展示了状态序列化模式
- 测试中的禁网策略揭示了 HA 的云依赖边界
- 测试文件的组织方式镜像了源码结构

**建议**：R 阶段应阅读测试基础设施（conftest.py、common.py），测试代码是"可执行的架构文档"。

---

### B.3 Markdown/技能集合项目（ai-agent-skills）

#### 经验教训 8：SKILL.md frontmatter 标准化

**现象**：ai-agent-skills bundle 的分析对象是 6 个开源技能项目，主要"源码"是 Markdown 文件（SKILL.md、README.md）和配置文件（plugin.json、divisions.json）。

**实践**：
- R 阶段的事实采集对象从"类/函数"转变为"frontmatter 字段、配置结构、脚本路径"
- SKILL.md 的 frontmatter（name/description/allowed-tools等）是技能的"API 声明"
- `plugin.json` 的 hooks/commands/checkpoints 是插件的"接口契约"
- PEP 723 shebang（`#!/usr/bin/env -S uv run --script`）是脚本依赖声明的关键事实
- 验证方法从"Grep 类定义"转变为"Glob 文件路径 + JSON 字段校验"

**教训**：无传统源码的项目仍可执行 R-I-E-V-C 流程，只需将"事实"的定义从代码符号扩展到结构化文档字段。

#### 经验教训 9：多子项目事实聚合策略

**现象**：ai-agent-skills 涵盖 6 个独立子项目，需要统一的知识结构。

**实践**：
- 为每个子项目创建独立的事实文件（`facts-agency-agents.md`、`facts-awesun-mcp.md` 等）
- 概念文档不按子项目组织，而按**跨项目模式**组织：
  - SKILL.md 标准（跨项目）
  - MCP 协议（awesun-mcp + awesun-skill）
  - 插件架构（agency-agents + jira-skill + retro-skill）
  - 脚本工具模式（jira-skill + retro-skill + awesun-ui-locator）
- I 阶段的洞察聚焦"共同模式"而非单个项目

**迁移**：适用于 monorepo、多包项目、技术生态调研等场景。

---

### B.4 Python 库/SDK 项目（mobile-use、veadk-python、okf-kit）

#### 经验教训 10：类继承层次分析

**现象**：Python 框架的核心架构往往体现在类继承层次中。

**实践**：
- veadk-python：`LlmAgent`（Google ADK）→ `Agent`（veadk 扩展），理解继承链是理解框架扩展点的关键
- mobile-use：`MobileDeviceController`（Protocol）→ `AndroidDeviceController`/`iOSDeviceController` → `UnifiedMobileController`（门面），Protocol + Factory + Facade 三层模式
- okf-kit：`Fetcher`（ABC）→ `HttpFetcher`/`BrowserFetcher`，抽象基类定义爬取接口

**建议**：R 阶段应优先绘制核心类的继承/实现关系图，这比逐函数阅读更高效。

#### 经验教训 11：API 签名验证的粒度

**现象**：Python 的动态类型使 API 签名错误更隐蔽（参数名错误在运行时才暴露）。

**实践**：
- mobile-use：V 阶段将 14 个 CLI 参数与 Typer 定义逐项比对，发现工具数量描述不准确
- veadk-python：V 阶段验证了 25+ 核心类和方法的签名，发现 3 个问题（事实编号错误、CLI 命令名错误、源文件名缺失）
- okf-kit：27 项 API 在源码中验证，发现 CLI 子命令数量错误（9 个 vs 实际 10 个）

**教训**：Python 项目的 V 阶段不能只验证类名/函数名存在，还必须验证：
- 方法签名（参数名、默认值、类型注解）
- CLI 命令名和选项名
- 枚举值和常量值
- 导入路径

---

## C. 遇到的问题与解决方案

### C.1 Windows 路径陷阱

**问题**：Windows 使用反斜杠（`\`）作为路径分隔符，而 OKF 规范、Markdown 链接、Python 源码中统一使用正斜杠（`/`）。

**表现**：
- Grep 搜索路径时 `\` 需要转义
- 文件路径在文档中需要统一为 `/` 格式
- PowerShell 的路径处理与 bash 不同
- 绝对路径 `d:\AI\...` 在文档中应转为 bundle-relative `/references/...`

**解决方案**：
1. 文档中的交叉链接统一使用 `/` 开头的 bundle-relative 路径
2. 源码路径引用使用正斜杠（`src/tal_system/include/tal_thread.h`）
3. Shell 命令中使用 PowerShell 兼容语法
4. verification-report 中的路径记录使用原始 Windows 路径以便定位，但文档内容中使用规范路径

**预防**：在 E 阶段的 prompt 中明确要求"所有路径使用正斜杠"。

---

### C.2 大型项目上下文溢出与分批策略

**问题**：大型项目（TVM 22 篇概念、HA 19 篇、Tuya 15 篇）在单次对话中生成全部文档会导致上下文溢出，后期文档遗忘前期约定。

**表现**：
- 后生成的文档 frontmatter 格式与前面不一致
- 事实编号引用混乱
- 交叉链接遗漏
- 代码风格漂移

**解决方案**：
1. **按架构层分批**：每批 5-7 个文档，聚焦一个内聚的架构层次
2. **信源先行**：每批生成前确认 references/ 信源文件已存在
3. **Index 最后写**：所有内容文档完成后再统一生成各级 index.md
4. **每批独立验证**：每批生成后立即做轻量检查（frontmatter、链接），不积累到最后
5. **事实清单分段**：为每个架构层创建独立的事实文件，而非一个巨大的 facts.md

**量化**：TVM 分 4 批（5+6+6+5），HA 分 3 批（7+7+5），Tuya 分 2 批（7+8），均无上下文溢出问题。

---

### C.3 C++ API 虚构风险与 Grep 验证机制

**问题**：AI 在生成 C++ 项目文档时，倾向于使用训练数据中更常见的旧版 API，而非源码中的新版 API。

**表现**（TVM 案例）：
- 虚构 `TVM_FFI_REGISTER_GLOBAL` 宏（实际为 `refl::GlobalDef().def(...)`）
- 使用旧版 `PackedFunc` 类型（实际已迁移到 `ffi::Function`）
- 使用旧版 `TVMArgs`/`TVMRetValue`（实际为 `ffi::PackedArgs`/`ffi::Any`）
- 使用 `@tvm.script.tir` 装饰器（实际已改为 `@tvm.script.tirx.prim_func`）

**根因**：
1. TVM 正在进行 API 迁移，旧版文档在互联网上仍占多数
2. C++ 宏和命名空间变更难以从"代码模式"推断
3. AI 的"统计惯性"使其倾向于输出训练数据中高频出现的形式

**解决方案**：
1. V 阶段对每个类名、宏名、函数名执行 Grep 源码验证
2. 特别注意命名空间前缀（`ffi::`、`refl::`）
3. 检查头文件中的实际定义，不依赖文档或注释
4. 对于正在迁移的项目，以最新头文件为权威来源
5. 发现一个虚构 API 后，对同类 API 执行全面检查（而非仅修复发现的那个）

**结果**：TVM 共发现并修复 8 类虚构 API，涉及 10 个文件，全部通过 Grep 验证。

---

### C.4 PowerShell vs Unix 命令差异

**问题**：执行环境为 Windows PowerShell，部分 Unix 命令不可用或行为不同。

**表现**：
- `find`/`grep`/`cat`/`head`/`tail` 等命令在 PowerShell 中不存在或别名不同
- 路径中的盘符（`d:`）需要特殊处理
- 环境变量语法不同（`$env:VAR` vs `$VAR`）
- 中文编码问题（GBK vs UTF-8）

**解决方案**：
1. 使用 TRAE 提供的专用工具（Grep/Glob/Read/LS）替代 shell 命令
2. 文件操作用 Write/Edit 工具而非 shell 重定向
3. 中文提交信息使用 UTF-8 临时文件 + `git commit -F`（参考 okf-spec 复盘经验）
4. Shell 命令仅用于 Python 脚本执行和 git 操作

---

### C.5 文档型项目（无源码）的处理方式

**问题**：ai-agent-skills bundle 的分析对象主要是 Markdown 文档和 JSON 配置，没有传统意义上的"源码"。

**表现**：
- 无法 Grep 类定义或函数签名
- 事实采集对象不明确
- "API 验证"概念不适用

**解决方案**：
1. 将 SKILL.md 的 frontmatter 字段视为"API 声明"
2. 将 `plugin.json`/`divisions.json`/`tools.json` 视为"接口契约"
3. 验证方法从"Grep 代码"转变为：
   - Glob 验证文件路径存在
   - Read 验证 JSON 字段值
   - Grep 验证脚本函数名（Python/Shell 脚本仍有代码）
4. 事实采集模板从"类/方法/参数"调整为"字段/结构/路径/约定"

**结果**：ai-agent-skills 采集了 292 条事实，验证了 60+ 个名称和 30+ 个路径，零虚构。

---

### C.6 V 阶段验证结果未回写 Frontmatter

**问题**：7 个 bundle 中有 6 个完成了 V 阶段验证并产出了验证报告，但 concepts/*.md 的 `verified.by` 仍为 `pending`、`status` 仍为 `draft`。

**根因**：
1. V 阶段流程中，验证员专注于发现和修复内容问题，忽略了元数据回写
2. source-code-to-okf-wiki 模式的 V 阶段检查清单未明确要求"验证完成后批量更新 frontmatter"
3. 验证报告作为独立文档产出，与内容文档的 frontmatter 更新脱节

**解决方案**：
1. 在 V 阶段检查清单中增加"验证通过后批量回写 frontmatter"步骤
2. 回写内容包括：`verified.by`（验证员标识）、`verified.at`（验证日期）、`status: verified`
3. 根 index.md 同步补充完整 frontmatter
4. home-assistant 是唯一正确执行回写的 bundle，可作为参考模板

---

## D. 反模式提炼

### 反模式 1：从事实文件直接生成概念而不经过 I 阶段洞察

**表现**：跳过 I 阶段（架构洞察与知识结构设计），直接按 facts.md 的文件顺序逐模块生成概念文档。

**后果**：
- 概念文档排列顺序是"源码目录顺序"而非"学习路径顺序"
- 缺乏跨模块的架构洞察，文档变成"API 罗列"
- 概念之间的依赖关系不清晰
- 读者无法建立整体架构认知

**正确做法**：R 阶段后必须有 I 阶段，从事实中提炼 3-5 个核心洞察，设计知识地图（分组、依赖、学习路径），再按知识地图生成概念。

**本次实践**：所有 7 个 bundle 均执行了 I 阶段，产出了 insights.md，概念文档按学习路径而非源码目录组织。

---

### 反模式 2：跳过 V 阶段 Grep 验证

**表现**：文档生成后仅检查 frontmatter 和链接，不验证 API 真实性。

**后果**：
- 虚构 API 混入文档（TVM 的 PackedFunc 案例、HA 的虚构 bus_fire() 方法）
- 读者照抄代码报错
- 文档可信度受损

**正确做法**：V 阶段必须用 Grep 在源码中验证每个关键类名、方法名、宏名、常量值。对于 C++ 项目，验证粒度需细到命名空间和宏定义。

**本次实践**：7 个 bundle 全部执行了 Grep 验证，累计发现并修复 61+ 处问题，验证了 300+ 个 API。

---

### 反模式 3：单批生成过多文档导致质量下降

**表现**：在一个 prompt 中要求生成 10+ 个文档。

**后果**：
- 后期文档遗忘前期的格式约定
- frontmatter 字段不一致
- 事实编号引用错误
- 交叉链接遗漏
- 代码示例质量下降

**正确做法**：分批生成，每批 5-7 个文件，每批聚焦一个内聚的架构层次。TVM 的 4 批策略（5+6+6+5）是成功实践。

---

### 反模式 4：跨语言项目未分别验证 API

**表现**：对包含多种语言的项目（如 TVM 的 C++ 核心 + Python 前端 + Rust FFI），使用统一的验证策略。

**后果**：
- C++ 的虚构宏未被发现
- Python 的导入路径错误被忽略
- 语言间绑定关系（如 TVMScript 装饰器到 C++ 实现的映射）未验证

**正确做法**：
- C++ 部分：Grep 头文件验证类名/宏/命名空间
- Python 部分：Grep `__init__.py` 验证导出符号、验证导入路径
- 绑定层：验证 Python API 到 C++ 实现的映射关系

**本次实践**：TVM 验证时分别检查了 C++ 头文件（`include/tvm/`）、Python 导出（`python/tvm/`）和 FFI 绑定（`tvm-ffi/`），发现了 `@tvm.script.tir` → `@tvm.script.tirx.prim_func` 等跨语言 API 变更。

---

### 反模式 5：信源后置

**表现**：先写概念文档，最后才补 references/ 信源文件。

**后果**：
- 概念文档的 sources 字段指向不存在的文件
- 交叉引用断裂
- 后续修复成本高

**正确做法**：E 阶段第一步生成 references/ 信源登记，其他文档的 sources 字段统一指向已存在的信源文件。

**本次实践**：7 个 bundle 均遵循了信源先行原则。

---

### 反模式 6：V 阶段只出报告不回写状态

**表现**：V 阶段产出了详细的验证报告，修复了内容问题，但不更新内容文档的 `verified` 和 `status` 字段。

**后果**：
- 文档元数据与实际验证状态矛盾
- 消费者无法从 frontmatter 判断文档是否经过验证
- bundle 看起来像"草稿"，实际已验证通过

**正确做法**：V 阶段最后一步是批量回写所有内容文档的 frontmatter：`verified.by`、`verified.at`、`status: verified`。

**本次实践**：仅 home-assistant 正确执行了回写，其他 6 个 bundle 存在此问题（见 CROSS_BUNDLE_REVIEW.md P2-1）。

---

### 反模式 7：根 index.md frontmatter 不完整

**表现**：根 index.md 仅有 `okf_version` 字段，缺少 title/description/tags/generated/stale_after。

**后果**：
- OKF 消费端无法正确展示 bundle 元信息
- 知识包缺乏可搜索的标签和描述
- 无法判断生成时间和过期时间

**正确做法**：根 index.md 应包含完整 frontmatter（参照 home-assistant 模板）：`okf_version`、`type: Index`、`title`、`description`、`tags`、`generated`、`stale_after`。

---

## E. 改进建议

### E.1 对 source-code-to-okf-wiki 技能的改进建议

| 编号 | 改进项 | 优先级 | 具体建议 |
|------|--------|:------:|---------|
| IMP-1 | V 阶段增加 frontmatter 回写步骤 | P1 | 在 V 阶段检查清单末尾增加："验证通过后，批量更新所有内容文档的 verified.by、verified.at、status 字段"，并提供回写脚本/prompt 模板 |
| IMP-2 | 根 index.md frontmatter 模板 | P1 | 在 E 阶段模板中明确根 index.md 的完整 frontmatter 要求（7 个字段），而非仅 okf_version |
| IMP-3 | C/C++ 项目验证清单 | P2 | 增加 C/C++ 专项验证项：命名空间前缀验证、宏定义 Grep、头文件 vs 实现文件区分、版本迁移 API 检查 |
| IMP-4 | 文档型项目适配 | P2 | 增加"无传统源码项目"的 R 阶段指南：frontmatter 字段采集、JSON 配置验证、Glob 路径校验 |
| IMP-5 | verification-report 位置规范 | P3 | 明确验证报告应放在 bundle 根目录（与 log.md 同级），统一 type 为 VerificationReport |
| IMP-6 | 子目录 index 无 frontmatter 规则 | P2 | 在检查清单中明确：concepts/index.md、references/index.md、examples/index.md 不应有 frontmatter（apache-tvm 违规） |
| IMP-7 | verified.at 格式规范 | P3 | 明确 verified.at 使用 ISO 8601 格式（与 generated.at 一致），不使用"YYYY-MM-DD"简写 |
| IMP-8 | 多子项目聚合指南 | P3 | 增加"多子项目/monorepo"场景的 I 阶段指南：按跨项目模式而非子项目组织概念 |

### E.2 对 seven-concepts-cmd 编排的改进建议

| 编号 | 改进项 | 优先级 | 具体建议 |
|------|--------|:------:|---------|
| IMP-9 | V→C 阶段过渡门控 | P1 | 增加自动化检查：C 阶段开始前，验证所有内容文档的 status 非 draft，否则阻断并提示回写 |
| IMP-10 | 跨 bundle 一致性审查 | P2 | C 阶段增加可选的跨 bundle 审查步骤（如本次任务），当多个 bundle 同期生成时自动触发 |
| IMP-11 | 分批生成进度追踪 | P2 | 为 E 阶段分批生成增加进度追踪机制，记录每批的文件清单和验证状态，避免遗漏 |
| IMP-12 | 事实编号格式统一 | P3 | R 阶段事实采集模板中明确编号格式（F-XXX，三位数字），并在 V 阶段检查事实文件与概念文档引用的编号一致性 |

---

## F. 模式成熟度更新

基于本次 7 个项目的实践，source-code-to-okf-wiki 模式的验证次数从 1 次增加到 8 次（含 PyInvoke 初始验证 + 7 个 bundle），建议成熟度从 L1 升级为 **L2（已充分验证）**。

| 维度 | L1（初始） | L2（本次后） |
|------|-----------|-------------|
| 验证次数 | 1 | 8 |
| 覆盖语言 | Python | Python、C/C++、Markdown/JSON |
| 覆盖项目规模 | 小型（15 模块） | 小型到大型（9647 文件） |
| 验证项目类型 | Python 库 | CLI、SDK、框架、嵌入式、编译器、文档集 |
| 反模式数量 | 7 | 7（新增 2 个：V阶段不回写、根index不完整） |
| 跨场景迁移验证 | 理论迁移 | 4 种项目类型实际迁移验证 |

---

> **沉淀结论**：source-code-to-okf-wiki 五阶段工作流在 7 个不同类型、不同语言、不同规模的项目中均成功落地，证明了"先建事实基础→再提炼架构洞察→信源先行分批生成→Grep 级事实验证→模式萃取沉淀"链路的通用性。主要改进方向集中在 V 阶段的元数据回写自动化和 C/C++ 项目的专项验证策略。
