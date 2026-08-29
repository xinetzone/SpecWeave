---
id: "source-stability-gate"
domain: "methodology"
layer: "methodology"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "basic"
source: "../../../../../../docs/retrospective/reports/concepts/milestone/jira-skill-wiki-vendor-sync-milestone-20260828.md#模式-E-1信源稳定性门"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/source-stability-gate.toml"
rules: []
references: []
skills:
  - "source-code-to-okf-wiki"
related_patterns:
  - "source-anchor-verification-protocol"
  - "file-existence-verification-gate"
  - "source-code-to-okf-wiki-workflow"
  - "okf-sources-path-normalization"
  - "cross-migration-link-fix-sop"
tags: ["信源稳定性", "路径断裂", "质量门", "文档生成", "vendor子模块", "临时目录", "file:///引用", "持久性验证"]
---
# 信源稳定性门（Source Stability Gate）

## 模式概述

从外部源码或本地克隆目录生成包含 `file:///` 绝对路径引用的文档时，必须在生成前将信源分类为 stable/temporary，并对 temporary 信源执行升级或标注，防止文档生成后信源目录被清理导致引用断裂。

> **术语界定**：本模式中的"稳定性"特指**信源路径的持久存在性**（路径指向的目录在文档生命周期内不被删除/迁移），而非信源内容的不变性（API 是否变更）。后者由版本锁定（git tag/commit hash）和内容同步机制保障。

本模式解决的核心问题是**"路径断裂延迟"**：文档生成时所有路径引用均有效（因为临时目录尚存在），审查通过后临时目录被删除，引用才断裂——断裂在生成和审查阶段不可见。这与 [source-anchor-verification-protocol](source-anchor-verification-protocol.md)（解决行号准确度）和 [file-existence-verification-gate](file-existence-verification-gate.md)（解决产出物存在性）共同构成源码引用质量的三层防护：

| 层次 | 防护维度 | 对应模式 | 验证时机 |
|------|---------|---------|---------|
| 输入层 | 信源路径是否持久存在 | **本模式** | 文档生成**前** |
| 内容层 | 行号/API签名是否准确 | source-anchor-verification-protocol | 研究→编写**跨阶段** |
| 输出层 | 产出文件是否真实创建 | file-existence-verification-gate | 文件创建**后** |

## 问题背景

AI 辅助从源码生成文档时存在一个结构性盲区——**内容审查通过 ≠ 引用可持续**：

> **`file:///` 是什么？** 这是 Markdown/HTML 中引用本地文件的 URI scheme（如 `[源码](file:///d:/AI/vendor/jira-skill/src/changelog.py#L10)`），OKF Wiki 等知识库规范使用此格式建立文档到源码的可点击追溯链接。与 `https://` 不同，`file:///` 引用指向本地文件系统，受本地目录生命周期影响。

1. **生命周期不匹配**：文档是长期资产（月/年级别），临时克隆目录是短期资源（小时/天级别），两者生命周期存在数量级差异
2. **断裂延迟暴露**：文档生成时 `file:///` 路径全部可达（临时目录存在），内容审查验证 API 名称和交叉链接均通过，但无人验证信源路径的持久性
3. **清理触发断裂**：临时目录在文档生成后被清理（磁盘回收、环境重置、CI runner 销毁），文档中的路径引用立即失效
4. **绝对路径绑定环境**：硬编码开发者个人目录路径（如 `d:\AI\.chaos\libs\...`），换机器、换用户、换盘符即断裂

这类似于软件工程中的"悬垂指针"问题——指针在赋值时有效，但指向的内存被释放后访问即崩溃。区别在于：悬垂指针在运行时立即报错，而文档路径断裂是静默的，只有读者点击链接时才发现。

**业务影响**：断链不仅是技术问题——文档可信度下降（读者无法验证声明）、知识传承受阻（新人无法通过链接找到源码）、合规审计失败（受控文档中引用的源码不可追溯）。在 AI Agent 自主工作流中，Agent 可能自动创建临时目录、生成文档、然后自动清理，断裂风险比人工操作更高。

## 核心做法（5步预检流程）

