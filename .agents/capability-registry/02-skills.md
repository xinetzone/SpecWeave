---
id: "capability-registry-skills"
title: "Skill索引"
source: "capability-registry.md#02-skills"
x-toml-ref: "../../.meta/toml/.agents/capability-registry/02-skills.toml"
---
# Skill索引


### 完整Skill（8个）

| Skill名 | 触发词 | 方案数 | 版本 | 路径 |
|---------|--------|-------|------|------|
| forum-posting | "发帖"、"编辑帖子"、"回复帖子"、"跟帖"、"清理草稿"、"读取帖子"、"操作forum.trae.cn"、"Discourse论坛" | 2（forum-bot.py脚本 + integrated_browser MCP） | v1.1.0 | [skills/forum-posting/SKILL.md](../skills/forum-posting/SKILL.md) |
| home-assistant | "智能家居"、"控制设备"、"查询状态"、"home assistant"、"ha_api" | 1（REST API，零第三方依赖） | v1.2.0 | [skills/home-assistant/SKILL.md](../skills/home-assistant/SKILL.md) |
| git-commit-helper | "提交"、"commit"、"原子提交"、"代码提交"、"提交变更"、"git commit"、"保存更改" | 1（内置validate_commit.py脚本，三查暂存法） | v1.1.0 | [skills/git-commit-helper/SKILL.md](../skills/git-commit-helper/SKILL.md) |
| client-overlay-scaffold | "新增/创建 client 叠加层"、"工作负载栈"、"新 invoke 命名空间 compose 栈"、"照 onnx-quantized/native-dev/agent-monetize-dev 再做一个"、"overlay 脚手架" | 2（形态 A 运行时依赖栈 / 形态 B 工具链挂载栈；v1.1 起声明式 StackSpec + extends rootless-base 基段，compose/namespace/.env 三套骨架模板 + 交付清单 + 两张测试黄金表） | v1.1.0 | [skills/client-overlay-scaffold/SKILL.md](../skills/client-overlay-scaffold/SKILL.md) |
| collect-api-decouple-cmd | "推理和后处理分开"、"采集/推理变成可选"、"已经推理过了复用日志"、"跳过设备执行"、"重放日志"、"只重新算指标" | 1（副作用边界切分 + dataclass 阶段契约 + run_<step> 开关逐层贯通 + 复用分支规避清理型工厂，I→F→A→V 执行卡） | v1.0.0 | [skills/collect-api-decouple-cmd/SKILL.md](../skills/collect-api-decouple-cmd/SKILL.md) |
| classical-festival-video | "祝福视频"、"节日贺卡视频"、"给 TA 做个视频"、"用老子/庄子/诗词做底本"、"中秋/春节/元宵祝福" | 1（三关键帧→10s竖版→随片文案+考据弹药；含情感分寸矩阵、画面禁字约束、预览确认门、物理量验收） | v1.0.0 | [skills/classical-festival-video/SKILL.md](../skills/classical-festival-video/SKILL.md) |
| meoo-skill-publish | "上传技能"、"发布技能到 Meoo/技能市场"、"更新技能版本"、"技能市场上架"、"meoo.com/skills 发布" | 1（P1 package 自包含根级 ZIP 与零包外引用扫描 → P2 登录态页内 POST /api/v1/skills/publish，带 skill_id 即版本更新 → P3 download 回流逐文件 SHA256 verify；含 127.0.0.1 relay 中继；L1） | v1.0.0 | [skills/meoo-skill-publish/SKILL.md](../skills/meoo-skill-publish/SKILL.md) |
| skill-mirror-archive | "归档技能"、"技能镜像入库"、"平台技能导入"、"镜像归档"、"外部技能入库"、"把 XX 技能归档到 .agents/skills" | 1（sovereign-rollout 四阶段治理门 + Copy 保真/哈希核验 + source 溯源泛化 + 登记面双轨裁剪 + 原子提交；L1） | v1.0.0 | [skills/skill-mirror-archive/SKILL.md](../skills/skill-mirror-archive/SKILL.md) |

### 工作流门面（6个）

