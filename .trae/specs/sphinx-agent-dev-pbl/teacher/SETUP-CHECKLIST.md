# 开课前机房准备清单

> **配套**：[`TEACHER-GUIDE.md`](TEACHER-GUIDE.md) 第〇节
> **用法**：首次开课前逐项打勾。第二学期起可只检查标 ⭐ 的项。
> **预计耗时**：首次 1–2 小时；后续 15 分钟。

---

## 〇、先做三个决定（10 分钟）

这三个决定会决定后面所有准备项。**先定了再动手**。

### 决定 1：CI 部署走哪一档？

| 档 | 判据（现场测） | 选了它意味着 |
|---|---|---|
| ① **GitHub Pages**（默认） | 机房能访问 github.com **并能稳定登录** | 学生需注册个人账号 |
| ② **内网 Git** | 机房无外网，但有内网 Git 服务 | 需提前确认内网服务地址 |
| ③ **RTD 托管替代** | 学生不想管 CI 细节 | 学生**失去**写 `docs.yml` 的机会 |

**现场测试命令**（在机房任一台学生机上跑）：

```bash
# 能不能通 github
curl -I https://github.com

# 能不能通 LLM API（换成你要用的厂商）
curl -I https://api.deepseek.com
```

> ⚠️ **只测"能打开"不够**：DQ-2 的可证伪信号明确指出——
> 若登录态无法保持（如需反复 SMS 验证），学生账号路径的实际成本会高于组织账号，
> 此时应翻转为 ①=组织账号 + ②=离线。**务必让学生实机登录试一次。**

**我的选择**：☐ ①　☐ ②　☐ ③

---

### 决定 2：Task6 走哪一档？

| 档 | 判据 | 需要准备什么 |
|---|---|---|
| **A（零 Token）** | 无配额 / 要控成本 | 打印预置草稿样例（见第 3.4 节） |
| **B（全自动）** | 学生有稳定配额 | 确认每人能申请到 Key |
| **C（降级）** | 预留方案 | 无需额外准备 |

**我的选择**：☐ A　☐ B　☐ C

> 💡 **建议**：默认选 **A**，把 B 作为加分项。
> 理由：档 A 零 Token、教学效果等同（见 [`../decisions.md`](../decisions.md) DQ-3），且不受网络波动影响。

---

### 决定 3：课时走哪个方案？

☐ 方案 A 标准版（12 课时 / 4 周）
☐ 方案 B 紧凑版（8 课时）
☐ 方案 C 集训版（4–5 天）

详见 [`TEACHER-GUIDE.md`](TEACHER-GUIDE.md) 第二节。

---

## 一、软件环境（⭐ 每学期必查）

### 1.1 Python

| 检查项 | 命令 | 期望 |
|---|---|---|
| ⭐ Python 已安装 | `python --version` | ≥ 3.10（本项目实测 3.13.12 可用） |
| ⭐ pip 可用 | `pip --version` | 显示版本 |
| ⭐ 能装包 | `pip install --dry-run sphinx` | 无权限错误 |

**检查结果**：

- [ ] Windows 学生机 `python --version` → `____________`
- [ ] 是否已在 PATH 中？　☐ 是　☐ 否（否 → 需重新安装并勾选 "Add to PATH"）
- [ ] ⚠️ 若是**离线机房**，需提前下载 whl 包（见 1.3 节）

> 🚨 **常见坑**：装了 Python 但没勾 Add to PATH → 学生 `python` 命令找不到。
> 这个坑会在 Task1 第一分钟出现，**务必提前查**。

### 1.2 依赖包

**Task0 热身**（`warmup-docs/`，只需 4 个包）：

```bash
pip install sphinx myst-parser sphinx-design sphinx-copybutton
```

**Task1–Task7**（完整依赖）：

```bash
pip install sphinx myst-parser sphinx-design sphinx-copybutton python-dotenv openai furo sphinxcontrib-mermaid
```

**实测版本参考**（2026-09 验证通过）：

| 包 | 实测版本 |
|---|---|
| Sphinx | 9.1.0 |
| myst-parser | 5.1.0 |
| furo | 2025.12.19 |
| sphinx-design | 0.7.0 |
| sphinx-copybutton | 0.5.2 |
| sphinxcontrib-mermaid | 2.1.1 |
| openai | 3.20.0 |
| python-dotenv | 1.2.3 |

