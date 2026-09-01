---
stage: C
topic: textualize-okf-wiki
generated: 2026-09-01
status: rolling
---

# Textualize OKF Wiki — 阶段复盘（C：模式沉淀）

## 一、流程概览

R（事实采集→377 条 F-xxx）→ I（5 洞察 + 27 概念 + 8 示例知识地图）→ E（references 信源先行 → concepts 分批 → examples 分批 → index 收尾）→ V（独立验证 + 批量修复）→ C（本复盘）。

产出物：`projects/Textualize/`（index / concepts×27+index / examples×8+index / references×12+index / log）。

## 二、顺利点

1. **insights.md 事实编号导航是其价值核心**：每篇概念文档的 F-xxx 覆盖在 I 阶段一次性标注，E 阶段子代理严格照抄，避免重复协商，"377 条每篇恰好主覆盖一次"目标可落地。
2. **references 信源先行**：commit hash 在 Task5 固定后，全部内容文档的 sources/路径引用一致，后续无需返工信源。
3. **防虚构纪律在子代理层生效**：多个子代理主动用 Grep 验证 `_post_validate`/`@medium` 不存在、`Segment.CONTROL_CLEAR` 不存在、`Server(app)` 与真实 `Server(command)` 签名不符、Gradient 无事实支撑——均选择弃用/改道而非编造。
4. **洞察5 的"两节结构"模板**（复用了哪些原语 + 本工具独有机制）显著降低了 7 个卫星仓库文档的同质化组织成本。

## 三、问题点

1. **description 长度门在生成阶段未前置**：33/35 篇 description 初稿超 80 字，V 阶段才批量压缩。属于"门迟设"——应在每个生成子代理的任务书里硬性写 30–80 字而非留给 V 抽查。
2. **跨批交叉链接目标名漂移**：`09-rich-progress` 引用了不存在的 `06-rich-table-panel.md`（正确是 `06-rich-table.md`）。并行子代理各自猜目标文件名，缺乏"已生成清单"共享，只能靠 V 断链检查兜底。
3. **Windows 路径触发信源审计误报**：示例代码 `escape("C:\\foo[bar]")` 被 check-source-path-stability.py 判为"不存在的路径引用"（blocking）。示例中应避免出现 `C:\` 形态的字符串字面量，或用不歧义文本。
4. **并行会话对源码根路径的认知分歧**：一个子代理误查 `external/` 而非 `external/dao/action/Textualize/` 得出"rich 未物化"的错误结论，其余子代理却能 Grep 到源码——暴露共享工作区目录认知需要统一注入信源根全路径。

## 四、反模式（供复用）

- **AM-努力编码于 prompt 而非门**：把质量约束（长度/字段/文件名）写进任务书而非依赖事后 gate，是更省的路径；本次因 prompt 缺长度约束导致 V 阶段 33 处改动。
- **AM-并行子代理共享目标异构**：多个写手并发写同一目录但各自推断文件名/交叉链接，必然产生断链；应先固化"目标文件清单 + 已存在命名"再开放并行写。
- **AM-示例代码泄露运行时环境形态**：示例/文档中的路径字符串应以"教学语义"而非"本机形态"呈现，避免被自动化审计误伤。

## 五、下轮改进

1. 每个内容文档生成任务书内嵌硬性门：description 30–80 字、sources 指向 references 已登记 id、交叉链接必须引用"预声明文件清单"。
2. 子代理任务书统一注入信源根绝对路径（`external/dao/action/Textualize/<repo>`）与每个 repo 的源码相对位（textual→src/textual/，rich-cli→src/rich_cli/），消除目录认知分歧。
3. 新增 bundle 后立即通过 references 清单反推交叉链接白名单，作为断链检查的前置约束。