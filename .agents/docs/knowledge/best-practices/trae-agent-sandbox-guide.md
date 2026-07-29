---
id: "trae-agent-sandbox-guide"
title: "TRAE Agent 沙箱配置与使用最佳实践指南"
date: "2026-07-20"
category: "best-practices"
source: "https://docs.trae.cn/ide/sandbox | https://docs.trae.cn/solo/sandbox | 社区实践总结"
tags: ["sandbox", "security", "agent-environment", "configuration", "trae", "best-practices", "newbie-guide"]
version: "1.0"
---

# TRAE Agent 沙箱配置与使用最佳实践指南

## 一、沙箱核心概念

沙箱为智能体生成的命令提供**受限的执行环境**，确保 AI 在安全隔离的环境中运行命令，防止未经授权的文件访问和系统误操作。

> **核心设计哲学**：沙箱是 AI 的"安全游乐场"——AI 可以在里面自由操作，但不会影响到你的真实系统。

### 支持的操作系统

- **macOS**：基于 sandbox-exec 自动配置
- **Windows**：原生支持 + Remote WSL 2
- **Linux**：Debian 10+ / Ubuntu 20.04+（通过 Remote SSH 和 Bubblewrap 实现）

---

## 二、运行模式选择推荐

| 使用场景 | 推荐模式 | 安全性 | 便捷性 | 理由 |
|---|---|:---:|:---:|---|
| **日常开发（默认）** | ✅ 沙箱运行（支持白名单） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 安全性最高，AI 误操作不会影响系统 |
| **首次使用/陌生项目** | ✅ 手动运行 | ⭐⭐⭐⭐⭐ | ⭐ | 每条命令都确认，最安全 |
| **完全信任的项目/个人实验项目** | ⚠️ 自动运行（沙箱外） | ⭐⭐ | ⭐⭐⭐⭐⭐ | 最便捷但风险高，仅推荐可随时回滚环境 |
| **处理敏感数据/公司项目** | ✅ 沙箱运行 + 严格白名单 | ⭐⭐⭐⭐⭐ | ⭐⭐ | 防止数据泄露和误操作 |
| **Work 模式（MTC）** | 🔒 内置虚拟化沙箱 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Work 模式强制隔离，无需额外配置 |

> **💡 推荐原则**：默认使用「沙箱运行（支持白名单）」，按需添加信任命令到白名单平衡安全与效率。

---

## 三、默认安全策略

启用沙箱后，TRAE 的文件目录访问权限如下：

| 权限类型 | 目录类型 | 目录列表（Windows） |
|---|---|---|
| 🔴 **只读** | 受保护目录 | `.vscode` |
| 🔴 **只读** | 根目录 | `/`（所有未显式声明为可写的目录均为只读） |
| 🟢 **读写** | 项目目录 | 除 `.trae`、`.vscode` 和 `.git` 之外的项目文件与目录 |
| 🟢 **读写** | 临时目录 | `~/AppData/Local/Temp`、`~/AppData/LocalLow/Temp` |
| 🟢 **读写** | 缓存目录 | `~/AppData/Local/` 下的工具缓存路径 |
| 🟢 **读写** | 工具依赖目录 | pip、uv、npm/pnpm、cmake 等工具的依赖目录 |
| 🟢 **读写** | 语言工具链 | Go、Java、Python、Node.js、Rust、C++ 等 |

> **重要规则**：
> - 当前安全策略不涉及网络访问（Windows 可通过 sandbox.json 配置网络）
> - 读写权限继承当前用户权限
> - 读写与只读权限冲突时，以**只读权限**为准

---

## 四、白名单配置推荐

白名单中的命令前缀将跳过沙箱，直接在沙箱外执行。请谨慎配置。

### ✅ 推荐加入白名单（低风险、高频使用）

```bash
# 代码查看与搜索
git status
git diff
git log
git branch
ls
cat
head
tail
grep
find
which
echo
pwd

# 包管理（只读查询）
pip list
pip show
npm list
npm view
pnpm list
node -v
python --version
java -version

# 编译/类型检查/测试（通常安全）
npm run build
npm run typecheck
npm run lint
tsc --noEmit
mypy
ruff check
pytest --collect-only
```

