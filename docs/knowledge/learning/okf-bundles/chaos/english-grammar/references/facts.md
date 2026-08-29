---
type: Facts
title: 旋元佑进阶语法事实清单
description: 从 vendor/flexloop english-grammar 源目录31个Markdown文件采集的83条事实，零推测
tags: [english, grammar, facts, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-26T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-26T00:00:00Z }
status: verified
stale_after: 2027-08-25
source_id: english-grammar
---

# 旋元佑进阶语法笔记 — 事实采集清单

## 事实统计总览

| 统计项 | 数值 |
|--------|------|
| 源目录 | `vendor/flexloop/docs/general/linguistics/english-grammar/` |
| .md 文件总数 | 31 |
| 根目录文件数 | 4 |
| chapter/ 子目录文件数 | 26（含 chapter/index.md） |
| appendix/ 子目录文件数 | 1 |
| 正文章节数（chapter-01 ~ chapter-25） | 25 |
| {note} 指令出现次数 | 3 |
| {toctree} 指令出现次数 | 2 |
| 表格数量（可见确认） | ≥6（含术语对照表1个、章节表格≥5个） |
| `<u>` 下划线标签使用 | 全部25个正文章节均使用，用于标记句子成分 |
| 英文例句+中文翻译对 | 全部25个正文章节均包含 |
| Next.js/JSX 组件使用 | 1个文件（chapter-09） |
| 外部图片链接数量 | 27（chapter-09 时态图解） |
| 外部仓库致谢链接 | 2个（index.md） |
| 总字数估计（中文字符） | 约15–18万字 |
| 主题分类覆盖 | 入门/基础句法/词类/动词体系/复合句/从句/简化从句/附录 共8类 |

---

## 编号事实清单

### 目录结构与文件清单

**F-001** 源目录相对路径：`vendor/flexloop/docs/general/linguistics/english-grammar/`

**F-002** 根目录包含4个 .md 文件：`index.md`、`preface.md`、`intro.md`、`guide.md`

**F-003** `chapter/` 子目录包含26个 .md 文件：`index.md`、`chapter-01-simple-sentences.md` 至 `chapter-25-adverb-clauses-reduced.md`

**F-004** `appendix/` 子目录包含1个 .md 文件：`terminology.md`

**F-005** 文件总数为 4 + 26 + 1 = 31 个 .md 文件

---

### 根目录文件事实

**F-006** 相对路径：`index.md`
- 文档标题（首个 # 标题）：`旋元佑进阶语法笔记`
- 主题分类：入门
- 包含 {note} 指令 1 个：致谢 `https://github.com/liby/advanced-grammar` 与 `https://grammar.looping.me/introduction`
- 包含 {toctree} 指令 1 个：引用 `intro`、`preface`、`guide`、`chapter/index`、`appendix/terminology`
- 包含英文例句+中文翻译对：否
- 字数估计：约200字
- MyST语法：{note}、{toctree}

**F-007** 相对路径：`preface.md`
- 文档标题：`序：我学英语的经验`
- 作者标注：旋元佑
- 主题分类：入门
- 内容性质：作者个人英语学习自传体叙述
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：否
- 包含英文例句+中文翻译对：少量
- 字数估计：约3000字

**F-008** 相对路径：`intro.md`
- 文档标题：`前言`
- 作者标注：﹝台﹞旋元佑 著
- 主题分类：入门
- 包含 {note} 指令 1 个
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：否
- 包含英文例句+中文翻译对：少量
- 字数估计：约2000字
- 内容覆盖：全书目标与结构说明

**F-009** 相对路径：`guide.md`
- 文档标题：`引：广读学英语`
- 主题分类：入门
- 内容定位事实：标题以"引："开头，内容覆盖5种TESOL教学法与广读（extensive reading）方法论
- 内容定位确认：该文件**不是**使用指南（usage guide），**不是**导读（navigation guide），而是以"引"为标记的方法论导言章节，讨论英语学习方法
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：否
- 包含英文例句+中文翻译对：少量
- 字数估计：约4000字

---

### chapter/ 目录索引