| Skill名 | 触发词 | 方案数 | 版本 | 路径 |
|---------|--------|-------|------|------|
| source-code-to-okf-wiki | "源码学习"、"读源码"、"源码阅读"、"生成Wiki"、"OKF Wiki"、"源码转文档"、"深度学一个库" | 1（R→I→E→V→C五阶段工作流，L2为源码转化模式文档+prompt模板） | v1.2.0 | [skills/source-code-to-okf-wiki/SKILL.md](../skills/source-code-to-okf-wiki/SKILL.md) |
| blog-article-to-okf-wiki | "博文转化"、"公众号文章"、"微信文章"、"转知识包"、"OKF bundle"、"OKF wiki"、"文章转文档"、"资讯转知识库" | 1（七阶段工作流，L2为博文转化L3模式文档；13篇实战验证） | v1.0.0 | [skills/blog-article-to-okf-wiki/SKILL.md](../skills/blog-article-to-okf-wiki/SKILL.md) |
| scanned-book-to-okf-wiki | "扫描版书籍转教程"、"书转Wiki"、"摘要替代转录"、"扫描版版权材料"、"书转知识包"、"混合型PDF" | 1（六工序工作流：route决策前置→文本层可信度判定+逐章通读→深度摘要→原创改写→合规声明契约化（含计数口径）→V实证对账；L2 双案例验证：案例1财商寓言/纯图像、案例2练习册/噪声OCR混合型；两配套模式已入 docs 模式库） | v2.0.0 | [skills/scanned-book-to-okf-wiki/SKILL.md](../skills/scanned-book-to-okf-wiki/SKILL.md) |
| role-model-methodology | "榜样学习"、"人物解读"、"正面解读师"、"名人方法论"、"人物关联洞察"、"榜样学习路径"、"终身学习者"、"怎么学名人"、"人物知识包"、"向谁学习" | 1（七阶段工作流：四级事实分层→三框架诊断→证据桥接审查→六步解读法；L1门面 + L2 七概念编排；含伦理四条约束与「门禁全绿≠链接都对」双重护栏；实战：2026-10-03 三人榜样知识包 4包/61文档/254事实） | v1.1.0 | [skills/role-model-methodology/SKILL.md](../skills/role-model-methodology/SKILL.md) |
| mindfulness-positivity | "正念"、"正面"、"积极心态"、"正能量"、"mindfulness"、"positive thinking"、"习得性乐观"、"有毒正能量"、"toxic positivity"、"先接纳后重构"、"正念和积极有什么区别"、"情绪调节" | 1（四场景决策树：概念问答/内容产出/自我调节方案/知识包沉淀；七维度辨析框架+先接纳后重构四步整合法+心理健康安全边界；L1门面 + L2 知识底座 sc-20261003-mindfulness-positivity：22事实/3洞察/1模式） | v1.0.0 | [skills/mindfulness-positivity/SKILL.md](../skills/mindfulness-positivity/SKILL.md) |
| dao-san-triads | "三生万物"、"道生一"、"二生三"、"三之位"、"三元组"、"过去现在未来"、"时间三分"、"奥古斯丁三分法"、"记忆注意期待"、"一分为三"、"真问题真需求真目标"、"品质技能身份"、"生存指南"、"行动准则"、"极简原则"、"二选一怎么办"、"自我诊断"、"古典哲学概念" | 1（四场景决策树：概念探究/自我诊断/行动准则/知识包沉淀；六类「三」解释谱系+第五义「三=关系位」统一模型+奥古斯丁三分法与最强反驳+时态检验+两组三元组四元关联+七条生存指南（≤1200字）+「三之位」可迁移模式（5反模式/3问检验/L1-draft）+《老子》版本纪律；L1门面 + L2 知识底座 sc-20261003-dao-san-yuan：50事实/4洞察/1模式/9条审查） | v1.0.0 | [skills/dao-san-triads/SKILL.md](../skills/dao-san-triads/SKILL.md) |

### Trae 内置工作流 Skill（2个，来自 external/doutops）

| Skill名 | 触发词 | 方案数 | 版本 | 路径 |
|---------|--------|-------|------|------|
| TRAE-plan-mode | "规划"、"实施计划"、"plan mode"、"计划批准"、"先规划后执行"、"有界变更" | 1（单一实施计划+一次批准门，批准前禁写，计划落盘 .trae/documents/） | v1.0.0 | [skills/TRAE-plan-mode/SKILL.md](../skills/TRAE-plan-mode/SKILL.md) |
| TRAE-spec-mode | "规范模式"、"spec mode"、"需求澄清"、"验收标准"、"任务队列"、"独立审查"、"恢复中断工作流" | 1（五阶段规范工作流，spec/tasks/review 三产物落盘 .trae/specs/，rule/rubric 验收+独立 Review 门） | v1.0.0 | [skills/TRAE-spec-mode/SKILL.md](../skills/TRAE-spec-mode/SKILL.md) |

> 两者互为选型路由：有界变更→plan，复杂/高影响/跨会话→spec。派生自 Trae 内置 doutops skill（external/ 非 git 目录），中文五要素适配版；Trae 同步覆盖后以本仓库版本为准（大写路径为权威位置）。

