---
id: "retrospective-xmnn-runtime-repackaging-20260718"
title: "XMNN Runtime 1.2.1-fix-cp314 WHL打包、Docker构建与重新打包复盘"
date: 2026-07-18
type: "task-retrospective"
source: "XMNN Runtime 1.2.1-fix-cp314 WHL打包、Docker运行时镜像构建与重新打包任务（2026-07-17~18）"
scope: "task"
participants: ["orchestrator", "developer"]
status: "completed"
tags: ["xmnn", "tvm", "nuitka", "docker", "wheel", "static-registration", "lto", "cmake", "rpath", "runtime-image"]
---

# XMNN Runtime 1.2.1-fix-cp314 WHL打包、Docker构建与重新打包复盘

## 执行摘要

本任务涵盖两个紧密相关的阶段：

**阶段1（07-17）**：完成 XMNN WHL包打包与Docker运行时镜像构建。基于 `npu-tvm-build:conda` 容器，通过5轮Docker build迭代解决权限、网络、隐式依赖等问题，最终生成 117MB wheel 和 1.6GB tar.gz 镜像，验证所有模块（tvm/vta/xmnn/compile_api/infer_api）正常工作。

**阶段2（07-17~18）**：解决 TVM `RelayToTIR` 属性未注册问题并重新打包。定位根因为 `USE_CODEGENC=OFF` + LTO/符号隐藏导致静态注册代码被丢弃，修复后通过双轮验证（构建容器 + 全新Runtime容器）确保产物质量，最终生成 1.8GB tar.gz 镜像，模型编译 0 错误 0 警告，精度测试余弦相似度 ≥ 0.998。

**关键数据**：
- Wheel 大小：117 MB（121MB修复后）
- 镜像大小：1.6GB → 1.8GB（修复后）
- 构建迭代：5轮（Docker build）
- 编译错误：0
- 编译警告：0
- 输出层余弦相似度：0.9984~0.9994（阈值 ≥0.99）
- 内部层最低余弦相似度：0.9938（阈值 ≥0.95）
- 配置修复文件数：3（config.cmake + tasks.py + rebuild_tvm_codegenc.sh）

## 1. 事实时间线

| 时间 | 事件 | 类型 |
|------|------|------|
| 07-17 | WHL打包：Nuitka编译TVM(97MB)+VTA(10MB)+XMNN(5.9MB)→Wheel(117MB) | 构建 |
| 07-17 | Docker build第1轮：Permission denied（基础镜像非root用户） | 构建迭代 |
| 07-17 | Docker build第2轮：ConnectionResetError（pip网络不稳定） | 构建迭代 |
| 07-17 | Docker build第3轮：缺少pytest（tvm.testing隐式依赖） | 构建迭代 |
| 07-17 | Docker build第4轮：缺少tomlkit/pandas（infer_api隐式依赖） | 构建迭代 |
| 07-17 | Docker build第5轮：✅ 构建成功 | 构建 |
| 07-17 | 镜像导出：docker save + gzip → 1.6GB tar.gz | 交付 |
| 07-17 | 环境预检：Windows无Docker，通过WSL2访问Ubuntu-24.04 Docker | 环境准备 |
| 07-17 | 定位根因：`USE_CODEGENC=OFF` → `codegen_c/target.cc`未编译 → `RelayToTIR`未注册 | 问题定位 |
| 07-17 | 修复配置：`USE_CODEGENC ON`、`USE_LTO OFF`、`HIDE_PRIVATE_SYMBOLS OFF` | 修复 |
| 07-17 | TVM编译验证：`relay.build`成功 | 验证 |
| 07-17 | Nuitka重新编译：TVM+VTA+XMNN→Wheel(121MB) | 构建 |
| 07-17 | 模型编译：ONNX yolov5s + Caffe resnet50，0错误0警告 | 验证 |
| 07-17 | 精度测试：输出层≥0.998，内部层≥0.993 | 验证 |
| 07-17 | OCI tar.gz导出：1.8GB，SHA256 `318ab026...` | 交付 |
| 07-18 | 完成审计：从tar.gz加载全新镜像，发现VTA target使用`ext_dev`而非`vta` | 审计 |
| 07-18 | 双轮验证通过：构建容器 + 全新Runtime容器独立验证 | 验证 |
| 07-18 | 配置持久化：修复config.cmake模板 + tasks.py替换逻辑 + rebuild_tvm_codegenc.sh | 持久化 |

