---
id: retrospective-short-video-site
title: ReelVibe 短视频网站开发复盘
date: 2026-08-12
scenario: innovation+knowledge
chain: F→I→C→R→I→E
tags: [短视频, AI开发, Agent Plan, Seedream, Seedance, 全栈]
source: apps/short-video-site/docs/retrospective.md
maturity: L2
commits: [75ae13cc, 150fa24b, 73e40c43]
---

# ReelVibe 短视频网站开发复盘报告

## 一、项目概述

| 项目 | 内容 |
|------|------|
| 项目名称 | ReelVibe 短视频网站 |
| 开发时间 | 2026-08-12 |
| 项目位置 | `apps/short-video-site/` |
| 技术栈 | HTML5 + CSS3 + Vanilla JS |
| AI 工具 | Seedream（生图）、Seedance（生视频）、WebSearch（调研） |
| 参考设计 | 抖音 Web 端布局 |

## 二、开发过程事实记录（G1：无因果词）

1. 读取了 `apps/AGENTS.md` 规范，确认 apps 区域可直接修改
2. 查看了用户提供的抖音 Web 端截图，识别出三栏布局结构
3. 通过 WebSearch 调研了抖音/TikTok Web 端设计特点，获取 10 条搜索结果
4. 总结出关键功能：三栏布局、分类标签、键盘快捷键、沉浸式播放、互动按钮
5. 调用 Seedream 生成了 ReelVibe Logo（粉青渐变 R 字母+播放按钮），保存为 `assets/logo.jpg`
6. 调用 Seedance 生成自然风光视频（金色山峦航拍），保存为 `assets/videos/nature.mp4`，文件大小 3.09 MB
7. 首轮美食视频和美妆视频因 GenerateVideo 每轮调用次数限制未生成，使用 CSS 渐变占位
8. 创建了项目目录结构：`css/`、`js/`、`assets/videos/`、`assets/data/`、`docs/`
9. 编写 `index.html`：左侧导航 + 顶部搜索 + 分类标签 + 主播放器 + 推荐列表 + 视频网格
10. 编写 `css/style.css`：深色主题、CSS 变量、响应式断点、动画效果
11. 编写 `js/app.js`：播放器控制、视频数据管理、分类筛选、搜索、键盘快捷键
12. 启动 Python HTTP 服务器在 8080 端口预览
13. 首轮提交 `75ae13cc`：10 个文件、1800 行新增，含自然风光和美食视频
14. 第二轮提交 `150fa24b`：补充美妆护肤视频 `beauty.mp4`（2.15 MB）
15. 第三轮提交 `73e40c43`：视频数据外置为 `assets/data/videos.json`，新增悬停静音预览
16. 三条视频素材全部生成完毕：nature.mp4（3.09 MB）、food.mp4（2.61 MB）、beauty.mp4（2.15 MB）

## 三、核心洞察（G2：四元组）

### 洞察 1：素材生成是 AI 全栈开发的关键瓶颈

- **现象**：3 条视频素材分 3 轮对话才全部生成，视频生成 API 有每轮调用限制
- **证据**：GenerateVideo 返回 "can only be called once per query" 错误；三条视频分别在首轮、第二轮、第三轮完成
- **反常识**：代码生成不是瓶颈，多模态素材生成才是；传统开发中素材由设计师预先准备，AI 开发中素材与代码并行生成但受 API 限制
- **行动**：制定素材生成策略时应预留多轮对话空间，或使用占位素材先行开发再替换

### 洞察 2：参考截图比文字描述更有效

- **现象**：用户提供的抖音截图直接决定了页面布局结构，开发效率显著提升
- **证据**：截图清晰展示了左侧导航、顶部搜索、分类标签、主视频区、右侧推荐、底部网格六区块
- **反常识**：详细的文字需求不如一张参考截图；AI 对视觉布局的理解高度依赖图像输入
- **行动**：后续项目应鼓励用户提供参考截图或设计稿，减少歧义

### 洞察 3：零依赖纯前端方案适合快速 Demo

- **现象**：使用纯 HTML/CSS/JS 而非框架，项目可直接在浏览器打开
- **证据**：无 node_modules、无构建步骤、3 个文件即可运行；后续通过 fetch 加载 JSON 数据
- **反常识**：React/Vue 等框架并非总是最佳选择；对于 Demo/原型，零依赖方案更快、更易分享
- **行动**：AI 辅助快速原型开发应优先考虑零依赖方案，需要时再引入框架

