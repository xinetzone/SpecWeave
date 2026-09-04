---
title: "Spec: 国外物理著作原文与解读 OKF Wiki 全面系统重建"
status: "draft"
---

# Spec: 国外物理著作原文与解读 OKF Wiki 全面系统重建

## 问题

现有 `kexue/physics/physics-classics-reading` 束覆盖 12 部核心元典（伽利略→朗道），以"阅读指南"格式组织（方法论 + 精读示范 + 信源登记）。用户要求"全面系统的调研和整理国外的物理著作原文和解读"，需要：

1. **扩充元典数量**：从 12 部扩展至 25-30 部，补入惠更斯、法拉第、普朗克、居里夫人、德布罗意、玻色、约旦、维格纳、费曼论文、温伯格、霍金等里程碑著作
2. **增加原文精读束**：新建独立束，收录公有领域物理著作原文片段（拉丁文/英文原文 + 中译），配逐段现代解读与物理注释，超越现有"指南"格式
3. **分领域专题束**：按物理分支新建专题束（量子力学论文精读、相对论原著精读、热统经典精读），每个束聚焦一个领域的核心论文/著作
4. **更新索引与门控**：同步更新 kexue/physics/ 分组索引、kexue/ 域索引、bundles 总索引，通过 `invoke gates.all`

## 用户

- 高中高年级至物理专业研究生
- 物理教师与科技史爱好者
- 希望直接阅读国外物理学经典原文的中文读者

## 目标

1. 在 `kexue/physics/` 下构建物理学经典阅读完整体系（3-4 个束）
2. 扩充核心元典覆盖至 25-30 部
3. 公有领域著作提供原文片段 + 逐段现代解读
4. 所有新增束通过 OKF v0.2 frontmatter 规范
5. 通过 `invoke gates.toctrees` 和 `invoke gates.bundles` 质量门

## 非目标

- 不替换现有 `physics-classics-reading` 束（在其基础上扩展）
- 不收录中国古代物理典籍（已有 `chinese-physics-classics` 束覆盖）
- 不做物理教材或科普读物
- 不转述在版权著作的大段译文

## 功能需求

### FR-1: 扩充现有 physics-classics-reading 束

- 在 facts.md 中增加 13-18 部扩展元典的事实登记（F-105 起），目标总数 25-30 部
- 在 references/05-extended-canon.md 中同步扩充扩展书单
- 在 concepts/01-canon-map.md 中更新元典地图
- 在 insights.md 中更新知识地图（编年 × 分支表）

### FR-2: 新建原文精读束（physics-original-text-reading）

- 路径：`kexue/physics/physics-original-text-reading/`
- 收录 6-8 部公有领域著作的关键段落原文（拉丁文/英文原文 + 中译示范）
- 每段配现代物理解读：概念定位、推导还原、历史脉络、与现代符号对照
- 结构：concepts/（精读方法论）、examples/（逐段精读）、references/（原文信源）

### FR-3: 新建分领域专题束

- **量子力学论文精读束**（`quantum-papers-reading/`）：海森堡 1925、薛定谔 1926、狄拉克 1928、玻尔 1913 等核心论文
- **相对论原著精读束**（`relativity-originals-reading/`）：爱因斯坦 1905 狭义相对论、1916 广义相对论、闵可夫斯基 1908
- **热统经典精读束**（`thermo-statistical-classics/`）：卡诺 1824、克劳修斯、玻尔兹曼 H 定理、吉布斯系综

### FR-4: 更新索引与门控

- 更新 `kexue/physics/index.md`（新增束条目）
- 更新 `kexue/index.md`（束数计数）
- 更新 `doc/bundles/index.md`（总索引计数对账）
- 运行 `invoke gates.toctrees` 和 `invoke gates.bundles` 验证

## 非功能需求

### NFR-1: OKF v0.2 frontmatter 合规
- 每个非保留 .md 文件包含可解析的 YAML frontmatter
- 每个 frontmatter 包含非空 `type` 字段
- bundle 根 index.md 可带 `okf_version: "0.2"`

### NFR-2: 版权合规
- PD 著作（1929 年前美国出版物）可中英双语引用关键段落
- 在版权著作短引 ≤50 词/段、每篇 ≤200 词并附官方链接
- 中译本不转述大段译文

### NFR-3: 质量门通过
- `invoke gates.utf8`：所有文件 UTF-8 编码无 BOM
- `invoke gates.toctrees`：零断链、零孤立文档、bundle 根 index 完整
- `invoke gates.bundles`：总索引计数与目录树三角一致

### NFR-4: seven-concepts-cmd 方法论
- 按 R→I→E→V→C 链路执行
- G1：事实无因果词
- G2：洞察四元组完整
- G3：模式可迁移
- G4：行动项原子化

## 约束

- 子模块工作树当前干净（commit 14e352db）
- 存在并行会话可能写共享索引——提交前必须显式 add 目标文件
- 目录已重组为拼音域名（kexue/sheke/yixue 等），非英文域名
- `invoke gates.bundles` 使用锚点组按 1 束计规则，禁止手工估算

## 依赖

- awesome-okf-xs 子模块（已初始化，heads/main）
- Python 3.14+ 环境
- `invoke` 任务工具（pyproject.toml 声明）
- Sphinx + myst_parser 构建链

## 假设

- 公有领域物理著作原文可通过 Project Gutenberg、Internet Archive、HathiTrust、LoC 获取
- 用户已确认"全面系统重建"方向
- 现有 `physics-classics-reading` 束内容正确且可扩展（对抗审查已于 2026-08-31 通过）

## 开放问题

- 无（用户已明确"全面系统重建"方向）

## 验收标准

### AC-1: 元典覆盖扩充（rule）
- 条件：physics-classics-reading 束的 facts.md 包含 ≥25 部元典的事实登记
- 证据：facts.md 中 F-001~F-xxx 编号连续，覆盖 ≥25 部著作

### AC-2: 原文精读束创建（rule）
- 条件：`kexue/physics/physics-original-text-reading/` 目录存在且包含 index.md、concepts/、examples/、references/、facts.md、insights.md、log.md
- 证据：Glob 确认文件存在，index.md 包含 OKF v0.2 frontmatter

### AC-3: 分领域专题束创建（rule）
- 条件：至少 2 个分领域专题束目录存在且结构完整（index.md + concepts/ + examples/ + references/）
- 证据：Glob 确认每个束的文件存在

### AC-4: 索引同步（rule）
- 条件：kexue/physics/index.md、kexue/index.md、bundles/index.md 均更新且计数一致
- 证据：`invoke gates.bundles` 通过

### AC-5: 质量门通过（rule）
- 条件：`invoke gates.toctrees` 和 `invoke gates.bundles` 均无 ERROR
- 证据：命令输出退出码 0

### AC-6: frontmatter 合规（rule）
- 条件：所有新增 .md 文件包含 YAML frontmatter 且有 `type` 字段
- 证据：Grep 检查每个文件首行 `---`

### AC-7: 版权合规（rule）
- 条件：在版权著作引用均 ≤50 词/段、附官方链接
- 证据：examples/ 文件中无超过 50 词的未标注 PD 外文引用

### AC-8: 方法论执行（rubric）
- 维度：seven-concepts R→I→E→V→C 链路完整性
- 评分：0-2
  - 2：完整执行 R→I→E→V→C，每阶段产出物通过对应质量门
  - 1：执行了主要阶段但缺少 V 或 C
  - 0：跳过质量门或未按链路执行
- 通过阈值：≥1
- 证据：log.md 中记录方法论执行过程
