---
id: "weasyprint-06-css-paged"
title: "CSS 分页与打印特性"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/weasyprint-wiki/06-css-paged-media.toml"
source: "https://weasyprint.org/ | https://weasyprint.com/ | 源码 d:\\spaces\\SpecWeave\\external\\WeasyPrint"
category: "learning"
tags: ["weasyprint","css","paged-media","@page","pagination"]
date: "2026-07-13"
status: "stable"
author: "SpecWeave"
summary: "WeasyPrint CSS分页媒体特性：@page规则、16个边距盒位置、分页控制、交叉引用、计数器、脚注，含完整CSS代码示例"
---
# CSS 分页与打印特性

WeasyPrint 的核心价值在于对**CSS Paged Media**规范的支持——这是浏览器方案长期薄弱的领域。

## 7.1 @page 规则

```css
@page {
    size: A4;                    /* 页面尺寸：A4, Letter, A3, 或自定义 210mm 297mm */
    margin: 2cm;                 /* 页边距 */
    marks: crop cross;           /* 裁切标记和对准标记 */
    bleed: 3mm;                  /* 出血区域 */
    
    @top-center {                /* 页眉边距盒 */
        content: "文档标题";
        font-family: "Noto Sans", sans-serif;
        font-size: 10pt;
        color: #666;
    }
    
    @bottom-center {             /* 页脚边距盒 */
        content: "第 " counter(page) " 页 / 共 " counter(pages) " 页";
        font-size: 9pt;
    }
    
    @bottom-right {
        content: string(doc-title); /* 命名字符串 */
    }
}

/* 第一页特殊样式 */
@page :first {
    margin-top: 5cm;            /* 第一页更大的上边距 */
    @top-center { content: none; } /* 第一页不显示页眉 */
}

/* 左页/右页（对开页） */
@page :left {
    margin-left: 3cm;
    margin-right: 2cm;
}
@page :right {
    margin-left: 2cm;
    margin-right: 3cm;
}
```

## 7.2 16 个边距盒（Margin Boxes）

```
┌─────────────────────────────────────────────────┐
│ top-left-corner  top-center  top-right-corner   │
│                                                 │
│ left-top      ┌───────────────┐    right-top    │
│               │               │                 │
│ left-middle   │   页面内容    │    right-middle │
│               │               │                 │
│ left-bottom   └───────────────┘    right-bottom │
│                                                 │
│ bottom-left-corner bottom-center bottom-right-corner │
└─────────────────────────────────────────────────┘
```

## 7.3 分页控制

```css
/* 分页符 */
.chapter {
    break-before: page;         /* 在元素前分页 */
    break-after: page;          /* 在元素后分页 */
    break-inside: avoid;        /* 避免在元素内部分页 */
}

/* 避免孤立行（widows/orphans） */
p {
    widows: 3;                  /* 页面顶部至少保留 3 行 */
    orphans: 3;                 /* 页面底部至少保留 3 行 */
}

/* 强制在某个元素后分页 */
.page-break {
    break-after: page;
}

/* 与下一个元素保持在一起 */
h2 {
    break-after: avoid;         /* 不在标题后立即分页 */
}
```

## 7.4 交叉引用与页码引用

```css
/* 使用 target-counter 引用其他位置的页码 */
.see-chapter-3::after {
    content: "（见第 " target-counter(attr(href), page) " 页）";
}

/* 使用 target-text 引用其他元素的文本 */
.cross-ref::after {
    content: " — " target-text(attr(href), content());
}

/* 命名字符串（用于页眉显示当前章节标题） */
h1 { string-set: doc-title content(); }
@page @top-center { content: string(doc-title); }

/* 运行元素（将内容移到页眉/页脚） */
.header { position: running(header); }
@page @top-center { content: element(header); }
```

## 7.5 计数器

```css
/* 自定义计数器 */
body { counter-reset: chapter figure; }

h1::before {
    counter-increment: chapter;
    content: "第 " counter(chapter) " 章 ";
}

figcaption::before {
    counter-increment: figure;
    content: "图 " counter(chapter) "." counter(figure) ": ";
}

/* 页码计数器 */
@page @bottom-center {
    content: counter(page) " / " counter(pages);
}
```

## 7.6 脚注

```css
.footnote {
    float: footnote;            /* 元素浮动到脚注区域 */
}

::footnote-call {
    content: counter(footnote);
    vertical-align: super;
    font-size: 0.7em;
}

::footnote-marker {
    content: counter(footnote) ". ";
}
```

---

| [返回总览](00-overview.md) | [上一章：Python API 完全指南](05-python-api-guide.md) | [下一章：高级功能详解](07-advanced-features.md) |
|---|---|---|
