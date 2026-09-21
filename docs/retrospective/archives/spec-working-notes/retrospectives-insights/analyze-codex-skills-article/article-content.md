---
source: "https://mp.weixin.qq.com/s/ib6J-9Pph3ybVD0rVGvnYQ?from=industrynews&color_scheme=light#rd"
title: "skill 拼起来，Codex 玩家必装的 6 个 GitHub 高星技能"
author: "自学资源库"
extracted_at: "2026-07-09"
---

# skill 拼起来，Codex 玩家必装的 6 个 GitHub 高星技能

> 原创：自学资源库 | AI行动手册

上图是 2026 年 7 月初我从 GitHub 抓的 6 个高星 repo。Star 数会变，仓库一直在更新，建议你看到时再核对。我每月翻一次 GitHub 搜 Codex 相关高星 repo，留下真改变工作流的，卸掉"看起来酷"的。这次筛出来的 6 个，有 5 个我装了，1 个是清单。下面每个都附推荐理由、我的用法、怎么装。

## 我的筛选标准

- **Star ≥ 1K** ——社区检验过
- **最近 3 个月有 commit** ——没烂尾
- **README 短（≤ 200 行）** ——README 比代码长的多半是营销
- **能 5 分钟内跑通 demo** ——装都装不上的直接 pass
- **不绑死单一模型** ——纯 OpenAI 锁定的扣分

筛完一轮大概 30 分钟，留下 5-8 个真用得上的。下面这 6 个是这轮留下来的。

## 推荐 1：wshobson/agents · 37K ★

**这是什么**：一个 markdown 源，自动生成 6 套原生包——Codex CLI / Claude Code / Cursor / OpenCode / Gemini CLI / Copilot 都吃同一份。88 插件 + 194 agent + 158 skill + 106 命令。

**为什么推荐**：写一次代码，6 个 IDE 都能用。我之前在 Codex CLI 里写的 skill，Cursor 用户想用得自己重写。现在不用了。

**我的用法**：`python-development` 和 `code-review` 两个插件每天开。

**怎么装**：
```bash
npx codex-marketplace add wshobson/agents
# 然后按提示装具体插件
```

## 推荐 2：sickn33/antigravity-awesome-skills · 42K ★

**这是什么**：1,800+ 通用 agent 技能，按场景分类（编程、写作、运营、设计、研究）。

**为什么推荐**：自己写 skill 是重复造轮子。我自己写了 4 个，发现这库全有现成的——而且比我写的精细。

**我的用法**：本地 skill 文件夹挂个 symlink，重启 Codex 直接生效。不装，只引用。

**怎么装**：
```bash
git clone https://github.com/sickn33/antigravity-awesome-skills ~/codex-skills
# Codex 配置加：skills_dir = ~/codex-skills
```

## 推荐 3：openai/codex-plugin-cc · 25K ★

**这是什么**：OpenAI 官方给 Claude Code 写的 Codex 插件。在 Claude Code 里调 Codex 做代码审查。

**为什么推荐**：跨工具 review 这个事自己实现要 200 行代码。这插件打包好直接用。

**我的用法**：
```
/codex:review --background    # 后台跑 Codex 审查
/codex:status                 # 看进度
/codex:result                 # 拿结果
```
Claude Code 干别的活，Codex 异步审代码。

**怎么装**：
```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

## 推荐 4：EveryInc/compound-engineering-plugin · 22K ★

**这是什么**：方法论类 skill 集。不讲具体写代码，讲怎么让每次改动让下次更容易。

**为什么推荐**：这是少有的"元方法"skill——其他 skill 教你做具体的事，它教你怎么学。

**我的用法**：
- `/ce-brainstorm` 动手前想清楚
- `/ce-plan` 出 readiness 评估
- `/ce-compound` 把经验沉淀成 markdown
- `/ce-code-review` / `/ce-doc-review` 复盘

**怎么装**：Claude Code 用户直接走 `/plugin marketplace add` 路径。Codex CLI 把 skill 文件夹里的 markdown 复制到本地即可。

## 推荐 5：YishenTu/claudian · 13K ★

**这是什么**：Obsidian 插件。把 Claude Code / Codex / Opencode 塞进 Obsidian 侧边栏，vault 当 working dir。

**为什么推荐**：我写公众号全在 Obsidian，这个插件让 Codex 直接读 vault、生成新文章直接写进 vault，不切窗口。

**我的用法**：
- 侧边栏开 chat
- `@` 引用 vault 文件当上下文
- `Shift+Tab` 切 plan mode
- 选中文字 + 快捷键直接 inline edit

**怎么装**：Obsidian 社区插件里搜 "Claudian"。

## 推荐 6：ComposioHQ/awesome-codex-skills · 14K ★

**这是什么**：Codex 实用技能清单 repo（不是装包）。按场景分类列了真用得上的 skill，每个给 prompt 模板。

**为什么推荐**：找新 skill 灵感的最佳入口。我每月翻一次，看到合适的挑 1 个试。

**我的用法**：加进 RSS 订阅，只看不装。看到的 prompt 模板手抄到自己的 skill 库。

**怎么装**：不用装。GitHub 收藏 + 每月翻一次即可。

## 我的组合（别学我全装）

| 用途 | 装啥 |
|---|---|
| 写代码 | wshobson/agents 的 python-development |
| 代码审查 | openai/codex-plugin-cc（异步 review） |
| 写公众号 | claudian + 我自己写的"公众号风格" skill |
| 做项目复盘 | EveryInc/compound-engineering-plugin |
| Obsidian 里调 agent | YishenTu/claudian |
| 找新 skill 灵感 | ComposioHQ/awesome-codex-skills（只看不装） |

## 装 6 个的代价

- Codex 启动 +2-3 秒（prompt 长）
- 安装包 +300MB
- 月维护：每月翻一次 sickn33 / ComposioHQ，挑 1 个新 skill 试

**值得吗**：值得。装 5 个省的时间 1 周就回本了。

## 怎么装

- **Codex CLI 装 skill**：放 `~/.codex/skills/` 文件夹下
- **Codex CLI 装插件**：`npx codex-marketplace add <repo>`
- **Claude Code 装插件**：`/plugin marketplace add <repo>`

## 留给自己的 3 条规矩

1. **装一个用 1 个月** ——不到 1 个月不算"用过"
2. **删"看起来酷"的** ——不改变工作流的都删
3. **每月底翻一次 sickn33** ——挑 1 个新 skill 试

## 最后

自己写 skill 不是错。错的是自己写完就不看外面的。GitHub 上 1800+ skill，总有 10 个比你自己写的更适合你。先翻一遍，再决定要不要自己写。

数据都是 2026.07 从 GitHub API 实时抓的，链接都给了，可能你看到时已经变了。
