# 教师准备指南 — Task0 热身项目脚手架

> 本文件面向**教师**。学生只需看 `README-学生.md`。
>
> ⏱️ 准备时间：约 10 分钟（含验证）

---

## 一、这个脚手架是什么

一个**已配置好的最小 Sphinx 项目**，学生拿到后只需编辑 `docs/index.md`，
运行一条命令就能看到自己的文字变成网页——全程不装任何软件。

对应手册：[`../handbook/task-0-warmup.md`](../handbook/task-0-warmup.md)
对应任务：[`../tasks.md`](../tasks.md) 的 Task 0
设计来源：V 对抗审查攻击 A-1（初学者失败点前置）

---

## 二、目录结构

```
warmup-docs/
├── BUILD.md              ← 学生看的构建说明
├── README-学生.md         ← 学生看的快速指引
├── TEACHER-SETUP.md      ← 本文件（教师专用，分发时可删）
├── requirements.txt      ← 依赖清单（教师安装用）
├── build.bat             ← Windows 一键构建
├── build.sh              ← macOS/Linux 一键构建
└── docs/
    ├── conf.py           ← 【教师区】已配好，学生不要动
    └── index.md          ← 【学生区】学生唯一要改的文件
```

---

## 三、准备步骤

### 步骤 1：安装依赖

```bash
cd warmup-docs
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 步骤 2：验证能构建（**必做，别跳过**）

```bash
python -m sphinx -b html docs docs/_build/html
```

**成功标志**：最后一行是 `build succeeded.`

> ⚠️ 如果这一步失败，学生在课堂上 100% 会失败。**务必在分发前验证通过。**

### 步骤 3：试运行一键脚本

- Windows：双击 `build.bat`，应自动构建并打开浏览器
- macOS/Linux：`bash build.sh`

### 步骤 4：分发

把**整个 `warmup-docs/` 文件夹**（**不要含 `.venv/`**）复制到：
- 每台学生机，或
- 共享盘/网络位置（学生自行复制到本地）

> 🚨 **重要：不要复制 `.venv/` 到别的机器！**
> Python 虚拟环境里 `pyvenv.cfg` 硬编码了创建时的 Python 安装路径
> （如 `home = D:\Users\你\anaconda3`）。复制到 Python 路径不同的机器后，
> 运行时会直接报 `did not find executable` 而失败。
> 详见下方「六、关于虚拟环境的重要说明」。

### 步骤 5：在每台机器上准备环境（两种方案）

**方案 A（推荐）：每台机器各自建环境**

在每台学生机上执行一次：

```bash
cd warmup-docs
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

优点：稳定可靠。缺点：需要逐台执行（可写成一键批处理分发）。

**方案 B（省事）：不建 venv，直接用系统 Python**

如果机房所有机器的 Python 环境一致，直接：

```bash
pip install -r requirements.txt   # 装到系统环境
```

`build.bat` / `build.sh` 会自动找到系统 Python。
优点：零额外步骤。缺点：会污染系统环境（机房机器通常无所谓）。

> 💡 **两个方案都行**，关键是**不要跨机器复制 `.venv/`**。
> 我们的构建脚本已内置自愈逻辑：预置环境失效时自动回退到系统 Python，
> 但仍建议按上述方案准备，减少课堂上的意外。

### 步骤 6：删除本文件（可选）

分发前可删掉本文件，避免学生误读。但不删也无妨。

---

## 四、课堂上的三条纪律

| # | 纪律 | 为什么 |
|---|---|---|
| 1 | **不教 `conf.py`** | 学生这节只需要编辑 `index.md`。讲配置 = 引入失败点 |
| 2 | **不教安装** | 环境已预置。任何 `pip` 讨论都是跑题 |
| 3 | **不教 Git** | Git 是 Task1 的内容。这里引入会分散注意力 |

> 🔑 **本任务唯一 KPI 是"正反馈"**，不是知识量。
> 如果学生开始纠结配置文件，说明你过度教学了，**请打断**。

---

## 五、如果连 Sphinx 都装不上（降级方案）

按手册 Task0 的降级路径执行：

1. 改用**在线 Markdown 预览器**（如任意 Markdown 在线编辑器），
   让学生把同样的内容贴进去，看到渲染效果
2. 教师在**自己的机器上投屏**演示一次 Sphinx 构建全过程
3. 学生仍然完成"我写的文字变成了网页"的体验，只是工具换了

降级不影响任务目标达成——**目标是正反馈，不是工具本身。**

---

## 六、关于虚拟环境的重要说明 ⚠️

**这一节是踩过坑之后的结论，请务必读完。**

### 问题：虚拟环境不能跨机器复制

Python 虚拟环境的 `pyvenv.cfg` 里记录了创建时的**绝对路径**：

```ini
home = D:\Users\你\anaconda3
executable = D:\Users\你\anaconda3\python.exe
```

`.venv/Scripts/python.exe` 只是一个"启动器"，它靠上面这两个路径去找到真正的
Python 解释器。**一旦复制到路径不同的机器，它就会失败**：

```
did not find executable at 'D:\...\python.exe'
（退出码 103）
```

这是**已实际验证过的失败**，不是理论推测。

### 应对：构建脚本已内置自愈

`build.bat` / `build.sh` 会：

1. 先尝试 `.venv` 里的 Python
2. **实际执行 `python -c "import sphinx"` 验证是否可用**
3. 不可用则自动回退到系统 Python / `py` 启动器
4. 全部失败才报错，并提示学生改用在线 Markdown 预览器

所以即使预置环境坏了，脚本仍会尽力找到可用解释器。

### 最省心的做法

**分发时不带 `.venv/`，到目标机器后再建。** 这样不会遇到任何路径问题。

---

## 七、常见问题

| 问题 | 原因 | 处理 |
|---|---|---|
| 学生看到 `command not found: python` | 机器没装 Python 或没加 PATH | 用预置 `.venv`；或装 Python 并勾选 Add to PATH |
| `did not find executable` | **跨机器复制了 `.venv`** | 删掉 `.venv`，在目标机器重建（见第六节） |
| 构建成功但页面是旧的 | 浏览器缓存 | `Ctrl+F5` 强制刷新 |
| 学生改坏了 `conf.py` | 误操作 | 从模板重新复制一份 `conf.py` |
| 中文显示成方框 | 字体缺失 | 极少见（alabaster 内置字体够用）；换机器测试 |
| 页面样式很朴素 | 用的是内置主题 | **这是故意的**，见下节 |

---

## 八、为什么主题这么朴素？（设计决策说明）

你可能觉得 alabaster 主题不如 `furo` 好看。这是**刻意的取舍**：

- `furo` 需要额外 `pip install`，多一个依赖 = 多一个失败点
- 热身任务的唯一目标是"零失败跑通"
- 好看的主题留给 Task1，那时学生**自己**安装、**自己**配置——
  那才是学习配置的时机

> 一句话：**Task0 求稳，Task1 求全。** 别在本任务追求美观。

---

## 九、验证清单（分发前逐项确认）

- [ ] `pip install -r requirements.txt` 成功
- [ ] `python -m sphinx -b html docs docs/_build/html` 输出 `build succeeded.`
- [ ] 构建时**无 WARNING**（本脚手架已配置为无警告）
- [ ] `docs/_build/html/index.html` 存在，浏览器中中文正常显示
- [ ] `build.bat` / `build.sh` 可运行（Windows 双击应能自动打开浏览器）
- [ ] **分发时已排除 `.venv/`**（或确认目标机器环境一致）
- [ ] 已删除或保留 `TEACHER-SETUP.md`（按需）
