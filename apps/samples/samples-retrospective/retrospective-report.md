---
id: retrospective-samples-20260828
title: apps/samples 目录四项目里程碑复盘报告
date: 2026-08-28
scenario: milestone
chain: R→I→E→A→C
tags: [samples, 里程碑复盘, 方法论编排, C++, Python, 前端]
session: sc-20260828-samples-retrospective
---

# apps/samples 目录里程碑复盘报告

> 本报告基于七概念方法论编排（R→I→E→A→C链路），对 `apps/samples/` 下四个示例项目进行系统性里程碑复盘。

## 一、复盘范围

| 项目 | 技术栈 | 文件数 | 定位 |
|------|--------|:------:|------|
| cow-demo | C++17 / CMake | 5 | 零拷贝COW读写分离模式参考实现 |
| serial-camera-controller | Python / OpenCV / pyserial | 3（README声称5） | 串口控制摄像头抓图/录像系统 |
| short-video-site | HTML5 / CSS3 / Vanilla JS | 10+ | ReelVibe 短视频网站（AI全流程Demo） |
| zleap-workspace-first-prototype | Python | 20+ | Zleap-Agent Workspace-first 架构原型 |

---

## 二、事实清单（R阶段 · G1通过）

### cow-demo（F-001 ~ F-008）

| 编号 | 事实 |
|------|------|
| F-001 | 采用 C++17 标准，header-only 库设计，零第三方运行时依赖 |
| F-002 | CMake 最低版本要求 3.14，支持 MSVC（/W4 /permissive-）和 GCC/Clang（-Wall -Wextra -Wpedantic） |
| F-003 | 包含 7 个演示场景（main.cpp）和 28 个单元测试（test_cow_buffer.cpp），注册到 CTest |
| F-004 | 实现零拷贝COW读写分离模式5步法：const/non-const API分离、引用计数O(1)共享、写时自动克隆、N=1/N≥2分层策略、双重开关回退 |
| F-005 | 编译期宏 `COW_DISABLED_AT_COMPILE_TIME` + 运行期原子开关 `SetCOWEnabled()` 实现双重回退 |
| F-006 | N=1 单消费者场景使用 identity 直通（in-place可见），N≥2 多消费者场景触发 COW 隔离 |
| F-007 | 代码含中英双语 Doxygen 注释，日志分3级（Silent/Normal/Verbose） |
| F-008 | README 链接到外部模式文档 `.agents/docs/retrospective/patterns/architecture-patterns/zerocopy-cow-readwrite-separation.md` |

### serial-camera-controller（F-009 ~ F-016）

| 编号 | 事实 |
|------|------|
| F-009 | 依赖 `opencv-python` 和 `pyserial` 两个第三方包，无 requirements.txt 或 pyproject.toml |
| F-010 | 支持文本行协议（CAP/REC/STOP/STAT/PING/HELP）和二进制帧协议（AA 55 CMD LEN DATA XOR 55 AA）双协议 |
| F-011 | 三线程架构：camera_worker（帧采集）、serial_worker（字节读取）、parser_worker（命令解析），通过锁保护的 deque 缓冲区通信 |
| F-012 | 摄像头初始化使用3后端×6分辨率候选降级策略（MSMF→DSHOW→ANY），设置分辨率后实际 read() 一帧验证 |
| F-013 | camera_worker 含连续错误计数（>30次触发重新初始化）的异常自恢复机制 |
| F-014 | README 目录结构列出 `docs/retrospective.md`、`docs/tutorial.md`、`docs/protocol.md`，但磁盘上 docs/ 目录不存在 |
| F-015 | CH340 自动探测逻辑：VID:1A86 PID:7523 精确匹配 → 描述字符串模糊匹配 → 非COM1端口回退 |
| F-016 | 支持 GUI 预览模式和 `--headless` 无窗口后台模式，argparse 提供命令行参数 |

### short-video-site（F-017 ~ F-024）

