---
id: "rules-alt-design-tokens"
title: "07 主题变量/设计令牌"
source: "alternatives-guide.md#design-tokens"
x-toml-ref: "../../../.meta/toml/.agents/rules/alternatives-guide/07-design-tokens.toml"
---
# 07 主题变量/设计令牌


## 适用场景

颜色值、字体族、字号、间距、阴影、圆角等样式硬编码（`HARD-STYLE`）。

## 实施步骤

1. 定义设计令牌 JSON 文件，按层次组织：**基础令牌 → 语义令牌 → 组件令牌**。
2. 在样式代码中引用令牌变量，禁止直接写入色值、像素值。
3. 支持通过切换令牌文件实现主题切换（如亮色/暗色模式）。

## 示例代码

**`tokens/design_tokens.json`**

```json
{
  "base": {
    "color": {
      "white": "#FFFFFF",
      "black": "#000000",
      "gray_50": "#F9FAFB",
      "gray_100": "#F3F4F6",
      "gray_200": "#E5E7EB",
      "gray_400": "#9CA3AF",
      "gray_600": "#4B5563",
      "gray_800": "#1F2937",
      "gray_900": "#111827",
      "blue_500": "#3B82F6",
      "blue_600": "#2563EB",
      "blue_700": "#1D4ED8",
      "red_500": "#EF4444",
      "red_600": "#DC2626",
      "green_500": "#22C55E",
      "green_600": "#16A34A",
      "yellow_500": "#EAB308",
      "yellow_600": "#CA8A04"
    },
    "spacing": {
      "xs": "4px",
      "sm": "8px",
      "md": "16px",
      "lg": "24px",
      "xl": "32px",
      "2xl": "48px"
    },
    "font_size": {
      "sm": "0.875rem",
      "base": "1rem",
      "lg": "1.125rem",
      "xl": "1.25rem",
      "2xl": "1.5rem",
      "3xl": "1.875rem"
    },
    "font_family": {
      "sans": "'Inter', 'Noto Sans SC', system-ui, sans-serif",
      "mono": "'JetBrains Mono', 'Fira Code', monospace"
    },
    "border_radius": {
      "sm": "4px",
      "md": "8px",
      "lg": "12px",
      "full": "9999px"
    },
    "shadow": {
      "sm": "0 1px 2px rgba(0, 0, 0, 0.05)",
      "md": "0 4px 6px rgba(0, 0, 0, 0.1)",
      "lg": "0 10px 15px rgba(0, 0, 0, 0.1)"
    }
  },
  "semantic": {
    "color": {
      "primary": "{base.color.blue_600}",
      "primary_hover": "{base.color.blue_700}",
      "danger": "{base.color.red_600}",
      "danger_hover": "{base.color.red_500}",
      "success": "{base.color.green_600}",
      "warning": "{base.color.yellow_600}",
      "text_primary": "{base.color.gray_900}",
      "text_secondary": "{base.color.gray_600}",
      "text_disabled": "{base.color.gray_400}",
      "bg_primary": "{base.color.white}",
      "bg_secondary": "{base.color.gray_50}",
      "border": "{base.color.gray_200}"
    }
  },
  "component": {
    "button": {
      "primary_bg": "{semantic.color.primary}",
      "primary_hover_bg": "{semantic.color.primary_hover}",
      "height": "40px",
      "padding_x": "{base.spacing.lg}",
      "border_radius": "{base.border_radius.md}",
      "font_size": "{base.font_size.base}"
    },
    "card": {
      "bg": "{semantic.color.bg_primary}",
      "border": "{semantic.color.border}",
      "border_radius": "{base.border_radius.lg}",
      "padding": "{base.spacing.lg}",
      "shadow": "{base.shadow.sm}"
    },
    "input": {
      "height": "40px",
      "border": "{semantic.color.border}",
      "border_radius": "{base.border_radius.md}",
      "padding_x": "{base.spacing.sm}",
      "font_size": "{base.font_size.base}"
    }
  }
}
```

**样式引用示例（CSS 变量风格）**

```css
/* 原有硬编码写法（禁止）：
   .button { background: #2563EB; padding: 16px 24px; border-radius: 8px; } */

/* 推荐写法：引用设计令牌生成的 CSS 变量 */
:root {
  --color-primary: #2563EB;
  --color-primary-hover: #1D4ED8;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --radius-md: 8px;
  --font-size-base: 1rem;
}

.button-primary {
  background: var(--color-primary);
  padding: 0 var(--spacing-lg);
  height: 40px;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
}

.button-primary:hover {
  background: var(--color-primary-hover);
}

.card {
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}
```
---

## 相关模式

- [硬编码治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/README.md)
- [三级问题解决](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-level-problem-solving.md)
- [检查与恢复模式](../../docs/retrospective/patterns/code-patterns/check-and-restore.md)
---

← 上一章: [06 模式常量库](06-regex-patterns.md) | **[返回索引](../alternatives-guide.md)** | 下一章: [08 模板与脚手架](08-project-scaffold.md) →
