# Checklist

## 落位与范围
- [x] 新增 `yishu/liaoyu/` 分组共 6 束（liaoyu-overview / art-therapy / music-therapy / dance-drama-therapy / expressive-arts / china-art-therapy），未修改任何既有束内容
- [x] 每束结构完整：concepts/ + examples/ + references/ + 根 index.md（toctree）+ facts.md + log.md；总览束额外含 insights.md（83 个 .md 实测）

## 可靠性（G1 + R 阶段）
- [x] 各束 facts.md 合计 77 条编号事实（≥60），无因果推断词（grep 0 命中），每条带信源 URL
- [x] 关键历史事实（术语首创、人物年代、组织成立、专业设立）均有 ≥2 独立信源，维基百科未被用作唯一信源；讹传修正显式留痕（Nordoff 1977、Priestley 2017、Knill 1932-2020、Whitehouse 1979、中国音乐学院 1988）
- [x] 抽查 13 条事实回访信源：11 条一致、2 条 WHO 官方 URL 不可达（已在 sources.md 登记可达性审查记录与镜像源依据，非虚构引证）；学术异说并列呈现不武断裁决

## 原文与合规
- [x] 中医古籍原文（五音疗疾、情志相胜）双源逐字核对（ctext.org 四部丛刊本为主），四组异文显式标注"某本作某"，交叉链接 yixue/tcm、yixue/daoyi 既有束可跳转
- [x] 现代受版权保护著作（Hill/Naumburg/Kramer/Alvin/Bonny/Nordoff-Robbins/McNiff/Knill/Emunah 等）仅 1-2 句结论性引用 + 完整书目登记，引文块审查无整段转录
- [x] AATA/AMTA/ADTA/NADTA/IEATA/NAPT 定义引用附官网 URL（抽查逐字一致）
- [x] 循证结论（WHO 2019、Cochrane 四篇综述）可溯源，证据局限明示（中至低置信度/未见长期效应逐条保留），无夸大疗效、无虚构效应量
- [x] 组 index + 6 束根共 7 处显著位置有免责声明与"艺术治疗/艺术疗愈"边界提示
- [x] 中国束分层呈现：传统中医语境与现代循证语境分节、互不冒充，含话语体系分界专条

## 方法论（G2 + G3 + V）
- [x] insights.md 6 条四元组洞察（陈述/证据引用 48 个事实编号经核真实/反常识/行动），维度独立
- [x] 3 个可复用模式（双源核年法/引文分层法/五步职业化判读框架）：触发场景 + 核心步骤（3-7 步）+ 各 3 个反模式 + 检验标准 + 跨领域迁移示例
- [x] 每束 log.md 记录 R-I-E-V-C 各阶段执行摘要

## 格式与导航
- [x] 全部文档 OKF v0.2 frontmatter 合规（type 必填、sources 溯源、generated/status/stale_after）；yaml.safe_load 解析 83 文件全过，双引号标量内无 ASCII 双引号（中文用全角“”）
- [x] 正文中文、文件名 kebab-case 纯英文、相对路径无断链、无 file:/// 绝对路径
- [x] toctree 完整：束根 → concepts/examples/references/facts(/insights)/log；组 index → 各束；check-toctrees 确认无孤立文档、全部可达

## 索引对账
- [x] `yishu/liaoyu/index.md`、`yishu/index.md`、`bundles/index.md` 三级索引全部更新
- [x] `bundles/index.md` 五面一致：frontmatter 计数（389 束/44 组/9 域，含并行会话 kexue +5 束合并）、正文计数行、yishu 分组表行（7 束·2 组）、mermaid 节点、toctree
- [x] 质量门三门全部通过：check-utf8（7518 文件）、check-toctrees、check-bundles-index（9 域/44 组/389 束三角对账）+ 自检探针（等效 `invoke gates.all`，因环境缺 `invocations` 模块改为直跑底层脚本）

## 提交
- [x] 按束原子提交 7 个（6 束各一提交 + 索引一提交），Conventional Commits 中文主体，UTF-8 -F 方式无乱码
- [x] pathspec 限定提交实现暂存隔离：`git status` 复核并行会话已暂存的 kexue 文件原样保留、未被带走；共享文件 bundles/index.md 以门禁通过的合并态入库（如实报告）
- [x] 仅本地提交、未推送子模块与主仓库（推送闸门维持用户指令）
