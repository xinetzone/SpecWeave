---
title: "第三期全面复盘行动项待办清单"
id: "retrospective-specweave-full-project-comprehensive-20260814-action-backlog"
date: "2026-08-14"
version: "1.0"
source: "report.md §五导出环节（A1-A6）+ §四洞察环节架构风险（S1-S4）+ 双角色对抗审查发现（S5-S6）+ 全量测试回归存量问题"
x-toml-ref: "../../../../../../../.meta/toml/.agents/docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-specweave-full-project-comprehensive-20260814/action-backlog.toml"
scenario: "C-comprehensive-20260814"
---

# 第三期全面复盘行动项待办清单

> 本文件归档 SpecWeave 第三期全面复盘（2026-07-06~08-14）产出的全部待执行行动项，含：复盘报告改进建议 A1-A6、架构师补充风险 S1-S6、全量测试回归发现的存量问题（T1-T4）。执行完成后在状态列更新并补充归档位置。

---

## 一、行动清单总览

| ID | 行动项 | 来源 | 优先级 | 状态 | Owner（RACI） |
|----|--------|------|:------:|------|--------------|
| A1 | 修复 3 个 pytest 收集错误（API 漂移/openpyxl/.Tests.py 文件名） | report.md §5.1 | **P0** | ⏳ 待规划 | developer + tester |
| A2 | SSOT 单一数据源制度化（.meta/toml + 统计脚本 + 校验门禁） | report.md §5.1 | **P0** | ⏳ 待规划 | architect |
| A3 | 多智能体并行安全边界规范（先量化冲突成本、定义成功率指标） | report.md §5.1 | **P0** | ⏳ 待规划 | orchestrator + architect |
| A4 | 断链自愈机制（check-links --fix 接入 pre-commit，dry-run+白名单） | report.md §5.1 | P1 | ⏳ 待规划 | developer |
| A5 | pip_install_group 跨变体复用（提取共享脚本，参数化） | report.md §5.1 | P1 | ⏳ 待规划 | developer |
| A6 | 测试覆盖率质量门（scripts/apps 两档，80%） | report.md §5.1 | P1 | ⏳ 待规划 | developer + tester |

## 二、架构风险补充项（Architect 审查 S1-S6）

| ID | 行动项 | 来源 | 优先级 | 状态 | 说明 |
|----|--------|------|:------:|------|------|
| S1 | vendor 子模块漂移治理（8 个中 7 个未 checkout，建立健康检查） | architect 评审 | **P0** | ⏳ 待规划 | 本轮已实测：仅 flexloop 就位，指针与内容不同步 |
| S2 | 单仓巨型化评审（pytest 收集 >300s，评估稀疏检出/apps 独立仓库） | architect 评审 | **P0** | ⏳ 待规划 | 本轮实测：全量收集 548s |
| S3 | pytest 收集性能专项（单文件 13-42s，定位 import 链瓶颈） | architect 评审 | **P0** | ⏳ 待规划 | 与 A1 捆绑，否则「CI 全量可跑」落空 |
| S4 | specs 生命周期管理（166 个规划目录 active/archived/superseded 标记） | architect 评审 | P1 | ⏳ 待规划 | 目录增长是扩散而非收敛 |
| S5 | 测试资产分布审计（64 测试文件全在 scripts，apps 层近零测试） | architect 评审 | P1 | ⏳ 待规划 | 明确 A6 覆盖率门禁作用域 |
| S6 | 环境可复现性（scripts 工具链无 pyproject/requirements） | architect 评审 | P1 | ⏳ 待规划 | 本轮已实证：pytest-benchmark/openpyxl 均缺失 |

## 三、全量测试回归存量问题（2026-08-14 实测）

| ID | 问题 | 根因 | 优先级 | 状态 |
|----|------|------|:------:|------|
| T1 | test_mp_forkserver_validation.py 5 errors | `ctx_name` fixture 从未定义（e69f0a14 引入时缺陷） | P1 | ⏳ 待规划 |
| T2 | test_check_sensitive_info.py 2 failed | Unix 路径检测断言（Windows 环境差异） | P2 | ⏳ 待规划 |
| T3 | test_check_academic_sources/test_error_tolerance/test_batch_cli/test_quality_utils 4 failed | 环境/性能断言/存量 skill 校验 | P2 | ⏳ 待规划 |
| T4 | 废弃 docs/ 壳遗留 29 文件未迁移（15 模式 + 14 里程碑报告） | 历史迁移未完成 + 新写入违规 | P1 | ⏳ 待规划 |

## 四、执行顺序建议

按依赖关系与 ROI 排序：

1. **A1 + S3（捆绑）**：修复 3 个收集错误 + 收集性能——打通 CI 全量测试的前提
2. **S1**：vendor 子模块健康检查——幻觉一致性风险最高
3. **A5**：pip 分组安装推广——纯重构、低风险、已验证模式
4. **T4**：废弃 docs 壳迁移——本次已迁移 2 个模式示范，剩余 29 文件同流程
5. **A2**：SSOT 制度化——先做「报告数字可复现」门禁
6. **A6 + S5**：覆盖率质量门 + 测试资产分布审计
7. **A4**：断链自愈——CI 检测先行，pre-commit --fix 后置
8. **A3**：并行安全边界——先量化冲突成本
9. **T1/T2/T3**：测试存量修复
10. **S2/S4**：架构级评审（单仓/生命周期）

---

## 相关资源索引

- **完整复盘报告**：[report.md](report.md)
- **对抗审查记录**：[report.md 第六章](report.md#六对抗审查记录v-阶段)
- **上期行动项归档**：[insight-action-backlog.md](../retrospective-specweave-full-lifecycle-20260705/insight-action-backlog.md)
- **可复用模式库**：[patterns/](../../../../patterns/README.md)

---

## Changelog

<!-- changelog -->
- 2026-08-14 | docs | v1.0 初始版本：归档第三期全面复盘全部行动项（A1-A6 + S1-S6 + T1-T4）
