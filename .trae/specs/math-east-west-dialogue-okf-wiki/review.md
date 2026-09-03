# 中西数学对读教程（east-west-dialogue）独立对抗审查报告

- **审查对象**：`projects/awesome-okf-xs/doc/bundles/kexue/math/east-west-dialogue/`（index/facts/insights/log + concepts 9 篇 + examples 3 篇 + references 3 篇，共 20 文件全部通读）
- **审查者**：独立对抗审查者（fresh reviewer，与写作者无关）
- **审查日期**：2026-09-01
- **方法论**：七阶段工作流 V 阶段四视角对抗审查（事实溯源 / 结构规范 / 读者可用性 / 时效边界）+ 独立 Web 检索复核（MacTutor 四页、Cambridge 出版页、CNRS SPHERE、SCIAMVS 书评 PDF、ctext、国学大师等实测抓取）+ 全部数学验算手工复算 + 相对链接逐条目录实测（LS/Glob 核对目标文件存在性）

---

## ① 审查范围与方法

| 审查维度 | 手段 | 覆盖 |
|---------|------|------|
| 事实性证伪 | MacTutor（Nine_chapters / Chinese_overview / Liu_Hui / Zhu_Shijie）逐字比对；Cambridge、Springer（Archive.org 扫描件）、Dunod（SCIAMVS 书评）、ctext、国学大师、Historia Mathematica（Xu 2005）独立检索 | 26+ 项关键事实（facts.md F-001~F-043 全扫描，重点项逐条复核） |
| 信源可达性 | WebFetch 实测 4 个新增外部 URL + 顺带实测 7 个复用/登记 URL | 11 个 URL |
| 中立性 | 通读 concepts/00、07 与 insights.md，逐条检查时代错置/单线进化/文化优越论/以先后当传承 | 全包正文 |
| 数学正确性 | examples 三篇逐步手工验算（含消元三步、Cramer 三分子式、弦图两种摆法、π 全部数值界） | 全部计算 |
| 结构与链接 | 四层结构逐篇核对；跨束相对链接按目录层级实测（LS/Glob）；复制嫌疑句抽查 | concepts 03–08 全部 + 抽查 8 条跨束链接 |

---

## ② 事实复核表

结论口径：**PASS**＝与独立权威信源一致；**WARN**＝主体成立但表述欠精确或无法完全独立复核；**FAIL**＝与权威信源矛盾或不可达。

