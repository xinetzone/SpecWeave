# 分类索引：operations

- [返回分类总索引](../category-index.md)
- [返回知识库首页](../README.md)
- [按标签检索](../tags/README.md)

> 本分片收录 **1** 个子分类，共 **21** 条条目。

### operations

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Docker镜像缓存→WSL2发行版迁移操作指南](../operations/docker-cache-wsl-migration-guide.md) |  | 2026-08-18 | docker-cache、wsl2、podman、wsl-import、rootfs、image-migration、offline-environment |
| [EPUB 转 Markdown 转换方案系统性调研报告](../operations/epub-to-markdown-conversion-research.md) |  | 2026-08-19 | epub、markdown、pandoc、calibre、ebooklib、转换方案 |
| [Discourse论坛（forum.trae.cn）自动化操作指南](../operations/forum-automation.md) | 基于Trae IDE集成浏览器（integrated_browser MCP）和Playwright Python脚本操作forum.trae.cn论坛的完整指南，包含DOM选择器参考、Ember框架感知操作方法、操作序列模板、JavaScript代码片段、独立Python脚本使用、故障排查和长期方案（@discourse/mcp）接入指南。v2.1更新：精确化DOM选择器、新增diagnoseButtons诊断函数、补充MCP参数陷阱警告、补全误操作恢复方法、新增MCP vs Playwright操作区别对照表。 | 2026-06-30 | discourse、论坛、自动化、browser、mcp、playwright、发布 |
| [Frontmatter 路径与链接批量修复流程指南](../operations/frontmatter-link-batch-repair-guide.md) | 大规模 frontmatter 路径与 Markdown 链接批量修复的完整流程指南：问题分类诊断、8 阶段分层修复策略、external 标记约定、LF 行尾保留、TOML source 覆盖问题处理，附 8 个自动化脚本的使用参考 | 2026-07-10 | frontmatter、链接修复、批量修复、check-links、路径规范化、external标记 |
| [HTML 正文提取操作指南](../operations/html-body-extraction.md) | HTML 正文提取双方案：正则提取（首选）与边界标记索引截取法（兜底），含 HTML 清洗六步流程，适用于复杂嵌套 HTML 容器 | 2026-06-29 | html、正文提取、正则、索引截取、边界标记、html清洗、降级策略 |
| [临时知识库归档规则正文](../operations/p0-02-knowledge-archive-rules.md) | 定义临时知识库与正式知识库的分层关系、分类规则、状态与优先级字段、最小元数据、自动归档触发条件、正式目录映射、保留与回退策略、索引结构、一致性校验项和异常修复闭环。 |  | - |
| [任务分类与追踪骨架说明](../operations/p0-05-task-classification-skeleton.md) | 定义 tasks/ 目录的三维正式分类骨架（task-types / business-domains / project-stages）、使用原则、临时历史目录定位和查找入口。 |  | - |
| [Docker 镜像构建与运行手册摘要](../operations/p1-06-docker-image-build-run.md) | Conda/Podman 镜像构建与运行手册，覆盖 Dockerfile 片段、构建命令、交互运行与挂载工作目录的标准操作。 |  | - |
| [测试依赖安装说明](../operations/p1-07-test-deps-install.md) | 工作区测试环境的依赖安装命令，覆盖 tqdm、tensorboard、pytorch-ignite 等测试依赖的 pip 安装。 |  | - |
| [Windows 沙盒安装与配置操作手册摘要](../operations/p1-08-windows-sandbox-guide.md) | Windows 沙盒从零到可用的安装与配置手册，覆盖版本检查、虚拟化启用、图形界面/PowerShell 启用、隔离验证、网络与共享策略、.wsb 一键启动模板及常见故障排查。 |  | - |
| [DaoMind 部署上线指南摘要](../operations/p1-11-daomind-deployment-guide.md) | DaoMind 部署上线操作手册，覆盖 GitHub Pages 文档站部署、create-daomind CLI 的 npm 发布、部署验证、上线后监控与常见排错速查。 |  | - |
| [TVM VTA 容器构建与 Nuitka 打包流水线说明](../operations/p2-14-tvm-vta-nuitka-pipeline.md) | hub/sync 本地附加分析说明，覆盖 TVM VTA 构建容器（Podman + Invoke）与 Nuitka wheel 打包流水线的目录导航、命令入口、跨平台连接方式与报告约定。 |  | - |
| [npm monorepo 包发布与 GitHub Release 操作流程](../operations/p2-15-npm-github-release-guide.md) | TypeScript monorepo 项目使用 pnpm 工作区发布 npm 包并创建 GitHub Release 的完整操作流程与故障排查指南 |  | - |
| [关键路径工具失败降级矩阵](../operations/tool-failure-degradation-matrix.md) | 关键路径工具失败的三级降级决策矩阵：网页内容获取、文件搜索、命令执行、子代理委派四类关键路径的降级策略、触发条件与决策流程 | 2026-07-06 | 工具降级、降级矩阵、webfetch、defuddle、浏览器mcp、关键路径、三级降级、标准化 |
| [Tuya IPC 最小闭环跑通路径](../operations/tuya-ipc-minimal-closed-loop.md) | 一条可落地执行、可观测验收的 Tuya IPC（网络摄像机）端-云-手机最小闭环跑通路径：先明确最小假设，再按步骤给出依赖/验收/排查，并附依赖关系图与闭环验收总表。 | 2026-06-30 | tuya、ipc、iot、闭环、配网、音视频、设备绑定、事件上报、联调、排查、验收 |
| [vendor/flexloop 功能集成方案决策指南](../operations/vendor-flexloop-integration-guide.md) | 当需要在 SpecWeave 中新增或使用 flexloop 相关功能时，基于三区域边界模型和四不原则的5种合规集成路径决策指南 | 2026-06-29 | vendor、flexloop、agentforge、submodule、集成方案、三区域模型、四不原则 |
| [微信公众号文章内容提取操作指南](../operations/wechat-mp-content-extraction.md) | 微信公众号文章内容提取双路径决策模型：defuddle CLI 与 PowerShell Invoke-WebRequest 互为兜底，含边界标记索引截取法作为正则失败时的兜底方案 | 2026-06-29 | 微信公众号、内容提取、defuddle、powershell、invoke-webrequest、html提取、反爬、降级策略 |
| [Windows平台兼容性手册：AI智能体执行任务陷阱系统化指南](../operations/windows-platform-compatibility-guide.md) | 系统化记录 Windows 平台执行任务时的10类陷阱（编码、URL解析、路径分隔符、命令链接、引号差异、heredoc、管道、脚本扩展、行尾符、环境变量），整合项目已有4个Windows文档并提供统一索引与快速诊断流程 | 2026-07-06 | windows、powershell、platform-compatibility、url-parsing、encoding、path-separator、shell-differences、quoting、line-ending、ai-agent |
| [Windows PowerShell 不支持 heredoc 语法](../operations/windows-powershell-heredoc.md) | 记录 Windows PowerShell 环境下 heredoc 语法不可用的替代方案 | 2026-06-23 | windows、powershell、shell、heredoc、git |
| [Windows PowerShell 文本管道可能污染中文文档输出](../operations/windows-powershell-pipe-utf8.md) | 记录 Windows PowerShell 下将 Python 中文 stdout 通过文本管道写入文件时可能发生的转码污染，以及推荐的安全写回方案 | 2026-06-30 | windows、powershell、encoding、utf-8、pipe、set-content、python、docs |
| [Windows终端UTF-8编码完整配置指南](../operations/windows-terminal-utf8-complete-guide.md) | 系统性解决Windows终端中文乱码问题的完整指南，涵盖系统级/用户级/项目级三层配置方案 | 2026-07-01 | windows、powershell、cmd、utf-8、encoding、gbk、chcp、乱码 |

---

*索引自动生成于 2026-08-21 15:32:36*
