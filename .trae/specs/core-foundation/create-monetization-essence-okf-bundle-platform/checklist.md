# Checklist

## 方法论编排（seven-concepts）
- [ ] CMD_START 日志已输出，场景=知识沉淀+创新突破混合，depth=deep
- [ ] 链路 F→V→R→I→E→A→C 依序执行，无跳序
- [ ] G1：事实台账 ≥20 条（facts.md），无因果词，每条可溯源（F 编号），纯客观陈述
- [ ] G2：洞察 ≥3 条四元组完整（陈述/证据 F 编号/反常识/行动），维度独立
- [ ] G3：方案可迁移（触发+步骤+反模式），反模式 ≥3 个且来自真实教训
- [ ] G4：所有提交原子化（单一职责、可独立验证、Conventional Commits 中文描述）
- [ ] V：对抗审查 ≥5 条具体意见，至少采纳 2 条修正，修正对照已记录
- [ ] F 后 V 强制执行，未跳过

## 变现本质研究与道家对齐（spec 需求 1/2）
- [ ] 变现本质公理体系 ≥5 条，每条有推导链 + 现实信源佐证，无源断言为零
- [ ] 有"变现本质一句话概括"
- [ ] 公理间关系以 Mermaid 呈现
- [ ] 道家对齐框架覆盖：道法自然/无为而无不为/不争/上善若水/天之道损有余而补不足/自化
- [ ] 道家对齐框架引用 `guoxue/daojia/` 等真实信源
- [ ] 给出"合道/不合道"判定与反模式

## Agent 自动变现架构（spec 需求 3）
- [ ] 架构覆盖五层：观察/决策/行动/反馈/治理
- [ ] 满足自主（自动运行）、自发（价值信号驱动）、自进化（反馈学习）三特性
- [ ] 架构可直接映射到 apps/agent-monetize/ 模块划分
- [ ] 合规红绿区边界清单已产出（反欺诈/反垃圾/ToS/隐私）

## 100+ 可行性方案目录（spec 需求 4）
- [ ] 全面考察 497 束/56 组/9 域（考察记录可查）
- [ ] 方案总数 ≥100 种
- [ ] 方案互异（去重校验通过）
- [ ] 每个方案含 6 要素：名称/机制/价值本质（引公理）/信源溯源（引束）/成本·风险·周期/道家对齐
- [ ] 每个方案至少引用 1 个真实束（溯源校验通过）
- [ ] 目录按 9 域分组组织，examples/ 下原子化多文件（每文件 ≤5000 字符）
- [ ] 覆盖度：单域方案 ≥10 种的域数 ≥5 个

## OKF 知识包（spec 需求 5 + OKF 规范）
- [ ] `projects/awesome-okf-xs/doc/bundles/sheke/industry/monetization-essence/` 束已创建
- [ ] 束结构完整：index.md / concepts/ / examples/ / references/ / facts.md / log.md
- [ ] frontmatter 遵循 OKF v0.2（okf_version/type/title/description/sources 等），中文标点、无双引号嵌套陷阱
- [ ] 束内 toctree 完整覆盖全部 .md
- [ ] 已注册至 `sheke/industry/index.md` 组索引与 `doc/bundles/index.md` 总索引
- [ ] `invoke gates.utf8` 通过（无 BOM）
- [ ] `invoke gates.toctrees` 通过（无断链/无孤立文档）
- [ ] `invoke gates.bundles` 通过（束/组/域计数三角一致）
- [ ] 与既有 ai-monetization 束/文档为并列互补关系，无内容重复

## 可运行平台（spec 需求 5/6）
- [ ] `apps/agent-monetize/` 包结构完整（pyproject.toml requires-python>=3.14、ruff/black、tests/）
- [ ] core 自主循环（observe→decide→act→learn）已实现
- [ ] tao 治理门控（无为门 + 红绿区合规）已实现
- [ ] channel 抽象（Channel 基类 4 钩子）已实现
- [ ] 沙箱演示通道 ≥2 个（内容计价模拟/数据服务计价模拟）
- [ ] 真实 API 适配器接口已预留，默认关闭，需显式配置启用
- [ ] tvm-ffi 在 py314 环境可 `import tvm_ffi`（自 xuanspace/vendor/tvm-ffi）
- [ ] C++ FFI 模块（PackedFunc）已实现并经 tvm-ffi 绑定暴露
- [ ] 决策层实际调用 FFI 打分函数完成机会评估
- [ ] `python -m agent_monetize demo` 演示闭环可运行（沙箱虚拟货币，零人工干预）
- [ ] pytest 通过，核心模块覆盖率 ≥90%，一般模块 ≥80%
- [ ] `ruff check` 零错误
- [ ] 平台 README 含启动方式/架构/通道扩展指南/合规边界

## 提交与收尾（C 阶段）
- [ ] awesome-okf-xs 子模块已原子提交（暂存 blob 核验通过，无他方文件混入）
- [ ] 主仓库已 bump 子模块指针并提交
- [ ] apps/agent-monetize 已原子提交
- [ ] `.trae/specs/core-foundation/README.md` 与全局看板已登记本 spec
- [ ] 链接检查与规范校验通过
- [ ] 七概念汇总输出：CMD-LOG 质量门通过记录 + 产出物清单