| # | 事实（facts.md 编号） | 独立信源（本次实测） | 结论 |
|---|----------------------|---------------------|------|
| 1 | F-001《原本》约前 300 年、13 卷；卷一 23 定义/5 公设/5 公理/48 命题 | 几何原本百科条目（同口径逐项一致）+ 通识 | PASS |
| 2 | F-002《九章》246 题、九章名目（方田…句股）、问答术结构 | MacTutor Nine_chapters（"246 problems"）+ chinaculture 九章英文名映射 | PASS |
| 3 | F-003 ctext 标注约公元前 120—公元 20 年；刘徽自序张苍/耿寿昌；成书无定论 | ctext.org/nine-chapters/zhs 逐字命中（"西汉 - 新 公元前120年-20年"）；MacTutor 序文引录一致 | PASS |
| 4 | F-004 刘徽约 220–280、魏人、无正史传记 | MacTutor Liu_Hui（Born about 220 / Died about 280 / Kingdom of Wei / "nothing is known of his life"） | PASS |
| 5 | F-006 李冶（1192–1279）1248《测圆海镜》天元术 | MacTutor Chinese_overview（Li Zhi…1192-1279…written in 1248…tian yuan） | PASS（"刊"字欠精确，见 WARN-5） |
| 6 | F-007 朱世杰《算学启蒙》1299、《四元玉鉴》1303 | MacTutor Zhu_Shijie / Chinese_overview 双页一致 | PASS |
| 7 | F-009 阿基米德正 96 边形，3+10/71 < π < 3+1/7 | 通识级标准结论；MacTutor 刘徽页反向印证（"He did not, like Archimedes, find bounds by using an inscribed as well as a circumscribed circle"） | PASS |
| 8 | F-010 刘徽 263 年注《九章》，正六边形倍增至 192 边形，徽率 157/50=3.14 | MacTutor Liu_Hui（263 AD；192 边形 3.141452472 在迭代表内）+ 中算史通说 | PASS |
| 9 | F-013/F-023 遍乘直除与高斯消元等价、独立起源 | MacTutor Nine_chapters 逐字（"augmented matrix…as is done today in the method of Gaussian elimination"） | PASS |
| 10 | F-014/F-018《方程》正负术为世界最早负数系统记载之一；丢番图亦有痕迹、影响无定论 | Shanghai Daily/Biola（"introduced negative numbers for the first time in the world"/"first known use"）+ MacTutor（"Negative numbers are used…the chapter includes rules to compute with them"） | PASS（bundle 的并列限定式表述比单源更严谨） |
| 11 | F-019 祖冲之（429–500）π ∈ (3.1415926, 3.1415927)、密率 355/113、约率 22/7；欧洲 16 世纪方达同等精度 | MacTutor Chinese_overview 逐字（"3.1415926 < π < 3.1415927…355/113…22/7"） | PASS |
| 12 | F-020 勾股证明归属两说并列：传统观点弦图构成证明；Cullen 认为该信念基于 Needham 缺陷翻译 | MacTutor Chinese_overview 逐字（"Cullen…disputes this, claiming that the belief is based on a flawed translation given by Needham"） | PASS |
| 13 | F-022 物不知数见于《孙子算经》；秦九韶 1247 大衍总数术；高斯 1801 同余一般理论；传播无文献证据 | MacTutor（Sun Zi about 400–460 "earliest known occurrence"；Qin Jiushao 1247） | PASS |
| 14 | F-024 1606 年起利玛窦口译、徐光启笔受，克拉维乌斯拉丁《原本 15 卷》底本，1607 年（万历三十五）春刻印 | 国学大师四库条目逐字命中 + 莫德版本研究（Clavius, Rome 1574）+ 中研院数学传播（1606 年 9 月起译） | PASS |
| 15 | F-025 界说/求作/公论/题 译名沿用至今并传入日韩 | 国学大师条目（"许多译名沿用至今，并传播到日、韩等国"） | PASS |
| 16 | F-027 1852 年起伟烈亚力（1815–1887）与李善兰（1811–1882）合作，Billingsley 1570 英译本底本，1856 译毕，1857 韩应陛刊刻 | **Xu Yibao, Historia Mathematica 32 (2005) 4–32**（"between the years 1852 and 1856…published in 1857…the first English translation of 1570 by Henry Billingsley was the actual source"）+ 国学大师（生卒、年份逐项一致） | PASS |
| 17 | F-028 1865（同治四年）金陵书局合刻十五卷全本，藏北京图书馆 | 国学大师/澎湃/经济日报一致（1865，曾国藩支持，金陵刊刻） | PASS（加分项：国学大师原文将同治四年误标"(1858)"，bundle 取正确值 1865，未照搬源文错误） |
| 18 | F-029 明清中算家几何著述清单（方中通 1661/李子金 1679/杜知耕/梅文鼎） | 国学大师条目逐字一致 | PASS |
| 19 | F-032/F-033/F-034/F-035/F-037 MacTutor 五条表述（无公理化发展/角色相似但证明概念不同/"not exactly proofs"/Chemla 修正/畴人） | MacTutor 四页逐字核对，全部命中（含"chouren refers to both mathematicians and astronomers"） | PASS |
| 20 | F-038 Needham SCC Vol.3，CUP 1959，与王铃合作，ISBN 9780521058018 | Cambridge 出版页实测（Published January 1959；ISBN 9780521058018；"Mathematics and the Sciences of the Heavens and the Earth"） | PASS（页面 Author 栏仅列 Needham，王铃合作为学界通识，可保留） |
| 21 | F-039 Martzloff 法文 1987 Masson；英文 Springer 1997；2006 重印 ISBN 3-540-33782-2；485 页 | Wisconsin 图书馆目录（Springer [1997], xxiv, 485 pages）+ 2006 重印本扫描件版权页（"Histoire des mathématiques chinoises. © Masson, Paris 1987"；"ISBN-10 3-540-33782-2"） | PASS |
| 22 | F-040 Chemla & 郭书春，Dunod 2004，ISBN 2-10-007778-3，1117 页，词汇表逾 140 页，CNRS–中科院二十余年合作 | SCIAMVS 7 (2006) 书评 PDF 逐字（"Paris (Dunod). 2004. ISBN 2-10-007778-3. XVII+1117 pp."；"glossary of more than 140 pages"；"more than twenty years collaboration"；SPHERE 页"l'accord cadre CNRS-CAS"） | PASS |
| 23 | F-041 Libbrecht 1973（MIT Press）专题研究 | 通识级书目事实（1973 年出版正确；出版社 MIT Press 正确） | PASS |
| 24 | F-042 Horiuchi 书评："任何从事中国数学史研究的历史学家都不能忽视这部著作" | SCIAMVS PDF 原句（"…this book which no historian engaged in the history of Chinese mathematics can ignore"） | PASS（译文忠实） |
| 25 | F-043 Chemla 2021 获 LMS/BSHM Hirst Prize；ERC SAW 项目研究古代世界数学文化多样性 | CNRS SPHERE 主页逐字（"2021 : Hirst Prize and Lectureship, London Mathematical Society and British Society for the History of Mathematics"；"Mathematical Sciences in the Ancient World (SAW)"） | PASS |
| 26 | F-008 Sarton《Introduction》卷三（1947–48）第 703 页评《四元玉鉴》 | 登记页 r-mactutor-jademirror 已 404（见⑥-3），无法在现行可达页面独立复核该页码；Zhu_Shijie 页仅见 Sarton 另一条评语（"one of the greatest mathematicians of his race…"） | **WARN**（引语与旧 MacTutor 页口径相符，但页码与原文暂无法独立核验） |

