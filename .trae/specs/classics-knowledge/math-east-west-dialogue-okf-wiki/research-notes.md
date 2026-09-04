# R 阶段调研笔记 — 中西数学对读知识包

> 采集时间：2026-09-01
> 调研工具：WebSearch（结果页面全文返回即视为内容验证通过）
> 用途：为 `kexue/math/east-west-dialogue` 知识包提供信源验证留痕
> 信源 ID 规划见本文件末尾；facts.md 与 references/ 均引用本清单

## 一、URL 验证清单

以下 URL 均于 2026-09-01 经 WebSearch 实际返回内容并核对（✅ = 内容匹配验证通过）。

| # | 信源 ID | URL | 验证结论 |
|---|---------|-----|---------|
| 1 | r-mactutor-ninechapters | https://mathshistory.st-andrews.ac.uk/HistTopics/Nine_chapters/ | ✅ 全文返回：246 题九章结构与欧氏《原本》角色对观、Chemla 证明观引述 |
| 2 | r-mactutor-chinese-overview | https://mathshistory.st-andrews.ac.uk/HistTopics/Chinese_overview/ | ✅ 全文返回：中国数学总览、无公理化发展、Cullen 对周髀勾股证明的质疑（via Needham 翻译争议） |
| 3 | r-mactutor-liuhui | https://mathshistory.st-andrews.ac.uk/Biographies/Liu_Hui/ | ✅ 全文返回：刘徽约 220–280、263 年注九章、"not exactly proofs in our understanding" |
| 4 | r-mactutor-jademirror | https://mathshistory.st-andrews.ac.uk/Extras/Jade_mirror/ | ✅ 全文返回：Jock Hoe 论《四元玉鉴》1303、Sarton 评价、Libbrecht/Lam Lay Yong 研究、九章最早负数记载 |
| 5 | r-chemla-sphere | https://sphere.cnrs.fr/chemla-karine/ | ✅ 全文返回：Chemla & Guo Shuchun《Les neuf chapitres》Dunod 2004 出版信息、CNRS-CAS 合作框架 |
| 6 | r-chemla-guo-2004 | https://www.sciamvs.org/files/SCIAMVS_07_213-218_Review_Horiuchi_On_Chemla_Guo.pdf | ✅ 全文返回：Horiuchi 书评确认 Dunod 2004、ISBN 2-10-007778-3、1117 页、术语词汇表 140+ 页 |
| 7 | r-needham-scc3 | https://www.cambridge.org/id/universitypress/subjects/history/history-science-and-technology/science-and-civilisation-china-volume-3 | ✅ 全文返回：SCC Vol.3《Mathematics and the Sciences of the Heavens and the Earth》CUP 1959、ISBN 9780521058018、与 Wang Ling 合作 |
| 8 | r-martzloff-1997 | https://www.mathematik.de/leseecke/geschichte/912-a-history-of-chinese-mathematics | ✅ 全文返回：Springer 1997 英文版（法文原版 1987 Masson）、2006 重印 ISBN 3-540-33782-2、485 页、按数学分支非编年组织 |
| 9 | r-cao-2025 | https://jdn.ucas.ac.cn/public/uploads/files/68f05ddb72880.pdf | ✅ 全文返回：曹婧博《〈几何原本〉第十卷汉译》自然辩证法通讯 47(11) 2025；1607 前六卷译毕刊刻、1857 后九卷、Billingsley 1570 底本、"界说/求作/公论/题"术语 |
| 10 | s-guoxuedashi-jhyb | https://www.guoxuedashi.com/SiKuQuanShu/bk101682c/ | ✅ 全文返回：四库百科《几何原本》条目——1606 起译、1607 刻印、克拉维乌斯拉丁文本、1857 韩应陛刊本、1865 金陵书局十五卷本 |
| 11 | r-siu-2013 | https://hkumath.hku.hk/~mks/MrOuChina_RevisedFinalDraft_MKSiu_Nov2013.pdf | ✅ 全文返回：萧文强 When "Mr. Ou (Euclid)" came to China——1607 译本历史语境、三次西学东渐浪潮框架 |
| 12 | r-chemla-roads | https://euromathsoc.org/magazine/articles/5 | ✅ 全文返回：Chemla "All roads come from China"——李冶《测圆海镜》1248 天元术、"celestial origin"（天元一）多项式位值记法 |

