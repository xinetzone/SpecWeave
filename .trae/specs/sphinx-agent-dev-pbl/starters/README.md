# 起步文件包（starters/）

> 本目录提供 **Task1 / Task3 需要学生"手建"的配置文件实物**。
> 不是答案，是**复制粘贴源**——避免手打 YAML 时缩进出错。

---

## 一、为什么需要这个目录？

手册里写"在项目根目录建 `.github/workflows/docs.yml`，内容如下…"，
学生在编辑器里**手动敲**这一段 YAML。

YAML 对缩进极其敏感——**少一个空格 CI 就整个不跑**，
而且报错信息往往不指向真正的原因。这个失败与 Task3 的学习目标
（理解"文档即代码"）**毫无关系**，纯粹是手工誊抄成本。

所以：**凡手册里给出"完整文件内容"的配置类文件，这里都提供一份实体。**

| 文件 | 对应手册位置 | 用途 |
|---|---|---|
| `requirements.txt` | Task1 步骤 2 | 依赖清单（CI 会读它） |
| `.gitignore` | Task1 步骤 5 | **AC-5 硬门槛**：排除 `.env` |
| `.github/workflows/docs.yml` | Task3 步骤 3 | GitHub Pages 自动部署 |
| `.github/workflows/docs-intranet.yml` | Task3「访问不了 GitHub？」 | 内网 runner 版（部署步骤不同） |

> ⚠️ **本目录与 `warmup-docs/` 是两回事，不要混用**：
> - `warmup-docs/` 是 **Task0（热身）**的**完整可构建项目**，依赖刻意压到最少，
>   用 Sphinx 默认主题、不装 furo、不装 openai——只为"零失败体验"。
> - `starters/` 是 **Task1 起的正式项目**的**配置片段**，
>   内容与手册正文一致（含 furo、含 openai）。
>
> 拿 `warmup-docs/requirements.txt` 当正式项目的依赖清单用，
> 会导致 **CI 里缺 furo、缺 openai**——构建直接失败。

---

## 二、怎么用

### 步骤 1：建好项目骨架

先按 Task1 步骤 1–3 建目录、激活虚拟环境、`sphinx-quickstart`。
**确认这步成功后**，再往下。

### 步骤 2：复制配置类文件

在**项目根目录**（与 `docs/` 同级，不是 `docs/` 里面）：

```bash
# 依赖清单 —— 覆盖 sphinx-quickstart 生成的那份
cp starters/requirements.txt .

# .gitignore —— 保命文件，务必复制
cp starters/.gitignore .

# CI 配置 —— 注意 .github 目录要先建
mkdir -p .github/workflows
cp starters/.github/workflows/docs.yml .github/workflows/
```

> 📌 **`.gitignore` 复制完成后立刻验证**：
> ```bash
> git status --short
> ```
> 如果输出里看到 `.env` 或 `.venv/`，说明没生效，**立刻停下**排查。
> 这一步关系到 AC-5（密钥安全），不是可选项。

### 步骤 3：安装依赖

```bash
pip install -r requirements.txt
```

---

## 三、常见问题

| 现象 | 原因 | 解决 |
|---|---|---|
| CI 报 `No such file or directory: requirements.txt` | 文件放进了 `docs/` 而不是根目录 | 移到根目录（与 `docs/` 同级） |
| CI 报 `Theme error: no theme named 'furo'` | 用了 `warmup-docs/` 那版依赖清单 | 换成 `starters/requirements.txt` |
| CI 报 YAML 语法错误，但看不出哪一行 | 手工誊抄缩进错了 | 删掉，直接从 `starters/` 复制 |
| `.env` 出现在了 `git status` 里 | `.gitignore` 没复制，或不在根目录 | 复制 `.gitignore` 到根目录，`git rm --cached .env` |
| 内网 runner 报 `runs-on: self-hosted` 找不到 runner | 机房没配自托管 runner | 找 IT 部门；或改用静态托管降级方案 |

---

## 四、教师提示

- 本目录可以**整包发放**（打进学生项目模板），不影响任何测评——
  Task7 现场答辩考的是"你为什么这样设计"，不是"你能不能默写 YAML"。
- **不要**只发 `docs.yml` 不发 `requirements.txt`：
  CI 里 `pip install -r requirements.txt` 会失败，学生卡在与教学目标无关的地方。
- `docs-intranet.yml` 里的部署步骤是**示意性的**，各校机房不同，
  请在开课前替换为 IT 部门确认的实际方式（见 `teacher/SETUP-CHECKLIST.md`）。
