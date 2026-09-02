# Tasks

> 方法论编排：seven-concepts（scenario = knowledge + innovation，链路 F→V→R→I→E→A→C）
> 会话前缀：`sc-20260902-monetization-essence`

## 阶段 0：方法论编排与预检
- [x] Task 0: 方法论编排启动（S0 场景识别 + S1 链路选择）
  - [x] SubTask 0.1: 输出 CMD_START 日志，确认场景 = 知识沉淀+创新突破混合，depth=deep
  - [x] SubTask 0.2: 完成内容敏感度预检（公开内容：开源知识+方法论研究，无隐私/私域数据）
  - [x] SubTask 0.3: 复核目标路径：OKF 束 → `projects/awesome-okf-xs/doc/bundles/sheke/industry/monetization-essence/`；平台 → `apps/agent-monetize/`
  - [x] SubTask 0.4: 预检 awesome-okf-xs 子模块状态（`git submodule status`、`git -C projects/awesome-okf-xs status`、查 `.git/MERGE_HEAD`），确认无并行会话冲突

## 阶段 1：F 第一性原理——变现本质研究
- [x] Task 1: 变现本质公理体系推导（F 阶段，G1 前置）
  - [x] SubTask 1.1: 问题界定与假设剥离：列出"变现"隐含假设（钱=？交换=？价值=？）并逐条归零
  - [x] SubTask 1.2: 推导 ≥5 条公理：价值→交换→稀缺→交易成本→信任→再分配→循环；每条附现实信源佐证
  - [x] SubTask 1.3: 产出"变现本质一句话概括"与公理间逻辑关系图（Mermaid）
  - [x] SubTask 1.4: 道家对齐框架：道法自然/无为/不争/上善若水/损有余补不足/自化 → 可操作设计原则 + 反模式

## 阶段 2：V 对抗审查（强制）
- [x] Task 2: 对本质研究与架构设计执行对抗审查（V 阶段）
  - [x] SubTask 2.1: 四视角攻击（魔鬼代言人/新人/老板/未来）本质公理与道家对齐框架，输出 ≥5 条具体意见
  - [x] SubTask 2.2: 修正公理/框架，至少采纳 2 条意见，记录修正对照
  - [x] SubTask 2.3: 对 agent 自动变现架构做合规视角攻击（反欺诈/反垃圾/ToS/隐私），输出红绿区边界清单

## 阶段 3：R/I 事实采集与洞察——全面考察 OKF bundles
- [x] Task 3: 497 束 OKF bundles 事实采集（R 阶段，G1）
  - [x] SubTask 3.1: 盘点 9 域/56 组/497 束清单，登记可用信源（重点：jishu 17 组 376 束、sheke/industry、guoxue/daojia 19 束、zhexue/methodology、sheke/finance+marketing）
  - [x] SubTask 3.2: 对每域抽取代表性束做深度阅读，采集事实台账 ≥20 条（facts.md，无因果词、可溯源、编号 F-001 起）
- [x] Task 4: 跨域变现洞察提炼（I 阶段，G2）
  - [x] SubTask 4.1: 提炼 ≥3 条四元组洞察（陈述/证据 F 编号/反常识/行动），维度独立
  - [x] SubTask 4.2: 归纳"可变现资产的共同特征"与"变现通道分类学"（第一层分类框架）

## 阶段 4：E 萃取——100+ 可行性方案目录
- [x] Task 5: 萃取 ≥100 种可行性方案（E 阶段，G3）
  - [x] SubTask 5.1: 按 9 域逐域萃取方案（jishu 每分组 3-8 种、guoxue/sheke 每域 5-15 种、其余各域 3-10 种），单域产出方案 ≥10 种的域数 ≥5 个
  - [x] SubTask 5.2: 每个方案含 6 要素：名称/机制/价值本质（引公理）/信源溯源（引束）/成本·风险·周期/道家对齐
  - [x] SubTask 5.3: 合计校验 ≥100 种、去重校验（方案互异）、溯源校验（每个方案至少引用 1 个真实束）
  - [x] SubTask 5.4: 反模式提炼（≥3 个变现反模式，来自真实教训）

