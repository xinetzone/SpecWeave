# 竹简悟道参考图驱动布局重构 Spec

## Why
当前首页虽然已经完成一轮视觉精修，但整体布局结构、组件排布密度、操作层级和主次关系与最新参考设计图仍存在明显差距。需要在不改动业务功能的前提下，按照参考图重组首页的视觉布局，并补齐桌面端、平板端、移动端的响应式适配与跨浏览器一致性验证。

## What Changes
- 以 `d:\AI\.temp\微信图片_20260714114536_380_1561.png` 为对齐基准，重构首页 Header、主内容区、输入区与侧边功能入口的布局关系
- 调整首页核心组件的排布方式、留白比例、对齐规则、层级顺序和交互位置逻辑
- 优化桌面端、平板端、移动端三档响应式断点下的布局表现，确保关键操作始终可见且不发生遮挡或挤压
- 保留现有功能组件和业务交互能力，仅改造布局容器、样式组织与组件在页面中的相对位置
- 增补跨浏览器验证方案，覆盖 Chromium、Edge、Firefox 与 WebKit 渲染一致性检查
- 交付布局调整说明文档，记录修改文件、核心调整点、断点适配策略与验证结果

## Impact
- Affected specs: `zhujian-wudao-ui-visual-polish`（其视觉精修成果作为本次布局重构的基础输入）
- Affected code:
  - `d:\AI\.chaos\zhujianwudao\src\routes\index.tsx` - 首页整体布局容器与区块层级重排
  - `d:\AI\.chaos\zhujianwudao\src\components\ContemplationInput.tsx` - 输入区在新布局中的尺寸与对齐适配
  - `d:\AI\.chaos\zhujianwudao\src\components\BambooSlip.tsx` - 对话卡片在新内容区中的间距与容器适配
  - `d:\AI\.chaos\zhujianwudao\src\components\LaidBackToggle.tsx` - Header 操作区中的位置逻辑适配
  - `d:\AI\.chaos\zhujianwudao\src\components\ModelSelector.tsx` - Header 操作区中的位置逻辑适配
  - `d:\AI\.chaos\zhujianwudao\src\components\A2ASidebar.tsx` - 与首页主内容区的横向关系、显隐和间距联动校准
  - `d:\AI\.chaos\zhujianwudao\src\styles\index.css` - 全局布局变量、断点和基础容器规则
  - `d:\AI\.chaos\zhujianwudao\src\styles\components.css` - 首页相关组件的布局样式与状态样式
  - `d:\AI\.chaos\zhujianwudao\src\styles\mobile.css` - 移动端与平板端适配规则
  - `d:\AI\.chaos\zhujianwudao\e2e\` - 跨浏览器布局验证用例或快照检查
  - `d:\AI\.chaos\zhujianwudao\outputs\reviews\` - 布局调整说明文档输出目录

## ADDED Requirements
### Requirement: 参考图对齐的首页布局重构
系统 SHALL 以参考设计图为基准，重构首页视觉布局，使品牌区、操作区、内容区和输入区的空间分配、对齐关系和视觉重心与参考图保持一致。

#### Scenario: Header 结构对齐
- **WHEN** 用户进入首页首屏
- **THEN** Header 须形成清晰的三段式信息关系：品牌识别区、核心操作区、状态/历史入口区；各区之间具有明确的间距层级，避免现有元素过于分散或权重不均

#### Scenario: 主内容区聚焦
- **WHEN** 页面处于空状态或首次访问状态
- **THEN** 欢迎消息卡片、引导文案与输入区域须围绕单一主交互焦点组织，形成“信息展示在上、输入行动在下”的稳定阅读路径

#### Scenario: 活动状态布局延续
- **WHEN** 用户进入连续对话状态
- **THEN** 消息流、统计卡片、今日领悟与输入区须保持统一对齐基线，避免不同卡片宽度、边距或粘性行为破坏阅读节奏

### Requirement: 组件排布与层级关系重组
系统 SHALL 重新定义首页关键组件的排布方式、间距比例和层级关系，但不得删减或替换原有功能组件。

#### Scenario: 核心操作重新分组
- **WHEN** 用户查看 Header 右侧操作区
- **THEN** `LaidBackToggle`、`ModelSelector`、导出按钮、清空按钮须按“主要操作优先、次要操作收束”的原则重新分组，避免当前操作密度失衡

#### Scenario: 内容卡片与输入区关系重组
- **WHEN** 用户滚动浏览对话内容
- **THEN** 对话卡片容器与底部输入容器须建立清晰的上下分层关系，输入区在桌面端表现为稳定底部锚点，在小屏设备上不遮挡最近一条消息

#### Scenario: 侧边功能入口关系校准
- **WHEN** 用户同时使用首页主内容区与侧边功能入口
- **THEN** 侧边区域的展开、折叠或浮层形态不得压缩首页核心阅读宽度到不可用范围，且页面视觉重心仍保持在主对话区

### Requirement: 三端响应式布局适配
系统 SHALL 在桌面端、平板端和移动端提供连续一致的布局适配，确保组件可读性、可点击性和视觉层级不退化。

#### Scenario: 桌面端布局
- **WHEN** 视口宽度大于等于 1024px
- **THEN** 首页须优先保持参考图中的横向结构关系，Header 操作区与主内容区拥有稳定的左右留白和最大宽度控制

#### Scenario: 平板端布局
- **WHEN** 视口宽度位于 768px 至 1023px
- **THEN** Header 与主内容区须适度收紧水平间距，保留核心操作可见性，避免按钮换行后破坏层级顺序

#### Scenario: 移动端布局
- **WHEN** 视口宽度小于 768px
- **THEN** Header 须允许次级信息折叠或重排，输入区和消息区须优先保障单手操作，所有点击目标满足触控尺寸要求且不发生横向滚动

### Requirement: 功能完整性保护
系统 SHALL 在布局调整过程中保留原有功能组件、事件绑定、状态管理与业务行为，不得因布局改造引入功能回退。

#### Scenario: 布局改造不影响交互
- **WHEN** 用户执行提问、导出、清空、模式切换、模型切换、打开统计、打开今日领悟、打开深呼吸或造梦等操作
- **THEN** 所有交互结果与调整前保持一致，仅组件视觉位置、容器关系和交互入口排布发生变化

### Requirement: 跨浏览器一致性验证
系统 SHALL 对重构后的布局执行跨浏览器兼容性测试，并记录差异与处理结论。

#### Scenario: 主流浏览器验证通过
- **WHEN** 在 Chromium、Edge、Firefox 与 WebKit 环境中加载首页
- **THEN** Header、主内容区、输入区、侧边入口、卡片边距和粘性区域的显示结果须保持一致，不出现明显错位、截断、遮挡、字体溢出或不可点击区域

#### Scenario: 差异可追踪
- **WHEN** 某一浏览器存在细微渲染差异
- **THEN** 差异须被记录到布局调整说明文档，并注明是否已修复、规避方案或接受理由

### Requirement: 布局调整说明文档交付
系统 SHALL 产出一份 Markdown 说明文档，清晰记录本次布局重构的修改范围和适配效果。

#### Scenario: 说明文档结构完整
- **WHEN** 实现完成并准备交付
- **THEN** 文档须至少包含修改文件路径、每个文件的核心调整内容、断点适配策略、跨浏览器验证结果、与参考图的主要对齐点

#### Scenario: 文档输出位置统一
- **WHEN** 布局调整说明文档生成
- **THEN** 文档须输出到 `d:\AI\.chaos\zhujianwudao\outputs\reviews\` 下的 Markdown 文件，遵循项目既有文档输出约定

## MODIFIED Requirements
### Requirement: 首页布局优先级
现有首页以“极简单列对话流”为主要布局策略，但本次重构后需升级为“参考图驱动的分层布局策略”，在保留极简审美的同时强化信息区块的结构感和操作区的组织性。

#### Scenario: 从单列极简到分层极简
- **WHEN** 用户对比重构前后的首页
- **THEN** 新版本应保持水墨简洁基调，但 Header、主内容区与输入区之间的层次、留白与对齐关系更明确，不再只是简单的单列堆叠
