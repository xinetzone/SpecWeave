# 知乎打卡工作台（zhihu-checkin-hub）

本地单用户 Web 应用，服务 [`projects/monetize/zhihu-monetization/`](../../../projects/monetize/zhihu-monetization/) 执行工作台：把「Markdown 手工台账 + 手工浏览器发布」升级为「每日打卡追踪 + 发布前固定门强制 + 浏览器半自动填充 + 发布存证回写」的闭环。

- 目标追踪与 tracker.md 行动项勾选回写（行级最小替换 + 原子写 + 备份 + round-trip 校验）
- 每日打卡：创作记录、互动记录、合格日判定、连续天数与本周回答/想法计数
- 盐粒到账登记、周复盘与中断记录（只照抄官方整数盐粒，不做收益估算）
- 草稿箱（Markdown/YAML 文件化，状态机 draft → ready → published）
- 发布前「固定门」四问：不过门不可进入填充
- 三类发布：知乎专栏文章 / 问题回答 / 想法，经 kimi-webbridge 自动填充到**你本人的浏览器**，最终「发布」按钮永远由你本人点击；点「我已发布」后回读 URL 并截图存证、回填草稿与当日打卡

## 安装（Python 3.14 / py314）

需要 conda 环境 `py314`（Python ≥ 3.14）：

```powershell
conda activate py314
cd apps/dev-tools/zhihu-checkin-hub
pip install -e .
```

依赖最小集：fastapi、uvicorn、jinja2、typer、pyyaml、httpx、python-multipart（scikit-build-core 纯 Python 包构建，无原生编译）。

## 用法

工作区自动定位顺序：`--workspace/-w` → 环境变量 `ZHIHU_CHECKIN_WORKSPACE` → 应用目录 `config.yaml` → 从当前目录向上寻找 `projects/monetize/zhihu-monetization` → 仓库默认路径。

```powershell
# 校验工作区结构（tracker.md、local/ 区、.gitignore 卫生）
zhihu-checkin check
zhihu-checkin check -w D:\spaces\SpecWeave\projects\monetize\zhihu-monetization

# 启动本地工作台（默认 127.0.0.1:17253，仅绑定 loopback）
zhihu-checkin serve
zhihu-checkin serve -w <工作台目录> -p 17253
```

启动后浏览器打开 `http://127.0.0.1:17253`。同一工作区同时只能启动一个实例（`local/.serve.lock` 文件锁，防止并发写坏 tracker.md）。

可选：编辑应用目录 `config.yaml` 覆盖 `port`、`webbridge_endpoint`、`session`、`week_start` 等。

## 发布桥前置（仅发布功能需要）

1. 运行 kimi-webbridge daemon（本地端点 `http://127.0.0.1:10086/command`，会话名固定 `zhihu-checkin-hub`）；
2. 在你自己的浏览器里登录知乎；
3. 打开发布页，应用会先显示桥健康状态（就绪 / daemon 未运行 / 浏览器未连接 / 未登录知乎）。

没有 daemon 时，打卡、记录、草稿、tracker 勾选等全部离线功能照常可用；填充失败自动降级为「打开目标页 + 正文入剪贴板 + 中文手动指引」，不会产生任何半成品回填。

## 数据边界

- 代码在本目录（主仓库直接管理）。
- 运行时数据**只**写入工作台的 `local/`：`local/entries/YYYY-MM-DD.yaml`、`local/posts/drafts/`、`local/records/*.yaml`、`local/screenshots/`、`local/backups/`、`local/gate-exports/`。
- `tracker.md` 允许行级勾选回写；`records.md` 等模板文件不被修改。
- `local/` 必须被工作台 `.gitignore` 忽略（`zhihu-checkin check` 会告警），真实个人数据不入库。
- 零数据库，全部为 Markdown/YAML 文本，可直接人工审阅。

## 安全与合规边界

- **无 AI**：应用不调用任何 LLM/生成式接口（无 openai/anthropic/chat completions），不生成、不润色、不扩写任何文案。内容全部本人撰写——这是变现计划 **F-037（AI 协作排除条款）** 的执行层落地。
- **无凭证**：应用不读取、不存储浏览器 cookie、知乎登录态（z_c0）、密码或 Access Secret；浏览器登录由你本人在真实浏览器中完成。
- **仅本地**：服务只允许绑定 127.0.0.1/localhost/::1；所有写操作有 CSRF 双提交令牌与 Origin/Referer 本地白名单。
- **人是发布主体**：自动操作仅限打开编辑入口（且回答入口按钮文本走白名单）与填充标题/正文；源码静态保证不存在最终发布按钮的程序化点击。
- **不做收益预估**：盐粒按官方创作者中心显示的整数照抄登记，人民币折算口径（F-059：100 盐粒 = 1 元）仅作文字标注，不在应用内推算收入。

## 测试

```powershell
conda run -n py314 python -m pytest tests/ --cov=src/zhihu_checkin_hub
```

关键模块（tracker/gate/streak/publisher）覆盖率 ≥ 90%，整体 ≥ 80%；`tests/test_audit.py` 以静态扫描守护上述全部红线，并断言真实工作台 `local/` 在测试后零 git 条目。
