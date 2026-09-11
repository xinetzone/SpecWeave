---
id: "capability-registry-skills"
title: "Skill索引"
source: "capability-registry.md#02-skills"
x-toml-ref: "../../.meta/toml/.agents/capability-registry/02-skills.toml"
---
# Skill索引


### 完整Skill（3个）

| Skill名 | 触发词 | 方案数 | 版本 | 路径 |
|---------|--------|-------|------|------|
| forum-posting | "发帖"、"编辑帖子"、"回复帖子"、"跟帖"、"清理草稿"、"读取帖子"、"操作forum.trae.cn"、"Discourse论坛" | 2（forum-bot.py脚本 + integrated_browser MCP） | v1.1.0 | [skills/forum-posting/SKILL.md](../skills/forum-posting/SKILL.md) |
| home-assistant | "智能家居"、"控制设备"、"查询状态"、"home assistant"、"ha_api" | 1（REST API，零第三方依赖） | v1.2.0 | [skills/home-assistant/SKILL.md](../skills/home-assistant/SKILL.md) |
| git-commit-helper | "提交"、"commit"、"原子提交"、"代码提交"、"提交变更"、"git commit"、"保存更改" | 1（内置validate_commit.py脚本，三查暂存法） | v1.1.0 | [skills/git-commit-helper/SKILL.md](../skills/git-commit-helper/SKILL.md) |

### 工作流门面（3个）

| Skill名 | 触发词 | 方案数 | 版本 | 路径 |
|---------|--------|-------|------|------|
| source-code-to-okf-wiki | "源码学习"、"读源码"、"源码阅读"、"生成Wiki"、"OKF Wiki"、"源码转文档"、"深度学一个库" | 1（R→I→E→V→C五阶段工作流，L2为源码转化模式文档+prompt模板） | v1.2.0 | [skills/source-code-to-okf-wiki/SKILL.md](../skills/source-code-to-okf-wiki/SKILL.md) |
| blog-article-to-okf-wiki | "博文转化"、"公众号文章"、"微信文章"、"转知识包"、"OKF bundle"、"OKF wiki"、"文章转文档"、"资讯转知识库" | 1（七阶段工作流，L2为博文转化L3模式文档；13篇实战验证） | v1.0.0 | [skills/blog-article-to-okf-wiki/SKILL.md](../skills/blog-article-to-okf-wiki/SKILL.md) |
| scanned-book-to-okf-wiki | "扫描版书籍转教程"、"书转Wiki"、"摘要替代转录"、"扫描版版权材料"、"书转知识包"、"混合型PDF" | 1（六工序工作流：route决策前置→文本层可信度判定+逐章通读→深度摘要→原创改写→合规声明契约化（含计数口径）→V实证对账；L2 双案例验证：案例1财商寓言/纯图像、案例2练习册/噪声OCR混合型；两配套模式已入 docs 模式库） | v2.0.0 | [skills/scanned-book-to-okf-wiki/SKILL.md](../skills/scanned-book-to-okf-wiki/SKILL.md) |

### Trae 内置工作流 Skill（2个，来自 external/doutops）

| Skill名 | 触发词 | 方案数 | 版本 | 路径 |
|---------|--------|-------|------|------|
| TRAE-plan-mode | "规划"、"实施计划"、"plan mode"、"计划批准"、"先规划后执行"、"有界变更" | 1（单一实施计划+一次批准门，批准前禁写，计划落盘 .trae/documents/） | v1.0.0 | [skills/TRAE-plan-mode/SKILL.md](../skills/TRAE-plan-mode/SKILL.md) |
| TRAE-spec-mode | "规范模式"、"spec mode"、"需求澄清"、"验收标准"、"任务队列"、"独立审查"、"恢复中断工作流" | 1（五阶段规范工作流，spec/tasks/review 三产物落盘 .trae/specs/，rule/rubric 验收+独立 Review 门） | v1.0.0 | [skills/TRAE-spec-mode/SKILL.md](../skills/TRAE-spec-mode/SKILL.md) |