### ⚠️ 谨慎加入白名单（中风险）

```bash
# 代码格式化（会修改文件，但在项目目录内通常安全）
npm run format
black
prettier
rustfmt

# Git 写操作（确保在正确分支）
git add
git commit
```

### ❌ 不推荐加入白名单（高风险）

**绝对不要轻易加白名单**：

```bash
rm -rf
rm -r
mv（跨目录移动时）
del /f /s /q（Windows）
format
mkfs
dd
chmod -R 777
chown -R
```

> **社区经验警示**：
> - 白名单是命令前缀匹配：加 `git` 会让所有 `git` 开头的命令都在沙箱外执行，建议精确到子命令
> - 沙箱内仍然不支持高危命令（如 `rm`、`mv`），配置了白名单也不行，需要在沙箱外执行
> - 务必随时 git commit，误删可通过版本控制恢复

---

## 五、自定义 sandbox.json 配置

通过 `sandbox.json` 文件可精细控制沙箱的文件系统和网络访问范围。

### 配置文件位置

- **Windows**：`%USERPROFILE%\.trae-cn\sandbox.json`
- **macOS & Linux**：`~/.trae-cn/sandbox.json`

### 打开方式

1. 前往 **设置 > 对话流**
2. 在「沙箱自定义配置」处，点击「打开配置」按钮
3. TRAE 将自动创建并打开 sandbox.json

### 文件初始结构

```json
{
  "filesystem": {
    "readWrite": [],
    "readOnly": []
  },
  "network": {
    "default": "allow",
    "allow": [],
    "deny": []
  }
}
```

---

## 六、推荐配置模板

### 模板 1：通用开发配置（默认推荐）

```json
{
  "filesystem": {
    "readWrite": [
      "$WORKSPACE_FOLDER",
      "~/AppData/Local/Temp",
      "~/.cache",
      "~/AppData/Local/pip",
      "~/AppData/Local/npm-cache",
      "~/AppData/Local/pnpm"
    ],
    "readOnly": [
      "$WORKSPACE_FOLDER/.git",
      "$WORKSPACE_FOLDER/.vscode",
      "$WORKSPACE_FOLDER/.trae"
    ]
  },
  "network": {
    "default": "allow",
    "allow": [],
    "deny": []
  }
}
```

### 模板 2：高安全配置（处理敏感项目/公司项目推荐）

```json
{
  "filesystem": {
    "readWrite": [
      "$WORKSPACE_FOLDER/src",
      "$WORKSPACE_FOLDER/tests",
      "~/AppData/Local/Temp"
    ],
    "readOnly": [
      "$WORKSPACE_FOLDER",
      "C:/Python3*",
      "C:/Program Files/nodejs"
    ]
  },
  "network": {
    "default": "deny",
    "allow": [
      "*.github.com:443",
      "*.gitcode.com:443",
      "*.npmjs.com:443",
      "*.pypi.org:443",
      "registry.npmjs.org:443",
      "files.pythonhosted.org:443"
    ],
    "deny": [
      "[10.0.0.0/8]",
      "[172.16.0.0/12]",
      "[192.168.0.0/16]",
      "localhost:22",
      "localhost:3306",
      "localhost:5432"
    ]
  }
}
```

**特点**：
- 默认禁止所有网络访问
- 仅允许访问 GitHub、npm、PyPI 等必要包管理仓库
- 禁止访问内网网段和本地数据库端口
- 仅开放项目 `src/` 和 `tests/` 目录写权限

### 模板 3：特殊软件适配（如 MATLAB、大型专业软件）

当沙箱拦截专业软件（如 MATLAB）的注册表或缓存文件访问时：

