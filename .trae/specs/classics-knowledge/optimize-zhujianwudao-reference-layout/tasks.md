# Tasks

- [ ] Task 1: 梳理参考图与现状页面的布局差异
  - [ ] SubTask 1.1: 盘点 `src/routes/index.tsx` 当前首页的 Header、主内容区、输入区、侧边功能入口的现状结构
  - [ ] SubTask 1.2: 将参考图中的区块关系映射为可实现的布局模型，明确哪些是排布重组、哪些是纯视觉微调
  - [ ] SubTask 1.3: 确认所有必须保留的功能组件、事件入口和状态流，形成“仅改布局不改功能”的边界清单

- [ ] Task 2: 重构首页主布局骨架
  - [ ] SubTask 2.1: 调整 `src/routes/index.tsx` 中 Header 的区块分组与组件顺序
  - [ ] SubTask 2.2: 重构空状态和活动状态的主内容区容器，使卡片、引导信息、消息流与输入区建立稳定层级
  - [ ] SubTask 2.3: 校准底部输入区的 sticky 策略和内容区底部留白，避免遮挡最后一条消息
  - [ ] SubTask 2.4: 校准首页与侧边功能入口的并存布局，确保主内容区宽度与视觉重心稳定

- [ ] Task 3: 完成三端响应式适配
  - [ ] SubTask 3.1: 在桌面端断点下落实参考图中的横向信息分布、留白比例和区块对齐
  - [ ] SubTask 3.2: 在平板端断点下处理 Header 操作区收缩、按钮换行与区块宽度回退逻辑
  - [ ] SubTask 3.3: 在移动端断点下重排 Header、主内容区和输入区，保证单手操作与触控可用性
  - [ ] SubTask 3.4: 统一更新 `src/styles/index.css`、`src/styles/components.css`、`src/styles/mobile.css` 中与断点相关的布局规则

- [ ] Task 4: 保护功能完整性并完成联调
  - [ ] SubTask 4.1: 验证 `LaidBackToggle`、`ModelSelector`、导出、清空、示例提问、消息发送等入口在新布局下仍可正常工作
  - [ ] SubTask 4.2: 验证统计卡片、今日领悟、深呼吸、造梦等浮层或扩展区块在新布局下不被遮挡
  - [ ] SubTask 4.3: 补充必要的布局回归检查或 E2E 验证，覆盖空状态与对话状态两类场景

- [ ] Task 5: 执行跨浏览器兼容性测试
  - [ ] SubTask 5.1: 在 Chromium/Chrome 环境下验证首页布局与交互显示
  - [ ] SubTask 5.2: 在 Edge 环境下验证首页布局与交互显示
  - [ ] SubTask 5.3: 在 Firefox 环境下验证首页布局与交互显示
  - [ ] SubTask 5.4: 在 WebKit 或 Safari 等价环境下验证首页布局与交互显示
  - [ ] SubTask 5.5: 记录差异项、修复结果或接受理由

- [ ] Task 6: 产出布局调整说明文档并整理交付
  - [ ] SubTask 6.1: 在 `outputs/reviews/` 下新增布局调整说明 Markdown 文档
  - [ ] SubTask 6.2: 记录修改文件路径、每个文件的核心调整内容、断点适配策略和参考图对齐点
  - [ ] SubTask 6.3: 汇总跨浏览器验证结果与最终适配效果截图或结论

# Task Dependencies
- Task 2 depends on Task 1（必须先明确参考图与现状差异，才能开始重构骨架）
- Task 3 depends on Task 2（响应式适配建立在新布局骨架之上）
- Task 4 depends on Task 2, Task 3（联调需要在骨架和断点布局稳定后进行）
- Task 5 depends on Task 3, Task 4（跨浏览器验证需要在功能与响应式布局完成后执行）
- Task 6 depends on Task 5（说明文档需基于最终实现和验证结果整理）
