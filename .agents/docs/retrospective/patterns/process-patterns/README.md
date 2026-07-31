---
id: "process-patterns-readme"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/process-patterns/README.toml"
---

# 流程模式索引（process-patterns）

本目录存放流程级可复用模式，聚焦于开发流程、构建流程、运维流程等宏观层面的最佳实践。

## 模式清单

| 模式 | 说明 | 成熟度 | 适用场景 |
|------|------|--------|---------|
| [container-build-env-optimization.md](container-build-env-optimization.md) | 容器化构建环境优化模式：镜像源优化+超时重试配置+命令链拆分+验证环节添加+多阶段构建，提升构建成功率和稳定性 | L2 已验证 | Docker镜像构建涉及网络依赖和复杂环境配置的场景 |
| [docker-build-network-resilience.md](docker-build-network-resilience.md) | Docker构建网络容错五步法：国内镜像源→本地COPY先于网络→非核心依赖容错→本地wheel后于网络依赖→核心验证最后执行，应对网络不稳定导致的构建失败 | L1 实验性 | 网络不稳定环境下的Docker构建、国内pip镜像源配置、核心vs非核心依赖分层安装 |
| [docker-entrypoint-two-step-reset.md](docker-entrypoint-two-step-reset.md) | Docker镜像ENTRYPOINT两步安全重置：commit+Dockerfile替代--change，应对docker commit --change在--entrypoint覆盖场景下静默失效 | L1 实验性 | Docker镜像导出/发布、容器以--entrypoint启动后commit |
| [release-gate-automated-verification.md](release-gate-automated-verification.md) | 发布门禁自动化验证：从最终产物加载→配置检查→回归测试→内容完整性→功能冒烟→符号可见性，输出PASS/FAIL报告 | L1 实验性 | 软件发布流程最后一步、Docker镜像/包/二进制产物验证 |
| [container-verify-script-permission-model.md](container-verify-script-permission-model.md) | 容器验证脚本权限安全模型：mkdtemp+显式chmod绕过entrypoint降权导致的Permission denied，区分基础设施错误与镜像质量错误 | L2 已验证 | conda环境镜像验证、含gosu entrypoint的镜像验证、CI门禁脚本 |
| [docker-build-reference-template-copy.md](docker-build-reference-template-copy.md) | Docker 构建系统参考模板复制法：识别参考项目→提取目录骨架→适配替换→逐层构建验证→补充文档，加速新项目Docker构建系统搭建 | L1 实验性 | 新项目Docker化、构建系统从零搭建、需要参考同类项目结构 |
| [legacy-cpp-compilation-compatibility-checklist.md](legacy-cpp-compilation-compatibility-checklist.md) | 老旧 C++ 项目编译兼容性预检清单：6项预检（BLAS/Python/OpenCV/protobuf/C++标准/Boost），在编写Dockerfile前预判兼容性问题 | L1 实验性 | 5年以上C++项目编译、深度学习框架旧版本移植、跨OS版本编译 |
| [ops-sop-standard-template.md](ops-sop-standard-template.md) | 操作 SOP 标准化模板：从复盘报告提取可执行步骤，按"前置条件→快速开始→详细步骤→验证→故障排查→关联文档"结构组织，确保知识可执行化 | L1 实验性 | 项目复盘后需产出操作手册、技术任务标准化流程文档、知识转化闭环 |
| [python-wheel-dependency-audit-wda4.md](python-wheel-dependency-audit-wda4.md) | Python Wheel依赖审计四步法（WDA-4）：静态import扫描→传递/动态依赖补全→声明格式验证→Docker环境同步+端到端验证，系统性确保pyproject.toml依赖声明完整 | L1 实验性 | Python wheel发布前依赖检查、requirements.txt迁移pyproject.toml、多环境依赖一致性验证、ModuleNotFoundError根因排查 |
| [cross-migration-link-fix-sop.md](cross-migration-link-fix-sop.md) | 跨迁移断链批量修复四步桶分法（P-Link-Migrate-v1）：A桶绝对路径批处理→B桶相对路径深度自动修→C桶不存在占位降级内联→复检归零，覆盖盘符迁移/原子拆分/vendor换源场景 | L1 实验性 | 盘符/主机拷贝、原子化目录重构后、vendor大版本升级、单轮本地断链≥20且50%含盘符绝对路径 |
| [external-url-dead-bucket-fix-sop.md](external-url-dead-bucket-fix-sop.md) | 外部URL死链分桶治理SOP（P-Link-ExtBucket-v1）：去超时噪声→按二级域分桶→A桶URL迁移纠正/B桶内联失效注记/C桶白名单保留→清缓存复检，统计口径必须三列拆分 | L1 实验性 | 外链硬错误≥10条、3+域名各≥2条、BibTeX文献管理、博客友链页死链清理 |

## 成熟度定义

| 等级 | 定义 | 验证条件 |
|------|------|---------|
| L1 实验性 | 仅 1 次成功案例，待更多验证 | 验证次数 = 1 |
| L2 已验证 | ≥ 2 次成功案例，模式稳定 | 验证次数 ≥ 2 |
| L3 可复用 | 已被其他任务复用，有文档化示例 | 复用次数 ≥ 1 |

> 详细评估标准见 [patterns/README.md](../README.md#模式成熟度评估标准)。

## 使用方式

1. 根据场景查找匹配模式
2. 阅读模式正文了解规则与正反例
3. 按模式规则执行操作
4. 验证后更新模式成熟度（若适用）