### 第一步：信源分类

在生成文档前，将所有信源路径分类为 `stable` 或 `temporary`：

| 分类 | 判据 | 典型路径特征 | 持久性预期 |
|------|------|-------------|-----------|
| `stable` | 纳入版本控制或系统级安装 | git submodule、vendor/目录、系统包安装路径、版本化发布包 | 与仓库同生命周期 |
| `temporary` | 临时创建、可能被自动清理 | 临时克隆、/tmp、.cache、AppData/Local/Temp、开发者个人目录、CI workspace | 小时/天级别 |

**灰色地带信源**（需根据团队约定判定）：
- 网络挂载盘/NAS：取决于挂载策略和备份机制，若有快照和权限管控可视为 stable，否则按 temporary 处理
- Docker volume/conda 环境：容器或环境重建后数据可能丢失，默认按 temporary 处理
- 云端 IDE 工作区（Codespaces/Gitpod）：环境销毁后文件不保留，按 temporary 处理，但模式的核心二分法仍然成立——只需将 stable 对应到持久化存储（对象存储、版本化仓库）

**自动化判据**：路径中包含 `.chaos`、`.tmp`、`/tmp/`、`AppData/Local/Temp`、`node_modules/.cache` 等特征段，即为 `temporary`。

### 第二步：临时信源升级

若信源为 `temporary`，在生成文档前必须升级为 `stable`，三选一：

1. **注册为 git submodule**：固定到具体 tag/commit，纳入 vendor/ 管理（推荐用于第三方源码，参见 [VENDOR-INTEGRATION.md](../../../../../VENDOR-INTEGRATION.md)）
2. **复制到版本化目录**：将信源复制到仓库内的 `vendor/` 或 `external/` 目录并提交（适用于自有代码或无法使用 submodule 的场景）
3. **记录不可变坐标**：记录确切的 commit hash + 远程仓库地址 + 获取方式（适用于无法本地存储的大型信源，文档中不使用 `file:///` 引用而使用坐标引用）

**选型决策**：
- 第三方开源代码 → 选项1（submodule），保留上游历史和许可证合规
- 自有/内部代码 → 选项2（版本化目录），直接纳入主仓库版本控制
- 大型二进制/数据集 → 选项3（不可变坐标），避免仓库膨胀

升级完成后，文档中的路径引用指向升级后的 stable 位置。

### 第三步：路径引用生成

文档中的 `file:///` 引用遵循以下规则：

- 只指向 `stable` 信源路径
- 若必须引用 `temporary` 信源（如调试日志、临时分析结果），在引用处标注 `transient: true` 和预期清理日期
- 优先使用相对路径而非绝对路径，减少环境绑定
- 路径中不含开发者用户名、个人目录等环境特定段

### 第四步：清理前扫描

删除任何目录前（尤其是临时克隆目录），执行引用扫描：

```bash
# 删除前确认无文档引用该路径
grep -r "<待删除目录路径>" docs/
# 或在 PowerShell 中
Select-String -Path "docs\**\*.md" -Pattern "<待删除目录路径>"
```

- 零匹配：可安全删除
- 有匹配：先更新文档中的路径引用，再删除目录

### 第五步：持久性验证

在文档生成的 V（验证）阶段，对所有 `file:///` URL 执行双重验证：

1. **存在性验证**：`Test-Path`（PowerShell）或 `test -f`（Bash）确认路径当前可达
2. **稳定性验证**：检查路径是否属于 `stable` 分类（不含临时目录特征段，且对应 git submodule 或版本化目录）

```powershell
# PowerShell：批量提取并验证 file:/// URL 的存在性和稳定性
$urls = Select-String -Path "docs\**\*.md" -Pattern "file:///([^)\s]+)" -AllMatches |
    ForEach-Object { $_.Matches.Groups[1].Value } | Sort-Object -Unique
foreach ($url in $urls) {
    $path = $url -replace '^file:///', '' -replace '/', '\'
    $exists = Test-Path $path
    $isStable = $path -notmatch '\.chaos|\.tmp|\\temp\\|AppData\\Local\\Temp|\.cache'
    Write-Host "[$($exists ? '✅' : '❌')][$($isStable ? 'stable' : 'TEMP')] $path"
}
```