> 两者互为选型路由：有界变更→plan，复杂/高影响/跨会话→spec。派生自 Trae 内置 doutops skill（external/ 非 git 目录），中文五要素适配版；Trae 同步覆盖后以本仓库版本为准（大写路径为权威位置）。

### 命令集门面（10个）

| Skill名 | 触发词 | 方案数 | 版本 | 路径 |
|---------|--------|-------|------|------|
| sovereign-rollout-cmd | "提案"、"批准落盘"、"主权区变更"、"治理资产落盘"、"先提案后批准" | 1（四阶段闭环：提案草案零写入→批准门→落盘执行→执行报告+check-links 验证） | v1.0.0 | [skills/sovereign-rollout-cmd/SKILL.md](../skills/sovereign-rollout-cmd/SKILL.md) |
| ⭐ seven-concepts-cmd | "方法论编排"、"用方法论"、"系统性分析"、"完整流程"、"七概念"（别名） | 5（里程碑复盘/问题解决/重构优化/知识沉淀/创新突破） | v1.1.0 | [skills/seven-concepts-cmd/SKILL.md](../skills/seven-concepts-cmd/SKILL.md) |
| retrospective-cmd | "复盘"、"retrospective"、"回顾"、"总结经验"、"项目总结"、"阶段回顾" | 3（标准/轻量/故障复盘） | v1.5.0 | [skills/retrospective-cmd/SKILL.md](../skills/retrospective-cmd/SKILL.md) |
| insight-cmd | "洞察"、"insight"、"分析问题"、"萃取洞察"、"根因分析"、"问题诊断"、"为什么" | 3（数据驱动/根因诊断/萃取洞察） | v1.2.1 | [skills/insight-cmd/SKILL.md](../skills/insight-cmd/SKILL.md) |
| extraction-cmd | "萃取"、"extraction"、"模式沉淀"、"模式入库"、"可复用模式"、"沉淀为模式"、"更新模式库" | 3（全新萃取/模式更新/合并重构） | v1.0.0 | [skills/extraction-cmd/SKILL.md](../skills/extraction-cmd/SKILL.md) |
| export-report-cmd | "导出报告"、"export"、"生成报告"、"导出文档"、"归档" | 2（Markdown/JSON） | v1.2.1 | [skills/export-report-cmd/SKILL.md](../skills/export-report-cmd/SKILL.md) |
| atomization-cmd | "原子化"、"拆分文件"、"atomize"、"拆分大文档"、"文档拆分" | 3（文档原子化/一键收尾/预检） | v1.2.1 | [skills/atomization-cmd/SKILL.md](../skills/atomization-cmd/SKILL.md) |
| atomic-commit-cmd | "提交"、"commit"、"原子提交"、"代码提交"、"git commit" | 3（标准/快速/CI检查） | v1.2.1 | [skills/atomic-commit-cmd/SKILL.md](../skills/atomic-commit-cmd/SKILL.md) |
| mermaid-cmd | "mermaid"、"流程图"、"时序图"、"状态图"、"画个图"、"图表"、"架构图"、"思维导图"、"画流程图" | 3（快速生成/检查修复/复杂协作） | v1.1.0 | [skills/mermaid-cmd/SKILL.md](../skills/mermaid-cmd/SKILL.md) |

### 脚本命令门面（10个）