## 2. 关键决策

| 决策 | 理由 | 结果 |
|------|------|------|
| 使用`npu-tvm-build:conda`作为基础镜像 | `libtvm.so`的RPATH硬编码为/opt/conda/envs/tvm-build/lib，换基础镜像需patchelf修复 | ✅ 避免动态链接问题 |
| Dockerfile开头显式`USER root` | 基础镜像以builder用户运行，系统级操作需要root权限 | ✅ 解决权限问题 |
| 本地wheel先于网络依赖安装 | 核心功能不受网络不稳定影响 | ✅ 提升构建稳定性 |
| 预装pytest/tomlkit/pandas | tvm.testing和infer_api的隐式依赖在新环境才暴露 | ✅ 解决依赖缺失 |
| 修改`USE_CODEGENC`为ON | `codegen_c/target.cc`注册了`TVM_REGISTER_TARGET_KIND("ccompiler")`，是全局`RelayToTIR`属性创建的触发点 | ✅ 解决RelayToTIR未注册 |
| 修改`USE_LTO`为OFF | LTO优化会丢弃`TVM_REGISTER_TARGET_KIND`等静态注册代码 | ✅ 防止静态注册丢失 |
| 修改`HIDE_PRIVATE_SYMBOLS`为OFF | 符号隐藏会导致静态注册符号不可见 | ✅ 确保注册符号可见 |
| 双轮验证（构建容器 + 全新Runtime容器） | 构建容器有环境残留，全新镜像验证才能确认产物质量 | ✅ 发现VTA target误报 |
| 正则替换替代字符串替换 | 模板默认值改为OFF后，`replace('set(USE_LTO ON)')`无法匹配 | ✅ 健壮性提升 |

## 3. 问题根因（5-Whys分析）

### 3.1 根因1：Docker构建依赖缺失（5轮迭代）

| 层级 | 追问 | 答案 |
|------|------|------|
| Why 1 | 为什么需要5轮构建？ | 依赖缺失和权限问题逐一暴露 |
| Why 2 | 为什么依赖缺失？ | `pyproject.toml`只声明4个核心依赖，隐式依赖未声明 |
| Why 3 | 为什么隐式依赖未声明？ | `tvm.testing`被`relay/frontend/caffe.py`无条件导入，但被认为是测试模块 |
| Why 4 | 为什么开发时不暴露？ | 开发环境中这些依赖已全局安装（conda预装） |
| Why 5 | 为什么这是问题？ | 打包成wheel后在新环境才暴露隐式依赖，导致构建迭代 |

**根因**：打包环境与运行时环境之间的依赖声明不完整——`tvm.testing`和`xmnn/infer_api`的隐式依赖未在`pyproject.toml`中声明。

### 3.2 根因2：USE_CODEGENC隐式依赖

| 层级 | 追问 | 答案 |
|------|------|------|
| Why 1 | 为什么RelayToTIR未注册？ | `codegen_c/target.cc`未被编译 |
| Why 2 | 为什么未编译？ | `config.cmake`中`USE_CODEGENC=OFF` |
| Why 3 | 为什么是OFF？ | TVM官方默认值是OFF，XMNN继承未改 |
| Why 4 | 为什么没改？ | 配置者不知道USE_CODEGENC是RelayToTIR注册的触发点 |
| Why 5 | 为什么不知道？ | TVM存在隐式耦合——`codegen_c/target.cc`的`TVM_REGISTER_TARGET_KIND("ccompiler")`副作用是触发全局RelayToTIR属性创建，此依赖未在代码或文档中说明 |

