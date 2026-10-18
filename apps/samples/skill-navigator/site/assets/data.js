// Skill 导航台 · 数据层
// ---------------------------------------------------------------------------
// 数据来源（两条真实来源页，同主题不同署名的条目各自登记，不判同一性）：
//   market = https://meoo.com/skills        （技能市场页，含累计使用量）
//   event  = https://ahhap1kka804.events.meoo.com/…/#/skills
//                                          （应用赏金广场「AI Builder Growth 共创计划」页，无使用量）
// 快照日期：2026-10-18
//
// 字段口径：
//   desc       —— 来源页简介，逐字保留，不改写
//   usage      —— 市场页累计使用量数字；事件页条目不提供 → null（UI 显示「事件页未提供」）
//   solve/fit/notFor/demo —— 本页整理（非平台官方口径），UI 上统一标注为「本页整理」
// 本文件不含任何网络请求；页面运行时零外部请求。
// ---------------------------------------------------------------------------

window.SKILL_DATA = {
  snapshot: '2026-10-18',
  sources: {
    market: { label: 'Meoo 技能市场页', url: 'https://meoo.com/skills' },
    event: { label: '应用赏金广场共创计划页', url: 'https://ahhap1kka804.events.meoo.com/#/skills' }
  },
  marketUrl: 'https://meoo.com/skills',

  // 痛点卡（两组）：卡文案为第一人称口语句；tags 为该卡命中的能力标签
  pains: [
    { id: 'p1', group: '我想做点什么', label: '我不会写代码，但想先做个小工具试试', tags: ['app', 'prototype', 'ui-polish'], top: ['ev-design-to-app', 'hunt-ui-specialist'] },
    { id: 'p2', group: '我想做点什么', label: '我想做个好看的网页 / 产品官网', tags: ['web', 'design', 'ui-polish'] },
    { id: 'p3', group: '我想做点什么', label: '我想做一份 PPT / 汇报演示页', tags: ['slide', 'doc'] },
    { id: 'p4', group: '我想做点什么', label: '我想做张图 / 海报 / 封面', tags: ['image', 'cover'] },
    { id: 'p5', group: '我想做点什么', label: '我想把资料、课程、笔记变成能卖的产品', tags: ['teach', 'content', 'doc'], top: ['hunt-xigua-productize', 'hunt-chinese-book'] },
    { id: 'p6', group: '我想做点什么', label: '我想做视频 / 把脚本变成动画', tags: ['video', 'animation'], top: ['ev-script-to-animation', 'ev-multi-platform-video'] },
    { id: 'p7', group: '我想做点什么', label: '我想做数据图表 / 地图', tags: ['data', 'map'] },

    { id: 'p8', group: '我卡在哪一步', label: '我有个模糊想法，不知道值不值得做', tags: ['idea-validate', 'brainstorm', 'plan'] },
    { id: 'p9', group: '我卡在哪一步', label: '我做完了，但没人用 / 不知道怎么推', tags: ['launch', 'audience', 'growth'], top: ['hunt-first-users', 'ev-growth-diag'] },
    { id: 'p10', group: '我卡在哪一步', label: '我不知道该卖多少钱 / 怎么变现', tags: ['pricing', 'price-cost'] },
    { id: 'p11', group: '我卡在哪一步', label: '界面很丑 / 设计稿还原不出来', tags: ['design', 'ui-polish', 'prototype'] },
    { id: 'p12', group: '我卡在哪一步', label: '代码有 bug / 想找人帮我检查', tags: ['code-quality', 'dev'], top: ['hunt-code-quality', 'hunt-code-reviewer'] },
    { id: 'p13', group: '我卡在哪一步', label: '用户反馈一大堆，不知道先改哪个', tags: ['feedback', 'growth'] },
    { id: 'p14', group: '我卡在哪一步', label: '想蹭热点 / 发小红书不知道写什么', tags: ['xhs', 'content', 'launch'] }
  ],

  // 标签中文名（用于回显「命中了什么」）
  tagLabels: {
    'web': '网页 / 网站', 'app': '应用 / 工具', 'design': '界面设计', 'slide': '演示 / PPT',
    'image': '图片 / 海报', 'video': '视频', 'doc': '文档 / 写作', 'data': '数据 / 图表',
    'content': '内容 / 文案', 'teach': '教学 / 课程',
    'idea-validate': '需求判断', 'launch': '首发推广', 'growth': '增长留存', 'pricing': '定价策略',
    'code-quality': '代码质量', 'dev': '开发 / 工程', 'feedback': '用户反馈', 'audience': '获客 / 冷启动', 'cover': '封面 / 视觉素材',
    'map': '地图 / 可视化', 'prototype': '设计稿转代码', 'ui-polish': '界面美化', 'plan': '计划 / 项目管理',
    'brainstorm': '发散 / 需求探索', 'xhs': '小红书 / 热点', 'price-cost': '成本核算', 'animation': '动画'
  },

  skills: [
    // ---------------- 市场页（market，含使用量） ----------------
    {
      id: 'hunt-brainstorm', name: '头脑风暴（Superpower）', author: 'Meoo开源收录', usage: 25445, source: 'market',
      desc: `任何创造性工作前必须使用。通过自然对话深入探索用户意图、需求和设计方案，确保在实施前完全理解需求。适用于创建功能、构建组件、添加功能或修改行为。`,
      solve: '在你动手之前，用对话把你的真实意图、需求和方案聊清楚。',
      fit: '想法还很模糊、说不清要做什么的人；要在开工前把需求问透的人。',
      notFor: '需求已经写得很清楚、只差执行的人——它会显得绕。',
      tags: ['brainstorm', 'idea-validate', 'plan'],
      demo: {
        input: '我想做个给自己用的小工具，但说不清要做成什么样。',
        steps: ['用对话逐个追问你的使用场景、真实痛点与已有替代方案', '把散乱描述收敛成「用户 / 场景 / 需求」三行结论', '给出可实施的方案轮廓与还需要确认的空白点'],
        deliverables: ['一页需求澄清结论（谁用、什么时候用、解决什么）', '方案轮廓 + 待确认清单']
      }
    },
    {
      id: 'hunt-ui-ux', name: '【Meoo】高级UI/UX 设计智能系统', author: 'Meoo编辑部', usage: 37115, source: 'market',
      desc: `Meoo UI UX，基于 140+ 精选设计方案，为你推荐最佳视觉风格。适用于 SaaS、电商、金融科技等项目场景，并产出可直接落地的 shadcn/ui + Tailwind CSS 代码。 核心能力包括：风格推荐、设计令牌生成、组件搭配方案、响应式布局指导、调色板构建以及风格评分系统。`,
      solve: '说清你的项目是什么，它从 140+ 种设计方案里挑出最合适的视觉风格并给出代码。',
      fit: '要搭 SaaS / 电商 / 金融科技类界面、又定不下视觉风格的人。',
      notFor: '已经有完整设计规范、只差写代码的人；纯静态单页小站可能用不上整套体系。',
      tags: ['design', 'ui-polish', 'web'],
      demo: {
        input: '做一个给自由职业者用的记账 SaaS，想要专业但不冷的感觉。',
        steps: ['按行业与调性匹配候选视觉风格并给出评分与理由', '生成配色、字号、圆角、阴影等设计令牌', '输出组件搭配方案与响应式布局指导'],
        deliverables: ['一套设计令牌（颜色 / 字体 / 间距）', '可直接落地的组件搭配与页面布局方案']
      }
    },
    {
      id: 'hunt-ui-specialist', name: '秒悟UI设计专家', author: '行休', usage: 7652, source: 'market',
      desc: `秒悟智能设计推荐助手 - 只需描述您的 Web 应用需求，AI 就能从 130+ 种设计风格中为您推荐最合适的方案，并提供完整的设计系统和 shadcn/ui 开发指南，帮助快速落地项目。`,
      solve: '描述你的 Web 应用要做什么，它从 130+ 种设计风格里给出推荐与开发指南。',
      fit: '第一次做 Web 应用、完全没有设计方向的人。',
      notFor: '只需要改一两处样式的微调场景。',
      tags: ['design', 'ui-polish', 'web'],
      demo: {
        input: '一个面向家教的预约与小班排课应用，要清爽、家长看得懂。',
        steps: ['解析应用类型与目标用户，筛出适配风格', '输出该系统下的完整设计规范', '附 shadcn/ui 组件落地指南'],
        deliverables: ['推荐风格 + 理由', '设计系统说明与组件使用指南']
      }
    },
    {
      id: 'hunt-frontend-design', name: '前端设计SKILL', author: '厚钧德扑', usage: 3765, source: 'market',
      desc: `为你打造独具特色的精美网页界面。无论是单个组件还是完整应用，都能呈现专业级的设计水准。代码风格独特，拒绝千篇一律的“AI味”，让你的产品拥有令人眼前一亮的视觉体验。`,
      solve: '把网页界面做得有辨识度，而不是一眼看出是套模板。',
      fit: '在意「一眼看上去不像 AI 批量生成」的人；需要单组件或整页设计的人。',
      notFor: '只需要功能跑通、界面能用就行的内部工具。',
      tags: ['web', 'design', 'ui-polish'],
      demo: {
        input: '给我的独立博客做一个首页，希望有人味儿，不要烂大街的卡片风。',
        steps: ['确定页面信息层级与视觉主张', '为单页设计定制化的排版与配色', '产出组件结构与样式实现'],
        deliverables: ['首页界面方案与样式代码', '可复用的组件规范']
      }
    },
    {
      id: 'hunt-glass-ui', name: '玻璃拟态UI', author: '不周山', usage: 2477, source: 'market',
      desc: `打造清新透亮的现代界面设计，模拟真实玻璃的质感与光影效果。通过模糊背景营造层次感，配合简约字体和卡片布局，让界面既现代又富有质感。适合需要通透、轻盈视觉体验的项目，如移动端应用、数据仪表盘或个人作品集展示。`,
      solve: '做出通透、有质感的界面风格（毛玻璃质感 + 光影层次）。',
      fit: '做仪表盘、作品集、移动端应用，想要轻盈现代观感的人。',
      notFor: '强调严肃、密信息的后台管理系统——通透感会削弱阅读效率。',
      tags: ['design', 'ui-polish', 'web'],
      demo: {
        input: '做一个个人作品集首页，想要通透一点、别太厚重。',
        steps: ['按场景确定模糊强度、层次与卡片布局', '搭配简约字体与光影细节', '输出组件样式与配色'],
        deliverables: ['毛玻璃风格样式方案', '可复用的卡片与层级规范']
      }
    },
    {
      id: 'hunt-ui-restore', name: 'UI精准还原', author: 'ioo_pro', usage: 191, source: 'market',
      desc: `上传设计图，智能识别技术栈并生成像素级还原方案。涵盖组件选型、样式参数及交互逻辑，助您一键实现从 Figma 或截图到代码的精准转换，高效完成 UI 复刻与页面开发。`,
      solve: '上传设计图或截图，给出像素级还原的实现方案（组件选型 + 样式参数 + 交互）。',
      fit: '有 Figma 稿或参考截图、要照着做出来的人。',
      notFor: '还没有设计稿、需要先决定长什么样的阶段。',
      tags: ['prototype', 'design', 'ui-polish'],
      demo: {
        input: '［上传一张后台列表页的截图］照着这个还原一版。',
        steps: ['识别图中布局、组件与技术栈线索', '给出组件选型与样式参数（间距 / 字号 / 颜色）', '补齐交互逻辑与实现步骤'],
        deliverables: ['还原实现方案（组件 + 样式参数）', '交互逻辑说明']
      }
    },
    {
      id: 'hunt-high-end-frontend', name: '高质前端设计', author: '妮可miku', usage: 134, source: 'market',
      desc: `专为打造高质感网页而生，涵盖落地页、作品集及界面重设计。智能匹配官方设计系统，拒绝模板化“AI味”，呈现如Linear般精致的专业视觉效果。助您轻松构建独具匠心的高端前端界面，让设计脱颖而出。`,
      solve: '把落地页 / 作品集 / 旧界面重做成精致的高端观感。',
      fit: '要给产品做对外落地页、或想把现有界面整体提质感的人。',
      notFor: '只需要局部调整的场景。',
      tags: ['web', 'design', 'ui-polish'],
      demo: {
        input: '我的产品落地页看起来像模板，想做成 Linear 那种精致感。',
        steps: ['诊断现有页面的观感问题', '匹配官方设计系统并给出改造方向', '产出版式与视觉细节实现'],
        deliverables: ['改造后的页面方案', '视觉细节规范']
      }
    },
    {
      id: 'hunt-product-site', name: '高审美产品官网', author: '郑建勋', usage: 141, source: 'market',
      desc: `提供产品资料，完成设计参考选择、Logo与图片准备、响应式页面、品牌化液态金属交互和检查修复。结合自动检查与人工截图复核，适用于产品官网、品牌展示页和发布页。zebrazjx × 秒悟 Meoo 共创。本地已有案例验证，Meoo 端完整运行仍待验收；浏览器检查需宿主提供相应工具。`,
      solve: '从产品资料出发，把产品官网 / 发布页整站做出来并做检查修复。',
      fit: '要上线产品官网、品牌展示页、发布页的人。',
      notFor: '只做单页小工具的人；作者已标注 Meoo 端完整运行仍待验收，介意者慎用。',
      tags: ['web', 'launch', 'ui-polish'],
      demo: {
        input: '［上传产品资料 + 想要的参考站风格］做一版发布页。',
        steps: ['选设计参考、准备 Logo 与配图', '产出响应式页面与品牌化交互', '自动检查 + 截图复核修复'],
        deliverables: ['响应式产品官网页面', '检查修复记录']
      }
    },
    {
      id: 'hunt-diagram-map', name: '中国全域地图展示', author: '一格', usage: 127, source: 'market',
      desc: `1分钟让你的地图成为标准地图！ 阿里云地图数据源获取，快速获取中国省市区行政区划地图数据，一键集成到 ECharts 实现数据可视化。适合制作数据地图、区域分析图表，让地图展示更加直观专业。`,
      solve: '拿到中国省市区行政区划数据，并把它接进 ECharts 做成可用的数据地图。',
      fit: '要做区域分布图、地区业务分析看板的人。',
      notFor: '要做全球 / 海外地图的人——数据源范围是中国行政区划。',
      tags: ['data', 'map'],
      demo: {
        input: '我要做一张各省销量分布图。',
        steps: ['获取省市区行政区划数据', '与你的数据字段做关联', '生成 ECharts 地图配置'],
        deliverables: ['标准地图数据', '可直接运行的 ECharts 地图配置']
      }
    },
    {
      id: 'hunt-map-ppt', name: 'PPT精编', author: '朱鹮', usage: 99, source: 'market',
      desc: `一键生成专业级可编辑网页PPT，告别AI模板的廉价感。支持逐页定制命题与排版，完美适配汇报、课件及演示场景。内容灵活可调，助您轻松打造独具匠心、逻辑清晰的高质量幻灯片，让每一次展示都脱颖而出。`,
      solve: '生成可逐页编辑的网页版 PPT，而不是套模板的廉价感稿子。',
      fit: '要做汇报、课件、路演的人；需要事后逐页改内容的人。',
      notFor: '要输出 .pptx 文件、必须在传统 Office 里放映的人。',
      tags: ['slide', 'doc'],
      demo: {
        input: '帮我做一份 10 页的季度复盘汇报，重点是三个数据结论。',
        steps: ['按汇报目标拆页与命题', '逐页生成排版与图示', '给出可继续编辑的结构'],
        deliverables: ['可编辑的网页 PPT', '每页命题与要点']
      }
    },
    {
      id: 'hunt-frontend-slides', name: 'Frontend-Slides 幻灯片生成', author: '山间14', usage: 85, source: 'market',
      desc: `轻松创建精美网页幻灯片，支持从零设计或一键转换 PPT。无需复杂依赖，通过直观视觉预览，助非设计师快速锁定美学风格。无论是演讲、路演还是日常汇报，都能高效打造专业且动感的演示体验。技能来自开源项目：https://github.com/zarazhangrui/frontend-slides?tab=readme-ov-file`,
      solve: '把已有 PPT 或一个主题，转成带视觉预览的网页幻灯片。',
      fit: '手上已有一份 PPT、想换成网页形态的人；非设计师。',
      notFor: '需要多人协作批注、走企业模板审批的场景。',
      tags: ['slide', 'doc', 'animation'],
      demo: {
        input: '［上传现有 PPT］把它变成网页幻灯片，风格更现代一点。',
        steps: ['解析原稿结构与内容层级', '匹配美学风格并预览确认', '生成动感的网页幻灯片'],
        deliverables: ['网页幻灯片成品', '风格预览与切换选项']
      }
    },
    {
      id: 'hunt-code-quality', name: '代码质控', author: '无心低语gd', usage: 3251, source: 'market',
      desc: `代码质量守护者 - 每次代码提交后自动进行全面"体检"，快速发现代码规范问题、安全隐患、性能瓶颈和测试盲区，帮助团队持续保持高质量代码输出。`,
      solve: '每次提交后自动体检代码：规范问题、安全隐患、性能瓶颈、测试盲区。',
      fit: '有人协作的代码仓库；要长期保持质量的项目。',
      notFor: '一次性脚本、跑完就丢的代码。',
      tags: ['code-quality', 'dev'],
      demo: {
        input: '［提交代码后触发］帮我看看这次改动有什么问题。',
        steps: ['扫描规范问题与安全隐患', '定位性能瓶颈与测试盲区', '按严重程度给出修复建议'],
        deliverables: ['按严重度排序的问题清单', '修复建议']
      }
    },
    {
      id: 'hunt-code-reviewer', name: '代码审查专家', author: 'liping', usage: 198, source: 'market',
      desc: `智能审查代码与日志，精准识别安全、性能及逻辑隐患。无论是日常 Code Review 还是排查 Bug，它都能提供按严重程度排序的最小化修复建议，助您高效评估风险，轻松提升代码质量与维护效率。`,
      solve: '审代码和日志，按严重程度排序给出「最小改动」的修复建议。',
      fit: '要代码走查的人；手里有报错日志想定位隐患的人。',
      notFor: '期望它直接替你重写整套架构的场景。',
      tags: ['code-quality', 'dev'],
      demo: {
        input: '［贴上这段接口代码和一段报错日志］帮我看问题在哪。',
        steps: ['结合日志定位可疑逻辑与隐患', '区分安全 / 性能 / 逻辑三类问题', '给出最小化修复建议并排序'],
        deliverables: ['分级问题清单', '最小修复补丁建议']
      }
    },
    {
      id: 'hunt-test-agent', name: '超级牛马测试员', author: '文行九知', usage: 1377, source: 'market',
      desc: `智能代码测试助手 - 自动检测代码问题、定位bug根源、修复常见错误，并提供性能分析报告。适合开发者在编码过程中快速验证代码质量、排查故障、提升性能。`,
      solve: '边写边测：自动查出问题、定位 bug 根源、顺手修掉常见错误。',
      fit: '个人开发者；编码过程中想快速自检的人。',
      notFor: '需要成体系的测试工程（覆盖率门禁、CI 流水线）的团队场景。',
      tags: ['code-quality', 'dev'],
      demo: {
        input: '［给一个报错的函数］它跑不通，帮我看看哪里错了。',
        steps: ['复现并检测代码问题', '定位 bug 根源', '修复常见错误并给出性能提示'],
        deliverables: ['bug 根因说明', '修复后的代码 + 性能分析']
      }
    },
    {
      id: 'hunt-user-research', name: 'AI产品调研', author: '北峰Agent', usage: 55, source: 'market',
      desc: `专为数字产品打造的结构化调研助手，助您快速验证AI工具、小程序等创意需求。无论是判断是否上线还是优化迭代，都能提供清晰的数据反馈，帮您精准决策，避免盲目开发，让产品打磨更高效。`,
      solve: '给 AI 工具、小程序这类创意做结构化调研，回答「该不该做、做得对不对」。',
      fit: '要判断是否上线、或要决定下一步迭代方向的人。',
      notFor: '已经有大量真实用户数据、只差看数的场景；想做图表或地图本身的话，它不是制图工具。',
      tags: ['idea-validate', 'data'],
      demo: {
        input: '我想做一个给宝妈用的辅食记录小程序，值得做吗？',
        steps: ['拆解创意对应的用户与场景', '检索可得的公开信息与同类产品情况', '汇总结论与不确定项'],
        deliverables: ['结构化调研结论（含判断依据）', '尚未确认的空白清单']
      }
    },
    {
      id: 'hunt-first-users', name: '首批用户获取', author: 'anyu1888888', usage: 20, source: 'market',
      desc: `专为已有产品的创作者设计，助您精准锁定首批用户，明确画像与动机。一键生成发布文案、沟通话术及七天冷启动计划，解决从0到1的获客难题。适合急需真实反馈与试用的场景，非付费投放或群发工具。`,
      solve: '已有产品、要第一批真实用户：定位人群，给发布文案与 7 天冷启动计划。',
      fit: '产品刚做完、急需真实反馈和试用的人。',
      notFor: '想投付费广告、或想做群发轰炸的人——作者明确说明不是这类工具。',
      tags: ['audience', 'launch', 'growth'],
      demo: {
        input: '我的简历优化小工具做完了，第一批用户从哪来？',
        steps: ['从产品反推首批用户画像与动机', '生成发布文案与沟通话术', '排出 7 天冷启动动作'],
        deliverables: ['用户画像 + 去哪找', '发布文案与 7 天计划表']
      }
    },
    {
      id: 'hunt-github-stars', name: 'GitHub星标增长器', author: '常成', usage: 16, source: 'market',
      desc: `帮助你的 GitHub 项目，大大增加获取更多星标的可能！ 具体方式是判断你说的用户、场景、需求的真伪程度。 用四个关键问题帮你找到真正会用它的"那群人"，然后把仓库名、简介、README 按真用户、真需求、真场景来重写/优化。 让你的GitHub项目获取更多Stars！`,
      solve: '用四个关键问题检验你的开源项目「谁真的会用」，再据此重写仓库名、简介与 README。',
      fit: '有 GitHub 开源项目、想涨星的人。',
      notFor: '闭源商业项目；只想刷量而不是真找用户的人。',
      tags: ['launch', 'audience', 'growth'],
      demo: {
        input: '［贴上我的仓库名、简介和 README］为什么没什么人点星？',
        steps: ['用四个关键问题检验用户 / 场景 / 需求真伪', '定位真正会用它的那群人', '重写仓库名、简介与 README'],
        deliverables: ['用户真伪判断结论', '重写后的仓库名 / 简介 / README']
      }
    },
    {
      id: 'hunt-launch-kit', name: '应用首发包助手', author: '桃子_0616', usage: 12, source: 'market',
      desc: `刚完成应用或教程却不知如何推广？本技能为您一键生成首发文案与数据解读指南。从第一条内容发布到关键指标分析，助您轻松搞定冷启动，让好产品迅速获得市场关注与反馈。`,
      solve: '产品刚做完不知怎么推：一键出首发文案 + 关键数据怎么看。',
      fit: '第一次做推广、不懂该看什么指标的人。',
      notFor: '已经有一套成熟推广流程的运营团队。',
      tags: ['launch', 'content'],
      demo: {
        input: '我做了个记账小工具，第一条推广内容怎么写？',
        steps: ['从产品提炼首发角度', '产出首发文案', '给出关键指标与解读方式'],
        deliverables: ['首发文案', '关键指标解读指南']
      }
    },
    {
      id: 'hunt-caitou-launch', name: '菜头应用首发素材包', author: '菜头Prompt', usage: 16, source: 'market',
      desc: `一键为您的应用生成首发宣传素材！只需提供产品链接或截图，即可自动提炼核心卖点，产出精美图文、宣传海报及演示脚本。完美适配新品上线、公测招募等场景，助您轻松完成首次亮相，专注内容创作，无需操心发布与推广。`,
      solve: '给产品链接或截图，产出核心卖点、图文、海报与演示脚本一套首发素材。',
      fit: '新品上线、公测招募，需要一整套宣传物料的人。',
      notFor: '只想写一句朋友圈文案的轻量场景。',
      tags: ['launch', 'content', 'image'],
      demo: {
        input: '［贴上产品链接］帮我出一套首发素材。',
        steps: ['从链接 / 截图提炼核心卖点', '生成图文与宣传海报', '输出演示脚本'],
        deliverables: ['核心卖点 + 图文素材', '宣传海报与演示脚本']
      }
    },
    {
      id: 'hunt-caitou-surf', name: '菜菜的冲浪Skill', author: 'caibucai', usage: 30, source: 'market',
      desc: `专注小红书营销，基于真实热帖挖掘传播机会。通过对比选题，为您生成可执行的推广内容。适用于寻找产品热点、制定冲浪策略或撰写传播报告。虽不保证爆款且需手动发布，但能助您精准捕捉流量，高效规划内容。`,
      solve: '在小红书上找传播机会：从真实热帖里对选题，产出可执行的推广内容。',
      fit: '要规划小红书内容、找产品热点的人。',
      notFor: '期望自动发布 / 保证爆款的人——作者明确说明不保证爆款且需手动发布。',
      tags: ['xhs', 'content', 'launch'],
      demo: {
        input: '我卖手工皂，小红书上该发什么内容？',
        steps: ['挖掘同类真实热帖与传播点', '对比候选选题', '生成可执行的推广内容'],
        deliverables: ['选题对比与建议', '可发布的推广内容']
      }
    },
    {
      id: 'hunt-xigua-productize', name: '西瓜业务产品化｜xigua-service-productization', author: '西瓜🍉', usage: 25, source: 'market',
      desc: `将你的业务文档、案例等专业内容转化为内容型产品。它不仅能提升客户参与度，还能自动生成建站提示词，帮您快速搭建专属网站，让专业知识轻松变现，高效连接潜在客户。`,
      solve: '把你的业务文档、案例变成内容型产品，并给出建站提示词。',
      fit: '手里有专业资料、课程笔记，想变成产品的人。',
      notFor: '没有任何现成素材、需要从零创作内容的人。',
      tags: ['teach', 'content', 'web'],
      demo: {
        input: '［上传我的咨询案例文档］帮我做成能给客户看的互动产品。',
        steps: ['梳理资料并设计互动形态（自测 / 预诊断等）', '转化为内容型产品结构', '生成建站提示词'],
        deliverables: ['内容型产品方案', '可直接使用的建站提示词']
      }
    },
    {
      id: 'hunt-chinese-book', name: '语文书籍模板', author: '一格', usage: 373, source: 'market',
      desc: `轻松打造语文整本书阅读应用！基于高效模板，支持动态加载书籍内容与导航。无论是定制教材、切换书目，还是按教学约束生成内容，都能快速实现。让阅读体验更灵活，助力师生畅享沉浸式语文学习之旅。`,
      solve: '用模板快速做一个整本书阅读应用，支持换书目、按教学约束生成内容。',
      fit: '语文老师、做阅读类教学产品的人。',
      notFor: '非语文 / 非整本书阅读的教学场景。',
      tags: ['teach', 'doc'],
      demo: {
        input: '我想给初一学生做一个《朝花夕拾》的整本书阅读应用。',
        steps: ['套用阅读应用模板并载入书目内容', '按教学约束生成导读与任务', '配置导航与切换书目'],
        deliverables: ['整本书阅读应用', '导读 / 任务内容']
      }
    },
    {
      id: 'hunt-plan-superpower', name: '计划编写（Superpower）', author: 'Meoo开源收录', usage: 2654, source: 'market',
      desc: `编写全面的实施计划文档。针对多步骤任务，提供详细的文件修改清单、代码示例、测试方案和文档需求，遵循 DRY、YAGNI、TDD 原则，适合零上下文的工程师执行。`,
      solve: '把多步骤任务写成一份「换个人也能照着做」的实施计划文档。',
      fit: '要交接给他人执行、或自己隔几天再回来做的事。',
      notFor: '一两个小时就能做完的小改动。',
      tags: ['plan', 'doc'],
      demo: {
        input: '我要给项目加一个登录功能，帮我把计划写出来。',
        steps: ['拆解任务为可执行步骤', '列出文件修改清单与代码示例', '附测试方案与文档需求'],
        deliverables: ['实施计划文档（含修改清单）', '测试与文档要求']
      }
    },
    {
      id: 'hunt-haiming-monetize', name: '海明 App 商业化｜haiming-app-monetization', author: '黄明远', usage: 14, source: 'market',
      desc: `海明Dev与秒悟Meoo联手，深度评估App引导、付费墙及定价策略。结合代码与竞品分析，提供定制化转化方案。专注优化试用与购买体验，助力开发中或已上线App提升商业化效率，非单纯获客工具。`,
      solve: '评估 App 的引导流程、付费墙与定价，给出提高付费转化的具体方案。',
      fit: '已经上线或开发中、想把付费转化做起来的 App 作者。',
      notFor: '要单纯买量获客的场景——作者明确说明不是获客工具。',
      tags: ['pricing', 'growth'],
      demo: {
        input: '［描述我的 App 与当前付费点］为什么试用的人很少付钱？',
        steps: ['评估引导、付费墙与定价现状', '结合代码与同类产品对比', '给出定制的转化方案'],
        deliverables: ['转化问题诊断', '定制化付费转化方案']
      }
    },
    {
      id: 'hunt-signalmine', name: 'SignalMine｜用户反馈转增长实验', author: 'Z_wk', usage: 12, source: 'market',
      desc: `SignalMine（中文名：用户反馈转增长实验）。把用户评论、客服记录、问卷和访谈，整理成有原话依据的痛点优先级、最多 3 条待验证增长假设，以及 1 个可执行的最小实验。支持文件时生成可点击的结果看板和空白实验记录表；只能聊天时提供 Markdown 卡片。 使用方法：添加技能后，说明产品用途、目标用户、希望改善的动作与可改范围，再粘贴反馈或上传平台可读取的附件。无需提前编号或分类；未读内容与未知信息会明确说明。 首次体验可发送：“请读取本技能 examples/quick-demo.txt，运行短示例，输出优先级、原话依据、增长假设和一个最小实验，并展示结果。”包内附使用指南、匿名真实短示例与明确标记的模拟测试数据。生成的是待执行方案，增长效果需通过真实实验验证。`,
      solve: '把一堆用户反馈整理成「痛点优先级 + 增长假设 + 一个最小实验」。',
      fit: '手里有评论 / 客服记录 / 问卷，不知道先改哪个的人。',
      notFor: '手上还没有任何真实用户反馈的阶段。',
      tags: ['feedback', 'growth'],
      demo: {
        input: '［粘贴 50 条用户评论］帮我排一下该先改什么。',
        steps: ['逐条归类并保留原话依据', '排出痛点优先级', '给出增长假设与最小实验'],
        deliverables: ['带原话依据的痛点优先级', '待验证假设 + 最小实验方案']
      }
    },
    {
      id: 'hunt-ai-image', name: 'AI图像生成', author: '尤达大师love', usage: 1608, source: 'market',
      desc: `这款AI图像工具可以帮你用文字描述生成图片，或上传现有图片进行修改。支持多种分辨率(1K/2K/4K)，无论是创作新作品还是编辑现有图片都能轻松搞定。`,
      solve: '用文字生成图片，或上传已有图片修改，支持 1K / 2K / 4K。',
      fit: '做文章配图、海报底图、概念图的人。',
      notFor: '需要精确排版与文字元素的成品海报——生成模型对文字与版式控制有限。',
      tags: ['image', 'cover'],
      demo: {
        input: '给一篇讲咖啡的文章配一张封面图，暖色调、不要文字。',
        steps: ['把描述转成生成参数', '按目标分辨率出图', '按反馈修改'],
        deliverables: ['1K 封面图', '可继续调整的修改入口']
      }
    },

    // ---------------- 赏金广场共创计划页（event，无使用量） ----------------
    {
      id: 'ev-need-validate', name: '产品需求验证判断', author: '北峰Agent', usage: null, source: 'event',
      desc: `把「我觉得有人需要」变成看得懂、查得到的产品判断`,
      solve: '把「我觉得有人需要」变成一份看得懂、查得到的判断。',
      fit: '只有一个直觉、说不出证据的人。',
      notFor: '已经做过充分用户访谈、只差开发的人。',
      tags: ['idea-validate', 'brainstorm'],
      demo: {
        input: '我觉得上班族都需要一个自动整理发票的工具，可行吗？',
        steps: ['把直觉拆成可检验的判断项', '查证可得的公开依据与替代方案', '给出结论与依据'],
        deliverables: ['产品需求判断结论', '判断依据与不确定项']
      }
    },
    {
      id: 'ev-true-need', name: 'AI 产品真需求诊断', author: 'yan（ai赚钱版）', usage: null, source: 'event',
      desc: `判断产品没人用是增长问题还是需求本身不成立`,
      solve: '回答「没人用」到底是推广没做到位，还是这件事本来就没需求。',
      fit: '已经做出产品、用的人很少的人。',
      notFor: '还没有产品形态、只在想法阶段的人。',
      tags: ['idea-validate', 'feedback'],
      demo: {
        input: '我的番茄钟 App 上线两个月，日活一直是个位数，问题出在哪？',
        steps: ['区分「增长不足」与「需求不成立」两类信号', '对照现有动作与结果找证据', '给出结论与下一步'],
        deliverables: ['问题归因结论', '下一步动作建议']
      }
    },
    {
      id: 'ev-need-sim', name: 'AI 应用需求模拟调研', author: '阿东玩AI', usage: null, source: 'event',
      desc: `动手前检索近30天用户抱怨与付费线索 结合有来源的模拟访谈给出需求判断与7天验证计划`,
      solve: '开工前先检索近 30 天用户抱怨与付费线索，给出需求判断和 7 天验证计划。',
      fit: '准备动手、但想先花一周验证需求的人。',
      notFor: '已经进入开发、只想优化实现的人。',
      tags: ['idea-validate', 'data'],
      demo: {
        input: '我想做一个宠物寄养匹配平台，动手前该怎么验证？',
        steps: ['检索近 30 天相关抱怨与付费线索', '做有来源的模拟访谈', '给出 7 天验证计划'],
        deliverables: ['需求判断（含来源）', '7 天验证计划']
      }
    },
    {
      id: 'ev-real-need', name: '真需求验证器', author: '南洋理工DAN讲AI', usage: null, source: 'event',
      desc: `帮 AI Builder 判断产品是否有真实需求 找到最小可卖单元与最合适的定价验证方式`,
      solve: '判断有没有真实需求，并找出「最小可卖单元」与合适的定价验证方式。',
      fit: '想先卖一小部分、验证有没有人掏钱的人。',
      notFor: '纯免费、完全不考虑收费的项目。',
      tags: ['idea-validate', 'pricing'],
      demo: {
        input: '我的服务要不要收费？该怎么试水？',
        steps: ['判断需求真实性', '切出最小可卖单元', '匹配定价验证方式'],
        deliverables: ['需求真实性判断', '最小可卖单元 + 定价验证方案']
      }
    },
    {
      id: 'ev-design-to-app', name: '一键设计稿转应用', author: '职场懒人', usage: null, source: 'event',
      desc: `把设计稿或截图直接变成能跑的应用并比对还原度`,
      solve: '把设计稿或截图直接变成能跑的应用，并比对还原度。',
      fit: '有设计稿、想跳过手写界面的人；不会写代码的人。',
      notFor: '没有设计稿、需要先决定界面的阶段。',
      tags: ['prototype', 'app', 'design'],
      demo: {
        input: '［上传三张页面设计稿］把它变成一个能点的小应用。',
        steps: ['解析设计稿结构并生成页面', '串起页面间跳转', '与设计稿比对还原度并修正'],
        deliverables: ['可运行的应用页面', '还原度比对记录']
      }
    },
    {
      id: 'ev-cost-pricing', name: 'AI 应用成本核算与定价', author: '古希腊掌管代码的神', usage: null, source: 'event',
      desc: `为 AI 应用做成本核算与定价变现方案`,
      solve: '算清 AI 应用的成本（含模型调用消耗），并给出定价与变现方案。',
      fit: '用到大模型、担心越用越亏的人。',
      notFor: '不调用任何模型、成本结构简单的项目。',
      tags: ['price-cost', 'pricing'],
      demo: {
        input: '我的写作助手每用一次要花多少钱？该定价多少？',
        steps: ['按用量核算单次成本', '统计成本结构占比', '给出定价与变现方案'],
        deliverables: ['成本核算表', '定价 / 变现方案']
      }
    },
    {
      id: 'ev-growth-diag', name: '产品增长诊断', author: '小E爱学习（AI提效）', usage: null, source: 'event',
      desc: `在一堆增长建议里判断当前最该先解决哪一个`,
      solve: '在一堆增长建议里，判断现在最该先做哪一个。',
      fit: '手里攒了一堆增长建议、不知道从哪下手的人。',
      notFor: '还没到增长阶段、产品还在做原型的人。',
      tags: ['growth', 'feedback'],
      demo: {
        input: '有人让我做 SEO、有人说要投广告、还有人让我做私域，先做哪个？',
        steps: ['对照当前阶段与瓶颈筛选建议', '按投入产出与前置条件排序', '给出当前唯一优先项'],
        deliverables: ['优先级排序与理由', '当前该做的第一件事']
      }
    },
    {
      id: 'ev-growth-lead', name: '产品增长负责人诊断', author: '花叔（只工作不上班版）', usage: null, source: 'event',
      desc: `把数据丢进来判断增长卡在哪一段 只给当前该做的三件事和哪些事做还太早`,
      solve: '把数据丢进去，判断增长卡在哪一段，只给「现在该做的三件事」和哪些还太早。',
      fit: '有基础数据、要做取舍的小团队 / 独立开发者。',
      notFor: '完全没有数据、无法量化现状的阶段。',
      tags: ['growth', 'data'],
      demo: {
        input: '［贴上近 4 周访问 / 注册 / 付费数据］问题出在哪一段？',
        steps: ['按漏斗定位卡点', '区分当下该做与为时过早的动作', '给出三件事清单'],
        deliverables: ['漏斗卡点定位', '现在该做的三件事 + 还太早的清单']
      }
    },
    {
      id: 'ev-script-to-animation', name: '文字脚本转可视化白板动画', author: '李叔聊AI', usage: null, source: 'event',
      desc: `上传脚本自动生成教程口播用的白板动画`,
      solve: '上传文字脚本，自动生成教程口播用的白板动画。',
      fit: '做教程、讲解类视频、需要口播配画面的人。',
      notFor: '需要复杂实拍与特效的影视级制作。',
      tags: ['video', 'animation', 'teach'],
      demo: {
        input: '［上传一段 300 字的讲解脚本］帮我配白板动画。',
        steps: ['切分脚本为分镜', '把每段转成白板绘制动作', '输出可直接口播配的画面'],
        deliverables: ['白板动画视频', '分镜与脚本对应表']
      }
    },
    {
      id: 'ev-multi-platform-video', name: '多平台推广视频生成', author: '一起Vibe', usage: null, source: 'event',
      desc: `一份素材产出多平台尺寸的推广视频与封面图`,
      solve: '一份素材，产出适配多个平台的尺寸的推广视频与封面图。',
      fit: '要在多个平台同时发推广视频的人。',
      notFor: '只发一个平台、只做单条内容的人。',
      tags: ['video', 'launch', 'content'],
      demo: {
        input: '［上传一段产品演示录屏］我要发抖音、B站和小红书。',
        steps: ['按各平台规格裁切与适配', '生成配套封面图', '输出成套素材'],
        deliverables: ['多平台尺寸视频', '配套封面图']
      }
    },
    {
      id: 'ev-note-cover', name: '笔记封面设计', author: '是树小姐', usage: null, source: 'event',
      desc: `输入封面设计技巧与参考 解决主副标题设计与从视频提取关键帧的封面设计`,
      solve: '解决笔记封面的主副标题设计，并能从视频里提取关键帧做封面。',
      fit: '发小红书 / 视频、封面总是差点意思的人。',
      notFor: '需要整套视觉系统而非单张封面的人。',
      tags: ['cover', 'image', 'xhs'],
      demo: {
        input: '［给一个视频链接 + 参考封面］帮我做张封面，标题要抓人。',
        steps: ['提取视频关键帧作为底图', '设计主副标题层级与排布', '输出封面成品与备选'],
        deliverables: ['封面成品（含主副标题）', '备选底图与排版']
      }
    },
    {
      id: 'ev-content-advisor', name: '内容选题咨询顾问', author: '塔斯海', usage: null, source: 'event',
      desc: `用深层方法论结合经验解决选题、内容逻辑与钩子拿捏不住的问题`,
      solve: '用方法论解决选题、内容逻辑、钩子拿捏不准的问题。',
      fit: '持续做内容、总是卡在「写什么 / 怎么开头」的人。',
      notFor: '只需要文案润色的场景。',
      tags: ['content', 'xhs'],
      demo: {
        input: '我做职场内容，最近选题越来越平，怎么办？',
        steps: ['诊断选题与内容逻辑的问题', '给出选题方向与钩子写法', '排出可执行的内容清单'],
        deliverables: ['选题诊断与方向', '钩子写法示例']
      }
    },
    {
      id: 'ev-hotspot-surf', name: '热点自传播网感冲浪', author: '蔡不菜（AI版）', usage: null, source: 'event',
      desc: `输入产品输出本周可蹭热点的冲浪图与蹭法避雷 一键生成蹭热点发布帖`,
      solve: '输入产品，输出本周可蹭的热点、蹭法与避雷提示，并生成发布帖。',
      fit: '要借热点给产品做曝光的人。',
      notFor: '不适合蹭热点的严肃行业 / 敏感品类。',
      tags: ['xhs', 'launch', 'content'],
      demo: {
        input: '我卖健身餐，这周有什么能蹭的热点？',
        steps: ['盘点本周可蹭热点与关联角度', '给出蹭法与避雷提示', '生成可发布的帖子'],
        deliverables: ['热点冲浪图（含避雷）', '蹭热点发布帖']
      }
    }
  ]
};
