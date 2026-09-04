# Tasks

> 交付策略：按「先验证模式、再规模复制」分三阶段推进。阶段一先落地般若系 2 个 bundle 验证 OKF 三层结构 + 双信源核对模式，阶段二/三复用该模式。每个 bundle 完成即原子提交一次（场景4 链路终点 C）。

## 阶段一：分组骨架 + 般若系 2 个 bundle

- [ ] Task 1：建立 `think/buddhism/` 分组骨架与导航索引
  - [ ] 1.1 新建 `doc/bundles/think/buddhism/index.md`（分组首页：一句话简介 + 5 个 bundle 列表表 + `{toctree}`）
  - [ ] 1.2 更新 `doc/bundles/think/index.md`：新增「📖 佛家核心经典」分组行（table 行 + `{toctree}` 条目）
  - [ ] 1.3 更新 `doc/bundles/index.md`：think 域描述图（`think["💭 think/ 思想与理论：..." ]`）、分组表新增佛家行、统计数字 286→291、分组 32→33
  - [ ] 1.4 运行 `invoke gates.toctrees` 验证导航无断链、无孤立文档

- [ ] Task 2：创建 `heart-sutra/`（《心经》）bundle
  - [ ] 2.1 信源采集与事实登记（R）：双信源核对《心经》玄奘译本全文（《大正藏》T08 No.251 + ctext.org），登记 facts.md（≥25 条编号事实，G1）
  - [ ] 2.2 架构洞察（I）：insights.md ≥3 条四元组洞察（G2）
  - [ ] 2.3 撰写 concepts/（译本系统、五蕴/十二处/十八界、般若空性、心经与金刚经关系、历代注家立场等 5-6 篇）
  - [ ] 2.4 撰写 examples/（原文分段对照精读 1-2 篇）
  - [ ] 2.5 撰写 references/（底本信源、注本分级、交叉引用 3 篇）
  - [ ] 2.6 生成 bundle 根 index.md（`{toctree}` 引用全部）+ log.md
  - [ ] 2.7 萃取 ≥2 个可复用阅读模式（含触发场景/核心步骤/反模式/迁移示例，G3）写入 insights.md 或独立 patterns 记录

- [ ] Task 3：对抗审查（V）+ 原子提交（C）阶段一
  - [ ] 3.1 对抗审查：随机抽 10 条 facts.md 核对信源；核对《心经》原文全录逐字
  - [ ] 3.2 运行 `invoke gates.all`（UTF-8 + toctree）
  - [ ] 3.3 原子提交（子模块仓库内，Conventional Commits）

- [ ] Task 4：创建 `diamond-sutra/`（《金刚经》）bundle
  - [ ] 4.1-4.7 复用 Task 2 七步（52 分/32 分两译系说明、三十二品结构、四相/无住生心/应无所住等核心概念、历代注家、阅读模式萃取）
  - [ ] 4.8 对抗审查 + `invoke gates.all` + 原子提交

## 阶段二：禅宗

- [ ] Task 5：创建 `platform-sutra/`（《六祖坛经》）bundle
  - [ ] 5.1-5.7 复用 Task 2 七步（敦煌本/宗宝本区分、自性本自清净/顿悟法门、禅宗史立场标注、阅读模式萃取）
  - [ ] 5.8 对抗审查 + `invoke gates.all` + 原子提交

## 阶段三：净土 + 法华选读

- [ ] Task 6：创建 `amitabha-sutra/`（《阿弥陀经》）bundle
  - [ ] 6.1-6.7 复用 Task 2 七步（鸠摩罗什译、称名往生立场标注、三资粮、注家分级、阅读模式萃取）
  - [ ] 6.8 对抗审查 + `invoke gates.all` + 原子提交

- [ ] Task 7：创建 `lotus-sutra/`（《法华经》选读）bundle
  - [ ] 7.1-7.7 复用 Task 2 七步，但改为「结构总览 + 核心品（方便品/譬喻品/信解品/法师品等选读）+ 关键偈颂 + 选读计划」，不全文照录；《华严经》《楞严经》登记入 references 交叉引用
  - [ ] 7.8 对抗审查 + `invoke gates.all` + 原子提交

- [ ] Task 8：最终验证
  - [ ] 8.1 全量 `invoke gates.all` + `invoke build` 构建通过
  - [ ] 8.2 核对 `bundles/index.md` 统计数字与实际 bundle 数一致（291）
  - [ ] 8.3 `git status`/`git log` 核对全部变更已提交至子模块仓库

# Task Dependencies

- Task 2/4/5/6/7 均依赖 Task 1（分组骨架与导航就绪后才能落 bundle）。
- Task 3 依赖 Task 2；Task 4.8 依赖 Task 4；依此类推（每个 bundle 完成即提交）。
- Task 8 依赖 Task 2-7 全部完成。
- Task 2 与 Task 4 串行（先用心经验证模式，再复制到金刚经）；Task 5/6/7 可在模式验证后考虑并行（但每 bundle 独立提交，串行亦安全）。