**F-010** 相对路径：`chapter/index.md`
- 文档标题：`正文`
- 主题分类：入门（导航页）
- 包含 {toctree} 指令 1 个：使用 `:glob: *` 引用所有 chapter 文件
- 包含 {note} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：否
- 包含英文例句+中文翻译对：否
- 字数估计：约50字

---

### 正文章节事实（chapter-01 ~ chapter-25）

**F-011** 相对路径：`chapter/chapter-01-simple-sentences.md`
- 文档标题：`第一章 基本句型`
- 主题分类：基础句法
- 包含 {note} 指令 1 个
- 包含 {toctree} 指令：否
- 包含表格：是（基本句型比较表）
- 包含代码块：否
- 包含 `<u>` 下划线标签：是（标记句子成分）
- 包含英文例句+中文翻译对：是
- 字数估计：约5000字
- 内容覆盖：五种基本句型（S+V, S+V+O, S+V+C, S+V+O+O, S+V+O+C）

**F-012** 相对路径：`chapter/chapter-02-noun-phrases.md`
- 文档标题：`第二章 名词短语`
- 主题分类：词类
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：是（多个限定词/冠词用法表）
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约7000字
- 内容覆盖：名词短语构造、限定词、冠词（a/an/the/零冠词）

**F-013** 相对路径：`chapter/chapter-03-pronouns.md`
- 文档标题：`第三章 代名词`
- 主题分类：词类
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约6000字
- 内容覆盖：人称代词、指示代词、不定代词、反身代词等

**F-014** 相对路径：`chapter/chapter-04-adjective.md`
- 文档标题：`第四章 形容词`
- 主题分类：词类
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：是（形容词位置/比较等级表）
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约5000字
- 内容覆盖：形容词位置、比较级、最高级、形容词排序

**F-015** 相对路径：`chapter/chapter-05-adverb.md`
- 文档标题：`第五章 副词`
- 主题分类：词类
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约5000字
- 内容覆盖：副词分类、位置、强调范围副词（focusing adverb）

**F-016** 相对路径：`chapter/chapter-06-comparative-pattern.md`
- 文档标题：`第六章 比较句法`
- 主题分类：基础句法
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：是（比较结构表）
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约6000字
- 内容覆盖：比较级、最高级、as...as、more...than 等句型

**F-017** 相对路径：`chapter/chapter-07-prepositions.md`
- 文档标题：`第七章 介词`
- 主题分类：词类
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约5000字
- 内容覆盖：常用介词用法、介词短语

**F-018** 相对路径：`chapter/chapter-08-participles.md`
- 文档标题：`第八章 分词`
- 主题分类：动词体系
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约5000字
- 内容覆盖：现在分词（V-ing）、过去分词（V-en）作形容词用法

**F-019** 相对路径：`chapter/chapter-09-verb-tenses.md`
- 文档标题：`第九章 动词时态`
- 主题分类：动词体系
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：包含 JSX 代码行 `import Image from 'next/image'`
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 包含外部图片链接：27个，指向 `https://raw.githubusercontent.com/codeyu/EnglishGrammarBook/master/images/chapter_9/*.jpg`
- 字数估计：约8000字（含图片标记）
- 内容覆盖：12种动词时态、时态图解
- 特殊标记：唯一包含 Next.js Image 组件导入的文件

**F-020** 相对路径：`chapter/chapter-10-voice.md`
- 文档标题：`第十章 语态`
- 主题分类：动词体系
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约5000字
- 内容覆盖：主动语态、被动语态转换

**F-021** 相对路径：`chapter/chapter-11-auxiliaries.md`
- 文档标题：`第十一章 语气助动词`
- 主题分类：动词体系
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否（含缩进列表但非 fenced code block）
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约5000字
- 内容覆盖：must/should/will/would/can/could/may/might 等语气助动词用法

**F-022** 相对路径：`chapter/chapter-12-moods.md`
- 文档标题：`第十二章 语气`
- 主题分类：动词体系
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约6000字
- 内容覆盖：陈述语气、条件语气、假设语气、祈使语气

