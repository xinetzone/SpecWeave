# 道家著作全谱系调研·目录结构与优先级建议（Structure Proposal）

> 依赖：facts.md（Task 1）+ insights.md（Task 2）+ patterns.md（Task 3）
> 用途：Phase 0 确认点（Task 5）的决策输入——待用户确认后进入 Phase 1+
> 落位根目录：`projects/awesome-okf-xs/doc/bundles/think/daojia/`

---

## 一、子 bundle 结构建议（段—家—著三级，P-004）

```
think/daojia/
├── index.md                       # 总纲：谱系图(mermaid) + 四段导航 + toctree
├── zhuzi/                         # ① 先秦道家诸子
│   ├── index.md
│   ├── laozi/                     # 老子（cross-ref 既有 think/laozi/boshu-reading）
│   ├── zhuangzi/                  # 庄子
│   ├── liezi/                     # 列子
│   ├── wenzi/                     # 文子
│   ├── heguanzi/                  # 鹖冠子
│   ├── guanyinzi/                 # 关尹子
│   └── guanzi/                    # 管子·道家四篇
├── huanglao/                      # ② 黄老之学
│   ├── index.md
│   ├── yinfujing/                 # 阴符经（并入既有 spec）
│   ├── huangdi-sijing/            # 黄帝四经
│   ├── huainanzi/                 # 淮南子
│   ├── yinwenzi/                  # 尹文子
│   └── shendao-tianpian/          # 慎到·田骈（辑佚）
├── xuanxue/                       # ③ 魏晋玄学注疏
│   ├── index.md
│   ├── wangbi/                    # 王弼（老子注/周易注）
│   ├── heshanggong/               # 河上公章句
│   ├── yanzun/                    # 严遵指归
│   ├── guoxiang/                  # 郭象庄子注
│   └── chengxuanying/             # 成玄英庄子疏
└── daojiao/                       # ④ 道教经典
    ├── index.md
    ├── cantongqi/                 # 周易参同契
    ├── baopuzi/                   # 抱朴子内篇
    ├── taipingjing/               # 太平经
    ├── huangtingjing/             # 黄庭经
    └── qingjingjing/              # 太上老君说常清静经
```

每部 bundle 内部结构（遵循 awesome-okf-xs 规范）：
`index.md`（toctree）+ `concepts/` + `examples/` + `references/` + `facts.md` + `insights.md` + `log.md`

---

## 二、开放问题的裁决建议

1. **既有 `think/laozi/boshu-reading` 的去向**（开放问题1）
   - 建议：**原地保留 + cross-ref**，不物理迁移。
   - 理由：`boshu-reading` 主题聚焦「帛书研读」这一特定角度，与「老子全谱系概览」主题不同；物理迁移会改动既有链接与索引，成本高、收益低。
   - 落地：`think/daojia/zhuzi/laozi/` 新建薄层 bundle，其 references 层 cross-ref 到既有 `think/laozi/boshu-reading`。

2. **《阴符经》spec 归属**（开放问题2）
   - 建议：**并入本谱系** `think/daojia/huanglao/yinfujing/`，归档（或废弃）独立 spec `create-yinfujing-okf-wiki`，避免重复建设。

3. **玄学注疏 bundle 粒度**（开放问题3）
   - 建议：**以「注家」为一束**（`wangbi/`、`guoxiang/`、`chengxuanying/` 等分列）。
   - 理由：每部注本是独立思想史文献，注家立场差异大，合并为单束会丢失主题边界。

4. **道教经典广度边界**（开放问题4）
   - 建议：**仅限义理/丹道经典 5 部**（参同契/抱朴子/太平经/黄庭经/清静经），暂不含善书类（太上感应篇）与科仪类。

---

## 三、入库优先级建议

> 排序依据：权威性评级（A＞B＞C）+ 思想史影响力 + 是否已有既有 bundle。

| 优先级 | 著作 | 权威性 | 理由 |
|---|---|---|---|
| P0（先做） | 老子 | A | 谱系总纲入口；多版本体系；cross-ref 既有 boshu-reading |
| P0 | 庄子 | A | 影响最深；郭庆藩集释权威 |
| P0 | 淮南子 | A | 集道家大成；何宁集释权威 |
| P0 | 黄帝四经 | A | 出土孤本；改写黄老认知 |
| P0 | 抱朴子内篇 | A | 道教方术集大成；葛洪自序确证 |
| P1（次做） | 列子 | B | 辨伪焦点；杨伯峻集释 |
| P1 | 文子 | B | 出土翻案典型 |
| P1 | 鹖冠子 | B | 黄老衔接 |
| P1 | 管子·四篇 | B | 稷下黄老 |
| P1 | 河上公章句 | B | 道教选刊 |
| P1 | 严遵指归 | B | 玄学先声 |
| P1 | 太平经 | B | 王明合校 |
| P2（后做） | 关尹子 | C | 伪托争议大 |
| P2 | 阴符经 | C | 并入既有 spec |
| P2 | 尹文子 | C | 真伪争议 |
| P2 | 慎到·田骈 | C | 辑佚残本 |
| P2 | 周易参同契 | C | 丹道、作者争议 |
| P2 | 黄庭经 | C | 托名、成书争议 |
| P2 | 清静经 | C | 短经、托名 |

---

## 四、需用户确认的决策点汇总

1. 是否采用「段—家—著三级 + 四段分组」目录结构（见第一节）？
2. 既有 `think/laozi/boshu-reading`：原地保留 + cross-ref（建议）还是物理迁移？
3. 《阴符经》spec：并入本谱系（建议）还是独立生成？
4. 玄学注疏粒度：按注家分列（建议）还是合并单束？
5. 道教经典边界：仅义理/丹道 5 部（建议）还是扩充善书/科仪类？
6. 入库优先级：P0→P1→P2（建议，见第三节）是否认可？