仅有存在性验证不够——存在但即将被删除的路径是"定时炸弹"。

## 反模式（来自实际案例）

### 反模式1：生成即遗忘

从临时克隆目录生成文档后，直接删除克隆目录，不更新文档中的路径引用。

**实际案例**：初次转换使用 `.chaos/libs/tests/jira-skill/` 临时克隆作为信源生成 22 个 Wiki 文件，子模块引入后删除临时目录，导致 7 处 `file:///` URL 和 1 处 Windows 路径全部断裂。

**为什么错**：文档生成时路径有效，但文档的生命周期远超临时目录。删除操作未触发引用扫描，断裂在删除后才暴露。

**正确做法**：删除前执行第四步扫描，发现引用后先迁移路径到 stable 信源。

### 反模式2：审查只看内容不看信源

Review 验证了 API 名称正确性和交叉链接可达性，但未验证 `file:///` 路径指向的目录是否会持续存在。

**实际案例**：初次转换的 Review R1 标记为 pass，验证了 API 名称（21个脚本+10个关键API）和交叉链接，但 7 处指向 `.chaos` 临时目录的路径未被识别为风险。

**为什么错**：内容正确性和信源持久性是两个独立的质量维度。API 名称正确不代表路径持久；交叉链接可达不代表信源目录不会被删除。审查清单缺少"信源生命周期"检查项。

**正确做法**：V 阶段检查清单增加"信源稳定性验证"步骤，对所有 `file:///` 路径同时验证存在性和稳定性。

### 反模式3：绝对路径绑定开发者环境

在文档中硬编码 `d:\AI\.chaos\libs\...` 等开发者个人目录路径。

**为什么错**：换机器、换用户、换盘符、换操作系统，路径立即断裂。即使目录不被主动删除，环境迁移也会导致引用失效。

**正确做法**：使用相对路径或 git submodule 路径；文档中引用信源时使用仓库根相对路径而非文件系统绝对路径。

### 反模式4：先生成后稳定化

文档生成先于信源稳定化完成，生成后才补做 submodule 引入和路径迁移。

**实际案例**：时间线显示初次文档转换在 16:17 完成，vendor 子模块在 16:29 才引入——文档生成时 stable 信源尚不存在，只能引用临时目录。

**为什么错**：先生成后稳定化导致两次路径写入（初次写临时路径 + 同步时改稳定路径），增加返工成本和遗漏风险。

**正确做法**：在文档生成工作流的 R 阶段（事实采集）之前，先完成信源稳定化——确认信源已注册为 submodule 或位于版本化目录，再开始生成。

### 反模式5：扫描只匹配链接语法

清理前扫描或持久性验证只搜索 `file:///` Markdown 链接，遗漏 frontmatter 字段、正文散文、元数据声明中的裸路径引用。

**实际案例**：veadk-python Wiki 案例初次统计为 788 处 `file:///` 正斜杠链接引用；全量扫描时另在 11 个文件中发现 12 处反斜杠裸路径（frontmatter `source: d:\AI\.chaos\...` 字段）。若仅按链接语法迁移，这 12 处在临时目录清理后同样断裂。

**为什么错**：路径引用的语法载体不止 Markdown 链接一种——YAML frontmatter 字段、正文反引号包裹的散文路径、log/验证报告中的元数据声明，都是解析到文件系统位置的字符串。`grep file:///` 隐含假设了引用形态，而引用的本质是"文档中任何解析到文件系统位置的字符串"。

**正确做法**：扫描与验证模式同时覆盖三类形态：`file:///` 正斜杠 URL、Windows 反斜杠绝对路径（`X:\...`）、POSIX 绝对路径；Windows 环境下同一物理路径的正斜杠与反斜杠两种写法都要匹配。

## 检验标准

做完之后怎么知道做对了？

