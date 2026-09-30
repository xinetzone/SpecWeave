# 采集服务私有部署与扫码登录指南

本目录承载归档工具的**采集服务侧**部署。架构上分两部分：

1. **采集服务**（容器）：承载微信公众号平台登录态，向管线提供文章列表与下载接口；
2. **归档管线**（本机 Python 包）：`mp-archiver`，通过回环端口访问采集服务，落盘归档与建库。

> **合规前置**：仅供个人账号下的个人学习、研究与备份使用；必须使用**采集专用订阅号**（非主力号）扫码，由账号管理员本人操作；不要将服务暴露到公网，不要公开再分发归档内容。

## 1. 前置条件

- 容器运行时（任一，均需带 Compose 能力；下文 `docker compose` 命令对 Podman 等价替换为 `podman compose`）：
  - Windows：Docker Desktop（启用 WSL2 后端）或 Podman 5.x（WSL2 后端）；
  - Linux：Docker Engine 24+ 与 Compose 插件，或 Podman 5.x + podman-compose；
  - ARM 设备/NAS：镜像为多架构（linux/amd64、linux/arm64），Docker/Podman 运行时均可。
- 若本机网络访问 Docker Hub 不稳定（拉取超时），先按第 13 节配置镜像源再启动。
- 一个用于采集的**专用微信订阅号**（注册主体个人即可），以及可扫码的微信客户端。
- 本机端口 5000 未被占用。

## 2. 启动采集服务

在本目录（`deploy/`）执行：

```bash
cp collector.env.example collector.env
# 如需 API Token（非本机独占环境建议设置），编辑 collector.env 填入长随机串
docker compose up -d
docker compose ps            # STATUS 应为 healthy
docker compose logs -f collector
```

服务仅绑定 `127.0.0.1:5000`，登录凭证持久化在命名卷 `mp_archiver_collector_data`（容器重建不丢失）。

## 3. 首次扫码登录

1. 浏览器打开 <http://127.0.0.1:5000/login.html>；
2. 使用**采集专用订阅号管理员**的微信扫描页面二维码并确认；
3. 页面提示登录成功后，凭证即写入服务端数据卷；
4. 在管线侧配置（项目根目录）：

   ```bash
   cp .env.example .env
   # MP_ARCHIVER_EXPORTER_URL=http://127.0.0.1:5000
   # 若 collector.env 设置了 MCP_TOKEN，MP_ARCHIVER_EXPORTER_TOKEN 填同一值
   ```

5. 运行自检：

   ```bash
   mp-archiver doctor
   ```

   预期看到 `[ok] 采集服务在线：OpenAPI 文档可访问`。

> 截图位（待用户实操补充）：①登录页二维码；②扫码确认页；③doctor 通过输出。补充时请自行遮挡二维码与账号信息。

## 4. 登录态失效的观测信号

微信侧登录凭证为短期有效（经验约 4 天，以微信实际策略为准，不保证续期）。出现以下任一信号即需重新扫码：

- `mp-archiver doctor` 输出 `采集服务需要授权`（探测端点返回 401/403）；
- 采集过程中接口返回 401/403，或响应被重定向到登录页；
- 目标号确有历史文章，但列表接口持续返回空；
- 采集服务自身日志出现登录态过期/凭证失效记录；
- 若配置了企业微信机器人 Webhook（见采集服务自身配置），收到失效告警。

## 5. 重新扫码 SOP

1. 打开 <http://127.0.0.1:5000/login.html>（如页面异常先执行 `docker compose restart collector`）；
2. 用同一专用订阅号管理员微信扫码确认；
3. 重跑 `mp-archiver doctor` 确认恢复；
4. 管线侧采集任务具备状态机，失效期间标记失败的文章可用 `mp-archiver run -a <账号> --full --include-failed` 或日常增量任务自动重试（见第 12 节），无需全量重采。

## 6. 停止、升级与备份

```bash
docker compose down              # 停止；凭证卷保留
docker compose pull && docker compose up -d   # 升级镜像
docker volume inspect mp_archiver_collector_data   # 查看凭证卷位置（备份/迁移用）
```

