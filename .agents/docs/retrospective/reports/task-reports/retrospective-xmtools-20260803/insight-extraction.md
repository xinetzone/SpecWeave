# XMNN 复盘模式萃取（insight-extraction）

> 质量门 G3：每条模式包含 触发场景/核心步骤/反模式/检验/迁移验证。

---

## 模式 P-01：原生库 + 数据目录的"CMake 安装"分离策略

### 触发场景
使用 Nuitka `--module` 编译 Python 包时，需要同时交付可被外部进程访问的可执行文件与动态库（如工具链 bin/、SOP 库 autolibs/）。

### 核心步骤
1. **Nuitka 仅编译 Python 代码**：`nuitka --module --include-package=<pkg>`，不传入 `--include-data-dir`。
2. **数据目录由 CMake 安装**：`install(DIRECTORY "<src>/" DESTINATION "<pkg>/<dname>" USE_SOURCE_PERMISSIONS)`。
3. **.so 安装到 site-packages 根目录**：利用 Nuitka 自动设置的 `__path__` 指向同名子目录。
4. **权限双重保障**：`USE_SOURCE_PERMISSIONS` + 显式 `chmod +x`。
5. **验证清单覆盖**：在镜像构建/验证脚本中检查数据目录存在性与可执行权限。

### 反模式
- 用 `--include-data-dir` 将含可执行文件/动态库的数据嵌入 `.so` → 外部进程无法通过文件系统路径访问。
- 将数据装到 wheel 非标准 `.data/` 子目录 → pip 报 `Unknown scheme key`。

### 检验方法
```bash
# 容器内验证
python -c "import xmnn,os; d=xmnn.__path__[0]; assert all(os.path.isdir(f'{d}/{n}') for n in ['autolibs','tools_cpp','fonts'])"
# 可执行权限
find <site-packages>/xmnn/tools_cpp/bin -type f -exec test -x {} \; -print | head
```

### 迁移验证
本模式已在本项目 BUILD_REPORT.md 的 RC1/RC2/RC3 修复中验证通过（ResNet-18 精度 > 0.996）。同类场景（任何"Python 包交付原生工具链"）均可复用。

---

## 模式 P-02：wheel 自包含原生运行时的"依赖解析 + $ORIGIN RPATH"方案

### 触发场景
将 Python 包 + 原生库（libtvm.so + libLLVM + 系统依赖）打包为自包含 wheel，需在目标环境无需预装依赖即可运行。

### 核心步骤
1. **依赖收集**：构建时从 Conda 环境解析真实 NEEDED 依赖（`install_real_lib` 解析 REALPATH）。
2. **集中存放**：所有原生库放入统一 `_libs/` 目录。
3. **RPATH 固化**：`patchelf --set-rpath '$ORIGIN'` 使库间相对引用无需系统路径。
4. **bootstrap 预加载**：`.pth`/`__init__` 预置 `TVM_LIBRARY_PATH` 并 `ctypes.CDLL(libtvm, RTLD_GLOBAL)`。
5. **运行时链接器兜底**：生产镜像将 `_libs` 注册到 ld.so.conf（可选，平滑兼容）。

### 反模式
- 依赖系统 `LD_LIBRARY_PATH` 全局设置 → 与其他包冲突，环境不可控。
- 复制符号链接而非真实文件 → 目标环境缺失链接目标导致加载失败。
- 忽略 RPATH → 库间依赖在非安装目录无法解析。

### 检验方法
- `auditwheel show` 检查依赖归属。
- 干净 venv 中 `pip install --no-deps` 后 `ctypes.CDLL(libtvm)` 成功。
- `lddtree` 确认所有依赖均由 `_libs` 内相对路径解析。

### 迁移验证
本项目 wheel 在干净 venv 与 runtime 镜像中均通过 libtvm 动态加载与 tvm.build 计算验证。

---

## 模式 P-03：三层镜像体系的"构建/运行时/服务"分层交付

### 触发场景
需要同时支持开发者本地构建、用户开箱即用、服务化 API 三种交付形态。

### 核心步骤
1. **dev 镜像**：完整工具链（Conda + LLVM + CMake + Nuitka），用于构建 wheel。
2. **runtime 镜像**：仅运行时依赖，预装 wheel，开箱即用。
3. **serve 镜像**：基于 runtime 叠加 Web 服务（Flask），暴露 REST API。
4. **空 ENTRYPOINT + 明确 CMD**：允许用户覆盖命令（交互 shell / 自定义脚本）。
5. **时区三层保障**：`tzdata` + `/etc/localtime` 软链 + `ENV TZ`。

### 反模式
- 单一大镜像同时承担构建与运行 → 镜像膨胀、攻击面大。
- 未设空 ENTRYPOINT → 无法覆盖基础镜像默认入口（如 `python`）。
- 时区仅设 `ENV TZ` → 容器内 `/etc/localtime` 仍为 UTC。

### 检验方法
- `docker run --rm --entrypoint bash <image>` 可进入。
- 容器内 `date` 显示 `Asia/Shanghai`（+0800）。
- dev 镜像可构建 wheel，runtime 镜像可直接 import。

### 迁移验证
本项目三层镜像已贯通（dev 2.07GB / runtime 1.35GB / serve 1.16GB 内容），README 提供完整命令链。

---

## 模式 P-04：Python 3.14 的 AST 兼容层（Monkey-patch）

### 触发场景
旧代码库引用了 Python 3.14 已移除/改版的 AST 节点（`NameConstant`/`Num`/`Str`/`Index`/`ExtSlice`），需在导入前注入兼容定义。

### 核心步骤
1. 在 `__init__.py` 顶部注入 `ast` 兼容补丁。
2. 用 `hasattr` 守卫，仅对缺失节点补定义。
3. 通过 bootstrap 注入机制（`_inject_preamble`）统一注入，避免污染源码。
4. 构建后恢复原始 `__init__.py`（备份式注入）。

### 反模式
- 直接修改源码文件 → 污染版本库，构建后未恢复。
- 无 `hasattr` 守卫 → 版本升级后重复定义冲突。

### 检验方法
- 在 Python 3.14 下 `import tvm` 无 AST 相关报错。
- `git diff` 确认源码 `__init__.py` 未被持久修改。

### 迁移验证
本项目在 Python 3.14 下通过 AST 补丁成功导入 tvm/vta/xmnn。

---

## 反模式库（从 V 对抗审查沉淀）

| 反模式 | 识别特征 | 规避 |
|---|---|---|
| 构建声明与执行脚本双轨 | pyproject 声明 vs 脚本 sed 覆盖 | 统一单一构建策略 |
| 全局动态库路径污染 | 顶层 `_libs` + ld.so.conf 全局注册 | 包内收敛 + $ORIGIN RPATH |
| 可选依赖被强制预装 | torch/opencv 进入核心镜像 | 严格按 `[project.optional-dependencies]` 分流 |
| 死代码/注释块残留 | 大段注释掉的安装逻辑 | 定期清理，配合 CI 检查 |
| 版本号含 dev 后缀对外发布 | `1.2.1-dev0` | 正式版用规范 semver |