1. **全新克隆可解析**：文档中所有 `file:///` URL 在仓库全新克隆后可解析（不依赖开发者本地环境）
2. **无临时目录特征**：信源路径中不含 `.chaos`、`.tmp`、`/tmp/`、`AppData/Local/Temp`、`.cache` 等临时目录特征段
3. **信源有版本标注**：每个外部信源在文档 frontmatter 的 `sources` 中有对应的 stable 类型标注（git submodule 含 commit hash）
4. **清理扫描留痕**：临时目录删除前有 Grep 扫描记录，确认零匹配或已完成路径迁移
5. **V阶段双重验证**：V 阶段对每个 `file:///` URL 同时有存在性验证（Test-Path）和稳定性验证（路径分类检查）记录
6. **引用形态全覆盖**：扫描/验证的匹配模式覆盖 `file:///` 链接、反斜杠裸路径、POSIX 路径三类形态；Windows 环境下同一物理路径的两种斜杠写法均零残留

## 跨场景迁移示例

### 场景A：代码文档生成（当前领域）

Sphinx/MkDocs 文档生成时，`conf.py` 中引用的源码路径应指向已安装包（site-packages）或 git submodule，而非开发者的 virtualenv 路径（`.venv/lib/python3.x/site-packages/`）。virtualenv 随时可能被重建，路径中的 Python 版本号也会变化。

### 场景B：AI 训练数据索引（跨领域）

RAG 知识库的文档索引中记录的文件路径应指向版本化数据目录（如 `data/v2.1/`），而非下载缓存目录（`~/.cache/huggingface/`）。缓存可能被清理工具自动删除，且不同模型/版本可能使用不同缓存路径。索引应记录数据集名称+版本号+校验和，而非本地缓存路径。

### 场景C：CI/CD 构建产物引用（跨领域）

CI 流水线中构建产物的归档路径应指向持久化存储（artifact registry、S3 bucket），而非 runner 本地工作目录（`/home/runner/work/...`）。runner 销毁后本地路径即失效，后续阶段或调试时无法访问。应通过 artifact ID 或版本化 URL 引用构建产物。

### 场景D：数据分析报告溯源（跨领域）

Jupyter Notebook 或数据分析报告中引用的数据源路径应指向版本化数据湖路径或 DVC 管理的数据文件，而非分析师本地的 `~/Downloads/` 或 `/tmp/` 目录。报告交付后数据源可能被清理，其他分析师无法复现结果。

## 实际案例

### 案例：jira-skill Wiki 供应商源码同步（2026-08-28）

**背景**：将 jira-skill 第三方源码转换为 OKF Wiki 教程，初次使用临时克隆目录作为信源。

**失败过程**：
1. 16:17 初次转换完成，22 个 Wiki 文件生成，信源为 `.chaos/libs/tests/jira-skill/` 临时克隆
2. Review R1 通过——验证了 API 名称和交叉链接，但未检查信源路径持久性
3. 16:29 引入 `vendor/jira-skill` git submodule（v3.29.0），临时目录被删除
4. 7 处 `file:///` URL 和 1 处 Windows 路径全部断裂

**修复**：
- 7 处 `file:///` URL 从 `.chaos` 路径更新为 `vendor/jira-skill/` 路径
- 1 处 Windows 路径同步更新
- 17 个文件的 frontmatter 格式同步修正（规范演进的被动技术债）

**根本教训**：文档生成先于信源稳定化（反模式4），审查维度缺少信源持久性检查（反模式2），临时目录删除前未做引用扫描（反模式1）。

**验证数据**：
- 断裂引用数：8处（7个file:/// URL + 1个Windows路径）
- 返工变更量：501增/130删（含格式转换和事实修正）
- 初次审查到发现断裂的时间差：约12分钟（16:17生成 → 16:29删除后断裂）

**ROI 对比**：
- 未执行本模式：初次转换约25分钟 + 返工修复约40分钟（含规格编写、V阶段验证、审查）= 约65分钟
- 执行本模式：信源稳定化（submodule引入）约5分钟 + 文档生成约25分钟 = 约30分钟
- 净节省：约35分钟（54%），且避免了8处断链的质量风险

### 案例2：veadk-python Wiki 临时信源定时炸弹（2026-08-29 前瞻性验证）