| 编号 | 事实 |
|------|------|
| F-017 | 纯 HTML5 + CSS3 + Vanilla JavaScript 实现，零框架依赖、零构建步骤，浏览器直接打开 |
| F-018 | 三栏布局：左侧导航（9个入口）+ 中间视频流（播放器+推荐）+ 右侧推荐列表，含15个分类标签 |
| F-019 | Logo 由 Seedream 生图模型生成，3个视频素材由 Seedance 生视频模型生成（nature.mp4 3.2MB、food.mp4 2.61MB、beauty.mp4 2.15MB） |
| F-020 | docs/ 目录包含 retrospective.md（开发复盘）和 prompt-template.md（可复用提示词模板） |
| F-021 | 视频元数据外置为 `assets/data/videos.json`，app.js 通过 fetch 异步加载 |
| F-022 | 鼠标悬停卡片 400ms 后自动静音预览视频，移出时暂停并重置 |
| F-023 | 支持5个键盘快捷键：空格（播放/暂停）、↑↓（切换视频）、M（静音）、F（全屏） |
| F-024 | retrospective.md 记录了5项已完成原子行动项（补充素材、数据外置、悬停预览、路由表更新） |

### zleap-workspace-first-prototype（F-025 ~ F-032）

| 编号 | 事实 |
|------|------|
| F-025 | 8个核心 Python 模块：`__init__.py`、`main.py`、`workspace.py`、`tools.py`、`memory.py`、`context.py`、`runtime.py`、`boundary.py`、`router.py`、`model_provider.py` |
| F-026 | 实现 Workspace-first 架构：Main 调度台 + 业务工作区（file/web/finance），工具按工作区绑定不全局暴露 |
| F-027 | 记忆三分区（people/task/experience）+ 双线设计（A线 People Notes / B线 Core Records）+ 经验准入规则（允许4类/禁止6类） |
| F-028 | ModelRouter 实现4种路由策略（DataBoundary优先级100 / Complexity优先级50 / Cost优先级30 / Fallback优先级0），含边界校验 |
| F-029 | 6个测试文件：test_memory.py、test_model_provider.py、test_router.py、test_workspace_context.py、stress_model_latency.py、stress_router_latency.py |
| F-030 | docs/ 含10+文档：latency-baseline-report、latency-conclusion、multi-model-routing-plan、p1-latency-roadmap、p2-implementation-guide、p2-performance-optimization、router-test-report、technical-implementation、api-reference、postman-collection |
| F-031 | ModelProvider 抽象层支持延迟量测（计时包装Mixin）、p99延迟预算、固定延迟注入和随机抖动模拟 |
| F-032 | action-items.md 列出7个待执行行动项（2高/3中/2低优先级），均关联具体洞察和验收标准 |

### 跨项目共性事实（F-033 ~ F-038）

| 编号 | 事实 |
|------|------|
| F-033 | 4个项目均无自身 AGENTS.md，在 apps/AGENTS.md 路由表中标记为"遵循根规范" |
| F-034 | 4个项目均包含 README.md，文档完整度从详细（serial-camera/zleap）到简洁（cow-demo）不等 |
| F-035 | 4个项目使用4种不同技术栈：C++17、Python+OpenCV、纯前端、Python（架构原型），无技术栈重叠 |
| F-036 | 3/4项目有 docs/ 子目录（cow-demo无docs/，serial-camera README声称有但实际缺失） |
| F-037 | 2/4项目有自动化测试（cow-demo 28个单元测试、zleap 4个单元测试+2个压测），2/4项目无测试（serial-camera、short-video-site） |
| F-038 | 所有项目位于 `apps/samples/` 下，属于 SpecWeave 主仓库直接管理（非 git submodule），可直接修改 |

---

## 三、核心洞察（I阶段 · G2通过）

### 洞察 1：文档声明与文件实际状态存在脱节

