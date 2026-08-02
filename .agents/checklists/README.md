# checklists

标准化检查清单索引。

## 内容

| 清单 | 用途 | 适用场景 |
|------|------|---------|
| [risk-scoring-checklist.md](risk-scoring-checklist.md) | 风险评分决策检查清单 | AI Agent 工具权限设计、自动化流程安全闸门、DevOps 部署审批 |
| [docker-build-optimization-checklist.md](docker-build-optimization-checklist.md) | Docker 构建流程优化检查清单 | 含 C/C++ 编译产物的 Python wheel Docker 运行时镜像构建 |
| [docker-container-management-script-checklist.md](docker-container-management-script-checklist.md) | Docker容器一键管理脚本开发检查清单 | Docker镜像一键启动/停止管理Shell脚本开发（含WSL兼容） |
| [docker-legacy-project-risk-warning-checklist.md](docker-legacy-project-risk-warning-checklist.md) | Docker 化老旧项目风险预警清单 | 5 年以上老旧 C/C++ 项目创建 Docker 构建系统 |
| [security-remediation-checklist.md](security-remediation-checklist.md) | 安全修复检查清单 | 安全漏洞修复与验证 |
| [build-config-change-checklist.md](build-config-change-checklist.md) | 构建配置变更检查清单 | 构建系统配置变更的影响评估 |
| [code-review-checklist.md](code-review-checklist.md) | 代码审查检查清单 | 代码审查标准流程 |
| [meta-retrospective-checklist.md](meta-retrospective-checklist.md) | 元复盘检查清单 | 复盘质量评估 |
| [tech-doc-writing-precheck.md](tech-doc-writing-precheck.md) | 技术文档写作预检清单 | 技术文档撰写前的完整性检查 |
| [self-reference-blindspot-defense.md](self-reference-blindspot-defense.md) | 自引用盲点防御清单 | 防范文档自引用导致的逻辑盲点 |
| [dl-framework-op-correctness-test-checklist.md](dl-framework-op-correctness-test-checklist.md) | 深度学习框架算子正确性测试检查清单 | Caffe/PyTorch/TF等DL框架算子正确性单元测试编写 |
| [pattern-extraction-hardening-checklist.md](pattern-extraction-hardening-checklist.md) | 新模式萃取补强检查清单 | 七概念E阶段萃取模式后、V阶段对抗审查前，自检递归风险/参数可落地性/自积累负反馈/信任链完整性（4大类17项） |
| [framework-extension-and-perf-logging-review.md](framework-extension-and-perf-logging-review.md) | 框架扩展与性能日志代码审查清单 | 基类接口渐进式扩展、算子性能日志埋点（单遍历+GEMM多阶段适配）、Monorepo CI盲区检测，三模式快速对照CR |