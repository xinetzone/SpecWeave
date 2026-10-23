# evidence/ · 参赛证据截图文件夹

> 用途：存放参赛全过程证据截图（对应 checklist.md 的 I 区「最后一遍」与 doubao-prompts.md 的截图检查点）。
> 规则：截图随做随存，不事后补拍；每张截图文件名可读、含版本/场景信息。

## 命名约定（五类前缀）

| 前缀 | 场景 | 示例 |
|---|---|---|
| `01-req-` | 对话界面 / 需求与提示词截图 | `01-req-prompt1.png` |
| `02-vN-` | 每轮豆包输出结果 / 存档界面 | `02-v2-result.png` |
| `03-extreme-` | 极端参数验证（如 S 2→8 对比） | `03-extreme-s2-to-8.png` |
| `04-error-` | 报错与修复过程 | `04-error-white-screen.png` |
| `05-deploy-` | 部署成功 / 公开链接 | `05-deploy-aiworks-link.png` |

## 截图检查点（随执行包进度推进）

- [x] 10-23：Prompt 2/3 页面结果截图已生成（`02-v3-result.png` S=2、`03-extreme-s2-to-8.png` S=8，均为浏览器实测截图）
- [x] 10-23：Prompt 4 自测结果页截图已生成（`02-v4-result.png` 7/10 档，浏览器实测）
- [x] 10-23：Prompt 5 计划生成器结果截图已生成（`02-v5-result.png`，浏览器实测）
- [x] 10-23：Prompt 6 移动端验证截图已生成（`02-v6-result.png` 首屏+实验台、`02-v6-result-b.png` 计划+科学依据，375px 全页切片）
- [x] 10-23：Prompt 7 最终版验收截图已生成（`02-v7-result.png`，对比表+结论，浏览器实测）
- [x] 10-23：豆包对话界面截图（`01-req-prompt1.png`）——已由用户附件补齐三张（见下方「三张已补齐」条目），并已补插到已发布文章
- [x] 10-23：部署打包提前完成（`deploy/index.html` + 合规包 `deploy/deploy.zip` 16.5KB；`memory-lab.zip` 12.9KB 早前版本；均含知乎 AI Works 所需 `frontend.deploy.json` 与事件桥）
- [x] 10-23：**部署+发布成功**（知乎 AI Works 项目详情页 `https://www.zhihu.com/project/detail/60591`，状态「科学季·可运行·项目审核中」；截图 `05-deploy-published.png` 已存档）
- [x] 10-23：**审核通过**（详情页「可在当前页面直接运行项目应用」；截图 `05-deploy-running.png` 已存档）
- [x] 10-23：文章成稿 v2 完成（`article-draft.md`：标题已确认「背了就忘不是你的错：我用豆包把遗忘曲线做成了能拖动的实验台」、正文 ~1000 字、赛道标注/链接就绪、5 图已映射到本目录截图）
- [x] 10-23：豆包对话界面截图（`01-req-prompt1.png`）——**已由用户上传附件补齐**（10-23 工具 GUI 通道故障：可见豆包窗口为未登录实例且虚拟桌面会话断开，无法自动截取；改由用户附件供给，见下方三张补齐条目）
- [x] 10-23：**文章发布完成**（知乎专栏文章 `https://zhuanlan.zhihu.com/p/2096941285965931971`，标题「背了就忘不是你的错：我用豆包把遗忘曲线做成了能拖动的实验台」，正文 1355 字 + 5 图，话题 #AI科学创新工坊/遗忘曲线/有趣的人工智能，创作声明「包含 AI 辅助创作」；发布四截图已存档于 `publish/`：01-article-top.png、02-topics-declaration.png、03-track-label.png、04-article-link.png）
- [x] 10-23：豆包对话界面截图三张已补齐（`01-req-prompt1.png` 学习洞察界面、`01-req-prompt2.png` 任务规划界面、`01-req-prompt3.png` 行动项推进界面，均来自用户上传附件）并已补插到已发布文章（图2a/2b/2c，文章现 8 图；更新后文章页验证通过；存档 `publish/05-article-doubao-shots.png`）

## 计数目标

- 配图最低 3 张，建议 8-10 张（文章插图复用本目录截图）。
