# okf-wiki-ecosystem — OKF/Wiki 知识生态

OKF/Wiki 知识生态：外部源码、官方文档、博客文章的知识化转译（OKF 知识包/Wiki 教程）spec。

**Spec 数量**：154（2026-09-20 docgen 扫描；明细见下方看板）
**上级看板**：[返回全局执行看板](../README.md)

---

## &#128451; 主题说明

- **归属判定**：OKF/Wiki 知识生态：外部源码、官方文档、博客文章的知识化转译（OKF 知识包/Wiki 教程）spec
- **新增 Spec 流程**：先查重 → 创建三件套 → 全局看板由 docgen（C-6）自动刷新

*本看板由 Python 脚本于 2026-09-04 生成（C-2b），后续应由 docgen 自动化维护（C-6）。*

> 生成器兼容性说明（2026-09-20）：当前 docgen 按旧复选框统计任务，未识别新版 `Status` 字段，且尚未检测 `review.md`。因此下表“三件套”不代表文件真实存在性；进行中任务与审查结果以各 Spec 的 `tasks.md`、`review.md` 为准。

<!-- THEME_DASHBOARD_START -->

| # | Spec 名称 | 状态 | 三件套 |
|---|---|---|---|
| 1 | [3b1b-okf-wiki](3b1b-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 2 | [a2a-mcp-convergence-okf-wiki](a2a-mcp-convergence-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 3 | [adversarial-review-knowledge-base](adversarial-review-knowledge-base/spec.md) | ✓ 完成 | ✓✗✗ |
| 4 | [agent-app-marketplace](agent-app-marketplace/spec.md) | ? 待启动 | ✓/✗ |
| 5 | [agent-architecture-book-outline](agent-architecture-book-outline/spec.md) | ? 待启动 | ✓/✗ |
| 6 | [agent-lightning-blog-okf-wiki](agent-lightning-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 7 | [agent-reach-blog-okf-wiki](agent-reach-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 8 | [agentgit-blog-okf-wiki](agentgit-blog-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 9 | [agentskills-okf-wiki](agentskills-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 10 | [agora-gemini-transcribe-okf-wiki](agora-gemini-transcribe-okf-wiki/spec.md) | ! 进行中 | ✓/✗ |
| 11 | [ai-agent-book-blog-okf-wiki](ai-agent-book-blog-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 12 | [ai-agent-deep-wiki](ai-agent-deep-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 13 | [ai-agents-okf-wiki](ai-agents-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 14 | [ai-app-survival-okf-wiki](ai-app-survival-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 15 | [ai-one-person-micro-product](ai-one-person-micro-product/spec.md) | ✓ 完成 | ✓✗✗ |
| 16 | [ai-powershell5-hell-wiki](ai-powershell5-hell-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 17 | [ai-side-hustle-playbook-blog-okf-wiki](ai-side-hustle-playbook-blog-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 18 | [aitokenbus-blog-okf-wiki](aitokenbus-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 19 | [anthropic-python-sdk-okf-wiki](anthropic-python-sdk-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 20 | [anything-okf-wiki](anything-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 21 | [auto-money-system-blog-okf-wiki](auto-money-system-blog-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 22 | [awesome-okf-exploration](awesome-okf-exploration/spec.md) | ✓ 完成 | ✓✗✗ |
| 23 | [awesome-okf-xs-doc](awesome-okf-xs-doc/spec.md) | ✓ 完成 | ✓/✗ |
| 24 | [book-to-skill-wiki](book-to-skill-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 25 | [bytedance-ai-consolidation-blog-okf-wiki](bytedance-ai-consolidation-blog-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 26 | [chaos-libs-okf-wiki](chaos-libs-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 27 | [claude-vision-skill-okf-wiki](claude-vision-skill-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 28 | [codex-agent-workflow-practices](codex-agent-workflow-practices/spec.md) | ? 待启动 | ✓✗✗ |
| 29 | [conda-source-okf-wiki](conda-source-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 30 | [containers-okf-wiki](containers-okf-wiki/spec.md) | ? 待启动 | ✓/✗ |
| 31 | [coze-dev-okf-wiki](coze-dev-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 32 | [create-ai-security-okf-wiki](create-ai-security-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 33 | [create-claude-system-prompts-wiki](create-claude-system-prompts-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 34 | [create-conda-dev-github-wiki-tutorial](create-conda-dev-github-wiki-tutorial/spec.md) | ! 进行中 | ✓/✗ |
| 35 | [create-conda-dev-source-wiki-tutorial](create-conda-dev-source-wiki-tutorial/spec.md) | ✓ 完成 | ✓/✗ |
| 36 | [create-cordis-paper-wiki-tutorial](create-cordis-paper-wiki-tutorial/spec.md) | ✓ 完成 | ✓/✗ |
| 37 | [create-hermes-okf-wiki-tutorial](create-hermes-okf-wiki-tutorial/spec.md) | ? 待启动 | ✓/✗ |
| 38 | [create-mermaid-wiki-tutorial](create-mermaid-wiki-tutorial/spec.md) | ✓ 完成 | ✓/✗ |
| 39 | [create-python314-stdlib-wiki-tutorial](create-python314-stdlib-wiki-tutorial/spec.md) | ✓ 完成 | ✓/✗ |
| 40 | [create-rea-okf-wiki](create-rea-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 41 | [create-sst-okf-wiki-tutorial](create-sst-okf-wiki-tutorial/spec.md) | ? 待启动 | ✓✗✗ |
| 42 | [create-standardized-agent-exams-okf-wiki](create-standardized-agent-exams-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 43 | [create-teaching-learning-okf-wiki](create-teaching-learning-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 44 | [create-xmnn-sdk-sphinx-docs](create-xmnn-sdk-sphinx-docs/spec.md) | ✓ 完成 | ✓/✗ |
| 45 | [cua-computer-use-blog-okf-wiki](cua-computer-use-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 46 | [datawhalechina-okf-wiki](datawhalechina-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 47 | [deepseek-ai-okf-wiki](deepseek-ai-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 48 | [deepseek-harness-mobile-blog-okf-wiki](deepseek-harness-mobile-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 49 | [deepseek-harness-wiki](deepseek-harness-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 50 | [deepseek-v4-free-plan-research](deepseek-v4-free-plan-research/spec.md) | ? 待启动 | ✓✗✗ |
| 51 | [deepseek-vision-blog-okf-wiki](deepseek-vision-blog-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 52 | [docs-okf-wiki-conversion](docs-okf-wiki-conversion/spec.md) | ? 待启动 | ✓✗✗ |
| 53 | [docs-to-okf-wiki-conversion](docs-to-okf-wiki-conversion/spec.md) | ✓ 完成 | ✓/✗ |
| 54 | [dolt-okf-wiki](dolt-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 55 | [domestic-token-export](domestic-token-export/spec.md) | ? 待启动 | ✓✗✗ |
| 56 | [doubao-work-context-layer-okf-wiki](doubao-work-context-layer-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 57 | [doubao-work-feishu-okf-wiki](doubao-work-feishu-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 58 | [doubao-work-org-productivity-okf-wiki](doubao-work-org-productivity-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 59 | [eve-framework-wiki-tutorial](eve-framework-wiki-tutorial/spec.md) | ✓ 完成 | ✓/✗ |
| 60 | [evox-agent-review](evox-agent-review/spec.md) | ? 待启动 | ✓✗✗ |
| 61 | [excellent-works-catalog](excellent-works-catalog/spec.md) | ? 待启动 | ✓/✗ |
| 62 | [executablebooks-okf-wiki](executablebooks-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 63 | [extend-cua-bundle-with-okw-solution](extend-cua-bundle-with-okw-solution/spec.md) | ✓ 完成 | ✓/✗ |
| 64 | [fastapi-okf-wiki](fastapi-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 65 | [female-charm-eq](female-charm-eq/spec.md) | ? 待启动 | ✓✗✗ |
| 66 | [firecrawl-blog-okf-wiki](firecrawl-blog-okf-wiki/spec.md) | ! 进行中 | ✓/✗ |
| 67 | [free-claude-code-career-ops-blog-okf-wiki](free-claude-code-career-ops-blog-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 68 | [free-llm-api-hands-on-blog-okf-wiki](free-llm-api-hands-on-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 69 | [free-llm-api-roundup](free-llm-api-roundup/spec.md) | ? 待启动 | ✓✗✗ |
| 70 | [free-llm-api-roundup-okf-wiki](free-llm-api-roundup-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 71 | [gpt56-large-prime-gaps-okf-wiki](gpt56-large-prime-gaps-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 72 | [gpt6-astra-usage-guide-okf-wiki](gpt6-astra-usage-guide-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 73 | [gpt6-sol-luna-blog-okf-wiki](gpt6-sol-luna-blog-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 74 | [graphql-okf-wiki](graphql-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 75 | [guard-quality-life-okf-wiki-site](guard-quality-life-okf-wiki-site/spec.md) | ? 待启动 | ✓✗✗ |
| 76 | [hangzhou-qiuyinyuan-okf-wiki](hangzhou-qiuyinyuan-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 77 | [harness-seven-components-wiki](harness-seven-components-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 78 | [harvest-aidomain-wechat-okf-skill](harvest-aidomain-wechat-okf-skill/spec.md) | ? 待启动 | ✓✗✗ |
| 79 | [hermes-agent-installation](hermes-agent-installation/spec.md) | ! 进行中 | ✓/✗ |
| 80 | [hermes-agent-learning-wiki](hermes-agent-learning-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 81 | [hongge-okf-wiki](hongge-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 82 | [how-to-live-better-okf-wiki](how-to-live-better-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 83 | [hr-admin-okf-wiki](hr-admin-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 84 | [huawei-ai-shell-blog-okf-wiki](huawei-ai-shell-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 85 | [hypit-video-replication-okf-wiki](hypit-video-replication-okf-wiki/spec.md) | ! 进行中 | ✓/✗ |
| 86 | [i-have-adhd-wiki-tutorial](i-have-adhd-wiki-tutorial/spec.md) | ✓ 完成 | ✓/✗ |
| 87 | [integrate-specweave-into-hermes-agent](integrate-specweave-into-hermes-agent/spec.md) | ✓ 完成 | ✓/✗ |
| 88 | [inurl-free-models-blog-okf-wiki](inurl-free-models-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 89 | [jev-automation-decision-okf-wiki](jev-automation-decision-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 90 | [jev-decision-model-okf-wiki](jev-decision-model-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 91 | [jira-skill-okf-wiki](jira-skill-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 92 | [jupyter-book-okf-wiki](jupyter-book-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 93 | [jupyter-extension-template-okf](jupyter-extension-template-okf/spec.md) | ? 待启动 | ✓✗✗ |
| 94 | [jupyter-okf-wiki-group](jupyter-okf-wiki-group/spec.md) | ? 待启动 | ✓/✗ |
| 95 | [jupyterlab-okf-wiki-completion](jupyterlab-okf-wiki-completion/spec.md) | ? 待启动 | ✓/✗ |
| 96 | [jupyterlab-translate-wiki](jupyterlab-translate-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 97 | [katex-okf-wiki-update](katex-okf-wiki-update/spec.md) | ✓ 完成 | ✓/✗ |
| 98 | [knocket-okf-wiki](knocket-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 99 | [knowledge-base-wiki-template](knowledge-base-wiki-template/spec.md) | ? 待启动 | ✓/✗ |
| 100 | [knowledge-catalog-wiki](knowledge-catalog-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 101 | [knowledge-consolidation](knowledge-consolidation/spec.md) | ? 待启动 | ✓✗✗ |
| 102 | [kylin-wlcom-okf-wiki](kylin-wlcom-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 103 | [langchain-ai-okf-wiki](langchain-ai-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 104 | [liaoyu-visual-assets](liaoyu-visual-assets/spec.md) | ✓ 完成 | ✓/✗ |
| 105 | [lift-agent-evolution](lift-agent-evolution/spec.md) | ✓ 完成 | ✓✗✗ |
| 106 | [lightvela-personal-agent-blog-okf-wiki](lightvela-personal-agent-blog-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 107 | [llama-cpp-local-inference-okf-wiki](llama-cpp-local-inference-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 108 | [llm-hallucination-governance-okf-wiki](llm-hallucination-governance-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 109 | [loopx-long-horizon-agent-okf-wiki](loopx-long-horizon-agent-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 110 | [male-charm-eq](male-charm-eq/spec.md) | ✓ 完成 | ✓✗✗ |
| 111 | [matrix-agent-company-blog-okf-wiki](matrix-agent-company-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 112 | [mattpocock-skills-wiki](mattpocock-skills-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 113 | [microsoft-mxc-agent-containment-blog-okf-wiki](microsoft-mxc-agent-containment-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 114 | [naval-learn-build-link-blog-okf-wiki](naval-learn-build-link-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 115 | [netease-youdao-okf-wiki](netease-youdao-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 116 | [neural-compressor-wiki](neural-compressor-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 117 | [nuitka-okf-wiki](nuitka-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 118 | [okf-100ep-anime](okf-100ep-anime/spec.md) | ! 进行中 | ✓/✗ |
| 119 | [okf-bundles-integrity](okf-bundles-integrity/spec.md) | ? 待启动 | ✓/✗ |
| 120 | [okf-ecosystem-infrastructure-learning](okf-ecosystem-infrastructure-learning/spec.md) | ✓ 完成 | ✓/✗ |
| 121 | [okf-kit-navigation-pattern-sediment](okf-kit-navigation-pattern-sediment/spec.md) | ✓ 完成 | ✓/✗ |
| 122 | [okf-knowledge-qa](okf-knowledge-qa/spec.md) | ? 待启动 | ✓✗✗ |
| 123 | [okf-open-knowledge-format-wiki](okf-open-knowledge-format-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 124 | [okf-spec-enrichment](okf-spec-enrichment/spec.md) | ? 待启动 | ✓✗✗ |
| 125 | [okf-spec-to-bundle](okf-spec-to-bundle/spec.md) | ✓ 完成 | ✓/✗ |
| 126 | [okf-toolchain-implementation](okf-toolchain-implementation/spec.md) | ✓ 完成 | ✓/✗ |
| 127 | [okr-wiki-manual](okr-wiki-manual/spec.md) | ✓ 完成 | ✓/✗ |
| 128 | [onnx-ecosystem-okf-wiki](onnx-ecosystem-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 129 | [onnx-wiki-tutorial](onnx-wiki-tutorial/spec.md) | ✓ 完成 | ✓/✗ |
| 130 | [open-source-subscription-alternatives-okf-wiki](open-source-subscription-alternatives-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 131 | [opencode-source-wiki](opencode-source-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 132 | [opencode-source-wiki-deepening](opencode-source-wiki-deepening/spec.md) | ? 待启动 | ✓✗✗ |
| 133 | [openhuman-blog-okf-wiki](openhuman-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 134 | [openmaic-wiki-20260909](openmaic-wiki-20260909/spec.md) | ? 待启动 | ✓✗✗ |
| 135 | [openmontage-agent-video-okf-wiki](openmontage-agent-video-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 136 | [opentui-okf-wiki](opentui-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 137 | [openviking-blog-okf-wiki](openviking-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 138 | [optimize-mystx-python314-stdlib](optimize-mystx-python314-stdlib/spec.md) | ✓ 完成 | ✓/✗ |
| 139 | [optimize-okf-python314-stdlib](optimize-okf-python314-stdlib/spec.md) | ✓ 完成 | ✓/✗ |
| 140 | [oracle-blog-okf-wiki](oracle-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 141 | [orca-ade-okf-wiki](orca-ade-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 142 | [overseas-freelance-night-work](overseas-freelance-night-work/spec.md) | ✓ 完成 | ✓✗✗ |
| 143 | [physics-okf-wiki](physics-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 144 | [pi-agent-harness-okf-wiki](pi-agent-harness-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 145 | [pickle-serialization-knowledge-sediment](pickle-serialization-knowledge-sediment/spec.md) | ✓ 完成 | ✓/✗ |
| 146 | [pinedrama-monetization-playbook](pinedrama-monetization-playbook/spec.md) | ? 待启动 | ✓✗✗ |
| 147 | [pocketflow-okf-wiki](pocketflow-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 148 | [podman-py-wiki-r3](podman-py-wiki-r3/spec.md) | ? 待启动 | ✓✗✗ |
| 149 | [protobuf-versions-wiki](protobuf-versions-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 150 | [protocolbuffers-okf-wiki](protocolbuffers-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 151 | [public-apis-blog-okf-wiki](public-apis-blog-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 152 | [pyinvoke-okf-wiki](pyinvoke-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 153 | [python314-cpython-wiki](python314-cpython-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 154 | [qbs-book-to-skill-okf-wiki](qbs-book-to-skill-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 155 | [qwen-creative-platform-news-okf-wiki](qwen-creative-platform-news-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 156 | [qwen-ui-agent-review-okf-wiki](qwen-ui-agent-review-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 157 | [rea-official-site-expansion](rea-official-site-expansion/spec.md) | ? 待启动 | ✓✗✗ |
| 158 | [real-needs-discovery-okf-wiki](real-needs-discovery-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 159 | [remote-messaging-okf-wiki](remote-messaging-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 160 | [rust-lang-okf-wiki](rust-lang-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 161 | [scrapli-full-coverage-wiki](scrapli-full-coverage-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 162 | [sell-before-build-blog-okf-wiki](sell-before-build-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 163 | [show-me-skill-okf-wiki](show-me-skill-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 164 | [siemens-industrial-agent-okf-wiki](siemens-industrial-agent-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 165 | [skills-manager-blog-okf-wiki](skills-manager-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 166 | [sphinx-argparse-okf-wiki](sphinx-argparse-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 167 | [ssh-python-okf-wiki](ssh-python-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 168 | [sympy-okf-wiki](sympy-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 169 | [tencent-buddy-family-blog-okf-wiki](tencent-buddy-family-blog-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 170 | [tencent-meeting-cli-reaudit-okf-wiki](tencent-meeting-cli-reaudit-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 171 | [tencent-okf-wiki](tencent-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 172 | [tencent-runtime-okf-wiki](tencent-runtime-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 173 | [textualize-okf-wiki](textualize-okf-wiki/spec.md) | ! 进行中 | ✓/✗ |
| 174 | [threeui-okf-wiki](threeui-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 175 | [tiktoken-okf-wiki](tiktoken-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 176 | [tkinter-okf-wiki](tkinter-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 177 | [toddler-chinese-animation](toddler-chinese-animation/spec.md) | ✓ 完成 | ✓/✗ |
| 178 | [token-economy-explosion](token-economy-explosion/spec.md) | ? 待启动 | ✓✗✗ |
| 179 | [tongyi-mai-okf-wiki](tongyi-mai-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 180 | [toolbox-source-okf-wiki](toolbox-source-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 181 | [tushare-ai-office-okf-wiki](tushare-ai-office-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 182 | [tvm-ffi-200-perspectives](tvm-ffi-200-perspectives/spec.md) | ✓ 完成 | ✓/✗ |
| 183 | [tvm-ffi-wiki-tutorial](tvm-ffi-wiki-tutorial/spec.md) | ✓ 完成 | ✓/✗ |
| 184 | [u2flash-free-month-okf-wiki](u2flash-free-month-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 185 | [update-invocations-bundle-optimize-okf](update-invocations-bundle-optimize-okf/spec.md) | ? 待启动 | ✓/✗ |
| 186 | [uumit-a2a-marketplace-blog-okf-wiki](uumit-a2a-marketplace-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 187 | [veadk-python-wiki](veadk-python-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 188 | [verbi-okf-wiki](verbi-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 189 | [vista-visual-harness-blog-okf-wiki](vista-visual-harness-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 190 | [volcengine-agent-plan-wiki-followups](volcengine-agent-plan-wiki-followups/spec.md) | ! 进行中 | ✓/✗ |
| 191 | [volcengine-agentkit-wiki](volcengine-agentkit-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 192 | [wechat-anti-aging-er100-nmn-okf-wiki](wechat-anti-aging-er100-nmn-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 193 | [wechat-presence-joy-meditation-blog-okf-wiki](wechat-presence-joy-meditation-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 194 | [wechat-probability-relationship-okf-wiki](wechat-probability-relationship-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 195 | [wecom-5-0-10-release-okf-wiki](wecom-5-0-10-release-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 196 | [wecom-5-0-12-release-okf-wiki](wecom-5-0-12-release-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 197 | [wecom-topic-scenarios-okf-wiki](wecom-topic-scenarios-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 198 | [weknora-blog-okf-wiki](weknora-blog-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 199 | [wigolo-blog-okf-wiki](wigolo-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 200 | [workbuddy-content-system](workbuddy-content-system/spec.md) | ✓ 完成 | ✓✗✗ |
| 201 | [workbuddy-hardware-integration-whitepaper-okf-wiki](workbuddy-hardware-integration-whitepaper-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 202 | [workbuddy-library-practice](workbuddy-library-practice/spec.md) | ? 待启动 | ✓✗✗ |
| 203 | [workbuddy-official-docs-okf-wiki](workbuddy-official-docs-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 204 | [workbuddy-one-sentence-blog-okf-wiki](workbuddy-one-sentence-blog-okf-wiki/spec.md) | ! 进行中 | ✓/✗ |
| 205 | [workbuddy-opc-whitepaper-okf-wiki](workbuddy-opc-whitepaper-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 206 | [workbuddy-open-platform-docs-okf-wiki](workbuddy-open-platform-docs-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 207 | [workbuddy-open-platform-sharing-and-promotion-okf-wiki](workbuddy-open-platform-sharing-and-promotion-okf-wiki/spec.md) | ✓ 完成 | ✓✗✗ |
| 208 | [workbuddy-sandbox-public-endpoint](workbuddy-sandbox-public-endpoint/spec.md) | ✓ 完成 | ✓/✗ |
| 209 | [wrap-bare-urls-mermaid-wiki](wrap-bare-urls-mermaid-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 210 | [xingchen300-edge-ai-blog-okf-wiki](xingchen300-edge-ai-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 211 | [xmtools-700-perspectives-okf-wiki](xmtools-700-perspectives-okf-wiki/spec.md) | ✓ 完成 | ✓/✗ |
| 212 | [zdtaichu5-0-9b-blog-okf-wiki](zdtaichu5-0-9b-blog-okf-wiki/spec.md) | ? 待启动 | ✓✗✗ |
| 213 | [zhihu-cli-okf-wiki](zhihu-cli-okf-wiki/spec.md) | ! 进行中 | ✓/✗ |
| 214 | [zleap-agent-learning-wiki](zleap-agent-learning-wiki/spec.md) | ✓ 完成 | ✓/✗ |

<!-- THEME_DASHBOARD_END -->
