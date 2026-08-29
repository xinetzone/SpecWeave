---
type: Concept
title: UI 定位器模式（坐标归一化、视觉定位）
description: awesun-ui-locator 的截图 UI 元素定位模式，五步视觉工作流、归一化坐标计算、坐标工具函数与 UI 元素视觉特征对照
tags: [agent-skills, ui-locator, computer-vision, coordinate, normalization, awesun]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: awesun-ui-locator-source
    resource: "/references/awesun-ui-locator-source.md"
    title: awesun-ui-locator 源码
---

# UI 定位器模式（坐标归一化、视觉定位）

awesun-ui-locator（技能名 `screenshot-ui-locator`）解决了一个 AI 自动化中的基础问题：**如何让 AI 通过视觉理解截图并精确定位 UI 元素，且定位结果可跨分辨率复用**。它通过"视觉模型识别 + 确定性坐标计算"的组合模式，将截图中的 UI 元素转化为归一化坐标，供远程控制工具（如 awesun-skill 的 desktop_click_mouse）使用。

## 问题背景

在远程桌面自动化中，AI 需要完成以下链路：

```text
截图 → 识别目标元素 → 获取坐标 → 执行点击/输入
```

挑战在于：
1. AI 的视觉模型可以识别元素，但输出的像素坐标依赖图片分辨率
2. 远程桌面的分辨率可能与截图分辨率不同
3. 不同时间截取的同界面可能有细微布局差异

归一化坐标解决了分辨率无关性问题：无论截图和远程桌面的分辨率如何，(0.5, 0.5) 始终表示屏幕中心。

## 五步工作流

SKILL.md 定义了严格的五步工作流：

### 步骤 1：读取图片

使用 read 工具读取用户提供的图片文件。AI 工具自动将图片转换为 base64 格式展示给视觉模型。支持的格式：
- PNG（`.png`）
- JPEG/JPG（`.jpg`、`.jpeg`）
- 其他常见图片格式

### 步骤 2：理解用户意图

解析用户想要定位的 UI 元素类型：
- 按钮（主要按钮、次要按钮、图标按钮等）
- 输入框（文本框、搜索框、密码框等）
- 图标（汉堡菜单、放大镜、齿轮等）
- 文本元素
- 导航组件（Tab、面包屑、侧边栏等）

### 步骤 3：视觉分析

视觉模型按"先整体后局部"的顺序分析：
1. **整体观察布局**：理解页面的整体结构和区域划分
2. **识别 UI 组件**：检测所有可见的交互元素
3. **匹配目标元素**：根据用户描述找到最匹配的元素
4. **精确定位像素位置**：确定元素的中心点或可点击点的像素坐标
5. **计算归一化坐标**：将像素坐标转换为 0.0-1.0 范围

### 步骤 4：计算归一化坐标

使用确定性公式：

```text
x_norm = x_pixel / image_width
y_norm = y_pixel / image_height
```

坐标系约定：
- **左上角**为原点 (0.0, 0.0)
- **右下角**为 (1.0, 1.0)
- X 轴向右增长，Y 轴向下增长
- 坐标值保留 6 位小数

### 步骤 5：返回结果

返回标准化 JSON 格式：

