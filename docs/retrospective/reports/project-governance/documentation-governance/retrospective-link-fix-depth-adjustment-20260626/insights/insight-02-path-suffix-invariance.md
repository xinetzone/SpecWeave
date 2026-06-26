+++
id = "retrospective-link-fix-depth-adjustment-20260626-insight-02"
date = "2026-06-26"
type = "insight"
parent = "retrospective-link-fix-depth-adjustment-20260626-insights"
source = "insight-extraction.md#发现-2路径后半段的不变性是自动校正的关键"
maturity = "L1"
pattern = "relative-depth-adjustment"
+++

# 发现 2：路径后半段的不变性是自动校正的关键

> ✅ 本洞察是 [relative-depth-adjustment](../../../../../patterns/code-patterns/relative-depth-adjustment.md)（L2）的核心假设。

**事实支撑**：断链路径中，非`../`部分（文件名和中间目录名）通常保持不变，只是相对根的位置变了。这使得"调整`../`层数"比"模糊搜索文件名"更精确，优先精确匹配可大幅降低误报率。

---

> **关联模块**：
> - [insight-01-predictable-link-breakage.md](insight-01-predictable-link-breakage.md)
> - *来源：[insight-extraction.md](../insight-extraction.md#一关键发现)*
