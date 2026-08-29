---
id: "source-path-debt-triage-20260829"
date: "2026-08-29"
type: "audit-report"
domain: "methodology"
source: "./veadk-a3-a6-closure-retrospective-20260829.md"
methodology: "信源稳定性门模式（source-stability-gate v2.3）+ 历史快照三分法"
gate: "GATE-SPS"
tags: ["信源稳定性", "技术债分诊", "GATE-SPS", "审计", "d:/spaces", "历史快照"]
---

# 全仓信源路径存量债务分诊审计（ACT-3）

> 本报告是 veadk 信源稳定性门系列行动项 **ACT-3** 的交付物：在 GATE-SPS 锚点假阳性修复（ba8272c6）与锚点行号越界复验（a2e37b25）之后，全仓 audit 基线首次可信，据此对全部失效路径引用做三分法分诊，回答"哪些该修、哪些不该动、哪些是工具自己的误报"。

## 一、审计基线（2026-08-29 实测）

| 指标 | 数值 | 说明 |
|------|------|------|
| 扫描 Markdown 文件 | 13,583 | 持久工作区（.chaos/vendor/.git 等目录级剪枝） |
| 路径引用总数 | 7,002 | link/frontmatter/prose 三类载体 |
| exists=False（失效） | **4,294** | 本次分诊对象 |
| temporary（临时信源） | 1,123 | 含 .chaos/.tmp/Temp 特征段 |
| env-bound（环境绑定） | 3,170 | 绝对路径但无临时/稳定特征 |
| 锚点行越界 | **0** | ACT-2 检出 10 条已全部修复（5207d558） |

> 数据来源：`python .agents/scripts/check-source-path-stability.py --json` 全仓扫描 + 双维聚类脚本（按 token 路径桶 × 引用来源区域交叉统计）。

## 二、三分法分诊结果

### A 类：历史快照证据（不改写，约 2,750 条）

事实表、复盘报告、spec 工作产物、模式案例中的时点路径，其语义是"记录当时发生了什么"，改写即销毁证据。与 [信源稳定性门模式 v2.3](../../../../../.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/source-stability-gate.md) 案例3"不改写边界"同源。

| 来源区域 | 失效数 | 主要内容 | 处置 |
|---------|-------:|---------|------|
| `.trae/specs/` 规划目录 | 1,298 | sympy-okf-wiki/facts.md（318 条 d:/spaces）、caffex gap 分析（45）、各 spec facts/tasks | 保留；spec 产物归档后即历史 |
| `docs/retrospective/reports/` | 599 | 各里程碑复盘事实表中的时点路径 | 保留 |
| awesome-okf 分析文档 | 435 | facts/findings 类事实采集（d:/spaces 230、POSIX 107） | 保留 |
| patterns/ 模式库 | 253 | 教学反例正文（.chaos//tmp//opt 等讲授对象） | 保留 |
| `.agents/docs/retrospective/` | 77 | 早期复盘归档 | 保留 |
| projects/ 子模块文档 | 89 | xuanspace caffe-ffi 复盘等 | **子模块内，主仓不可改，登记上报** |

### B 类：教学反例与环境正确路径（不改写，约 1,050 条）

路径在文档语境中是**正确内容**而非失效引用：

| 形态 | 数量 | 判定依据 |
|------|-----:|---------|
| `/opt/...` POSIX 路径 | 592 | 大宗在 apps/docker-images/devcontainer-base（134 条）——容器内路径在 Docker 教学文档中本就正确，Windows 主机不存在属预期 |
| `/usr/...`、`/tmp/...` | 229 | 规范文档/脚本教学中的 Linux 路径示例；代码块内 22 条 |
| AGENTS.md / .agents 规范 | 217 | 路由示例、SOP 中的环境路径演示 |

### C 类：工具误报（非文档债，约 200 条，登记工具增强候选）

GATE-SPS 路径提取正则的中文/符号边界缺陷产生的伪 token：

- **119 条**含 `{}`、`→`、中文标点：如 `/绝对路径转相对路径，类型B（80个）`、`C:\project\video.prproj，完成后发给我并关机`（教学案例中的示例句被整句吞入）
- **约 90 条**中文文本误命中：`/绝对路径引用`、`/链接指向正确` 等以 `/` 开头的中文句子片段
- LaTeX 形态：`C:\mathbb{Z...}`、`\Pi_{...}` 等被盘符正则误匹配

