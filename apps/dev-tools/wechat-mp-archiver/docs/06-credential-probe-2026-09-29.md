# 微信凭证联调实测记录（2026-09-29）

> 触发：用户配置好 `.env` 中的微信相关凭证后，请求验证。
> 方法：直接运行项目自带官方接口探针 `mp-archiver official-doctor`（TR-8.1 分阶段探针），不写库、不下载正文。

## 1. 实测输出（原文）

```text
官方接口联调探针（TR-8.1）：配置 → 网络 → token → batchget → biz 一致性

[ok]   [config]  AppID 形态正常：wx4c62…（已脱敏显示）
[ok]   [config]  AppSecret 已配置且形态正常（内容不显示）
[ok]   [config]  biz 来自显式配置：MzcwMzE5…（已脱敏）
[ok]   [network] 网络链路正常（平台以 40001 正确应答探针 token，证明 DNS/TLS/网关可达）
[fail] [token]   换取 access_token 失败 ret=40164: invalid ip <EGRESS_IPV4>
                 ipv6 ::ffff:<EGRESS_IPV4>, not in whitelist
[skip] [batchget] token 无效，跳过实页探测

[fail] 1 个阶段失败，按上述提示处置后重跑本命令
EXIT=1
```

## 2. 结论

**凭证本身正确且有效，唯一阻塞是 IP 白名单。**

判定依据：平台返回 `40164 invalid ip` 而非 `40013 invalid appid` / `40125 invalid appsecret`。若凭证有误，错误码不会是 40164。因此 AppID、AppSecret 均已被平台接纳，仅在"调用方出口 IP 未授权"这一步被拦下。

该出口 IP 已用独立 `curl` 直调 `cgi-bin/token` 复现（同样返回 `<EGRESS_IPV4> not in whitelist`），**非环境偶发、非本项目代码问题**。

## 3. 待处置（用户侧操作，二选一或全做）

### 3.1 解除唯一阻塞：加 IP 白名单

在公众号后台「设置与开发 → 基本配置 → IP 白名单」中新增：

```text
<EGRESS_IPV4>
```

> 该 IP 为当前网络出口地址。若出口 IP 为动态（家宽/移动网络常见），IP 变更后需重新添加——这是该能力的固有约束，不是配置错误。

处置后重跑：

```bash
PYTHONPATH=src <python> -m mp_archiver.cli official-doctor
```

（安装后可直接 `mp-archiver official-doctor`。）

### 3.2 启动采集服务（R2 主路径，未部署）

**当前状态：127.0.0.1:5000 无进程监听，采集服务未部署。**

R2 是**历史全量归档的主路径**；R1 官方接口只覆盖"发布成功"的图文素材、不含传统群发历史，**仅靠 R1 拿不到全量历史**。因此要真正开始归档，R2 必须起来。

前置条件与缺口：

| 项 | 状态 |
|---|---|
| 容器运行时 | ✗ 无 Docker Desktop / Docker CLI；已装 Podman 但 **machine 未启动**（`podman ps` 拒绝连接 127.0.0.1:60432） |
| `deploy/collector.env` | ✗ 缺失，需从 `collector.env.example` 复制 |
| 端口 5000 | ✓ 未被占用 |
| 专用订阅号 + 可扫码微信 | 待确认（需账号管理员本人扫码） |

启动步骤（Podman 路线）：

```bash
cd deploy
cp collector.env.example collector.env
podman machine start          # 先解决 machine 未启动
podman compose up -d          # 或 podman-compose up -d
```

再按 `deploy/README.md` 第 3 节扫码登录，然后 `mp-archiver doctor` 应显示 `[ok] 采集服务在线`。

## 4. 附带环境事实（可复用）

### 4.1 绕过 Python 版本门槛的有效跑法

`pyproject.toml` 声明 `requires-python = ">=3.14"`，本机 managed Python 为 3.13.12、anaconda 为 3.13.9，均低于门槛，`pip install -e .` 会被拒。

**无需安装即可运行**——源码不依赖 3.14 独有语法，直接挂 `PYTHONPATH` 调模块即可：

```bash
PYTHONPATH=src "<anaconda>/python.exe" -m mp_archiver.cli <子命令>
```

anaconda 环境已装齐运行时依赖（httpx / pydantic / pydantic-settings / beautifulsoup4 / markdownify / pandas / jinja2）。

### 4.2 系统代理会伪造"本地服务故障"假象

**本机 shell 环境设有 `http_proxy=127.0.0.1:<PROXY_PORT>`。**

裸测 localhost 时，curl 会走该代理，得到误导性结果：

```text
（裸测）http://127.0.0.1:5000/  →  HTTP/1.1 502 Bad Gateway
        body: upstream connect failed: 目标计算机积极拒绝 (os error 10061)
（绕代理）curl --noproxy '*'    →  code=000（真实：无进程监听）
```

**排查本地服务时必须加 `--noproxy '*'`**，否则会把"服务没起来"误读成"服务起来了但反过来连不上上游"。

### 4.3 凭证安全已核验

`.env` 被 `apps/dev-tools/wechat-mp-archiver/.gitignore:2` 正确忽略（`git check-ignore` 命中，`git status` 该目录干净）→ 凭证未进入版本库。

### 4.4 数据现状

`data/archive.db` 五表（articles / media / comments / metrics / sync_state）**全部 0 行**；`archive/`、`exports/` 为空 → 尚未产生任何归档产出，R2 与 R1 均未跑过。

## 5. R1 调用前的业务前提（未验证）

`MP_ARCHIVER_WECHAT_OFFICIAL_BIZ=MzcwMzE5NTI5NA==` 对应的自有号须为**认证服务号**（或认证订阅号经实测可调）。

- 官方文档适用范围表当前仅列认证服务号；
- 2025-07 平台收紧后，个人主体、未认证主体调用返回 `errcode=48001`，工具会打印降级提示并以退出码 0 结束。

**白名单通过后若见 48001，即为账号主体权限问题，非配置问题。**

## 6. 合规边界（重申）

本工具限个人学习、研究与本地存档使用；必须使用**采集专用订阅号**（非主力号）并由管理员本人扫码；不得将采集服务暴露公网；不得公开再分发归档内容。详见 [05-compliance.md](05-compliance.md)。