**发现方式**：模式入库后，按第五步持久性验证脚本对 `knowledge/` 目录做全量扫描（预测性验证，非失败回溯）。

**背景**：veadk-python（火山引擎 Agent 开发框架）Wiki 教程位于 `knowledge/learning/03-agent-platforms-tools/01-domestic-platforms/veadk-python/`，共 64 个 Markdown 文件，8 个子目录。

**模式五步检测结果**：

| 步骤 | 检测项 | 结果 |
|------|--------|------|
| 第一步 | 信源分类 | `d:/AI/.chaos/libs/veadk-python/` 含 `.chaos` 特征段 → 自动判定 `temporary` |
| 第二步 | 升级状态 | ❌ 未升级：`.gitmodules` 无 veadk-python 条目，`vendor/veadk-python` 不存在 |
| 第三步 | 路径引用 | ❌ 788 处 `file:///` 引用全部硬编码 `.chaos` 绝对路径，分布于 41 个文件 |
| 第四步 | 清理扫描 | ⚠️ 临时克隆当前仍存在，一旦 `.chaos` 清理（如 2026-08-28 清理 jira-skill 临时克隆的同类操作），788 处引用将同时断裂 |
| 第五步 | 持久性验证 | 存在性验证当前通过（目录在）；稳定性验证全部失败（temporary 路径 + 无版本锁定） |

**与案例1的差异——风险更高的变体**：
- 案例1的临时克隆已固定在 v3.29.0 tag；案例2的克隆跟踪 `main` 分支（commit `7bd1207`，2026-08-05），**内容本身可随上游变更而漂移**，路径持久性和内容不变性双重缺失
- 案例1断裂规模为8处；案例2为788处，规模约100倍
- 案例1是失败后回溯（retrospective）；案例2是失效前预测检出（prospective），证明模式第一步的自动判据（路径特征段 → temporary）无需人工判断即可命中独立案例

**验证结论**：模式的检测步骤（第一/四/五步）在独立案例上零修改命中，预测有效性验证通过。

**修复闭环（2026-08-29 同日完成）**：按第二步升级方法执行修复并复验通过：

1. **升级信源**：注册 `vendor/veadk-python` submodule（`git@github.com:volcengine/veadk-python.git`，Apache-2.0），固定至 tag `1.0.10`（commit `ffbf2957`）。tag 选型经差异分析：`1.0.10` 是 Wiki 生成时 commit `7bd1207` 的祖先，其间 5 个 commit 全部为 Studio 前端特性，Wiki 引用的核心框架文件（`veadk/agent.py`、`veadk/runner.py`、`veadk/tools/`、`examples/` 等）在 1.0.10 中均存在，内容漂移风险归零
2. **批量替换**：41 个文件共 800 处引用迁移至 vendor 路径——788 处 `file:///` 正斜杠链接 + 12 处 frontmatter `source:` 反斜杠路径（第五步脚本最初只统计 `file:///`，反斜杠裸路径在替换前全量扫描中补获，提示第四步清理扫描的匹配模式必须覆盖两种斜杠变体）
3. **复验结果**：`.chaos` 残留 0 处；661 个严格 Markdown 链接（227 个唯一目标）**信源链接缺失 0**；另修复 1 处生成时即畸形的链接（`webui/` 缺 `veadk/` 路径段）
4. **附带发现（超出本模式边界）**：9 处 Wiki 内部导航链接生成时即断（缺少 `03-agent-platforms-tools/01-domestic-platforms/` 路径段，从未指向 `.chaos`），属输出层 file-existence-verification-gate 领域，另行处理

## 与其他模式的关系