**处置**：文档侧不动；登记为 GATE-SPS 增强候选（DRIVE_RE 增加 CJK 标点边界、prose 形态要求路径字符集白名单），优先级低。

### D 类：活动信源债（登记跟踪，分批修复）

当前仍对读者开放的活动文档中的真实死链：

| 债务项 | 规模 | 性质 | 修复路径 |
|--------|-----:|------|---------|
| **D-1** knowledge Wiki 中 `d:/spaces/SpecWeave` 旧机器路径 | 265 | book-to-skill-wiki concepts（单文件 14-23 条）等活动教程；前缀映射 `d:/spaces/SpecWeave/<rest>` → `d:/AI/<rest>` 实测可达 | ✅ **已闭环（2026-08-29，`685506db`）**：45 个活动文档逐文档语义核验后修复，活动教程 spaces 令牌清零；事实表子集归 A 类不动；详见第六章闭环记录 |
| **D-2** bundles/chaos/tuya-iot 临时克隆引用 | 269 | facts-tuya-skills-ecosystem.md 引用 `.chaos/libs/TuyaOpen-dev-skills/`（已清理）；.cache 探针文件 | 信源归宿升级（vendor submodule 或 external 固定 tag），或在 bundle 中降级为不可变坐标引用 |
| **D-3** `.chaos/` 临时克隆活动引用 | 139 | 跨区域分布，需逐条甄别活动文档 vs 历史记录 | 随各文档维护顺带修复 |
| **D-4** `C:/Users/...` 环境绑定活动引用 | 129 | 开发者用户目录硬编码（knowledge 38、retro 36 等） | 活动文档子集改相对路径；历史子集归 A 类 |
| **D-5** projects/xuanspace 子模块内 d:/spaces | 53+23 | 子模块仓库自身的历史路径债 | 主仓不可改，向子模块上游登记 |

**d:/spaces 总量 1,732 条的去向说明**：SpecWeave 1,547 / chaos 92 / 其他 93；映射 d:/AI 可达 557 条。但大宗位于 A 类历史文档（.trae/specs 695、retro 244、awesome-okf 230、patterns 58），这些路径是旧机器时代的时点记录，**不做批量改写**；仅 D-1 活动教程子集进入修复队列。

## 三、分诊原则（可复用判据）

1. **历史快照原则**：文档体裁为事实表/复盘/spec 产物/模式案例时，路径是证据而非链接，失效不改写（与 A-3/A-6 复盘中 veadk 源码常量、实验脚本路径的处置一致）
2. **语境正确原则**：容器内 `/opt`、教学用 `/usr` 在其文档语境中是正确内容，主机不存在不构成债务
3. **工具误报与文档债分离**：含 CJK 标点/LaTeX 的伪 token 是工具缺陷，统计入工具 backlog 而非文档修复清单
4. **子模块边界**：projects/ 内债务只登记不修复
5. **前缀映射的语义安全前提**：`d:/spaces/SpecWeave` → `d:/AI` 机械映射仅适用于活动教程；对事实表执行映射等于篡改历史证据

## 四、与审计基线的关系

本次分诊后，4,294 条失效引用的管理口径：

- **立即修复**：0（锚点越界 10 条已在 ACT-2 闭环）
- **后续专项**：~~D-1（约 200+ 条活动 Wiki）~~ ✅ 已闭环（2026-08-29，`685506db`，45 文档，见第六章）、D-2（269 条 bundle 信源升级）
- **顺带修复**：D-3/D-4 活动子集
- **登记上报**：D-5 子模块、C 类工具误报
- **明确不动**：A 类约 2,750 + B 类约 1,050

GATE-SPS audit 退出码 1 在可预见未来将持续（A/B 类预期命中），工具职责是零漏报，语义裁决由本分诊框架人工执行。

## 五、关键数据溯源

- 扫描命令：`python .agents/scripts/check-source-path-stability.py --json`（GATE-SPS，含 ACT-1/ACT-2 全部增强）
- 聚类维度：token 路径桶（d:/spaces、POSIX、.chaos、Temp、vendor/projects/bundles 等）× 引用来源区域（specs/reports/knowledge/patterns/bundles/apps 等）
- 前缀映射验证：`d:/spaces/<root>/<rest>` → `d:/AI/<rest>` 逐条 Test-Path，557/1,732 可达
- 关联报告：[veadk A-3/A-6 闭环复盘](veadk-a3-a6-closure-retrospective-20260829.md)、[veadk 信源稳定性修复父里程碑](veadk-python-source-stability-fix-milestone-20260829.md)
- 模式依据：[信源稳定性门 v2.3](../../../../../.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/source-stability-gate.md)（检验标准 7/8、反模式 6、案例3 不改写边界）

