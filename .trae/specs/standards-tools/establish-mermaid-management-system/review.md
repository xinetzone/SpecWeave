---
version: "1.0"
last_updated: "2026-06-30"
theme: "standards-tools"
spec_type: "feature-addition"
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/establish-mermaid-management-system/checklist.toml"
---
# Mermaid 图表管理体系 - Verification Checklist

## 一、核心功能验证

### 1. Mermaid 检查脚本增强
- [x] `_detect_diagram_type` 正确识别 "classDiagram" 和 "erDiagram" 声明
- [x] `_check_classDiagram` 正确检测空行、类名引号缺失、关系标签问题
- [x] `_fix_classDiagram` 自动修复空行、补全类名/关系标签双引号
- [x] `_check_erDiagram` 正确检测空行、实体名引号缺失、关系基数格式问题
- [x] `_fix_erDiagram` 自动修复空行、补全实体名双引号
- [x] 新检查器/修复器已在 DIAGRAM_CHECKERS/DIAGRAM_FIXERS 字典注册
- [x] 现有 flowchart/stateDiagram/sequenceDiagram 等功能无回归

### 2. 单元测试覆盖
- [x] test_checks_mermaid.py 包含 classDiagram 正反例测试（正确/错误/修复后）
- [x] test_checks_mermaid.py 包含 erDiagram 正反例测试（正确/错误/修复后）
- [x] 所有现有测试（37个）继续通过
- [x] 新增代码行覆盖率 ≥ 80%

### 3. Mermaid 指令集文档
- [x] commands/mermaid.md 存在且 TOML frontmatter 完整（id/category/source）
- [x] 包含触发条件、输入规范表、RACI责任分配矩阵
- [x] RACI矩阵符合三大强制规则（A唯一性、R≠A分离、双列设计）
- [x] 包含7个执行步骤（S0启动→S6归档）
- [x] 包含输出规范表、质量验收标准、约束条件
- [x] 包含CMD-LOG规范（cmd=mermaid、session前缀merm-、事件定义、日志示例）
- [x] 所有相对路径链接有效

### 4. mermaid-cmd Skill 门面
- [x] skills/mermaid-cmd/SKILL.md 存在且 YAML frontmatter 完整
- [x] 包含三层架构声明（L0→L1→L2）
- [x] description 包含完整触发词列表和"必须使用此技能"强制措辞
- [x] 包含3种方案选择（快速生成/检查修复/复杂图表协作）和决策树
- [x] Why解释 ≥ 2个，解释合理
- [x] 包含安全检查清单
- [x] CMD-LOG概要引用L2 cmd-log-specification.md，无重复内容
- [x] 关键参考表包含 layer 列
- [x] SKILL.md 行数 ≤ 500
- [x] check-skill-quality.py mermaid-cmd 检查全部通过
- [x] 所有相对路径链接有效

### 5. 角色能力绑定更新
- [x] architect.md 的 [bindings].skills 包含 "mermaid-cmd"
- [x] developer.md 的 [bindings].skills 包含 "mermaid-cmd"
- [x] reviewer.md 的 [bindings].skills 包含 "mermaid-cmd"
- [x] tester.md 的 [bindings].skills 包含 "mermaid-cmd"
- [x] 4个角色文件的 Responsibilities 部分补充了Mermaid相关职责
- [x] orchestrator.md 和 co-founder.md 未被修改
- [x] TOML frontmatter 格式正确可解析

### 6. team-mermaid 专项团队
- [x] teams/mermaid-team.md 存在且 TOML frontmatter 完整
- [x] teams/data/team-mermaid.yaml 存在且 YAML 语法正确可解析
- [x] 团队成员包含 architect/developer/reviewer/tester 4个角色
- [x] 治理范围明确（模板/检查脚本/安全规则/质量标准）
- [x] 定义3个标准工作流（简单生成/复杂协作/批量修复）
- [x] 成员职责与RACI矩阵一致
- [x] 所有相对路径链接有效

### 7. 索引与注册中心更新（L0-L2链）
- [x] ONBOARDING.md（L0）添加Mermaid能力速查条目，行数 ≤ 100
- [x] capability-registry.md（L1）添加mermaid命令集和mermaid-cmd Skill条目
- [x] capability-registry.md counts计数更新正确
- [x] AGENTS.md 指令集索引和上下文路由表添加mermaid条目
- [x] commands/README.md 指令集清单和RACI总览表添加mermaid
- [x] skills/README.md 命令集门面表格添加mermaid-cmd
- [x] teams/README.md 团队清单添加team-mermaid
- [x] L0→L1→L2引用链完整可追溯
- [x] 所有索引文件中路径与实际文件位置一致

### 8. CMD-LOG 规范更新
- [x] cmd-log-specification.md 适用范围表格添加mermaid行
- [x] Session ID格式规范表格添加mermaid行
- [x] 步骤编号规范表格添加mermaid列（S0-S6）
- [x] 添加7.6节"mermaid特有事件定义"
- [x] 提供2-3条mermaid典型日志示例
- [x] 日志示例格式可被现有正则表达式解析
- [x] 所有相对路径链接有效

## 二、架构合规性验证

### 渐进式披露三层架构
- [x] L0（ONBOARDING.md）：<100行速查，Mermaid条目简洁
- [x] L1（capability-registry.md、SKILL.md）：<500行，完整索引与门面
- [x] L2（commands/mermaid.md、cmd-log-specification.md）：详细规范文档
- [x] 无层间断裂（L1不重复L2详细内容，通过引用链接）

### 代码风格与规范一致性
- [x] 新增Python代码风格与现有mermaid.py一致（函数命名、错误消息、返回格式）
- [x] 新增Markdown文档遵循现有格式（TOML/YAML frontmatter、章节结构、中文注释）
- [x] 所有路径引用使用相对路径，无file:///绝对路径
- [x] 命名规范统一使用kebab-case

### RACI治理规范
- [x] commands/mermaid.md RACI矩阵中每项活动A唯一
- [x] L3执行操作层R≠A分离
- [x] 双列设计（活动+RACI）正确

## 三、安全与质量验证

### 链接有效性
- [x] check-links.py --path .agents/ 返回0断链
- [x] check-links.py --path .trae/specs/standards-tools/establish-mermaid-management-system/ 返回0断链

### 综合CI检查
- [x] ci-check.ps1 五项检查（filename/gitignore/mermaid/vendor/roles）全部通过
- [x] check-mermaid.py --path .agents/ --fix 对新文档Mermaid代码块无error级问题
- [x] check-role-permissions.py 通过
- [x] pytest 全部测试通过无失败

### 向后兼容性
- [x] 现有Mermaid模板文件未被修改
- [x] 现有check-mermaid.py入口脚本继续正常工作
- [x] vendor/目录无任何修改
- [x] 未新增npm/pip依赖

## 四、文档完整性验证

- [x] 所有新增Markdown文件包含TOML/YAML frontmatter
- [x] 关键规则后有"> **为什么？**"解释
- [x] Changelog章节格式正确（时间倒序，type/description）
- [x] 文档语言为中文，术语一致
- [x] 无空章节（空内容用"无"/"暂无"/"N/A"标记）