迁移主机时先在旧主机备份该卷，再在新主机恢复；`.env`/`collector.env` 内含凭证，勿提交版本库（已在 `.gitignore`）。

## 7. 备选承载：wechat-article-exporter

主承载不满足需求（如需其成熟 UI）时，可改用 wechat-article-exporter（Nuxt 全栈应用）。该项目无可在线核实的官方预构建镜像，需从其官方仓库源码自行构建，构建与运行参数**以仓库当前 README 为准**：

- 仓库：<https://github.com/wechat-article/wechat-article-exporter>

构建完成后将管线 `.env` 的 `MP_ARCHIVER_EXPORTER_URL` 指向其地址；`doctor` 对 FastAPI 与普通 Web 两种形态均能识别存活状态。

## 8. 互动数据采集凭证（可选，默认关闭）

评论、阅读数、点赞、在看、转发等互动数据**没有公开接口**，需借助微信网页文章的短期访问凭证，且更容易触发风控，因此默认不采集。

### 8.1 启用方式

```bash
mp-archiver fetch -a <公众号> --fetch-metrics
```

或在 `.env` 中置 `MP_ARCHIVER_FETCH_METRICS=true`。凭证通过以下环境变量提供（写入项目根目录 `.env`，已被 `.gitignore` 忽略）：

| 变量 | 必需 | 含义 |
|---|---|---|
| `MP_ARCHIVER_WECHAT_APPSMSG_TOKEN` | 是 | 网页端互动接口令牌（请求参数 `appmsg_token`） |
| `MP_ARCHIVER_WECHAT_PASS_TICKET` | 是 | 访问票据（请求参数 `pass_ticket`） |
| `MP_ARCHIVER_WECHAT_KEY` | 否 | 文章链接短期密钥（参数 `key`，部分接口形态需要） |
| `MP_ARCHIVER_WECHAT_WXUIN` | 否 | 微信用户标识（参数 `wxuin`，部分接口形态需要） |

### 8.2 凭证获取步骤（抓包，需自担风险）

1. 在与网络环境一致的机器上启动本地 HTTPS 抓包代理（mitmproxy/Charles/Fiddler），并让微信客户端信任其根证书；企业管控设备请勿操作。
2. 用微信打开任意一篇**目标公众号**文章，等待页面加载完成（此时客户端会请求 `/mp/appmsg_comment` 与 `/mp/getappmsgext`）。
3. 在抓包记录中定位上述两个请求，从 URL 查询串复制 `appmsg_token`、`pass_ticket`，从文章页 URL 复制 `key`（如有）与 `wxuin`（如有）。
4. 粘贴到 `.env` 后重新执行 fetch。

### 8.3 失效与降级

- 凭证为短期有效（通常仅数小时至数天，随会话变化），失效后无需干预：该文章 metrics 行记为 `skipped_no_credential`（不记 failed），正文与图片归档正常，任务退出码仍为 0；
- 网络或接口结构异常记为 `failed` 并保留原因，可在更新凭证后重跑；
- 接口字段为经验形态，真实联调若字段名变化，以抓包实测为准在 `src/mp_archiver/core/comment_sync.py` 校准。

> 仅限管理员个人对已关注内容做学习备份；请勿高频请求，勿在不可信网络或他人设备上操作。

## 9. 许可证与署名义务（部署时复核）

| 组件 | 许可证（核实状态） | 义务要点 |
|---|---|---|
| wechat-download-api（`tmwgsicp/wechat-download-api`） | AGPL-3.0（据其项目文档 2026-09 记载；部署时以镜像内 `/app/LICENSE` 复核） | 个人本地自用不构成网络分发；**切勿将服务对公网开放**（既触发 AGPL 网络交付条款，也会泄露微信登录态） |
| wechat-article-exporter | 当前网络环境未能在线核实（Gitee 镜像有人机验证拦截） | 部署时从所用版本仓库的 LICENSE 文件核实后回填本表；保留原作者版权声明 |

## 10. 故障速查