### 命令集门面（11个）

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
| github-org-bootstrap-cmd | "创建GitHub组织"、"建个org"、"组织名怎么起"、"demo组织"、"huncheng-lab"、"GitHub Organization" | 1（命名收敛F→V→I + gh api 自动配置） | v1.0.0 | [skills/github-org-bootstrap-cmd/SKILL.md](../skills/github-org-bootstrap-cmd/SKILL.md) |

### 脚本命令门面（16个）

| Skill名 | 触发词 | 对应脚本 | 版本 | 路径 |
|---------|--------|---------|------|------|
| compose-overlay-ops | "启动/重建 native-dev/onnx-quantized/agent-monetize 栈"、"native.up/build/smoke"、"quant.up"、"容器 Exited(0)"、"netavark nft"、"Jupyter 保存 Errno 13"、"checkpoint 权限"、"WSL 发行版回收容器"、"tuna 构建叠加镜像" | invoke quant.*/native.*/monetize.*（apps/containers/client，podman-compose 子进程层；保活锚→预检→build→up→浸泡→smoke SOP） | v1.0.0 | [skills/compose-overlay-ops/SKILL.md](../skills/compose-overlay-ops/SKILL.md) |
| jpman-podman-ops | "jpman"、"启动jupyter容器"、"podman machine"、"工作区挂载"、"容器WARN分诊"、"fuse device"、"rootless排障"、"WSL保活"、"rebuild"、"crun pids not available"、"non-systemd cgroup"、"pids-limit 不生效"、"WSL3 容器起不来"、"machine not in running state" | jpman（apps/containers/jupyter-podman-rootless/bin，bash/cmd/ps1 三版本；WSL3 cgroup 委托修复=systemd=true+/sbin/init argv[0] shim 两步） | v1.3.0 | [skills/jpman-podman-ops/SKILL.md](../skills/jpman-podman-ops/SKILL.md) |
| openkylin-wsl-devkit | "okw"、"openKylin WSL 导入/验收"、"发行版内装 podman"、"okw podman/compose/image"、"xuan-compose/xc 引导"、"开发容器镜像"、"deb/dput 脚手架"、"okw ref"、"修改 openkylin-wsl-devkit" | okw（apps/dev-tools/openkylin-wsl-devkit，Python 零运行时依赖七组命令；--yes 授权门、verify 禁隐式拉取、CLI 快照再生成门禁） | v1.0.0 | [skills/openkylin-wsl-devkit/SKILL.md](../skills/openkylin-wsl-devkit/SKILL.md) |
| docker-cache-cmd | "保存镜像"、"缓存Docker镜像"、"docker缓存"、"镜像缓存"、"加载镜像"、"封存镜像"、"docker save/load"、"WSL重置恢复"、"镜像本地缓存" | docker-cache（bash脚本） | v1.0.0 | [skills/docker-cache-cmd/SKILL.md](../skills/docker-cache-cmd/SKILL.md) |
| docker-wsl-bridge-cmd | "镜像转WSL"、"docker镜像导入WSL"、"镜像转rootfs"、"podman export转wsl"、"WSL重置后恢复开发环境"、"docker-wsl-bridge"、"没有Docker Desktop怎么启动镜像" | wsl+podman跨Shell编排 | v1.0.0 | [skills/docker-wsl-bridge-cmd/SKILL.md](../skills/docker-wsl-bridge-cmd/SKILL.md) |
| wsl-ops-cmd | "WSL磁盘清理"、"vhdx压缩"、"盘爆红"、"Docker GPU不可用"、"--gpus报错"、"nvidia-container-toolkit"、"wsl --shutdown后Docker不自启"、"wsl.conf boot"、"setsid dockerd"、"Trae缓存清理"、"fstrim"、"孤儿卷/build cache清理" | compress-wsl-vhdx.ps1、Restart-WslDockerGpu.ps1、setup-wsl-docker-gpu.sh、cleanup-trae-cache.ps1（4脚本+存储清理五步法/GPU三层分诊两模式） | v1.0.0 | [skills/wsl-ops-cmd/SKILL.md](../skills/wsl-ops-cmd/SKILL.md) |
| link-check-cmd | "链接检查"、"检查链接"、"断链"、"链接修复"、"fix links"、"check links"、"验证链接"、"死链" | check-links.py + lib/link_fixer.py | v1.0.0 | [skills/link-check-cmd/SKILL.md](../skills/link-check-cmd/SKILL.md) |
| atomization-finalize-cmd | "原子化收尾"、"finalize atomization"、"文档拆分完成"、"文件移动后处理"、"断链修复导航更新"、"一键收尾" | finalize-atomization.py | v1.0.0 | [skills/atomization-finalize-cmd/SKILL.md](../skills/atomization-finalize-cmd/SKILL.md) |
| submodule-atomization-finalize-cmd | "子模块文档原子化收尾"、"projects 下文档拆分收尾"、"子模块断链/中文锚点检查"、"GitHub slug 校验"、"子模块文件移动引用核对"、"事实守恒 diff" | 自带 scripts/check_doc_links.py（GitHub slug 门禁，中文锚点/显式 a id/非 .md 锚点豁免）+ 六步收尾 SOP（边界→入站引用→链接门禁→HEAD 守恒→残留→清理） | v1.0.0 | [skills/submodule-atomization-finalize-cmd/SKILL.md](../skills/submodule-atomization-finalize-cmd/SKILL.md) |
| docgen-cmd | "生成导航"、"更新导航"、"docgen"、"更新README"、"刷新看板"、"生成文档索引"、"应用清单" | docgen.py（含nav/dashboard/apps/stats/all子命令） | v1.1.0 | [skills/docgen-cmd/SKILL.md](../skills/docgen-cmd/SKILL.md) |
| ci-check-cmd | "CI检查"、"提交前检查"、"综合检查"、"ci-check"、"流水线检查"、"提交门禁"、"全量检查"、"跑一下CI"、"pre-commit"、"预检" | ci-check.ps1 + ci-check.sh | v1.0.0 | [skills/ci-check-cmd/SKILL.md](../skills/ci-check-cmd/SKILL.md) |
| check-duplication-cmd | "重复代码"、"重复检查"、"代码重复"、"check-duplication"、"重复检测"、"提取共享库"、"DRY检查"、"脚本重复" | check-duplication.py + lib/ | v1.0.0 | [skills/check-duplication-cmd/SKILL.md](../skills/check-duplication-cmd/SKILL.md) |
| knowledge-graph-generator | "知识图谱"、"knowledge graph"、"概念关系可视化"、"交互式知识图谱"、"节点关系网络"、"生成知识图谱" | generate-graph.py + knowledge_graph_core.py | v1.0.0 | [skills/knowledge-graph-generator/SKILL.md](../skills/knowledge-graph-generator/SKILL.md) |
| artifact-consistency-audit | "核验一致性"、"复验"、"体检"、"覆盖率核对"、"引用是否忠实"、"有无遗漏"、"修补后复验"、"对照源文档检查" | 复用 check-links.py + check-source-traceability.py（无新建脚本） | v1.0.0 | [skills/artifact-consistency-audit/SKILL.md](../skills/artifact-consistency-audit/SKILL.md) |
| docs-as-product-cmd | "文档即产品"、"docs-as-product"、"Diátaxis四型分区"、"文档质量门G1-G4/V门"、"sphinx-build -W"、"元数据漂移F-021"、"读者契约"、"文档指标M1-M5" | docs-as-product.py + lib/docs_as_product/（structure/gates/metadata/contract/metrics/all 子命令；只读，外部工具缺失降级） | v1.0.0 | [skills/docs-as-product-cmd/SKILL.md](../skills/docs-as-product-cmd/SKILL.md) |
| wsl-vhdx-compact-cmd | "压缩WSL磁盘"、"vhdx回收"、"ext4.vhdx太大"、"wsl --manage --compact"、"宿主机FreeGiB核对"、"VHDX前后基线"、"podman-machine-default vhdx压缩"、"openKylin WSL磁盘回收"、"C/D盘爆红 清WSL"、"wsl vhdx瘦身"、"Win32_LogicalDisk对账"、"fstrim 基线 闭环" | compact-vhdx-with-baseline.ps1；失败自动降级 compress-wsl-vhdx.ps1（双方案自动降级 + BaselineOnly dry-run 只读基线 + RestorePodman/RestoreOriginalState 原态恢复 + Win32 FreeGiB 数值闭环 + PCMClawUbuntu 永久黑名单） | v1.0.0 | [skills/wsl-vhdx-compact-cmd/SKILL.md](../skills/wsl-vhdx-compact-cmd/SKILL.md) |

> **Skill类型说明**：
> - **完整Skill**：包含完整双方案实现、工具函数、详细步骤，可独立完成复杂任务
> - **工作流门面**：对 `docs/retrospective/patterns/` 方法论模式的触发封装（L1 门面含触发词/阶段流程/质量门，L2 为完整模式文档）
> - **命令集门面**：对 `.agents/commands/` 命令集的轻量封装，提供触发词、决策树、快速开始和安全检查
> - **脚本命令门面**：对 `.agents/scripts/` 高频自动化脚本的封装，提供参数说明、dry-run/预览机制、幂等性说明和错误处理

---


---

## 相关模式


← 上一章: [脚本索引](01-scripts.md) | **[返回索引](../capability-registry.md)** | 下一章 → [命令集、工作流、协议、规则索引](03-commands-workflows-protocols-rules.md)