## 阶段 5：A/OKF 知识包生成（awesome-okf-xs）
- [x] Task 6: 创建 monetization-essence 束（OKF v0.2 规范）
  - [x] SubTask 6.1: 创建 `sheke/industry/monetization-essence/` 目录骨架（index.md/concepts/examples/references/facts.md/log.md）
  - [x] SubTask 6.2: 编写 concepts/（本质公理·道家对齐·agent 自动变现架构·通道分类学）与 examples/（100+ 方案目录，按 9 域原子化多文件）
  - [x] SubTask 6.3: 编写 references/（信源登记）与 facts.md（事实台账）；frontmatter 遵循 OKF v0.2 规范（okf_version/type/title/description/sources 等，中文标点，双引号嵌套合规）
  - [x] SubTask 6.4: 束内 toctree 完整（覆盖全部 .md），`invoke gates.toctrees` 通过
  - [x] SubTask 6.5: 注册至 `sheke/industry/index.md` 组索引 + `doc/bundles/index.md` 总索引（注意共享索引并行会话竞态：gates 重算→Edit→提交紧凑完成）
  - [x] SubTask 6.6: `invoke gates.bundles` + `invoke gates.utf8` 三门全绿（py314 conda 环境执行）
- [x] Task 7: awesome-okf-xs 原子提交（C 阶段，G4）
  - [x] SubTask 7.1: 暂存核验（git add 指定文件→git show :<path> 核验暂存 blob），确认不含他方文件
  - [x] SubTask 7.2: 提交信息遵循 Conventional Commits（`docs(monetization-essence): 新增变现本质 OKF 束（100+ 方案）`）
  - [x] SubTask 7.3: 记录子模块新 SHA，供主仓库 bump

## 阶段 6：可运行平台实现（apps/agent-monetize/）
- [x] Task 8: 平台骨架与自主循环（Python 3.14+）
  - [x] SubTask 8.1: 创建 `apps/agent-monetize/` 包结构（pyproject.toml，requires-python>=3.14，ruff/black 配置，tests/）
  - [x] SubTask 8.2: 实现 core 自主循环（observe→decide→act→learn）+ state + feedback 自进化机制
  - [x] SubTask 8.3: 实现 tao 治理门控（无为门：低确定性不行动/待时；红绿区合规：红区禁行清单）
  - [x] SubTask 8.4: 实现 channel 抽象（Channel 基类 4 钩子）+ 2-3 个沙箱演示通道（内容计价模拟/数据服务计价模拟）
  - [x] SubTask 8.5: 实现真实 API 适配器接口（adapter 协议，默认关闭，需显式配置）
- [x] Task 9: tvm-ffi 高性能计算集成
  - [x] SubTask 9.1: 在 py314 环境安装/引用 tvm-ffi（自 `projects/xuanspace/vendor/tvm-ffi`，验证 `import tvm_ffi`）
  - [x] SubTask 9.2: 编写 C++ FFI 模块（PackedFunc 注册：机会扫描打分/结构化计算等），用 tvm-ffi 绑定暴露给 Python
  - [x] SubTask 9.3: 决策层调用 FFI 打分函数完成机会评估（证明平台使用 tvm-ffi）
- [x] Task 10: 演示闭环与测试
  - [x] SubTask 10.1: `python -m agent_monetize demo` 演示模式：自主循环完整跑通（沙箱虚拟货币），零人工干预
  - [x] SubTask 10.2: pytest 测试（核心模块覆盖率 ≥90%，一般模块 ≥80%），`ruff check` 零错误
  - [x] SubTask 10.3: 平台 README（启动方式/架构/通道扩展指南/合规边界）

## 阶段 7：C 原子提交与收尾
- [x] Task 11: 主仓库原子提交与收尾
  - [x] SubTask 11.1: 主仓库 bump 子模块指针至 awesome-okf-xs 新 SHA 并提交（`chore(submodules): 更新 awesome-okf-xs 至 monetization-essence 束`）
  - [x] SubTask 11.2: apps/agent-monetize 变更原子提交（`feat(apps/agent-monetize): 智能体自动变现平台（tvm-ffi 集成+沙箱闭环）`）+ 决策层测试补充提交
  - [x] SubTask 11.3: 更新 `.trae/specs/core-foundation/README.md` 主题看板与全局看板登记本 spec
  - [x] SubTask 11.4: 链接检查与规范校验通过（check-links/规范一致性）
  - [x] SubTask 11.5: 七概念汇总输出：CMD-LOG 全链路质量门通过记录 + 产出物清单

# Task Dependencies

- Task 0 为基础，全部任务依赖
- Task 1（F）→ Task 2（V 强制在 F 后）→ Task 3/4（R/I）→ Task 5（E）
- Task 5 → Task 6（OKF 束内容）→ Task 7（子模块提交）
- Task 8/9 平台实现与 Task 5 方案目录并行不冲突；Task 8 → Task 9 → Task 10
- Task 7 与 Task 11 顺序：先子模块提交 → 主仓库 bump（遵循推送闸门流程；本地提交，用户未令推送则不推送）
- Task 11 依赖 Task 6/7 与 Task 10 全部完成
- 建议执行顺序：Task 0 → 1 → 2 → 3/4 → 5 → 6 → 7 → 8/9 → 10 → 11
