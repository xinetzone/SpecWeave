# 变更日志
## 2026-09-01

- 文档中心统一迁移：`.agents/docs/` 全部内容迁入根 `docs/` 单文档中心（spec：`.trae/specs/agents-docs-migration/`，session sc-20260901-agents-docs-migration-resume）
- 迁移规模：文档树 4360 个文件 git mv 落位（源 2698 = 迁入 2657 + 去重丢弃 41）；`.meta/toml` 镜像 1714 rename + 241 删除 + 1240 骨架新建 + 252 移动保留；x-toml-ref 路径批量重写；`.agents/docs/` 与 `.meta/toml/.agents/docs/` 实体消亡；`.meta/toml/.agents/` 399 个规范层镜像合法保留
- 系列原子提交：docs(structure) 文档树迁移、chore(meta) TOML 镜像、chore(scripts) 门禁工具链适配、fix(links) 全仓链接收敛（754 文件）、docs(spec) 迁移档案；收尾四原子提交——fix(links) 补齐 .agents 区 37 处链接深度回归（check-links 断链 765→728）、fix(meta) 两处 TOML id/title 漂移对齐（version-ripple 红错清零）、fix(scripts) pattern-maturity 排除 index/log 导航文件、docs(changelog) docgen 统计同步 3173+
- 门禁终验（迁移回归 = 0）：check-toctrees 通过、check-utf8 5810 文件通过、check-frontmatter 5805 文件全部合规（exit=0）、version-ripple（CI 门）红错 0、docgen all exit=0、pattern-maturity 0 FAIL（327 通过）、repo-check gitignore/vendor/roles 三项通过；check-links 残留 728 断链 + 230 目录警告全部经 HEAD~5 基线比对证实为预存债务（异机 file://、历史重组缺口）；generate-readme 205 缺 README 全预存；mermaid 10880 错误为基线即红的预存内容债务，均登记 backlog
- 遗留债务登记：`.trae/specs/agents-docs-migration/mapping.md` §8——子模块待修清单（xuanspace 25 处旧口径引用、awesome-okf-xs 1 处，含 1 条迁移后已 404 的 GitHub blob URL）+ 主仓门禁债务清单 10 项（9 项预存债务分流治理、1 项 check-frontmatter 终验已转绿）+ 可复现复验命令

## 2026-08-31

- docs 文档中心全量复盘行动项推进（session sc-20260831-docs-debt-remediation，源报告：retrospective/reports/concepts/milestone/docs-full-retrospective-20260831.md 第六章 ACT-1~ACT-6）
- ACT-1/ACT-2（P0）：移除 7 处 toctree 断链；fix-toctrees 四轮收敛（220 个 toctree 新建、343 个更新），未收录内容全部分流可达，check-toctrees 归零
- ACT-3（P1）：frontmatter 批量治理——53 处 Malformed YAML 修复、21 处剥离、98 个文件补 frontmatter、1506 个文件补 type 字段、1 处手工修复；check-frontmatter 归零（2695 个文件合规）
- ACT-4（P1）：retrospective 索引修复——index.md 板块表/使用建议/接入约定链接改指 concepts 层级；methodology-patterns 清单表去重 1 行、补登 5 个模式（终态 22 行）；milestone 报告表补录 4 份报告（终态 22 行）
- ACT-5（P1）：双文档体系边界治理——根 AGENTS.md 文档边界条款与知识库表修订、global-core-rules 路径解析规则重写（R1-R6）；新建 retrospective/cross-reference-ledger.md 收敛台账（基线 675/164 处，B1-B5 分批）并登记 toctree；R2 冻结生效，新增跨区引用数=0
- ACT-6（P2）：bp-nav-co-registration（生成-登记同步法，L1.5）入库终检通过——模式文件、concepts/index 表格与 toctree、主清单表、源报告 L138 交叉引用四处一致
- 门禁回归：check-toctrees / check-frontmatter / check-utf8 全部 exit=0（2696 个文件）
- 项目级复盘：新增 [doc-governance-program-retrospective-20260831.md](retrospective/reports/concepts/milestone/doc-governance-program-retrospective-20260831.md)（2026-07~08 文档治理工作项目级复盘，session retr-20260831-doc-governance）；34 条事实/4 条项目级洞察/6 项行动项（ACT-G1~G6）；里程碑索引表与 toctree 同步登记；门禁复验通过（utf8 5810/toctrees 全可达/frontmatter 5805）；待 co-founder 审批

## 2026-08-22

- 初始 OKF v0.2 转换