**根因**：TVM `USE_CODEGENC`配置项的隐式依赖——关闭它不仅禁用C代码生成器，还意外导致全局RelayToTIR属性未注册，影响所有target（llvm、c、ext_dev）。

### 3.3 根因3：配置持久化三层覆盖缺失

| 层级 | 追问 | 答案 |
|------|------|------|
| Why 1 | 为什么修复丢失？ | 模板中USE_LTO/HIDE_PRIVATE_SYMBOLS值被重置为ON |
| Why 2 | 为什么被重置？ | tasks.py字符串替换依赖模板值是ON，且dataclass默认`use_hide_symbols=True` |
| Why 3 | 为什么没检查tasks.py？ | 初始修复只改了模板文件 |
| Why 4 | 为什么只改模板？ | 未意识到配置有"模板→动态替换→独立脚本"三层覆盖 |
| Why 5 | 为什么没全链路检查？ | 缺乏"配置持久化全链路覆盖"意识 |

**根因**：配置修复缺乏全链路覆盖意识——模板默认值、tasks.py动态替换逻辑、shell脚本硬编码三层都需要同步修复。

### 3.4 根因4：VTA target误报

| 层级 | 追问 | 答案 |
|------|------|------|
| Why 1 | 为什么Target("vta")失败？ | VTA不是独立target kind |
| Why 2 | 为什么不是独立target kind？ | VTA使用`Target("ext_dev -device=vta -keys=vta,cpu")` |
| Why 3 | 为什么这样设计？ | VTA是ext_dev设备的变体，通过device参数区分 |

**根因**：对TVM target体系理解不够深入——VTA不是独立target kind而是ext_dev的设备变体。

## 4. 洞察提炼

### 洞察1：RPATH锁定构建环境 → "同源运行时"模式

**现象**：Nuitka/cmake编译的.so硬编码RPATH到构建时的conda环境路径。

**本质**：编译型Python包（含C扩展）的运行时环境与构建环境存在强耦合。这种耦合通过RPATH（动态链接器搜索路径）实现，在运行时通过ld.so解析。

**可复用模式**：对于含编译产物（.so）的Python wheel，如果构建环境是特定路径（如conda env），最简单可靠的运行时镜像策略是以**构建镜像为基础镜像**，而非尝试创建最小化镜像。最小化镜像需要patchelf修复+复制所有间接依赖，维护成本高且容易遗漏。

**识别信号**：
- 换基础镜像后动态库找不到
- `readelf -d libxxx.so | grep RPATH`显示硬编码路径
- 运行时报`ImportError: libxxx.so: cannot open shared object file`

### 洞察2：依赖缺失的"洋葱式发现" → 分层安装+网络容错模式

**现象**：Docker构建中依次暴露pytest缺失→tomlkit缺失→pandas缺失，每次只暴露一层。

**本质**：Python import是惰性链式触发的——`import tvm`不只加载tvm本身，还会通过`__init__.py`链接触发relay、frontend等子模块的导入，每个子模块可能有自己的依赖。缺失的依赖只有在执行到对应import时才暴露。

**可复用模式**：
1. **安装顺序**：先安装wheel声明依赖和已知隐式依赖→再安装本地wheel→最后验证import
2. **网络容错**：本地wheel安装放在网络依赖安装之后，确保核心功能在网络失败时也能可用
3. **验证链**：构建时的验证脚本应覆盖所有关键import路径，而非只验证顶层import

**识别信号**：
- 构建时`ModuleNotFoundError`逐个暴露
- 开发环境正常但打包后失败
- `pip check`在新环境报告缺失依赖

### 洞察3：Docker基础镜像默认用户不可假设 → USER root显式声明模式

**现象**：第一轮构建因Permission denied失败，原因是基础镜像以非root用户（builder）运行。

