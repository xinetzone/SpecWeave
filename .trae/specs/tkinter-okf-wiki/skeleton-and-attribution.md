# tkinter 简书系列 → OKF Wiki：骨架判定与归属决策

## 1. 信源概况（公开内容）

| 博客集 | 简书 URL | 篇数 | 作者 |
|---|---|---|---|
| tkinter GUI 设计 | https://www.jianshu.com/nb/41423750 | 34 | 水之心（uid 1114626） |
| tkinter 手册 | https://www.jianshu.com/nb/45837499 | 21 | 水之心 |
| tkinterx 手册 | https://www.jianshu.com/nb/45403586 | 5 | 水之心 |

合计 60 篇、354,027 字符、235 张唯一图片（已本地化，0 失败）。付费文章 1 篇（3.12 创建登录窗口，登录会话下完整获取）；「待更」短文 3 篇。抓取方式：Kimi WebBridge 拟人化慢速抓取。

## 2. 骨架判定（操作可复现性两问）

两问均为「是」：教程含大量可运行 Python 代码，截图即作者实测运行结果。→ 3 个博客集均采用完整骨架 references/ + concepts/ + examples/。

## 3. 归属决策

- 域：jishu；分组：**新建 gui**（_static/bundles/jishu/gui/ 约定已存在）。
- bundle 映射：tkinter-gui-design（34 篇，F-TGD-01…34）、tkinter-handbook（21 篇，F-THB-01…21）、tkinterx-handbook（5 篇，F-TXH-01…05）。

## 4. F 编号与图片规则

1. references/sources.md 逐篇登记：F 编号 | 标题 | 原文链接 | 抓取日期 | 备注。
2. 正文事实以脚注 [^F-XXX-NN] 溯源，文末脚注指向信源登记。
3. 图片本地化路径：_static/bundles/jishu/gui/<bundle>/images/<article-slug>-<original-name>；内容文档相对引用 ../../../../../_static/bundles/jishu/gui/<bundle>/images/...。
4. 「待更」篇目标注备注，不臆造未发布内容。

## 5. 落盘策略

生成区：.trae/specs/tkinter-okf-wiki/dist/ 镜像 OKF 树；V 阶段门禁后部署至 projects/awesome-okf-xs/doc/，接入 gui 分组 index、jishu 域 index 与总索引对账（invoke gates.bundles）。

## 6. 时效

status: stable；tkinter 为标准库、API 稳定，stale_after: 2027-09-02；generated.by: blog-article-to-okf-wiki/trae。