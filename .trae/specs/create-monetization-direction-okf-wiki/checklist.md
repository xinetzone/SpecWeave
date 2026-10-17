# 个人变现方向发现方法论 · OKF Wiki — 验证清单（checklist.md）

> 用途：Spec Mode 第七阶段逐项验证。每项通过后勾选；未通过则在 `tasks.md` 新建任务修复后重验。

## 事实与核验

- [ ] CP-1（AC-1）：`facts.md` 存在，F 编号 F-001 起连续无跳号（跳号显式注记），条数 ≥60，四类信源关键声明均有对应条目，观点/主张与事实分层标注
- [ ] CP-2（AC-2）：C1/C3/C4 类 P0 声明（提出者/年份/核心主张归属）与全部数字声明 100% 有核验记录（权威 URL 或显式单源标注）
- [ ] CP-3（AC-2）：勘误四张清单（日期/年份表、成效数字溯源表、口径对照表、引文逐字核对表）逐项过筛并记录于 `verification.md`
- [ ] CP-4（AC-2）：涉及性格/天赋测评工具的内容均有科学效度争议与"非决定论"边界标注
- [ ] CP-5（AC-6）：`facts.md` 与 `references/article-source.md` 的 F 编号集合正则比对一致，差异项已在 `log.md` 注记

## 结构与归属

- [ ] CP-6（AC-3）：bundle 落于既有分组（`sheke/industry`），未新建顶级分组，归属理由已留痕于 `knowledge-map.md` / `log.md`
- [ ] CP-7（AC-3）：组 index 导航表行、toctree 条目、束数计数三面同步；`sheke/index.md` 与 `bundles/index.md` 计数同步（以现值 +1 为准）
- [ ] CP-8（AC-4）：bundle 结构符合 OKF v0.2——根 `index.md` 带 `okf_version: "0.2"` 且含 toctree；`concepts/`、`references/`（article-source.md + verification.md）、`log.md` 齐备；全部非保留 `.md` 含非空 `type`
- [ ] CP-9（AC-4）：`examples/` 取舍由操作可复现性两问判定，结论与理由已记录于 `log.md`
- [ ] CP-10（AC-4）：frontmatter 字段齐备（type/title/description/tags/generated/verified/status/stale_after/sources），`sources` 含理论/著作来源与核验权威 URL

## 链接与编码

- [ ] CP-11（AC-5）：三级 toctree 完整，条目（排除 `:` 指令行）逐一可达
- [ ] CP-12（AC-5）：全部新增/修改 `.md` 相对链接可达，零 `file:///` 绝对路径
- [ ] CP-13（AC-5）：UTF-8 strict roundtrip 无乱码

## 质量与边界

- [ ] CP-14（AC-8，rubric）：方法链路可操作性 ≥4 分——自我盘点表 + 候选方向生成法 + 需求验证实验 + 决策清单，每步有输入、步骤、判定标准与常见误区；附理由与证据
- [ ] CP-15（AC-9，rubric）：七概念质量门 ≥4 分——G1 事实无因果词 / G2 洞察四元组完整 / G3 模式含触发场景+核心步骤+反模式+迁移验证 / G4 行动项原子化；F 后经 V 对抗审查；附理由与证据
- [ ] CP-16（AC-10）：无 F 支撑的因果或收益断言为零（或已降级为显式假设）；无收益承诺；无具体产品/课程推荐
- [ ] CP-17（AC-10）：魔鬼代言人专项审查记录存在，逐条给出"成立/降级/删除"结论

## 门禁与提交

- [ ] CP-18（AC-7）：`invoke gates.all` 三 gate 全绿；依赖不可用时已执行手动等效验证清单并在 `log.md` 注明（未谎报 gates 状态）
- [ ] CP-19（AC-7）：提交顺序为子模块 → 主仓库 spec → 主仓库子模块指针；Conventional Commits 中文描述；显式文件列表
- [ ] CP-20（AC-7）：`git log` 验证未 push；既有 bundle 正文零改动（仅新增与索引追加）

## 交付物

- [ ] CP-21：`projects/awesome-okf-xs/doc/bundles/sheke/industry/<bundle>/` 新 bundle 落盘完整
- [ ] CP-22：`.trae/specs/create-monetization-direction-okf-wiki/` 含 spec.md / tasks.md / checklist.md / facts.md / sources.md / knowledge-map.md
