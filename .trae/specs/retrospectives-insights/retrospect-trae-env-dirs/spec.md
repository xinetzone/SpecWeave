# Trae 双版本环境目录全面复盘（.trae vs .trae-cn）Spec

## Why

`external/dao/xinzo/.trae`（国际版）与 `external/dao/xinzo/.trae-cn`（国内版）是用户两套 Trae IDE 个人环境目录，长期独立演化，存在技能集漂移、配置不一致与潜在安全隐患（如 `trae-jwt-token` 明文存放）。需要一次系统性复盘：还原事实（R）→ 洞察根因（I）→ 萃取可复用治理模式（E）→ 导出报告，为后续环境收敛/同步治理提供依据。

## 内容敏感度判定

- **级别：私域内容（Private）**——分析对象含个人凭证（trae-jwt-token）、user_profile、记忆数据
- **工作流**：规划文档按用户显式 `/spec` 指令存放于 `.trae/specs/retrospectives-insights/retrospect-trae-env-dirs/`；最终报告产出物存放 `playground/reports/`，不入 `docs/`，不提交 git
- **脱敏约束**：报告与所有中间产物中禁止出现 token/凭证的实际值，仅可记录文件存在性与路径

## What Changes

- 新增 R 阶段事实登记（两目录结构、skills 清单、配置文件、版本、memory/cleanup 记录）
- 新增 I 阶段洞察（四元组：现象+根因+影响+建议），主线：双版漂移、技能冗余、配置安全、治理机会
- 新增 E 阶段可复用模式（触发条件+核心步骤+反模式+迁移验证）
- 导出复盘报告至 `playground/reports/trae-env-retrospective-20260901/README.md`（Markdown，frontmatter 含 source 溯源）
- 不修改两个被分析目录中的任何文件（只读分析）

## Impact

- Affected specs: 无（新建独立 spec）
- Affected code: 无代码变更；仅新增分析产物
- 产出物位置：
  - 中间产物：`.trae/specs/retrospectives-insights/retrospect-trae-env-dirs/`（facts.md、insights.md、patterns.md）
  - 最终报告：`playground/reports/trae-env-retrospective-20260901/README.md`

## ADDED Requirements

### Requirement: 方法论链路（场景4 知识沉淀）
系统 SHALL 按 seven-concepts-cmd 场景4 链路 R→I→E 执行，每阶段通过对应质量门（G1/G2/G3），并输出 CMD-LOG（session 前缀 `sc-20260901-trae-env`）。

#### Scenario: R 阶段事实采集
- **WHEN** 对 `.trae` 与 `.trae-cn` 执行结构盘点
- **THEN** 产出 facts.md，含两目录顶层结构、skills 全量清单（含各自独有/共有标记）、配置文件清单、版本信息、memory 与 cleanup 记录，且无因果推断词（G1）

#### Scenario: I 阶段洞察
- **WHEN** 基于事实登记执行对比分析
- **THEN** 产出 insights.md，每条洞察含四元组（现象+根因+影响+建议），覆盖漂移/冗余/安全/治理四主线（G2）

#### Scenario: E 阶段萃取
- **WHEN** 基于洞察提炼模式
- **THEN** 产出 patterns.md，每个模式含触发场景+核心步骤+反模式+迁移验证（G3）

#### Scenario: 报告导出
- **WHEN** 三阶段完成且质量门通过
- **THEN** 汇总报告写入 `playground/reports/trae-env-retrospective-20260901/README.md`，frontmatter 含 `source` 字段，正文不含任何凭证值

### Requirement: 只读分析
系统 SHALL 不修改 `external/dao/xinzo/.trae` 与 `external/dao/xinzo/.trae-cn` 下任何文件。

#### Scenario: 分析过程零写入
- **WHEN** 执行 R/I/E 任一阶段
- **THEN** 两个被分析目录的文件内容与修改时间保持不变
