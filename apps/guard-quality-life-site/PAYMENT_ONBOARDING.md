# 真实收款操作手册（支付宝电脑网站支付）

> 从申领沙箱凭据到完成**首笔真实支付**的逐步操作清单。本手册在**你的主环境**（非受限沙箱）执行。
> 全程遵守两条铁律：**① 一切值来自支付宝开放平台实发，禁止编造/猜测；② 应用私钥与 `.env` 一律不得进入 Git 或公网**。
>
> 配套代码链路已就绪（见 [README.md](README.md)「开通真实支付」）；本手册回答"每一步具体怎么点、在哪里看验证结果"。

---

## 阶段 0 · 前置准备

| 项 | 说明 | 状态核验方式 |
|---|---|---|
| Python 3.14+ 环境 | `conda activate py314` 后 `python --version` | 应显示 `Python 3.14.x` |
| 应用可运行 | 见 README「快速开始」，`invoke run` 能打开首页 | 浏览器访问 `http://127.0.0.1:8000` 返回 200 |
| `cloudflared` | `cloudflared --version` 有输出即已装；否则按 tasks.py 指引 winget 安装 | 终端能执行该命令 |
| Google Chrome / Edge | Pay > 跳转收银台、异步通知，无需专用浏览器，任选即可 | —

> **关键认知**：支付宝**沙箱环境**用于功能闭环自测（不产生真钱），**正式环境**才真实扣款。本手册先走沙箱验证闭环，再给「正式上线」切换清单。沙箱不需要你上传营业执照。

---

## 阶段 A · 申领沙箱凭据（支付宝开放平台）

> 全程在 `https://open.alipay.com` 操作；Windows 无自动沙箱工具，需人工登录控制台领取。

1. **登录开放平台**：进入 `open.alipay.com`，用支付宝账号登录（建议用企业或个人主线支付宝账号，后续可升级正式商户）。
2. **进入沙箱控制台**：控制台 → **沙箱应用**（位于「开发设置/沙箱」菜单，不同版本入口名略有差异，特征是提供独立的沙箱网关地址）。
3. **记录沙箱信息**，至少拿到 6 项并把它们**原样粘贴到一个临时本地文本**（不要发到任何聊天/云端）：
   - 应用 `AppId`（形如 `2021xxxxxxxxxxxx`）
   - 应用公钥 / 应用私钥——**生成的密钥对中，勾选并复制 `appPrivatePkcsKey`（PKCS#1）**，勿用 JAVA 用的那串
   - 支付宝公钥（沙箱应用详情页单独展示的一串，**与应用公钥不同**）
   - 沙箱网关地址（形如 `https://openapi-sandbox.dl.alipaydev.com`）
   - 沙箱**商家账号**（收款方测试号）
   - 沙箱**买家账号**（付款方测试号，含付款密码）
4. **保存密钥**：把 `appPrivatePkcsKey` 存成文件，例如放在应用目录以外的 `%USERPROFILE%\.gqlsite\app_private_pkcs1.pem`，文件首尾应是 `-----BEGIN…RSA PRIVATE KEY-----` / `-----END RSA PRIVATE KEY-----`（**保持原样，禁止格式转换/拼接**）。

**本步完成条件**：你手里有 `AppId / 应用私钥(PKCS#1) / 支付宝公钥 / 沙箱网关 / 沙箱商家号 / 沙箱买家号` 六项真实值。

---

## 阶段 B · 填写 `.env`

1. 复制模板：
   ```powershell
   cd apps\guard-quality-life-site
   copy .env.example .env
   ```
2. 编辑 `.env`，逐项粘贴真实值：
   ```
   GQLSITE_PAY_APP_ID=2021xxxxxxxxxxxx
   GQLSITE_PAY_APP_PRIVATE_KEY=-----BEGIN…RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----
   GQLSITE_PAY_ALIPAY_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----
   GQLSITE_PAY_SERVER_URL=https://openapi-sandbox.dl.alipaydev.com
   ```
   > ⚠️ 私钥是多行 PEM。在 `.env` 内把换行**保留为真实换行**（不支持写成单行 `\n` 转义）；配置解析会将多行识别为带换行的私钥文本。
3. **自检私钥格式**：确认首行 `BEGIN RSA PRIVATE KEY`（非 `BEGIN PRIVATE KEY`、非 JAVA 8 字节头格式）。选错格式会导致验签失败，是最常见坑。
4. 确认 `.env` **在一级子目录被 Git 忽略**：`git check-ignore .env` 应输出 `.env`（若未忽略，自行加入该应用的 `.gitignore`，**绝不能提交**）。

**本步完成条件**：`.env` 四值已填且格式正确；`git check-ignore .env` 命中。

---

## 阶段 C · 开通公网回调（异步通知必需）

沙箱异步通知必须由支付宝服务器回调到**公网可达**的地址，本机 127.0.0.1 收不到。

