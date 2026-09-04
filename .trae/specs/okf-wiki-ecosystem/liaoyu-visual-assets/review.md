# 艺术疗愈六束视觉资产增补 - Verification Checklist

## R/I 阶段（方案）
- [x] visual-plan.md 存在，含 7 行配图表（束/文件名/落盘目录/插入位置/alt/prompt/尺寸）与 8–12 行 Mermaid 表（编号/目标文件/章节锚点/类型/完整源码/引导句/事实来源）
- [x] 每张 Mermaid 的事实性内容（人名/年份/组织/模型/阶段名）均标注束内来源文件，无新造事实
- [x] Mermaid 源码草案静态合规：无空行、中文标签双引号、无 `\n`、无 `"1. "`/`"- "` 列表触发、subgraph 与边标签格式正确
- [x] 配图 prompt 含统一风格约束（暖调纸感编辑插画、no text）且无医疗疗效暗示

## E 阶段（配图）
- [x] 7 张图片全部落盘于 `doc/_static/bundles/yishu/liaoyu/<bundle>/images/`（组首页图在 `liaoyu/images/`），单文件 > 50KB（实测 363–482 KB，均 .jpg）
- [x] 7 图风格统一（暖灰/米白/暖赭、柔和纸感、无文字乱码），主题与各束定位一一对应
- [x] visual-plan.md 已回写每张图实际文件名与扩展名

## E 阶段（插入）
- [x] 6 束 index.md 与组 liaoyu/index.md 导语后各插入 1 张封面图引用，路径为 `/_static/bundles/yishu/liaoyu/...` 正斜杠形式且与落盘文件完全一致
- [x] 8–12 张 Mermaid 按方案插入 concepts/examples 目标章节，每块前有中文引导句（实际 10 张）
- [x] 每束 ≥1 张 Mermaid；总量 ≤12（适度原则）（分布 3/2/2/1/1/1）
- [x] 6 束 log.md 均追加 2026-09-02 视觉增补记录（数量/位置/方法）
- [x] frontmatter、facts.md、references/、免责声明、toctree 零改动（Task 3 自检 git diff 确认，V 阶段独立复核）

## V 阶段（对抗验证）
- [x] 新增 Mermaid 块逐个通过六规则人工复核（空行/引号/列表触发/换行/subgraph/边标签）——10 块 0 违规
- [x] Mermaid 事实抽查 ≥5 束：年份/人名/组织名与 facts.md/正文一致——实查 6 束（M2/M4/M6/M7/M8/M10）全一致
- [x] `invoke build`（sphinx-build）零警告零错误（无 image not readable、无 mermaid parse error、无 Malformed YAML）——全量 reading 0 warning；聚焦构建 succeeded，liaoyu 相关 warning 为 0；7/7 图入 _images，10/10 mermaid 块输出渲染容器（全量 writing 受沙箱时长与 intersphinx 工具链 bug 限制，非内容问题）
- [x] `invoke gates.all`：utf8 / toctrees / bundles 三项全绿（7518 文件 UTF-8；9 域/44 组/389 束五面一致）
- [x] `git diff --stat` 审计：变更集仅含图片新增、7 个 index.md、concepts/examples 目标文档、6 个 log.md；无既有正文行被删除或改写（23 md 全部 hunk 纯新增）
- [x] `.git/MERGE_HEAD` 不存在，无并行合并竞态
- [x] 所有新增/修改文件 UTF-8 无 BOM，无 `file:///` 绝对路径引用

## C 阶段（闭环）
- [x] 交付报告含：7 图清单、Mermaid 清单、构建/门禁结果、变更统计、遗留项
- [x] 未执行 git commit（遵用户未要求即不提交）；已提示后续原子提交建议
- [x] tasks.md 全部任务勾选完成、本 checklist 全部勾选