| Skill名 | 触发词 | 对应脚本 | 版本 | 路径 |
|---------|--------|---------|------|------|
| jpman-podman-ops | "jpman"、"启动jupyter容器"、"podman machine"、"工作区挂载"、"容器WARN分诊"、"fuse device"、"rootless排障"、"WSL保活"、"rebuild" | jpman（apps/containers/jupyter-podman-rootless/bin，bash/cmd/ps1 三版本） | v1.0.0 | [skills/jpman-podman-ops/SKILL.md](../skills/jpman-podman-ops/SKILL.md) |
| docker-cache-cmd | "保存镜像"、"缓存Docker镜像"、"docker缓存"、"镜像缓存"、"加载镜像"、"封存镜像"、"docker save/load"、"WSL重置恢复"、"镜像本地缓存" | docker-cache（bash脚本） | v1.0.0 | [skills/docker-cache-cmd/SKILL.md](../skills/docker-cache-cmd/SKILL.md) |
| docker-wsl-bridge-cmd | "镜像转WSL"、"docker镜像导入WSL"、"镜像转rootfs"、"podman export转wsl"、"WSL重置后恢复开发环境"、"docker-wsl-bridge"、"没有Docker Desktop怎么启动镜像" | wsl+podman跨Shell编排 | v1.0.0 | [skills/docker-wsl-bridge-cmd/SKILL.md](../skills/docker-wsl-bridge-cmd/SKILL.md) |
| wsl-ops-cmd | "WSL磁盘清理"、"vhdx压缩"、"盘爆红"、"Docker GPU不可用"、"--gpus报错"、"nvidia-container-toolkit"、"wsl --shutdown后Docker不自启"、"wsl.conf boot"、"setsid dockerd"、"Trae缓存清理"、"fstrim"、"孤儿卷/build cache清理" | compress-wsl-vhdx.ps1、Restart-WslDockerGpu.ps1、setup-wsl-docker-gpu.sh、cleanup-trae-cache.ps1（4脚本+存储清理五步法/GPU三层分诊两模式） | v1.0.0 | [skills/wsl-ops-cmd/SKILL.md](../skills/wsl-ops-cmd/SKILL.md) |
| link-check-cmd | "链接检查"、"检查链接"、"断链"、"链接修复"、"fix links"、"check links"、"验证链接"、"死链" | check-links.py + lib/link_fixer.py | v1.0.0 | [skills/link-check-cmd/SKILL.md](../skills/link-check-cmd/SKILL.md) |
| atomization-finalize-cmd | "原子化收尾"、"finalize atomization"、"文档拆分完成"、"文件移动后处理"、"断链修复导航更新"、"一键收尾" | finalize-atomization.py | v1.0.0 | [skills/atomization-finalize-cmd/SKILL.md](../skills/atomization-finalize-cmd/SKILL.md) |
| docgen-cmd | "生成导航"、"更新导航"、"docgen"、"更新README"、"刷新看板"、"生成文档索引"、"应用清单" | docgen.py（含nav/dashboard/apps/stats/all子命令） | v1.1.0 | [skills/docgen-cmd/SKILL.md](../skills/docgen-cmd/SKILL.md) |
| ci-check-cmd | "CI检查"、"提交前检查"、"综合检查"、"ci-check"、"流水线检查"、"提交门禁"、"全量检查"、"跑一下CI"、"pre-commit"、"预检" | ci-check.ps1 + ci-check.sh | v1.0.0 | [skills/ci-check-cmd/SKILL.md](../skills/ci-check-cmd/SKILL.md) |
| check-duplication-cmd | "重复代码"、"重复检查"、"代码重复"、"check-duplication"、"重复检测"、"提取共享库"、"DRY检查"、"脚本重复" | check-duplication.py + lib/ | v1.0.0 | [skills/check-duplication-cmd/SKILL.md](../skills/check-duplication-cmd/SKILL.md) |
| knowledge-graph-generator | "知识图谱"、"knowledge graph"、"概念关系可视化"、"交互式知识图谱"、"节点关系网络"、"生成知识图谱" | generate-graph.py + knowledge_graph_core.py | v1.0.0 | [skills/knowledge-graph-generator/SKILL.md](../skills/knowledge-graph-generator/SKILL.md) |

> **Skill类型说明**：
> - **完整Skill**：包含完整双方案实现、工具函数、详细步骤，可独立完成复杂任务
> - **工作流门面**：对 `docs/retrospective/patterns/` 方法论模式的触发封装（L1 门面含触发词/阶段流程/质量门，L2 为完整模式文档）
> - **命令集门面**：对 `.agents/commands/` 命令集的轻量封装，提供触发词、决策树、快速开始和安全检查
> - **脚本命令门面**：对 `.agents/scripts/` 高频自动化脚本的封装，提供参数说明、dry-run/预览机制、幂等性说明和错误处理

---


---

## 相关模式


← 上一章: [脚本索引](01-scripts.md) | **[返回索引](../capability-registry.md)** | 下一章 → [命令集、工作流、协议、规则索引](03-commands-workflows-protocols-rules.md)
