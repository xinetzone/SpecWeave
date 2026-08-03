# 三个热门AI工具：微软AI终端、Claudian笔记插件、book-to-skill书籍转Skill

## 01 微软下场做了个 AI 终端

最近逛 GitHub Trending，看到一个挂着 Microsoft 官方 logo 的项目：intelligent-terminal。

简单说，这是微软在 Build 2026 上发布的 Windows Terminal 实验分支，把 AI Agent 原生塞进了命令行。

你不用再在聊天窗口和终端之间反复横跳，Agent 直接盯着你的 Shell 输出。

作为出品方，微软把 Copilot、Claude Code、OpenAI Codex、Gemini CLI 全部平等支持，你想接哪个 Agent CLI 都行，本地自建的也能用。这在微软产品里挺少见。

三个亮点：
- **Agent 面板**：停靠式上下文面板，自动读取 Shell 输出，`Ctrl+Shift+.` 一键唤起
- **错误自动检测**：命令跑挂了状态栏指示灯亮，`Ctrl+Alt+.` 把错误上下文直接喂给 Agent，让它解释或者直接修
- **协议无关**：基于 Agent Client Protocol（ACP），未来接新 Agent 几乎零成本

底层设计也干净，它只是本地传输层，不调云 API、不持久化会话，数据走向完全由你选的 Agent 决定。

唯一劝退点：只支持 Win11 22H2+，装法：
```bash
winget install --id Microsoft.IntelligentTerminal -e
```

如果你是 Windows 用户、又天天和 Shell 打交道，这个值得装一个玩玩。

开源地址：https://github.com/microsoft/intelligent-terminal

## 02 Claude Code 直接嵌进笔记库

刷 X 的时候看到中文博主 Jackywine 在推一个插件。

Claudian 能让你在 Obsidian 里面最便捷最强大地使用 Claude Code。

Claudian 是个 Obsidian 插件，把 Claude Code 嵌进你的 vault，让整个笔记库变成 Agent 的工作目录。

7 个月拿下 1.3 万 Star，已经是 Obsidian 社区最火的 AI 插件之一。

之前的方案太憋屈了。Obsidian 用户要用 Claude Code，多半靠 Terminal 类插件，体验拉胯。

Claudian 把 Agent 塞进侧边栏，文件读写、搜索、跑 bash、多步工作流全在笔记库内闭环。

如果你是 Obsidian 重度用户又在搞 AI Coding，这个属于必备插件。

开源地址：https://github.com/YishenTu/claudian

## 03 把技术书变成 AI 可以调用的 Skill

book-to-skill能把任意技术书籍编译成符合 Agent Skills 开放标准的结构化技能。

让你用 Claude Code、CodeX 的时候，AI 能按章节即时调用书里的知识。

2 个月破 6.8k Star。

开源地址：https://github.com/virgiliojr94/book-to-skill

它的路线和 RAG 不一样。RAG 在查询时做向量相似度搜索，返回原文片段。book-to-skill 在编译时一次性深挖作者构建的框架、命名方法、反模式，输出可推理的结构。

作者有句金句：RAG indexes a shelf, book-to-skill masters a spine.

最硬的卖点是作者自己写的基准测试：
- 把一本 256K token 的大书塞进上下文，AI 答一题的发现循环成本约 77,866 token
- 用 skill 只需约 5,000 token，省 15.6 倍。

成本上，单本编译约 1 美元（Sonnet 4.5 一次性费用），之后每次查询固定 5000 token。

用法：
```bash
git clone https://github.com/virgiliojr94/book-to-skill.git ~/.claude/skills/book-to-skill/book-to-skill 你书籍的地址
```

原文链接：https://mp.weixin.qq.com/s/gFlPzfjpY8zs3tOcw3o5Lg
来源：逛逛GitHub微信公众号
