---
title: learning → OKF bundles 迁移文件级台账
source: .trae/specs/migrate-learning-to-okf-bundles/spec.md（分类映射表）+ docs/knowledge/learning/ 实测（PowerShell Get-ChildItem -Recurse，2026-09-02）
type: facts-ledger
---

# facts-ledger — learning → OKF bundles 迁移文件级台账

## 0. 头部：实测总量

| 指标 | 实测值 |
|---|---|
| 源目录 | `docs/knowledge/learning/` |
| 测量日期 | 2026-09-02（PowerShell 7.6.4，`Get-ChildItem -Recurse -File`） |
| **总文件数** | **2146** |
| **md 文件数** | **2124** |
| **非 md 文件数** | **22**（清单见 §15） |
| 目标库 | `projects/awesome-okf-xs/doc/bundles/`（git submodule，现状 9 域/44 组/389 束，最终以 `gates.bundles` 重算为准） |

**处置类型图例**：新建（无对应束，建新束）/ 合并（对应束已存在，回填不建影子束）/ 直迁（chaos 已成型 OKF 包，零改写重定位）/ 重复删除（内容已被覆盖，执行期确认后删除）/ 舍弃-隐私元数据（retrospective/seven-concepts-report/log.md 等工作流元数据，不迁入）/ 舍弃-导航元数据（index/README/分类导航，随源目录删除）。

> 计数口径：各分类表按「主题目录（二级/三级）递归 md 数」登记，分类根级散文件单列行；隐私元数据文件包含在所属主题计数内，处置以 §14 专节为准（覆盖主题行处置）。

## 1. learning/ 根级散文件（5）

| 主题/文件 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| CATEGORIES.md、index.md、LEARNING-PATHS.md、README.md | 4 | — | 舍弃-导航元数据 |
| docx-template-report-skill-design.md | 1 | `jishu/ai/docx-report-skill` | 新建（⚠️ 异常：不在映射表，见 §16-A1） |

小计：**5**

## 2. 分类 00-essence-and-thinking（63）

| 主题目录 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| （分类根）index.md、README.md | 2 | — | 舍弃-导航元数据 |
| boshu-laozi-wiki | 10 | `guoxue/laozi/boshu-reading` | 合并（重复对 #1） |
| first-principles（含三级 15-cross-domain-cases 7、chinese-philosophy-parallels 14、exercises 12） | 51 | `zhexue/methodology/first-principles` | 新建（新组 methodology） |

小计：2+10+51 = **63**

## 3. 分类 01-agent-protocols-interfaces（199）

| 主题目录 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| （分类根）index.md、README.md | 2 | — | 舍弃-导航元数据 |
| （分类根散文件）agent-communication-protocols-wiki.md、agent-runtime-protocol-wiki.md、domestic-skill-mcp-ecosystem-wiki.md | 3 | 并入下方同名主题束 | 新建（并入） |
| （分类根散文件）agent-skills-open-standard-wiki.md | 1 | `jishu/ai/ai-agent/agent-skills-spec` | 合并（重复对 #2 关联） |
| agent-communication-protocols | 14 | `jishu/ai/ai-agent/agent-communication-protocols` | 新建（含散文件 1） |
| agent-interface-deep-dive | 9 | `jishu/ai/ai-agent/agent-interface-deep-dive` | 新建 |
| agent-runtime-protocol-wiki | 17 | `jishu/ai/ai-agent/agent-runtime-protocol` | 新建（含散文件 1） |
| agent-skills-wiki | 17 | `jishu/ai/ai-agent/agent-skills-spec` | 合并（重复对 #2） |
| ffi-wiki | 10 | `jishu/comm/ffi` | 新建 |
| graphql-wiki | 12 | `jishu/web/graphql/graphql` | 合并（重复对 #3） |
| idl-wiki | 12 | `jishu/comm/idl` | 新建 |
| interface-api-abi-protocol-wiki | 9 | `jishu/comm/interface-api-abi` | 新建 |
| jira-skill-wiki（含三级 concepts 11、examples 4、references 4） | 22 | `jishu/ai/ai-agent/jira-skill` | 新建 |
| knowledge-catalog-wiki | 11 | `meta/okf-spec` | 合并（部分重叠 #4） |
| okf-desktop-wiki | 9 | `jishu/ai/ai-agent/okf-desktop` | 新建 |
| okf-wiki（含三级 awesome-okf-analysis 7、okf-ecosystem-wiki 5） | 25 | `meta/okf-spec` | 合并（重复对 #4） |
| protobuf-wiki | 8 | `jishu/comm/serialization/protobuf` | 合并（重复对 #5） |
| tvm-ffi-wiki | 18 | `jishu/comm/tvm-ffi` | 新建 |

小计：2+3+1+14+9+17+17+10+12+12+9+22+11+9+25+8+18 = **199**

## 4. 分类 02-agent-engineering-methodology（321）

> 按 spec「六板块整合为 1-2 束」：新建 `jishu/ai/ai-engineering-methodology`（范式/提示词/方法论/评估/性能）与 `jishu/ai/context-optimization`（上下文优化板块）。

