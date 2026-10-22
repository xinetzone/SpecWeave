---
name: ui-screenshot-review
description: "网页与本地 Web 应用/UI 视觉验证工作流。当需要对页面或界面做截图走查、视觉评审、UI 品质打分、界面打磨前后对比时使用；尤其在交互浏览不可用（如 Playwright MCP 缺系统浏览器）或本地服务无法常驻时，提供静态模板渲染 + headless Chromium 截图 + 视觉模型结构化评审的等价验证方案。触发词：UI 验证、截图评审、视觉走查、页面截图、界面评分、UI 打磨、视觉验收、截图看看效果"
supported_os:
  - windows
source: "镜像自 TeleAgent（星辰超级智能体）平台技能 ui-screenshot-review（2026-10-21 归档；原文版权归 TeleAgent 平台所有，镜像仅供本工作区自托管，不随平台版本演进改写；原位于 TeleAgent 用户级技能目录 skills/ui-screenshot-review/）"
---

---
name: ui-screenshot-review
description: 网页与本地 Web 应用的 UI 视觉验证工作流。当需要对页面或界面做截图走查、视觉评审、UI 品质打分、界面打磨前后对比时使用；尤其在交互浏览不可用（如 Playwright MCP 缺系统浏览器）或本地服务无法常驻时，提供静态模板渲染 + headless Chromium 截图 + 视觉模型结构化评审的等价验证方案。触发词：UI 验证、截图评审、视觉走查、页面截图、界面评分、UI 打磨、视觉验收、截图看看效果。
name_cn: UI 截图评审
description_cn: 对网页或本地 Web 应用做截图与视觉评审的完整工作流：静态渲染、headless 截图、视觉模型打分与迭代打磨。
---

# UI 截图评审（ui-screenshot-review）

为 Web 页面 / 本地应用界面产出**可复核的视觉验证证据**：截图 + 结构化评审结论，并支持「打磨 → 复截图 → 复评审」的迭代闭环。核心价值在于交互浏览不可用（无可用浏览器 MCP、服务无法常驻）时的**等价验证方案**。

## 何时使用

- 本地 Web 应用开发完成，验收标准含 UI 品质要求，需要视觉证据
- 需要独立评审界面质量（配色 / 层级 / 密度 / 一致性 / 破损排查）
- 样式打磨后需要前后对比，证明改进有效
- 交互式浏览器不可用，或页面服务无法在工具调用之间保持存活

注：真实服务的**功能冒烟**可在单条命令内完成（启动 → 轮询请求 → 停止），不依赖跨调用存活；本技能聚焦其后的**视觉验证**环节。

## 决策流程（按序降级）

1. **交互浏览优先**：Playwright MCP 可用且目标 URL 可访问 → 直接 navigate + screenshot，无需降级。
2. **MCP 报浏览器缺失**（如 `Chromium distribution 'chrome' is not found`）→ 改用命令行 headless Chromium 截图（方案 B）。
3. **服务无法在工具调用间存活**（后台常驻启动被拒，见陷阱表第 1 行）→ 先用静态渲染等价方案（方案 A）产出可截图的 HTML。
4. **截图后无法自评**（read 图片不回传图像内容）→ 用 image_understanding 做结构化评审。

## 方案 A：静态渲染等价方案（服务无法常驻时）

核心原则：**复用应用自身的模板引擎与真实模板**渲染静态 HTML，绝不手写页面副本——预览与真实服务输出一致，是评审有效性的前提。

1. 写一次性渲染脚本：导入应用的模板环境（如 starlette `Jinja2Templates` / `jinja2.Environment`），用真实模型或夹具数据填充上下文，逐页渲染写出 HTML。
2. **相对化静态资源引用**：把输出中的 `/static/...` 改写为相对路径 `static/...`，使 `file://` 打开时 CSS/JS 生效。
3. 将应用的 static 目录复制到预览目录旁。
4. 预览目录放临时区（如 `.temp/`），逐页截图评审，用完清理。