- [ ] ⭐ 已在一台机器上验证 `pip install` 全部成功
- [ ] 已记录实际安装的版本（供后续排错参考）：`____________`

### 1.3 离线机房：预下载 whl 包

若机房无外网，需在有外网的机器上先下载：

```bash
# 在有外网的机器上执行
pip download -d ./pkgs \
  sphinx myst-parser sphinx-design sphinx-copybutton \
  python-dotenv openai furo sphinxcontrib-mermaid

# 把 ./pkgs 拷贝到机房，然后
pip install --no-index --find-links=./pkgs \
  sphinx myst-parser sphinx-design sphinx-copybutton \
  python-dotenv openai furo sphinxcontrib-mermaid
```

- [ ] 已下载 whl 包到共享盘：`____________`
- [ ] 已在机房一台机器上验证离线安装成功
- [ ] ⚠️ 注意：需按机房 Python 版本下载对应 whl（3.10/3.11/3.12 不通用）

> 💡 **简化方案**：若机房所有机器配置一致，可在一台机器装好后**用系统 Python**
> （不建 venv），其他机器无需再装。但**绝不可跨机器复制 `.venv/`**——
> 详见 [`../warmup-docs/TEACHER-SETUP.md`](../warmup-docs/TEACHER-SETUP.md) 第六节（真实验证过的 P0 坑）。

---

## 二、脚手架与模板分发（⭐ 每学期必做）

### 2.1 Task0 热身脚手架

| 检查项 | 命令 / 动作 |
|---|---|
| ⭐ 已验证能构建 | `cd warmup-docs && python -m sphinx -b html docs docs/_build/html` → `build succeeded.` |
| ⭐ 已确认**不含** `.venv/` | `ls warmup-docs/`（不应看到 .venv 目录） |
| 已确认无 WARNING | 构建输出中无 `WARNING` 字样 |
| 已决定是否保留 `TEACHER-SETUP.md` | ☐ 保留　☐ 删除（分发前删，避免学生误读） |

**分发位置**：

- [ ] 每台学生机本地
- [ ] 共享盘 / 网络位置：`____________`
- [ ] 学生自行复制到本地

> 🚨 **不要分发 `.venv/`！** `pyvenv.cfg` 硬编码创建时的绝对路径，
> 跨机器复制必然报 `did not find executable`（退出码 103）。
> 这是**已实际验证过的失败**，不是理论推测。

### 2.2 Task4/5 代码模板

| 检查项 | 动作 |
|---|---|
| ⭐ `templates/agent.py` 可复制 | 确认文件存在且非空（约 300 行） |
| ⭐ `templates/.env.example` 可复制 | 确认文件存在 |
| 已确认 `TODO` 标记数量 | 应有 **13 处**（`grep -c TODO templates/agent.py`） |
| 已验证模板能编译 | `python -m py_compile templates/agent.py` 无报错 |
| 已验证未配密钥不崩 | `python -c "import agent"`（在模板目录）不抛异常 |

> 💡 **`import agent` 不崩**是模板的关键设计（延迟初始化）。
> 若这里报 `OpenAIError`，说明模板被改坏了，会导致学生在**第一条命令**就撞上
> 与环境相关而非知识点相关的报错。详见 [`../insight.md`](../insight.md) T-1（P0）。

---

## 三、学生侧准备（课前一周通知学生）

### 3.1 账号与密钥

| 项 | 说明 | 截止 |
|---|---|---|
| GitHub 个人账号（走档①时） | 让学生**提前注册**，课上注册会卡 | 课前 3 天 |
| LLM API Key（走档 B 时） | 确认学生能申请、有配额 | 课前 3 天 |
| 或：确认走档 A（零 Token） | 无需申请 | — |

- [ ] 已通知学生注册 Github 账号（若走档①）
- [ ] 已确认 LLM Key 获取方式（若走档 B）：`____________`
- [ ] ⚠️ 已提醒学生：**Key 绝不外传、绝不提交到仓库**

### 3.2 后台启动说明（给学生的话术）

建议直接发这段给学生：

> **课前准备（10 分钟）**
>
> 1. 注册一个 GitHub 账号（如果你还没有），**用户名记住**。
> 2. 确认你能登录（不要只注册不登录）。
> 3. 如果老师通知需要 LLM API Key，去 `<你的平台>` 申请一个，**保存在安全的地方**。
> 4. 不需要现在学任何东西——课上会带你做。
>
> ❗ 一个提醒：**不要**把密钥发给任何人，也不要写进代码里。