| 主题目录 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| （分类根）index.md、README.md | 2 | — | 舍弃-导航元数据 |
| 01-paradigms（含三级 ai-engineering-four-milestones-wiki 12、harness-engineering-wiki 12、harness-seven-components-wiki 16） | 46 | `jishu/ai/ai-engineering-methodology` | 新建（整合） |
| 02-prompt-coding（根级散文件） | 5 | `jishu/ai/ai-engineering-methodology` | 新建（整合） |
| 02-prompt-coding/agent-skills-wiki | 10 | `jishu/ai/ai-agent/agent-skills-spec` | 合并（重复对 #2 同名） |
| 02-prompt-coding/book-to-skill-wiki | 13 | `jishu/ai/ai-agent/book-to-skill` | 合并（新发现重复，§16-A5） |
| 02-prompt-coding/karpathy-llm-coding-guidelines | 10 | `jishu/ai/ai-engineering-methodology` | 新建（整合） |
| 02-prompt-coding/seven-concepts-prompt-wiki | 17 | `jishu/ai/ai-engineering-methodology` | 新建（整合，内容章节，隐私复审） |
| 03-methodology（含三级 adversarial-review-wiki 16、seven-concepts-deeptutor-wiki 42） | 61 | `jishu/ai/ai-engineering-methodology` | 新建（整合） |
| 04-context-optimization（含三级 headroom-context-compression-wiki 14、llm-token-optimization 37、trae-ide-token-optimization 19） | 73 | `jishu/ai/context-optimization` | 新建 |
| 05-evaluation（含三级 agent-eval-methodology-wiki 29、agent-evaluation-wiki 13） | 44 | `jishu/ai/ai-engineering-methodology` | 新建（整合） |
| 06-performance（含三级 longcat-agent-learning-wiki 11、neural-compressor-wiki 11） | 26 | `jishu/ai/ai-engineering-methodology` | 新建（整合） |
| ai-engineering-notes | 8 | `jishu/ai/ai-engineering-methodology` | 新建（整合） |
| deep-learning-atomic-design | 6 | `jishu/ai/ai-engineering-methodology` | 新建（整合） |

小计：2+46+5+10+13+10+17+61+73+44+26+8+6 = **321**

## 5. 分类 03-agent-platforms-tools（546）

| 主题目录 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| （分类根）index.md、README.md、WIKI-INDEX.md | 3 | — | 舍弃-导航元数据 |
| （散文件）2026-08-25 三份研究报告（zhihu-article、best-agent-systems-research、global-ai-agent-systems-industry-research） | 3 | `jishu/ai/agent-industry-research` | 新建（整合，附 2 份 .html） |
| （散文件）anthropic-agent-roadmap-wiki.md | 1 | `jishu/ai/anthropic/agent-roadmap` | 新建 |
| （散文件）anthropic-financial-services-wiki.md | 1 | `jishu/ai/anthropic/financial-services` | 合并（新发现重复，§16-A5） |
| （散文件）areal-agent-rl-wiki.md、areal-official-practical-wiki.md | 2 | `jishu/ai/areal` | 新建（整合） |
| （散文件）atomgit-ai-best-practices.md | 1 | `jishu/ai/atomgit-ai` | 新建 |
| （散文件）browseract-official-wiki.md、browseract-wiki.md | 2 | `jishu/ai/browseract` | 新建（整合） |
| （散文件）claude-tag-article.md | 1 | `jishu/ai/anthropic/claude-tag` | 新建（与同名目录整合） |
| （散文件）echobird-wiki.md | 1 | `jishu/ai/echobird` | 新建（与同名目录整合） |
| （散文件）langgraph-implementation-roadmap.md | 1 | `jishu/ai/langchain-ai/langgraph` | 新建 |
| （散文件）minitap-official-wiki.md | 1 | `jishu/ai/minitap` | 新建 |
| （散文件）minitest-mobile-use-official-docs-wiki.md、mobile-use-deep-learning-analysis.md | 2 | `jishu/ai/mobile-use` | 合并（并入 chaos 直迁束） |
| （散文件）mopmonk-security-agent-wiki.md | 1 | `jishu/ai/mopmonk` | 新建（与 02-security 同名目录整合） |
| （散文件）octo-platform-wiki.md | 1 | `jishu/ai/octo-platform` | 新建 |
| （散文件）open-code-review-wiki.md | 1 | `jishu/ai/open-code-review` | 新建（三源整合去重） |
| （散文件）quantdinger-ai-trading-wiki.md | 1 | `jishu/ai/quantdinger` | 新建（与同名目录整合） |
| （散文件）rainman-translate-book-wiki.md | 1 | `jishu/ai/rainman-translate` | 新建（与 06-content-translation 同名目录整合） |
| （散文件）the-agency-project-wiki.md | 1 | `jishu/ai/ai-agent/agency-agents` | 合并（重复对 #6 关联） |
| （散文件）trae-v3-3-74-release-notes.md | 1 | `jishu/ai/trae` | 合并（Release Notes，时效核验） |
| 00-agent-frameworks（根级散文件） | 1 | — | 舍弃-导航元数据 |
| 00-agent-frameworks/claude-tag-article | 10 | `jishu/ai/anthropic/claude-tag` | 新建（含散文件 1） |
| 00-agent-frameworks/echobird-wiki | 14 | `jishu/ai/echobird` | 新建（含散文件 1） |
| 00-agent-frameworks/eve-wiki | 12 | `jishu/ai/eve` | 新建 |
| 00-agent-frameworks/hermes-agent-installation 13 + hermes-agent-integration 11 + hermes-agent-wiki 14 | 38 | `jishu/ai/ai-agent/hermes-agent` | 合并（新发现重复，三目录整合） |
| 00-agent-frameworks/orca-wiki | 10 | `jishu/ai/orca` | 新建 |
| 00-agent-frameworks/zleap-agent-wiki | 11 | `jishu/ai/ai-agent/zleap-agent` | 合并（新发现重复） |
| 01-domestic-platforms（根级散文件） | 1 | — | 舍弃-导航元数据 |
| 01-domestic-platforms/veadk-python | 72 | `jishu/ai/ai-agent/veadk-python` | 合并（三重重复异常，§16-A2） |
| 01-domestic-platforms/volcengine-agent-plan-wiki 11 + volcengine-agentkit-wiki 14 | 25 | `jishu/ai/volcengine-agent` | 新建（整合，定价/产品时效核验） |
| 02-security（根级散文件） | 1 | — | 舍弃-导航元数据 |
| 02-security/mopmonk-security-agent-wiki | 9 | `jishu/ai/mopmonk` | 新建（含散文件 1） |
| 03-code-devtools（根级散文件） | 1 | — | 舍弃-导航元数据 |
| 03-code-devtools/codewhale-wiki | 11 | `jishu/ai/ai-agent/codewhale` | 合并（重复对 #8） |
| 03-code-devtools/fable5-cost-optimization-wiki | 11 | `jishu/ai/fable5-cost-optimization` | 新建 |
| 03-code-devtools/i-have-adhd-wiki | 15 | `jishu/ai/ai-agent/i-have-adhd` | 合并（新发现重复） |
| 03-code-devtools/open-code-review-wiki | 19 | `jishu/ai/open-code-review` | 新建（三源整合去重） |
| 03-code-devtools/seven-concepts-monkeycode-vibe-coding-wiki | 9 | `jishu/ai/monkeycode-vibe-coding` | 新建（内容主题） |
| 05-mobile-testing（根级散文件） | 1 | — | 舍弃-导航元数据 |
| 05-mobile-testing/minitest-mobile-use-wiki | 88 | `jishu/ai/mobile-use` | 合并（并入 chaos 直迁束） |
| 06-content-translation（根级散文件） | 1 | — | 舍弃-导航元数据 |
| 06-content-translation/rainman-translate-book-wiki | 10 | `jishu/ai/rainman-translate` | 新建（含散文件 1） |
| agency-agents-wiki（含三级 concepts 9、examples 2、references 3） | 29 | `jishu/ai/ai-agent/agency-agents` | 合并（重复对 #6） |
| cordis-spatiotemporal-composability-wiki（含三级 concepts 8、examples 2、references 6） | 33 | `jishu/ai/ai-agent/cordis` | 合并（新发现重复） |
| deepseek-harness-wiki（含三级 concepts 14、references 4） | 38 | `jishu/ai/ai-agent/deepseek-harness` | 合并（重复对 #7） |
| okf-kit-wiki（含三级 concepts 9、references 5） | 30 | `meta/okf-spec/okf-kit` | 新建 |
| open-code-review-wiki（含三级 concepts 8、references 4） | 14 | `jishu/ai/open-code-review` | 新建（三源整合去重） |
| quantdinger | 6 | `jishu/ai/quantdinger` | 新建（含散文件 1） |