**事实层总评**：26 项复核，25 PASS + 1 WARN，**0 项事实性错误**。facts.md 编号 F-001~F-043 连续无跳号；争议条目（F-018/F-020/F-022）均并列诸说；"文献先后不构成传承证据"的限定句式在优先权条目中全部到位。特别值得肯定：对国学大师源文的"同治四年(1858)"笔误做了纠正而非照搬（F-028），符合"源文错误不静默照搬"要求。

---

## ③ URL 抽查表（新增外部 URL，2026-09-01 实测）

| # | URL | 登记位置 | 实测结果 | 与登记内容的一致性 |
|---|-----|---------|---------|-------------------|
| 1 | https://www.sciamvs.org/files/SCIAMVS_07_213-218_Review_Horiuchi_On_Chemla_Guo.pdf | comparative-studies（r-chemla-guo-2004） | ✅ 可达（PDF 全文抓取） | 完全一致：Dunod 2004 / ISBN / 1117 页 / 140+ 页词汇表 / 书评原句 |
| 2 | https://sphere.cnrs.fr/chemla-karine/ | comparative-studies（r-chemla-sphere） | ✅ 可达 | 完全一致：2021 Hirst Prize、ERC SAW、CNRS-CAS 框架 |
| 3 | https://www.cambridge.org/id/universitypress/subjects/history/history-science-and-technology/science-and-civilisation-china-volume-3 | comparative-studies（r-needham-scc3） | ✅ 可达（含 `/id/` 语言前缀仍有效） | 一致：1959 年 1 月、ISBN 9780521058018、卷名 |
| 4 | https://euromathsoc.org/magazine/articles/5 | comparative-studies（r-chemla-roads） | ✅ 可达 | 一致：EMS Magazine 119, pp. 23–30，开放获取 |
| 附 | https://www.guoxuedashi.com/SiKuQuanShu/bk101682c/ | joint-sources（s-guoxuedashi-jhyb） | ✅ 可达（检索引擎今日返回正文） | 一致：1606 起译/1607 刻印/克拉维乌斯/1857 韩应陛本/1865 金陵本 |
| 附 | https://ctext.org/nine-chapters/zhs | joint-sources（s-ctext-jiuzhang，复用） | ✅ 可达 | 一致：年代标注、《四部丛刊初编》res 77423（示例 02 引用号亦正确） |
| 附 | https://mathshistory.st-andrews.ac.uk/HistTopics/Nine_chapters/ | comparative-studies | ✅ 可达 | 一致 |
| 附 | https://mathshistory.st-andrews.ac.uk/HistTopics/Chinese_overview/ | comparative-studies | ✅ 可达 | 一致 |
| 附 | https://mathshistory.st-andrews.ac.uk/Biographies/Liu_Hui/ | comparative-studies | ✅ 可达 | 一致 |
| 附 | **https://mathshistory.st-andrews.ac.uk/Biographies/Jade_Mirror/** | comparative-studies（r-mactutor-jademirror） | ❌ **404**（站点提示"just moved to a new site, some pages have moved around"） | **登记页失效**；而该表标注"✅ 2026-09-01 验证"，验证标记与实测不符。替代锚点 /Biographies/Zhu_Shijie/ 今日实测可达 |

