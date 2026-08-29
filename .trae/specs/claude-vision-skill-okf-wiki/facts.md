# Facts：claude-vision-skill

> 主信源：微信公众号"macrozheng"，2026-08-21 14:10 发布
> URL：https://mp.weixin.qq.com/s/3AZbLPVwg45PrQSuvcJDHQ
> P0核验：6项全部 ✅ 通过（含3项时效性补充）

## 元信息（F-001）

| 编号 | 事实 |
|------|------|
| F-001 | 标题《DeepSeek V4 Pro 也能看图了！》，公众号macrozheng，2026-08-21 14:10 |

## 问题背景（F-002~F-005）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-002 | 用Claude Code接第三方纯文本模型时，发图片读图直接返回[Unsupported Image] | ✅ |
| F-003 | DeepSeek V4 Pro这类模型本身不带视觉能力 | ✅ 官方API文档确认：仅deepseek-v4-flash-vision-exp接受图片，其他模型返回400错误 |
| F-004 | DeepSeek V4 Pro正式版（DeepSeek-V4-Pro-0813）2026-08-13发布 | ✅ 官方更新日志 |
| F-005 | ⚠️时效性补充：DeepSeek首个多模态模型deepseek-v4-flash-vision-exp于2026-08-21上线（博文发布当天），基于V4-Flash实验性；V4 Pro截至核验日仍无视觉API | 补充核验 |

## 解决方案（F-006~F-010）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-006 | 思路：文本模型看不见图，找一个看得见的——先把图片发给支持视觉的模型转录成文字描述，再把文字交回文本模型推理 | ✅ 项目README一致 |
| F-007 | 对文本模型来说只是多收到一段上下文，但实际效果等于"看图" | — |
| F-008 | claude-vision-skill是该思路的轻量级开源实现：标准Claude Code Skill，配置好后直接发图片自动识图 | ✅ |
| F-009 | 项目地址 https://github.com/asuojun/claude-vision-skill ，作者asuojun，公开仓库 | ✅ 仓库存在，含vision.js/SKILL.md/clipboard.ps1/clipboard.swift |
| F-010 | 识图准确度/速度/成本取决于视觉模型；博文使用阿里云百炼qwen-vl-max | ✅ |

## 工作原理（F-011~F-017）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-011 | 链路：用户发图片→SKILL.md的description自动匹配触发→运行vision.js <图片路径> "<prompt>"→dotenv注入环境变量→图片base64→POST视觉模型API（OpenAI兼容格式）→返回文字描述→交回DeepSeek推理 | ✅ |
| F-012 | 真正"看图"的是视觉模型，DeepSeek拿到文字转录结果 | ✅ |
| F-013 | Skill机制：放~/.claude/skills/<skill-name>/SKILL.md，模型调用而非用户调用，Claude启动时预加载name/description进系统提示，按上下文自动决定加载，无需斜杠命令 | ✅ Anthropic官方机制 |
| F-014 | SKILL.md必须以YAML frontmatter开头，含name（≤64字符）和description（≤1024字符，含"做什么+何时用"） | ✅ |
| F-015 | ⚠️ 仓库SKILL.md硬编码了他人机器路径/Users/wwu/.codex/skills/claude-vision-skill/vision.js共3处（本地路径/--url/--clipboard三种场景），最近提交者为waynewu411非作者本人，且是Codex路径，需替换为本机绝对路径 | ✅ 核验确认 |
| F-016 | ⚠️ 仓库README主推安装方式是"场景A"：vision.js拷到项目根目录+合并CLAUDE.md，并非~/.claude/skills/标准安装 | ✅ 核验补充 |
| F-017 | vision.js加载.env的require("dotenv")包在try{}catch{}里，不装dotenv会静默失败、Key退回默认值sk-xxx；必须在skill目录执行npm install dotenv——最容易踩的坑，不装不会报错但.env完全不生效 | ✅ |

## 安装配置（F-018~F-023）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-018 | git clone https://github.com/asuojun/claude-vision-skill.git 放到用户级skills目录~/.claude/skills/claude-vision-skill/（全局安装） | ✅ |
| F-019 | 在skill目录（vision.js旁边）创建.env，填三个配置项：DASHSCOPE_API_KEY（必填）、VISION_MODEL（qwen-vl-max或qwen3.5-omni-plus）、DASHSCOPE_BASE_URL | ✅ |
| F-020 | DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1（阿里云百炼OpenAI兼容接口，一般不用改） | ✅ 官方端点确认 |
| F-021 | API Key在阿里云百炼控制台申请 | ✅ |
| F-022 | 安装命令：cd ~/.claude/skills/claude-vision-skill && npm install dotenv | ✅ |
| F-023 | 验证：node vision.js "图片路径" "请描述这张图片"，能输出详细描述即装好 | — |

## 视觉模型（F-024~F-027）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-024 | qwen-vl-max真实存在：阿里云百炼，输入Text/Image/Video，输出Text，快照qwen-vl-max-2025-08-13，北京/新加坡可用 | ✅ 官方模型页 |
| F-025 | qwen3.5-omni-plus真实存在：Qwen3.5-Omni旗舰全模态，输入Text/Image/Video/Audio，输出Text/Audio，快照qwen3.5-omni-plus-2026-03-15 | ✅ |
| F-026 | ⚠️成本补充：qwen3.5-omni-plus文本/图片输入7元/百万token，qwen-vl-max输入1.6元/百万，omni看图成本约4倍，博文未提示 | 补充核验 |
| F-027 | 百炼新用户免费额度：每个模型100万Token、开通后180天内有效 | 补充核验 |

## 使用方式（F-028~F-034）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-028 | Claude Code自动触发：装好后直接发图片即可——本地路径、粘贴截图、图片URL都支持，description自动匹配，文字描述进入上下文，DeepSeek接着分析 | ✅ |
| F-029 | 博文案例：mall-swarm微服务电商项目架构图，复制粘贴到Claude Code问"这张图片里有什么"，DeepSeek V4 Pro借助Skill认出图 | — |
| F-030 | 手动命令-本地图片：node ~/.claude/skills/claude-vision-skill/vision.js "C:/path/to/image.png" "请描述这张图片" | ✅ |
| F-031 | 手动命令-网络图片：vision.js --url "https://example.com/image.png" "请描述这张图片" | ✅ |
| F-032 | 手动命令-剪贴板：vision.js --clipboard "请描述这张图片"（Windows用仓库附带clipboard.ps1） | ✅ |
| F-033 | 回退逻辑：给了本地路径但文件不存在时自动回退读剪贴板；完全没给路径和URL时也自动尝试剪贴板 | ✅ |
| F-034 | 加--no-fallback参数可关闭回退、直接报错 | ✅ |

## 作者身份（F-035）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-035 | macrozheng为真实知名技术博主：个人站macrozheng.com，mall单体电商60k+ star，mall-swarm微服务商城11k+ star（Spring Cloud Alibaba/Spring Boot 3/JDK17/K8s），教程站cloud.macrozheng.com | ✅ |

## 事实统计

| 类别 | 数量 |
|------|------|
| 元信息 | 1 |
| 问题背景 | 4 |
| 解决方案 | 5 |
| 工作原理 | 7 |
| 安装配置 | 6 |
| 视觉模型 | 4 |
| 使用方式 | 7 |
| 作者身份 | 1 |
| **合计** | **35** |
| ✅ P0通过 | 6/6 |
| ⚠️/补充核验 | 5 |