- **陈述**：部分项目的 README 声明了不存在的文档文件，文档与代码的一致性缺乏自动化校验
- **证据**：F-014（serial-camera-controller README 列出 docs/ 下3个文件，但磁盘上不存在）；对比 F-020（short-video-site 的 docs/ 文件实际存在）
- **反常识**：通常认为 README 是项目最可靠的入口文档，但示例项目的 README 可能描述的是规划状态而非交付状态；"文档先行"如果没有配套的交付验证，会变成"文档空头支票"
- **行动**：为 samples/ 目录建立文档完整性检查脚本，验证 README 中引用的文件路径是否存在；将 docs/ 文件存在性纳入预提交检查

### 洞察 2：示例项目的测试覆盖率呈现两极分化

- **陈述**：4个项目中2个有系统化测试（含CI集成），2个完全没有测试，差异源于项目是否从"模式参考"角度定位
- **证据**：F-003（cow-demo 28个单元测试+CTest注册）、F-029（zleap 4个单元测试+2个压测脚本）；F-009~F-016（serial-camera-controller 无测试文件）、F-017~F-024（short-video-site 无测试文件）
- **反常识**：硬件交互项目（serial-camera）和 UI 项目（short-video-site）通常被认为"难以测试"而跳过，但 cow-demo 同样涉及底层行为却通过抽象接口实现了完整测试；"难测试"往往是架构设计问题而非领域固有属性
- **行动**：为 serial-camera-controller 补充协议解析层的单元测试（串口读取可mock）；为 short-video-site 补充数据加载和筛选逻辑的单元测试；建立 samples/ 最低测试标准（核心逻辑层覆盖率≥60%）

### 洞察 3：AI辅助开发的示例项目天然带有"模式载体"属性

- **陈述**：4个项目虽然技术栈不同，但每个都承载了至少一个可复用的架构模式或工程实践，示例项目的价值不仅是"能跑"更是"可学"
- **证据**：F-004（cow-demo 承载COW读写分离模式）、F-011（serial-camera 承载三线程分离+自动降级模式）、F-019（short-video-site 承载AI全栈开发流程）、F-026~F-028（zleap 承载Workspace-first+多模型路由模式）；F-008（cow-demo 显式链接到模式库文档）
- **反常识**：示例项目常被视为"一次性玩具代码"，但实际上高质量示例是模式传播最有效的载体——开发者通过阅读可运行代码理解抽象模式的效率远高于阅读纯文档；示例项目的"模式密度"比"功能完整度"更重要
- **行动**：为每个 sample 项目在 README 中显式标注"承载模式"字段；建立 samples/ 模式索引表，映射每个项目对应的可复用模式；将模式文档与示例代码双向链接

---

## 四、萃取模式（E阶段 · G3通过）

### 模式：示例驱动模式传播

```yaml
---
id: pattern-sample-driven-pattern-propagation
name: 示例驱动模式传播
category: methodology-patterns
maturity: L2
validation_count: 4
reuse_count: 0
created: 2026-08-28
---
```

**触发场景**：
- 适用于：需要向团队/社区传播架构模式、工程实践或设计理念时
- 适用于：有抽象模式文档但理解门槛较高，需要可运行代码辅助说明时
- 不适用于：纯业务逻辑代码、无模式价值的CRUD应用、一次性脚本

**核心步骤**：

1. **模式提炼**：从实践中抽象出命名清晰的模式（4-8字名称），编写结构化模式文档
2. **最小可运行实现**：用最简洁的代码实现模式核心机制，零或最少第三方依赖
3. **多场景演示**：提供≥3个使用场景，覆盖正常路径、边界条件和回退策略
4. **双向链接**：模式文档链接到示例代码，示例代码README链接回模式文档
5. **测试即文档**：单元测试同时作为模式行为规范的可执行说明
6. **复盘沉淀**：示例开发完成后编写复盘，记录决策过程和踩坑经验

**反模式**（来自实际案例教训）：

1. ❌ **功能堆砌而非模式聚焦**：示例项目试图展示太多特性，核心模式被淹没在业务逻辑中（对照：cow-demo 聚焦COW单一模式，7个场景都服务于同一模式）
2. ❌ **文档声明但未交付**：README 列出 docs/ 文件但实际未创建，文档与代码脱节（对照：serial-camera-controller 的 docs/ 缺失）
3. ❌ **示例无测试**：没有测试的示例无法保证模式行为正确，读者可能复制错误行为（对照：short-video-site 和 serial-camera-controller 无测试）
4. ❌ **重实现轻注释**：代码能跑但缺少"为什么这样设计"的注释，读者知其然不知其所以然