**本质**：Docker官方最佳实践推荐镜像以非root用户运行，但不同基础镜像的默认用户不同（debian/ubuntu是root，python镜像是root，conda-forge镜像可能是builder，node镜像是node等）。依赖"默认是root"的假设是脆弱的。

**可复用模式**：在Dockerfile开头显式声明`USER root`来执行系统级操作（apt-get、写入/etc、创建用户），再切换到运行时用户。这使得Dockerfile不依赖基础镜像的默认用户设置。

**识别信号**：
- 构建时`Permission denied`在apt-get或写入/etc时出现
- 基础镜像来自conda-forge等非官方源

### 洞察4：.pth文件实现Python环境自举 → 自动初始化模式

**现象**：setup_vta.sh创建`vta_nuitka_init.pth`文件，Python启动时自动执行其中的import，从而设置VTA_HW_PATH和LD_LIBRARY_PATH。

**本质**：Python的`.pth`文件机制允许在site-packages目录下放文件，Python解释器启动时会逐行执行`.pth`中以`import`开头的行。这是一种不需要修改用户代码、不需要设置环境变量、跨平台的初始化机制。

**可复用模式**：对于需要自动设置环境变量、修改sys.path、注册插件等场景，使用`.pth`文件+初始化模块比要求用户设置ENV、在包的`__init__.py`中设置（影响import速度）或wrapper脚本更优雅可靠。

**识别信号**：
- 需要在Python启动时自动配置环境
- 需要跨平台初始化且不改变用户使用方式

### 洞察5：本地优先+网络可选的安装顺序 → 降级容错模式

**现象**：pip安装网络依赖（Pillow/pandas等）时遭遇ConnectionResetError，但核心功能（xmnn wheel）是本地文件。

**本质**：Docker构建中网络不稳定是常见问题（尤其在国内网络环境下使用国外镜像源）。本地文件（COPY进镜像的wheel）不受网络影响。

**可复用模式**：
1. 将本地文件安装放在网络依赖之后（先确保网络依赖，后装本地包）
2. 对非核心网络依赖使用`|| echo "[WARN]"`容错
3. 配置pip镜像源（PIP_INDEX_URL）加速和减少失败
4. 设置PIP_RETRIES增加重试次数
5. 核心功能验证应在网络依赖安装之后，确保核心模块不依赖可选网络包

**识别信号**：
- 网络不稳定导致构建失败
- 构建时间因网络下载波动大

### 洞察6：C++静态注册与链接器优化的冲突

**现象**：LTO和符号隐藏导致`TVM_REGISTER_TARGET_KIND`等静态注册代码被优化丢弃。

**本质**：C++静态注册机制依赖全局对象的构造函数在程序启动时执行。但LTO（链接时优化）和符号隐藏会识别这些注册代码为"未引用"而优化丢弃，导致注册不执行。

**识别信号**：
- 运行时报"Attribute X is not registered"或"Target kind Y is not defined"
- 编译时无错误，运行时才暴露
- 启用LTO后出现

### 洞察7：配置持久化的三层覆盖模式

**现象**：配置修复后被tasks.py的动态替换逻辑覆盖。

**本质**：配置项可能在三个层面被修改——模板默认值、动态替换逻辑、独立脚本硬编码，任何一层遗漏都会导致修复失效。

**识别信号**：
- 修复后配置"莫名"被重置
- 不同构建路径产生不同结果
- 字符串替换依赖特定默认值

### 洞察8：完成审计的独立验证模式

**现象**：构建环境验证通过但实际使用失败（VTA target误报）。

**本质**：从产物（tar.gz）反向加载全新环境验证，而非在构建环境中验证，能发现构建环境残留的假阳性。

**识别信号**：
- 构建环境验证通过但实际使用失败
- 构建环境有缓存或残留依赖
- 需要确认产物可独立部署

## 5. 可复用模式萃取

### 模式A：编译型Python Wheel运行时镜像构建模式