**小结**：抽查的 4 个新增 URL 全部可达且登记信息属实；但 r-mactutor-jademirror 为死链（涉及 F-007/F-008/F-013/F-014/F-016/F-022/F-041 七条事实的信源锚点），需按行动项 R-6 处理。

---

## ④ 中立性检查发现

**总体判定：PASS（无系统性倾向；双向防范显式且到位）**。逐项：

1. **时代错置**：✅ 无。concepts/05 专设"谁更接近'极限'？"节，明确"都不接近……必须避免时代错置"；concepts/01 反模式一给出"用 ε-δ 要求刘徽注"的具体病例；examples/01 明言"把弦图读作 I.47 的东方版本是无文献依据的时代错置"。
2. **单线进化史观**：✅ 无。concepts/00 以"打破单线进化史观"为节题；concepts/06 主动指出"记法形态并非线性进步，中途可能回退"（丢番图缩写早于花剌子米修辞）；insights 洞察 2 双向否定"接力赛"与"一切源于某方"。
3. **文化优越论（任一方向）**：✅ 无。concepts/07"反偏见的两条边界"同时点名"贬中扬西"与"贬西扬中"，并给出词面报警判据（"进步/落后/早该"出现即报警）；concepts/00 对 Needham 问题的处置（"不是本包要回答的问题……容易滑向文化优越论（无论哪个方向）"）是恰当的降维避坑。
4. **以"文献先后"当"传承证据"**：✅ 无，且为全包最 consistently 执行的纪律。facts F-019/F-021/F-022/F-023 每条均附限定句；concepts/01 反模式三给出"优先权三栏记录法"；examples/03 主动阻断"约率 22/7 = 阿基米德上界"的伪关联（"此为数值巧合，两传统之间没有任何传承证据"）——这是超出及格线的细节。
5. **勾股证明归属（Cullen 争议）**：✅ 并列诸说。facts F-020 与 MacTutor 原文一致（传统观点 + Cullen 质疑 + 两说并列不作裁决）；concepts/03 与 examples/01 均按"并列陈述＋不裁决"处理，并进一步区分"经文 vs 注文"两个文本层次，处理得当。
6. **轻微倾向性瑕疵（不构成 FAIL）**：
   - concepts/04："宋元算书把算法传统推到了中世纪世界的最高水准之一（F-008）"——Sarton 的评语针对《四元玉鉴》一部书，此处经"同样适用于这一谱系"过渡推广至宋元算书整体，略有放大；因有"之一"限定且已注明系由 Sarton 评语延伸，记为轻微。
   - concepts/08"方法论小结"称范式冲击"要等到主题 07 所述的近代重译与科学教育时代才充分展开"，属解释性判断，已与事实分层，可接受。

---

## ⑤ 数学验算记录

### examples/01 勾股（欧氏 I.47 vs 赵爽弦图）——全对 ✅

- 弦图恒等式：$c^2=4\cdot\frac{ab}{2}+(b-a)^2=2ab+b^2-2ab+a^2=a^2+b^2$ ✅
- 3-4-5 验算：4×6+1=24+1=25=5² ✅（任务点名项，正确）
- 实方图变体：$(a+b)^2=2ab+c^2$；49=24+25，$c^2=49-24=25$ ✅
- I.47 六步推理链（I.4 全等 / I.14 共线 / I.41 翻倍）与欧氏原证一致；"夹角各添一直角后仍相等"的转述正确 ✅
- "两矩共长二十有五"释为"两块矩形合计面积 25"：按赵爽自注（"两矩者，句股各自乘之实"）应为两直角边上的正方形；"矩形"是"正方形"的上位词，面积和 25 无误——记轻微措辞问题，不算错误。

### examples/02 线性方程组（3x+2y+z=39, 2x+3y+z=34, x+2y+3z=26）——全对 ✅

