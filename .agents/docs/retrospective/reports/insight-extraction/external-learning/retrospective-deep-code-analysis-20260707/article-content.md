---
id: "deep-code-article-content"
title: "Deep Code被收录进DeepSeek Agent工具"
source: "https://mp.weixin.qq.com/s/2uEb1OA0Y8WkOFXLF12aZA?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../../../../.meta/toml/.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-deep-code-analysis-20260707/article-content.toml"
author: "杨京丽"
editor: "李水青"
publisher: "智东西"
publish_date: "2026-07-06"
extracted_at: "2026-07-07"
extracted_by: "defuddle --md"
---
# Deep Code被收录进DeepSeek Agent工具

Deep Code支持深度思考、推理强度控制、Agent Skills以及MCP集成。

**作者 |** 杨京丽

**编辑 |** 李水青

智东西7月6日报道，据DeepSeek官方API文档及GitHub仓库信息，一款名为 **Deep Code的第三方开源AI编程助手** 近日被收录进DeepSeek Agent工具。该工具面向DeepSeek-V4系列模型做了适配，支持 **深度思考、推理强度控制、Agent Skills以及MCP集成** 。截至发稿，Deep Code GitHub仓库显示，该工具收获 **超** **1500星、127 fork** 。

Github开源地址：

https://github.com/lessweb/deepcode-cli

该开源工具主要由开发者qorzj发布和维护。据其Github主页显示，qorzj来自维加动量公司。该公司2009年在重庆成立，主营业务覆盖AI应用开发、大模型调优、智能体搭建、大数据治理、企业数字化升级等方向。

GitHub页面显示，该工具今年5月发布第一个版本（v0.1.20），目前版本仍在持续迭代。最新版本为v0.1.31，发布于2026年6月16日。

Deep Code可通过npm安装，用户在项目目录下运行deepcode即可启动。其推荐配置模型包括 **deepseek-v4-pro和deepseek-v4-flash** ，同时也支持其他兼容OpenAI接口的模型服务。如果团队已经部署了其他OpenAI兼容API，也可以将Deep Code作为前端编程Agent接入。

功能上，Deep Code覆盖了当前AI编程Agent的常见能力，包括读取和修改项目文件、执行Shell命令、恢复历史对话、调用MCP服务以及配置工具权限等。Deep Code将这些能力围绕DeepSeek-V4系列模型做适配，并提供CLI和VS Code插件两种使用入口。

在扩展能力方面，Deep Code支持 **Agent Skills** 。根据GitHub README，其Skills会从项目目录和用户目录中扫描，包括./.deepcode/skills/、./.agents/skills/、~/.deepcode/skills/和~/.agents/skills/等路径。开发者可以把团队内部常用流程、项目规范或特定任务能力封装成技能，供编程助手调用。

此外，Deep Code还支持 **MCP配置** ，可连接GitHub、浏览器、数据库等外部服务；内置免费的 **Web Search工具** ，也允许用户配置自定义搜索脚本。其配置文档显示，用户可在settings.json中设置模型、API地址、API Key、思考模式、推理强度、MCP服务器、任务完成通知等参数。

安全机制也是这类Agent式工具的关键点。Deep Code文档显示，它内置了细粒度权限控制机制，可针对读取文件、写入文件、删除文件、访问网络、调用MCP、查询或修改Git历史等操作设置放行、拒绝或询问。

Deep Code的出现，给DeepSeek生态又补上了一个编程Agent入口：开发者既可以在终端里调用DeepSeek-V4系列模型，也可以通过VS Code插件把它接入日常开发流程。至于这套围绕DeepSeek适配的工具链，能否在代码理解、任务执行、权限控制和多轮协作中带来足够稳定的体验，还要看后续开发者的实际使用反馈。