## 六、D-1 闭环记录（2026-08-29）

D-1 于分诊同日完成修复并通过验收，原子提交 `685506db`（fix(docs)，45 文件，+91/-83）。

### 6.1 修复构成（逐文档语义核验，无机械映射）

| 组 | 文档数 | 处置 |
|----|-------:|------|
| D1 活动命令组 | 6 | 旧机器绝对路径改仓库相对路径写法（命令统一以仓库根为 CWD）：powershell-secure-download-verification、spec-loader-cold-start-storm-contingency、forum-automation、docker-cache-wsl-migration-guide（速查表 WSL 路径派生改写为 PowerShell 5.1/7 通用的 `-match`/`$matches` 形式并实测）、python-314t-conda-env-usage、tvm-ffi-wiki/12-faq |
| D2 external 库坐标组 | 32 | 本地 `d:/spaces` 源码坐标升级为 GitHub 官方 URL 或剥离机器前缀：zleap（10）、weasyprint（11）、pyinvoke（5）、caffe（3）、python314-stdlib（3）；agentskills skills-ref 死链经上游仓库结构核实（WebFetch）后改 tree/blob URL；conda-docs、CPython 补 clone 指引 |
| 分诊遗漏补修组 | 7 | devcontainer-ci-build-manual 2 处 file:/// 死链改相对链接（目标文件 Test-Path 实测存在）；docker-cache-wsl-sop WSL 挂载路径改占位写法；model-env-template、glm-model-call-example 的 `.chaos` 临时溯源按 mystx 先例剥离机器前缀；zleap README、agent-skills 09、conda-dev 06、chatgpt raw-content 补修 |

（分组按修复手法聚类、计数有交叉，以提交文件清单 45 个为准。）

### 6.2 边界遵守

- **A 类归档零改动**：p0-/p1-/p2- 前缀的 22 个事实表/归档文件 spaces 令牌全部保留
- **B 类教学零改动**：7 个活动教程文件中的残留令牌经逐字核验确认为教学反例/路径映射表/禁止项表格内容——fix-hardcoded-paths-guide、config-file-placement-convention、powershell-nativebuild-faq、powershell-nativebuild-refactoring-summary、seven-concepts-report 教训句、docker-cache-wsl-migration-guide（L138/142/143 WSL 映射教学，明示"替换为你自己的实际路径"）、frontmatter-link-batch-repair-guide

### 6.3 验收实测

- GATE-SPS 复扫（13,587 文件）：knowledge 区活动（非 p0/p1/p2 前缀）文档 spaces 令牌仅剩上述 7 个 B 类教学文件；锚点行越界 **0**
- 单元测试：`python -m pytest .agents/scripts/tests/test_check_source_path_stability.py -q` → **36 passed**
- 提交纪律：显式暂存（`git add docs/knowledge/`）、UTF-8 无 BOM 提交信息（`-F`）、`git show --stat` 核验零混入——并行会话的 `projects/awesome-okf-xs` 子模块指针与 docx 产物均未入提交

### 6.4 根 `docs/` 空壳旧树处置决策（登记不改写）

根 `docs/` 为空壳废弃树（规范引用一律解析至 `.agents/docs/`），其内 18 个 md 文件共 116 条 `d:/spaces` 令牌登记为 **deprecated 快照，不改写**：

| 子集 | 命中文件 | 令牌数 | 判定 |
|------|-------:|-------:|------|
| `docs/knowledge/learning/book-to-skill-wiki/` 旧副本 | 10 | 96 | 规范新版在 `docs/knowledge/learning/02-agent-engineering-methodology/02-prompt-coding/book-to-skill-wiki/`（复扫 0 令牌），旧副本随空壳树废弃 |
| python314 系列 wiki 旧 shell 副本 | 4 | 7 | 规范新版已在本次 D-1 修复，旧副本废弃 |
| 复盘/审计报告与里程碑索引 | 4 | 13 | A 类历史证据（报告正文引用的分析对象令牌，本报告即含 9 条） |
