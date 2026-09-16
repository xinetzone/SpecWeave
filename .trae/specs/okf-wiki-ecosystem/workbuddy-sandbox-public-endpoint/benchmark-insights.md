---
okf_version: "0.2"
type: insights-addendum
title: "WorkBuddy 与 TraeCode/TraeWork/豆包工作对标洞察"
generated: { by: "seven-concepts-cmd:I", at: "2026-09-16T23:25:00+08:00" }
source:
  - ./facts.md
  - ./benchmark-facts.md
---

# 对标洞察

## 洞察 1：四类产品不是同一种“公网化”机制

- **陈述**：WorkBuddy/CloudStudio 更像沙箱端口/已部署环境的即时公网入口；TraeCode 走外部/平台部署服务；TraeWork 走页面生成后的 Pages Skill；豆包工作首先提供云电脑执行环境，公网部署需另看具体 Skill/云资源。
- **证据**：WorkBuddy 实时域名返回 CloudStudio Gateway（F-034/F-035）；TraeCode 国际版经 Vercel 部署（F-041/F-042）；TRAE CN 明确当前未内置一键部署，需 IGA Pages（F-043/F-044）；TraeWork 经 BytePlus Pages Skill 发布（F-048/F-049）；豆包工作官方只确认云电脑隔离与后台运行（F-051），公网 IP/EdgeOne 为第三方实测（F-052）。
- **反常识**：都能“生成网页/运行任务”不代表都提供同一层级的公网 HTTPS 暴露；有的是端口转发，有的是静态/全栈托管，有的仅是云端执行环境。
- **行动**：比较矩阵按“执行环境、发布动作、托管底座、域名稳定性、适用负载”拆分，不用单一“能否公网访问”二元判断。

## 洞察 2：域名稳定性决定 Demo 与生产的分界

- **陈述**：WorkBuddy/TraeWork 的默认地址都更偏临时分享；长期地址依赖正式 Pages/自定义域名/托管平台。
- **证据**：WorkBuddy 博文提示会话与沙箱生命周期，域名后缀出现漂移（F-014/F-019/F-036）；BytePlus Pages 明确 TraeWork 临时预览地址约 3 小时重置，长期分享需自定义域名（F-050）；IGA Pages 提供自定义域名、GitOps、SSL 与持续部署（F-045）。
- **反常识**：临时链接“打开越快”越适合 Demo，但同等的易变性也使它越不适合作为外部系统回调入口。
- **行动**：矩阵中将“可分享链接”和“稳定线上地址”拆成两列，Webhook/支付/长期 API 只推荐后者。

## 洞察 3：中国版/国际版与办公/编码形态必须分开比较

- **陈述**：TraeCode 中国版与国际版部署底座不同；TraeWork 的 Work/Code/Design 与 TraeCode 的 IDE 开发职责不同；豆包工作偏通用办公任务编排，不等同专业 IDE 部署链路。
- **证据**：TRAE CN 文档明确“当前未提供一键部署能力”并给 IGA Pages 方案（F-043）；TraeCode SOLO 官方国际文档明确 Vercel（F-041）；TraeWork 三端三模式与 Cloud agent 定位（F-046/F-047）；豆包工作官方强调任务模式、云电脑、技能、连接器和工作伙伴（F-051）。
- **反常识**：品牌名都含 Trae/工作/Agent，但产品边界和部署能力不可互相外推。
- **行动**：新增概念文档采用“产品形态→发布底座→推荐场景→不适用场景”的统一模板，并对第三方实测单独打⚠️。