小计：3+23（散文件）+96+98+10+66+89+11+29+33+38+30+14+6 = **546**

## 6. 分类 04-docs-markup-tooling（146）

| 主题目录 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| （分类根）index.md、README.md | 2 | — | 舍弃-导航元数据 |
| （分类根散文件）declarative-partial-updates-wiki.md | 1 | `jishu/document/myst` 相关束 | 合并（执行期定束，建议 MyST-Parser） |
| （分类根散文件）executablebooks-myst-guide-wiki.md | 1 | `jishu/document/myst` | 合并（部分重叠 #1） |
| executablebooks-myst-guide（含三级 examples 11、resources 2、syntax 2、templates 2） | 26 | `jishu/document/myst` | 合并（部分重叠 #1） |
| mdx-graphql-guide | 6 | `jishu/web/graphql/graphql` | 合并 |
| mermaid-wiki | 14 | `jishu/document/mermaid` | 新建 |
| myst-markdown-tutorial（含三级 appendix 4、examples 7） | 30 | `jishu/document/myst` | 合并（部分重叠 #1） |
| pyinvoke-wiki（含三级 core-concepts 10、overview 6；6 个空子目录见 §16-A9） | 19 | `jishu/build/tooling/pyinvoke` | 合并（重复对 #9） |
| python314-stdlib-wiki | 21 | `jishu/python/python314-stdlib` | 新建（与 10 类 python314-cpython 内容互补去重） |
| scikit-build-core-wiki | 9 | `jishu/build/scikit-build` | 合并（重复对 #10） |
| weasyprint-wiki | 17 | `jishu/document/weasyprint` | 新建 |

小计：2+1+1+26+6+14+30+19+21+9+17 = **146**

## 7. 分类 05-ai-multimodal-content（55）

