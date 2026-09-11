# checklists

标准化检查清单索引。

## 内容

| 清单 | 用途 | 适用场景 |
|------|------|---------|
| [risk-scoring-checklist.md](risk-scoring-checklist.md) | 风险评分决策检查清单 | AI Agent 工具权限设计、自动化流程安全闸门、DevOps 部署审批 |
| [docker-build-optimization-checklist.md](docker-build-optimization-checklist.md) | Docker 构建流程优化检查清单 | 含 C/C++ 编译产物的 Python wheel Docker 运行时镜像构建 |
| [docker-pip-user-ownership-checklist.md](docker-pip-user-ownership-checklist.md) | Docker 构建时/运行时属主分离（PIP_USER 治理）检查清单 | 多阶段 Dockerfile + 非 root 运行用户 + conda/pip AI 开发容器，构建期/运行期属主分离、禁止整体 chown |
| [docker-buildkit-compliance-checklist.md](docker-buildkit-compliance-checklist.md) | Dockerfile BuildKit 合规性速查清单 | 新建/修改 Dockerfile 后30秒快速对照：语法声明+安全Shell+缓存挂载三件套，含一页纸速查卡片 |
| [docker-container-management-script-checklist.md](docker-container-management-script-checklist.md) | Docker容器一键管理脚本开发检查清单 | Docker镜像一键启动/停止管理Shell脚本开发（含WSL兼容） |
| [docker-legacy-project-risk-warning-checklist.md](docker-legacy-project-risk-warning-checklist.md) | Docker 化老旧项目风险预警清单 | 5 年以上老旧 C/C++ 项目创建 Docker 构建系统 |
| [security-remediation-checklist.md](security-remediation-checklist.md) | 安全修复检查清单 | 安全漏洞修复与验证 |
| [build-config-change-checklist.md](build-config-change-checklist.md) | 构建配置变更检查清单 | 构建系统配置变更的影响评估 |
| [code-review-checklist.md](code-review-checklist.md) | 代码审查检查清单 | 代码审查标准流程 |
| [meta-retrospective-checklist.md](meta-retrospective-checklist.md) | 元复盘检查清单 | 复盘质量评估 |
| [tech-doc-writing-precheck.md](tech-doc-writing-precheck.md) | 技术文档写作预检清单 | 技术文档撰写前的完整性检查 |
| [self-reference-blindspot-defense.md](self-reference-blindspot-defense.md) | 自引用盲点防御清单 | 防范文档自引用导致的逻辑盲点 |
| [declaration-reconciliation-checklist.md](declaration-reconciliation-checklist.md) | 统计型声明实证核验清单（声明对账） | 产出物含"合计/不超过/均为/全覆盖"类自我声明时的实证核验（字数逐条数、链接逐个开、声明-事实对账），V 对抗审查固定检查项 |
| [declaration-reconciliation-reproduction-checklist.md](declaration-reconciliation-reproduction-checklist.md) | 声明对账模式复现检查清单（A-004） | 第 2 个独立任务中复现"声明对账"模式 5 步骤并逐项留证，验收通过后模式升 L2 入 `docs/retrospective/patterns/`；区别于 A-001 的"用时核验清单" |
| [summary-over-transcription-reproduction-checklist.md](summary-over-transcription-reproduction-checklist.md) | 扫描版版权材料摘要替代转录复现检查清单（A-005） | 第 2 个独立扫描版版权材料任务中复现"摘要替代转录"模式 6 步骤并逐项留证，验收通过后模式升 L2 入 `docs/retrospective/patterns/`。**已于 2026-09-11 案例 2《魔力》复现通过，模式升 L2 入库** `docs/retrospective/patterns/methodology-patterns/summary-over-transcription.md` |
| [compliance-contracting-reproduction-checklist.md](compliance-contracting-reproduction-checklist.md) | 合规契约化复现检查清单（A-006） | 第 2 个独立案例（合规红线产出物，跨场景迁移类优先）中复现"合规契约化"模式 4 步骤并逐项留证，验收通过后模式升 L2 入 `docs/retrospective/patterns/`。**已于 2026-09-11 案例 2《魔力》复现通过（新增计数口径与主张分层经验），模式升 L2 入库** `docs/retrospective/patterns/methodology-patterns/compliance-contracting.md` |
| [scanned-book-to-okf-wiki-reproduction-checklist.md](scanned-book-to-okf-wiki-reproduction-checklist.md) | 扫描版书籍转OKF Wiki教程 Skill L2 案例复现检查清单 | 第 2 个独立扫描版版权材料任务中复现 scanned-book-to-okf-wiki Skill 六工序并留证门面层证据（CMD-LOG/G1–G4 判定/缺陷反哺），与 A-005/A-006 模式层清单配合，三清单全过后 Skill 升 L2。**已于 2026-09-11 案例 2《魔力》复现通过，Skill 升 v2.0.0（L2）** |
| [dl-framework-op-correctness-test-checklist.md](dl-framework-op-correctness-test-checklist.md) | 深度学习框架算子正确性测试检查清单 | Caffe/PyTorch/TF等DL框架算子正确性单元测试编写 |
| [pattern-extraction-hardening-checklist.md](pattern-extraction-hardening-checklist.md) | 新模式萃取补强检查清单 | 七概念E阶段萃取模式后、V阶段对抗审查前，自检递归风险/参数可落地性/自积累负反馈/信任链完整性（4大类17项） |
| [framework-extension-and-perf-logging-review.md](framework-extension-and-perf-logging-review.md) | 框架扩展与性能日志代码审查清单 | 基类接口渐进式扩展、算子性能日志埋点（单遍历+GEMM多阶段适配）、Monorepo CI盲区检测，三模式快速对照CR |