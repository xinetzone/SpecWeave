# Changelog

本文件记录项目的重要变更历史，格式遵循 `- YYYY-MM-DD | type | description`，按时间倒序排列。

<!-- changelog -->
- 2026-07-09 | docs | P0阶段核心入口README补全：为docs/下13个核心目录创建结构化入口文档，覆盖L1根级目录4个（architecture/superpowers/task-summaries/test-plans）、knowledge二级4个（decisions/mdi-research/operations/troubleshooting）、retrospective二级2个（concepts/frameworks）、learning三级3个（01-Agent协议接口/02-工程方法论/03-平台工具），共新增13个README.md+13个.meta/toml元数据文件；全量扫描311个Markdown文件1338个本地链接，新README引入0断链
- 2026-07-09 | docs | best-practices目录断链修复与入口文档建设：①系统性扫描docs/knowledge/best-practices/下12个Markdown文件85个本地链接，修复2个路径深度错误（b2b-product-info-collection-sop.md第145行../retrospective/→../../retrospective/、eight-dimensions-concurrent-safety-spec.md frontmatter source路径补全）和1个frontmatter路径格式不一致问题；②新增best-practices/README.md入口文档，包含八维检查法核心概念概述（三级严重度分级表/12类反模式覆盖/核心原则）、关键应用场景、5分钟快速上手指南、11篇最佳实践文档索引表、9场景分组快速导航和相关资源链接；③创建对应.meta/toml元数据文件并通过docgen重新生成knowledge/README.md索引（best-practices条目数从8更新为10，新增ai-anthropomorphic和eight-dimensions两篇此前遗漏条目）
- 2026-07-08 | feat | TRAE v3.3.74 版本发布：设置中新增 Browser 配置聚合页【仅个人版】；Windows 接入 MSSDK【仅个人版】；修复了已知问题
- 2026-07-07 | docs | 新增@volcengine/ark-cli安装与SSO配置任务复盘：解决npm包名与bin命令名不一致、IDE沙箱权限限制、非交互式终端OAuth流程三个关键问题，沉淀CLI工具配置四步法和无浏览器OAuth认证流程2个可复用模式
- 2026-07-07 | docs | 沉淀相对路径三类特殊踩坑案例模式文档：replace_all子串级联替换、归档目录深度计算错误、跨目录前缀误判，共性教训是用工具验证替代心算
- 2026-07-07 | fix | 修复复盘报告481个断链，恢复链接体系完整性：类型A（377个）file:///绝对路径转相对路径，类型B（80个）路径深度校正，类型C（24个）无效链接转 inline code，归档路径层级错误（15个）。预防措施：沉淀3类路径陷阱为模式文档
- 2026-07-07 | fix | 批量修复复盘报告中file:///绝对路径为相对路径（26个文件）：competitive-analysis/目录8个复盘报告、task-reports/目录oray/tvm报告的交付物链接和导航路径；同步更新.trae/specs/retrospectives-insights/README.md（新增7个已完成条目）和asset-inventory.md（新增codex/mainecoon索引）。预防措施：retrospective-cmd v1.5.0已新增Grep数据验证三查法，其中第二查即为file:///绝对路径检查
- 2026-07-07 | feat | 实现L0探针代码阶段守卫豁免机制：新增is_baby_code()识别函数（baby-前缀/.temp/baby/目录），扩展guard_operation()入口支持自动豁免，更新阶段守卫文档规则，新增34个E2E测试（共105测试通过）
- 2026-07-07 | docs | 归档Codex产品哲学文章分析至docs/retrospective/reports/insight-extraction/external-learning/
- 2026-07-07 | docs | 新增L0-L3流程分级模板设计复盘报告（含重叠评估、目录结构冲突评估）
- 2026-07-07 | feat | 新增MaineCoon实时音视频模型深度分析全链路产出（知识库+洞察归档+任务复盘+Skill v1.5.0升级）
- 2026-07-07 | feat | 沉淀5个方法论模式：诚实承认局限性、豁免机制合法化、三角困境架构级解决、外部文章深度分析工作流、外部文章深度分析方法论
