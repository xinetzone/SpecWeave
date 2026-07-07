# Changelog

本文件记录项目的重要变更历史，格式遵循 `- YYYY-MM-DD | type | description`，按时间倒序排列。

<!-- changelog -->
- 2026-07-07 | docs | 新增@volcengine/ark-cli安装与SSO配置任务复盘：解决npm包名与bin命令名不一致、IDE沙箱权限限制、非交互式终端OAuth流程三个关键问题，沉淀CLI工具配置四步法和无浏览器OAuth认证流程2个可复用模式
- 2026-07-07 | docs | 沉淀相对路径三类特殊踩坑案例模式文档：replace_all子串级联替换、归档目录深度计算错误、跨目录前缀误判，共性教训是用工具验证替代心算
- 2026-07-07 | fix | 修复复盘报告481个断链，恢复链接体系完整性：类型A（377个）file:///绝对路径转相对路径，类型B（80个）路径深度校正，类型C（24个）无效链接转 inline code，归档路径层级错误（15个）。预防措施：沉淀3类路径陷阱为模式文档
- 2026-07-07 | fix | 批量修复复盘报告中file:///绝对路径为相对路径（26个文件）：competitive-analysis/目录8个复盘报告、task-reports/目录oray/tvm报告的交付物链接和导航路径；同步更新.trae/specs/retrospectives-insights/README.md（新增7个已完成条目）和asset-inventory.md（新增codex/mainecoon索引）。预防措施：retrospective-cmd v1.5.0已新增Grep数据验证三查法，其中第二查即为file:///绝对路径检查
- 2026-07-07 | feat | 实现L0探针代码阶段守卫豁免机制：新增is_baby_code()识别函数（baby-前缀/.temp/baby/目录），扩展guard_operation()入口支持自动豁免，更新阶段守卫文档规则，新增34个E2E测试（共105测试通过）
- 2026-07-07 | docs | 归档Codex产品哲学文章分析至docs/retrospective/reports/insight-extraction/external-learning/
- 2026-07-07 | docs | 新增L0-L3流程分级模板设计复盘报告（含重叠评估、目录结构冲突评估）
- 2026-07-07 | feat | 新增MaineCoon实时音视频模型深度分析全链路产出（知识库+洞察归档+任务复盘+Skill v1.5.0升级）
- 2026-07-07 | feat | 沉淀5个方法论模式：诚实承认局限性、豁免机制合法化、三角困境架构级解决、外部文章深度分析工作流、外部文章深度分析方法论
