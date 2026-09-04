---
id: sympy-okf-wiki-spec
title: SymPy 符号计算库 OKF Wiki 教程生成 - PRD
date: 2026-08-23
category: spec
maturity: L0-draft
---

# SymPy 符号计算库 OKF Wiki 教程 - Product Requirement Document

## Problem Statement

SymPy 是 Python 生态中最成熟的开源符号计算（Computer Algebra System, CAS）库，采用 BSD-3-Clause 许可证。其源码规模庞大（核心模块 20+ 个，涵盖核心表达式、假设系统、微积分、积分、求解器、多项式、矩阵、化简、级数、数论、逻辑、几何、物理、统计等），现有官方文档以英文 API 参考和教程为主，缺乏从源码架构角度的系统化中文教程。开发者学习 SymPy 时往往停留在 API 调用层面，难以理解其核心表达式树模型、假设推理机制、化简策略、积分算法等内部原理。

## Users

- **Python 科学计算开发者**：需要理解 SymPy 符号计算的核心机制以高效使用
- **数学建模工程师**：需要掌握符号积分、微分方程求解、化简等高级功能
- **计算机代数研究者**：需要理解 SymPy 的表达式树、Risch 算法、Groebner 基等实现原理
- **教学人员与学生**：需要系统化的中文教程辅助符号计算学习
- **CAS 工具开发者**：需要参考 SymPy 架构设计自己的符号计算系统

## Goals

- 使用 `source-code-to-okf-wiki` 技能（R→I→E→V→C 五阶段链路）系统化学习 `external/libs/python/sympy/sympy/sympy/` 核心源码
- 在 `projects/awesome-okf-xs/bundles/pydata/sympy/` 下创建 OKF v0.2 规范的知识束（Bundle），产出结构化中文源码教程
- 通过 `seven-concepts-cmd` 方法论编排知识沉淀链路，确保质量门 G1-G4 全部通过
- 知识束遵循 concepts/examples/references 三层结构，frontmatter 完整，交叉引用正确
- 所有文档中的 API/类名/方法名经过 Grep 级源码验证，杜绝虚构内容
- 更新 `bundles/pydata/index.md`，将 SymPy 加入 PyData 生态清单

## Non-Goals (Out of Scope)

- 不做官方文档的完整翻译或复述
- 不覆盖 physics/（物理量子/力学/光学）、geometry/（几何）、liealgebras/（李代数）、holonomic/（完整函数）、categories/（范畴论）、crypto/（密码学）、diffgeom/（微分几何）、combinatorics/（组合数学）、algebras/（四元数）、discrete/（离散变换）等领域特定模块（聚焦通用符号计算核心）
- 不深入 polys/agca/（代数几何）和 polys/domains/ 下全部有限域/代数域实现细节
- 不覆盖 parsing/autolev/、parsing/latex/lark/、parsing/c/、parsing/fortran/、parsing/smtlib/ 等解析器子模块
- 不覆盖 plotting/ 模块（依赖 matplotlib 且非核心计算逻辑）
- 不覆盖 multipledispatch/（第三方依赖副本）、external/（外部工具封装）、benchmarks/（性能基准）、conftest.py 等非核心内容
- 不修改 awesome-okf-xs 子项目的 `.agents/` 规范文件
- 不生成 git 提交（用户未要求）

## Source Code Inventory

