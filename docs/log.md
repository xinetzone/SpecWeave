# 变更日志
## 2026-08-31

- docs 文档中心全量复盘行动项推进（session sc-20260831-docs-debt-remediation，源报告：retrospective/reports/concepts/milestone/docs-full-retrospective-20260831.md 第六章 ACT-1~ACT-6）
- ACT-1/ACT-2（P0）：移除 7 处 toctree 断链；fix-toctrees 四轮收敛（220 个 toctree 新建、343 个更新），未收录内容全部分流可达，check-toctrees 归零
- ACT-3（P1）：frontmatter 批量治理——53 处 Malformed YAML 修复、21 处剥离、98 个文件补 frontmatter、1506 个文件补 type 字段、1 处手工修复；check-frontmatter 归零（2695 个文件合规）
- ACT-4（P1）：retrospective 索引修复——index.md 板块表/使用建议/接入约定链接改指 concepts 层级；methodology-patterns 清单表去重 1 行、补登 5 个模式（终态 22 行）；milestone 报告表补录 4 份报告（终态 22 行）
- ACT-5（P1）：双文档体系边界治理——根 AGENTS.md 文档边界条款与知识库表修订、global-core-rules 路径解析规则重写（R1-R6）；新建 retrospective/cross-reference-ledger.md 收敛台账（基线 675/164 处，B1-B5 分批）并登记 toctree；R2 冻结生效，新增跨区引用数=0
- ACT-6（P2）：bp-nav-co-registration（生成-登记同步法，L1.5）入库终检通过——模式文件、concepts/index 表格与 toctree、主清单表、源报告 L138 交叉引用四处一致
- 门禁回归：check-toctrees / check-frontmatter / check-utf8 全部 exit=0（2696 个文件）

## 2026-08-22

- 初始 OKF v0.2 转换
