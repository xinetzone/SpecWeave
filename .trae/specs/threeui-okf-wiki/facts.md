# Facts：ThreeUI 爆火

> 主信源：微信公众号"前端开发爱好者"，2026-08-25 08:33 发布
> URL：https://mp.weixin.qq.com/s/Gtmstp6HyXSqdK5h-3GcNQ
> P0核验：7项中4✅ 3⚠️ 0❌

## 元信息

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-001 | 标题《ThreeUI 爆火！一个基于 Three.js 的160+ 3D 组件全开源！》，"前端开发爱好者"，2026-08-25 08:33 | 元信息 | — |

## 项目概述（F-002~F-008）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-002 | ThreeUI由Meng To开源，是专门给Three.js/WebGL做的视觉组件库 | 产品 | ✅ |
| F-003 | 官网threeui.com，GitHub github.com/MengTo/threeui，MIT许可证，基于React+Three.js | 产品 | ✅ |
| F-004 | 项目上线后突破1000+ GitHub Star（博文发布时）；核验时已达4.1k | 数据 | ✅ 博文数据准确 |
| F-005 | npm包名@designcodeio/threeui | 技术 | ✅ |
| F-006 | Meng To是Design+Code（designcode.io）创始人，有20余年设计与编程经验，著有Design+Code书籍（35000读者） | 人物 | ✅ |
| F-007 | 使用方式：找到效果→在线预览→调参数→查看源码→拿到项目里改，类似shadcn/ui但组件升级为Three.js+WebGL | 用法 | ✅ |
| F-008 | Community版本164个可浏览效果，源码和资源一起开放，非黑盒npm包 | 开源 | ✅ |

## 组件数据（F-009~F-010）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-009 | Community版本包含：50个父组件、111个Routes、141个免费Variant、23个独立组件=164个可浏览效果 | 数据 | ✅ README逐字确认 |
| F-010 | 官方划分10个分类：Landing Pages/Hero/Three.js/Motion Design/Sections/Backgrounds/Buttons/Text Animation/UI Elements/CSS | 分类 | ⚠️ 官网当前9个分类，"Sections"为空/不存在 |

## 六大核心组件类型（F-011~F-022）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-011 | Landing Page/Hero：完整页面含布局/滚动/交互/Three.js场景；代表Kage（日式寺庙夜景/灯笼/樱花/3D场景/鼠标键盘滚动导航）、Complete Shelf、Bestsellers Book Showcase | 组件 | ✅ |
| F-012 | Three.js 3D场景：Temple Night/Japanese Tower/Bookshelf/Globe/Orbital Sphere/Landscape等；Camera/Light/Material/Animation已封装 | 组件 | ✅ |
| F-013 | 适用场景：AI官网、SaaS、作品集、Web3、开发者工具的Hero区域 | 场景 | ✅ |
| F-014 | Shader/动态背景：Liquid Form/Dot Matrix/Warp Field/Nebula Background/Particle Network/Flux Vortex等流体/粒子/星云/点阵/空间扭曲效果 | 组件 | ✅ |
| F-015 | Buttons：Liquid Metal Button/Plasma Button/Thinking Button/Glassmorphism CTA/Gradient Beam CTA等，流体/金属/玻璃/光效/渐变/粒子远超传统CSS Hover | 组件 | ✅ |
| F-016 | Text Animation：Typography Vortex/Morphing Glyph Cloud/Particle Wordmark/Neon Typography；文字粒子化/变形/沿路径运动，适合Logo/Hero标题/品牌展示 | 组件 | ✅ |
| F-017 | 以前文字动画需自己折腾GSAP+Canvas+Shader，现在可直接拿现成实现 | 对比 | 📝 |
| F-018 | UI Elements：Genie Dock/Animated Top Dock/Gallery/Uplink Loader/Performance Gauges/Skeuomorphic Toggle等Dock/Loading/Gallery/Toggle/仪表盘 | 组件 | ✅ |
| F-019 | 整体覆盖完整页面/3D场景/背景/按钮/文字/UI元素一整套视觉开发场景 | 总结 | 📝 |
| F-020 | Kage日式寺庙主题包含夜景/灯笼/樱花和3D场景，保留鼠标/键盘/滚动和导航交互 | 组件 | ✅ |
| F-021 | 很多效果直接放首屏背景就能明显提升页面质感 | 评价 | 📝 |
| F-022 | 官网显示总计373 components（含Pro组件） | 数据 | ✅ |

