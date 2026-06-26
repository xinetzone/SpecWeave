# xinet 沙箱多项目迁移计划 Spec

## Why

`d:\AI\.temp\.chaos\tests\xinet` 是一个未经治理的混沌测试沙箱，聚合了 9 个互不相关的一级子项目、37 个嵌套 Git 仓库、双份矛盾的 AI 指引文档与多处明文密钥泄露。此前的 `xinet-content-extraction-and-archiving` spec 已完成「内容价值评估与元数据归档」（仅建立索引，未实际迁移文件）。

本 spec 的目标不同——它要在前期评估结论之上，制定一份**可执行的迁移落地计划**：把沙箱中具有保留价值的子项目，按项目治理规范（`.agents/protocols/app-development-workflow.md`）实际迁移到目标位置（`apps/` / `docs/`），消除安全风险，并明确各阶段目标、实施步骤与验收标准。本 spec 处于规划阶段，仅产出迁移计划文档，不在本阶段执行任何文件迁移。

## What Changes

- 建立 xinet 子项目迁移台账：对 9 个一级子项目逐一确定「迁移决策」（迁移 / 归档 / 丢弃）与「目标位置」
- 制定迁移分类标准：按价值等级、技术栈独立性、安全风险三维度对子项目分类
- 制定迁移顺序与依赖关系：按风险优先级与依赖拓扑排序，先安全治理后内容迁移
- 制定兼容性处理方案：嵌套 Git 仓库剥离、明文密钥外置、双 AI 指引文档冲突消解、命名规范对齐
- 制定潜在风险评估与应对措施：误删、依赖断裂、密钥泄露、路径硬编码等风险的识别与缓解
- 生成完整迁移计划文档：明确五个阶段的目标、步骤、产出与验收标准
- **本 spec 仅产出规划文档，不执行实际迁移**（迁移执行属于后续独立 spec）

## Impact

- Affected specs:
  - `xinet-content-extraction-and-archiving`（前置依赖，提供价值评估结论与归档索引）
- Affected code:
  - `apps/`（迁移目标位置，新增子目录候选：blog、wechat-publisher 等）
  - `docs/retrospective/archives/xinet/`（迁移决策记录补充）
  - `.agents/protocols/app-development-workflow.md`（迁移流程依据，不修改）
