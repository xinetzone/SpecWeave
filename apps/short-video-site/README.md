# ReelVibe - 短视频网站

> 基于 Agent Plan 全流程 AI 开发的短视频网站 Demo，参考抖音 Web 端设计，采用纯 HTML/CSS/JS 实现。

## 项目概述

ReelVibe 是一个简洁时尚的短视频浏览网站，还原了主流短视频平台 Web 端的核心布局与交互体验。

## 功能特性

- **三栏布局**：左侧导航 + 中间视频流 + 右侧推荐
- **视频播放器**：播放/暂停、进度条、音量控制、全屏
- **分类筛选**：全部、公开课、影视、游戏、音乐、美食、美妆穿搭、旅行等
- **搜索功能**：支持标题、作者、标签关键词搜索
- **互动按钮**：点赞、评论、收藏、分享
- **键盘快捷键**：空格播放/暂停、↑↓切换视频、M静音、F全屏
- **响应式设计**：适配桌面端和移动端
- **视频网格**：底部卡片式内容发现

## 技术栈

- HTML5 + CSS3 + Vanilla JavaScript
- Google Material Icons
- 无外部框架依赖，零构建步骤

## 目录结构

```
short-video-site/
├── index.html          # 主页面
├── css/
│   └── style.css       # 样式文件
├── js/
│   └── app.js          # 交互逻辑
├── assets/
│   ├── logo.jpg        # 网站 Logo（Seedream 生成）
│   └── videos/         # 视频素材（Seedance 生成）
│       ├── nature.mp4  # 自然风光
│       ├── food.mp4    # 美食推荐
│       └── beauty.mp4  # 美妆护肤
└── docs/
    ├── retrospective.md    # 开发复盘报告
    └── prompt-template.md  # 可复用提示词模板
```

## 快速开始

直接在浏览器中打开 `index.html` 即可，或使用本地服务器：

```bash
# Python
python -m http.server 8080

# Node.js
npx serve .
```

## 素材来源

- Logo：Seedream 生图模型生成
- 视频素材：Seedance 生视频模型生成
  - 自然风光：金色山峦航拍
  - 美食推荐：手工和牛汉堡
  - 美妆护肤：晨间护肤流程

## 键盘快捷键

| 按键 | 功能 |
|------|------|
| 空格 | 播放/暂停 |
| ↑ | 上一个视频 |
| ↓ | 下一个视频 |
| M | 静音/取消静音 |
| F | 全屏/退出全屏 |

## License

MIT