| 现象 | 排查 |
|---|---|
| `doctor` 输出「采集服务未响应：无法连接…」告警 | `docker compose ps` 容器是否 healthy；端口是否被占；是否有本地代理拦截 127.0.0.1 |
| 容器反复重启 | `docker compose logs collector`；确认 `collector.env` 存在且 `SITE_URL` 与端口绑定一致 |
| 扫码后仍 401 | 确认扫码的是订阅号管理员微信；尝试重启容器后重新扫码 |
| ARM 设备拉取失败 | 确认容器运行时支持多架构清单（manifest list）；镜像已提供 arm64 变体 |
| 拉取镜像报 `TLS handshake timeout`、`pinging container registry registry-1.docker.io` 失败或 DNS 解析超时 | 本机到 Docker Hub 不可达，与项目无关；按第 13 节配置 registry mirror 或手动转存镜像 |
| 容器一直 `unhealthy`（旧版本清单） | 2026-09 已将健康检查端点修正为 `/api/health`；本镜像 API 挂在 `/api` 前缀下，根路径 `/openapi.json` 返回 404 |
| `sync-official` 报 48001 | 主体无接口权限（2025-07 后个人/未认证号常态）；官方源不可用，历史全量以 R2 采集服务为准 |
| `sync-official` 报配额触顶 | 当日 batchget 调用达安全阈值（默认 90 次/日），UTC 0 点后重跑；状态见 `data/official_api_quota.json` |
| `sync-official` 提示无法解析 biz | 先对该账号执行一次 `list`（R2），或在 `.env` 显式配置 `MP_ARCHIVER_WECHAT_OFFICIAL_BIZ` |

## 11. 自有号官方接口（可选，R1 条件补充）

> 该能力**仅服务于自己管理的认证服务号**，用于官方清单与 R2 采集结果交叉补全；不采集他人账号，不绕过任何权限。

### 11.1 适用边界（2026-09 时点，以官方文档为准）

- 接口：`cgi-bin/freepublish/batchget`（已发布图文列表），返回群发记录，每组含 1–8 篇图文；
- 覆盖范围：**仅"发布成功"的图文素材**（含 2025-07 后"发表不通知"内容），不含传统群发历史——历史全量仍以 R2 采集服务为主路径；
- 权限要求：当前官方文档的适用范围表仅列**认证服务号**；认证订阅号能否调用以公众号后台「接口权限」页与实测为准。2025-07 平台收紧后，个人主体、未认证主体调用返回 `errcode=48001`，工具打印降级提示并以退出码 0 结束，不影响其他流程；
- 配额：接口存在日调用上限（经验约 100 次/日）。工具以本地持久化计数器（`data/official_api_quota.json`，按 UTC 日滚动）守护，默认阈值 90 次，触顶后当次翻页优雅停止、次日继续。

### 11.2 配置与使用

1. 在公众号后台「设置与开发 → 基本配置」获取 AppID 与 AppSecret，将服务器出口 IP 加入 IP 白名单；
2. 在 `.env` 配置：
   ```dotenv
   MP_ARCHIVER_WECHAT_APP_ID=wx...
   MP_ARCHIVER_WECHAT_APP_SECRET=...
   # 二选一：先做过 R2 同步则可按别名自动解析 biz；否则显式填写
   MP_ARCHIVER_WECHAT_OFFICIAL_BIZ=
   MP_ARCHIVER_OFFICIAL_DAILY_CALL_CAP=90
   ```
3. 执行（别名与 `list`/`fetch` 一致）：
   ```bash
   mp-archiver sync-official -a <账号别名>
   ```
   未配置凭证时命令直接跳过且不发起任何网络请求；48001 时打印降级提示并以退出码 0 结束。

### 11.3 入库语义

- 一条群发按 `idx` 展开为多篇文章，以 `biz+mid+idx` 及 `sn`（从图文 URL 解析）与 R2 数据去重，不产生重复行；
- 已删除条目（`is_deleted=1`）跳过并计数，不进入待采集队列；
- `articles.source` 标记来源：`exporter` / `official_api`，同一篇文章被两个源命中时合并为 `exporter+official_api`，可用于事后对账；
- 官方同步不回退已有采集状态（已归档文章保持 `downloaded`），正文、图片、Markdown 的实际下载仍由 `fetch` 统一完成。

