# Tasks — 道家著作全谱系调研与 OKF 知识包

方法论：seven-concepts 场景4（知识沉淀）R→I→E→V→C。
产出根目录（Phase 1+ 入库）：`projects/awesome-okf-xs/doc/bundles/think/daojia/`
Phase 0 调研工作区：`.trae/specs/daojia-canon-okf-wiki/`
规范前置：实现前先读 `projects/awesome-okf-xs/.agents/rules/frontmatter.md` 与 `.agents/global-core-rules.md`。

> 用户决策：范围=全谱系通览；落位=统一 `think/daojia/` 分组；节奏=先调研后定。Phase 0 是本次可执行交付；Phase 1+ 摘要属待确认后展开的下一阶段，不在此处过度展开。

---

## Phase 0：全谱系调研（R，本次交付）

- [x] Task 1: 四段谱系信源采集与事实登记（G1）
  - [x] 1.1 先秦道家诸子段：庄/列/文子/鹖冠子/关尹子/管子道家四篇——采集书名、托名、出土/传世版本、核心思想、权威底本注本
  - [x] 1.2 黄老之学段：阴符经、黄帝四经（马王堆帛书四种）、淮南子、尹文子、慎到/田骈辑佚——采集同上，重点核校出土文献释文
  - [x] 1.3 魏晋玄学注疏段：王弼老子注/周易注、河上公章句、严遵指归、郭象庄子注、成玄英庄子疏——采集注家立场与版本沿革
  - [x] 1.4 道教经典段：参同契/抱朴子/太平经/黄庭经/清静经——采集道藏本源流与义理定位
  - [x] 1.5 产出 `.trae/specs/daojia-canon-okf-wiki/facts.md`：四段谱系编号事实目录，纯客观描述（禁因果词），每部著作带信源 URL 与权威性评级
- [x] Task 2: 谱系洞察提炼（I，G2），依赖 Task 1
  - [x] 2.1 产出 `insights.md`：≥5 条四元组洞察（现象+根因+影响+建议），重点覆盖「托名层/文本层之分」「出土文献改写谱系认知」「伪书鉴别」「玄学注疏承前启后」等
  - [x] 2.2 每部著作标注「托名层/文本层」判定与争议学说（≥2 观点及依据，如有争议）
- [x] Task 3: 判读模式萃取（E，G3），依赖 Task 2
  - [x] 3.1 萃取 ≥3 个可复用「道家经典判读/谱系重建」模式（如「托名文本三层判读法」「双源逐字核读法」「传本谱系重建法」），各含触发场景/核心步骤/反模式/迁移示例
- [x] Task 4: 目录结构与优先级建议（Phase 0 确认点输入），依赖 Task 1
  - [x] 4.1 提出 `think/daojia/` 统一分组的子 bundle 结构建议（含既有 `think/laozi` 与《阴符经》 spec 的迁移/并入方案）
  - [x] 4.2 提出入库优先级序（先核心诸子，后黄老/玄学/道教）与每部著作的 bundle 粒度建议
- [x] Task 5: 确认点（checkpoint，阻塞 Phase 1+）
  - [x] 5.1 向用户呈现全谱系清单 + 目录结构建议 + 优先级，经用户确认入库范围/顺序/迁移决策后进入 Phase 1+

---

## Phase 1+：逐册入库（调研确认后展开，此处仅列骨架）

- [ ] Task 6: 建 `think/daojia/` 分组总纲 index + 更新 `think/index.md`、`bundles/index.md`
- [ ] Task 7: 逐著作建立 bundle（index + concepts/examples/references + facts/insights/log），按确认优先级展开
  - 每册复用「R 事实核校 → I 洞察 → E 模式 → V 双源抽查 → C 原子提交」子链路
- [ ] Task 8: 每册 V 对抗审查（原文 10 处 + 事实 10 条抽查）+ `invoke gates.all` 质量门
- [ ] Task 9: 逐册 atomic-commit 原子提交（`docs(bundles): 新增道家<著作>知识包`），同步主仓 gitlink（如适用）

# Task Dependencies

- Task 2/3 依赖 Task 1（事实先行）
- Task 4 依赖 Task 1；Task 5（确认点）依赖 Task 1-4 全部完成
- Phase 1+（Task 6-9）**阻塞**于 Task 5 用户确认；确认后 Task 6/7 可并行，Task 8 依赖对应册 Task 7，Task 9 依赖 Task 8