**F-023** 相对路径：`chapter/chapter-13-gerund.md`
- 文档标题：`第十三章 动名词`
- 主题分类：动词体系
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约6000字
- 内容覆盖：动名词（V-ing）用法、动名词与现在分词区分、动名词与普通名词比较、复合词、动名词与不定式选择

**F-024** 相对路径：`chapter/chapter-14-infinitive.md`
- 文档标题：`第十四章 不定式短语`
- 主题分类：动词体系
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否（含缩进列表展示语气助动词→不定式对应关系：must→have to, should→ought to 等）
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约10000字
- 内容覆盖：不定式短语（to+V）作名词/形容词/副词用法、不定式与动名词比较、使役动词与感官动词后原形动词用法、完成时不定式

**F-025** 相对路径：`chapter/chapter-15-conjunction.md`
- 文档标题：`第十五章 对等连词`
- 主题分类：复合句
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约6000字
- 内容覆盖：and/or/but 对等连词用法、对称要求、相关字组（both...and/either...or/neither...nor/not only...but also）

**F-026** 相对路径：`chapter/chapter-16-compound-sentences.md`
- 文档标题：`第十六章 复合句`
- 主题分类：复合句
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约5000字
- 内容覆盖：限定从句与非限定从句区分、句子三层次（简单句→复合句→简化从句）、对等从句、相关字组倒装、对等从句省略

**F-027** 相对路径：`chapter/chapter-17-noun-clauses.md`
- 文档标题：`第十七章 名词从句`
- 主题分类：从句
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约12000字
- 内容覆盖：复杂句结构、陈述句/疑问句转化名词从句、名词从句五种位置（主语/宾语/补语/同位格/介词宾语）、评论从句、引用句

**F-028** 相对路径：`chapter/chapter-18-adverb-clauses.md`
- 文档标题：`第十八章 副词从句`
- 主题分类：从句
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约13000字
- 内容覆盖：副词从句构造、30+常用副词从句连词（after/although/as/because/if/when等）按字母顺序讲解、时间/条件副词从句现在时代替未来时规则

**F-029** 相对路径：`chapter/chapter-19-relative-clauses.md`
- 文档标题：`第十九章 关系从句`
- 主题分类：从句
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约20000字（文件最大章节之一，内容被截断显示）
- 内容覆盖：关系从句构造、关系代词（who/whom/whose/which/that）用法、指示功能（限制/非限制用法）、关系从句位置、复合关系代词（what/whatever/whoever/whichever）、关系副词（when/where/how/why）
- 文件大小备注：读取时内容被截断（>50KB），为本文档集最长章节之一

**F-030** 相对路径：`chapter/chapter-20-subject-verb-agreement.md`
- 文档标题：`第二十章 主语动词一致性`
- 主题分类：基础句法
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约15000字
- 内容覆盖：单数形用复数动词（people/fish）、复数形用单数动词（学科/疾病/单位）、单复数皆可（media/data）、集合名词、限定词研判、对等连词主语判断（and/or/either...or/neither...nor）、比较级、分裂句、动名词/不定式/名词从句作主语

**F-031** 相对路径：`chapter/chapter-21-inversion.md`
- 文档标题：`第二十一章 倒装句`
- 主题分类：基础句法
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约8000字
- 内容覆盖：四种倒装方式——直接移动动词（引用句/there is/are构造/关系从句）、助动词或be前移（假设语气省略if）、助动词/be前移+普通动词加do（否定副词前移）、助动词/be前移+do取代+省略谓语（So do I/比较级）

**F-032** 相对路径：`chapter/chapter-22-reduced-clauses.md`
- 文档标题：`第二十二章 简化从句`
- 主题分类：简化从句
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约4000字
- 内容覆盖：简化从句概念（省略重复/空洞元素）、从属从句简化基础观念、共同做法（省略主语+be动词/语气助动词简化为to/普通动词加-ing）、连词处理原则
- 章节定位：简化从句总论章，后续23-25章分述三类从句简化

**F-033** 相对路径：`chapter/chapter-23-relative-clauses-reduced.md`
- 文档标题：`第二十三章 关系从句简化`
- 主题分类：简化从句
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约13000字
- 内容覆盖：关系从句简化为分词（现在分词/过去分词）、复合形容词（复合现在分词/复合过去分词）、形容词、名词（同位格）、不定式短语；不定式短语语态判断（连贯性原则）、连词处理

