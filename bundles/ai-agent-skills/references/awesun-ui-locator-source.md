---
type: Reference
title: awesun-ui-locator 源码
description: 截图 UI 元素定位器源码登记，含 SKILL.md 五步工作流、coordinate_utils.py 坐标计算与 ui_patterns.md 视觉参考
tags: [agent-skills, awesun, ui-locator, source, reference, computer-vision]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: pending, at: pending }
status: draft
stale_after: 2027-08-23
sources:
  - id: facts-awesun-ui-locator
    resource: "/references/facts-awesun-ui-locator.md"
    title: awesun-ui-locator 事实清单
---

# awesun-ui-locator 源码

## 仓库信息

| 属性 | 值 |
|------|-----|
| 项目名 | Awesun UI Locator - 截图 UI 元素定位器 |
| 定位 | 分析桌面截图并精确定位 UI 元素，返回标准化归一化坐标 |
| 源码路径 | `d:\AI\.chaos\libs\awesun-ui-locator\` |
| 技能名称 | `screenshot-ui-locator` |
| Python 要求 | 3.7+（坐标计算工具） |
| 客户端要求 | 向日葵客户端 16.3.2+ |
| 支持 AI 编辑器 | Claude Code、Open Code、OpenClaw |

## 目录结构

```text
awesun-ui-locator/
├── SKILL.md                      # 技能主入口（五步工作流）
├── README.md                     # 项目说明
├── scripts/
│   └── coordinate_utils.py       # 坐标计算工具（3 个函数）
└── references/
    └── ui_patterns.md            # UI 元素视觉特征参考
```

## SKILL.md 结构

### frontmatter

```yaml
---
name: screenshot-ui-locator
description: [引导 AI 视觉模型识别桌面截图中的 UI 元素位置并返回归一化坐标]
---
```

### 五步工作流

1. **读取图片**：使用 read 工具读取用户提供的图片文件，自动转换为 base64 格式展示给视觉模型。支持 PNG（.png）、JPEG/JPG（.jpg、.jpeg）及其他常见格式。
2. **理解用户意图**：解析用户想要定位的 UI 元素类型（按钮、输入框、图标、文本元素等）。
3. **视觉分析**：整体观察布局 → 识别 UI 组件 → 匹配目标元素 → 精确定位像素位置 → 计算归一化坐标。
4. **计算归一化坐标**：
   - 公式：`x_norm = x_pixel / image_width`，`y_norm = y_pixel / image_height`
   - 坐标系：左上角为原点 (0.0, 0.0)，右下角为 (1.0, 1.0)
5. **返回结果**：JSON 格式，包含 found、element、coordinates、confidence、description。

### 返回格式

```json
{
  "found": true,
  "element": "按钮名称",
  "coordinates": { "x": 0.5, "y": 0.5 },
  "confidence": "high",
  "description": "对元素位置和特征的描述"
}
```

confidence 取值：`high`、`medium`、`low`。

## scripts/coordinate_utils.py

坐标计算工具，仅使用 typing.Tuple 类型注解，无外部依赖。

### 函数清单

| 函数 | 参数 | 返回值 | 功能 |
|------|------|--------|------|
| `calculate_coordinates(pixel_x, pixel_y, image_width, image_height)` | 四个 int | `Tuple[float, float]` | 计算归一化坐标，保留 6 位小数 |
| `validate_coordinates(x, y)` | 两个 float | `bool` | 验证坐标在 [0.0, 1.0] 范围内 |
| `format_coordinates(x, y)` | 两个 float | `dict` | 格式化为 `{"coordinates": {"x": x, "y": y}}` |

## references/ui_patterns.md

UI 元素识别参考文档，提供常见 UI 元素特征对照表和定位策略。

### 按钮分类（5 类）

| 类型 | 视觉特征 |
|------|---------|
| 主要按钮 | 实心填充、高对比度、位于表单底部或显眼位置 |
| 次要按钮 | 描边样式、较低视觉权重 |
| 文字按钮 | 无边框无背景、仅文字 |
| 图标按钮 | 仅图标无文字（工具栏常见） |
| 幽灵按钮 | 透明背景、悬停时显示边框 |

### 输入框分类（5 类）

单行文本框、多行文本框、搜索框、密码框、下拉选择框。

### 图标对照表（12 种）

汉堡菜单（☰）、放大镜（🔍）、齿轮（⚙️）、人像（👤）、房子（🏠）、心形（❤️）、铃铛（🔔）、购物车（🛒）、分享（↗️）、垃圾桶（🗑️）、关闭（✕）、箭头（→）。

### 导航元素

Tab 标签、面包屑、侧边栏、分页器、步骤条。

### 反馈元素

提示消息、加载动画、徽章/角标、工具提示。

### 定位策略

1. **先整体后局部**：理解页面结构 → 缩小搜索范围 → 精确定位
2. **多特征匹配**：位置、颜色、形状、文字、图标结合判断

## 渐进式披露三层结构

| 层级 | 文件 | 内容 | Token 消耗 |
|------|------|------|-----------|
| 第一层 | SKILL.md | 完整工作流程和坐标计算公式 | 激活时加载 |
| 第二层 | scripts/coordinate_utils.py | 可执行的坐标计算和验证函数 | AI 按需调用 |
| 第三层 | references/ui_patterns.md | 详细的 UI 元素视觉特征参考 | 需深度识别时读取 |
