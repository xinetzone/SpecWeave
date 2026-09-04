# 腾讯 AI 生态 OKF Wiki 教程 - 验证清单

## 目录结构与规范
- [x] `bundles/tencent/index.md` 存在且含 `okf_version: "0.2"` frontmatter
- [x] `bundles/tencent/codebuddy/` 含完整子目录（concepts/examples/references）+ index.md + log.md
- [x] `bundles/tencent/ai-infra-guard/` 含完整子目录 + index.md + log.md
- [x] `bundles/tencent/octop/` 含完整子目录 + index.md + log.md
- [x] `bundles/tencent/ncnn/` 含完整子目录 + index.md + log.md
- [x] 每个知识束含 `spec/facts.md`（R 阶段事实清单）和 `spec/insights.md`（I 阶段洞察）
- [x] 子目录 index.md 不含 frontmatter（仅根 index.md 保留 okf_version）

## Frontmatter 合规
- [x] 每个非保留 .md 文件含 `type` 字段（Concept/Example/Reference）
- [x] 每个文档含 `title`、`description`（30-80字）、`tags`
- [x] 每个文档含 `generated: { by, at }` 和 `verified: { by, at }`
- [x] 每个文档含 `status: stable` 和 `stale_after` 日期
- [x] 每个文档含 `sources` 字段指向 references/ 下已存在的信源文件
- [x] generated.at 使用 ISO 8601 格式

## CodeBuddy 产品知识束
- [x] references/ 含 6 个信源文件（ide/docs-intro/cli/npc/workbuddy/security）
- [x] concepts/ 覆盖 5+ 产品形态（IDE/CLI/NPC/WorkBuddy/Security）
- [x] examples/ 含 2+ 使用示例
- [x] 产品特性描述与网页原文一致（安装命令、功能列表、定价信息）
- [x] CLI 安装命令 `npm install -g @tencent-ai/codebuddy-code` 准确
- [x] NPC 与 CNB 平台关系描述准确
- [x] Security 六步闭环和 CVE 战绩数据准确（18漏洞/14高危/18 CVE/12项目）

## AI-Infra-Guard 源码知识束
- [x] Grep 验证文档中所有 Go 结构体/函数名在 `external/libs/ai/Tencent/AI-Infra-Guard/` 中存在
- [x] 五种任务类型名称与源码一致（AI-Infra-Scan/Mcp-Scan/Model-Redteam-Report/Agent-Scan/Skill-Scan）
- [x] 指纹 DSL 操作符与 common/fingerprints/parser/ 实现一致
- [x] 漏洞版本范围 DSL 与 pkg/vulstruct/ 一致
- [x] WebSocket 消息类型（newPlanStep/statusUpdate/toolUsed/actionLog/resultUpdate）准确
- [x] Python 子模块路径正确（mcp-scan/main.py、agent-scan/main.py、AIG-PromptSecurity/）
- [x] 数据规模描述准确（146 指纹/2014 CVE/15 MCP插件/17 评测集）

## Octop 源码知识束
- [x] Grep 验证 OctopServer 在 src/octop/infra/server.py 中存在
- [x] Grep 验证 AgentManager 在 src/octop/infra/agents/manager.py 中存在
- [x] Grep 验证 Gateway 在 src/octop/infra/gateway/gateway.py 中存在
- [x] Grep 验证 SharedServices/RepoBundle 在 src/octop/infra/db/services.py 中存在
- [x] Grep 验证 _LazyCLI 在 src/octop/cli/main.py 中存在
- [x] Grep 验证 PathLayout 在 src/octop/infra/utils/paths.py 中存在
- [x] 20 个 CLI 子命令与 cli/registry.py COMMANDS 字典完全一致
- [x] 四层架构禁令（infra↛api/cli/launch）与 AGENTS.md 一致
- [x] ACP 四个内置 runner（opencode/codebuddy/claude_code/codex）与 docs/acp.md 一致
- [x] 数据库支持（SQLite WAL + PostgreSQL）描述准确
- [x] harness-* 外部依赖标注为外部包，未虚构其内部 API

## ncnn 源码知识束
- [x] Grep 验证 Net/Extractor 在 src/net.h 中存在
- [x] Grep 验证 Mat 在 src/mat.h 中存在，dims/w/h/d/c/elempack/cstep 字段准确
- [x] Grep 验证 Layer 在 src/layer.h 中存在，虚函数签名准确
- [x] Grep 验证 Blob 在 src/blob.h 中存在
- [x] Grep 验证 Option 在 src/option.h 中存在，关键选项默认值准确
- [x] Grep 验证 Allocator/PoolAllocator/UnlockedPoolAllocator 在 src/allocator.h 中存在
- [x] Grep 验证 VkAllocator/VkBlobAllocator/VkWeightAllocator 在 src/allocator.h 中存在
- [x] Grep 验证 ParamDict/ModelBin 在 src/ 中存在
- [x] Grep 验证 Vulkan 相关类（VkMat/VkCompute/Pipeline/GpuDevice）在 src/ 中存在
- [x] CMake 构建选项名称与 CMakeLists.txt 一致（NCNN_VULKAN/NCNN_INT8/NCNN_PYTHON 等）
- [x] 算子层按类别代表性覆盖，未逐个罗列 120+ 算子
- [x] Python 绑定 pybind11 文件路径准确（python/src/pybind11_*.h）

## 链接与路径
- [x] 所有交叉链接使用 `/` 开头 bundle-relative 路径
- [x] 无 `../` 相对路径交叉链接
- [x] 无断链（所有链接目标文件存在）
- [x] 无 `file:///` 绝对路径（文档内部引用）
- [x] 文件名使用 kebab-case 纯英文

## 生成纪律
- [x] references/ 文件先于 concepts/examples 生成
- [x] index.md 最后生成
- [x] 每批生成文档数 ≤ 7
- [x] facts.md 中无推断性表述（"用于"/"目的是"/"设计为"）
- [x] insights.md 含洞察四元组（陈述/证据/反常识/行动）

## 内容质量
- [x] 正文中文撰写，英文术语首次出现时括号注释
- [x] 每个概念文档 500-5000 字，用 `##` 分节
- [x] 每个文档结尾有"## 相关概念"章节
- [x] 代码块标注语言
- [x] 示例文档包含完整可运行代码或清晰的使用步骤