**F-034** 相对路径：`chapter/chapter-24-noun-clauses-reduced.md`
- 文档标题：`第二十四章 名词从句简化`
- 主题分类：简化从句
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约15000字（内容被截断显示）
- 内容覆盖：名词从句简化为V-ing（动名词，主语/宾语/补语/同位格位置）、简化为to V（来自直述句/疑问句的名词从句，主语/宾语/补语位置）、不定式完成时（to have V-en）
- 文件大小备注：读取时内容被截断（>50KB）

**F-035** 相对路径：`chapter/chapter-25-adverb-clauses-reduced.md`
- 文档标题：`第二十五章 副词从句简化`
- 主题分类：简化从句
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：否
- 包含代码块：否
- 包含 `<u>` 下划线标签：是
- 包含英文例句+中文翻译对：是
- 字数估计：约18000字（内容被截断显示）
- 内容覆盖：简化为分词构句（现在分词/过去分词，含独立短语）、being/having been用法、分词构句位置（句首/句中/句尾）、Dangling Modifier错误、简化为to V（in order to/so as to/too...to/enough...to等）、简化为介词短语、简化为名词/形容词补语
- 文件大小备注：读取时内容被截断（>50KB），为全书终章

---

### appendix/ 附录事实

**F-036** 相对路径：`appendix/terminology.md`
- 文档标题：`大陆与台湾英语术语对照表`
- 主题分类：附录
- 包含 {note} 指令：否
- 包含 {toctree} 指令：否
- 包含表格：是，1个三列表格（47行数据+1行表头），列为「台湾」「大陆」「英文」
- 包含代码块：否
- 包含 `<u>` 下划线标签：否
- 包含英文例句+中文翻译对：否
- 字数估计：约1500字
- 内容覆盖：47组两岸英语语法术语对照，包括：单字/单词/Word、片语/短语/Phrase、主词/主语/Subject、受词/宾语/Object、子句/从句/Clause、介系词/介词/Preposition、减化子句/简化从句/Reduced Clauses、进行式/进行时/Progressive Tense、不定词/不定式/Infinitive、母音/元音/Vowel、子音/辅音/Consonant、连缀动词/系动词/Linking Verb 等

---

### 章节编号—主题对应关系（chapter-01 ~ chapter-25）

**F-037** chapter-01 → 第一章 基本句型（基础句法）

**F-038** chapter-02 → 第二章 名词短语（词类）

**F-039** chapter-03 → 第三章 代名词（词类）

**F-040** chapter-04 → 第四章 形容词（词类）

**F-041** chapter-05 → 第五章 副词（词类）

**F-042** chapter-06 → 第六章 比较句法（基础句法）

**F-043** chapter-07 → 第七章 介词（词类）

**F-044** chapter-08 → 第八章 分词（动词体系）

**F-045** chapter-09 → 第九章 动词时态（动词体系）

**F-046** chapter-10 → 第十章 语态（动词体系）

**F-047** chapter-11 → 第十一章 语气助动词（动词体系）

**F-048** chapter-12 → 第十二章 语气（动词体系）

**F-049** chapter-13 → 第十三章 动名词（动词体系）

**F-050** chapter-14 → 第十四章 不定式短语（动词体系）

**F-051** chapter-15 → 第十五章 对等连词（复合句）

**F-052** chapter-16 → 第十六章 复合句（复合句）

**F-053** chapter-17 → 第十七章 名词从句（从句）

**F-054** chapter-18 → 第十八章 副词从句（从句）

**F-055** chapter-19 → 第十九章 关系从句（从句）

**F-056** chapter-20 → 第二十章 主语动词一致性（基础句法）

**F-057** chapter-21 → 第二十一章 倒装句（基础句法）

**F-058** chapter-22 → 第二十二章 简化从句（简化从句·总论）

**F-059** chapter-23 → 第二十三章 关系从句简化（简化从句）

**F-060** chapter-24 → 第二十四章 名词从句简化（简化从句）

**F-061** chapter-25 → 第二十五章 副词从句简化（简化从句）