```json
{
  "found": true,
  "element": "提交按钮",
  "coordinates": { "x": 0.523, "y": 0.891 },
  "confidence": "high",
  "description": "蓝色主要按钮，位于表单底部右侧"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `found` | boolean | 是否找到目标元素 |
| `element` | string | 元素名称/标识 |
| `coordinates.x` | float | 归一化 X 坐标 [0.0, 1.0] |
| `coordinates.y` | float | 归一化 Y 坐标 [0.0, 1.0] |
| `confidence` | string | 置信度：high/medium/low |
| `description` | string | 元素位置和特征的文字描述 |

## coordinate_utils.py 坐标工具

`scripts/coordinate_utils.py` 是无外部依赖的坐标计算工具，仅使用 `typing.Tuple` 类型注解。它提供三个纯函数，视觉模型和 AI 可直接调用以验证和格式化坐标。

### calculate_coordinates

```python
def calculate_coordinates(
    pixel_x: int, pixel_y: int, image_width: int, image_height: int
) -> Tuple[float, float]:
```

将像素坐标转换为归一化坐标。

- **参数**：像素 X、像素 Y、图片宽度、图片高度（均为整数）
- **返回**：`(x_norm, y_norm)` 元组，每个值保留 6 位小数
- **公式**：`x = pixel_x / image_width`，`y = pixel_y / image_height`

### validate_coordinates

```python
def validate_coordinates(x: float, y: float) -> bool:
```

验证归一化坐标是否在有效范围内。

- **返回**：`0.0 <= x <= 1.0 and 0.0 <= y <= 1.0`
- **用途**：在执行点击操作前验证坐标合法性，防止越界值

### format_coordinates

```python
def format_coordinates(x: float, y: float) -> dict:
```

将坐标格式化为标准化字典。

- **返回**：`{"coordinates": {"x": x, "y": y}}`
- **用途**：生成符合桌面操作工具参数格式的输出

## UI 元素视觉特征对照

`references/ui_patterns.md` 是第三层参考文档，提供常见 UI 元素的视觉特征和定位策略。AI 在视觉分析不确定时可读取此文档增强识别能力。

### 按钮分类（5 类）

| 类型 | 视觉特征 | 常见位置 |
|------|---------|---------|
| 主要按钮 | 实心填充、高对比色、粗体文字 | 表单底部、对话框右下角 |
| 次要按钮 | 描边样式、较低视觉权重 | 主要按钮旁 |
| 文字按钮 | 无边框无背景、仅文字 | 工具栏、内联操作 |
| 图标按钮 | 仅图标无文字 | 工具栏、卡片右上角 |
| 幽灵按钮 | 透明背景、悬停显示边框 | 英雄区、卡片叠加层 |

### 输入框分类（5 类）

- **单行文本框**：矩形边框、单行高度、有 placeholder
- **多行文本框**：可调整大小、多行高度
- **搜索框**：通常有放大镜图标前缀、圆角
- **密码框**：输入内容显示为圆点/星号
- **下拉选择框**：右侧有向下箭头、点击展开选项

### 常见图标对照（12 种）

| 图标 | 含义 | 常见位置 |
|------|------|---------|
| ☰ 汉堡菜单 | 主菜单/导航 | 页面左上角 |
| 🔍 放大镜 | 搜索 | 顶部导航栏 |
| ⚙️ 齿轮 | 设置 | 右上角/用户菜单 |
| 👤 人像 | 用户/账户 | 右上角 |
| 🏠 房子 | 首页 | 导航栏 |
| ❤️ 心形 | 收藏/喜欢 | 卡片/列表项 |
| 🔔 铃铛 | 通知 | 顶部栏 |
| 🛒 购物车 | 购物车 | 电商网站右上角 |
| ↗️ 分享 | 分享 | 内容页 |
| 🗑️ 垃圾桶 | 删除 | 列表项/管理界面 |
| ✕ 关闭 | 关闭/清除 | 模态框/标签页 |
| → 箭头 | 前进/下一步 | 引导流程 |

### 导航与反馈元素

- **导航**：Tab 标签（内容切换）、面包屑（层级路径）、侧边栏（功能导航）、分页器（页面导航）、步骤条（流程进度）
- **反馈**：提示消息（成功/警告/错误）、加载动画（旋转器/进度条）、徽章/角标（未读计数）、工具提示（悬停信息）

## 定位策略

### 先整体后局部

1. 理解页面整体结构（头部/内容区/侧边栏/底部）
2. 将搜索范围缩小到目标区域
3. 在区域内精确定位元素

这种策略避免了在全图中盲目搜索，提高了识别准确率和速度。

### 多特征匹配

结合多个特征判断元素身份：
- **位置**：元素在页面中的相对位置（如"表单底部右侧"）
- **颜色**：品牌色、语义色（红色=危险/删除，绿色=成功/确认）
- **形状**：矩形按钮、圆形图标、输入框样式
- **文字**：按钮文字、标签文字、placeholder
- **图标**：标准图标及其含义

当多个元素特征冲突时，优先使用文字标签和位置信息。

## 与远程控制的协作模式

ui-locator 通常与 awesun-skill（远程控制）配合使用：

```text
1. control_screenshot 获取远程桌面截图
2. screenshot-ui-locator 分析截图，返回归一化坐标
3. validate_coordinates 验证坐标范围
4. desktop_click_mouse 使用坐标执行点击
5. 再次截图验证操作结果
```

归一化坐标是这一协作的关键：截图分辨率和远程桌面分辨率可能不同（截图可能是压缩后的图片），但归一化坐标在两者间保持一致。

## 设计启示

1. **视觉+确定性混合**：让 LLM/视觉模型做擅长的事（模式识别），让确定性代码做可靠的事（数值计算和验证）。
2. **分辨率无关性**：自动化系统的坐标应使用归一化值，像素坐标仅作为中间计算值。
3. **结构化输出**：JSON 格式的返回结果包含置信度和描述，便于 AI 判断是否需要重新分析或人工确认。
4. **参考知识分层**：SKILL.md 包含核心工作流，references/ 包含详细的 UI 模式参考，按需加载。

## 相关概念

- [Awesun 远程控制 Skill 实战](/concepts/06-awesun-remote-control.md)
- [SKILL.md 标准与渐进式披露](/concepts/01-skill-md-standard.md)
- [Skill 脚本工具模式](/concepts/10-skill-tooling-scripts.md)