---

## 四、部署平台准备（按第〇节的决定 1）

### 若选 ① GitHub Pages（学生个人账号）

| 检查项 | 说明 |
|---|---|
| ⭐ 机房能访问 github.com | `curl -I https://github.com` 返回 200 |
| ⭐ 学生能**成功登录**（不只注册） | 让学生实机试一次，确认不需要反复验证 |
| 已了解 Pages 设置路径 | 仓库 → Settings → Pages → Source 选 **GitHub Actions** |
| 已准备 `docs.yml` 范本 | 见 [`../handbook/task-3-ci.md`](../handbook/task-3-ci.md) |
| 已知道 `-W` 不可省 | 三档均执行 `sphinx-build -W --keep-going` |

> 🚨 **最容易错的一步**：Pages 的 Source 必须选 **GitHub Actions**，
> 不要选 "Deploy from a branch"——后者不会跑我们的 CI。

### 若选 ② 内网 Git

| 检查项 | 说明 |
|---|---|
| 内网 Git 服务地址已确认 | `http://____________` |
| 学生账号已在内网服务上开好 | |
| 自托管 runner 已部署并在线 | 确认 runner 状态为 idle |
| **[本地化] `docs-intranet.yml` 三项已改写** | 见下方 ⬇️ |
| **[已备好] 内网版 CI 实物** | 直接用 [`../starters/.github/workflows/docs-intranet.yml`](../starters/.github/workflows/docs-intranet.yml)，**无需手写** |

#### ⬇️ `docs-intranet.yml` 本地化三项（开课前必做）

该文件已把**默认值填好**（开箱即用），但三项参数因校而异，请按机房实际改写：

| # | 位置 | 默认值 | 改成 |
|---|---|---|---|
| 1 | `runs-on:` | `self-hosted` | 贵校 runner 的实际标签（如 `[self-hosted, linux, x64]`） |
| 2 | `python-version:` | `'3.11'` | 机房实际 Python 版本（建议 3.10+） |
| 3 | `DEPLOY-MODE` 段 | 方式 B（打包 artifact） | 二选一；若选方式 A 还要改 `/var/www/docs/` 为实际 Web 根目录 |

> ✅ **文件内已内嵌这份清单**（见文件头注释"教师本地化清单"）——
> 教师打开文件即可照做，无需回到本页对照。
>
> 🚫 **不要修改 `Build docs` 那一步**：`sphinx-build -b html -W --keep-going docs docs/_build/html`
> 是本任务的教学目标，改了就等于把 Task3 的核心删掉了。

> 💡 **若内网连 Git 服务都没有**：回退到最简方案——
> 本地 `sphinx-build` + 把 `_build/html` 拷贝到共享盘（学生自己的文件夹）。
> 此时 **TR-3.1 需相应下调**：改为验证"本地构建产物 + 共享盘可访问"，
> 而非验证 CI 绿灯。详见 [`../decisions.md`](../decisions.md) DQ-2 可证伪信号。

### 若选 ③ RTD 托管替代

| 检查项 | 说明 |
|---|---|
| 学生已注册 RTD 账号 | 用 Github 账号关联即可 |
| 已确认 RTD 能拉到学生仓库 | 关联后测试一次构建 |
| ⚠️ 已知代价 | 学生跳过 `docs.yml` 编写 → **TR-3.1 改为验证 RTD 构建记录** |

---

## 五、Task6 档 A 素材准备（若走档 A）

✅ **素材已随方案提供，无需自备**：[`task6-tier-a/`](task6-tier-a/README.md)

| 文件 | 给谁 | 说明 |
|---|---|---|
| [`task6-tier-a/calculator-draft.md`](task6-tier-a/calculator-draft.md) | **发给学生** | 预置草稿样例，已刻意植入 3 处误解 |
| [`task6-tier-a/ANSWER-KEY.md`](task6-tier-a/ANSWER-KEY.md) | **只给教师** | 3 处误解的具体内容 + 2 处加分差异 + 课堂讨论引导稿 |
| [`task6-tier-a/README.md`](task6-tier-a/README.md) | 教师 | 分发顺序与红线讲法 |

> 🚨 **`ANSWER-KEY.md` 不得发给学生。** 学生手册里**已刻意删去**三种误解的说明——
> 提前给出，本任务的发现过程即归零。

### 课前核对

