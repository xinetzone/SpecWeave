# Checklist

## 色彩与字体规范
- [x] `src/styles/index.css` 中包含三级色彩（朱砂红/墨色/宣纸色）的使用注释和变量定义
- [x] `src/styles/typography.css` 中包含字号阶梯规范（标题 20px / 正文 14-16px / 辅助 12px / 提示 11px）
- [x] `src/styles/components.css` 中包含统一的交互反馈工具类（.btn-hover / .btn-active / .btn-focus）

## Header 视觉精修
- [x] Logo 呈现为朱砂红印章风格（方形圆角、seal-red 背景、白色书法字"悟"、微妙阴影）
- [x] "竹简悟道"标题使用 font-calligraphy 类、字号 20px、字间距 0.08em
- [x] 副标题"慢下来，把问题想透"使用宋体、字号 12px、字重 300、opacity 0.7
- [x] Header 右侧所有按钮高度 36px、圆角 6px、hover/active/focus 三态一致
- [x] Header 底部分隔线为渐变效果（中间深、两端浅）

## LaidBackToggle 视觉重构
- [x] 正经模式态：宣纸色背景 + 墨色细边框 + 卷轴图标（无 amber/orange 渐变）
- [x] 摆烂模式态：朱砂红/8% 背景 + 朱砂红边框 + 咖啡图标（无 amber/orange 渐变）
- [x] 按钮尺寸为 36px 高、圆角 6px、内边距 8px 12px

## ModelSelector 视觉优化
- [x] 选择器默认态：宣纸色背景 + 墨色细边框 + 36px 高 + 6px 圆角
- [x] 下拉列表展开态：宣纸色背景 + 阴影 + 选项 hover 朱砂红/8% + 选中项朱砂红左边框（原生 select 限制下已最大化美化）

## 空状态视觉增强
- [x] 道德经引言使用书法字体、字号 18px、字重 400、上下 32px 留白
- [x] 引言下方有 40px 宽的渐变墨色分隔线
- [x] 示例提问按钮为胶囊形（20px 圆角）、hover 时朱砂红边框和文字

## 竹简卡片视觉微调
- [x] 卡片阴影使用柔和墨色阴影（rgba(20,20,20,0.06)）
- [x] 卡片边框使用墨色/10% 透明度细边框，hover 时加深

## 验证与回归
- [x] Vite 开发服务器正常启动，页面可访问
- [x] 控制台无 Google Fonts 相关错误（net::ERR_ABORTED）
- [x] 控制台无 TypeScript 编译错误
- [x] 截图对比确认所有视觉变更符合 spec 要求
