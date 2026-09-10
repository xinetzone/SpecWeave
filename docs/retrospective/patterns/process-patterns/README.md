---
type: Pattern
id: "process-patterns-readme"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/process-patterns/README.toml"
---

# 流程模式索引（process-patterns）

本目录存放流程级可复用模式，聚焦于开发流程、构建流程、运维流程等宏观层面的最佳实践。

## 模式清单

| 模式 | 说明 | 成熟度 | 适用场景 |
|------|------|--------|---------|
| [app-execution-alias-file-not-found-repair-sop.md](app-execution-alias-file-not-found-repair-sop.md) | App Execution Alias 文件找不到修复 SOP：查包 Status→fsutil 解码别名核对目标版本→关实例→Add-AppxPackage -Register 重注册→Get-Command+Start-Process 双重验证，防止一见报错就卸载重装 | L1 实验性 | Windows 报错找不到 `...\WindowsApps\<app>.exe`、Store 应用别名瞬时失效、wt.exe/mspaint.exe/winget.exe 启动失败 |
| [container-build-env-optimization.md](container-build-env-optimization.md) | 容器化构建环境优化模式：镜像源优化+超时重试配置+命令链拆分+验证环节添加+多阶段构建，提升构建成功率和稳定性 | L2 已验证 | Docker镜像构建涉及网络依赖和复杂环境配置的场景 |
| [docker-build-network-resilience.md](docker-build-network-resilience.md) | Docker构建网络容错五步法：国内镜像源→本地COPY先于网络→非核心依赖容错→本地wheel后于网络依赖→核心验证最后执行，应对网络不稳定导致的构建失败 | L1 实验性 | 网络不稳定环境下的Docker构建、国内pip镜像源配置、核心vs非核心依赖分层安装 |
| [docker-entrypoint-two-step-reset.md](docker-entrypoint-two-step-reset.md) | Docker镜像ENTRYPOINT两步安全重置：commit+Dockerfile替代--change，应对docker commit --change在--entrypoint覆盖场景下静默失效 | L1 实验性 | Docker镜像导出/发布、容器以--entrypoint启动后commit |
| [release-gate-automated-verification.md](release-gate-automated-verification.md) | 发布门禁自动化验证：从最终产物加载→配置检查→回归测试→内容完整性→功能冒烟→符号可见性，输出PASS/FAIL报告 | L1 实验性 | 软件发布流程最后一步、Docker镜像/包/二进制产物验证 |
| [container-verify-script-permission-model.md](container-verify-script-permission-model.md) | 容器验证脚本权限安全模型：mkdtemp+显式chmod绕过entrypoint降权导致的Permission denied，区分基础设施错误与镜像质量错误 | L2 已验证 | conda环境镜像验证、含gosu entrypoint的镜像验证、CI门禁脚本 |
| [docker-build-reference-template-copy.md](docker-build-reference-template-copy.md) | Docker 构建系统参考模板复制法：识别参考项目→提取目录骨架→适配替换→逐层构建验证→补充文档，加速新项目Docker构建系统搭建 | L1 实验性 | 新项目Docker化、构建系统从零搭建、需要参考同类项目结构 |
| [docker-cross-os-internal-build.md](docker-cross-os-internal-build.md) | 跨OS Docker构建"编辑在外、构建在内"模式：bind mount用于编辑同步，构建目录放在容器原生文件系统（ext4/Docker卷），规避CRLF/权限/文件锁/临时文件等跨OS隐式转换问题 | L2 已验证 | Windows/macOS宿主+Linux容器编译C/C++/Rust/Go、CI/CD跨OS runner、autotools/cmake构建 |
| [legacy-cpp-compilation-compatibility-checklist.md](legacy-cpp-compilation-compatibility-checklist.md) | 老旧 C++ 项目编译兼容性预检清单：6项预检（BLAS/Python/OpenCV/protobuf/C++标准/Boost），在编写Dockerfile前预判兼容性问题 | L1 实验性 | 5年以上C++项目编译、深度学习框架旧版本移植、跨OS版本编译 |
| [ops-sop-standard-template.md](ops-sop-standard-template.md) | 操作 SOP 标准化模板：从复盘报告提取可执行步骤，按"前置条件→快速开始→详细步骤→验证→故障排查→关联文档"结构组织，确保知识可执行化 | L1 实验性 | 项目复盘后需产出操作手册、技术任务标准化流程文档、知识转化闭环 |
| [python-wheel-dependency-audit-wda4.md](python-wheel-dependency-audit-wda4.md) | Python Wheel依赖审计四步法（WDA-4）：静态import扫描→传递/动态依赖补全→声明格式验证→Docker环境同步+端到端验证，系统性确保pyproject.toml依赖声明完整 | L1 实验性 | Python wheel发布前依赖检查、requirements.txt迁移pyproject.toml、多环境依赖一致性验证、ModuleNotFoundError根因排查 |
| [cross-migration-link-fix-sop.md](cross-migration-link-fix-sop.md) | 跨迁移断链批量修复四步桶分法（P-Link-Migrate-v1）：A桶绝对路径批处理→B桶相对路径深度自动修→C桶不存在占位降级内联→复检归零，覆盖盘符迁移/原子拆分/vendor换源场景 | L1 实验性 | 盘符/主机拷贝、原子化目录重构后、vendor大版本升级、单轮本地断链≥20且50%含盘符绝对路径 |
| [external-url-dead-bucket-fix-sop.md](external-url-dead-bucket-fix-sop.md) | 外部URL死链分桶治理SOP（P-Link-ExtBucket-v1）：去超时噪声→按二级域分桶→A桶URL迁移纠正/B桶内联失效注记/C桶白名单保留→清缓存复检，统计口径必须三列拆分 | L1 实验性 | 外链硬错误≥10条、3+域名各≥2条、BibTeX文献管理、博客友链页死链清理 |
| [monorepo-ci-blindspot-detection.md](monorepo-ci-blindspot-detection.md) | Monorepo子项目CI盲区检测五步法：审计根testpaths→审计子项目配置→collect-only计数对比→检查构建命令→选择修复方案，解决主CI绿灯但子项目测试从未执行的陷阱 | L1 候选 | pytest/pnpm/cargo/gradle等任意Monorepo项目、子项目/子模块CI覆盖审计、新增子项目后的CI验证、CI配置重构验证 |
| [pdf-book-to-okf-wiki.md](pdf-book-to-okf-wiki.md) | PDF书籍→OKF-MyST Wiki四阶段工作流：环境准备→结构探查→工具降级链→清洗转换→确定性校验→Sphinx构建验证，含三层忠实边界与已知边界 | L1 实验性 | 纯文本排版书籍/论文PDF→OKF规范Markdown知识库→Sphinx+MyST+mystx静态Wiki |
| [okf-bundle-toctree-repair-workflow.md](okf-bundle-toctree-repair-workflow.md) | OKF bundle 目录树完整性修复工作流：全量扫描三类问题（缺index.md/缺toctree/缺条目）→建索引/追加/补充分类处理→精确追加定位闭合→dry-run验证→git兜底回滚，修复toc.not_included警告 | L1 实验性 | Sphinx/MyST知识库出现大量toc.not_included警告、OKF bundle目录树不完整、任意目录树驱动内容组织批量补导航 |
| [svf-compiler-migration.md](svf-compiler-migration.md) | SVF 编译器迁移模式（Spike-Validate-Fallback）：识别ABI变体→最小Spike→失败记录→回退设计→最复杂模块预验证→全量构建→决策记录七步，防止直接全量构建返工和sed降级补丁技术债 | L2 已验证 | 原生编译器（Nuitka/Cython/mypyc）迁移新Python版本或ABI变体、CUDA/Emscripten工具链升级、编译器兼容性未知的场景 |
| [vhdx-two-phase-recovery-sop.md](vhdx-two-phase-recovery-sop.md) | VHDX 二相回收 SOP：sparse 在线相与 compact 离线相互斥二选一；离线相含停 wslservice+vmcompute、清 sparse 标志、diskpart compact 全流程，含 6 类故障排查与 5 个实战反模式 | L2 已验证 | WSL2/Podman machine/Hyper-V 虚拟磁盘 vhdx 膨胀回收、系统盘空间治理、容器镜像清理后宿主空间未归还 |
| [nested-engine-storage-externalize.md](nested-engine-storage-externalize.md) | 嵌套引擎存储卷外置模式：容器内 podman-in-podman/dinod 存储指向命名卷或显式挂载，避免镜像层写可写层形成黑洞；含双重不可见排查路径与僵尸容器处置，与 VHDX 二相回收构成预防/治理对 | L1 实验性 | 常驻容器内嵌套构建、CI docker-in-docker、可写层膨胀监控、容器磁盘配额治理 |
| [nested-disk-blindspot-diagnosis.md](nested-disk-blindspot-diagnosis.md) | 嵌套容器磁盘盲区诊断模式：双重不可见（宿主 system df 只见总量 + 容器内 du 权限遮蔽低估4倍）下的四层下钻诊断链（system df→df/du矛盾→root du→UpperDir diff），结论须全链条数字交叉验证闭合 | L1 实验性 | 多层虚拟化栈磁盘占用对不上账、可写层异常膨胀定位、僵尸容器排查、vhdx 增速与挂载内容不匹配 |
| [nested-disk-blindspot-diagnosis-sop.md](nested-disk-blindspot-diagnosis-sop.md) | 嵌套容器磁盘盲区诊断 SOP：四层下钻链的可执行细化（L1预警→L2矛盾检测→L3提权核实→L4 UpperDir解剖→L5数字闭合验收），含僵尸容器处置、7类故障排查与 lsof inode 泄漏分支，每层判定阈值与命令 | L1 实验性 | 同上模式的实操执行：宿主磁盘对不上账时的标准排查手册 |
| [submodule-ssh-stall-recovery-sop.md](submodule-ssh-stall-recovery-sop.md) | 子模块 SSH 停滞换源恢复 SOP：确诊双通道差异→杀竞争传输保终端→残骸双清（工作区+.git/modules）→GIT_CONFIG_* 环境变量 insteadOf 整树换源→受控重跑→原命令退出码0+全树零脏标记验收，含 pull 后 pin 漂移收敛与 7 条反模式 | L2 已验证 | git submodule update 克隆停滞/Unable to find current revision、.gitmodules 用 SSH URL 而本机 SSH 大传输挂死、npm git+ssh 依赖停滞、CI 无 SSH key 场景 |

## 成熟度定义

| 等级 | 定义 | 验证条件 |
|------|------|---------|
| L1 实验性 | 仅 1 次成功案例，待更多验证 | 验证次数 = 1 |
| L2 已验证 | ≥ 2 次成功案例，模式稳定 | 验证次数 ≥ 2 |
| L3 可复用 | 已被其他任务复用，有文档化示例 | 复用次数 ≥ 1 |

> 详细评估标准见 [patterns/README.md](../index.md#模式成熟度评估标准)。

## 使用方式

1. 根据场景查找匹配模式
2. 阅读模式正文了解规则与正反例
3. 按模式规则执行操作
4. 验证后更新模式成熟度（若适用）