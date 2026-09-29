# 移动端 Design Token 工作台

由 Ardot 画布《移动端 Design Token 体系》设计稿生成的可运行应用，严格还原设计稿的布局结构、配色、圆角、间距与字体排印。

## 运行

零构建、零依赖（仅字体走 CDN，离线自动回退系统字体）：

```bash
# 方式一：直接打开
start index.html          # Windows

# 方式二：本地静态服务（推荐，便于复制 / 导出能力完整生效）
python -m http.server 5173
# 访问 http://127.0.0.1:5173
```

## 目录结构

```
mobile-design-tokens/
├── index.html            # 页面骨架 + 05 组件预览（双份同结构 Markup）+ 06 字体排印
├── styles/
│   ├── tokens.css        # Token 唯一真源：Primitives / Semantic / Radius / Shadow / Typography
│   └── app.css           # 组件样式，只引用语义变量
└── scripts/
    ├── tokens.js         # Token 数据源（与画布变量一一对应）
    └── app.js            # 渲染 + 换肤 + 搜索 + 复制 + 导出
```

## Token 架构

```
Primitives（静态色板，双 Mode 同值）
      ↓ 只被语义层引用
Semantic（intent 命名，Light / Dark 两套取值）
      ↓ 唯一允许被组件引用
组件（Button / Card / List / Progress …）
```

- 组件层**只允许**引用 `--bg-*`、`--text-*`、`--border-*`、`--accent-*`、`--radius-*`、`--shadow-*`、`--font-*`、`--text-<size>`、`--weight-*`、`--leading-*`、`--type-*`；
- 明暗切换 = 切换变量集合的 Mode，**不改任何组件属性**；Typography 为单 Value 模式、双主题同值，不随换肤变化。

## 换肤作用域

| 作用域 | 写法 | 效果 |
|---|---|---|
| 全局浅色 | `<html class="theme-root">` | Light Mode |
| 全局深色 | `<html class="theme-dark">` | Dark Mode |
| 跟随系统 | `<html class="theme-auto">` | 读 `prefers-color-scheme` |
| 局部强制 | 容器加 `.theme-light` / `.theme-dark` | 页面内的 Light / Dark 对照面板 |

自定义属性在元素自身上的声明优先于继承值，因此同一页面可以同时存在强制浅色面板与强制深色面板——这正是设计稿 02 / 04 / 05 区块的对照演示方式。

## 应用能力

- **主题切换**：浅色 / 深色 / 跟随系统，选择写入 `localStorage`
- **变量搜索**：实时过滤色阶、语义变量、圆角、阴影、字体排印，导航自动收敛
- **点击复制**：色值 / CSS 变量名一键复制（带 `file://` 兜底）
- **导出**：一键导出 `tokens.css`、`tokens.json`，供下游项目接入

## 与设计稿的对应关系

| 设计稿区块 | 页面节点 |
|---|---|
| 页头 | `.page-head`（gap 10，标题 38/48，副标题 15/26） |
| 01 原始色阶 Primitives | `#primitives-groups`（chip 76px 高、radius 10、stroke `#E4E7EC`、10/14px 标注） |
| 02 语义色 Semantic Colors | `#semantic-light` / `#semantic-dark`（300px 单元 + 16px gap，色块 56px / radius-md） |
| 03 圆角 Radius | `#radius-grid`（示例面 96px，名称 Inter SemiBold 13，用法说明 Noto Sans SC 12） |
| 04 阴影 Elevation | `#shadow-light` / `#shadow-dark`（演示台 padding 28、卡片 120px、radius-md） |
| 05 组件预览 | `.preview-row`（双份完全一致 Markup，仅外层 Mode 作用域不同） |
| 06 字体排印 Typography | `#type-fonts`（字体族卡片）+ `#type-scale`（语义角色字样阶梯） |

> Dark 模式阴影统一换为纯黑 `#000000 @ 30%–60%`，避免深色表面上阴影「消失」——这是设计稿里的关键决策，已在 `tokens.css` 中保留。