| 主题目录 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| （分类根）index.md、README.md | 2 | — | 舍弃-导航元数据 |
| （散文件）animejs-threejs-adapter-analysis.md | 1 | `jishu/viz/animejs-threejs-adapter` | 新建（与同名目录整合） |
| （散文件）mainecoon-social-world-model.md | 1 | `jishu/ai/mainecoon` | 新建（与同名目录整合） |
| （散文件）agnes-pavo-creative-platform-wiki.md | 1 | `jishu/ai/agnes-pavo` | 新建（执行期比对 `jishu/ai/agnes-ai` 防重） |
| （散文件）audiox-turbo-audio-generation-wiki.md | 1 | `jishu/ai/audiox-turbo` | 新建 |
| （散文件）ian-xiaohei-illustrations.md | 1 | `jishu/ai/ian-xiaohei-illustrations` | 新建 |
| （散文件）libtv-ai-shortdrama-wiki.md | 1 | `jishu/ai/libtv-shortdrama` | 新建 |
| （散文件）text-to-cad-wiki.md | 1 | `jishu/ai/text-to-cad` | 新建 |
| animejs-threejs-adapter-wiki | 10 | `jishu/viz/animejs-threejs-adapter` | 新建（含散文件 1） |
| atomic-emergence | 5 | `jishu/ai/atomic-emergence` | 新建（附 index.html） |
| causal-ai | 6 | `jishu/ai/causal-ai` | 新建 |
| mainecoon-wiki | 14 | `jishu/ai/mainecoon` | 新建（含散文件 1） |
| minit2i-wiki | 11 | `jishu/ai/minit2i` | 新建 |

小计：2+7+10+5+6+14+11 = **55**

## 8. 分类 06-business-trends-analysis（93）

> 全部入 `sheke/industry`（新建组）。

| 主题目录 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| （分类根）index.md、README.md | 2 | — | 舍弃-导航元数据 |
| （散文件）ems-energy-management-wiki.md | 1 | `sheke/industry/ems-energy` | 新建（与同名目录整合） |
| （散文件）papi-jiang-solo-ip-trend-wiki.md | 1 | `sheke/industry/papi-jiang-solo-ip` | 新建（与同名目录整合） |
| （散文件）three-ai-tools-wiki.md | 1 | `sheke/industry/three-ai-tools` | 新建（与同名目录整合） |
| （散文件）2026-07-08-ai-anthropomorphic-interim-measures-analysis.md | 1 | `sheke/industry/ai-anthropomorphic-analysis` | 新建 |
| （散文件）domestic-llm-comparison-notes.md | 1 | `sheke/industry/domestic-llm-comparison` | 新建 |
| （散文件）huaqiu-sigmastar-partnership-analysis-20260709.md | 1 | `sheke/industry/huaqiu-sigmastar` | 新建 |
| ai-hardware-design-tools-wiki | 4 | `sheke/industry/ai-hardware-design-tools` | 新建 |
| ai-monetization-wiki | 15 | `sheke/industry/ai-monetization` | 新建 |
| ai-switch-governance | 7 | `sheke/industry/ai-switch-governance` | 新建 |
| copilot-cost-multimodel-era-wiki | 10 | `sheke/industry/copilot-cost` | 新建 |
| douyin-vibecoding-wiki | 5 | `sheke/industry/douyin-vibecoding` | 新建 |
| ems-energy-management-wiki | 4 | `sheke/industry/ems-energy` | 新建（含散文件 1） |
| papi-jiang-solo-ip-trend-wiki | 11 | `sheke/industry/papi-jiang-solo-ip` | 新建（含散文件 1） |
| rqndd | 4 | `sheke/industry/rqndd` | 新建 |
| seven-concepts-india-manufacturing-wiki | 8 | `sheke/industry/india-manufacturing` | 新建 |
| three-ai-tools-wiki | 7 | `sheke/industry/three-ai-tools` | 新建（含散文件 1） |
| volcengine-ai-ecosystem-wiki | 10 | `sheke/industry/volcengine-ecosystem` | 新建（产品生态时效核验） |

小计：2+6+4+15+7+10+5+4+11+4+8+7+10 = **93**

## 9. 分类 07-vendor-product-learning（200）

| 主题目录 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| （分类根）index.md、README.md | 2 | — | 舍弃-导航元数据 |
| baidu（根级散文件） | 2 | `jishu/ai/baidu-ocr` | 新建（并入） |
| baidu/baidu-ocr-wiki | 12 | `jishu/ai/baidu-ocr` | 新建 |
| comparison | 4 | `jishu/ai/llm-vendor-comparison` | 新建（执行期可判低价值舍弃） |
| deepseek | 13 | `jishu/ai/deepseek` | 合并（部分重叠 #5，定价时效核验） |
| google-cloud（含三级 knowledge-catalog-wiki 8） | 11 | `meta/okf-spec` | 合并（部分重叠 #4） |
| miaowu（含三级 miaowu-ambassador-guide 4、miaowu-meoo-practice-cases 5） | 11 | `jishu/ai/miaowu` | 新建 |
| okr-wiki（含三级 appendix 3、concepts 8、implementation 8、methods 6、scoring 6、templates 9、tools 4） | 48 | `sheke/workplace/okr` | 新建 |
| openai（根级散文件） | 2 | `jishu/ai/ai-agent/openai-codex` | 合并（并入） |
| openai/chatgpt-codex-wiki | 19 | `jishu/ai/ai-agent/openai-codex` | 合并（部分重叠 #3，附 page.html） |
| oray（根级散文件） | 4 | `jishu/iot/oray` | 新建（新组 iot） |
| oray/retrospective-oray-comprehensive-analysis-20260706 | 5 | — | 舍弃-隐私元数据（§14） |
| sunlogin（根级散文件） | 17 | `jishu/iot/sunlogin` | 新建 |
| sunlogin/retrospective-sunlogin-wiki-mobile-control-update-20260706 | 5 | — | 舍弃-隐私元数据（§14） |
| sunlogin/sunlogin-bootbox-analysis | 12 | `jishu/iot/sunlogin` | 合并（并入） |
| sunlogin/sunlogin-offline-hardware-wiki | 13 | `jishu/iot/sunlogin` | 合并（并入） |
| tuya | 5 | `jishu/iot/tuya-iot` | 合并（并入 chaos 直迁束） |
| volcengine | 15 | `jishu/ai/volcengine` | 新建（产品/定价时效核验） |

