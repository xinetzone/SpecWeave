# Checklist — 《鬼谷子》OKF 知识包

## 内容正确性
- [x] 现存篇目原文全录（道藏本十二篇 + 本经阴符七术 + 中经 + 持枢残篇）与至少 2 个独立权威信源逐字一致（ctext.org 四部丛刊本 + 正统道藏本双列，已抽查捭阖/反應/抵巇逐字复核）
- [x] 亡佚篇目（转丸、胠乱）已存目说明，未构拟补全；持枢残篇如实标注
- [x] 书志著录源流准确（汉书未著录 → 隋书首录 → 新唐书），对应卷次与注家无误
- [x] 托名传说（鬼谷子著、苏秦张仪之师）与学术成书年代学说明确区分，未混淆
- [x] 成书/作者各学说均标注依据文献（《史记》、柳宗元、钱穆、余嘉锡等）
- [x] 核心句解读均呈现传统注家与现代校注对照且出处可溯（无据注家评语统一标注"待考"）

## 方法论质量门
- [x] G1：facts.md 42 条编号事实，纯客观描述（无"因为/导致/所以"），每条带信源 URL
- [x] G2：insights.md 4 条四元组洞察（现象+根因+影响+建议）
- [x] G3：2 个可复用阅读模式，各含触发场景/核心步骤/反模式/迁移示例
- [x] V：原文抽查 ≥7 处（捭阖/反應/抵巇逐字对照）+ 事实抽查通过

## OKF 格式与结构
- [x] 全部新增文档 frontmatter 符合 OKF v0.2（type/generated/verified/status/stale_after）
- [x] bundle 根 index.md 及各子目录 index.md 均含 toctree 且引用全部文档（gates toctree 对 guiguzi 0 错误）
- [x] 文件名 kebab-case 纯英文；正文中文；交叉引用为相对路径无断链、无 file:///
- [x] `bundles/think/guiguzi/` 分组 index 与 toctree 完整
- [x] `bundles/think/index.md` 与 `bundles/index.md` 统计数字、分组表行、toctree 已同步更新

## 交付验证
- [x] `invoke gates.all`（在 projects/awesome-okf-xs）：utf8 + toctrees 均通过（guiguzi 0 错误；整体 29 处失败均来自其它在建 bundle，非本 bundle 原因）
- [ ] 原子提交完成且符合 Conventional Commits；主仓 gitlink 同步处理妥当（待用户确认后执行）