- [ ] 已打印 `calculator-draft.md`（每组 1 份，或准备投影）：`____` 份
- [ ] 已阅读 `ANSWER-KEY.md`，**未**发放给学生
- [ ] 已确认学生手册对应位置**没有**泄漏答案（方案已修正，勿用旧版）

> 💡 **课堂组织建议**：发草稿 → 学生独立找差异（10 min）→
> **小组讨论"为什么 AI 会这么理解"（10 min）** → 全班分享（10 min）。
>
> 第二个环节是关键：学生要意识到**误解的根源是"代码里没写出来的东西"**，
> 而不是"AI 太笨"。这才是本任务的认知目标。
> **引导稿见 [`task6-tier-a/ANSWER-KEY.md`](task6-tier-a/ANSWER-KEY.md) 第三节。**

> 🚨 **别忘了讲诚实性红线**：用档 A 必须在 `diff-notes.md` 开头声明
> "本次草稿来自教师预置样例"。谎报判 0。讲法：
> *"用老师给的样例拿满分，和调 API 拿满分，是一样多的分。"*

---

## 六、评分材料准备

| 检查项 | 份数 |
|---|---|
| ⭐ 评分表已打印（[`SCORING-SHEET.md`](SCORING-SHEET.md) 第二节起） | 每组 1 份 |
| ⭐ 答辩记录表已打印（SCORING-SHEET 第六节） | 每组 1 份 |
| Git 检查表已打印（SCORING-SHEET 第七节） | 教师自用 1 份 |
| **档 C 折半版已打印**（若教室可能断网） | 备用 |

> ⚠️ **若全班走档 C，记得用折半版**，且**全组统一**（混用会导致成绩不可比）。
> 详见 [`SCORING-SHEET.md`](SCORING-SHEET.md) 第五节。

---

## 七、开课前 30 分钟最终检查

### 教师机

- [ ] ⭐ 教师机已装好完整依赖并能构建
- [ ] ⭐ 教师机已跑通一次完整流程（Task0→Task5）
- [ ] 已准备好投屏演示的 Task0 构建过程
- [ ] 已把 Task1 的「常见报错」小节加入收藏/置顶

### 学生机（抽查 1–2 台）

- [ ] ⭐ `python --version` 正常
- [ ] ⭐ `pip install sphinx` 能成功（或已预装）
- [ ] `warmup-docs/` 已就位且能构建
- [ ] 能访问 github.com（或内网 Git）

### 分发材料

- [ ] `warmup-docs/`（**不含 .venv**）
- [ ] `templates/agent.py` + `.env.example`
- [ ] `handbook/`（8 个任务的 Markdown，学生可自行查阅）
- [ ] Task6 档 A 草稿样例（若走档 A）
- [ ] 评分表 + 答辩记录表

### 心里有数的三件事

- [ ] 我知道 **Task0 不教配置**（唯一 KPI 是正反馈）
- [ ] 我知道 **Task2 要强调手写**（物理断 AI 更好）
- [ ] 我知道 **Task7 要随机抽函数**（不让学生自己选）

---

## 八、故障应急预案

| 故障 | 现场处理 | 事后 |
|---|---|---|
| 机房突然断外网 | 切档 C（Task6）+ 本地构建代替部署 | 按 [SCORING-SHEET 第五节](SCORING-SHEET.md) 折半版评分 |
| LLM API 全部超时 | 用 `templates/` 的 `ask_simple()` 演示；Task6 切档 A | 通知学生课后补 |
| 学生机 Python 环境全坏 | 用在线的 Markdown 预览器完成 Task0；Task1 改期 | 检查是否 PATH 问题 |
| 学生 GitHub 账号登不上 | 切内网 Git 档，或本地构建 + 共享盘 | 记录账号问题，下次课前先测 |
| 某组进度严重落后 | 允许用 `templates/` 全量模板（**不影响评分**） | 保证 Task7 至少能展示 |

> 🔑 **应急的共同原则：降范围，不降标准。**
> 少做一个工具可以，讲不清已做的那个不行。

---

## 九、清单存档

| 项 | 内容 |
|---|---|
| 检查日期 | |
| 检查人 | |
| 选择档位 | CI: ☐① ☐② ☐③　｜　Task6: ☐A ☐B ☐C　｜　课时: ☐A ☐B ☐C |
| 实测 Python 版本 | |
| 实测依赖版本 | |
| 内网 Git 地址（如适用） | |
| 遗留问题 | |