## 二、复用既有束已验证信源（不重复验证，链接指向）

以下信源在既有两束中已于 2026-08-30 验证，本束 references 以链接指向其登记页：

- 国外原文信源：Project Gutenberg（#21076/#21016/#78050）、Internet Archive、Gallica、Euler Archive、Perseus、Clay Institute、Fitzpatrick 希英对照《原本》 → 见 `classics-reading/references/original-sources.md`
- 中国原典信源：ctext.org（s-ctext-jiuzhang / s-ctext-zhoubi 等）、汉典古籍、中华文库、国学大师 → 见 `suanjing-reading/references/online-sources.md`
- 国外译本注本谱系：Heath、Bonola、Clarke 等 → 见 `classics-reading/references/translations-commentaries.md`
- 中国点校本：钱宝琮 1963、郭书春/刘钝 1998、白尚恕 1983 → 见 `suanjing-reading/references/core-editions.md`

## 三、信源 ID 规划（本束新增）

| 前缀 | 含义 | 本束新增 id |
|------|------|------------|
| s- | 一级原典/在线全文 | s-guoxuedashi-jhyb（国学大师四库条目）；复用 s-ctext-jiuzhang、s-ctext-zhoubi |
| e- | 二级点校/现代版本 | e-jihe-yuanben-15v（1865 金陵书局十五卷本，藏北京图书馆，作版本事实登记不作在线信源） |
| r- | 三级学术研究 | r-mactutor-ninechapters、r-mactutor-chinese-overview、r-mactutor-liuhui、r-mactutor-jademirror、r-martzloff-1997、r-chemla-guo-2004、r-chemla-sphere、r-chemla-roads、r-needham-scc3、r-cao-2025、r-siu-2013、r-libbrecht-1973（MIT Press 1973，出版信息经 r-mactutor-jademirror 交叉确认） |

## 四、关键事实采集记录（供 facts.md 展开）

1. 《九章》246 题、九章名目、《原本》13 卷 5 公设 5 公理 23 定义（卷一 48 命题）——r-mactutor-ninechapters、r-mactutor-chinese-overview
2. Chemla 证明观：中国数学家对其算法正确性有论证（反驳"无证明"旧说）——r-mactutor-ninechapters
3. Cullen 质疑周髀含勾股证明（归因 Needham 误译）——r-mactutor-chinese-overview
4. 刘徽约 220–280，263 年注九章；"not exactly proofs in our understanding"——r-mactutor-liuhui
5. 《九章·方程》含最早负数记载——r-mactutor-jademirror
6. 李冶《测圆海镜》1248，天元术多项式位值记法——r-chemla-roads
7. 朱世杰《四元玉鉴》1303、《算学启蒙》1299——r-mactutor-jademirror
8. SCC vol.3 1959 CUP 与王铃合作——r-needham-scc3
9. Martzloff 法文 1987 / 英文 1997 Springer——r-martzloff-1997
10. Chemla & Guo《Les neuf chapitres》Dunod 2004（1117 页，法译含刘徽注）——r-chemla-guo-2004
11. 1607 前六卷（利玛窦口译、徐光启笔受、克拉维乌斯底本）；1857 后九卷（伟烈亚力+李善兰、Billingsley 1570 底本、韩应陛刊本）；1865 金陵书局十五卷合刻——r-cao-2025、s-guoxuedashi-jhyb、r-siu-2013
12. 译名"界说/求作/公论/题"对应定义/公设/公理/命题，沿用至今并传日韩——r-cao-2025、s-guoxuedashi-jhyb