1. 启动穿透：
   ```powershell
   cd apps\guard-quality-life-site
   conda activate py314
   $env:PYTHONPATH="src"
   python -m invoke tunnel
   ```
2. 终端会打印形如 `https://<随机串>.trycloudflare.com` 的地址（每次重启变化）。
3. 把该地址写入 `.env`：
   ```
   GQLSITE_PAY_NOTIFY_URL=https://<随机串>.trycloudflare.com/pay/notify
   GQLSITE_PAY_RETURN_URL=https://<随机串>.trycloudflare.com/checkout/gql-weekly
   ```
4. 另开一个终端，用 `--env-file` 加载并重启服务：
   ```powershell
   $env:PYTHONPATH="src"
   python -m uvicorn gqlsite.main:app --port 8000 --env-file .env
   ```

**本步完成条件**：浏览器直接访问 `https://<随机串>.trycloudflare.com/ping` 返回 `{"status":"ok"}`（公网可达性验证）。

---

## 阶段 D · 沙箱首笔真实交易

1. 打开下单页：`http://127.0.0.1:8000/checkout/gql-weekly`。此时应显示**商品确认 + 渲染出的支付宝支付表单**（不再是「支付待配置」）。
2. 点击"去支付"，页面应**自动提交表单**跳转到沙箱收银台（沙箱网关域名 `openapi-sandbox.dl.alipaydev.com`）。收银台有两种：**扫码** 或 **登录付款**。
3. 用**沙箱买家账号**（阶段 A 领取的付款测试号）登录或扫码付款，输入买家付款密码确认支付。
4. 付款成功后，浏览器应 `return` 回跳到 `RETURN_URL`（即你的 `/checkout/gql-weekly` 或落地页），显示"支付成功/订单已提交"。

**本步完成条件**：收银台完成付款，页面回跳到 `RETURN_URL` 且未报错。

---

## 阶段 E · 异步通知到账核对（权威口径）

> 页面跳转只是"前端告诉你的"，**真正的入账凭据是支付宝异步通知**。必须核对这一步，否则不算闭环。

1. 回到跑 `uvicorn` 的终端，观察日志是否收到来自 `/pay/notify` 的 POST（付款后几秒内）。
2. 数据库订单状态应 `PENDING → PAID`：
   ```powershell
   python -c "import sqlite3,os;db=os.environ.get('GQLSITE_DB','.data/gqlsite.db');print([r for r in sqlite3.connect(db).execute('select out_trade_no,status,amount,paid_at from pay_orders')])"
   ```
   （报表路径若你在 `.env` 里配置了 `GQLSITE_DB` 则以实际为准。）
3. 确认 `status=PAID` 且 `paid_at` 非空；`out_trade_no` 与你下单时的订单号一致。

**本步完成条件**：数据库显示该订单 `status=PAID`，且是**异步通知**触发的（非仅页面跳转）。

---

## 阶段 F · 重复通知 / 退款处置（幂等自检）

- **重复通知**：支付宝会重投异步通知。`mark_order_paid` 用 `status=PENDING` 守卫，重复成功通知不会二次发放——可手动向 `/pay/notify` 用同一 body 重发，确认状态不再变化即通过。
- **关单**：未支付订单超时（默认 30m，见 `timeout_express`）由支付宝关闭。若测试产生滞留 `PENDING` 订单，可在控制台批量关闭或忽略（不产生扣款）。

---

## 阶段 G · 正式上线切换清单

沙箱验证通过后，若要真实扣款，按序执行（一旦开启即产生真实交易）：

| # | 动作 | 说明 |
|---|---|---|
| 1 | 入驻并签约「电脑网站支付」 | 在开放平台用真实主体（企业/个体户/个人）开通产品 `alipay.trade.page.pay`，通过签约审核 |
| 2 | 换取正式应用 | 创建/使用正式应用，域名备案、绑定公网域名，配好 `notify_url`/`return_url`，**不再用随机隧道** |
| 3 | 换正式凭据 | 更新 `.env` 四值为正式应用的值（正式网关 `https://openapi.alipay.com`） |
| 4 | `GQLSITE_PAY_PROD=1` | 让配置解析切到正式网关常量 |
| 5 | HTTPS | 公网站点必须 HTTPS，支付宝要求回调与跳转均为 HTTPS |
| 6 | 回归 | 复跑 `invoke check`，并先小额真币自测 1 笔再宣发 |

---

## 安全红线速查

- ⛔ 应用私钥 / `.env` 永不进 Git、不进日志、不贴聊天。
- ⛔ 不向任何"AI 对话/支持论坛"粘贴私钥或完整 `.env`。
- ⚠️ 前台页面显示的结果不可信，**以异步通知 + 数据库 `PAID` 为准**。
- ⚠️ 未支付确认前不重复发起支付（幂等）。
- ✅ 后台上线前把私钥轮换，避免开发密钥泄漏。