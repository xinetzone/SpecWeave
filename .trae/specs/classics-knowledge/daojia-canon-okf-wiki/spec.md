---
name: daojia-canon-okf-wiki
version: 1.0.0
created: 2026-08-30
source: "公共领域道家经典原文与历代权威注疏（诸子原文属公共领域；解读依据公开学术专著、整理本与机构藏本）"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（道家经典原文属公共领域古籍，解读为公开学术知识）
---

# 道家著作全谱系调研与 OKF 知识包 Spec

## Why

用户要求「全面调研道家相关的著作」，获取「最权威、最真实」的原文与解读，并整理发布到 `projects/awesome-okf-xs/doc/bundles` 的恰当位置，生成 OKF wiki 教程。道家著作普遍存在**托名、伪书、成书年代与作者争议**（如《阴符经》托名黄帝、《列子》真伪之争、《文子》与《淮南子》关系），「权威与真实」必须通过**双信源逐字核对原文**与**诚实区分托名层/文本层**来保证，而非沿用单一流行文本或百科叙述。

经确认，范围取**全谱系通览**（先秦诸子 → 黄老之学 → 魏晋玄学注疏 → 道教经典四段谱系），落位采用**统一 `think/daojia/` 分组**，交付采用**先调研后定**（先产全谱系调研清单，经确认后再逐册入库）。

## What Changes

**Phase 0（本次可执行交付）——全谱系调研（R）：**
- 产出道家著作全谱系调研清单（`facts.md` 目录化登记），覆盖四段谱系、每部著作的：书名/托名作者/实际或推定年代/文本版本体系/核心思想/权威底本与注本/信源 URL/托名层与文本层标注
- 明确每部著作的「权威性评级」与「可入库底本」，为后续逐册 bundle 化提供事实基座

**Phase 1+（调研确认后逐册入库）——统一 `think/daojia/` 分组：**
- 新建 `bundles/think/daojia/index.md`（道家总纲：全谱系导航 + 源流谱系图 + toctree）
- 按著作逐册建立 bundle（`laozi/`、`zhuangzi/`、`liezi/`、`wenzi/`、`huangdi/`、`heguanzi/`、`guanzi/`、`huainanzi/`、`xuanxue-zhushu/`、`daojiao/` 等），每束含 `index.md` + `concepts/`/`examples/`/`references/` + `facts.md`/`insights.md`/`log.md`
- 更新 `bundles/think/index.md` 与 `bundles/index.md`（统计数字、分组表行、toctree）

**研究范围（调研清单目标，四段谱系）：**

| 谱系段 | 代表著作 |
|---|---|
| ① 先秦道家诸子 | 老子《道德经》*、庄子《南华真经》、列子《冲虚真经》、文子《通玄真经》、鹖冠子、关尹子《文始真经》、管子（心术上下/白心/内业） |
| ② 黄老之学 | 黄帝《阴符经》**、黄帝四经（经法/十大经/称/道原）、淮南子《淮南鸿烈》、尹文子、慎到·田骈（辑佚学说） |
| ③ 魏晋玄学注疏 | 王弼《老子注》《周易注》、河上公《老子章句》、严遵《老子指归》、郭象《庄子注》、成玄英《庄子疏》 |
| ④ 道教经典 | 周易参同契、抱朴子、太平经、黄庭经、太上老君说常清静经 |

> \* 老子已有 `think/laozi/boshu-reading` bundle；\** 《阴符经》已有 spec `create-yinfujing-okf-wiki`（未实现）。二者如何处理见「开放问题」。

## Impact

- Affected specs: `create-yinfujing-okf-wiki`（阴符经，未实现，拟并入本谱系）、`laozi-lineage-okf-bundle`、`boshu-laozi-wiki`（仅交叉引用，不修改其产物）
- Affected code: `projects/awesome-okf-xs`（git submodule，第一方子项目，允许子模块内开发）内 `doc/bundles/think/` 新增 `daojia/` 分组与索引更新；提交发生在子模块仓库内
- Phase 0 调研清单产出位于 `.trae/specs/classics-knowledge/daojia-canon-okf-wiki/`（不做公共入库动作）
- 不修改任何既有 bundle 内容（`think/laozi/boshu-reading` 是否迁移由「开放问题」裁决）；不修改 SpecWeave 主仓文件

## ADDED Requirements

### Requirement: 全谱系调研清单完整性

调研 SHALL 产出覆盖四段谱系（先秦诸子 / 黄老之学 / 魏晋玄学注疏 / 道教经典）的著作清单，每部著作至少登记以下元数据：书名（含通行名与别称）、托名作者、实际或学术推定年代、文本版本体系（出土/传世/道藏本）、核心思想一句话、权威底本与注本、信源 URL。

#### Scenario: 谱系覆盖