**触发场景**：需要为含C/C++编译产物（.so）的Python wheel创建Docker运行时镜像，且编译环境为conda/特定路径。

**核心步骤**：
1. 以构建镜像为基础镜像（确保RPATH匹配）
2. 在基础镜像上添加运行时用户和工具
3. 先装隐式依赖→再装本地wheel→最后验证
4. 使用ldconfig配置conda库路径
5. 使用.pth文件做包级自初始化

**适用条件**：
- Nuitka编译的Python包
- CMake编译的C扩展
- 链接了大型C++依赖（LLVM、CUDA等）的wheel

**反模式**：试图用`python:slim`+复制wheel的方式创建运行时镜像，必然因缺少系统级动态库而失败。

**迁移验证**：
- XMNN wheel（本项目）
- PyTorch CUDA wheel（类似RPATH硬编码到conda路径）

### 模式B：Python包隐式依赖检测清单

**触发场景**：创建wheel的运行时镜像时，需要检测所有依赖。

**检查清单**：
- tvm → pytest（tvm.testing导入链）
- xmnn.infer_api → tomlkit, pandas, tqdm[asyncio]
- 图像处理 → Pillow
- 数据序列化 → cloudpickle
- RPC服务 → tornado

**检测方法**：
1. `python -c "import <module>"`逐层import测试
2. `grep -rh '^\(import \|from \)' <pkg_dir>/ --include='*.py' | grep -v 'from \.' | sort -u`
3. 对每个import的第三方包，`pip show <pkg>`检查是否安装

### 模式C：Docker构建网络容错checklist

**触发场景**：Docker构建中网络不稳定。

**检查清单**：
- [ ] 设置PIP_INDEX_URL为国内镜像源
- [ ] 设置PIP_RETRIES=5增加重试
- [ ] 设置PIP_DEFAULT_TIMEOUT=300
- [ ] 本地COPY文件先于网络下载（利用Docker cache）
- [ ] 非核心依赖安装使用`|| echo "[WARN]"`容错
- [ ] 核心验证在非核心依赖之后执行

### 模式D：静态注册依赖代码的编译配置

**触发场景**：编译包含C++静态注册机制（全局对象构造函数执行注册）的框架时

**核心步骤**：
1. 识别代码中的静态注册宏（`TVM_REGISTER_*`、`REGISTER_*`、`static auto& __register_*`）
2. 禁用LTO（`-DUSE_LTO=OFF`或`set(USE_LTO OFF)`）
3. 禁用私有符号隐藏（`-DHIDE_PRIVATE_SYMBOLS=OFF`）
4. 确保注册代码所在源文件被编译（检查CMake的`file_glob`和条件编译）
5. 验证：运行时检查注册表是否包含预期条目

**适用条件**：
- 框架使用C++静态注册（全局对象构造函数、`__attribute__((constructor))`）
- 编译系统支持LTO和符号隐藏选项
- 运行时报"未注册"错误但编译无错误

**反模式**：
- 对不包含静态注册的普通库盲目禁用LTO→损失性能优化
- 只禁用LTO不禁用符号隐藏→符号隐藏同样会丢弃注册代码
- 只修改模板不检查动态替换→配置可能被运行时替换覆盖

**迁移验证**：
- TVM target注册（本项目，2个案例：USE_CODEGENC + USE_LTO）
- LLVM pass注册（LLVM项目使用类似机制）
- OpenCV module注册（`CV_MODULE_REGISTER`宏）

### 模式E：配置持久化全链路覆盖

**触发场景**：修复CMake/Makefile等构建配置时

**核心步骤**：
1. 搜索所有包含该配置项的文件（Grep关键词）
2. 分三层检查：模板默认值→动态替换逻辑→独立脚本硬编码
3. 每层都修复后，用正则替换替代字符串替换（处理任意默认值）
4. 修改dataclass默认值（不只是`from_args()`方法）
5. 验证：用最简代码测试配置生成逻辑