```json
{
  "filesystem": {
    "readWrite": [
      "$WORKSPACE_FOLDER",
      "C:/Program Files/MATLAB",
      "~/AppData/Local/MathWorks",
      "C:/Python314/Lib/site-packages",
      "~/AppData/Local/Temp"
    ],
    "readOnly": [
      "C:/Python314/Lib"
    ]
  },
  "network": {
    "default": "allow",
    "allow": [],
    "deny": []
  }
}
```

> **更简单的方案**：直接将 MATLAB 命令前缀加入白名单在沙箱外运行，比逐个配置路径更省事。

---

## 七、路径格式说明

`sandbox.json` 中支持以下路径格式：

| 格式 | 说明 | 示例 |
|---|---|---|
| 绝对路径 | 完整路径 | `C:\Program Files`、`/usr/local/bin` |
| Home 目录 | `~` 表示用户主目录 | `~/Documents` |
| 环境变量 | `$VAR` | `$HOME/.config`、`$LOCALAPPDATA` |
| 工作区变量 | `$WORKSPACE_FOLDER` | 当前打开的项目目录 |
| 通配符 | `*` 匹配任意字符 | `C:/Python3*` |

### 路径匹配优先级规则

1. 路径越长、越精确，优先级越高
2. 如果路径同时在 `readWrite` 和 `readOnly` 中，**readOnly 优先级更高**
3. 未配置的路径遵循系统默认安全策略

---

## 八、网络配置说明（仅 Windows 支持）

`network` 字段用于管理沙箱内进程的网络请求策略（仅 Windows 支持）。

### 网络目标匹配格式

| 格式 | 含义 | 示例 |
|---|---|---|
| `[ip]` | 单个 IP（所有端口） | `"[192.168.1.100]"` |
| `[ip/mask]` | CIDR 子网（所有端口） | `"[192.168.1.0/24]"` |
| `[ip]:port` | 单个 IP:单个端口 | `"[192.168.1.100]:443"` |
| `domain` | 域名（所有端口） | `"example.com"` |
| `*.domain` | 通配符域名 | `"*.example.com"` |

### 网络场景示例

#### 场景 A：仅允许访问特定域名（防数据泄露）

```json
{
  "network": {
    "default": "deny",
    "allow": ["*.github.com:443", "*.gitcode.com:443"],
    "deny": []
  }
}
```

#### 场景 B：禁止访问内网（开发连公网时推荐）

```json
{
  "network": {
    "default": "allow",
    "allow": [],
    "deny": [
      "[10.0.0.0/8]",
      "[172.16.0.0/12]",
      "[192.168.0.0/16]",
      "localhost:22",
      "localhost:3306",
      "localhost:5432"
    ]
  }
}
```

---

## 九、命令运行策略

### 普通命令

- **在白名单内**：自动在沙箱外运行
- **不在白名单内**：自动在沙箱内运行；如果运行失败，系统会询问是否需要在沙箱外重试

### 高风险命令

当智能体生成 `rm -rf` 等高风险命令时，系统会拦截并弹出提示，你可以选择：

| 选项 | 说明 |
|---|---|
| **跳过** | 跳过该命令，不运行（最安全） |
| **添加到白名单** | 将该命令前缀加入白名单，之后同类命令在沙箱外运行 |
| **运行** | 本次仅在沙箱内运行该命令 |

---

## 十、不同场景最佳实践

### 🚀 场景 1：日常编码开发

1. **模式**：沙箱运行（支持白名单）
2. **白名单**：添加 `git status`、`git diff`、`ls`、`cat`、`npm run`、`pytest` 等常用命令前缀
3. **sandbox.json**：使用「通用开发配置」模板
4. **习惯**：AI 提交代码前先人工 review，高风险命令（删除、移动）手动确认

### 🔒 场景 2：处理公司敏感项目

1. **模式**：沙箱运行（不使用自动运行）
2. **白名单**：仅加只读查询命令，不加任何写操作命令白名单
3. **sandbox.json**：使用「高安全配置」模板，禁止内网访问
4. **额外措施**：
   - 开启隐私模式（对话内容不用于模型训练）
   - 重要文件手动备份
   - Git 频繁提交，便于回滚