## 12. 定时调度（增量同步与周期全量）

日常无需手动执行：增量任务列表只翻到「整页全已知」即停、正文只下载新文章，天然幂等，重复执行零新增、零重复文件；进程被中途终止后重跑即可从断点补齐（已归档文章按状态跳过，文章目录整体重建保证无残留碎片）。

### 12.1 频率建议

| 任务 | 建议频率 | 说明 |
|---|---|---|
| 增量同步 `sync` | 每日 1 次（建议 03:00–05:00 低峰时段，分钟数取非整点，如 03:17） | 登录态经验约 4 天有效，每日一次足以追平；过高频率没有时效收益，徒增风控暴露 |
| 全量回溯 `run --full` | 每周至多 1 次（或每月 1 次） | 完整翻到历史尾页并做下架对账，请求量大；用于发现历史文章删除/违规并校验元数据完整性 |
| 登录态失效后 | 人工扫码（第 5 节），不自动重试 | 自动重试无法恢复凭证，只会产生无效请求；任务退出码为 2 时需人工介入 |

> 执行调度前确认采集容器在线（`docker compose ps` 为 healthy）。增量任务失败不影响下次执行；正文单篇失败会在后续增量（含 `--include-failed` 的全量）中自动重试。

### 12.2 Windows 任务计划程序（pwsh7）

仓库提供 [sync-incremental.ps1](sync-incremental.ps1)（要求 PowerShell 7.4+），自动定位项目根目录、优先使用项目 `.venv`、透传退出码并将输出追加到 `logs/sync-yyyyMMdd.log`。

先手工验证一次：

```powershell
pwsh -File .\deploy\sync-incremental.ps1 -Account "账号别名"
```

注册每日增量任务（在项目根目录的 pwsh7 会话中执行；路径请按实际位置替换）：

```powershell
$root    = (Get-Location).Path
$script  = Join-Path $root 'deploy\sync-incremental.ps1'
$pwsh    = (Get-Command pwsh).Source
$account = '账号别名'

$action = New-ScheduledTaskAction -Execute $pwsh -Argument `
    "-NoProfile -ExecutionPolicy Bypass -File `"$script`" -Account `"$account`""
$trigger = New-ScheduledTaskTrigger -Daily -At 03:17
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -DontStopOnIdleEnd
Register-ScheduledTask -TaskName 'mp-archiver-sync-daily' `
    -Action $action -Trigger $trigger -Settings $settings `
    -Description 'wechat-mp-archiver 每日增量同步（列表→正文/富媒体）'
```

再注册每周全量对账（周日 04:17，带 `-Full`）：

```powershell
$fullTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 04:17
$fullAction = New-ScheduledTaskAction -Execute $pwsh -Argument `
    "-NoProfile -ExecutionPolicy Bypass -File `"$script`" -Account `"$account`" -Full"
Register-ScheduledTask -TaskName 'mp-archiver-full-weekly' `
    -Action $fullAction -Trigger $fullTrigger -Settings $settings `
    -Description 'wechat-mp-archiver 每周全量回溯+下架对账'
```

任务默认在当前用户下运行；需要未登录时也执行，可在「任务计划程序」图形界面中改为「不管用户是否登录都要运行」并凭据保存（此时请确保 Docker Desktop/WSL 与 `.venv` 在该会话可用）。查看结果：任务计划程序「历史」选项卡，或项目 `logs/` 目录。

退出码监测语义：`0` 成功；`1` 有文章归档失败（下次自动重试）或参数错误；`2` 登录态失效，需按第 5 节重新扫码；`3` 账号未找到（`sync-official` 路径亦表示 AppID/biz 未配置）；`4` 采集服务不可达、端点发现失败、R2 列表 biz 不可得或正文阶段风控/传输熔断。

### 12.3 NAS / Linux（cron）

在安装了归档管线（Python 3.14+ 虚拟环境）的主机上：

```bash
crontab -e
# 每日 03:17 增量（日志追加到项目 logs/）
17 3 * * * cd /srv/wechat-mp-archiver && \
  /srv/wechat-mp-archiver/.venv/bin/mp-archiver sync -a '账号别名' \
  >> logs/sync-$(date +\%Y\%m\%d).log 2>&1
