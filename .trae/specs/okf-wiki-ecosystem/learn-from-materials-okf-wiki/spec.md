---
title: "Spec：learn-from-materials OKF 知识包"
status: "draft"
---

# Spec：learn-from-materials OKF 知识包

> 来源：GitHubDaily《一个神级学习 Skill，开源了！》（2026-11-03）
> URL：https://mp.weixin.qq.com/s/MUvHmFc4ItWfN57tuNjZkQ
> 模式：blog-article-to-okf-bundle L2（工具教程完整骨架，含 examples/）

## 产出位置

- Bundle：`projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/learn-from-materials/`
- 归属：ai 域 / ai-agent 组 / `### 📰 产品资讯` 段（与 claude-vision-skill、show-me-skill、hypit-video-replication、book-to-skill 同段）

### 归属判定（候选位置 | 判定 | 理由）

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/frameworks/ai-agent/` | ✅ 采用 | 主线实体是 Agent Skill；`ai-agent/index.md` 明确"本组也容纳官方文档驱动的架构学习包；资讯转化采用 R→I→E→V 核验"；`### 📰 产品资讯` 段已有 `claude-vision-skill`／`show-me-skill`／`hypit-video-replication`／`wigolo` 等同族工具教程先例；`book-to-skill`（书籍→Agent Skill 编译器）与本文功能最直接类比 |
| `jishu/ai/products/` | ❌ 不采用 | 该分类是终端任务型产品工具，本文主线是 Skill 本体而非宿主产品 |
| `jishu/ai/learning/` | ❌ 不采用 | 该分类是学习路径与上手教程，本文主体是工具能力而非学习体系 |
| 新建分组 | ❌ 禁止 | 单篇博文不得新建分组（最小变更） |

## 文件骨架（13 文件）

| 文件 | 内容 |
|------|------|
| index.md | 知识包入口、机制图、分层导航、信任声明、已知边界 |
| concepts/index.md | 概念学习路径（4篇） |
| concepts/00-project-overview.md | 项目是什么：定位、仓库画像、许可与语言、开源状态 |
| concepts/01-material-to-learning-page.md | 材料→学习网页机制：单一顺序工作流、六板块、`.learnkb/`、来源映射、四类内容区分 |
| concepts/02-two-depths-and-methodology.md | 两种深度（快速了解/系统学习）+ 方法论库（methods.json/methodology.json）与交付物 |
| concepts/03-host-integration-and-boundaries.md | 宿主集成与安装目录表、运行要求、兼容边界与不可用场景 |
| examples/index.md | 实战索引（2篇） |
| examples/00-install-and-three-steps.md | 安装（ZIP/git 两法）+ 博文三步实操（逐字提示词）+ CLI 链 |
| examples/01-output-and-sharing.md | 学习网页六板块读法 + 两种深度产出差异 + 分享链接流程与边界 |
| references/index.md | 信源索引（官方文档链接） |
| references/article-source.md | F-001~F-041 事实登记 |
| references/verification.md | P0核验报告（9✅+1⚠️ 口径差异 + 单源项登记） |
| log.md | 变更日志 |

## 事实基数

41条事实（F-001~F-041）；P0核验10项（9项 ✅ 通过 + 1项 ⚠️ 口径差异双源并列）；4项单源/一手实测已标注；3项官方补充（支持格式面更宽、版本号 1.1.0、两种深度与 CLI 链）。

## 质量门

- G1（事实）：41条编号登记，主信源逐字提取、官方 README 双份比对 ✅
- G2（核验）：P0 9/10 ✅；1项口径差异（豆包工作 vs README 宿主清单）双源并列不掩盖 ✅
- G3（结构）：三级 toctree、相对链接、无 `file:///`、UTF-8 严格解码 ✅
- G4（索引）：⏸️ **登记延后** —— 共享索引（`doc/bundles/index.md`、`doc/index.md`、`README.md`、`jishu/**/index.md`）被并发的在途会话改动占用（含 5 个未跟踪新束：`super-agent-architecture`、`doubao-work-remotion-photo-video`、`ub-mode-coding-discipline`、`pagekin`、`riscv-automotive`）。为避免回滚其未提交变更，本次**仅交付包体**：父级 toctree 登记（`ai-agent/index.md` 加 `learn-from-materials/index`）与各级计数（含本包 1 束）交由该会话统一处理。另注：**HEAD（3a6b6280）目录树实际 704 束，而索引声明 703**，本身已漂移 +1。