### 🧪 场景 3：快速原型/个人实验项目

1. **模式**：可以考虑 Work 模式（完全虚拟化隔离）
2. **白名单**：适当放宽，提升效率
3. **注意**：Work 模式文件在虚拟磁盘中，记得及时导出产物到本地
4. **文件同步提示**：明确告诉 AI "请把文件保存在当前项目根目录下，不要使用绝对路径"

### 🐛 场景 4：遇到沙箱拦截报错

**报错特征**：
```
TRAE Sandbox Error: hit restricted
Not allow operate files: xxx
```

**解决方案优先级**：
1. **最省事**：将该命令前缀加入白名单（仅限信任的命令）
2. **精细化控制**：在 `sandbox.json` 中给被拦截的路径添加 `readWrite` 权限
3. **最安全**：手动在外部终端执行该命令，不让 AI 自动执行

---

## 十一、Work 模式特别说明

TRAE Work 桌面版的 Work 模式采用**完全虚拟化隔离技术**，与 Code 模式的沙箱机制不同：

| 特性 | Code 模式沙箱 | Work 模式虚拟化沙箱 |
|---|---|---|
| 隔离方式 | 文件系统权限限制 | 完整虚拟环境（VMCache） |
| 磁盘访问 | 直接读写授权目录 | 虚拟磁盘镜像 |
| 环境配置 | 使用本地环境 | 预装完整 Skills 工具链 |
| 文件获取 | 直接在本地目录 | 通过「任务产物」或挂载目录同步 |
| 白名单设置 | 支持命令白名单 | 与设置中的"沙箱外运行"独立 |

> **常见问题解答**：为什么 Work 模式设置了"沙箱外运行"还是无法直接写入本地桌面？
>
> 因为 Work 模式的虚拟环境隔离与 Code 模式的沙箱是两套机制。Work 模式下 AI 看到的 `D:\` 是虚拟磁盘镜像，不是你真实的 D 盘。解决方法：
> 1. 通过右侧「任务产物」栏下载文件
> 2. 发起任务时选择本地已授权文件夹作为项目根目录
> 3. 明确告诉 AI："请把生成的文件保存在当前项目根目录下"

---

## 十二、安全红线与注意事项

1. ❌ **永远不要**将 `rm -rf`、`del /f /s /q` 等递归删除命令加入白名单
2. 💾 **随时 Git**：让 AI 操作前确保代码已提交，误删可通过 git 恢复
3. 📂 **Work 模式文件同步**：Work 模式是虚拟环境，文件需要通过「任务产物」或指定挂载目录获取
4. 🎯 **白名单精确匹配**：建议精确到子命令（如只加 `git status` 而不是 `git`）
5. 🌐 **网络配置仅 Windows**：macOS/Linux 暂不支持网络访问控制
6. 🔍 **导出后验证链接**：如果将此文档移动到其他目录，记得运行链接检查验证相对路径

---

## 十三、快速启用步骤

1. 点击左下角 **头像 > 设置**（IDE 模式点击右上角设置图标）
2. 左侧导航栏选择 **对话流**
3. 在「自动运行」部分，将命令运行方式设置为 **沙箱运行（支持白名单）**
4. （可选）在白名单列表中添加信任的命令前缀
5. （可选）点击「打开配置」编辑 `sandbox.json` 进行精细化配置

---

## 参考资源

- 官方文档：[IDE 沙箱配置](https://docs.trae.cn/ide/sandbox)
- 官方文档：[Work 沙箱说明](https://docs.trae.cn/solo/sandbox)
- 相关最佳实践：[cli-setup-in-agent-environment.md](cli-setup-in-agent-environment.md)（IDE Agent 环境下 CLI 工具配置）
- 社区案例：沙箱拦截 MATLAB 等专业软件的解决方案

<!-- changelog -->
- 2026-07-20 | docs | 初始版本：整理沙箱配置推荐、白名单策略、配置模板、网络控制、场景实践等完整指南
