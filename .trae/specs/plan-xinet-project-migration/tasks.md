# Tasks

> 本 spec 处于**规划阶段**，下列任务的产出是「迁移计划文档」中的对应章节，而非实际迁移操作。所有任务围绕「制定可执行的迁移计划」展开。

- [x] Task 1: 编制子项目迁移台账：对 9 个一级子项目逐一确认迁移决策与目标位置
  - [x] SubTask 1.1: 复用 `xinet-content-extraction-and-archiving` 的价值评估结论，填充各子项目价值等级
  - [x] SubTask 1.2: 评估各子项目技术栈独立性（是否自包含可运行）
  - [x] SubTask 1.3: 标注各子项目安全风险（明文密钥、嵌套仓库、环境特定）
  - [x] SubTask 1.4: 综合三维度给出迁移决策（迁移/归档/丢弃）与目标位置及理由

- [x] Task 2: 制定迁移分类标准与决策规则
  - [x] SubTask 2.1: 定义价值/独立性/安全风险三维分类维度
  - [x] SubTask 2.2: 定义三维度到迁移决策的映射规则
  - [x] SubTask 2.3: 对照 `.agents/protocols/app-development-workflow.md` 校验目标位置合规性

- [x] Task 3: 制定迁移顺序与依赖关系图
  - [x] SubTask 3.1: 按「安全治理优先 → 应用迁移 → 归档丢弃」排序
  - [x] SubTask 3.2: 用 Mermaid 绘制阶段依赖关系图
  - [x] SubTask 3.3: 标注可并行执行的迁移任务

- [x] Task 4: 制定兼容性处理方案
  - [x] SubTask 4.1: 嵌套 Git 仓库剥离方案（37 个 `.git/` 的处理策略）
  - [x] SubTask 4.2: 明文密钥外置方案（WeChat、AI 的密钥替换为环境变量 + `.env.example`）
  - [x] SubTask 4.3: 双 AI 指引文档冲突消解方案（CLAUDE.md / CODEBUDDY.md 的 SSOT 处理）
  - [x] SubTask 4.4: 命名规范对齐方案（目录名转 kebab-case 的映射表）

- [x] Task 5: 制定潜在风险评估与应对措施
  - [x] SubTask 5.1: 识别误删、依赖断裂、密钥泄露、路径硬编码四类风险
  - [x] SubTask 5.2: 为每类风险制定缓解措施与回退方案
  - [x] SubTask 5.3: 制定迁移前后的验证检查点

- [x] Task 6: 编制分阶段迁移计划（五阶段）
  - [x] SubTask 6.1: 阶段一「勘察与台账确认」目标/步骤/产出/验收标准
  - [x] SubTask 6.2: 阶段二「安全治理」目标/步骤/产出/验收标准
  - [x] SubTask 6.3: 阶段三「应用迁移」目标/步骤/产出/验收标准
  - [x] SubTask 6.4: 阶段四「归档与丢弃」目标/步骤/产出/验收标准
  - [x] SubTask 6.5: 阶段五「验证与清理」目标/步骤/产出/验收标准

- [x] Task 7: 整合并输出完整迁移计划文档
  - [x] SubTask 7.1: 将台账、分类、顺序、兼容性、风险、阶段计划整合为单一计划文档
  - [x] SubTask 7.2: 校验文档与 spec.md 需求逐条对齐
  - [x] SubTask 7.3: 对照 checklist.md 逐项自检

# Task Dependencies

- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 1
- Task 5 depends on Task 1
- Task 6 depends on Task 3, Task 4, Task 5
- Task 7 depends on Task 6