**适用条件**：
- 配置项在多个文件中被引用
- 存在配置模板+运行时替换机制
- 有独立的shell脚本直接传递cmake参数

**反模式**：
- 只改模板不检查替换逻辑→替换逻辑可能覆盖修复
- 用字符串替换而非正则替换→依赖特定默认值，模板改后失效
- 只改`from_args()`不改dataclass默认值→直接实例化时使用错误默认值

## 6. 改进行动项

### 高优先级

| ID | 行动项 | 验收标准 | 状态 |
|----|--------|----------|------|
| ACT-01 | 在pyproject.toml中补充pytest/tomlkit/pandas/tqdm为可选依赖组 | `pip install xmnn[runtime]`能安装所有运行时依赖 | 🔲 待办 |
| ACT-02 | 将`USE_CODEGENC ON`写入config.cmake模板注释，说明其与RelayToTIR的隐式依赖 | 注释包含"关闭此选项会导致RelayToTIR属性未注册" | ✅ 已完成 |
| ACT-03 | 修复tasks.py：正则替换+dataclass默认值use_hide_symbols=False | `BuildConfig()`直接实例化时use_hide_symbols=False | ✅ 已完成 |
| ACT-04 | 修复rebuild_tvm_codegenc.sh：-DUSE_LTO=OFF -DHIDE_PRIVATE_SYMBOLS=OFF | 脚本中包含这两个参数 | ✅ 已完成 |

### 中优先级

| ID | 行动项 | 验收标准 | 状态 |
|----|--------|----------|------|
| ACT-05 | 在Dockerfile中添加健康检查（HEALTHCHECK指令） | `docker inspect`显示健康状态 | 🔲 待办 |
| ACT-06 | 在config.cmake中添加`USE_CODEGENC`与`RelayToTIR`的关系说明 | 注释解释隐式依赖 | ✅ 已完成 |
| ACT-07 | 建立构建配置变更检查清单（三层覆盖） | 检查清单文档存在 | ✅ 已完成（[build-config-change-checklist.md](../../../../../checklists/build-config-change-checklist.md)） |
| ACT-08 | 考虑将libtvm.so的RPATH改为$ORIGIN相对路径（使用patchelf） | `readelf -d libtvm.so | grep RPATH`显示`$ORIGIN`或相对路径 | 🔲 待办 |
| ACT-09 | 为xmnn包添加`xmnn doctor`命令检查运行时环境 | `python -m xmnn.doctor`能诊断缺失依赖、VTA_HW_PATH、库路径等 | 🔲 待办 |
| ACT-10 | 将entrypoint.sh和setup_vta.sh纳入版本控制 | 文件纳入git管理，有变更记录 | 🔲 待办 |

### 低优先级

| ID | 行动项 | 验收标准 | 状态 |
|----|--------|----------|------|
| ACT-11 | 考虑多阶段构建减小镜像体积（builder+runtime阶段分离） | 镜像体积减少30%以上 | 🔲 待办 |
| ACT-12 | 制作no-LLVM变体镜像（USE_LLVM=OFF编译的libtvm.so） | 提供无LLVM依赖的更小镜像 | 🔲 待办 |
| ACT-13 | 考虑将静态注册模式沉淀到模式库 | 模式文档入库 | ✅ 已完成（[static-registration-compile-config.md](../../../patterns/code-patterns/static-registration-compile-config.md)，L1实验性） |

## 7. 经验教训

