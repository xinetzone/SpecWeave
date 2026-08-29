---
type: Methodology Pattern
title: 避讳断代法
description: 以帝讳改字为相对年代标尺，结合多重讳字组合与书体、出土语境交叉验证的出土/传世抄本断代方法
tags: [laozi, methodology, taboo, 避讳, 断代, 出土文献, 校勘学]
generated: { by: extraction_agent/trae-glm, at: 2026-08-20T14:30:00Z }
verified: { by: process:seven-concepts-EV, at: 2026-08-20T14:50:00Z }
status: stable
sources:
  - id: gao-ming-boshu-jiaozhu
    resource: "../references/gao-ming-boshu-jiaozhu.md"
    title: 帛书老子校注
    author: human:高明
  - id: mawangdui-hanmu-boshu-yi
    resource: "../references/mawangdui-hanmu-boshu-yi.md"
    title: 马王堆汉墓帛书（壹）
    author: team:国家文物局古文献研究室
  - id: beida-han-jian-er
    resource: "../references/beida-han-jian-er.md"
    title: 北京大学藏西汉竹书（贰）
    author: team:北京大学出土文献研究所
  - id: taboo-bang-guo
    resource: "../variants/taboo-bang-guo.md"
    title: 邦/国避讳异文
    author: team:laozi-lineage
  - id: taboo-heng-chang
    resource: "../variants/taboo-heng-chang.md"
    title: 恒/常避讳异文
    author: team:laozi-lineage
  - id: mawangdui-jia
    resource: "../manuscripts/mawangdui-jia.md"
    title: 马王堆帛书《老子》甲本
    author: team:laozi-lineage
  - id: mawangdui-yi
    resource: "../manuscripts/mawangdui-yi.md"
    title: 马王堆帛书《老子》乙本
    author: team:laozi-lineage
  - id: beida-han-jian
    resource: "../manuscripts/beida-han-jian.md"
    title: 北大汉简本《老子》
    author: team:laozi-lineage
  - id: guodian-chu-jian
    resource: "../manuscripts/guodian-chu-jian.md"
    title: 郭店楚简本《老子》
    author: team:laozi-lineage
---

# 避讳断代法

避讳断代法是以抄本中帝讳字的回避或改易为相对年代标尺，对无明确纪年的出土简帛与传世抄本推定抄写年代区间的校勘学方法。该方法将讳字视为一种"时代水印"，但须以多重讳字组合与外部证据交叉验证，不宜单凭一字定时代。[^gao-ming-boshu-jiaozhu][^mawangdui-hanmu-boshu-yi]

## 触发场景

- 出土简帛、敦煌写卷或传世抄本无直接纪年材料，需推定抄写年代的相对早晚。[^mawangdui-hanmu-boshu-yi]
- 同一墓葬或同一收藏单位所出多本用字系统不同（如甲本用"邦"、乙本用"国"），需判定其抄写先后。[^gao-ming-boshu-jiaozhu]
- 文本中出现帝讳字或其代字（如"邦/国""恒/常""盈/满""启/开""彻/通"），需定位讳令施行的时间节点。[^taboo-bang-guo][^taboo-heng-chang]
- 讳字组合与据书体、器物推定的年代之间出现张力（如某本避"邦"而不避"彻"），需复核既有断代。[^beida-han-jian]
- 后世校勘本、仿古本保留或回改古字，需辨识讳字的层位与真伪。[^gao-ming-boshu-jiaozhu]

## 核心步骤