# 每周日 04:17 全量回溯+下架对账（失败重试）
17 4 * * 0 cd /srv/wechat-mp-archiver && \
  /srv/wechat-mp-archiver/.venv/bin/mp-archiver run -a '账号别名' --full --include-failed \
  >> logs/sync-$(date +\%Y\%m\%d).log 2>&1
```

采集服务容器与归档管线可以同机部署；若分机部署，注意管线需能访问采集服务的回环/内网地址（默认 `MP_ARCHIVER_EXPORTER_URL=http://127.0.0.1:5000`，分机时改为内网地址并设置双方一致的 API Token，仍不得暴露公网）。容器化定时可在 NAS 上用与 cron 等价的「计划任务」功能调用同一命令，或由宿主机 `docker exec` 进入含 Python 环境的辅助容器执行；采集服务容器本身不包含归档管线，不要把同步命令发到采集容器内。

## 13. 网络受限时拉取镜像（Docker Hub 不可达）

症状：`compose up` 在 `Trying to pull docker.io/...` 阶段报 `TLS handshake timeout`、`pinging container registry registry-1.docker.io` 失败或 DNS 解析超时。根因是本机网络到 Docker Hub 的连接被干扰，与本项目无关。下列方案只改「从哪拉」，不改镜像名，compose 文件无需改动。

> **时效声明**：以下镜像源为 **2026-09 实测可用**的第三方公开缓存（同一时段 `registry-1.docker.io` DNS 解析超时）。免费镜像源可用性随网络政策变化，失效时更换 `location` 域名即可；第三方源仅用于拉取公开镜像，不要用于私有镜像。

### 13.1 Podman（Linux 直接配置；Windows 配置在 podman machine 内部）

新增 `/etc/containers/registries.conf.d/995-dockerhub-mirror.conf`：

```toml
[[registry]]
location = "docker.io"

  [[registry.mirror]]
  location = "docker.m.daocloud.io"
```

Linux 或已进入 `podman machine ssh` 会话时，可直接落盘：

```bash
sudo tee /etc/containers/registries.conf.d/995-dockerhub-mirror.conf >/dev/null <<'EOF'
[[registry]]
location = "docker.io"

  [[registry.mirror]]
  location = "docker.m.daocloud.io"
EOF
```

Windows 上若 `podman machine ssh` 因私钥权限（`UNPROTECTED PRIVATE KEY FILE`）不可用，可先将上面的 TOML 存为本机临时文件，再经 WSL 直连放入：

```powershell
wsl -d podman-machine-default -u root -- cp /mnt/c/Users/<用户>/AppData/Local/Temp/995-dockerhub-mirror.conf /etc/containers/registries.conf.d/
```

配置即时生效，无需重启，验证镜像仍以原始名落地：

```bash
podman pull docker.io/tmwgsicp/wechat-download-api:latest
podman compose up -d
```

回滚：删除该文件即恢复直连 Docker Hub。注意重建 podman machine（`podman machine reset`/`rm`）后配置会丢失，需重新放置。

### 13.2 Docker Desktop / Docker Engine

- Docker Desktop：Settings → Docker Engine，在 JSON 中加入 `"registry-mirrors": ["https://docker.m.daocloud.io"]`，Apply & Restart；
- Linux Docker Engine：向 `/etc/docker/daemon.json` 写入同名键后 `sudo systemctl restart docker`。

### 13.3 无配置权限时的一次性转存

不改全局配置，手动经镜像源拉取后改回原始名，再正常 `compose up`（镜像名与清单一致即被直接使用，不再触发拉取）：

```bash
# Podman
podman pull docker.m.daocloud.io/tmwgsicp/wechat-download-api:latest
podman tag  docker.m.daocloud.io/tmwgsicp/wechat-download-api:latest docker.io/tmwgsicp/wechat-download-api:latest
# Docker 将 podman 换为 docker 即可
```

缺点：升级（`compose pull`）时需重复手动操作，长期使用建议走 13.1/13.2。
