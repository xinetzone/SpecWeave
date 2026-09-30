```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-cli-install
02-login-auth
03-deploy-static
04-deploy-framework
05-deploy-output
06-troubleshooting
```

# 概念文档索引

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [EdgeOne Pages 平台概览与适用场景](/concepts/00-overview.md) | 平台能力、China/Global 站点选择、适用与不适用场景 |
| 01 | [CLI 安装与 Windows 排错](/concepts/01-cli-install.md) | 版本要求、标准安装、esbuild postinstall 故障根因与 `--ignore-scripts` 绕过 |
| 02 | [登录与鉴权：站点选择与两种登录方式](/concepts/02-login-auth.md) | 浏览器登录 vs Token 登录、Session 复用陷阱、Token 安全 |
| 03 | [部署静态站点（无构建步骤）](/concepts/03-deploy-static.md) | 纯静态目录部署全流程、StaticAssetsBuilder 实测日志、monorepo 消歧 |
| 04 | [部署需构建的前端项目](/concepts/04-deploy-framework.md) | 框架自动检测构建、与静态部署的差异、不可绕过 esbuild |
| 05 | [解析部署产物：URL、项目 ID 与落区](/concepts/05-deploy-output.md) | 完整保留 URL query 参数、落区与站点不一致、自定义域名绑定 |
| 06 | [故障排查速查表](/concepts/06-troubleshooting.md) | 14 类高频故障的现象-定位-解法，含「表层报错≠根因」排错心法 |
