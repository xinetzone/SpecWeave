---
id: "wechat-mp-archiver-docs-quickstart"
title: "wechat-mp-archiver 快速开始"
source: "../README.md#快速开始（从零到单篇演练）"
---
# wechat-mp-archiver 快速开始

## 安装

要求 **Python ≥ 3.14** 与 Docker（用于采集服务，NAS 可用多架构镜像）。

```bash
cd apps/dev-tools/wechat-mp-archiver
python -m venv .venv && . .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1；Linux/macOS: . .venv/bin/activate
pip install -e ".[dev]"
```

## 从零到单篇演练

1. **准备专用账号**：注册一个**采集专用微信订阅号**（个人主体即可），不要使用主力号；采集只能由该号管理员本人扫码授权（账号注册与扫码前提见 [deploy/README.md](../deploy/README.md) 第 1–3 节）。

2. **部署采集服务并扫码**：在 `deploy/` 目录 `docker compose up -d`（服务仅绑 `127.0.0.1:5000`，切勿暴露公网），浏览器打开 <http://127.0.0.1:5000/login.html> 扫码确认。完整步骤、Token 设置与升级备份见 [deploy/README.md](../deploy/README.md) 第 1–3、6 节。

3. **配置管线**：

   ```bash
   copy .env.example .env   # PowerShell；bash: cp .env.example .env
   ```

   默认采集服务地址 `http://127.0.0.1:5000` 即可；若服务端设置了静态 Token，在 `.env` 填同一值。归档根目录、数据库路径、限速参数均可在 `.env` 调整（默认值已是保守档，见 [03-operations.md](03-operations.md) 的「默认限速」）。**凭证只走环境变量/.env，`.env` 已被 gitignore。**

4. **建库与自检**：

   ```bash
   mp-archiver init-db
   mp-archiver doctor     # 预期「采集服务在线：OpenAPI 文档可访问」
   ```

5. **列表小批量试跑**（只翻 2 页，不触发下架对账）：

   ```bash
   mp-archiver list -a 意识食谱 --max-pages 2
   ```

6. **单篇下载演练**：

   ```bash
   mp-archiver fetch -a 意识食谱 --limit 1
   ```

   成功后检查 `archive/意识食谱/<年>/<日期_标题>/` 下四件套（`article.html` 可离线打开、图片已本地化）。

7. **转入日常**：每日执行 `mp-archiver sync -a 意识食谱`（增量、幂等）；每周至多一次 `mp-archiver run -a 意识食谱 --full`（全量回溯+下架对账）。计划任务配置见 [deploy/README.md](../deploy/README.md) 第 12 节。

## 账号准备与凭证管理

| 凭证 | 用途 | 获取方式 | 有效期与失效处置 |
|---|---|---|---|
| 采集服务扫码登录态 | 文章列表与下载（主路线） | 专用订阅号管理员扫码，deploy 第 2–3 节 | 经验约 4 天；`doctor` 提示需要授权或命令退出码 2 时，按第 4–5 节重新扫码，无需全量重采 |
| `MP_ARCHIVER_EXPORTER_TOKEN` | 管线访问采集服务（非独占环境建议设置） | 与 `deploy/collector.env` 的静态 Token 取同一值 | 随部署变更 |
| `appmsg_token` / `pass_ticket`（另需 `key`/`wxuin` 视接口形态） | 评论、阅读/点赞等互动数据，**默认关闭** | 本机抓包，自担风险，deploy 第 8 节 | 仅数小时至数天；失效后该篇互动行记 `skipped_no_credential`（非 failed），正文归档不受影响 |
| AppID / AppSecret（+IP 白名单） | 自有认证号官方清单交叉补全（可选） | 公众号后台「设置与开发」，deploy 第 11 节 | 个人/未认证主体返回 48001 时自动降级退出码 0；日配额默认 90 次 |

凭证安全：所有凭证只存于本地 `.env`（已在 `.gitignore`），日志对凭证脱敏；不共享账号、不转售凭证。官方接口仅用于自己管理的认证服务号，2025-07 权限收紧事实与适用边界见 deploy 第 11 节。

## 相关文档

- [文档索引](README.md)
- [命令参考](02-commands.md)
- [限速与故障处置](03-operations.md)