小计：2+2+12+4+13+11+11+48+2+19+4+5+17+5+12+13+5+15 = **200**

## 10. 分类 08-systems-infrastructure（114）

> git/github 主题并入既有 `jishu/dev/git`、`jishu/dev/github`（不建影子束，§16-A7）；新组 `jishu/systems` 收 wsl/powershell。

| 主题目录 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| （分类根）index.md、README.md | 2 | — | 舍弃-导航元数据 |
| （分类根散文件）wsl-cli-and-architecture-wiki.md、wsl-learning-plan.md | 2 | `jishu/systems/wsl` | 新建（与 wsl-wiki 整合） |
| ai-powershell5-hell-wiki | 12 | `jishu/systems/powershell-hell` | 新建 |
| caffe-architecture-wiki | 9 | `jishu/ml/caffe` | 新建 |
| conda-dev-github-wiki 12 + conda-dev-source-wiki 12 | 24 | `jishu/build/conda` | 合并 |
| cpython-devguide-wiki | 8 | `jishu/python/cpython` | 合并 |
| git-advanced-wiki | 4 | `jishu/dev/git` | 合并 |
| git-baidu-sync | 13 | `jishu/dev/git-baidu-sync` | 新建 |
| github-cli-wiki | 12 | `jishu/dev/github` | 合并（⚠️ spec 原列新建，因既有束改合并，§16-A4） |
| intelligent-terminal-wiki | 15 | `jishu/ai/ai-agent/intelligent-terminal` | 合并（⚠️ spec 原列新建，因既有束改合并，§16-A3） |
| wsl-wiki | 13 | `jishu/systems/wsl` | 新建（含散文件 2） |

小计：2+2+12+9+24+8+4+13+12+15+13 = **114**

## 11. 分类 09-ml-inference-deployment（10）

| 主题目录 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| （分类根）index.md、README.md | 2 | — | 舍弃-导航元数据 |
| onnx-wiki | 8 | `jishu/ml/onnx/onnx` | 合并（回填既有 onnx 组） |

小计：2+8 = **10**

## 12. 分类 10-foundational-knowledge（49）

| 主题目录 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| （分类根）index.md、README.md | 2 | — | 舍弃-导航元数据 |
| academic-skills（含三级 thesis-writing-wiki 14） | 15 | `sheke/workplace/academic-writing` | 新建 |
| mathematical-foundations（含三级 pythagorean-theorem-wiki 11） | 12 | `kexue/math/pythagorean-theorem` | 新建 |
| python314-cpython-wiki | 20 | `jishu/python/cpython` | 合并（部分重叠 #2；与 04 同名系去重） |

小计：2+15+12+20 = **49**

## 13. 分类 okf-bundles（323）

> chaos 10 个已成型 OKF 包格式已合规，直迁=零改写重定位+登记索引+toctree 接线。

| 主题目录 | md 数 | 目标束路径 | 处置 |
|---|---|---|---|
| okf-bundles/index.md | 1 | — | 舍弃-导航元数据 |
| chaos/index.md | 1 | — | 舍弃-导航元数据 |
| chaos/CROSS_BUNDLE_REVIEW.md、PATTERNS_LESSONS.md | 2 | `meta/okf-spec/references` | 合并 |
| chaos/retrospective-okf-wiki-build.md | 1 | — | 舍弃-隐私元数据（§14） |
| chaos/ai-agent-skills | 32 | `jishu/ai/ai-agent-skills` | 直迁（执行期比对 `agent-skills-spec` 防重，§16-A6） |
| chaos/apache-tvm | 38 | `jishu/ml/apache-tvm` | 直迁 |
| chaos/english-grammar | 70 | `wenxue/english/english-grammar` | 直迁（新组 english） |
| chaos/home-assistant | 35 | `jishu/iot/home-assistant` | 直迁（新组 iot） |
| chaos/laozi-lineage | 37 | `guoxue/laozi/laozi-lineage` | 直迁 |
| chaos/mobile-use | 17 | `jishu/ai/mobile-use` | 直迁 |
| chaos/okf-ecosystem | 18 | `meta/okf-ecosystem` | 直迁 |
| chaos/tiktoken | 22 | `jishu/ai/tiktoken` | 直迁 |
| chaos/tuya-iot | 27 | `jishu/iot/tuya-iot` | 直迁（并入 07/tuya 5） |
| chaos/veadk-python | 22 | `jishu/ai/ai-agent/veadk-python` | 合并（⚠️ 目标束已存在，直迁改合并，§16-A2） |

小计：1+1+2+1+32+38+70+35+37+17+18+22+27+22 = **323**

## 13b. 重复对专节

### 10 对明确重复（bundles 侧为权威基线，learning 侧独有内容回填，不建影子束）

