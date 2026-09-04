# SymPy 符号计算库 OKF Wiki 教程 - Implementation Plan

## Task Dependencies

```
Phase 0: Setup → Phase 1: R+I (fact collection + insights) → Phase 2: E (references→concepts→examples→indexes) → Phase 3: V (verification) → Phase 4: Category Index Update → Phase 5: Independent Review
```

Processing order within E: references/ 先生成（信源先行），然后 concepts/ 按学习路径分三批（入门基础→核心计算→高级主题），然后 examples/，最后 indexes。

Rationale: 与 numpy bundle 类似（单库 bundle 而非多子项目生态），但 sympy 模块更多，需要分批生成。

---

## Phase 0: Setup & Scaffolding

### Task 1: 创建 SymPy 知识束目录脚手架
- **Priority**: high
- **Depends On**: None
- **ACs Addressed**: [AC-1, AC-2]
- **Description**:
  - 确认完整的 sympy 源码目录结构（解决 spec Open Question #1）：LS `external/libs/python/sympy/sympy/sympy/` 确认 simplify/、series/、solvers/、sets/、stats/、tensors/、printing/、vector/ 等目录是否存在
  - 创建 `bundles/pydata/sympy/` 目录
  - 创建 `concepts/`、`examples/`、`references/` 空子目录
  - 创建 `.trae/specs/okf-wiki-ecosystem/sympy-okf-wiki/` 工作目录
- **Test Requirements**:
  - `rule` TR-1.1: 目录结构存在且完整（1 bundle × 3 子目录 + spec 工作目录）
  - `rule` TR-1.2: 确认源码完整目录列表，记录存在/不存在的模块

---

## Phase 1: R+I 阶段（事实采集与架构洞察）

