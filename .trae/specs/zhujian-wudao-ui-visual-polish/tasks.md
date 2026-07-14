# Tasks

- [x] Task 1: 建立色彩体系与字体层级规范（CSS 变量层）
  - [ ] SubTask 1.1: 在 `src/styles/index.css` 中补充色彩使用注释，明确三级色彩（朱砂红/墨色/宣纸色）的变量定义和使用场景
  - [ ] SubTask 1.2: 在 `src/styles/typography.css` 中建立字号阶梯规范（标题 20px / 正文 14-16px / 辅助 12px / 提示 11px）
  - [ ] SubTask 1.3: 添加统一的交互反馈工具类（`.btn-hover` / `.btn-active` / `.btn-focus`）到 `src/styles/components.css`

- [x] Task 2: Header 视觉精修
  - [ ] SubTask 2.1: 修改 `src/routes/index.tsx` 中 Header 的 Logo 区域 — 改为朱砂红印章风格（方形圆角、seal-red 背景、白色书法字"悟"、微妙阴影）
  - [ ] SubTask 2.2: 优化 Header 标题排版 — "竹简悟道"使用 font-calligraphy 类、字号 20px、字间距 0.08em；副标题 opacity 0.7
  - [ ] SubTask 2.3: 统一 Header 右侧按钮样式 — 所有按钮高度 36px、圆角 6px、hover/active/focus 三态一致
  - [ ] SubTask 2.4: 为 Header 底部分隔线添加渐变效果（中间深、两端浅），增强视觉层次

- [x] Task 3: LaidBackToggle 视觉重构
  - [ ] SubTask 3.1: 修改 `src/components/LaidBackToggle.tsx` — 正经模式态：宣纸色背景 + 墨色细边框 + 卷轴图标
  - [ ] SubTask 3.2: 修改 `src/components/LaidBackToggle.tsx` — 摆烂模式态：朱砂红/8% 背景 + 朱砂红边框 + 咖啡图标（移除 amber/orange 渐变）
  - [ ] SubTask 3.3: 统一按钮尺寸为 36px 高、圆角 6px、内边距 8px 12px

- [x] Task 4: ModelSelector 视觉优化
  - [ ] SubTask 4.1: 读取 `src/components/ModelSelector.tsx` 当前实现
  - [ ] SubTask 4.2: 优化选择器默认态 — 宣纸色背景 + 墨色细边框 + 36px 高 + 6px 圆角
  - [ ] SubTask 4.3: 优化下拉列表展开态 — 宣纸色背景 + 阴影 + 选项 hover 朱砂红/8% + 选中项朱砂红左边框

- [x] Task 5: 空状态视觉增强
  - [ ] SubTask 5.1: 优化 `src/routes/index.tsx` 中空状态引言排版 — 书法字体、18px、上下 32px 留白
  - [ ] SubTask 5.2: 添加引言下方渐变墨色分隔线（40px 宽，中间深两端浅）
  - [ ] SubTask 5.3: 美化示例提问按钮 — 胶囊形（20px 圆角）、宣纸色背景、hover 朱砂红边框和文字

- [x] Task 6: 竹简卡片（BambooSlip）视觉微调
  - [ ] SubTask 6.1: 读取 `src/components/BambooSlip.tsx` 当前实现
  - [ ] SubTask 6.2: 优化卡片阴影 — 使用更柔和的墨色阴影（rgba(20,20,20,0.06)）替代纯黑
  - [ ] SubTask 6.3: 优化卡片边框 — 使用墨色/10% 透明度的细边框，hover 时边框加深

- [x] Task 7: 验证与回归测试
  - [ ] SubTask 7.1: 启动 Vite 开发服务器，访问 http://localhost:3015 验证所有视觉变更
  - [ ] SubTask 7.2: 检查控制台无错误（特别确认无 Google Fonts 相关错误）
  - [ ] SubTask 7.3: 截图对比优化前后效果，确认 Header/空状态/按钮样式均符合 spec 要求

# Task Dependencies
- Task 2 depends on Task 1（需要色彩和字体规范先建立）
- Task 3 depends on Task 1（需要统一的交互反馈工具类）
- Task 4 depends on Task 1（需要色彩规范）
- Task 5 depends on Task 1（需要字体层级规范）
- Task 6 无依赖，可与 Task 2-5 并行
- Task 7 depends on Task 2, Task 3, Task 4, Task 5, Task 6（所有视觉变更完成后统一验证）