| # | learning 侧（文件数） | bundles 侧基线束 | 处置决定 |
|---|---|---|---|
| 1 | 00/boshu-laozi-wiki（10） | `guoxue/laozi/boshu-reading` | 合并回填，log.md 登记合并事件 |
| 2 | 01/agent-skills-wiki（17）+ 02/02-prompt-coding/agent-skills-wiki（10）+ 散文件 agent-skills-open-standard-wiki.md（1） | `jishu/ai/ai-agent/agent-skills-spec` | 三源合并回填 |
| 3 | 01/graphql-wiki（12）+ 04/mdx-graphql-guide（6） | `jishu/web/graphql/graphql` | 合并回填 |
| 4 | 01/okf-wiki（25） | `meta/okf-spec` | 合并回填 |
| 5 | 01/protobuf-wiki（8） | `jishu/comm/serialization/protobuf` | 合并回填 |
| 6 | 03/agency-agents-wiki（29）+ 散文件 the-agency-project-wiki.md（1） | `jishu/ai/ai-agent/agency-agents` | 合并回填 |
| 7 | 03/deepseek-harness-wiki（38） | `jishu/ai/ai-agent/deepseek-harness` | 合并回填 |
| 8 | 03/03-code-devtools/codewhale-wiki（11） | `jishu/ai/ai-agent/codewhale` | 合并回填 |
| 9 | 04/pyinvoke-wiki（19） | `jishu/build/tooling/pyinvoke` | 合并回填 |
| 10 | 04/scikit-build-core-wiki（9） | `jishu/build/scikit-build` | 合并回填 |

### 5 项部分重叠

| # | learning 侧（文件数） | 处置决定 |
|---|---|---|
| 1 | myst 系：04/executablebooks-myst-guide（26）+ myst-markdown-tutorial（30）+ 散文件 2 | 合并入 `jishu/document/myst/` 相关束（MyST-Parser/sphinx-book-theme 等，执行期按内容分配），两教程互为补充不重复建束 |
| 2 | 10/python314-cpython-wiki（20） | 合并入 `jishu/python/cpython`；与 04/python314-stdlib-wiki（21，新建）按 cpython 内部机制 vs 标准库分工去重 |
| 3 | 07/openai/chatgpt-codex-wiki（19+2） | 与既有 `jishu/ai/ai-agent/openai-codex` 比对合并 |
| 4 | 01/knowledge-catalog-wiki（11）+ 07/google-cloud（11） | 合并入 `meta/okf-spec` |
| 5 | 07/deepseek（13，定价/产品为主） | 合并入 `jishu/ai/deepseek`，2026-09 定价时效核验 |

### 新发现重复（超出 spec 10 对清单，见 §16-A5）

book-to-skill-wiki（13）→ `book-to-skill`；hermes-agent 三目录（38）→ `hermes-agent`；zleap-agent-wiki（11）→ `zleap-agent`；cordis-wiki（33）→ `cordis`；i-have-adhd-wiki（15）→ `i-have-adhd`；anthropic-financial-services-wiki.md（1）→ `anthropic/financial-services`；veadk-python 双源（72+22）→ `veadk-python`；intelligent-terminal-wiki（15）→ `intelligent-terminal`；github-cli-wiki（12）→ `jishu/dev/github`。以上一律合并回填，不建影子束。open-code-review 三源（1+14+19=34）整合为新建束 `jishu/ai/open-code-review`，执行期内容比对后重复文件可转重复删除。

## 14. 隐私元数据专节（处置=不迁入）

> 以下文件包含在各分类主题计数内，处置以本节为准。迁入束的 `log.md` 一律重置为迁移事件日志。

### retrospective 类（12 文件，4 处）

| 文件 | 处置 |
|---|---|
| okf-bundles/chaos/retrospective-okf-wiki-build.md | 不迁入 |
| 08-systems-infrastructure/github-cli-wiki/retrospective.md | 不迁入 |
| 07-vendor-product-learning/oray/retrospective-oray-comprehensive-analysis-20260706/（index、README、execution-retrospective、export-suggestions、insight-extraction，共 5） | 不迁入（整目录） |
| 07-vendor-product-learning/sunlogin/retrospective-sunlogin-wiki-mobile-control-update-20260706/（同构 5 文件） | 不迁入（整目录） |

注：02/03-methodology/seven-concepts-deeptutor-wiki/01-seven-concepts-theory/01-r-retrospective.md 为 wiki 内容章节（七概念 R 步骤），随主题迁移并做隐私复审，不按元数据舍弃。

### seven-concepts-report 类（严格匹配 10 文件）

| 文件 | 处置 |
|---|---|
| 10-foundational-knowledge/python314-cpython-wiki/seven-concepts-report.md | 不迁入 |
| 06-business-trends-analysis/three-ai-tools-wiki/03-seven-concepts-report.md | 不迁入 |
| 06-business-trends-analysis/ai-switch-governance/02-seven-concepts-report.md | 不迁入 |
| 05-ai-multimodal-content/causal-ai/02-seven-concepts-report.md | 不迁入 |
| 04-docs-markup-tooling/python314-stdlib-wiki/seven-concepts-report.md | 不迁入 |
| 03-agent-platforms-tools/quantdinger/02-seven-concepts-report.md | 不迁入 |
| 03-agent-platforms-tools/okf-kit-wiki/seven-concepts-report.md | 不迁入 |
| 03-agent-platforms-tools/okf-kit-wiki/references/seven-concepts-report.md | 不迁入 |
| 03-agent-platforms-tools/cordis-spatiotemporal-composability-wiki/seven-concepts-report.md | 不迁入 |
| 03-agent-platforms-tools/cordis-spatiotemporal-composability-wiki/references/seven-concepts-report.md | 不迁入 |

