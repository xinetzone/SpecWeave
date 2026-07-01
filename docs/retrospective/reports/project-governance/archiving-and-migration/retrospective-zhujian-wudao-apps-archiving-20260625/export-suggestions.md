---
id: "retrospective-zhujian-wudao-apps-archiving-20260625-export"
source: "retrospective-zhujian-wudao-apps-archiving-20260625/README.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/project-governance/archiving-and-migration/retrospective-zhujian-wudao-apps-archiving-20260625/export-suggestions.toml"
---
# 导出建议 — 竹简悟道归档至 apps/

## 一、行动项清单

### P0 — 立即执行（本次任务已完成）

| # | 行动项 | 状态 | 验证方式 |
|---|--------|------|---------|
| 1 | 创建 `apps/zhujian-wudao/` 目录 | ✅ 完成 | 目录存在 |
| 2 | 迁移 HTML Demo 与报名帖 | ✅ 完成 | 3 文件齐全 |
| 3 | 编写应用 README.md | ✅ 完成 | 文件可读 |
| 4 | 更新 apps/README.md §2.3 应用清单 | ✅ 完成 | 索引可见 |

### P1 — 短期跟进（1 周内）

| # | 行动项 | 责任 | 说明 |
|---|--------|------|------|
| 5 | Git 提交归档变更 | developer | 提交 `apps/zhujian-wudao/` 新增与 `apps/README.md` 修改，遵循 Conventional Commits：`feat(apps): 归档竹简悟道参赛作品至 apps/zhujian-wudao/` |
| 6 | 提交本次复盘报告 | developer | 提交 `docs/retrospective/reports/project-governance/retrospective-zhujian-wudao-apps-archiving-20260625/` 4 文件 |
| 7 | 运行归类验证脚本 | developer | 执行 `.agents/scripts/check-report-categorization.py` 确认新报告已正确归类 |

### P2 — 中期优化（1 个月内）

| # | 行动项 | 责任 | 说明 |
|---|--------|------|------|
| 8 | 补充 app-development-workflow.md 选择性归档子流程 | architect | 在协议中新增「选择性归档」场景，明确门禁跳过规则（详见 INS-03） |
| 9 | 评估竹简悟道完整资产归档价值 | architect | 评估 `.temp/AI/.agents/` 下规格文档、洞察库（62 条）是否归档至 `apps/zhujian-wudao/docs/` |
| 10 | 开发 apps/ 索引自动生成脚本 | developer | 类似 `generate-nav.py`，自动扫描 `apps/` 子目录生成 §2.3 应用清单 |

### P3 — 长期规划（3 个月内）

| # | 行动项 | 责任 | 说明 |
|---|--------|------|------|
| 11 | 建立归档前自包含验证工具 | developer | 封装 INS-02 的 Grep 验证为可复用脚本，检测 HTML/MD 外部依赖 |
| 12 | 参赛作品归档工作流模板化 | architect | 将本次方法论提炼为可复用模板，纳入 `docs/retrospective/patterns/` |

---

## 二、可复用方法论

### 方法论 1：参赛作品归档工作流（5 步法）

```
S1 规范读取 → S2 依赖验证 → S3 目录创建与文件迁移 → S4 应用 README → S5 索引同步
```

| 步骤 | 输入 | 输出 | 耗时占比 |
|------|------|------|---------|
| S1 规范读取 | AGENTS.md + app-development-workflow.md + apps/README.md | 上下文建立 | 40% |
| S2 依赖验证 | 源文件 | 自包含性确认 | 15% |
| S3 目录与迁移 | 文件清单 | apps/ 子目录 + 文件 | 15% |
| S4 应用 README | 报名帖/规格文档 | README.md | 20% |
| S5 索引同步 | apps/README.md | 更新后的索引 | 10% |

**复用条件**：
- 归档对象为参赛交付物（HTML Demo + 报名帖/说明文档）
- 源文件位于 `.temp/` 暂存区
- 目标为 `apps/` 正式目录

### 方法论 2：自包含验证模式