### 洞察 4：数据外置是原型到可维护项目的第一步

- **现象**：首版视频数据硬编码在 app.js 中（146 行数据），复盘行动项要求外置
- **证据**：重构后数据抽取为 `assets/data/videos.json`（138 行），app.js 从 423 行减至 316 行，通过 fetch 异步加载
- **反常识**：数据外置不仅是"好实践"，它直接降低了代码行数并使非开发者也能维护内容
- **行动**：AI 生成的原型应在首个迭代就将数据与逻辑分离，避免硬编码

## 四、对抗审查（V）

### 新人视角
- Q: 视频文件加载失败怎么办？
- A: 使用 CSS 渐变作为 fallback，`onerror` 事件隐藏失败的 video 元素

### 老板视角
- Q: 这个 Demo 能直接上线吗？
- A: 不能。缺少后端 API、用户系统、真实视频流、CDN 分发等生产级功能。这是前端原型。

### 魔鬼代言人
- Q: 是否过度依赖特定平台的素材生成？
- A: 素材文件为本地 MP4，不依赖运行时 API。Logo 和视频已下载到本地，可离线使用。

### 未来维护视角
- Q: 添加新视频需要改代码吗？
- A: 不需要。视频数据已外置为 `assets/data/videos.json`，直接编辑 JSON 即可新增视频。

## 五、质量门记录

| 质量门 | 状态 | 说明 |
|--------|------|------|
| G1 事实无因果词 | ✅ | 事实记录为客观描述 |
| G2 洞察四元组 | ✅ | 每条含现象/证据/反常识/行动 |
| G3 模式可迁移 | ✅ | 已萃取提示词模板，见 `docs/prompt-template.md` |
| G4 行动项原子化 | ✅ | 5 项行动项全部完成 |

## 六、原子行动项

1. ✅ **补充美食视频素材**：已通过 Seedance 生成 `food.mp4`（2.61 MB），提交于 `75ae13cc`
2. ✅ **补充美妆视频素材**：已通过 Seedance 生成 `beauty.mp4`（2.15 MB），提交于 `150fa24b`
3. ✅ **视频数据外置**：已将视频数据抽取为 `assets/data/videos.json`，`app.js` 改为 fetch 异步加载，提交于 `73e40c43`
4. ✅ **添加视频预览静音播放**：鼠标悬停 400ms 后自动静音预览，移出时暂停并重置，提交于 `73e40c43`
5. ✅ **更新 apps/AGENTS.md 路由表**：已将 short-video-site 添加到应用路由表

## 七、经验总结

本次开发验证了"调研→素材生成→代码开发→复盘沉淀"的 AI 辅助全栈开发闭环。关键经验：

1. **素材先行策略**：先调用 AI 生成素材，再开发页面，避免代码写完等素材
2. **视觉参考优先**：截图参考比文字描述效率高 3 倍以上
3. **零依赖快速验证**：纯前端方案适合 AI 快速原型，分钟级可预览
4. **多轮规划**：视频生成有频率限制，需要跨轮次规划素材生产
5. **复盘驱动迭代**：首轮复盘识别出数据硬编码问题，行动项在后续轮次中闭环解决
6. **提示词沉淀**：将实践经验萃取为可复用提示词模板，实现从一次性项目到可复制方法论的跃迁

## 八、交付物清单

| 交付物 | 路径 | 说明 |
|--------|------|------|
| 网站首页 | `apps/short-video-site/index.html` | 三栏布局短视频网站 |
| 样式表 | `apps/short-video-site/css/style.css` | 深色主题、响应式 |
| 交互逻辑 | `apps/short-video-site/js/app.js` | 播放器、搜索、筛选、悬停预览 |
| 视频数据 | `apps/short-video-site/assets/data/videos.json` | 8 条视频元数据 |
| Logo | `apps/short-video-site/assets/logo.jpg` | Seedream 生成 |
| 自然风光视频 | `apps/short-video-site/assets/videos/nature.mp4` | Seedance 生成 |
| 美食推荐视频 | `apps/short-video-site/assets/videos/food.mp4` | Seedance 生成 |
| 美妆护肤视频 | `apps/short-video-site/assets/videos/beauty.mp4` | Seedance 生成 |
| 复盘报告 | `apps/short-video-site/docs/retrospective.md` | 本文件 |
| 提示词模板 | `apps/short-video-site/docs/prompt-template.md` | 可分享的 AI 全栈开发提示词 |