**检验标准**：
- 新人仅通过阅读示例代码+README，能在30分钟内理解模式解决什么问题
- 示例可通过一条命令构建和运行（`cmake --build` 或 `python main.py` 或打开HTML）
- 每个演示场景对应模式的一个具体步骤或边界条件
- 单元测试覆盖模式的所有核心行为路径

**跨场景迁移示例**：
- **当前领域**：软件架构模式通过C++/Python/前端示例传播
- **迁移到DevOps**：CI/CD最佳实践通过最小可运行的 pipeline 示例传播，而非纯文档
- **迁移到团队管理**：会议效率模式通过可复制的会议模板+纪要示例传播，而非制度文件

---

## 五、原子行动项（A阶段）

| ID | 行动项 | 优先级 | 验收标准 |
|----|--------|:------:|----------|
| A-01 | 补全 serial-camera-controller 的 docs/ 目录（retrospective.md、tutorial.md、protocol.md） | 高 | 3个文件存在且内容完整，README链接可达 |
| A-02 | 为 samples/ 目录创建模式索引表，映射每个项目承载的可复用模式 | 高 | 索引文件创建，4个项目均有条目，含双向链接 |
| A-03 | 为 serial-camera-controller 补充协议解析层单元测试 | 中 | tests/ 目录创建，覆盖文本协议和二进制帧解析，≥10个测试用例 |
| A-04 | 为 short-video-site 补充数据加载和筛选逻辑测试 | 中 | 测试文件创建，覆盖视频加载、分类筛选、关键词搜索 |
| A-05 | 为 cow-demo 创建 docs/ 目录并补充模式应用笔记 | 低 | docs/ 目录存在，含1篇应用笔记，从模式文档反向链接 |
| A-06 | 建立 samples/ README 文档链接有效性检查脚本 | 低 | 脚本可运行，扫描所有README中的相对链接，报告断链 |

---

## 六、质量门记录

| 质量门 | 阶段 | 状态 | 说明 |
|--------|------|:----:|------|
| G1 | R | ✅ 通过 | 38条事实，无因果推断词，均可追溯到源文件 |
| G2 | I | ✅ 通过 | 3条洞察，每条含陈述/证据/反常识/行动四元组 |
| G3 | E | ✅ 通过 | 1个L2模式，4案例支撑，4个反模式，跨领域迁移示例 |
| G4 | C | ⏳ 待提交 | 本报告和教程作为原子交付物提交 |

---

## 七、方法论编排日志

```
[CMD-LOG] S0  CMD_START       session=sc-20260828-samples-retrospective
[CMD-LOG] S1  SCENARIO_DETECTED  scenario=milestone
[CMD-LOG] S2  CHAIN_SELECTED   chain=R→I→E→A→C (V skipped, depth=standard)
[CMD-LOG] R0  CONCEPT_STARTED  采集4项目事实数据
[CMD-LOG] R99 CONCEPT_COMPLETED fact_count=38
[CMD-LOG] G1  GATE_PASSED      facts=38, no_causal_words=true
[CMD-LOG] I0  CONCEPT_STARTED  根因分析与洞察提炼
[CMD-LOG] I99 CONCEPT_COMPLETED insights=3
[CMD-LOG] G2  GATE_PASSED      four_tuple_complete=true
[CMD-LOG] E0  CONCEPT_STARTED  模式萃取
[CMD-LOG] E99 CONCEPT_COMPLETED patterns=1, maturity=L2
[CMD-LOG] G3  GATE_PASSED      trigger+steps+antipatterns+migration=true
[CMD-LOG] A0  CONCEPT_STARTED  原子化拆分产出物
[CMD-LOG] A99 CONCEPT_COMPLETED report+tutorial+index
```
