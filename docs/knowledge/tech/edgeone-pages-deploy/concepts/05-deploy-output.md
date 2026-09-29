---
type: Concept
title: 解析部署产物：URL、项目 ID 与落区
description: 部署成功后需完整保留访问 URL 的 query 参数（含 eo_token/eo_time），并记录项目 ID 与控制台链接；预览链接可能过期，长期访问须绑定自定义域名
tags: [edgeone, deploy-url, project-id, console, domain]
generated:
  by: agent-workbuddy
  at: "2026-09-29T14:47:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-29T14:47:00+08:00"
status: draft
stale_after: "2027-09-29"
sources:
  - id: S-002
    resource: /references/00-sources.md
    title: designer-portfolio 部署里程碑复盘报告
  - id: S-004
    resource: /references/00-sources.md
    title: edgeone CLI 实测输出（v1.2.30+）
---

# 解析部署产物：URL、项目 ID 与落区

部署成功后，CLI 输出三个关键字段。正确提取它们很重要——尤其是访问 URL，截断后会直接导致页面打不开。

## 实测输出

```
[cli][✔] Deploy Success
[cli][✔] Deploy URL: https://designer-portfolio-w1ras6ms.edgeone.cool?eo_token=629627c63dd4e9bc9254e0518735a4b4&eo_time=1790663452
[cli][✔] Console URL: https://console.cloud.tencent.com/edgeone/pages/project/makers-kibjgortw1bl/deployment/dpebpaq47jjs
```

在 CI 等自动化场景中，这些字段也可能以环境变量形式给出（`EDGEONE_DEPLOY_URL`、`EDGEONE_DEPLOY_TYPE`、`EDGEONE_PROJECT_ID`），供脚本解析。

## 提取规则

| 字段 | 如何提取 | 注意事项 |
|---|---|---|
| **访问 URL** | `Deploy URL:` 后的完整值 | ⛔ **必须包含完整 query 串**（`?` 及其后全部内容）。这些是鉴权参数，去掉后页面无法加载 |
| **Project ID** | `Using Project ID:` 后的值（形如 `makers-xxxxxxxx`） | 项目唯一标识，用于控制台定位 |
| **Console URL** | `Console URL:` 后的完整链接 | 查看部署记录、绑定域名、获取 Token 的入口 |

### 为什么不能截断 URL

访问 URL 形如：

```
https://<project>-<hash>.edgeone.cool?eo_token=<token>&eo_time=<timestamp>
```

`eo_token` 与 `eo_time` 是预览访问所需的鉴权参数。复制时只取 `?` 前的部分，得到的是一个无鉴权的裸域名，访问会被拒绝。把 URL 写进文档或分享给他人时，务必整串复制。

## 落区与站点可能不一致

登录时指定的站点（`--site china` / `--site global`）与项目实际落区**不是同一个概念**。实测中以 `--site china` 登录，CLI 仍输出：

```
[CreatePagesProject] Creating new project with name: designer-portfolio in global area
[cli][✔] Deploying ... (Production environment, global area)
```

这里的 `global area` 指加速区域，不由 `--site` 唯一决定。判断项目真实归属与区域，以控制台 URL 打开后的显示为准，不要仅凭 CLI 输出下结论。

## 预览链接的时效与限制

预览链接用于快速验证部署结果，但有两个限制：

1. **鉴权参数带时间属性**（`eo_time` 字段），链接可能在一段时间后失效；
2. **分享后受限**：在国内网络环境下，因域名备案状态 / 加速策略等原因，他人访问时可能出现访问限制（如 401）。

### 长期对外访问的正确做法

需要稳定对外访问时，绑定**已备案的自定义域名**：

1. 打开控制台 URL 进入项目管理页
2. 找到自定义域名配置，添加自有域名
3. 按提示配置 CNAME 解析
4. 国内访问需确保域名已完成 ICP 备案

绑定后即可脱离预览链接的鉴权限制，获得稳定的公开访问地址。

## 相关概念

- [部署静态站点](/concepts/03-deploy-static.md)
- [故障排查速查表](/concepts/06-troubleshooting.md)
- [EdgeOne Pages 平台概览](/concepts/00-overview.md)
