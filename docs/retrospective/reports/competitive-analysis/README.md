---
type: Report
id: "docs-retrospective-reports-competitive-analysis-index"
title: "竞品分析"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/README.toml"
category: "retrospective"
date: "2026-07-15"
---
# 竞品分析

本目录汇总外部产品、工具与平台的学习分析复盘，按单任务目录归档。

## 使用说明

- 优先从各任务目录的 `README.md` 进入
- 如任务包含 `insight-action-backlog.md` 或 `insights/` 子目录，请继续沿索引阅读

## 最近归档

| 报告目录 | 简要说明 | 日期 |
|---|---|---|
| [retrospective-vibeknow-video-expert-20261021/README.md](retrospective-vibeknow-video-expert-20261021/) | VibeKnow 视频专家全面调研报告（七概念 R→I→E→V，场景4 知识沉淀）：106 条可追溯事实（PRO-01~25 产品功能 / TEC-01~31 技术与 CLI / COM-01~25 商业化与竞品 / RP-01~25 主体口碑与风险，4 份事实附录），8 项跨站与跨来源口径冲突多值并陈 + 24 项未获取项显式登记；4 条四元组洞察（可编辑性与批量是差异化而生成质量是共性红海/收费点落在不可逆动作且 preset 禁带授权开关/可续跑中间态被提升为一等退出码语义/对外体量叙事全部落在厂商单源），六维加权 65 分（证据强度维度仅 2/5）；含最小试用路径、CLI 最小可用序列与采购前必问八问；萃取 `agent-cli-charge-authority-resume`「Agent 原生 CLI 扣费-授权-续跑三元契约」L1-draft（与既有 `cli-as-api-design` 显式划界） | 2026-10-21 |
| [retrospective-openkylin-evaluation-20261014/README.md](retrospective-openkylin-evaluation-20261014/) | openKylin 全面评估报告（七概念 R→I→E→V，场景4 知识沉淀）：145 条可追溯事实（CMP-01~75/ECO-01~70，12 项数据冲突＋12 项未获取项显式登记）＋复用既有知识包约 148 条，4 条四元组洞察（指标无独立审计/治理与商业主体重合/跟版激进但 EOL 缺位/官方叙事与第三方信号背离），六维加权 70 分，含 okw（openKylin 3.0 WSL）最小可验证切片 LOC-01~08；萃取 `community-metric-triple-check`「社区指标三查法」L1-draft；**同日 Q 门首轮复核**：Q-1 证实成文 LTS 2+3 政策存在（新旧口径冲突、无日期表，部分推翻「无 EOL」原判断）、Q-3 取得 DistroWatch 6 个月 #107/HPD 132、Q-4 坐实 2400 万套仅厂商单源外部全转引、Q-5 量化麒麟占单位归属 PR 85.2%、Q-6 证伪社区版等保/安可记录、Q-7 日期事件全部定性；附录 C 新增 VF-01~49，评分 70→73；同日傍晚功能级二轮实测：Q-2 升级断裂三重坐实并闭环（服务端通道冻结于 2024-08），Q-8 MCP 架构级验证（kylin-bot Rust MCP host/66 供应商/12 桌面技能/ModelScope 分发，VF-50~61），评分维持 73 | 2026-10-14 |
| [retrospective-atomgit-selection-evaluation-20260928/README.md](retrospective-atomgit-selection-evaluation-20260928/) | AtomGit 选型评估报告（七概念 R→I→E→V，场景4 知识沉淀）：对标 GitHub / 极狐 GitLab / Gitee，40 条可追溯事实（F-001~F-040）+ 4 条四元组洞察 + 六维加权评分（AtomGit 71 / GitHub 80 / 极狐 86 / Gitee 80），萃取 `pat-code-hosting-four-filter-001`「代码托管四筛法」；指出 AtomGit 在 CI/CD 生态兼容（`.gitcode/workflows/` 而非 `.github/workflows/`）与私有化部署上的关键缺口 | 2026-09-28 |
| [research-china-side-income-platforms-20260919/README.md](research-china-side-income-platforms-20260919/) | 中国「赚外快」平台全景调研（2026）：七大类渠道（众包微任务/数据标注、技能自由职业与威客、内容自媒体、电商无货源、出行配送、游戏陪玩、海外远程接单）的门槛、抽成、收益区间、结算与合规风险；含 11 家平台抽成对照表、劳务报酬累计预扣法与增值税口径、招转培与刷单返利骗局识别，44 条可追溯来源 | 2026-09-19 |
| [zhihu-monetization-path-20260923/README.md](zhihu-monetization-path-20260923/) | 知乎个人变现路径（2026）：三个公开活动页（AI Works 项目广场/创作打卡挑战赛第五十三期/科学季 2026）深度学习 + 67 条 F 编号事实核验（P0 十六条中十条平台页单源，flagged）→ 三角色路径矩阵 + AI/技术创作者主路径 18 条原子化行动项；收益全部挂 F 或标待验证，含防画饼阅读纪律、AI 协作排除条款可操作自检与退出/切换条件 | 2026-09-23 |
| [retrospective-tts-engine-selection-20260904/README.md](retrospective-tts-engine-selection-20260904/) | 本地/在线 TTS 引擎选型深度报告（七概念F→V→I）：sherpa-onnx+Matcha（中文本地首选，RTF 0.04）/ Edge TTS（逆向端点 2026-08 已大面积 403）/ Gemini TTS / KittenTTS / Piper，含 30 条可追溯事实、9 维决策矩阵与 5 分钟上手命令 | 2026-09-04 |
| [retrospective-copywriting-ai-tools-gemini-analysis-20260901/README.md](retrospective-copywriting-ai-tools-gemini-analysis-20260901/) | Cherry Studio vs TraeCode vs TraeWork × Gemini三模型（2.5 Pro/3.1 Pro/3.7 Flash）写文案选型分析（七概念R→F→V→I→C），产出工具×模型可用性矩阵、成本测算与4条四元组洞察 | 2026-09-01 |
| [retrospective-knowledge-catalog-wiki-20260815/README.md](retrospective-knowledge-catalog-wiki-20260815/) | Google Cloud Knowledge Catalog学习Wiki（OKF开放知识格式v0.2），产出7篇结构化教程，萃取5条核心洞察、3个可复用模式，包含完整环境配置指南与反模式检查清单 | 2026-08-15 |
| [retrospective-action-first-command-bootstrap-20260728/README.md](retrospective-action-first-command-bootstrap-20260728/) | action-first范式commands注册与自举验证元复盘（二次沉淀），提炼"格式类范式自举验证"L1模式，发现范式入库螺旋深化链 | 2026-07-28 |
| [retrospective-i-have-adhd-knowledge-crystallization-20260728/README.md](retrospective-i-have-adhd-knowledge-crystallization-20260728/) | i-have-adhd文章知识沉淀任务元复盘（R→I→E→V全链路），产出行动优先输出范式/逆向适配创新2个L2模式，提炼3条执行经验 | 2026-07-28 |

## 相关资源

- [返回上级：复盘报告分类索引](../index.md)
- [文档首页](../../../index.md)
