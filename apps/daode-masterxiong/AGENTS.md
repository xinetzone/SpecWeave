# AGENTS.md — 道德大师兄 AI 协作入口

> 本文档是路由索引，不包含具体规范。根据需求选择性阅读子模块。

---

## 项目身份

**道德大师兄**：以帛书《老子》为哲学根基的微信小程序品牌。道德即得到，大道自然，追求质朴。大师兄是先走一步、回头拉你一把的人。

当前阶段：品牌规划已完成，产品设计文档已落地到产品站。

---

## 文件地图

```
apps/daode-masterxiong/            ← 本目录（规范层）
├── README.md                      # 品牌入口说明
├── AGENTS.md                      ← 本文件（路由索引）
└── .agents/
    ├── README.md                  # 规范资产索引
    └── rules/
        ├── brand-redlines.md      # 品牌红线（18条）
        └── content-guidelines.md # 内容规范

projects/daoapps.github.io/       ← 产品站（产品层）
└── doc/jieban/design/            # 产品设计文档
    ├── PLAN.md                   # 品牌蓝图总览（三环闭环+MVP路径）
    ├── brand-positioning.md      # 品牌定位（命名哲学、简介、视觉、类目）
    ├── closed-loop.md             # 三环闭环详细设计
    └── channels/
        ├── zhizu.md               # 知足·心（好事墙）
        ├── hengyu.md              # 恒与·伴（同行故事墙）
        ├── zhihe.md               # 知和·家（经验墙）
        └── yuduo.md               # 愈多·业（案例本）
```

---

## 路由索引

| 需要了解 | 阅读文件 | 位置 |
|---------|---------|------|
| 什么绝对不能做 | [.agents/rules/brand-redlines.md](.agents/rules/brand-redlines.md) | 本目录 |
| 帛书引文使用规范、内容边界 | [.agents/rules/content-guidelines.md](.agents/rules/content-guidelines.md) | 本目录 |
| 品牌整体定位、命名哲学、简介结构 | `brand-positioning.md` | 产品站 design/ |
| 三环闭环设计（结伴/学习/变现） | `closed-loop.md` | 产品站 design/ |
| 四频道具体内容设计 | `channels/` | 产品站 design/ |
| MVP 路径与里程碑 | `PLAN.md` | 产品站 design/ |

---

## 关联外部资产

| 资产 | 位置 | 关系 |
|------|------|------|
| 道用组织站点 | `projects/daoapps.github.io/` | 品牌主站，Sphinx 构建 GitHub Pages |
| 结伴子站（主推） | `projects/daoapps.github.io/doc/jieban/` | 小程序第一阶段落地页 |
| 学习实验室 | `projects/daoapps.github.io/doc/xuexi/` | 学习闭环产品（待建） |
| 复盘站 | `projects/daoapps.github.io/doc/fupan/` | 第三子站（待建） |
| 结伴之旅小程序 | `apps/jieban-zhilv-mp/` | 不同小程序（活动报名），勿混淆 |

---

## P0 约束速览

1. **名称不动**：道德大师兄，不加品类后缀
2. **三环顺序不可反**：结伴（人）→ 学习（学）→ 变现（钱）
3. **不卖课、不做训练营、不卖会员**
4. **邀请制是筛选，不是限制**
5. **反杀猪盘、反收费导流**
6. **不催婚、不打分、不围观**
7. **不设表单、不收集个人信息**

详细红线见 [.agents/rules/brand-redlines.md](.agents/rules/brand-redlines.md)。