- 遍乘直除三步复算：3R₂−2R₁=(0,5,1|24) ✅；3R₃−R₁=(0,4,8|39) ✅；5R₃−4R₂=(0,0,36|99) ✅
- 回代：z=99/36=**11/4** ✅；y=(24−11/4)/5=**17/4** ✅；x=(39−2·17/4−11/4)/3=**37/4** ✅（任务点名项，正确）
- 三式验算：(111+34+11)/4=39 ✅；(74+51+11)/4=34 ✅；(37+34+33)/4=26 ✅
- det A=3(9−2)−2(6−1)+1(4−3)=21−10+1=12 ✅；Cramer 三分子式 111/51/33 ✅
- 《九章》原答换算：九又四分之一=37/4 ✅、四又四分之一=17/4 ✅、二又四分之三=11/4 ✅
- 莱布尼茨 1693 年致洛比达信中出现行列式排列 ✅（与信史一致）

### examples/03 圆周率——两处错误 ❌，其余全对

正确部分：
- S₉₆=313+584/625≈313.9344 ✅、S₁₉₂=314+64/625≈314.1024 ✅、差幂 105/625=0.168 ✅（均为刘徽注原始数据）
- 3.141024 < π < 3.142704 ✅（由 (S₁₉₂+r·100)/100 与 S₁₉₂/100 算得，正确）
- 223/71≈3.140846 < π < 22/7≈3.142857 ✅；n·sin(π/n) 六行数值表全部复算一致（3.0000/3.1058/3.1326/3.1394/3.1410/3.1415）✅
- 徽率 157/50=3.14 落在刘徽上下界之内 ✅；265/153<√3<1351/780 为阿基米德实际使用的分数不等式 ✅；"密率是分母小于 16604 的一切分数中最接近 π 者"为标准结论 ✅

**错误 1（FAIL-M1，结论性陈述错误）**：第 131 行"密率 $\tfrac{355}{113}\approx3.1415929$ **落在祖冲之的盈朒二限之内**"。355/113≈3.14159292 > 盈限 3.1415927，**不在** (3.1415926, 3.1415927) 之内——文中自己给出的 3.1415929 已自证其伪。正确表述应为：密率是略高于盈限的过剩有理逼近，与盈朒二限分属"有理近似值"与"十进制界"两种对象，二者数值不相容。

**错误 2（FAIL-M2，推导理由句错误）**：第 77 行"正 2n 边形由 2n 个以圆心为顶点、底 $l_{2n}$ 高 $r$ 的三角形组成，故 $S_{2n}=\tfrac12 n l_n r$"。前提算出的面积是 $2n\cdot\frac12 l_{2n} r=n\,l_{2n}r$，推不出结论中的 $\frac12 n l_n r$（二者仅当 $l_{2n}=l_n/2$ 时相等，不成立）。公式本身正确（即刘徽"以六觚之一面乘半径，因而三之"），正确的理由是 **n 个以 $l_n$（n 边形边长）为底、r 为高的三角形**（或 2n 个底 $l_{2n}$、高为边心距的三角形）。属"结论对、理由句错"的表述性硬伤，须改写。

---

## ⑥ 结构与链接检查

### 6.1 四层结构（concepts/03–08）

| 篇目 | 西方节点 | 中国平行 | 比较分析 | 对读示范指引 | 判定 |
|------|---------|---------|---------|-------------|------|
| 03 几何与度量 | ✅ | ✅ | ✅ | ✅ | 合格 |
| 04 数论与代数 | ✅ | ✅ | ✅ | ✅ | 合格（列表渲染有断行瑕疵） |
| 05 极限与无穷小 | ✅ | ✅ | ✅ | ✅ | 合格（正文两处变量丢失，见 WARN-1） |
| 06 符号化与抽象 | ✅ | ✅ | ✅ | ✅ | 合格 |
| 07 公理化与算法化 | ✅ | ✅ | ✅ | ✅ | 合格 |
| 08 接触与互鉴 | ✅ | ✅ | ✅ | ✅ | 合格（两处"240 年"算术错误，见 FAIL-S1） |

### 6.2 跨束链接抽查（8 条，含任务点名 6 条）

| # | 出发文件 → 目标 | 实测 | 判定 |
|---|----------------|------|------|
| 1 | concepts/00 → `../../classics-reading/index.md` | kexue/math/classics-reading/index.md 存在 | ✅ |
| 2 | concepts/00 → `../../../../guoxue/suanxue/suanjing-reading/index.md` | bundles/guoxue/suanxue/suanjing-reading/index.md 存在 | ✅ |
| 3 | concepts/02 → `../../classics-reading/examples/03-reading-roadmap.md` | 存在 | ✅ |
| 4 | concepts/02 → `../../../../guoxue/suanxue/suanjing-reading/examples/08-reading-plan.md` | 存在 | ✅ |
| 5 | examples/01 → `../../classics-reading/examples/01-euclid-close-reading.md` | 存在 | ✅ |
| 6 | examples/03 → `../../../../guoxue/suanxue/suanjing-reading/examples/07-geyuan-pi.md` | 存在 | ✅ |
| 7 | concepts/07 → `../../../../zhexue/psi/psi-math/index.md` | bundles/zhexue/psi/psi-math/index.md 存在 | ✅ |
| 8 | examples/02 → `../../../../jishu/data/pydata/sympy/index.md` | 存在 | ✅ |