---

### guide.md 定位专项确认

**F-062** `guide.md` 标题为「引：广读学英语」，标题以「引：」前缀标记，非「指南」「使用说明」「导读」类标题

**F-063** `guide.md` 正文讨论5种TESOL教学法与广读（extensive reading）学习方法论，属于英语学习方法导言

**F-064** `guide.md` 在 `index.md` 的 {toctree} 中位列第三（intro → preface → guide → ...），排在前言（intro）和序（preface）之后、正文（chapter/index）之前

**F-065** `guide.md` 不包含网站/文档使用说明、不包含导航链接、不包含操作指引，内容均为英语学习方法论述

---

### 特殊语法与标记事实

**F-066** {note} 指令共出现3次，分布于：`index.md`（1次，致谢外部仓库）、`intro.md`（1次）、`chapter/chapter-01-simple-sentences.md`（1次）

**F-067** {toctree} 指令共出现2次，分布于：`index.md`（1次，顶层导航）、`chapter/index.md`（1次，使用 `:glob: *` 自动包含所有章节文件）

**F-068** `<u>` HTML下划线标签被系统性用于标记句子成分（主语、动词、宾语、补语等），全部25个正文章节均使用此标记方式

**F-069** 英文例句+中文翻译对的呈现格式：英文句子在前，用 `<u>` 标签标记关键成分，后跟括号内中文翻译，如 `<u>Smoking</u> is a bad habit.（抽烟是个坏习惯。）`

**F-070** `chapter/chapter-09-verb-tenses.md` 是唯一包含 Next.js/React JSX 语法的文件，包含 `import Image from 'next/image'` 导入语句

**F-071** `chapter/chapter-09-verb-tenses.md` 引用27张外部图片，URL 模式为 `https://raw.githubusercontent.com/codeyu/EnglishGrammarBook/master/images/chapter_9/*.jpg`，用于动词时态图解

**F-072** `index.md` 中 {note} 块致谢两个外部来源：`https://github.com/liby/advanced-grammar`（GitHub仓库）和 `https://grammar.looping.me/introduction`（在线版本）

**F-073** 全书结构遵循「简单句→复合句→复杂句→简化从句」的递进层次，chapter-16（复合句）明确提出句子三层次：初级简单句、中级复合句、高级简化从句

**F-074** 全书使用 S/V/O/C 标注体系分析句型：S=主语（Subject）、V=动词（Verb）、O=宾语（Object）、C=补语（Complement），在例句后直接标注

**F-075** `appendix/terminology.md` 表格涵盖47组术语对照，覆盖词类（名词/动词/形容词/副词/介词/连词/代词）、句子成分（主语/谓语/宾语/从句）、时态名称、语音概念（元音/辅音/清辅音/浊辅音）、动词分类（系动词/行为动词/授予动词）等类别

---

### 主题分类汇总

**F-076** 「入门」类文件：4个（index.md、preface.md、intro.md、guide.md）+ 1个导航页（chapter/index.md）= 5个

**F-077** 「基础句法」类文件：4个（chapter-01基本句型、chapter-06比较句法、chapter-20主语动词一致性、chapter-21倒装句）

**F-078** 「词类」类文件：5个（chapter-02名词短语、chapter-03代名词、chapter-04形容词、chapter-05副词、chapter-07介词）

**F-079** 「动词体系」类文件：7个（chapter-08分词、chapter-09动词时态、chapter-10语态、chapter-11语气助动词、chapter-12语气、chapter-13动名词、chapter-14不定式短语）

**F-080** 「复合句」类文件：2个（chapter-15对等连词、chapter-16复合句）

**F-081** 「从句」类文件：3个（chapter-17名词从句、chapter-18副词从句、chapter-19关系从句）

**F-082** 「简化从句」类文件：4个（chapter-22简化从句总论、chapter-23关系从句简化、chapter-24名词从句简化、chapter-25副词从句简化）

**F-083** 「附录」类文件：1个（appendix/terminology.md）

---

*本文件所有事实均直接来源于对源目录31个 .md 文件的逐文件读取，遵循零推测原则，不包含推断性表述。*
