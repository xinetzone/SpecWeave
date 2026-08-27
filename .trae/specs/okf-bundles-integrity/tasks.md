# OKF知识包完整性修复 - The Implementation Plan

## [ ] Task 1: 修复 think/psi 域的内部交叉引用（Pattern B）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 修复 psi-core、psi-math、psi-universe、godgpt 四个子bundle之间互相引用的路径
  - 当前错误：使用 `/psi-core/...`、`/psi-math/...` 等被解析为当前目录下的子目录
  - 正确路径：需要从当前文件位置计算到目标bundle的正确相对路径（如 `../psi-core/...`）
- **Acceptance Criteria Addressed**: [FR-2, AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: 修复后运行链接检查，think/psi/目录下无断链
  - `human-judgement` TR-1.2: 抽查5个修复后的链接，确认路径计算正确

## [ ] Task 2: 修复 viz/3b1b 域的内部引用（Pattern C）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 修复 viz/3b1b/videos 下引用 manim 知识包的路径
  - 当前错误：`/viz/3b1b/manim/...` 被解析为 videos/viz/3b1b/manim/...
  - 正确路径：`../manim/...`
  - 同时修复 videos/spec/insights.md 中的 `../manim/spec/insights.md` 路径
- **Acceptance Criteria Addressed**: [FR-3, AC-1]
- **Test Requirements**:
  - `programmatic` TR-2.1: 修复后viz/3b1b/目录下无断链

## [ ] Task 3: 修复 document/sphinx 域的内部引用（Pattern A+C）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 修复 sphinx-argparse 下所有 `/concepts/...`、`/examples/...`、`/references/...` 链接
  - 正确路径：相对于 sphinx-argparse 根目录，即去掉开头的 `/` 或使用正确相对路径
  - 修复 alabaster 下 `/document/sphinx/...`、`/build/...` 链接，计算正确相对路径
- **Acceptance Criteria Addressed**: [FR-1, FR-3, AC-1]
- **Test Requirements**:
  - `programmatic` TR-3.1: 修复后document/sphinx/目录下无断链

## [ ] Task 4: 修复零散单域错误（Pattern E+其他）
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 修复 python/cpython/concepts/07-bytecode-execution.md 中的 `05-garbage-collection.md` 路径
  - 修复 meta/okf-spec 下的错误链接（format-overview.md、okf-spec.md、attested-computations.md、脚注误判）
  - 修复 document/jupyter/index.md 中的 jupyter-client 引用
  - 修复其他零散的单个文件错误
- **Acceptance Criteria Addressed**: [FR-5, FR-6, AC-1]
- **Test Requirements**:
  - `programmatic` TR-4.1: 上述单个文件的断链全部修复

## [ ] Task 5: 处理 think/laozi 无效引用（Pattern D）
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 处理 think/laozi 下指向不存在的 `SpecWeave/bundles/laozi-lineage/` 的引用
  - 由于laozi-lineage当前不存在于bundles中，暂时将这些链接注释掉或改为纯文本
- **Acceptance Criteria Addressed**: [FR-4, AC-1]
- **Test Requirements**:
  - `programmatic` TR-5.1: think/laozi/目录下无断链

## [ ] Task 6: 使用链接修复工具自动处理可修复问题
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 先dry-run运行 `python .agents/scripts/check-links.py --fix --dry-run --path projects/awesome-okf-xs/doc/bundles`
  - 确认预览结果正确后执行自动修复
  - 自动修复能处理：绝对路径转相对、层级校正、斜杠补全
- **Acceptance Criteria Addressed**: [FR-1, AC-1]
- **Test Requirements**:
  - `programmatic` TR-6.1: 自动修复后再次运行检查，断链数量大幅减少

## [ ] Task 7: 手动修复剩余断链并验证
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 自动修复后剩余的断链需要手动逐一处理
  - 重新运行链接检查，直到本地断链数为0
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-7.1: 本地断链数为0
  - `programmatic` TR-7.2: toctree检查通过
  - `programmatic` TR-7.3: UTF-8检查通过

## [ ] Task 8: 最终审查与质量门
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 人工抽查修复后的链接，确认语义正确
  - 检查git diff确认未修改非链接内容
- **Acceptance Criteria Addressed**: [AC-4, NFR-3, NFR-4]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 抽查20个链接，确认路径正确、文本未改
  - `human-judgement` TR-8.2: git diff仅包含链接URL修改，无其他内容变更