### Task 2: R阶段 - 核心模块事实采集（Tier 1）
- **Priority**: high
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 深度阅读 Tier 1 核心源码模块：
    - **core/**: `basic.py`（Basic基类/元类/参数处理）、`expr.py`（Expr/AtomicExpr/Atom）、`add.py`（Add类）、`mul.py`（Mul类）、`power.py`（Pow类）、`symbol.py`（Symbol/Wild/Dummy）、`numbers.py`（Integer/Rational/Float/Number层次）、`sympify.py`（sympify转换）、`evalf.py`（数值计算）、`function.py`（Function类/AppliedUndef/UndefinedFunction）、`relational.py`（Relational/Equality）、`operations.py`（LatticeOp）、`traversal.py`（表达式遍历）、`subs.py`（subs.py或在core/__init__.py中的替换逻辑）、`__init__.py`（导出API）
    - **assumptions/**: `ask.py`（ask查询）、`assume.py`（全局假设）、`cnf.py`（CNF合取范式）、`facts.py`（事实库）、`refine.py`（refine精炼）、`satask.py`（SAT求解）、`sathandlers.py`（SAT处理器）、`wrapper.py`（假设包装）、`predicates/`（谓词目录）、`handlers/`（处理器目录）、`__init__.py`
    - **calculus/**: `__init__.py`（导出API）、`finite_diff.py`（有限差分）、`singularities.py`（奇点检测）、`euler.py`（欧拉数）、`util.py`
    - **functions/**: `__init__.py`（导出）、`elementary/`目录（三角函数/指数/对数/双曲/复数/整数函数）、`special/`目录（特殊函数如存在）
    - **integrals/**: `__init__.py`、`integrals.py`（积分入口）、`risch.py`（Risch算法）、`meijerint.py`（Meijer G积分）、`heurisch.py`（启发式积分）、`laplace.py`（拉普拉斯变换）、`transforms.py`（积分变换）、`trigonometry.py`（三角积分）、`rationaltools.py`（有理函数积分）、`quadrature.py`（数值积分）
  - 提取 ≥60 条编号事实（F-001起），写入 `.trae/specs/okf-wiki-ecosystem/sympy-okf-wiki/facts.md`
  - 事实覆盖：表达式树层次、Basic/Expr核心机制、Symbol/Number类型、sympify转换、Add/Mul/Pow运算组合、Function类体系、假设查询机制、微积分/积分/化简/级数API、核心类名/方法名/参数签名
- **Test Requirements**:
  - `rule` TR-2.1: 事实数量 ≥60 条，编号连续
  - `rule` TR-2.2: 事实无"用于"/"目的是"/"设计为"等推断词（G1 质量门）
  - `rule` TR-2.3: 每个事实标注源码文件路径

### Task 3: R阶段 - 扩展模块事实采集（Tier 2/3）
- **Priority**: medium
- **Depends On**: Task 2
- **ACs Addressed**: [AC-7]
- **Description**:
  - 阅读 Tier 2/3 模块（按目录确认后的实际存在情况调整）：
    - **matrices/**: `matrixbase.py`、`dense.py`（Matrix类）、`sparse.py`、`determinant.py`、`eigen.py`、`solvers.py`、`decompositions.py`、`expressions/`（矩阵表达式）、`__init__.py`
    - **polys/**: `__init__.py`、`constructor.py`（Poly构造）、`factortools.py`（因式分解）、`polytools.py`（多项式工具）、`domains/`（域系统）、`groebnertools.py`（Groebner基，如存在）、`densetools.py`（稠密多项式工具）、`euclidtools.py`（欧几里得工具）、`fields.py`/`rings.py`（域/环，如存在）
    - **logic/**: `boolalg.py`（布尔代数）、`inference.py`（推理）、`algorithms/`（DPLL等）
    - **ntheory/**: `__init__.py`、`factor_.py`（因子分解）、`primetest.py`（素性测试）、`generate.py`（素数生成）、`modular.py`（模运算）
    - **simplify/**:（如独立目录存在）`simplify.py`、`trigsimp.py`、`fu.py`、`radsimp.py`、`powsimp.py`
    - **series/**:（如独立目录存在）核心模块
    - **solvers/**:（如独立目录存在）核心模块
    - **printing/**:（如独立目录存在）`printer.py`、`latex.py`、`str.py`
    - **parsing/**: `sympy_parser.py`（核心Python表达式解析器）
    - **concrete/**: `summations.py`、`products.py`、`gosper.py`
    - **codegen/**:（Tier 3，时间允许）`ast.py`、`pyutils.py`、`cnodes.py`/`fnodes.py`/`cxxnodes.py`
    - **abc.py**、**__init__.py**（顶层导出）
  - 追加提取 ≥30 条事实（F-061起），写入 facts.md
- **Test Requirements**:
  - `rule` TR-3.1: 追加事实 ≥30 条（累计 ≥90 条），无推断词
  - `rule` TR-3.2: 覆盖 matrices/polys/logic/ntheory 核心模块

### Task 4: I阶段 - 架构洞察与知识地图
- **Priority**: high
- **Depends On**: Task 3
- **ACs Addressed**: [AC-7, AC-9]
- **Description**:
  - 基于 facts.md 提炼 4-6 个核心架构洞察（四元组：陈述+证据(F-xxx)+反常识+行动）
  - 洞察方向建议：
    1. 表达式树不可变模型（SymPy表达式是不可变DAG而非AST树，subs返回新对象）
    2. 运算自动分发机制（Add/Mul/Pow的自动创建/化简/参数排序）
    3. 假设系统的SAT求解架构（基于CNF和DPLL的逻辑推理）
    4. 积分算法分层体系（Risch→MeijerG→启发式→数值的fallback链）
    5. 函数与求值分离（Function类定义数学关系，evalf/doit等方法触发计算）
  - 设计知识地图：文档分组（入门基础/核心计算/高级主题）、学习路径、每个概念文档覆盖的事实编号
  - 确定 references/、concepts/、examples/ 的最终文档清单
  - 写入 `.trae/specs/okf-wiki-ecosystem/sympy-okf-wiki/insights.md`
- **Test Requirements**:
  - `rule` TR-4.1: 洞察数量 ≥4 条
  - `rule` TR-4.2: 每条洞察包含陈述/证据/反常识/行动四元组（G2 质量门）
  - `rule` TR-4.3: 知识地图覆盖所有计划的 concepts/examples/references 文档

---

## Phase 2: E 阶段（批量生成 OKF 文档）

> **E 阶段铁律**：references/ 先生成（信源先行），每批 ≤7 文件，index 最后写。

### Task 5: 生成 references/ 信源文档（批次1：core模块，4-5篇）
- **Priority**: high
- **Depends On**: Task 4
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - 生成第一批 references/ 信源文档（≤5篇）：
    1. `core-basic-expr.md` - core/basic.py、core/expr.py：Basic/Expr/AtomicExpr/Atom类层次、_args/_assumptions属性、核心方法（args, func, subs, xreplace, doit, rewrite, simplify等）
    2. `core-operations.md` - core/add.py、core/mul.py、core/power.py：Add/Mul/Pow类、自动分发与参数排序、AssocOp/BooleanArgs等
    3. `core-symbol-number.md` - core/symbol.py、core/numbers.py、core/sympify.py：Symbol/Wild/Dummy、Integer/Rational/Float/Number层次、sympify转换机制
    4. `core-evalf-function.md` - core/evalf.py、core/function.py、core/relational.py：数值计算、Function/AppliedUndef类、Relational/Equality
    5. `assumptions.md` - assumptions/：ask查询、SAT推理、CNF、refine精炼
- **Test Requirements**:
  - `rule` TR-5.1: 信源文档 4-5 篇
  - `rule` TR-5.2: 每篇 frontmatter 完整（type: reference）
  - `rule` TR-5.3: 每篇包含关键事实 F-xxx 引用和源码路径

### Task 6: 生成 references/ 信源文档（批次2：算法模块，3-5篇）
- **Priority**: high
- **Depends On**: Task 5
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - 生成第二批 references/ 信源文档（≤5篇）：
    6. `functions-calculus.md` - functions/、calculus/：初等函数体系、微分/有限差分/奇点
    7. `integrals.md` - integrals/：积分入口、Risch算法、Meijer G、启发式积分、变换
    8. `matrices.md` - matrices/：Matrix类、稠密/稀疏矩阵、线性代数运算
    9. `polys.md` - polys/：多项式系统、Poly类、因式分解、域系统
    10. `solvers-series-simplify.md` - solvers/、series/、simplify/（如这些目录存在）：求解器/级数/化简入口
- **Test Requirements**:
  - `rule` TR-6.1: 信源文档 3-5 篇
  - `rule` TR-6.2: frontmatter 完整
  - `rule` TR-6.3: 关键事实引用准确

### Task 7: 生成 concepts/ 概念文档（批次1：入门基础篇，5-6篇）
- **Priority**: high
- **Depends On**: Task 6
- **ACs Addressed**: [AC-3, AC-4, AC-7, AC-9]
- **Description**:
  - 第一批概念文档（入门基础，≤6篇）：
    1. `00-introduction.md` - SymPy简介：符号计算定位、BSD许可证、核心特性概览、模块架构、安装与isympy
    2. `01-expression-tree.md` - 表达式树模型：Basic/Expr层次、Add/Mul/Pow嵌套结构、不可变性、args/func属性、表达式遍历
    3. `02-symbol-number.md` - 符号与数值：Symbol/Wild/Dummy的区别、Integer/Rational/Float数值类型、数值精度、S()简写
    4. `03-sympify.md` - sympify转换机制：字符串转表达式、类型推断、locals参数、parse_expr
    5. `04-assumptions.md` - 假设系统：Symbol(positive=True)等声明、ask()查询、is_*属性、refine精炼、新旧假设系统
    6. `05-elementary-functions.md` - 初等函数：sin/cos/tan/exp/log、三角函数化简、常数（pi/E/I/oo）、分段函数Piecewise
  - 每篇含：概述、核心机制（配表格/代码片段）、代码示例、相关概念链接
- **Test Requirements**:
  - `rule` TR-7.1: 文档数量 5-6 篇
  - `rule` TR-7.2: frontmatter 完整（type: concept, sources 指向 references/）
  - `rule` TR-7.3: 代码示例中引用的 API 在 facts.md 中有对应事实

### Task 8: 生成 concepts/ 概念文档（批次2：核心计算篇，5-7篇）
- **Priority**: high
- **Depends On**: Task 7
- **ACs Addressed**: [AC-3, AC-4, AC-7, AC-9]
- **Description**:
  - 第二批概念文档（核心计算，≤7篇）：
    7. `06-calculus.md` - 微积分：diff()微分、Derivative类、limit()极限、finite_diff有限差分、singularities奇点
    8. `07-integration.md` - 积分体系：integrate()/Integral、定积分/不定积分、换元、Risch算法简介、Meijer G积分、数值积分
    9. `08-solvers.md` - 方程求解：solve()/solveset、线性/非线性方程、方程组、ODE（dsolve）、不等式
    10. `09-simplification.md` - 化简策略：simplify()、trigsimp/powsimp/fu/ratsimp/radsimp、collect/factor/expand
    11. `10-series-expansion.md` - 级数：series()泰勒展开、lseries/nseries、渐近展开、极限计算
    12. `11-matrices.md` - 符号矩阵：Matrix类、矩阵运算、det()行列式、inv()逆、eigenvals/eigenvects、rref/solve
    13. `12-polynomials.md` - 多项式代数：Poly类、factor/expand/gcd/div/quo/rem、Groebner基简介、factor_list
- **Test Requirements**:
  - `rule` TR-8.1: 文档数量 5-7 篇
  - `rule` TR-8.2: frontmatter 完整，sources 正确
  - `rule` TR-8.3: 交叉链接使用 / 开头 bundle-relative 路径

### Task 9: 生成 concepts/ 概念文档（批次3：高级主题篇，3-5篇）+ examples/（3-5篇）
- **Priority**: medium
- **Depends On**: Task 8
- **ACs Addressed**: [AC-3, AC-4, AC-7, AC-9]
- **Description**:
  - 第三批概念文档（高级主题，≤5篇，时间允许）：
    14. `13-logic-boolalg.md` - 布尔代数：And/Or/Not/Xor、satisfiable()、逻辑推理
    15. `14-number-theory.md` - 数论：isprime/factorint/primefactors、modular_inverse、continued_fraction
    16. `15-printing.md` - 打印系统：init_printing、latex()、sstr/pretty、打印自定义
    17. `16-discrete-sums.md` - 离散数学：Sum/Product/summation、gosper_sum
    18. `17-code-generation.md` - 代码生成（时间允许）：lambdify、codegen、C/Fortran/Python代码生成
  - examples/（3-5 篇）：
    1. `basic-usage.md` - 基础使用：定义符号、构建表达式、subs代入、evalf求值、化简
    2. `calculus-practice.md` - 微积分实战：求导/高阶导/偏导/定积分/不定积分/极限/泰勒展开
    3. `equation-solving.md` - 方程求解：一元二次/非线性/方程组/常微分方程
    4. `matrix-calculations.md` - 矩阵运算实战（时间允许）
    5. `advanced-examples.md` - 高级主题组合示例（时间允许）
- **Test Requirements**:
  - `rule` TR-9.1: 概念文档 3-5 篇，示例文档 3-5 篇
  - `rule` TR-9.2: 每篇 example 含可运行的代码示例（基于 facts.md 中验证过的 API）
  - `rule` TR-9.3: frontmatter 完整（example 类型的 sources 指向相关 concepts 和 references）

### Task 10: 生成 indexes 和 log.md
- **Priority**: high
- **Depends On**: Task 9
- **ACs Addressed**: [AC-2, AC-4]
- **Description**:
  - 生成 concepts/index.md、examples/index.md、references/index.md（子目录索引，无 frontmatter）
  - 生成根 index.md（含 okf_version: "0.2"、知识包概述、文档导航、学习路径建议）
  - 生成 log.md（变更日志，记录 2026-08-23 创建）
- **Test Requirements**:
  - `rule` TR-10.1: 子目录 index.md 列出对应目录下所有文档
  - `rule` TR-10.2: 根 index.md 含 okf_version: "0.2" frontmatter
  - `rule` TR-10.3: log.md 包含 2026-08-23 日期记录和文档统计

---

## Phase 3: V 阶段（独立验证）

### Task 11: V阶段验证与修复
- **Priority**: high
- **Depends On**: Task 10
- **ACs Addressed**: [AC-4, AC-5, AC-6, AC-7]
- **Description**:
  - 结构检查：所有文件存在、frontmatter 可解析、必需字段完整
  - Grep API 验证：随机抽取 ≥15 个类名/方法名/函数名（覆盖 Basic/Expr/Add/Mul/Symbol/integrate/diff/solve/simplify/Matrix/Poly/ask/sympify/evalf/lambdify等核心API），在源码中验证存在性
  - 链接检查：所有交叉引用目标文件存在
  - frontmatter 检查：type/title/description/tags/generated/verified/status/stale_after/sources 字段齐全
  - 检查子目录 index.md 无 frontmatter
  - 检查路径引用使用 / 开头 bundle-relative 路径
  - 修复发现的问题
  - 更新所有文档的 verified 字段
- **Test Requirements**:
  - `rule` TR-11.1: 结构检查 100% 通过
  - `rule` TR-11.2: Grep 验证 ≥15 个 API，命中率 100%
  - `rule` TR-11.3: 链接检查无断链
  - `rule` TR-11.4: 所有问题修复完成（G4 质量门通过）

---

## Phase 4: 分类索引更新

### Task 12: 更新 PyData 分类索引
- **Priority**: high
- **Depends On**: Task 11
- **ACs Addressed**: [AC-8]
- **Description**:
  - 更新 `bundles/pydata/index.md`：
    - 在库清单表格中新增 SymPy 行（简介：符号计算库——符号表达式/微积分/方程求解/矩阵/化简）
    - 更新生态依赖关系图（SymPy 与 NumPy 为可选互操作关系，非强依赖）
    - 更新学习路径建议（在科学计算基础后增加符号计算选项）
- **Test Requirements**:
  - `rule` TR-12.1: pydata/index.md 新增 SymPy 条目
  - `rule` TR-12.2: 生态关系图和学习路径更新

---

## Phase 5: 独立审查

### Task 13: 独立审查（Independent Review）
- **Priority**: high
- **Depends On**: Task 12
- **ACs Addressed**: [AC-1~AC-9]
- **Description**:
  - 委派一个独立 reviewer（fresh context）对所有产出物进行审查
  - Reviewer 检查：结构完整性、frontmatter 合规、API 真实性（抽样 Grep ≥10 个 API）、链接有效性、文档质量（中文表达/结构清晰度/学习路径合理性）
  - 产出 review.md 报告
  - 如发现 actionable findings，返回 Implement 阶段修复后重新审查
- **Test Requirements**:
  - `rule` TR-13.1: review.md 存在，包含 pass/fail/blocked 结论
  - `rule` TR-13.2: 所有 rule 类型 AC 有独立通过证据
  - `rubric` TR-13.3: 文档质量评分 ≥1.5/2

---

## Task Summary

| Phase | Tasks | 数量 | 说明 |
|-------|-------|------|------|
| Phase 0: Setup | Task 1 | 1 | 目录脚手架 + 源码目录确认 |
| Phase 1: R+I | Task 2-4 | 3 | 核心模块事实采集 + 扩展模块事实采集 + 架构洞察 |
| Phase 2: E | Task 5-10 | 6 | references(2批) + concepts(3批) + examples + indexes |
| Phase 3: V | Task 11 | 1 | 全bundle验证修复 |
| Phase 4: Index | Task 12 | 1 | PyData分类索引更新 |
| Phase 5: Review | Task 13 | 1 | 独立审查 |
| **Total** | | **13** | |
