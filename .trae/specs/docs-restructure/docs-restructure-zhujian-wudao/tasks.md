# 竹简悟道文档结构重组 - 实施计划

## [x] Task 1: 备份原始文件并记录基线状态
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 记录所有7个文件的原始路径、文件大小、行数作为基线
  - 计算每个文件的内容哈希用于完整性验证
  - 备份原始文件到临时位置（可选，Git已有版本控制，可简化为记录基线信息）
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-1.1: 输出7个文件的原始路径、大小、行数统计表
  - `programmatic` TR-1.2: 记录每个文件的MD5/SHA256哈希值
- **Notes**: 使用 `Get-FileHash` PowerShell命令计算哈希

## [x] Task 2: 创建主题分类子目录结构
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 在 `apps/zhujian-wudao/.agents/docs/` 下创建4个子目录：
    - `product/` - 产品规格文档
    - `insights/` - 洞察库
    - `reviews/` - 复盘报告
    - `knowledge-transfer/` - 可迁移知识资产
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-2.1: 验证4个子目录均存在
  - `programmatic` TR-2.2: 验证新目录为空
- **Notes**: 使用 `New-Item -ItemType Directory -Force`

## [x] Task 3: 制定文件迁移与重命名映射表
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 明确每个文件的目标路径和新文件名：
    | 原文件 | 新路径 | 新文件名 |
    |--------|--------|----------|
    | `superpowers/specs/2026-06-17-zhujian-wudao-spec.md` | `product/` | `2026-06-17-product-spec.md` |
    | `superpowers/specs/2026-06-17-zhujian-wudao-insights-01-30.md` | `insights/` | `2026-06-17-insights-01-30.md` |
    | `superpowers/specs/2026-06-17-zhujian-wudao-insights-31-65.md` | `insights/` | `2026-06-17-insights-31-65.md` |
    | `superpowers/specs/2026-06-17-zhujian-wudao-review.md` | `reviews/` | `2026-06-17-project-review.md` |
    | `superpowers/specs/2026-06-17-zhujian-wudao-registration-review.md` | `reviews/` | `2026-06-17-registration-review.md` |
    | `superpowers/specs/2026-06-17-zhujian-wudao-transferable-methods.md` | `knowledge-transfer/` | `2026-06-17-transferable-methods.md` |
    | `superpowers/specs/2026-06-17-transferable-patterns.md` | `knowledge-transfer/` | `2026-06-17-transferable-patterns.md` |
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 检查映射表中所有文件名一致性
  - `human-judgement` TR-3.2: 确认冗余前缀移除合理（如 `zhujian-wudao-` 在子目录上下文中可简化）
- **Notes**: 文件名简化原则：子目录已表达分类，文件名中无需重复项目名前缀，保留日期+类型即可

## [x] Task 4: 执行文件迁移（复制到新位置）
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 将7个文件复制到新目录并重命名
  - 暂时保留旧位置文件（双写状态），待引用更新验证通过后再删除
  - 验证新位置文件大小和哈希与原始一致
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-4.1: 新位置7个文件大小与原始一致
  - `programmatic` TR-4.2: 新位置7个文件哈希与Task1基线一致
  - `programmatic` TR-4.3: 旧位置文件仍然存在（双写状态）
- **Notes**: 使用 `Copy-Item` 先复制，验证通过后再删除旧文件

## [x] Task 5: 更新所有文档内部的跨文件引用路径
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 分析所有Markdown链接，计算新的相对路径深度
  - 路径深度变化：原文件都在 `superpowers/specs/`，互相引用是同级路径（`filename.md`）；新结构需要跨目录引用：
    - product/ → insights/: `../insights/filename.md`
    - insights/ → product/: `../product/filename.md`
    - reviews/ → product/: `../product/filename.md`
    - reviews/ → insights/: `../insights/filename.md`
    - knowledge-transfer/ → 其他: `../{dir}/filename.md`
  - 更新以下文件中的引用：
    1. `product/2026-06-17-product-spec.md` - 引用insights
    2. `insights/2026-06-17-insights-01-30.md` - 引用spec和insights-31
    3. `insights/2026-06-17-insights-31-65.md` - 引用spec和insights-01
    4. `reviews/2026-06-17-project-review.md` - 引用spec、insights、transferable
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-5.1: 所有内部链接路径更新为正确的相对路径
  - `programmatic` TR-5.2: 无旧路径字符串残留
  - `human-judgement` TR-5.3: 抽查10个链接确认路径深度计算正确