**从 concepts/ 与 examples/ 出发的跨束链接全部正确。但 references/ 两篇存在系统性层级错误**（references/ 与 concepts/ 同为 bundle 根下一级，前缀应相同）：

- **FAIL-S2（约 14 条断链）**：
  - `references/cross-references.md` 第一、二节：classics-reading 链接误用 `../classics-reading/...`（解析到 `east-west-dialogue/classics-reading/`，不存在），涉及 05-greek-geometry / 06-hellenistic-number-theory / 07-islamic-algebra / 08-early-modern-17c / 10-gauss-turn / 12-rigor-and-foundations / examples/01-euclid-close-reading 共 7 条，应为 `../../classics-reading/...`；
  - 同文件第三节：`../../../jishu/...`（×4）、`../../../zhexue/...`（×1）解析到 `kexue/jishu`、`kexue/zhexue`（不存在），应为 `../../../../...`；
  - 同文件第四节：`../../chemistry/index.md`、`../../physics/index.md` 解析到 `kexue/math/chemistry|physics`（实际位于 `kexue/chemistry|physics`，应为 `../../../`）；`../../../guoxue/suanxue/index.md` 解析到 `kexue/guoxue/...`（实际 `bundles/guoxue/suanxue`，应为 `../../../../`）；
  - `references/joint-sources.md` 西方侧表 2 条 `../classics-reading/references/original-sources.md`、`.../translations-commentaries.md` 同病，应为 `../../...`。
  - 对照组：同文件中 suanjing-reading 链接（`../../../../guoxue/...`）全部正确，说明是 classics/jishu/zhexue/chemistry 侧前缀少写一层，属 Skill 已知瑕疵模式"跨 bundle 相对路径少一层"。
- **FAIL-S3（死链信源）**：r-mactutor-jademirror（/Biographies/Jade_Mirror/）404，comparative-studies.md 仍标"✅ 2026-09-01 验证"。

### 6.3 复制检查

✅ 未发现整段复制既有束内容。与 suanjing-reading 重合的仅为刘徽注、商高原文等经典引文（引录规范允许且已标注底本）；正文为原创对读分析。反证：bundle 对源文错误做了纠正（F-028 的 1865 vs 源文 1858），证明非机械照搬。

### 6.4 索引接入与计数

- `kexue/math/index.md`：束数 1→2 ✅、统计（2 束/23 概念/6 示例/7 信源）与实际一致 ✅、toctree 收录 east-west-dialogue/index ✅。
- `doc/bundles/index.md`：kexue/math 行束数 2 ✅、kexue 域描述含"中西数学对读" ✅。total_bundles 现为 389（log 记录当时 378→379）——差额系后续其他束并行新增所致，组内计数无误，不构成本束问题。
- 根 index frontmatter `type: OKF` 与同分组 classics-reading 惯例一致 ✅；facts 编号连续、双处引用（正文↔facts.md）抽查一致 ✅。
- 轻微：insights.md 覆盖矩阵"接触与互鉴→对读示范：示例 01（译名对照）"指向失真——示例 01 为勾股对读，无译名对照内容，译名对照实际在 concepts/08；建议改指概念 08 或标"无专文示范"。

---

## ⑦ Rubric 评分表（1–5 分）

