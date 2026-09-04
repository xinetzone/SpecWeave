# GPT-5.6 大素数空隙突破资讯 → OKF 知识包 - Independent Review

> 仅在实施队列清空后执行独立审查。当前阶段：Specify + Plan 完成，待批准。

- [ ] CP-R1: 7 个 bundle 文件全部生成且 UTF-8 编码无乱码
  - **Type**: `rule`
  - **Covers**: AC-6, AC-8
  - **Evidence**: Pending

- [ ] CP-R2: toctree 三级完整（根 → 子目录 → 文档），所有条目文件存在
  - **Type**: `rule`
  - **Covers**: AC-8
  - **Evidence**: Pending

- [ ] CP-R3: 双份 F 编号一致（spec facts.md 与 bundle article-source.md）
  - **Type**: `rule`
  - **Covers**: AC-3, AC-8
  - **Evidence**: Pending

- [ ] CP-R4: 全部内部链接使用相对路径，无 `file:///` 绝对路径
  - **Type**: `rule`
  - **Covers**: AC-8
  - **Evidence**: Pending

- [ ] CP-R5: 索引计数同步（组 index + 域 index + 总 index 三面一致）
  - **Type**: `rule`
  - **Covers**: AC-10
  - **Evidence**: Pending

- [ ] CP-R6: 勘误在 verification.md 和 bundle 正文中均如实落实
  - **Type**: `rule`
  - **Covers**: AC-4, AC-9
  - **Evidence**: Pending

- [ ] CP-U1: 内容质量——事实溯源完整、观点与事实分层清晰
  - **Type**: `rubric`
  - **Covers**: AC-3, AC-5
  - **Scale**: 1-5
  - **Anchors**: 1 = 事实无F编号、观点事实混淆；3 = 主要事实有编号、观点基本可区分；5 = 全部声明可溯源、分层严格、勘误落实
  - **Pass Threshold**: >= 4
  - **Evidence**: Pending

- [ ] CP-U2: 结构规范——符合 OKF v0.2 bundle 结构与资讯速报骨架
  - **Type**: `rubric`
  - **Covers**: AC-2, AC-7
  - **Scale**: 1-5
  - **Anchors**: 1 = 缺 frontmatter 或缺 toctree；3 = 结构完整但细节不规范；5 = 严格遵循 OKF v0.2，frontmatter/toctree/命名全部合规
  - **Pass Threshold**: >= 4
  - **Evidence**: Pending

## Review History

<!-- 实施完成后在此记录审查轮次 -->