1. **建讳字表**：据抄本可能涉及的朝代，列出帝王名讳及其常见代字、嫌名、二名偏讳规则。汉代重点字包括"邦（高祖）、盈（惠帝）、恒（文帝）、启（景帝）、彻（武帝）"等，秦代另有"楚/荆、政/正"等系统。[^mawangdui-hanmu-boshu-yi]
2. **逐字普查**：对全文作穷尽式讳字统计，逐项记录讳字（应讳而未讳）与代字（已讳）的位置、频次与语境，区分专名（人名、地名、官名）、常语、引文与哲学概念词（如《老子》"恒道""恒名"）。[^gao-ming-boshu-jiaozhu][^taboo-heng-chang]
3. **定避讳向量**：将"已讳/未讳"诸帝讳汇成有序组合。例如甲本为（邦未讳、恒未讳），乙本为（邦已讳、恒未讳），北大汉简本为（邦已讳、盈未讳、恒未讳、启未讳、彻未讳）。[^mawangdui-jia][^mawangdui-yi][^beida-han-jian]
4. **嵌年代区间**：以帝讳即位或诏令颁行年份为节点，将避讳向量映射为年代区间。避某帝讳提供抄写"晚于该节点"的参照，不避某帝讳提供"早于该讳严格施行"的参照；输出区间而非单点年代。[^mawangdui-hanmu-boshu-yi]
5. **交叉验证**：与书体（篆隶、古隶、成熟汉隶、八分）、出土纪年物（同墓纪年简、有铭器物）、考古类型学、同卷佚书与同篇他处讳例相互比对。[^gao-ming-boshu-jiaozhu][^beida-han-jian-er]
6. **记弹性与张力**：标注地区执行时滞、抄手随意漏改、仿古保留旧字、后世回改等不确定因素；讳字组合与所推年代冲突时，将张力显题化并列待决，不取一端。[^taboo-bang-guo][^beida-han-jian]
7. **输出证据链**：按"讳字—代字—频次—帝讳节点—交叉证据—年代区间"格式记录结论，每条断代言之有故，脚注指向原整理本与图版。[^mawangdui-hanmu-boshu-yi][^gao-ming-boshu-jiaozhu]

## 反模式

魔鬼代言人视角下，避讳断代法至少存在以下具体陷阱：

1. **"不避讳≠本子早"**。将"未避某帝讳"直接等同于"抄写早于该帝即位"，忽略三种常见情形：抄手随意漏改或疏忽；好古之抄手、校勘者仿古本保留旧字而不讳旧朝之讳；边远地区（如汉初长沙国）对中央讳令存在执行时滞，诏令到达与实际改字并不同步。傅奕本为唐代校定本，第五十四章等位置仍保留"邦"字，其"邦"字系所据古本面貌，不能据此判定唐本早于汉初。[^gao-ming-boshu-jiaozhu][^taboo-bang-guo]
2. **"避讳回改"使讳字层位失真**。后世校勘者或抄手据古本将讳字回改（"国"回改"邦"、"常"回改"恒"），或注疏本以古字补正，回改之字与原讳未改之字在字形上无从分别。仅凭单字无法判定该字属"原未避讳"还是"后世回改"，须结合该本版本源流、所据底本系统与校本关系综合判断。[^taboo-bang-guo][^gao-ming-boshu-jiaozhu]
3. **单字断代而不做多重讳字交叉验证**。只凭一个讳字定年代，回避讳字组合内部的张力。北大汉简本避"邦"讳作"国"，却仍用"盈""恒""启""彻"等字，若抄写于武帝时期，按例应避"彻"字，该避讳组合与整理者推定的武帝年代之间存在张力；单看"邦已讳"可将本子置于高祖以后任意时点，单看"彻未讳"又可置于武帝以前，须综合书体、同批"孝景元年"纪年简与文本形态作多重验证，并将张力保留为开放问题。[^beida-han-jian][^beida-han-jian-er]
4. **把通假与义近替换一律当作讳改**。如"恒""常"在汉语中词义本有重叠，某一"常"字未必皆出避讳，亦可能为同义换读或传抄异文；判定讳改须有同书系统性改易的证据，而非孤立字例。[^taboo-heng-chang][^gao-ming-boshu-jiaozhu]

## 迁移验证

该方法可迁移至《老子》之外的秦汉出土简帛。以马王堆帛书《老子》乙本卷前佚书《经法》《十六经》《称》《道原》（后世学者或称《黄帝四经》）为例：四篇佚书与乙本《老子》同抄于一卷帛上，书体同属成熟汉隶，其避讳情况可与乙本《老子》互相校准。[^mawangdui-hanmu-boshu-yi]

具体应用：

1. 先建西汉早期讳字表，对四篇佚书逐字普查"邦/国""恒/常""盈""启""彻"，记录各自避讳向量；
2. 将佚书向量与乙本《老子》（邦已讳、恒未讳）比对，观察是否出同时段抄手之手；
3. 结合卷中语词、谥法与书体特征，推定佚书抄写的相对年代区间；
4. 与唐兰等学者对佚书成书与抄写年代的考辨互校，报告讳字证据与思想史证据的异同。[^mawangdui-hanmu-boshu-yi]