| 关联模式 | 关系类型 | 关系说明 |
|---------|---------|---------|
| [source-anchor-verification-protocol.md](source-anchor-verification-protocol.md) | 姊妹模式 | 前者解决"行号准确度"的跨阶段传递，本模式解决"路径持久性"的生成前预检；两者分别防护内容层和输入层 |
| [file-existence-verification-gate.md](file-existence-verification-gate.md) | 互补模式 | 后者验证产出文件存在性（输出层），本模式验证信源路径持久性（输入层）；前者防"AI声称创建但实际没有"，本模式防"信源当时存在但后来消失" |
| [source-code-to-okf-wiki-workflow.md](source-code-to-okf-wiki-workflow.md) | 上位模式 | 本模式应内置于该工作流的 R 阶段之前作为预检清单（pre-flight checklist），在事实采集开始前自动执行信源分类和持久性验证 |
| [okf-sources-path-normalization.md](../../code-patterns/okf-sources-path-normalization.md) | 下游模式 | 后者解决 sources 字段的路径格式规范化（相对路径层级计算），本模式解决路径指向的信源是否持久存在；先稳定信源再规范化路径 |
| [cross-migration-link-fix-sop.md](../../process-patterns/cross-migration-link-fix-sop.md) | 补救模式 | 当信源稳定性门未执行导致断链后，使用跨迁移断链修复 SOP 进行批量修复 |

## 边界与选型

**何时使用本模式**：
- 从外部源码/仓库生成包含 `file:///` 或绝对路径引用的文档
- AI 智能体基于本地克隆/临时目录生成知识库
- 文档生命周期长于信源目录的预期生命周期
- 多人协作环境中文档需要跨机器/跨用户可达

**何时不需要本模式**：
- 纯外部 URL 引用（`https://` 不受本地文件生命周期影响）
- 临时笔记/草稿/个人备忘录（不需要长期持久性）
- 一次性分析脚本（脚本本身和输出都不纳入版本控制）
- 信源已为 stable 类型（git submodule、系统安装目录），直接生成即可

**轻量场景裁剪**：当信源数量 ≤3 个且均已确认为 stable 类型时，可跳过第一步分类和第二步升级，仅执行第五步持久性验证（存在性+稳定性检查）即可，无需全套5步流程。

**云端环境适用性**：GitHub Codespaces、Gitpod、AWS Cloud9 等云端 IDE 环境同样适用——环境销毁后本地文件不保留，stable 对应到持久化存储（git 仓库、对象存储、artifact registry），temporary 对应到环境本地存储。模式的核心二分法与部署形态无关。

**与 [source-anchor-verification-protocol](source-anchor-verification-protocol.md) 的选型**：

| 维度 | 本模式 | source-anchor-verification-protocol |
|------|--------|-------------------------------------|
| 防护对象 | 信源目录路径 | 源码行号/API签名 |
| 失效方式 | 目录被删除→路径不可达 | 行号漂移→指向错误位置 |
| 检测难度 | 断链可被 link-check 检测 | 行号偏差不报错，需人工/Grep校验 |
| 执行时机 | 文档生成**前** | 研究→编写**跨阶段** |
| 适用范围 | 任何含本地路径引用的文档 | 多阶段 sub-agent 协作的源码文档 |

两个模式可叠加使用：先用本模式确保信源路径持久，再用 source-anchor-verification-protocol 确保行号准确。

## Changelog

<!-- changelog -->
- 2026-08-29 | docs | v2.2：里程碑复盘（sc-20260829-veadk-source-stability-fix）补充反模式5「扫描只匹配链接语法」（案例2中12处frontmatter反斜杠裸路径初检漏统计）与检验标准第6条「引用形态全覆盖」
- 2026-08-29 | fix | v2.1：案例2修复闭环——注册 vendor/veadk-python submodule 固定 tag 1.0.10（ffbf295），41个文件800处引用（788处file:/// + 12处frontmatter反斜杠路径）迁移至 vendor 并复验信源链接缺失0；补充教训：清理扫描匹配模式须覆盖两种斜杠变体；记录9处输出层内部断链为边界外发现
- 2026-08-29 | validate | v2.0：第2个独立案例（veadk-python Wiki，64文件/788处file:///引用）前瞻性验证通过——模式五步检测零修改命中，成熟度 L1→L2，validation_count 1→2；发现更高风险变体（main分支跟踪克隆无tag锁定）；修复行动项待执行
- 2026-08-28 | create | v1.0：初始版本，L1 成熟度，源自 jira-skill Wiki 供应商源码同步里程碑复盘的模式 E-1 萃取
