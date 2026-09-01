# Checklist

## 分组骨架与导航

- [ ] 新建 `doc/bundles/think/buddhism/index.md`，含一句话简介 + 5 bundle 列表表 + `{toctree}`
- [ ] `think/index.md` 新增「📖 佛家核心经典」分组行（table + toctree）
- [ ] `bundles/index.md` think 域描述与分组表新增佛家行
- [ ] `bundles/index.md` 统计数字更新为 291 束 / 33 组

## 译本系统与底本（每 bundle）

- [ ] 每部经标注译者、译经年代、《大正藏》卷次（No.），并说明梵文原典是否存世
- [ ] 原文全录经 ≥2 个独立信源逐字核对，异文处显式标注
- [ ] 关键异译/异文登记入 facts.md 编号事实

## 解读多元性与立场

- [ ] 般若系呈现 ≥2 种立场（中观空性/唯识/禅宗）
- [ ] 《坛经》区分敦煌本与宗宝本、标注禅宗史立场
- [ ] 《阿弥陀经》标注净土宗「称名往生」立场
- [ ] 每处引用注明注家与出处（窥基/憨山/印顺等）

## OKF 格式与导航

- [ ] 所有新增 `.md` 含 OKF v0.2 frontmatter（type/sources/generated/verified/status/stale_after）
- [ ] 每个 bundle 根 index.md 以 `{toctree}` 引用全部内容文档
- [ ] 正文中文、文件名 kebab-case 纯英文
- [ ] 交叉引用相对路径无断链
- [ ] `invoke gates.all`（UTF-8 + toctree）通过

## 方法论闭环（七概念场景4）

- [ ] 每 bundle facts.md ≥25 条编号事实、无因果推断词（G1）
- [ ] 每 bundle insights.md ≥3 条四元组洞察（G2）
- [ ] 每 bundle ≥2 个可复用阅读模式（触发/步骤/反模式/迁移）（G3）
- [ ] 提交前经对抗审查（V）随机抽 10 条 facts 核对信源

## 交付与提交

- [ ] 5 个 bundle 全部创建：heart-sutra / diamond-sutra / platform-sutra / amitabha-sutra / lotus-sutra
- [ ] 每个 bundle 原子提交至子模块仓库
- [ ] `invoke build` 构建通过，无 Sphinx 报错
- [ ] `git log` 核对全部变更已提交