另有 7 个含 seven-concepts 字样的内容章节文件（03/03-code-devtools/seven-concepts-monkeycode-vibe-coding-wiki 2、02/05-evaluation/agent-eval-methodology-wiki 3、02/03-methodology/workbuddy-four-layers-seven-concepts-analysis.md 1、02/02-prompt-coding/seven-concepts-prompt-wiki/02-seven-concepts-mapping.md 1）：属主题内容，随主题迁移并做隐私复审。

### log.md 类（37 文件，全部不迁入）

03/03-code-devtools/codewhale-wiki、05/minit2i-wiki、07/baidu/baidu-ocr-wiki、02/02-prompt-coding/book-to-skill-wiki、10/python314-cpython-wiki、02/04-context-optimization/headroom-context-compression-wiki、06/three-ai-tools-wiki、02/01-paradigms/ai-engineering-four-milestones-wiki、08/github-cli-wiki、05/atomic-emergence、04/python314-stdlib-wiki、03/deepseek-harness-wiki、03/03-code-devtools/open-code-review-wiki、02/deep-learning-atomic-design、02/ai-engineering-notes、03/open-code-review-wiki、03/okf-kit-wiki、03/cordis-spatiotemporal-composability-wiki、01/jira-skill-wiki、okf-bundles/chaos/{english-grammar、tiktoken、veadk-python、tuya-iot、okf-ecosystem、mobile-use、laozi-lineage、home-assistant、apache-tvm、ai-agent-skills}、03/agency-agents-wiki、06/rqndd、06/ai-switch-governance、05/mainecoon-wiki、05/causal-ai、03/quantdinger、01/agent-runtime-protocol-wiki、04/pyinvoke-wiki（各 1，共 37）。

隐私元数据合计：12 + 10 + 37 = **59 不迁入**（另有 8 个七概念/复盘字样的内容章节随主题迁移+隐私复审）。

## 15. 非 md 资源专节（22 文件）

| 文件 | 处置 |
|---|---|
| 00/first-principles/12-knowledge-graph.html | 随主题迁移（references） |
| 00/first-principles/knowledge-graph-config.toml | 随主题迁移（references） |
| 01/agent-runtime-protocol-wiki/interactive-selection-matrix.html | 随主题迁移（references） |
| 02/03-methodology/adversarial-review-wiki/knowledge-graph-config.toml | 随主题迁移（references） |
| 02/03-methodology/adversarial-review-wiki/knowledge-graph.html | 随主题迁移（references） |
| 02/04-context-optimization/llm-token-optimization/01-principles/.gitkeep | 舍弃（空目录占位） |
| 02/04-context-optimization/llm-token-optimization/02-methods/.gitkeep | 舍弃（空目录占位） |
| 02/04-context-optimization/llm-token-optimization/03-tools/.gitkeep | 舍弃（空目录占位） |
| 02/04-context-optimization/llm-token-optimization/04-cases/.gitkeep | 舍弃（空目录占位） |
| 02/04-context-optimization/llm-token-optimization/05-evaluation/.gitkeep | 舍弃（空目录占位） |
| 02/04-context-optimization/llm-token-optimization/06-decision-framework/.gitkeep | 舍弃（空目录占位） |
| 03/2026-08-25-best-agent-systems-research.html | 随主题迁移（agent-industry-research） |
| 03/2026-08-25-global-ai-agent-systems-industry-research.html | 随主题迁移（agent-industry-research） |
| 04/executablebooks-myst-guide/examples/poc/myst_mcp_server.py | 随主题迁移（POC 代码，并入 myst 相关束 references） |
| 04/executablebooks-myst-guide/examples/poc/test_poc.py | 随主题迁移（POC 代码） |
| 04/executablebooks-myst-guide/examples/poc/__pycache__/myst_mcp_server.cpython-313.pyc | 舍弃（构建产物，§16-A10） |
| 04/executablebooks-myst-guide/resources/.gitkeep | 舍弃（空目录占位） |
| 04/executablebooks-myst-guide/syntax/.gitkeep | 舍弃（空目录占位） |
| 04/executablebooks-myst-guide/templates/myst.yml.template | 随主题迁移（模板资源） |
| 05/atomic-emergence/index.html | 随主题迁移（references） |
| 07/openai/chatgpt-codex-wiki/page.html | 随主题迁移（openai-codex references） |
| 10/python314-cpython-wiki/python314-cheatsheet.html | 随主题迁移（cpython references） |

合计 22 = 随主题迁移 13 + 舍弃 9（.gitkeep 8 + .pyc 1）。

## 16. 异常登记

