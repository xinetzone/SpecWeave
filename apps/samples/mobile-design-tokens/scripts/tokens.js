/* =============================================================
   Token 数据源 —— 与 Ardot 画布《移动端 Design Token 体系》一一对应
   数据来源：画布变量集合导出（Primitives / Semantic / Radius / Shadow）
   注意：这里只存「值」，视觉层一律通过 CSS 变量在 styles/tokens.css 中消费，
        因此切换 Mode 时组件属性不变、整体自动换肤。
   ============================================================= */

window.DESIGN_TOKENS = {
  meta: {
    collections: 4,
    variables: 113,
    modes: 2,
    summary: "语义层与色阶层分离",
  },

  /* ---------------- 01 原始色阶 Primitives ---------------- */
  primitives: [
    {
      id: "neutral",
      title: "Neutral 中性色 · 12 阶（表面与文字的基础）",
      swatches: [
        { step: "0", hex: "#FFFFFF" },
        { step: "50", hex: "#F7F8FA" },
        { step: "100", hex: "#F1F3F6" },
        { step: "200", hex: "#E4E7EC" },
        { step: "300", hex: "#CFD4DC" },
        { step: "400", hex: "#A6AEBB" },
        { step: "500", hex: "#7A8496" },
        { step: "600", hex: "#5A6474" },
        { step: "700", hex: "#414A5A" },
        { step: "800", hex: "#2B3240" },
        { step: "900", hex: "#1A1F29" },
        { step: "950", hex: "#0E1218" },
      ],
    },
    {
      id: "brand",
      title: "Brand 品牌色 · 10 阶（brand-500 为默认主色）",
      swatches: [
        { step: "50", hex: "#EEF3FF" },
        { step: "100", hex: "#DCE6FF" },
        { step: "200", hex: "#BCD0FF" },
        { step: "300", hex: "#92B2FF" },
        { step: "400", hex: "#638CFF" },
        { step: "500", hex: "#3B62F6" },
        { step: "600", hex: "#2B4BD4" },
        { step: "700", hex: "#2139AB" },
        { step: "800", hex: "#1C2E88" },
        { step: "900", hex: "#182670" },
      ],
    },
    {
      id: "functional",
      title:
        "Functional 功能色 · 成功 / 警告 / 危险（100 浅底、500 主色、700 文本）",
      swatches: [
        { step: "100", hex: "#E7F8EF" },
        { step: "500", hex: "#17B26A" },
        { step: "700", hex: "#087443" },
        { step: "100", hex: "#FEF0DC" },
        { step: "500", hex: "#F79009" },
        { step: "700", hex: "#B54708" },
        { step: "100", hex: "#FEE4E2" },
        { step: "500", hex: "#F04438" },
        { step: "700", hex: "#B42318" },
      ],
    },
  ],

  /* ---------------- 02 语义色 Semantic ----------------
     value 为画布上 STRING 变量（-hex）的展示值，与设计稿完全一致 */
  semantic: [
    { name: "bg-canvas", light: "#F1F3F6", dark: "#0E1218" },
    { name: "bg-surface", light: "#FFFFFF", dark: "#1A1F29" },
    { name: "bg-surface-secondary", light: "#F7F8FA", dark: "#2B3240" },
    { name: "bg-surface-raised", light: "#FFFFFF", dark: "#2B3240" },
    { name: "bg-surface-inverse", light: "#1A1F29", dark: "#F1F3F6" },
    { name: "bg-overlay", light: "#0E1218 60%", dark: "#0E1218 72%" },
    { name: "text-primary", light: "#1A1F29", dark: "#F1F3F6" },
    { name: "text-secondary", light: "#414A5A", dark: "#A6AEBB" },
    { name: "text-tertiary", light: "#7A8496", dark: "#7A8496" },
    { name: "text-disabled", light: "#A6AEBB", dark: "#414A5A" },
    { name: "text-on-accent", light: "#FFFFFF", dark: "#FFFFFF" },
    { name: "text-link", light: "#2B4BD4", dark: "#92B2FF" },
    { name: "border-subtle", light: "#F1F3F6", dark: "#2B3240" },
    { name: "border-default", light: "#E4E7EC", dark: "#414A5A" },
    { name: "border-strong", light: "#CFD4DC", dark: "#5A6474" },
    { name: "accent-primary", light: "#3B62F6", dark: "#638CFF" },
    { name: "accent-primary-pressed", light: "#2B4BD4", dark: "#3B62F6" },
    { name: "accent-disabled", light: "#BCD0FF", dark: "#2139AB" },
    { name: "accent-subtle-bg", light: "#EEF3FF", dark: "#182670" },
    { name: "accent-subtle-text", light: "#2B4BD4", dark: "#BCD0FF" },
    { name: "accent-focus-ring", light: "#92B2FF", dark: "#638CFF" },
    { name: "success-fg", light: "#087443", dark: "#17B26A" },
    { name: "success-bg", light: "#E7F8EF", dark: "#10281E" },
    { name: "warning-fg", light: "#B54708", dark: "#FDB022" },
    { name: "warning-bg", light: "#FEF0DC", dark: "#33200A" },
    { name: "danger-fg", light: "#B42318", dark: "#F97066" },
    { name: "danger-bg", light: "#FEE4E2", dark: "#3A1714" },
  ],

  /* ---------------- 03 圆角 Radius ---------------- */
  radius: [
    { name: "radius-none", px: 0, usage: "通栏容器 / 全屏封面图" },
    { name: "radius-xs", px: 4, usage: "Chip 标签 / 进度条 / 徽标" },
    { name: "radius-sm", px: 8, usage: "按钮 / 输入框 / 小提示条" },
    { name: "radius-md", px: 12, usage: "列表项 / 基础卡片（默认）" },
    { name: "radius-lg", px: 16, usage: "信息卡片 / 底部弹层顶角" },
    { name: "radius-xl", px: 24, usage: "大图卡 / 抽屉把手容器" },
    { name: "radius-2xl", px: 32, usage: "全屏模态顶部 / Banner" },
    { name: "radius-full", px: 999, usage: "头像 / 圆形图标按钮 / FAB" },
  ],

  /* ---------------- 04 阴影 Shadow ---------------- */
  shadow: [
    { name: "shadow-1", y: 1, blur: 2, spread: 0, alpha: "5%", rgba: "0.05" },
    { name: "shadow-2", y: 2, blur: 8, spread: -2, alpha: "8%", rgba: "0.08" },
    { name: "shadow-3", y: 4, blur: 16, spread: -4, alpha: "10%", rgba: "0.10" },
    { name: "shadow-4", y: 8, blur: 24, spread: -6, alpha: "12%", rgba: "0.12" },
    { name: "shadow-5", y: 16, blur: 40, spread: -8, alpha: "16%", rgba: "0.16" },
  ],

  /* 预览区文案（对应画布 05 组件预览节点） */
  preview: {
    modeLabelLight: "LIGHT MODE",
    modeLabelDark: "DARK MODE",
    pageTitle: "今日概览",
    pageSubtitle: "数据已更新 · 5 分钟前",
    badge: "NEW",
    cardTitle: "本周周报已生成",
    cardBody: "共完成 18 个任务，比上周多 3 个。点击查看完整数据看板。",
    listPrimary: "09:30 早会纪要已归档",
    listDisabled: "11:00 设计评审待确认（占位 / disabled 示例）",
    link: "查看全部动态",
    primaryAction: "立即查看",
    secondaryAction: "稍后再说",
  },
};
