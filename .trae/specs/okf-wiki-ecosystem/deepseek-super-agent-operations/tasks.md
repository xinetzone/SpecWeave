# DeepSeek Super-agent 安装与权限管理实施任务

## Task 1: 信源与编号事实登记
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**: 经规格批准后创建 source-manifest、facts、article-source、verification；原文逐段登记，继续核对实时官方价格与机器账号政策，记录 GitHub CLI 受阻而非猜测源码。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-1.1: 两份 F 编号集合相等、连续且唯一，verification 全覆盖；实际访问与单源项可查。
  - `rule` TR-1.2: 核验不同模型与时段口径，未读源码与未复现个案均有明确标记。

## Task 2: 知识地图与概念教程
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 写知识地图及概念页，拟为原型范围与身份、事件接收与放权、静默规则、任务停止与恢复、费用与支持边界；三条洞察与渐进授权模式保持推论等级。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rubric` TR-2.1: 覆盖度与可读性，scale 1-5；anchors 1=遗漏多个主题，3=主要主题覆盖但操作前提含混，5=六部分及文末限制完整且来源明确；threshold >=4；evidence 为章节映射与逐段比对。
  - `rule` TR-2.2: 三条四元组洞察完整，模式有适用边界、反模式与未验证迁移说明。

## Task 3: 学习示例与包内导航
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 原创整理安装前审阅、首个工单、观察到自动接单、静默与停止演练；不运行示例。各子目录索引和根 index 最后生成，log 记访问失败与方法论质量门。
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5
- **Test Requirements**:
  - `rubric` TR-3.1: 示例与前置条件，scale 1-5；anchors 1=无来源命令或假实测，3=步骤可理解但失败判据不足，5=步骤、来源、预期与失败处置齐备且不暗示生产保证；threshold >=4；evidence 为示例全文审查。
  - `rule` TR-3.2: 命令有 F 来源，不含真实账号或凭证；所有新增正文被包内 toctree 收录。

## Task 4: 共享索引接入与机械自验
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 回读 DeepSeek 分组、相关域与总索引，只接入本包并同步计数；运行子项目 toctree、UTF-8、计数门与范围链接检查，尝试文档构建。他方存量红项独立报告，不擅改。
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-4.1: 本包零断链、零孤立文档、UTF-8 无 BOM、元数据可解析，新增导航和计数符合当前真实状态。
  - `rule` TR-4.2: diff/status 显示无架构包或无关实现改动；工具不可用或全局存量红项有范围归因和替代验证证据。

## Task 5: 独立审查与交付
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 在任务自验完成后创建 review，由全新只读上下文复核 AC/TR，四视角审查事实、结构、读者与时效；发现固化为修复任务，修复后重审。交付教程入口与信源、限制和验证结果，不提交不推送。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 全部 AC/TR 有独立审查证据，最新 review 为 pass，无本任务可行动问题。
  - `rule` TR-5.2: flagged 状态与复核期限、未运行示例和源码未读限制一致；最终链接指向实际文件。
