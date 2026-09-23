# 陈墨设计师作品集（designer-portfolio）

> 纯 HTML/CSS/JS 实现的独立产品设计师作品集网站示例，零构建、零框架依赖，可直接在浏览器打开运行。

## 项目概述

本项目是一个虚构设计师「陈墨」的个人作品集网站 Demo，展示极简设计语言下的个人品牌呈现方式：首页以作品卡片流组织四个设计案例，每个案例配有独立详情页，并包含工作/教育经历时间线与联系方式区块。

## 功能特性

- **单页式首页**：Hero 自我介绍、精选作品网格、关于我（工作/教育双时间线）、联系方式四大区块
- **四个项目详情页**：独立 HTML 页面，含项目元信息（年份/角色/交付物）、大图展示与返回导航
- **滚动动效**：基于 GSAP + ScrollTrigger 的入场动画与滚动触发效果
- **固定返回按钮**：详情页滚动后显现的快捷返回入口
- **响应式导航**：桌面端水平菜单 + 移动端汉堡按钮全屏菜单
- **平滑滚动与导航高亮**：滚动位置与当前区块联动（IntersectionObserver 风格的 scroll-spy）
- **图片懒加载**：作品缩略图与详情大图均使用 `loading="lazy"`
- **设计变量体系**：CSS 自定义属性统一管理配色、字号、间距，主题色为克制的鼠尾草绿（`#a8b5a0`）

## 技术栈

- HTML5 + CSS3（CSS 自定义属性、响应式媒体查询）+ Vanilla JavaScript（IIFE + strict mode）
- [GSAP 3.12.5](https://gsap.com/) / ScrollTrigger（经 cdnjs CDN 引入，`defer` 加载）
- [Inter](https://fonts.google.com/specimen/Inter) + [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)（Google Fonts CDN）
- 无包管理器、无构建步骤，所有内部引用均为相对路径

## 目录结构

```
designer-portfolio/
├── index.html              # 首页（Hero / 作品 / 关于 / 联系）
├── style.css               # 全局样式（约 19KB，含设计变量与响应式规则）
├── script.js               # 交互逻辑（导航、平滑滚动、GSAP 动效、懒加载）
├── projects/               # 项目详情页（4 个，均使用 ../ 相对引用）
│   ├── project-1.html      # 绿意生活（移动应用 / 可持续生活）
│   ├── project-2.html      # 云书阅读（Web 平台 / 数字阅读）
│   ├── project-3.html      # 城市骑行（品牌设计 / 网站设计）
│   └── project-4.html      # 艺廊空间（网站设计 / 当代艺术）
└── assets/                 # 演示图片（每个项目 1 张缩略图 + 1 张详情大图）
    ├── project-1-thumb.jpg / project-1-detail.jpg
    ├── project-2-thumb.jpg / project-2-detail.jpg
    ├── project-3-thumb.jpg / project-3-detail.jpg
    └── project-4-thumb.jpg / project-4-detail.jpg
```

## 快速开始

直接双击 `index.html` 在浏览器中打开即可；如需避免本地文件协议限制，可启动任意静态服务器：

```bash
# Python
python -m http.server 8080

# Node.js
npx serve .
```

然后访问 `http://localhost:8080`。

## 页面内容

| 页面 | 路径 | 说明 |
|------|------|------|
| 首页 | `index.html` | 作品卡片流 + 经历时间线 + 联系方式 |
| 绿意生活 | `projects/project-1.html` | 低碳习惯养成移动应用 |
| 云书阅读 | `projects/project-2.html` | 沉浸式数字阅读 Web 平台 |
| 城市骑行 | `projects/project-3.html` | 城市骑行社群品牌识别与官网 |
| 艺廊空间 | `projects/project-4.html` | 当代艺术画廊线上展览空间 |

## 素材说明

- 页面文案、人物身份（陈墨）、社交链接均为占位演示内容，不对应真实人物或机构。
- `assets/` 内 8 张图片为随项目提供的演示素材，来源未在项目中记录；如需公开发布请替换为自行拥有版权的图片。
- 字体与 GSAP 均通过公共 CDN 加载，离线环境下页面可打开但字体与动效会回退。

## 适用场景

- 作为极简风格作品集 / 个人品牌页的前端实现参考
- 作为纯静态多页面站点（首页 + 子页面相对路径组织）的结构范例
- 作为 GSAP ScrollTrigger 滚动动效的轻量接入示例