同一方法亦可施于帛书《周易》、银雀山汉简、睡虎地秦简等秦汉抄本，操作时须替换讳字表（秦讳、汉讳、三国吴讳、唐讳各不相同），并注意出土语境与地域因素。

## 在《老子》谱系中的应用

本 bundle 已为避讳断代法提供了由两个异文簇构成的完整案例：

- **马王堆帛书甲本**：可辨"邦"字约二十二处，第五十四章"修之于邦""以邦观邦"、第八十章"小邦寡民""邻邦相望"均作"邦"；第一章"道可道也，非恒道也"作"恒"。避讳向量为（邦未讳、恒未讳），与古隶书体互证，学界推定其抄写约在秦汉之际、高祖避讳严格施行以前。[^mawangdui-jia][^taboo-bang-guo][^taboo-heng-chang]
- **马王堆帛书乙本**：甲本所见"邦"字俱改作"国"，对应处作"修之于国""以国观国""小国寡民""邻国相望"，而第一章仍作"非恒道也"。避讳向量为（邦已讳、恒未讳），与成熟汉隶书体互证，学界推定其抄写在高祖称帝之后、文帝即位以前（约惠帝至吕后期）。[^mawangdui-yi][^taboo-bang-guo][^taboo-heng-chang]
- **甲、乙同墓而讳字组合不同**，构成甲本早于乙本的核心相对年代证据链；该证据链与书体差异（甲本篆隶之间、乙本成熟汉隶）相互印证。[^mawangdui-hanmu-boshu-yi][^gao-ming-boshu-jiaozhu]
- **北大汉简本**：不用"邦"字而相应位置作"国"，仍见"盈""恒""启""彻"，避讳向量为（邦已讳、盈恒启彻未讳）。该组合与整理者推定的武帝时期年代存在张力，本 bundle 在异文与传本文档中均将此张力列为待决问题，不以单一讳字下断语。[^beida-han-jian][^taboo-bang-guo]
- **郭店楚简本**：下葬于战国中期偏晚楚墓，不涉汉代帝讳，"邦""恒"均存其旧，提供汉代讳改以前的用字基线。[^guodian-chu-jian]
- **传世本系统**（河上公本、王弼本等）"邦→国""恒→常"俱已完成，其讳字层位经历代传刻叠加，又有傅奕本等仿古本保留古字，避讳断代时须先辨版本源流与回改，不作单一断代依据。[^taboo-bang-guo][^taboo-heng-chang]

相关异文与传本详见[邦/国避讳异文](../variants/taboo-bang-guo.md)、[恒/常避讳异文](../variants/taboo-heng-chang.md)、[马王堆帛书甲本](../manuscripts/mawangdui-jia.md)、[马王堆帛书乙本](../manuscripts/mawangdui-yi.md)、[北大汉简本《老子》](../manuscripts/beida-han-jian.md)。

[^gao-ming-boshu-jiaozhu]: 高明撰《帛书老子校注》，中华书局1996年版，ISBN 9787101013436。
[^mawangdui-hanmu-boshu-yi]: 国家文物局古文献研究室编《马王堆汉墓帛书（壹）》，文物出版社1980年版，统一书号7068·380。
[^beida-han-jian-er]: 北京大学出土文献研究所编、韩巍整理《北京大学藏西汉竹书（贰）》，上海古籍出版社2012年版，ISBN 9787532560998。
[^taboo-bang-guo]: 本 bundle 异文概念 [邦/国避讳异文](../variants/taboo-bang-guo.md)。
[^taboo-heng-chang]: 本 bundle 异文概念 [恒/常避讳异文](../variants/taboo-heng-chang.md)。
[^mawangdui-jia]: 本 bundle 传本概念 [马王堆帛书《老子》甲本](../manuscripts/mawangdui-jia.md)。
[^mawangdui-yi]: 本 bundle 传本概念 [马王堆帛书《老子》乙本](../manuscripts/mawangdui-yi.md)。
[^beida-han-jian]: 本 bundle 传本概念 [北大汉简本《老子》](../manuscripts/beida-han-jian.md)。
[^guodian-chu-jian]: 本 bundle 传本概念 [郭店楚简本《老子》](../manuscripts/guodian-chu-jian.md)。