```regex
# HTML 自包含验证
(href|src)=["']\.agents|\.css|\.js["']

# Markdown 本地图片验证
!\[.*\]\(\./
```

**使用时机**：迁移任何含资源引用的文件前。

### 方法论 3：工作流协议的骨架与门禁分离

```
完整协议 = 流程骨架（必选）+ 质量门禁（按场景）
```

- 流程骨架：迁移前检查 → 执行迁移 → 更新索引 → 验证 → 清理
- 质量门禁：测试 / 审查 / 缺陷 / 文档（参赛场景可跳过）

---

## 三、风险预警

### 风险 1：`.temp/AI/` 残留文件长期未清理

**现象**：`.temp/AI/` 下仍保留 `竹简悟道.html`、`竹简悟道_展示页.html`、`.agents/` 子目录等中间产物。

**风险**：
- `.temp/` 为暂存区，长期堆积中间产物会导致暂存区膨胀
- 不同版本 HTML 共存可能引发混淆（哪个是定稿？）

**建议**：
- 短期：在 `apps/zhujian-wudao/README.md` 中明确标注「完整版」为定稿版本
- 中期：评估 `.temp/AI/.agents/` 下洞察库等资产的归档价值（详见 P2-9）
- 长期：`.temp/AI/` 整体清理或归档至 `.temp/_archived/`

### 风险 2：应用 README 内容来源单一

**现象**：`apps/zhujian-wudao/README.md` 主要基于报名帖内容提炼，未引入产品规格、洞察库等深度内容。

**风险**：作为长期项目资产，README 信息密度不足，未来维护者难以理解产品全貌。

**缓解**：P2-9 评估完整资产归档时，同步扩充 README 或建立 `apps/zhujian-wudao/docs/` 子目录。

### 风险 3：中文文件名的跨平台兼容性

**现象**：`竹简悟道_完整版.html`、`报名帖_竹简悟道.md` 使用中文 + 下划线命名。

**风险**：
- 部分工具链（如某些 CI/CD 系统）对非 ASCII 文件名支持不佳
- 下划线命名不符合 kebab-case 约定（但项目仅强制目录命名 kebab-case）

**缓解**：
- 当前保留原名（语义价值 > 规范一致性）
- 若未来出现工具链兼容问题，可考虑软链接或重命名

---

## 四、后续跟进事项

| 事项 | 触发条件 | 负责角色 |
|------|---------|---------|
| Git 提交归档变更 | 用户确认本次归档结果 | developer |
| 归类验证脚本执行 | 本次复盘报告创建后 | developer |
| 协议补丁评估 | 下次面临选择性归档场景时 | architect |
| 完整资产归档评估 | 竹简悟道参赛结束后 | architect |
| apps/ 索引自动化 | apps/ 下应用数 ≥ 3 时 | developer |

---

## 五、知识资产导出

### 本次任务产出的知识资产

| 资产类型 | 资产名称 | 存储位置 | 成熟度 |
|---------|---------|---------|--------|
| 流程模式 | 选择性归档模式 | 本报告 insight-extraction.md INS-01 | L2 |
| 技术模式 | 自包含验证前置模式 | 本报告 insight-extraction.md INS-02 | L3 |
| 治理模式 | 工作流协议骨架与门禁分离原则 | 本报告 insight-extraction.md INS-03 | L3 |
| 文档模式 | 索引同步的「首个应用」破冰原则 | 本报告 insight-extraction.md INS-04 | L2 |
| 方法论 | 参赛作品归档工作流（5 步法） | 本报告 insight-extraction.md | L2 |

### 建议入库路径

| 资产 | 当前位置 | 建议目标 | 入库条件 |
|------|---------|---------|---------|
| INS-02 自包含验证模式 | 本报告 | `docs/retrospective/patterns/` | L3 已达入库标准 |
| INS-03 骨架与门禁分离原则 | 本报告 | `docs/retrospective/patterns/` | L3 已达入库标准 |
| 参赛作品归档方法论 | 本报告 | `docs/retrospective/patterns/methodology-patterns/` | 经第 2 次验证后入库 |