- Affected files（仅作为分析与规划对象，本阶段不修改）:
  - `d:\AI\.temp\.chaos\tests\xinet\` 下的 9 个子项目目录

## 子项目现状清单（分析结论）

| 子项目 | 技术栈 | 独立性 | 价值 | 安全风险 | 迁移倾向 |
|---|---|---|---|---|---|
| `blog/` | Vue3 + Express + TS | 高（自包含全栈应用） | 中高 | 低 | 迁移至 `apps/` |
| `WeChat/` | Python（公众号发布工具） | 高 | 中高 | 高（明文密钥/凭证） | 脱敏后迁移至 `apps/` |
| `Dao/` | TS monorepo（哲学框架） | 中（仅 README+空壳） | 低 | 低 | 归档（实体不完整） |
| `cli/` | Python + TS（skillhub CLI） | 中 | 中 | 中（硬编码 URL） | 归档/参考 |
| `AI/` | PowerShell 脚本（API 调用） | 低 | 低 | 高（明文 code/token） | 脱敏后归档 |
| `links/` | 工作区配置 + ClawWork 角色 | 低（环境特定） | 低 | 低 | 丢弃/归档 |
| `spaces/` | 多个嵌套 Git 仓库（tao/daoApps） | 低（嵌套仓库混杂） | 低 | 中 | 归档（剥离嵌套仓库） |
| `main.ipynb` | Jupyter 测试占位 | 低 | 低 | 低 | 丢弃 |
| `tests/` | 测试占位 | 低 | 低 | 低 | 丢弃 |

## ADDED Requirements

### Requirement: 子项目迁移台账

迁移计划应为每个一级子项目建立迁移台账，明确迁移决策与目标位置。

#### Scenario: 台账完整覆盖
- **WHEN** 查看迁移计划文档
- **THEN** 台账包含全部 9 个一级子项目（blog、WeChat、Dao、cli、AI、links、spaces、main.ipynb、tests）
- **AND** 每个子项目标注迁移决策（迁移 / 归档 / 丢弃）、目标位置、决策理由

### Requirement: 迁移分类标准

迁移计划应建立子项目分类标准，用于判定迁移决策。

#### Scenario: 分类维度明确
- **WHEN** 对子项目进行分类
- **THEN** 采用以下三个维度：
  - **价值等级**：复用前期 `xinet-content-extraction-and-archiving` 的高/中/低评估结论
  - **技术栈独立性**：是否为自包含、可独立运行的应用
  - **安全风险**：是否包含明文密钥、凭证、嵌套仓库等风险项

#### Scenario: 决策规则可执行
- **WHEN** 综合三维度评估后
- **THEN** 决策遵循以下规则：
  - 高价值 + 独立 + 风险可控 → **迁移至 `apps/`**
  - 中价值或不完整但有参考价值 → **归档至 `docs/retrospective/archives/xinet/`**
  - 低价值 + 占位/环境特定 → **丢弃（仅记录，不保留）**

### Requirement: 迁移顺序与依赖关系

迁移计划应定义迁移执行顺序，按风险优先级与依赖拓扑排序。

#### Scenario: 顺序遵循安全优先
- **WHEN** 查看迁移顺序
- **THEN** 执行顺序为：
  1. 安全治理（密钥外置、敏感文件清理）先于任何内容迁移
  2. 独立应用（blog、WeChat）迁移先于归档操作
  3. 归档与丢弃操作最后执行
- **AND** 标注各步骤间的依赖关系

### Requirement: 兼容性处理方案

迁移计划应针对沙箱的四类熵增问题提供兼容性处理方案。

#### Scenario: 嵌套 Git 仓库处理
- **WHEN** 迁移含嵌套 `.git/` 的子项目
- **THEN** 方案规定：剥离嵌套 `.git/` 目录，使迁移后的内容纳入主仓库版本控制，不携带子仓库历史

#### Scenario: 明文密钥处理
- **WHEN** 迁移含明文密钥的子项目（WeChat、AI）
- **THEN** 方案规定：密钥替换为环境变量占位符，提供 `.env.example` 模板，敏感文件加入 `.gitignore`

#### Scenario: 双 AI 指引文档冲突处理
- **WHEN** 迁移含矛盾指引文档（CLAUDE.md / CODEBUDDY.md）的内容
- **THEN** 方案规定：确立单一 SSOT 指引，矛盾文档不随迁移携带或合并为单一来源

#### Scenario: 命名规范对齐
- **WHEN** 子项目迁移至 `apps/`
- **THEN** 目录名转换为 kebab-case（如 `WeChat` → `wechat-publisher`、`blog` → `tech-blog`）

### Requirement: 潜在风险评估与应对

迁移计划应识别迁移过程中的潜在风险并提供应对措施。

#### Scenario: 风险清单完整
- **WHEN** 查看风险评估章节
- **THEN** 至少覆盖以下风险及对应缓解措施：
  - **误删风险**：源文件采用「先复制后验证再清理」而非直接移动
  - **依赖断裂风险**：迁移前验证依赖声明完整性（package.json/requirements.txt）
  - **密钥泄露风险**：迁移前执行敏感信息扫描，外置后再纳入版本控制
  - **路径硬编码风险**：迁移后检查并修正指向 `.temp/` 的硬编码路径

### Requirement: 分阶段迁移计划

迁移计划应划分清晰的执行阶段，每阶段有明确目标、步骤、产出与验收标准。

#### Scenario: 阶段结构完整
- **WHEN** 查看迁移计划文档
- **THEN** 包含五个阶段，每阶段说明：阶段目标、实施步骤、关键产出、验收标准
  - **阶段一：勘察与台账确认**（确认子项目台账与迁移决策）
  - **阶段二：安全治理**（密钥外置、敏感文件清理）
  - **阶段三：应用迁移**（blog、WeChat 迁移至 `apps/`）
  - **阶段四：归档与丢弃**（剩余子项目归档或记录丢弃）
  - **阶段五：验证与清理**（迁移后验证、索引同步、沙箱清理）

#### Scenario: 验收标准可度量
- **WHEN** 查看各阶段验收标准
- **THEN** 验收标准以可验证条件表述（如「`apps/tech-blog/` 下 README 与依赖声明齐全」「无明文密钥残留」「`apps/README.md` 索引已同步」）

### Requirement: 规划阶段边界

本 spec 处于规划阶段，仅产出迁移计划文档，不执行实际迁移。

#### Scenario: 不执行迁移操作
- **WHEN** 本 spec 完成
- **THEN** 仅生成 spec.md、tasks.md、checklist.md 三份规划文档
- **AND** 不在 `xinet` 源目录或 `apps/`、`docs/` 目标位置进行任何文件迁移、删除或修改
