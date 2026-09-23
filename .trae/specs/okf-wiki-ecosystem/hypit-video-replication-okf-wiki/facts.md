---
type: Reference
title: "Hypit 博文转化事实底稿"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/N5jRPXG_fSs668l5mSUdvQ?from=industrynews&color_scheme=light#rd
  - id: repo
    resource: https://github.com/hypit-ai/hypit
  - id: readme
    resource: https://raw.githubusercontent.com/hypit-ai/hypit/main/README.md
  - id: skill
    resource: https://raw.githubusercontent.com/hypit-ai/hypit/main/skills/hypit/SKILL.md
---

# 事实登记

| 编号 | 事实 | 来源/状态 |
|---|---|---|
| F-001 | 文章标题为《一条视频复刻 100 个版本，Hypit 开源了。》 | blog，页面元数据 |
| F-002 | 作者署名“开源日记”，发布时间为 2026-09-21 11:49。 | blog，页面元数据 |
| F-003 | Hypit 官方仓库为 `hypit-ai/hypit`，公开仓库。 | repo，已核验 |
| F-004 | 官方 README 将 Hypit 定位为“用 AI Agent 克隆视频”，可将参考视频转为完整工作流。 | readme，已核验 |
| F-005 | 工作流覆盖 footage、captions、B-roll 和 effects，并以 words 而非 seconds 作为锚点。 | readme，已核验 |
| F-006 | 视频克隆不是唯一入口，也可从模板或自然语言描述从零生成工作流。 | readme，已核验 |
| F-007 | 生成模型是可选项，字幕、动效和代码渲染视觉可在不调用生成模型时编译为视频。 | readme，已核验 |
| F-008 | 官方 Skill 名为 `hypit`，描述包含 SVML、SVS、SVRun 编写与 Runtime/凭证设置。 | skill，已核验 |
| F-009 | 安装命令为 `npx skills add hypit-ai/hypit -g`。 | readme，已核验 |
| F-010 | 官方 README 提供 Quickstart、Develop、Demo 入口。 | readme，已核验 |
| F-011 | 官方仓库徽章声明 Node.js 22.15+、pnpm 10.33、TypeScript 5.9。 | readme，已核验 |
| F-012 | 官方仓库许可证徽章为 Apache-2.0 with conditions。 | readme，已核验 |
| F-013 | 官方 GOAT DEBATE 示例是 20 秒足球 tier list。 | readme，已核验 |
| F-014 | GOAT DEBATE 示例使用两段 Seedance 2 Mini 720p、GPT Image 2、WhisperX 词级对齐和声音同步排行榜。 | readme，已核验 |
| F-015 | GOAT DEBATE 示例包含三个 clone：香蕉猫解说、翻转排名、科技公司创始人版本。 | readme，已核验 |
| F-016 | 官方页面给出 GOAT DEBATE 示例总成本 `$1.15`。 | readme，官方示例口径 |
| F-017 | 官方页面说明示例并发使用 64 个 headless Chromium 进程。 | readme，官方示例口径 |
| F-018 | 官方还展示 Podcast 和 Street Interview 示例，均可复用结构并替换人物或产品。 | readme，已核验 |
| F-019 | 官方列出 TikTok Shop/affiliate、AI UGC、播客访谈、代码渲染视频等应用方向。 | readme，定位声明 |
| F-020 | 官方 Skill 要求收到参考视频时检查画面、帧和语音时间，并理解参考视频的结构。 | skill，已核验 |
| F-021 | Skill 将 Brief、Treatment、Timeline、Components 与 Runtime 作为制作过程中的不同概念。 | skill，已核验 |
| F-022 | Skill 建议在 clone 中识别 cut、picture、reveal、sound 对应的语义关系，再为目标词语和意图重建关系。 | skill，已核验 |
| F-023 | 博文称项目已获得 1.1 万多个 GitHub Star。 | blog，时点单源 |
| F-024 | 博文将 Hypit 适用于信息流广告、TikTok Shop、联盟营销、AI UGC 和短视频批量生产。 | blog，作者转述/未作效果核验 |