源码根目录：`d:\spaces\SpecWeave\external\libs\python\sympy\sympy\sympy\`

| 模块 | 语言 | 代码规模 | 包含级别 | 说明 |
|------|------|---------|---------|------|
| core/ | Python | 大（核心引擎） | Tier 1 | 表达式树核心：Basic/Expr/Symbol/Number/Add/Mul/Power/Function/Relational、假设关联、缓存、遍历、sympify、evalf数值计算 |
| assumptions/ | Python | 中 | Tier 1 | 假设推理系统：ask/假设注册/SAT求解/CNF/精炼/refine/谓词处理 |
| functions/ | Python | 大（函数库） | Tier 1 | 数学函数：初等函数（三角/指数/对数/双曲）、特殊函数（Bessel/Gamma/Hypergeometric/误差函数/分段函数） |
| calculus/ | Python | 小 | Tier 1 | 微积分工具：有限差分/奇点检测/欧拉数 |
| integrals/ | Python | 大 | Tier 1 | 积分算法：Risch算法/Meijer G积分/启发式积分/拉普拉斯变换/三角积分/有理函数积分/数值积分 |
| solvers/ | Python | 大（需检查是否独立目录） | Tier 1 | 方程求解：多项式求解/ODE/PDE/方程组/递推/不等式/丢番图方程 |
| simplify/ | Python | 中（需确认是否独立目录） | Tier 1 | 表达式化简：trigsimp/powsimp/simplify/fu三角化简/radsimp/合并/ ratsimp |
| series/ | Python | 中（需确认是否独立目录） | Tier 1 | 级数展开：泰勒/洛朗/渐近展开/极限/序列/傅里叶级数 |
| matrices/ | Python | 大 | Tier 2 | 符号矩阵：稠密/稀疏矩阵/行列式/特征值/分解/线性求解/矩阵表达式/图矩阵/正规形 |
| polys/ | Python | 大（多项式代数） | Tier 2 | 多项式运算：因式分解/Groebner基/域/环/构造器/行列式工具/多项式矩阵/AGCA |
| logic/ | Python | 中 | Tier 2 | 布尔代数与推理：boolalg/推理算法/DPLL SAT/DIMACS工具 |
| ntheory/ | Python | 中 | Tier 2 | 数论：素性测试/因子分解/模运算/连分数/分拆/椭圆曲线/BBP π/QS/ECM |
| sets/ | Python | 中（需确认是否独立目录） | Tier 2 | 集合论：模糊集/条件集/集合运算/图像处理集合 |
| stats/ | Python | 中（需确认是否独立目录） | Tier 2 | 符号统计：概率分布/随机变量/期望/方差/协方差/联合分布 |
| tensors/ | Python | 中（需确认是否独立目录） | Tier 2 | 张量：索引结构/张量运算/数组模块 |
| concrete/ | Python | 小 | Tier 2 | 离散数学：求和/乘积/Gosper算法/递归猜测 |
| printing/ | Python | 中（需确认是否独立目录） | Tier 2 | 打印系统：LaTeX/Str/Pretty/Unicode/Repr/树打印/数学ML |
| parsing/ | Python | 中（仅sympy_parser） | Tier 2 | 表达式解析：sympy_parser/LaTeX解析/Mathematica/Maxima转换（仅覆盖核心Python表达式解析器） |
| codegen/ | Python | 中 | Tier 3 | 代码生成：AST抽象节点/C/Fortran/Julia/Python代码生成/矩阵节点/算法优化/近似 |
| vector/ | Python | 中 | Tier 3 | 向量微积分：坐标系/向量/并矢/参考系 |
| interactive/ | Python | 小 | Tier 3 | 交互式会话：IPython集成/遍历打印/会话初始化 |
| __init__.py/abc.py | Python | 小 | Tier 1 | 包入口与符号定义（abc.py中预定义符号x,y,z等） |

**排除模块**：physics/（物理子系统，领域特定）、geometry/（几何）、liealgebras/（李代数）、holonomic/（完整函数）、categories/（范畴论）、crypto/（密码学）、diffgeom/（微分几何）、combinatorics/（组合数学）、algebras/（四元数代数）、discrete/（离散卷积/递推/变换）、plotting/（绑图）、multipledispatch/（第三方依赖副本）、external/（外部工具封装）、benchmarks/（性能基准）、parsing下非核心解析器（autolev/c/fortran/latex/lark/smtlib）、galgebra.py（几何代数接口）。

**待确认**：simplify/、series/、solvers/、sets/、stats/、tensors/、printing/、vector/ 是否在 sympy/ 目录下有独立子目录（之前 LS 被截断，需在 R 阶段确认完整目录列表）。

## Functional Requirements

### FR-1: 创建 SymPy 知识束目录
- 在 `bundles/pydata/sympy/` 下创建知识束目录
- 包含 `index.md`（根索引，含 okf_version）、`log.md`（变更日志）
- 包含 `concepts/`、`examples/`、`references/` 三个子目录

### FR-2: references/ 信源登记（6-10 篇）
- **references/**（6-10 篇，信源先行）：
  1. `core-basic-expr.md` - core/basic.py、core/expr.py 核心表达式基类（Basic/Expr/AtomicExpr/Atom）
  2. `core-operations.md` - core/add.py、core/mul.py、core/power.py 核心运算类（Add/Mul/Pow）
  3. `core-symbol-number.md` - core/symbol.py、core/numbers.py、core/sympify.py 符号/数值/转换
  4. `core-evalf-function.md` - core/evalf.py、core/function.py、core/function.py 数值计算与函数基类
  5. `assumptions.md` - assumptions/ 假设推理系统
  6. `functions-elementary.md` - functions/elementary/（如存在）或核心函数模块（三角函数/指数/对数）
  7. `integrals.md` - integrals/ 积分算法体系
  8. `matrices.md` - matrices/ 符号矩阵系统
  9. `polys-overview.md` - polys/ 多项式代数系统概述
  10. `printing.md` - printing/ 打印系统（如时间允许）

### FR-3: concepts/ 概念文档（14-20 篇）
- **入门基础篇**（5-6 篇）：
  1. `00-introduction.md` - SymPy 简介、定位、架构概览、核心特性
  2. `01-expression-tree.md` - 表达式树模型：Basic/Expr层次结构、Add/Mul/Pow嵌套、不可变性
  3. `02-symbol-number.md` - 符号（Symbol/Wild/Dummy）与数值（Integer/Rational/Float/Number）体系
  4. `03-sympify.md` - sympify转换机制、字符串解析、类型推断
  5. `04-assumptions.md` - 假设系统：Symbol假设声明、ask查询、SAT推理、refine精炼
  6. `05-elementary-functions.md` - 初等函数：三角函数/指数对数/双曲函数/分段函数/特殊常数

- **核心计算篇**（5-7 篇）：
  7. `06-calculus.md` - 微积分：diff微分/极限/有限差分/奇点
  8. `07-integration.md` - 积分体系：定积分/不定积分/换元/Risch算法/Meijer G/数值积分
  9. `08-solvers.md` - 方程求解：代数方程/方程组/不等式/ODE/PDE
  10. `09-simplification.md` - 化简策略：simplify/trigsimp/powsimp/fu/ratsimp/radsimp
  11. `10-series-expansion.md` - 级数：泰勒/洛朗/渐近展开/极限计算
  12. `11-matrices.md` - 符号矩阵：Matrix类/行列式/逆/特征值/分解/线性求解
  13. `12-polynomials.md` - 多项式代数：Poly类/因式分解/Groebner基/域扩张

- **高级主题篇**（3-5 篇，按时间）：
  14. `13-logic-boolalg.md` - 布尔代数与逻辑推理（如时间允许）
  15. `14-number-theory.md` - 数论功能（如时间允许）
  16. `15-printing.md` - 打印与显示系统：LaTeX/Str/Pretty（如时间允许）
  17. `16-code-generation.md` - 代码生成简介（如时间允许）

### FR-4: examples/ 示例文档（3-5 篇）
- **examples/**（3-5 篇）：
  1. `basic-usage.md` - 基础使用：定义符号、表达式构建、代入、求值、化简
  2. `calculus-practice.md` - 微积分实战：求导/积分/极限/级数展开
  3. `equation-solving.md` - 方程求解：线性/非线性/微分方程
  4. `matrix-calculations.md` - 矩阵运算实战（如时间允许）
  5. `advanced-topics.md` - 高级主题组合（如时间允许）

### FR-5: OKF 结构完整性
- 每个内容文档包含完整 YAML frontmatter：`type`、`title`、`description`、`tags`、`generated`、`verified`、`status`、`stale_after`、`sources`
- 子目录 `index.md` 不含 frontmatter
- 根 `index.md` 含 `okf_version: "0.2"`
- `log.md` 记录创建日期和各阶段完成情况

### FR-6: 方法论遵循
- 严格遵循 source-code-to-okf-wiki 五阶段流程：R（事实采集）→ I（架构洞察）→ E（批量生成）→ V（独立验证）→ C（模式沉淀）
- 通过 seven-concepts-cmd 编排知识沉淀场景链路（R→I→E）
- R 阶段：提取编号事实清单（F-xxx），写入 `.trae/specs/okf-wiki-ecosystem/sympy-okf-wiki/facts.md`，零推测
- I 阶段：提炼 3-5 个核心洞察（陈述+证据+反常识+行动四元组），写入 `insights.md`
- E 阶段：信源先行（references/ 先生成）、分批生成（每批≤7 文件）、index 最后写
- V 阶段：Grep 级 API 真实性验证、链接检查、frontmatter 检查

### FR-7: 更新 PyData 分类索引
- 更新 `bundles/pydata/index.md`，在库清单表格中新增 SymPy 行
- 更新生态依赖关系图和学习路径建议

## Non-Functional Requirements

- **NFR-1（语言）**：所有文档正文使用中文，技术术语保留英文并在首次出现时括号注释
- **NFR-2（文件命名）**：文件名使用 kebab-case 纯英文，概念文档按学习路径编号（00-xxx.md, 01-xxx.md, ...）
- **NFR-3（路径引用）**：交叉引用使用 `/` 开头的 bundle-relative 绝对路径
- **NFR-4（溯源）**：每个文档的 `sources` 字段指向对应 references/ 信源文件和事实编号
- **NFR-5（真实性）**：所有引用的类名、方法名、API 签名必须能在源码中通过 Grep 验证存在
- **NFR-6（代码示例）**：代码块标注语言，Python 代码示例基于实际源码 API 编写
- **NFR-7（原子性）**：每个概念文档聚焦单一主题，控制在合理长度
- **NFR-8（stale_after）**：统一设置为 `2027-12-31`（SymPy 核心 API 相对稳定）

## Constraints

- **规范约束**：产出物必须符合 OKF v0.2 规范和 awesome-okf-xs frontmatter 规范
- **格式参考**：以现有 `bundles/pydata/numpy/` 为格式范本（同为 PyData 生态单库 bundle）
- **源码路径**：源码位于 `external/libs/python/sympy/sympy/sympy/`，为第三方代码（禁止修改）
- **目标路径**：产出物位于 `projects/awesome-okf-xs/bundles/pydata/sympy/`，该子项目是 git submodule
- **禁止修改范围**：不修改 awesome-okf-xs 子项目的 `.agents/` 目录、AGENTS.md 等规范文件
- **分批约束**：E 阶段每批生成不超过 7 个文件，防止上下文过载
- **验证约束**：V 阶段必须对每个文档中引用的关键类名/方法名执行 Grep 验证
- **时间约束**：sympy 模块极多，优先保证 Tier 1 核心模块质量，Tier 2/Tier 3 按时间允许情况覆盖

## Dependencies

- `source-code-to-okf-wiki` Skill：提供 R→I→E→V→C 五阶段工作流和质量门
- `seven-concepts-cmd` Skill：提供知识沉淀场景的方法论编排
- 现有 OKF 规范文档：`bundles/meta/okf-spec/` 作为格式标准
- 现有 NumPy bundle：`bundles/pydata/numpy/` 作为格式参考范本（同属 PyData 单库 bundle）

## Assumptions

- 源码目录 `external/libs/python/sympy/sympy/sympy/` 已通过 git submodule 初始化，代码可读取
- SymPy 使用 BSD-3-Clause 许可证，文档生成属于合理使用
- 用户已有 Python 和基础数学（微积分/线性代数）基础
- 不需要安装 SymPy 或运行代码（静态源码分析为主），V 阶段通过 Grep 验证而非运行时测试
- Tier 1 核心模块预计产出 25-35 个内容文档，加上 Tier 2 模块总计约 30-40 个内容文档
- R 阶段首先需要确认完整目录结构（LS 输出被截断）

## Acceptance Criteria

### AC-1: SymPy 知识束目录创建
- **type**: rule
- **Pass condition**: `bundles/pydata/sympy/` 目录存在，包含 index.md、log.md、concepts/、examples/、references/
- **Evidence source**: 文件系统检查

### AC-2: 知识束结构完整
- **type**: rule
- **Pass condition**: 子目录 concepts/、examples/、references/ 下均有 index.md（无 frontmatter）；根 index.md 含 okf_version: "0.2"
- **Evidence source**: 文件系统检查 + 文件内容检查

### AC-3: 内容文档数量达标
- **type**: rule
- **Pass condition**:
  - references/ ≥6 篇信源文档
  - concepts/ ≥14 篇概念文档（入门基础≥5 + 核心计算≥7 + 高级主题≥2）
  - examples/ ≥3 篇示例文档
  - 总计 ≥23 篇内容文档（不含 index.md 和 log.md）
- **Evidence source**: 文件系统统计

### AC-4: Frontmatter 规范合规
- **type**: rule
- **Pass condition**: 每个非 index.md/log.md 的 .md 文件包含可解析的 YAML frontmatter，含 type/title/description/tags/generated/verified/status/stale_after/sources 字段；type 值为 concept/example/reference 之一
- **Evidence source**: 逐文件 frontmatter 检查

### AC-5: 无虚构 API（Grep 验证）
- **type**: rule
- **Pass condition**: 随机抽取 ≥15 个引用的类名/方法名/函数名在源码中 Grep 验证，命中率 100%；对于发现虚构的情况必须修正
- **Evidence source**: Grep 命令验证记录

### AC-6: 交叉引用无断链
- **type**: rule
- **Pass condition**: 所有内部交叉引用（/concepts/xxx.md, /examples/xxx.md, /references/xxx.md）目标文件存在
- **Evidence source**: 链接检查

### AC-7: 七概念质量门通过
- **type**: rule
- **Pass condition**:
  - G1（R 阶段）：facts.md 存在，事实编号 F-xxx，无"用于"/"目的是"等推断词，核心模块全覆盖
  - G2（I 阶段）：insights.md 存在，洞察包含陈述/证据/反常识/行动四元组
  - G3（E 阶段）：references/ 先于 concepts/ 生成，分批≤7 文件，index 最后写
  - G4（V 阶段）：Grep 验证、链接检查、frontmatter 检查全部通过
- **Evidence source**: 各阶段质量门检查记录

### AC-8: PyData 分类索引更新
- **type**: rule
- **Pass condition**: `bundles/pydata/index.md` 中新增 SymPy 条目，生态依赖关系图和学习路径更新
- **Evidence source**: 文件内容检查

### AC-9: 文档质量（中文表达与结构清晰度）
- **type**: rubric
- **Dimension**: 文档可读性、结构清晰度、知识地图合理性
- **Scale**: 0-2
  - 0: 文档结构混乱、中文表达不通顺、概念排列无逻辑
  - 1: 文档基本可读，概念排列有基本逻辑，但有少量表述不清或跳跃
  - 2: 文档结构清晰、中文表达流畅、概念按学习路径递进、有架构图/表格辅助理解
- **Pass threshold**: ≥1.5（抽评文档平均）
- **Evidence source**: 独立审查抽评

## Open Questions

1. simplify/、series/、solvers/、sets/、stats/、tensors/、printing/ 等目录是否在 sympy/sympy/ 下有独立子目录？（需在 R 阶段确认完整目录列表后决定覆盖范围）
2. 是否需要覆盖 codegen/（代码生成）模块？（当前列为 Tier 3，按时间允许情况决定）
3. 是否需要更新 `bundles/pydata/index.md` 中的生态依赖关系图？（SymPy 与 NumPy 关系为"SymPy 可与 NumPy 互操作但非依赖"）
4. physics/vector/ 模块是否需要简要提及？（当前方案排除，但向量微积分与数学物理方法密切相关）