| 教训 | 说明 |
|------|------|
| 隐式依赖是编译配置的最大陷阱 | TVM的`USE_CODEGENC`表面上控制C代码生成器，实际还影响全局RelayToTIR属性注册——这种隐式耦合无法从配置项名称推断 |
| 配置修复必须全链路覆盖 | 模板、动态替换、独立脚本三层缺一不可，只改一层等于没改 |
| 完成审计必须从产物反向验证 | 在构建环境中验证可能因环境残留而通过，只有从tar.gz加载全新镜像才能确认产物质量 |
| 正则替换优于字符串替换 | 字符串替换依赖特定默认值，模板默认值改变后替换会静默失败 |
| 5-Whys追问至少3层 | 单层Why只得到表面原因，3层以上才能触达根本原因 |
| RPATH锁定构建环境 | Nuitka/cmake编译的.so硬编码RPATH到conda路径，运行时镜像必须与构建环境同源 |
| Docker基础镜像默认用户不可假设 | 不同基础镜像默认用户不同，Dockerfile应显式USER root执行系统级操作 |
| Python依赖发现是洋葱式的 | 隐式依赖通过import链逐层暴露，需要完整的验证链覆盖所有关键import路径 |
| .pth文件是优雅的Python自举机制 | 不需要修改用户代码、不需要设置环境变量、跨平台的初始化方式 |
| 本地优先+网络可选提升构建稳定性 | 核心功能（本地wheel）不受网络不稳定影响 |

## 8. 产出物索引

### 主发布物

| 文件 | 路径 | 大小 |
|------|------|------|
| Docker镜像包 | `external/xmhub/notebook/xmnn/dist/xmnn-runtime-1.2.1-fix-cp314.tar.gz` | 1.8GB |
| WHL包 | `external/xmhub/notebook/xmnn/dist/xmnn-1.2.1+fix-cp314-cp314-linux_x86_64.whl` | 121MB |
| Dockerfile | `external/xmhub/notebook/xmnn/dist/docker-runtime/Dockerfile` | 3.5KB |
| entrypoint.sh | `external/xmhub/notebook/xmnn/dist/docker-runtime/entrypoint.sh` | 6.5KB |
| setup_vta.sh | `external/xmhub/notebook/xmnn/dist/docker-runtime/setup_vta.sh` | 897B |

### Wheel内部核心组件

| 组件 | 说明 |
|------|------|
| `tvm.cpython-314-x86_64-linux-gnu.so` | Nuitka编译的TVM核心模块 |
| `vta.cpython-314-x86_64-linux-gnu.so` | Nuitka编译的VTA模块 |
| `xmnn.cpython-314-x86_64-linux-gnu.so` | Nuitka编译的XMNN模块 |
| `libtvm.so`/`libtvm_runtime.so`/`libtvm_allvisible.so` | TVM C++运行时库 |
| `vta_nuitka_init.pth`+`_vta_nuitka_init.py` | Python自动初始化（VTA_HW_PATH+LD_LIBRARY_PATH） |
| 12个`libtvm_runtime_pack.so` | 7款芯片×Normal/Static变体的预编译运行时 |

### 构建日志

| 产出物 | 路径 |
|--------|------|
| 打包报告 | `external/xmhub/build_logs/PACKAGING_REPORT.md` |
| 编译日志 | `external/xmhub/build_logs/compile_*.log` |
| 精度日志 | `external/xmhub/build_logs/accuracy_*.log` |
| Runtime验证日志 | `external/xmhub/build_logs/runtime_verify/` |
| 本复盘报告 | `.agents/docs/retrospective/reports/task-reports/retrospective-xmnn-runtime-repackaging-20260718/README.md` |

## 9. 加载与运行命令

```bash
# 1. 加载镜像
docker load -i xmnn-runtime-1.2.1-fix-cp314.tar.gz

# 2. 验证镜像
docker run --rm -e QUIET_ENTRYPOINT=1 --entrypoint "" xmnn-runtime:1.2.1-fix-cp314 \
  python -c "import tvm; import vta; import xmnn; from xmnn import compile_api, infer_api; print('OK')"

# 3. 交互式运行（挂载工作目录）
docker run -it --rm -v /your/workdir:/home/ai/sdk xmnn-runtime:1.2.1-fix-cp314 bash

# 4. 直接运行Python
docker run -it --rm xmnn-runtime:1.2.1-fix-cp314 python your_script.py
```