## AI Coding集成（F-023~F-029）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-023 | ThreeUI明显方向之一是AI Coding，支持将源码或Prompt直接给Codex/Claude Code/Cursor等AI Agent | AI集成 | ✅ |
| F-024 | 示例指令："整体改成深蓝色科技风"/"减少粒子数量"/"把灯光调柔和一点"/"动画速度降低30%"，AI基于现有Three.js代码修改 | AI集成 | ✅ |
| F-025 | 解决痛点：看得懂效果但改不动——Three.js的Camera/Material/Shader参数容易劝退 | 痛点 | 📝 |
| F-026 | 新流程：先找接近目标的效果→再让AI改 | 工作流 | 📝 |
| F-027 | 组件自带配套Skills（agent skills），可直接放入Claude Code/Cursor/Codex/OpenCode/Kiro等agent使用 | AI集成 | ✅ |

## MCP支持（F-030~F-034）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-030 | ThreeUI提供自己的MCP，让支持MCP的AI Coding Client直接访问ThreeUI Catalog | MCP | ✅ |
| F-031 | MCP提供4个能力：search_catalog搜索组件和模板、get_catalog_item获取组件信息/资源/使用方式、get_item_source读取完整源码、get_item_prompt获取组件对应实现Prompt | MCP | ⚠️ MCP Pro确认但4个工具名无法从公开来源验证 |
| F-032 | MCP属于Pro能力 | MCP | ✅ 定价页确认 |
| F-033 | MCP工作流：需求→AI Agent→ThreeUI→组件源码→页面 | MCP | 📝 |
| F-034 | Pro含50+额外组件、MCP和skills | MCP | ✅ |

## 行业趋势（F-035~F-040）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-035 | Canvas UI此前火了，把WebGL Shader带进真实DOM，让普通网页做出夸张视觉效果（DavidHDev创建，2026-07-23发布） | 行业 | ⚠️ 项目存在且性质吻合，博文未误归属 |
| F-036 | 前端组件库已开始卷到WebGL层 | 趋势 | 📝 |
| F-037 | ThreeUI从按钮/文字/背景到完整3D场景和Landing Page，越来越多需手搓的视觉效果变成可直接用的组件 | 趋势 | 📝 |
| F-038 | 加AI Agent后流程：找效果→拿源码→描述需求→AI修改 | 趋势 | 📝 |
| F-039 | Three.js门槛正在快速下降 | 趋势 | 📝 |
| F-040 | 以后想做看起来很贵的3D官网可能没以前难 | 展望 | 📝 |

## 核验补充事实（F-041~F-043）

| 编号 | 事实 | 分类 | 来源 |
|------|------|------|------|
| F-041 | 官网当前9个分类（非10个）：Landing Pages/Hero/Three.js/Backgrounds/Buttons/Text Animation/UI Elements/CSS/Motion Design；Sections分类访问返回"No components match" | 勘误 | threeui.com/browse |
| F-042 | MCP 4个工具名（search_catalog/get_catalog_item/get_item_source/get_item_prompt）无法从公开网页验证，可能仅在Pro认证后的MCP配置文档中披露 | 勘误 | threeui.com/pricing |
| F-043 | Canvas UI由DavidHDev（react-bits维护者）创建，2026-07-23发布，核心为html-in-canvas API，支持React/Vue/Svelte/vanilla TS，发布时24组件现33个 | 补充 | GitHub/cssscript |

## 事实统计

| 类别 | 数量 |
|------|------|
| 元信息 | 1 |
| 项目概述 | 7 |
| 组件数据 | 2 |
| 六大组件类型 | 12 |
| AI Coding集成 | 5 |
| MCP支持 | 5 |
| 行业趋势 | 6 |
| 核验补充 | 3 |
| **合计** | **41** |
