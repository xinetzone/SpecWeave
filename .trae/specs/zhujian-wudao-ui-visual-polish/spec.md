# 竹简悟道 UI 视觉精修 Spec

## Why
第一性原理布局优化已完成（Header 精简、空状态/活动状态二分、输入框 sticky、Google Fonts 本地化），但视觉设计质量仍未达到预期。头部导航栏的色彩搭配、字体样式、交互反馈和视觉层次感不足，整体专业度和现代 UI/UX 标准存在差距。需要在保持布局结构不变的前提下，对视觉层进行系统性精修。

## What Changes
- 重构 Header 视觉设计：Logo 印章化、标题排版优化、按钮样式统一
- 统一色彩体系：建立朱砂红/墨色/宣纸色的三级色彩使用规范，明确各场景用色
- 优化字体层级：标题用书法体、正文用宋体、辅助文字用轻字重，建立清晰的字号阶梯
- 增强交互反馈：hover/active/focus 三态视觉反馈统一，触觉反馈保留
- 提升视觉层次：通过留白、分隔线、阴影、透明度建立内容层级
- 美化 ModelSelector 和 LaidBackToggle 组件视觉风格，使其与水墨主题协调
- 优化空状态视觉：引言排版、示例提问按钮的视觉吸引力

## Impact
- Affected specs: 无（新建独立 spec）
- Affected code:
  - `d:\AI\.chaos\zhujianwudao\src\routes\index.tsx` — Header 和空状态视觉调整
  - `d:\AI\.chaos\zhujianwudao\src\styles\index.css` — 色彩变量和基础样式
  - `d:\AI\.chaos\zhujianwudao\src\styles\components.css` — 组件样式精修
  - `d:\AI\.chaos\zhujianwudao\src\styles\typography.css` — 字体层级规范
  - `d:\AI\.chaos\zhujianwudao\src\components\LaidBackToggle.tsx` — 按钮视觉优化
  - `d:\AI\.chaos\zhujianwudao\src\components\ModelSelector.tsx` — 选择器视觉优化
  - `d:\AI\.chaos\zhujianwudao\src\components\BambooSlip.tsx` — 竹简卡片视觉优化

## ADDED Requirements

### Requirement: Header 视觉设计规范
系统 SHALL 对 Header 进行视觉精修，使其符合水墨禅意主题的同时达到现代 UI/UX 专业标准。

#### Scenario: Logo 印章化
- **WHEN** 用户查看 Header 左侧 Logo
- **THEN** Logo 呈现为朱砂红印章风格（方形圆角、印章红背景、白色书法字"悟"），带有微妙阴影和边框，尺寸为 36x36px（桌面）/ 32x32px（移动）

#### Scenario: 标题排版层级
- **WHEN** 用户查看 Header 标题区域
- **THEN** "竹简悟道"使用书法字体（STKaiti/KaiTi），字号 20px，字重 400，字间距 0.08em；副标题"慢下来，把问题想透"使用宋体，字号 12px，字重 300，颜色为 ink-light，opacity 0.7

#### Scenario: 按钮视觉统一
- **WHEN** 用户查看 Header 右侧操作按钮（LaidBackToggle、ModelSelector、Export、Clear）
- **THEN** 所有按钮遵循统一的视觉规范：高度 36px、圆角 6px、内边距 8px 12px、hover 时背景色为 seal-red/8%、active 时 scale 0.96、过渡时间 200ms

### Requirement: 色彩体系三级规范
系统 SHALL 建立朱砂红/墨色/宣纸色三级色彩使用规范，确保所有界面元素色彩协调。

#### Scenario: 主色（朱砂红）使用场景
- **WHEN** 界面需要强调关键操作或品牌识别
- **THEN** 使用 `--seal-red: #a83f35`，适用场景：Logo 印章、发送按钮、激活态指示器、链接 hover 色

#### Scenario: 辅色（墨色层次）使用场景
- **WHEN** 界面需要展示文字内容或结构元素
- **THEN** 使用墨色四级层次：`--ink-heavy: #141414`（标题）、`--ink-medium: #2d2d2d`（正文）、`--ink-light: #555555`（辅助文字）、`--ink-wash: #888888`（占位/提示）

#### Scenario: 背景色（宣纸色）使用场景
- **WHEN** 界面需要背景或卡片底色
- **THEN** 使用宣纸色系：`--xuan-paper: #f8f5f0`（主背景）、`--xuan-paper-dark: #f3efe8`（卡片/悬停）、`--background: oklch(0.97 0.01 85)`（CSS 变量层）

### Requirement: 交互反馈三态统一
系统 SHALL 为所有可交互元素提供统一的 hover/active/focus 三态视觉反馈。

#### Scenario: Hover 态
- **WHEN** 用户鼠标悬停在按钮/链接上
- **THEN** 元素背景色变为 `seal-red/8%`，文字色加深，过渡时间 200ms ease-out

#### Scenario: Active 态
- **WHEN** 用户点击按钮/链接
- **THEN** 元素 `transform: scale(0.96)`，背景色变为 `seal-red/15%`，过渡时间 100ms

#### Scenario: Focus 态
- **WHEN** 用户通过键盘 Tab 聚焦到按钮/链接
- **THEN** 元素显示 `2px solid seal-red/40%` 的 focus ring，`border-radius` 与元素一致

### Requirement: 空状态视觉增强
系统 SHALL 优化空状态的视觉呈现，使首次访问用户感受到品牌调性和引导性。

#### Scenario: 引言排版美化
- **WHEN** 用户首次访问页面看到空状态
- **THEN** 道德经引言使用书法字体，字号 18px，字重 400，颜色 ink-medium，斜体；引言上下有 32px 留白；引言下方分隔线为 40px 宽的渐变墨色线

#### Scenario: 示例提问按钮视觉
- **WHEN** 用户查看空状态的示例提问按钮
- **THEN** 按钮使用宣纸色背景 + 墨色边框，hover 时边框变为朱砂红/40%、文字变为朱砂红、背景微泛朱砂红/4%；按钮间距 8px，圆角 20px（胶囊形）

## MODIFIED Requirements

### Requirement: LaidBackToggle 视觉优化
现有 LaidBackToggle 组件的视觉风格与水墨主题不协调（使用了 amber/orange 渐变），需调整为与整体色彩体系一致。

#### Scenario: 正经模式态
- **WHEN** LaidBackToggle 处于正经模式（isLaidBack=false）
- **THEN** 按钮样式：宣纸色背景 + 墨色细边框 + 墨色文字 + 卷轴图标；hover 时边框变为朱砂红/40%

#### Scenario: 摆烂模式态
- **WHEN** LaidBackToggle 处于摆烂模式（isLaidBack=true）
- **THEN** 按钮样式：朱砂红/8% 背景 + 朱砂红边框 + 朱砂红文字 + 咖啡图标；不再使用 amber/orange 渐变

### Requirement: ModelSelector 视觉优化
现有 ModelSelector 的下拉选择器视觉风格需与 Header 整体协调。

#### Scenario: 选择器默认态
- **WHEN** ModelSelector 显示在 Header 中
- **THEN** 选择器使用宣纸色背景 + 墨色细边框，高度 36px，圆角 6px，内含模型名称和下拉箭头

#### Scenario: 选择器展开态
- **WHEN** 用户点击 ModelSelector 展开下拉列表
- **THEN** 下拉列表使用宣纸色背景 + 阴影，选项 hover 时背景为朱砂红/8%，选中项有朱砂红左边框指示