- **A1**：learning/ 根级 5 文件不在映射表——4 个导航文件舍弃；docx-template-report-skill-design.md 定为新建 `jishu/ai/docx-report-skill`。
- **A2**：veadk-python 三重重复——03/01-domestic-platforms/veadk-python（72）+ okf-bundles/chaos/veadk-python（22）+ bundles 既有 `jishu/ai/ai-agent/veadk-python`。chaos 包由「直迁」改判「合并」，两 learning 源与既有束三方比对回填。
- **A3**：intelligent-terminal-wiki（08，15）spec 映射为新建，但 `jishu/ai/ai-agent/intelligent-terminal` 已存在 → 改判合并。
- **A4**：github-cli-wiki（08，12）spec 映射为新建，但 `jishu/dev/github` 已存在 → 改判合并。
- **A5**：新发现重复 9 组（见 §13b 第三表），超出 spec 已识别的 10 对。
- **A6**：chaos/ai-agent-skills 与既有 `jishu/ai/ai-agent/agent-skills-spec` 潜在重叠，直迁执行时必须内容比对，确认重叠则转合并。
- **A7**：spec 拟新建 `jishu/systems` 组收 wsl/powershell/terminal/git，但 `jishu/dev/git`、`jishu/dev/github`、`jishu/terminal/textualize` 已存在 → git 系主题并入 `jishu/dev/*`，systems 组仅收 wsl/powershell（避免影子束）。
- **A8**：06 分类根级 ems/papi/three-ai-tools 散文件与同名目录并存（种子文件重复），已按「并入同名目录主题束」处理。
- **A9**：04/pyinvoke-wiki 下 6 个空子目录（cli/configuration/patterns/python-api/reference/references，0 文件），迁移时不保留空目录。
- **A10**：04/executablebooks-myst-guide/examples/poc/ 含 `__pycache__/*.pyc` 构建产物，属应被 .gitignore 拦截的历史遗留，随源目录删除。

## 17. 校验节

### 分类计数汇总（必须等于实测 md 总数）

| 分节 | 范围 | md 数 |
|---|---|---|
| §1 | learning/ 根级散文件 | 5 |
| §2 | 00-essence-and-thinking | 63 |
| §3 | 01-agent-protocols-interfaces | 199 |
| §4 | 02-agent-engineering-methodology | 321 |
| §5 | 03-agent-platforms-tools | 546 |
| §6 | 04-docs-markup-tooling | 146 |
| §7 | 05-ai-multimodal-content | 55 |
| §8 | 06-business-trends-analysis | 93 |
| §9 | 07-vendor-product-learning | 200 |
| §10 | 08-systems-infrastructure | 114 |
| §11 | 09-ml-inference-deployment | 10 |
| §12 | 10-foundational-knowledge | 49 |
| §13 | okf-bundles | 323 |
| **合计** | | **2124** |

**校验等式**：5 + 63 + 199 + 321 + 546 + 146 + 55 + 93 + 200 + 114 + 10 + 49 + 323 = **2124** = 实测 md 总数 ✅

**逐节复核**（各节表格行求和）：
- §1：4+1 = 5 ✅
- §2：2+10+51 = 63 ✅
- §3：2+3+1+14+9+17+17+10+12+12+9+22+11+9+25+8+18 = 199 ✅
- §4：2+46+5+10+13+10+17+61+73+44+26+8+6 = 321 ✅
- §5：3+23+（1+10+14+12+38+10+11=96）+（1+72+25=98）+（1+9=10）+（1+11+11+15+19+9=66）+（1+88=89）+（1+10=11）+29+33+38+30+14+6 = 546 ✅
- §6：2+1+1+26+6+14+30+19+21+9+17 = 146 ✅
- §7：2+7+10+5+6+14+11 = 55 ✅
- §8：2+6+4+15+7+10+5+4+11+4+8+7+10 = 93 ✅
- §9：2+2+12+4+13+11+11+48+2+19+4+5+17+5+12+13+5+15 = 200 ✅
- §10：2+2+12+9+24+8+4+13+12+15+13 = 114 ✅
- §11：2+8 = 10 ✅
- §12：2+15+12+20 = 49 ✅
- §13：1+1+2+1+32+38+70+35+37+17+18+22+27+22 = 323 ✅

**交叉核对**：
- 实测总文件 2146 = md 2124 + 非 md 22 ✅
- 非 md 22 = 随迁 13 + 舍弃 9 ✅
- 隐私元数据不迁入 59（retrospective 12 + seven-concepts-report 10 + log.md 37），均包含在上表主题计数内，处置由 §14 覆盖 ✅
- 三级目录计数与二级目录递归计数逐项核对一致（first-principles 18+7+14+12=51、jira-skill-wiki 3+11+4+4=22、okf-wiki 13+7+5=25、01-paradigms 6+12+12+16=46、02-prompt-coding 5+10+13+10+17=55、03-methodology 3+16+42=61、04-context-optimization 3+14+37+19=73、05-evaluation 2+29+13=44、06-performance 4+11+11=26、00-agent-frameworks 1+10+14+12+13+11+14+10+11=96、01-domestic-platforms 1+72+11+14=98、02-security 1+9=10、03-code-devtools 1+11+11+15+19+9=66、05-mobile-testing 1+88=89、06-content-translation 1+10=11、agency-agents-wiki 15+9+2+3=29、cordis 17+8+2+6=33、deepseek-harness 20+14+4=38、okf-kit 16+9+5=30、open-code-review 2+8+4=14、executablebooks-myst-guide 9+11+2+2+2=26、myst-markdown-tutorial 19+4+7=30、pyinvoke-wiki 3+10+6=19、baidu 2+12=14、google-cloud 3+8=11、miaowu 2+4+5=11、okr-wiki 4+3+8+8+6+6+9+4=48、openai 2+19=21、oray 4+5=9、sunlogin 17+5+12+13=47、academic-skills 1+14=15、mathematical-foundations 1+11=12、chaos 4+32+38+70+35+37+17+18+22+27+22=322）✅