## 方案 B：headless Chromium 截图

**定位可执行文件**：Playwright 缓存中通常已有 Chromium，用通配定位最新版本：

```powershell
$chrome = (Get-ChildItem "$env:LOCALAPPDATA\ms-playwright\chromium-*\chrome-win64\chrome.exe" | Select-Object -Last 1).FullName
```

注意：`npx playwright install chromium` 超时**不代表下载失败**，先检查缓存目录是否已有 chrome.exe，再决定是否重试。

**命令模板（PowerShell，每页单独一次工具调用）**：

```powershell
& $chrome --headless=new --disable-gpu --screenshot="<输出>.png" --window-size=1440,1050 --hide-scrollbars "file:///<页面>.html" 2>&1 | Select-String 'written'
```

关键行为：

- **必须 `--headless=new`**：旧 `--headless` 会静默失败（无 PNG 产出、无报错）。
- **每页单独一次工具调用**：在同一条命令里 for 循环批量截图会静默失败；单次调用稳定可复现。
- **用默认 profile**：全新 `--user-data-dir` 首跑可能超时。
- 成功标志：stderr 出现 `N bytes written to file ...png`，据此确认产出。

## 视觉评审（image_understanding + rubric prompt）

read 工具读图可能不把图像内容注入模型上下文（仅返回「读取成功」）；截图评审改用 image_understanding，并配**结构化 rubric prompt**（模板见 [references/review-prompts.md](references/review-prompts.md)）。

固定评审维度：

1. 配色（底色 / 主色 / 文字色 / 卡片层次）
2. 信息层级与排版密度
3. 图标风格一致性
4. 徽章 / 标签 / 按钮的视觉权重
5. 布局破损 / 错位 / 文字溢出 / 对比度排查
6. 总体评分 1–5 + 理由（标尺：1=粗糙后台模板感，5=精致工具感）

**迭代闭环**：评分低于阈值（如 <4）→ 按反馈针对性打磨（典型去模板化手段：品牌渐变色块 logo、标题强调线、卡片顶部渐变条 + hover 浮起、分组点标、输入控件间分隔符）→ 复截图 → 复评审，直到达标。保留前后评分作为改进证据。

## 陷阱速查表

| 现象 | 原因 | 处置 |
|---|---|---|
| 后台常驻服务启动被拒（分离进程 `Start-Process` / 后台模板 exit=-1） | 环境限制进程跨工具调用存活 | 单条命令内「启动→请求→停止」短生命周期冒烟可行；需跨调用浏览页面时改用方案 A，勿反复重试后台启动 |
| 旧 `--headless` 截图无产出 | 旧 headless 模式兼容问题 | 改用 `--headless=new` |
| 一条命令循环截多页全部失败 | 批量调用静默失败 | 每页单独一次工具调用 |
| 全新 `--user-data-dir` 超时 | 首跑初始化慢 | 用默认 profile |
| read 图片后模型「看不到」图 | 图像未注入上下文 | 用 image_understanding 评审 |
| MCP 报系统 Chrome 缺失 | MCP 期望固定系统安装路径 | 用 ms-playwright 缓存的 Chromium；**禁止在用户目录伪造 Chrome 安装位置**（会污染未来真实安装） |
| `npx playwright install` 超时 | 下载收尾慢 | 先查 ms-playwright 缓存是否已有产物，勿盲目重试 |
| 临时目录删除报「路径无效」 | 残留 headless Chromium 进程锁定 profile/缓存文件 | 先核验进程归属（命令行指向 ms-playwright 缓存与本任务临时目录），再 `taskkill /PID <主进程> /T /F` 终止进程树后删除 |

## 产出留档

- 每页：截图 PNG + 评审结论（各维度反馈 + 评分 + 理由）
- 打磨迭代：前后评分对比（如 3/5 → 4/5）+ 改动点清单
- 验收记录中注明验证方式（静态渲染等价 / 真实服务）与截图环境