| 维度 | 分数 | 理由与证据 |
|------|------|-----------|
| **AC-8 对读示范质量** | **3.5 / 5** | 加分：三篇结构统一（原文对照→逐步对照→现代统一解读→差异分析）；双源原文均标底本（ctext res 号、《四部丛刊》初编、Fitzpatrick/Heath 公共领域译本），版权译本零复制；示例 02 全链路零误差（消元三步、回代、Cramer、原答换算全对），"遍乘直除 ↔ 初等行变换"逐步对应表是全包最扎实的落地；示例 01 两种弦图摆法+I.47 六步链均正确。扣分：示例 03 存在两处硬伤（密率"落在盈朒二限之内"为结论性错误；S₂ₙ 分解理由句推导不通）；concepts/05 正文两处数学变量丢失直接损伤同主题阅读体验。 |
| **AC-9 比较分析洞察力** | **4 / 5** | 加分：非贴标签式比较——"穷竭法证明已知值为真 vs 割圆术算出未知值为用"的镜像概括、"媒介的存亡即知识的存亡"（洞察 4）、"底本更替本身就是西方数学出版史的一面镜子"（克拉维乌斯→Billingsley）、对象/文体/动机三层差异追问，均达到比较研究写作的良好水准；三波西学东渐框架、对 Needham 问题的降维处置显示史学分寸感。扣分：Sarton 一书评语放大为宋元算书整体（concepts/04）；concepts/08 两处"240 年"算术错误与"三百年"虚指损害交流史篇目的数字严谨性。 |
| **AC-10 方法论闭环** | **4 / 5** | 加分：facts.md 43 条零因果推断词、编号连续、优先权条目全部携带"不构成传承证据/无定论/无文献证据"限定；insights 四条洞察四元组（现象/根因/影响/建议）齐备；两个可迁移模式四要素（触发条件/核心步骤/反模式/迁移示例）齐备；正文 F 编号引用密度高且抽查全部能在 facts.md 对应；争议条目并列诸说（F-020/F-018/F-022）。扣分：references/index.md 声称"每条事实的信源 ID 均可在此三篇文档中定位"，但 e-qian-1963 实际登记于 suanjing-reading 束，本束无法定位（声明过强）；"Jade Mirror"死链上的 ✅ 验证标记失真；"MacTutor 转载 Jock Hoe 论文"表述不准（系引用而非转载）。 |

---

## ⑧ 总体结论

### **FAIL（有条件通过前需修复）**

事实层质量很高（26 项复核 0 硬错误、1 项待复核），比较分析中立性与方法论闭环达到发布水准；但 **references/ 两篇约 14 条跨束断链、示例 03 两处数学硬伤、概念 08 算术错误、一条死链信源带失真验证标记**，构成发布阻塞项。按下列清单修复后可复检转 PASS。

### 行动项清单

| # | 级别 | 位置 | 问题 | 修复动作 |
|---|------|------|------|---------|
| R-1 | FAIL | references/cross-references.md | classics-reading 7 条链接少一层（`../classics-reading/` → 应为 `../../classics-reading/`）；jishu×4、zhexue×1 少一层（`../../../` → `../../../../`）；chemistry/physics 少一层（`../../` → `../../../`）；guoxue/suanxue 少一层（`../../../` → `../../../../`） | 逐条改前缀并重跑链接检查 |
| R-2 | FAIL | references/joint-sources.md 西方侧表 | 2 条 `../classics-reading/...` 应为 `../../classics-reading/...` | 同上 |
| R-3 | FAIL | examples/03-pi-comparison.md | 删除/改写"密率 355/113 落在祖冲之的盈朒二限之内"——355/113≈3.1415929 > 盈限 3.1415927 | 改为"密率是略高于盈限的过剩有理逼近，与盈朒二限分属不同对象" |
| R-4 | FAIL | examples/03-pi-comparison.md | "正 2n 边形由 2n 个底 l₂ₙ 高 r 的三角形组成，故 S₂ₙ=½n l_n r"前提与结论不匹配 | 改为"n 个以 l_n 为底、r 为高的三角形"（与刘徽"以一面乘半径"原文一致） |
| R-5 | FAIL | concepts/08-contact-mutual-learning.md（"方法论小结"与"与平行主题的呼应"） | 两处"240 年"应为"250 年"（1607→1857） | 改数字；建议连带把根 index"汉译三百年"改为"两个半世纪以上"或"258 年" |
| R-6 | FAIL | references/comparative-studies.md（r-mactutor-jademirror） | 登记页 /Biographies/Jade_Mirror/ 404 但标"✅ 已验证"；F-007/F-008/F-013/F-014/F-016/F-022/F-041 锚点悬空 | 改锚 https://mathshistory.st-andrews.ac.uk/Biographies/Zhu_Shijie/（今日实测可达）并在 log.md 注记；F-008 的"卷三第 703 页"页码标注"转引待复核"；"MacTutor 转载"改为"MacTutor 页面引用 Jock Hoe 研究" |
| R-7 | WARN | concepts/05-limits-infinity.md（"递推程序的技术细节"） | 两处"$ 后变量丢失（"由正 $ 边形边长算出正 $ 边形边长"、"算出 $ 个小三角形"） | 补为"由正 n 边形边长算出正 2n 边形边长""算出 2n 个小三角形"并检查 MyST 行内数学转义 |
| R-8 | WARN | concepts/03-geometry-measurement.md | "出入相补作为named原理"中英混排 | 改"具名原理" |
| R-9 | WARN | insights.md 覆盖矩阵 | "接触与互鉴→示例 01（译名对照）"指向失真（示例 01 无译名内容） | 改指 concepts/08 或标"无专文示范" |
| R-10 | WARN | facts.md F-006 / references/index.md | "1248 年刊"欠精确（MacTutor 口径 written 1248）；"每条事实信源 ID 均可在此三篇定位"与 e-qian-1963 实况不符 | "刊"改"成书"；声明加"（e- 前缀点校本信源见 suanjing-reading 束登记）" |
| R-11 | WARN | examples/02、concepts/06、concepts/04 | 编号列表中间插入未缩进段落导致渲染断列；examples/01 "两块矩形"宜按赵爽自注表述为"两直角边上的正方形" | 微调排版与措辞 |

