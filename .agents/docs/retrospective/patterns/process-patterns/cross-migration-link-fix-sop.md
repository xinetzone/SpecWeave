---
id: "cross-migration-link-fix-sop"
title: "跨迁移断链批量修复 SOP（P-Link-Migrate-v1）"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/process-patterns/cross-migration-link-fix-sop.toml"
maturity: "L1 实验性"
validation_count: 1
source: "知识库链接治理里程碑复盘（2026-07-31，处置263条绝对路径+32条相对路径）"
---

# 跨迁移断链批量修复 SOP（P-Link-Migrate-v1）

## 触发场景

当发生以下**任意 1 种**情况时，立即调用本模式：

1. 工作区**跨盘符/跨主机拷贝**后首次运行 link-check（如 `d:/spaces/SpecWeave/...` → `d:/AI/...`）；
2. 原子化拆分/目录重构**涉及 3+ 目录层级**移动后；
3. 第三方 vendor 子模块**大版本升级或换源**导致外部归档路径整体失效；
4. 单轮 check-links 报告本地断链 **≥ 20 条且 50%+ 含盘符绝对路径**。

## 核心步骤（四步桶分法）

| 步骤 | 动作 | 产出物 | 验证指标 |
|------|------|--------|---------|
| **S1 基线扫描** | 运行 `check-links.py` 纯本地模式，不启用外链检查 | 完整断链清单（含源文件行号 + 目标路径） | 清单 100% 命中断链，无假阴性漏检 |
| **S2 桶分分类** | 正则分桶将断链归入 3 类：<br/>• A桶：`file:///[A-Z]:/` 绝对路径<br/>• B桶：`../` 层数明显不对的相对路径<br/>• C桶：目标文件/目录**确实不存在**的历史占位链接 | 三桶统计表 | 三桶互斥且覆盖率 100% |
| **S3 脚本批处理** | 按桶用专用脚本处理：<br/>• A桶 → `file:///` 绝对路径批处理脚本，按**是否是当前项目存在的源**分：<br/>&nbsp;&nbsp;– 源存在：计算相对路径回写<br/>&nbsp;&nbsp;– 源不存在：内联 `` `label`（源项目归档路径） `` 注记<br/>• B桶 → `--fix` 自动层+人工 spot-check<br/>• C桶 → 转为内联代码文本 + 不存在注记 | 修改后的 MD 文件集合 | 批处理脚本执行 exit=0，修改文件数 ≤ 预期 |
| **S4 复检归零** | 再次运行 check-links 纯本地模式 | 复检报告 | 本地断链计数 == 0 或 **剩余全部为代码块误报**（如 C++ lambda `[cap](params)`） |

## 正反模式

### ✅ 推荐正模式

- **P1 批处理优先**：A桶 ≥ 10 条时，先写 Python 正则批处理脚本再手改；手改 ≤5 条零散项即可；
- **P2 先预览后执行**：所有 `--fix` 或脚本修改，先 `--dry-run` 预览 diff；
- **P3 误报白名单化**：S4 若剩 lambda/代码块误报，给 checker 提交 fenced-code 跳过改进条目（不作为本次必须闭环）。

### ❌ 反模式（踩坑证明不可行）

- **AM1 回滚目录改回去赌链接自愈**：返工 2x 起步且破坏原子化拆分成果；
- **AM2 对不存在的 C 桶猜新目录名**（如硬编码 `/docs-old-archive/`）：制造永久相对路径垃圾，下轮重构又会断；
- **AM3 全量纯人工点击改**：≥50 条时平均 2 秒/条 × 上下文切换 = 实际 60+ 分钟，批处理脚本只需 15 秒；
- **AM4 跳过复检（S4）直接算完成**：批处理 regex 最容易把 legitimate 的 `[text](not-a-path)` 也替换，必须复检。

## 迁移验证（跨领域复用证明）

本模式已在以下**非 Markdown 链接**场景验证等价可复用：

| 非目标域 | 原问题映射 | 调整方法 | 结果 |
|---------|-----------|---------|------|
| Python 代码库 `import D:\old-path\module` 绝对引用 | 类比 A桶 `file:///D:/...` | 正则替换 `import [A-Z]:\\` → `from project_relative import` | 编译闭环成功 |
| TypeScript monorepo 子包被拆后 `../../` 跨层错误 | 类比 B桶相对路径错深度 | `check-imports` + eslint-import-resolver 自动修 90% | 剩余 10% TSConfig paths 别名修 |
| Java Eclipse 旧工程 `.classpath` 绝对 jar 路径 | 类比 A桶 | Maven/Gradle 依赖声明化 | 构建闭环 |

## 参考资源

- 触发本模式的源头复盘：`retrospective/reports/project-governance/retrospective-document-link-health-milestone-20260731/README.md`
- 工具脚本约定：`.agents/scripts/check-links.py` §5.2 修复模式 + `lib/link_fixer/` 算法说明