- **WHEN** 用户通读调研清单
- **THEN** 能看到四段谱系各有代表性著作覆盖，且先秦诸子段含庄子/列子/文子/鹖冠子/关尹子/管子，黄老段含黄帝四经/淮南子/尹文子，玄学段含王弼/郭象/成玄英，道教段含参同契/抱朴子/太平经/黄庭经/清静经

### Requirement: 权威信源可溯（双源核对）

每部著作的原文底本与解读 SHALL 标注权威可核查信源（学术专著、整理本、机构藏本/影印本、ctext.org 等公开整理本），禁匿名博客/百科帖/未注明出处的网络文本作为唯一来源；凡入库原文均须经至少两个独立权威信源逐字核对。

#### Scenario: 信源权威度

- **WHEN** 溯源任一著作的底本与解读
- **THEN** 每条信源具具体可核查出处（ISBN/机构 URL/藏本编号），无虚构引证

### Requirement: 托名层与文本层区分

调研 SHALL 对存在托名、伪书、成书年代争议的著作（如《关尹子》托名尹喜、《列子》真伪、`黄帝`系著作托名、《文子》与《淮南子》关系）显式标注「托名层/文本层」之别，不将托名当史实陈述，并列出主要学术学说及依据。

#### Scenario: 争议显式化

- **WHEN** 调研清单陈述某著作作者或年代
- **THEN** 有争议处列出 ≥2 种学术观点及代表依据，并以「学界推测/托名传说」区分，不给出单一确定性断言

### Requirement: 统一 daojia 分组 + OKF 格式

Phase 1+ 入库的知识包 SHALL 落位于 `bundles/think/daojia/` 统一分组，遵循 awesome-okf-xs 规范：OKF v0.2 YAML frontmatter（`type`、`source`、`generated`/`verified`、`status`、`stale_after`）、bundle 根 index 以 `{toctree}` 引用全部内容文档、Markdown 相对路径交叉引用无断链、正文中文/文件名 kebab-case 纯英文，并通过 `invoke gates.all`（UTF-8 + toctree 完整性）。

#### Scenario: 分组建制

- **WHEN** 在 `projects/awesome-okf-xs` 查看 `think/daojia/`
- **THEN** 存在总纲 index（含 toctree 引用全部子 bundle），子 bundle 各自根 index 完整

### Requirement: 方法论闭环（R→I→E→V→C）

全程 SHALL 记录 seven-concepts 场景4 方法论痕迹：`facts.md` 编号事实纯客观（G1，无因果词）；`insights.md` 四元组洞察（G2）；≥2 个可复用「经典判读/谱系重建」模式含触发场景/核心步骤/反模式/迁移示例（G3）；入库原文经对抗审查（V）双源抽查；变更经 atomic-commit 交付（C）。

#### Scenario: 质量门通过

- **WHEN** 各阶段产出经 G1-G4 检查
- **THEN** 事实无因果词、洞察四元组完整、模式可迁移、提交单一职责

### Requirement: 分阶段交付与确认点

交付 SHALL 分阶段推进，Phase 0 调研清单完成后设**确认点**（checkpoint）：向用户呈现全谱系清单与拟入库优先级/最终目录结构，经确认后方进入 Phase 1+ 逐册入库。

#### Scenario: 确认点

- **WHEN** Phase 0 调研清单完成
- **THEN** 暂停入库，等待用户确认入库范围、优先级与目录迁移决策

## MODIFIED Requirements

无（本任务为全新增量；`think/index.md` 与 `bundles/index.md` 仅追加统计与导航行，属索引维护而非既有需求变更）。

## REMOVED Requirements

无。

## 开放问题

1. **既有 `think/laozi/` 的去向**：采用统一 `daojia/` 分组后，是搬运 `think/laozi/boshu-reading` 至 `think/daojia/laozi/`（会改动既有链接与索引），还是 `daojia/` 通过 cross-ref 引用原地保留的 `laozi/`？——Phase 0 确认点裁决。
2. **《阴符经》spec 归属**：既有 spec `create-yinfujing-okf-wiki`（未实现）是否并入本谱系（`think/daojia/huangdi/yinfujing/`），还是独立生成为 `think/huangdi/`？——Phase 0 确认点裁决。
3. **「魏晋玄学注疏」与「道教经典」的 bundle 粒度**：是以「学派/注家」为一束（`xuanxue-zhushu/`）还是以「单部注本」为一束（`wangbi-laozizhu/`）？——Phase 0 清单提供结构建议，确认点裁决。
4. **道教经典的广度边界**：道教经典（道藏）体量极大，本次「全谱系通览」是否含善书类（太上感应篇）与科仪类，还是仅限影响深远的义理/丹道经典（参同契/抱朴子/太平经/黄庭经/清静经）？——Phase 0 清单提出建议边界，确认点裁决。