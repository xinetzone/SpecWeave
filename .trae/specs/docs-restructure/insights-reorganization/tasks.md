# 竹简悟道洞察库重组 - 实施计划

## [x] Task 1: 修复和优化第一个洞察文件 (01-30)
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 更新文件头部：移除动态行数/字节数统计，添加层级声明和关联文件引用，修正措辞
  - 优化模糊标题：洞察16（"架构"→"内容架构：八层模块化结构"）、洞察18（"架构"→"架构：竹简式UI原型的设计原则"）、洞察20（"命名"→"命名：帛书术语的中文命名原则"）
  - 确保所有洞察结构一致（来源+核心内容标记完整）
  - 清理头部中引用旧文件名的地方
- **Acceptance Criteria Addressed**: AC-3, AC-6, AC-7, AC-10
- **Test Requirements**:
  - `programmatic` TR-1.1: grep统计`^## 洞察`数量为30
  - `human-judgement` TR-1.2: 文件头部无行数/字节数统计，包含层级说明和关联文件
  - `human-judgement` TR-1.3: 洞察16/18/20标题为描述性标题
  - `human-judgement` TR-1.4: 所有30条洞察内容完整保留，无文字丢失
- **Notes**: 原文件 `2026-06-17-insights-01-30.md` 结构基本良好，主要是头部更新和标题优化

## [x] Task 2: 创建第二个洞察文件 - 哲学层 (31-53)
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 从原 `2026-06-17-insights-31-65.md` 中提取洞察31-53，写入新文件 `2026-06-17-insights-31-53.md`
  - 编写新文件头部：包含编号范围（31-53）、洞察数量（23条）、层级说明（哲学层·帛书核心概念与体道四法系统化）、关联文件声明
  - 修复洞察53的结构：添加`**来源**`和`**核心内容**`标记，添加`---`分隔符，子节标题从`##`改为`###`
  - 修复洞察50的子节标题层级（如存在`##`误用）
  - 清理提取范围内的临时统计块
  - 确保洞察49/51/52/53的七节结构使用`###`三级标题
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-7, AC-10, AC-11
- **Test Requirements**:
  - `programmatic` TR-2.1: grep统计`^## 洞察`数量为23
  - `programmatic` TR-2.2: grep `^## [一二三四五六七]、` 结果为0（无标题层级错误）
  - `programmatic` TR-2.3: 不存在临时统计块（58条/59条/60条标记）
  - `human-judgement` TR-2.4: 文件头部结构正确，无动态行数统计
  - `human-judgement` TR-2.5: 洞察53有标准结构（来源+核心内容+七节）
  - `human-judgement` TR-2.6: 23条洞察内容完整保留
- **Notes**: 洞察49（虚静内观系统化手册）是最长的单条洞察，确保七节内容完整提取

## [x] Task 3: 创建第三个洞察文件 - 元层 (54-68)
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 从原 `2026-06-17-insights-31-65.md` 中提取洞察54-68，写入新文件 `2026-06-17-insights-54-68.md`
  - 编写新文件头部：包含编号范围（54-68）、洞察数量（15条）、层级说明（元层·场景拓展与产品深化）、关联文件声明、说明洞察66对体道四法的补全
  - 修复洞察54-65的子节标题：从`##`改为`###`
  - 为缺少标准标记的洞察补充`**来源**：[§本文件]`和`**核心内容**：`标记
  - 清理临时统计块
  - 修复双分隔符问题（洞察66/67前多余的`---`）
  - 确保洞察66（柔弱不争系统化手册）的七节结构完整
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-7, AC-10, AC-11
- **Test Requirements**:
  - `programmatic` TR-3.1: grep统计`^## 洞察`数量为15
  - `programmatic` TR-3.2: grep `^## [一二三四五六七]、` 结果为0
  - `programmatic` TR-3.3: 不存在临时统计块
  - `programmatic` TR-3.4: 不存在连续`---\n---`双分隔符
  - `human-judgement` TR-3.5: 所有15条洞察有来源和核心内容标记
  - `human-judgement` TR-3.6: 文件头部结构正确，包含体道四法补全说明
  - `human-judgement` TR-3.7: 15条洞察内容完整保留
- **Notes**: 洞察54-65的子节标题普遍使用了错误的`##`级别，需要系统性修正

## [x] Task 4: 删除旧文件并更新目录索引
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**: 
  - 删除旧文件 `2026-06-17-insights-31-65.md`
  - 更新 `docs/README.md` 中的文件清单表：将`2026-06-17-insights-31-65.md`替换为`2026-06-17-insights-31-53.md`和`2026-06-17-insights-54-68.md`
  - 更新README中的目录树结构
  - 更新README中的快速查找表和文档分类指引中的引用
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `programmatic` TR-4.1: 旧文件 `2026-06-17-insights-31-65.md` 不存在
  - `human-judgement` TR-4.2: README中的文件清单包含3个insights文件，旧文件名不在其中
  - `human-judgement` TR-4.3: README目录树正确反映3文件结构
- **Notes**: 确保README中的行数统计也相应更新或移除

## [x] Task 5: 更新全项目交叉引用
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 搜索全项目中所有引用 `2026-06-17-insights-31-65.md` 的位置
  - 对每个引用，根据引用目标的洞察编号确定应指向哪个新文件：
    - 引用洞察1-30：保持指向 `2026-06-17-insights-01-30.md`
    - 引用洞察31-53：更新为 `2026-06-17-insights-31-53.md`
    - 引用洞察54-68：更新为 `2026-06-17-insights-54-68.md`
    - 泛化引用（如"洞察库"或"insights-31-65"无特定编号）：更新为3个文件列表
  - 需要更新的文件包括但不限于：AGENTS.md、conventions.md、project.md、README.md（已在Task4处理）、product-spec.md、2026-06-23-project-review-01.md、2026-06-24-project-review-02.md、architect.md、co-founder.md、developer.md、reviewer.md、build-zhujian-wudao.md、insight-manager.md
  - 同一文件内的自引用（如31-53文件内部引用洞察49）保持文件名不变
  - 对于引用了洞察31-65中特定洞察且行号锚点可能变化的，至少确保文件名正确
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-5.1: grep `insights-31-65` 在insights目录外的结果为0
  - `human-judgement` TR-5.2: 每个被更新的引用指向正确的文件（根据洞察编号判断）
  - `human-judgement` TR-5.3: insights文件内部的自引用文件名正确
- **Notes**: 这是涉及文件最多的任务，需要系统性搜索和逐个更新

## [x] Task 6: 验证文件大小均衡和完整性
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 统计3个文件的行数，确认无文件超过2000行
  - 统计3个文件中的洞察总数（应为30+23+15=68）
  - 检查所有洞察编号连续性（1-68无跳号）
  - 对比重组前后关键洞察的开头和结尾段落，确认无截断
- **Acceptance Criteria Addressed**: AC-2, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-6.1: wc -l 统计3个文件，每个≤2000行
  - `programmatic` TR-6.2: grep `^## 洞察[0-9]` 跨3个文件去重计数为68
  - `human-judgement` TR-6.3: 抽样检查洞察1/30/31/53/54/68的首尾段落完整
- **Notes**: 这是最终验证任务