**修复优先级**：R-1/R-2（断链）> R-3/R-4/R-5（数字与数学）> R-6（死链）> R-7~R-11。全部修复后建议复跑 §7 机械门禁手动清单（链接 Test-Path 逐条 + UTF-8 roundtrip + toctree 计数）并在 log.md 追加修复记录。

---

*本报告由独立对抗审查者出具，与 bundle 写作者无关；所有 URL 实测与数学验算均为本次独立执行，检索与抓取时间 2026-09-01。*

---

## ⑨ 修复复验记录（写作者执行，2026-09-01）

行动项 R-1~R-11 已全部修复并在 log.md 追加闭环记录：

| 项 | 修复内容 | 复验结果 |
|---|---------|---------|
| R-1 | cross-references.md 14 条链接前缀（classics-reading→`../../`、jishu/zhexue/guoxue→`../../../../`、chemistry/physics→`../../../`） | ✅ 脚本全量解析 0 断链 |
| R-2 | joint-sources.md 2 条 `../classics-reading/`→`../../classics-reading/` | ✅ 同上 |
| R-3 | 密率句改为"略高于盈限 3.1415927——过剩有理逼近，与十进制小数界分属两类对象，不落入区间之内" | ✅ 数值自洽 |
| R-4 | S₂ₙ 理由句改为"正 n 边形剖分为 n 个以 lₙ 为底、r 为高的三角形"（与刘徽"以一面乘半径"一致） | ✅ 推导成立 |
| R-5 | concepts/08 两处"240 年"→"250 年"；根 index"三百年"→"258 年（1607–1865）"、frontmatter"三百年"→"两个半世纪的历程" | ✅ |
| R-6 | r-mactutor-jademirror 改锚 `/Biographies/Zhu_Shijie/`（实测可达）、"MacTutor 转载"→"页面引用"、F-008 页码标"转引待复核"、迁移情况注记 | ✅ |
| R-7 | concepts/05 两处变量补齐（正 $n$ / 正 $2n$、$2n$ 个小三角形） | ✅ |
| R-8 | "named原理"→"具名原理" | ✅ |
| R-9 | 覆盖矩阵"接触与互鉴"示范指向改为"译名对照见概念 08 时间线（无专文示范）" | ✅ |
| R-10 | F-006 "刊"→"成书"；references/index 溯源声明补充"e- 前缀点校本信源见 suanjing-reading 束" | ✅ |
| R-11 | examples/01 "两块矩形"→"两个正方形分别等于两直角边上的正方形"（含 mermaid 标签同步） | ✅ |

**机械复验**：本束 22 个 Markdown 文件——YAML 可解析且 type 非空 22/22；相对链接断链 0；`file:///` 0；sphinx-build（dummy, -E）本束警告 0（全库残余 5 条均属并行会话在途文件 meitong-yanyin-pedagogy 与 yishu/liaoyu，非本束射程）。

**复验结论：PASS**（R-1~R-6 发布阻塞项全部消除；WARN 项 R-7~R-11 一并落地）。事实层 26 项复核 0 硬错误的结论维持有效。