- **Notes**: 注意同文件内锚点链接（`#Lxxx`）无需修改，只修改文件路径部分
- **完成情况**: 4个文件中共更新15处内部引用

## [x] Task 6: 更新外部引用文件（AGENTS.md 和 conventions.md等）
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 更新 `apps/zhujian-wudao/AGENTS.md`：
    - 文件地图树状目录中的路径
    - 路由索引表中的文件路径
  - 更新 `apps/zhujian-wudao/.agents/conventions.md`：
    - 设计文档存放路径说明
    - 交叉引用格式示例中的路径
  - 同时更新其他发现的外部引用文件：project.md、git.md、roles/philosopher.md、skills/下的文件
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-6.1: AGENTS.md中无旧路径 `superpowers/specs/`
  - `programmatic` TR-6.2: conventions.md中无旧路径
  - `human-judgement` TR-6.3: 路由表中每个路径指向正确的新位置
- **Notes**: 检查是否还有其他文件引用了旧路径（用Grep搜索）
- **完成情况**: 8个外部文件中共更新33处引用

## [x] Task 7: 创建 docs/README.md 索引导航文档
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 在 `apps/zhujian-wudao/.agents/docs/` 创建 README.md
  - 内容包括：
    - 文档体系说明
    - 完整目录树
    - 每个文件的用途、行数、内容简介
    - 快速查找表（按需求类型索引到对应文件）
    - 新增文档归类指南
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-7.1: README包含完整目录树
  - `human-judgement` TR-7.2: 每个文件有清晰的用途说明
  - `human-judgement` TR-7.3: 快速查找表覆盖常见需求场景
  - `human-judgement` TR-7.4: 新增文档归类指南明确

## [x] Task 8: 生成重组前后结构对比文档
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 在 `apps/zhujian-wudao/.agents/docs/` 创建 `restructure-comparison.md`
  - 内容包括：
    - 重组前结构树
    - 重组后结构树
    - 文件迁移映射表（原路径→新路径）
    - 重命名对照表
    - 引用变更统计（多少处链接被更新）
    - 重组日期与说明
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 对比文档结构完整
  - `human-judgement` TR-8.2: 迁移映射表7个文件全部覆盖
  - `programmatic` TR-8.3: 统计数据准确

## [x] Task 9: 验证所有链接有效性
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - 运行项目链接校验脚本或手动验证
  - 同时检查所有外部文件中的链接
  - 发现并修复额外断链（HTML文件路径、角色文件引用等）
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `programmatic` TR-9.1: 链接校验脚本运行无错误
  - `programmatic` TR-9.2: 0个断链
  - `human-judgement` TR-9.3: 手动抽查跨目录链接可正常跳转
- **完成情况**: 扫描29个Markdown文件、36个本地链接，额外修复3处断链，全部验证通过

## [x] Task 10: 删除旧文件并清理空目录
- **Priority**: high
- **Depends On**: Task 9
- **Description**: 
  - 删除 `superpowers/specs/` 下的7个旧文件
  - 删除空的 `superpowers/specs/` 目录
  - 如果 `superpowers/` 目录为空，一并删除
  - 验证新结构完整性
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-10.1: 旧位置文件已删除
  - `programmatic` TR-10.2: 空目录已清理
  - `programmatic` TR-10.3: 新结构7个文件+README+对比文档共9个文件存在

## [x] Task 11: 最终验证与完整性检查
- **Priority**: high
- **Depends On**: Task 10
- **Description**: 
  - 最终目录结构审计
  - 可扩展性评估：确认新增文档归类路径清晰
  - 确认无遗留旧路径引用
- **Acceptance Criteria Addressed**: [AC-2, AC-10]
- **Test Requirements**:
  - `programmatic` TR-11.1: 新结构文件完整
  - `programmatic` TR-11.2: 全项目Grep搜索无 `superpowers/specs` 残留（对比文档除外）
  - `human-judgement` TR-11.3: 可扩展性评估通过
