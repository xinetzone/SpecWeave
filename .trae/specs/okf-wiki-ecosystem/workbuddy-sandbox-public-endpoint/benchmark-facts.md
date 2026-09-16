---
okf_version: "0.2"
type: facts-addendum
title: "WorkBuddy 对标 TraeCode/TraeWork/豆包工作补充事实（F-040~F-052）"
generated: { by: "seven-concepts-cmd:R", at: "2026-09-16T23:20:00+08:00" }
source:
  - https://docs.trae.ai/ide/solo-mode?_lang=en
  - https://docs.trae.ai/ide/vercel-deployment
  - https://docs.trae.ai/solo/what-is-trae-solo?_lang=en
  - https://docs.byteplus.com/th/docs/byteplus-cdn/pages-trae_zh-cn
  - https://www.volcengine.com/docs/6559/2387290?lang=zh
  - https://www.doubao.com/legal/DoubaoAgentModeNotice
  - https://ai.lzw.me/best-blogs/article/5c76486940
---

# 对标补充事实（F-040~F-052）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-040 | O | TraeCode 官方 SOLO 模式文档称，SOLO 让 AI 自主完成需求理解、代码生成、测试、结果预览和部署的完整开发过程 | Trae 官方 | P0 | ✅ |
| F-041 | O | TraeCode 官方文档称 Deployment service 通过第三方服务 Vercel 在线部署 Web 应用；部署后可通过链接分享，应用更新后可重新部署新版本 | Trae 官方 | P0 | ✅ |
| F-042 | O | TraeCode 的部署入口包括 AI 聊天面板中的 Deploy 按钮、Browser 工具右上角 Deploy 按钮，或由自然语言请求触发部署任务 | Trae 官方 | P0 | ✅ |
| F-043 | O | 火山引擎 IGA Pages 文档明确写明“TRAE 中国版当前未提供一键部署能力”，推荐组合为 TRAE CN（AI IDE）× IGA Pages；TRAE 负责生成与迭代，IGA Pages 负责部署、分发与运行时 | 火山引擎官方 | P0 | ✅ 中国版与国际版 TraeCode 部署口径不同 |
| F-044 | O | IGA Pages 是火山引擎一站式 AI 应用部署与全球加速平台，提供零配置部署、全球边缘网络和 Serverless 函数能力，接管节点、证书、缓存等基础设施细节 | 火山引擎官方 | P0 | ✅ |
| F-045 | O | IGA Pages 支持 Skill 或 CLI 部署、GitHub 仓库集成自动部署、自定义域名和平台托管/自有 SSL 证书；文档提示其不适合常驻后台服务、定时任务、数据库常连接和深度定制 Nginx/容器镜像 | 火山引擎官方 | P0 | ✅ |
| F-046 | O | TraeWork 官方定义为 AI-native workspace，提供 Web、桌面、移动三端，包含 Work、Code、Design 三种模式；Web 端适合临时需求和快速验证，桌面端支持本地与云端任务，移动端可派发和监控云任务 | Trae 官方 | P0 | ✅ |
| F-047 | O | TraeWork Cloud agent 在云端环境执行代码分析、运行和调试，提供统一运行时与依赖管理，环境稳定隔离，可避免本地环境兼容或性能问题 | Trae 官方 | P0 | ✅ 这是云端执行环境，不等同自动公网托管 |
| F-048 | O | BytePlus Pages + Trae Work 官方实操指南称，Trae Work 负责生成网页，Pages 负责发布；用户说“部署该页面并获取分享链接”后，Trae Work 调用 `byted-bp-cdn-pagesdeploy` Skill 上传 Pages 并返回分享链接 | BytePlus 官方指南 | P0 | ✅ |
| F-049 | O | BytePlus Pages 是一站式静态站点与 Web 应用托管服务，支持静态 HTML/CSS/JavaScript、SPA、文档站、博客和基于 Git 持续部署的前端项目，通过 BytePlus 全球边缘节点分发 | BytePlus 官方指南 | P0 | ✅ |
| F-050 | O | Trae Work 经 Pages 部署后得到的临时预览地址便于快速验证，但会定期重置（指南称约每 3 小时）；长期对外分享应在 Pages 控制台绑定稳定自定义域名，并可查看部署记录和回滚历史版本 | BytePlus 官方指南 | P0 | ✅ |
| F-051 | O | 豆包工作任务模式官方须知确认存在本地电脑与云电脑两种执行环境；云电脑为云端独立隔离环境，默认不访问本地文件，本地电脑关机后任务仍可在后台运行，任务产物保存在云端；技能、连接器、工作伙伴可扩展执行能力 | 豆包官方 | P0 | ✅ 官方未在该须知中承诺公网 IP 或公网 HTTPS 端点 |
| F-052 | O | 第三方豆包工作实测文称云电脑为 2 核 4G Debian 沙盒、提供公网 IP，并演示使用 EdgeOne 部署网站；该说法未在豆包官方任务功能须知中直接核验 | 第三方实测 | P0 | ⚠️ 可作为用户实测线索，不能写成豆包官方通用承诺 |
