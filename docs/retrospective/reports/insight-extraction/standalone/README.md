---
id: "standalone-insights-index"
title: "独立洞察卡片索引"
---
# 独立洞察卡片

本目录存放不属于特定原子化复盘报告的独立洞察卡片。每份洞察为单个 Markdown 文件，遵循"事实采集 → 根因分析 → 纠正预防"结构，可直接查阅和引用。

与 `insight-extraction/` 下原子化报告的区别：
- **原子化报告**（子目录形式）：围绕特定项目/任务的完整复盘，包含 README、execution-retrospective、insight-extraction、export-suggestions 等多文件
- **独立洞察卡片**（单文件形式）：跨项目、单主题的精炼洞察，直接由"洞察"指令或复盘过程产出，无需完整的四文件结构

## 洞察卡片清单

| 文件 | 日期 | 主题 | 来源 |
|------|------|------|------|
| [insight-temp-file-discipline-20260701.md](insight-temp-file-discipline-20260701.md) | 2026-07-01 | 临时文件路径规范执行卡点 | defuddle-web-content-extraction |
| [insight-tuyaopen-folder-20260630.md](insight-tuyaopen-folder-20260630.md) | 2026-06-30 | TuyaOpen 目录洞察 | .temp/libs/TuyaOpen |
| [insight-windows-git-encoding-20260701.md](insight-windows-git-encoding-20260701.md) | 2026-07-01 | Windows Git 非 ASCII 提交信息编码陷阱 | atomic-commit-cmd-execution |
| [insight-dockerfile-caching-20260703.md](insight-dockerfile-caching-20260703.md) | 2026-07-03 | Dockerfile 层缓存与开发环境镜像构建的七条深层洞察 | llvm-dev Dockerfile全面优化任务 |
| [insight-subagent-batch-checkpoint-20260706.md](insight-subagent-batch-checkpoint-20260706.md) | 2026-07-06 | 批量子代理委派的中间检查点缺失风险 | volcengine-sandbox-learning复盘 |
| [insight-domestic-llm-comparison-20260706.md](insight-domestic-llm-comparison-20260706.md) | 2026-07-06 | 国产AI模型对比与使用场景推荐 | 微信公众号文章萃取 |
| [insight-analyze-wechat-article-3dnk-20260706.md](insight-analyze-wechat-article-3dnk-20260706.md) | 2026-07-06 | 3D神经核团微信公众号文章洞察萃取 | 微信公众号文章萃取 |

## 新增洞察卡片规范

1. 文件名遵循 `insight-{主题关键词}-{日期}.md` 格式（kebab-case）
2. 文件开头使用 YAML frontmatter，包含 `id` 和 `source` 字段
3. 内容结构遵循"1. 事实数据采集 → 2. 根因分析与洞察 → 3. 纠正与预防措施"三段式
4. 完成后同步更新本索引文件
