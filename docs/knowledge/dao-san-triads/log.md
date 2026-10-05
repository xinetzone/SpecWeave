# 更新日志

## 2026-10-05

- **新增**：`examples/02-zhen-xu-qiu-day5.md` —— 腾讯会议 501921501「如何找到真需求Day5」实录走查（seven-concepts 场景4，链路 R→I→E→V，depth=deep）
  - R：RF-001~RF-050 事实清单（三源：元宝纪要接口 / 分享页 / 本包对照）
  - I：4 条洞察，其中 I-1 首次登记「真需求」的**方向层分叉**（向内＝缺口 vs 向外＝要价）
  - E：新增候选模式「**格式判据**」（L1-draft，待第二案例）；「三之位」迁移域 4→5，成熟度 **L1-draft 升 L2**
  - V：4 视角 / 15 条意见 / 采纳 8 条
- **信源限制**：该会议录制文件权限为 `can_apply`，未取得观看权限，全过程未使用逐字稿；02 页素材全部为元宝纪要（AI 加工产物）
- **连带更新**：`examples/index.md`（toctree + 索引表 + 信源声明）、根 `index.md` §6 迁移表与成熟度、§8 G3 行、§11 相关页面
- **方法论**：场景4 知识沉淀的标准链路为 R→I→E→V→C；本次**未执行 C 原子提交**——所在仓库工作区已存在 2 个已修改文件、1 个已修改子模块、4 个未跟踪条目，需单独确定性提交，待确认

## 2026-10-03

- **归档**：从 SpecWeave 主仓库 `docs/knowledge/dao-san-triads/` 迁移至本库 `guoxue/laozi/dao-san-triads/`（OKF v0.2 bundle，完整保留 concepts/examples/references 三层结构与 12 个文件）
- **位置依据**：内容锚定《道德经》第四十二章「道生一，一生二，二生三」，归入「国学/老子（Laozi）」组，与 `boshu-reading`（怎么读）、`laozi-works`（原文与解读）、`laozi-lineage`（版本源流）并列互补
- **调整**：根 `index.md` frontmatter 将 `spec` 相对路径替换为 `sources` 溯源字段；「上游规范」改为纯文本说明（原相对链接指向 SpecWeave 工作区内部资产，本仓库内不可解析）
- **方法论**：seven-concepts 场景4（知识沉淀），链路 F→R→I→E→V→A→C（源包内留痕）
