# npuusertools 打包环境 (vta-dev) - 验证清单

## 目录结构与文件存在性
- [x] C1: `external/dao/runtime/vta-dev/` 目录已创建
- [x] C2: `external/dao/runtime/vta-dev/AGENTS.md` 存在且包含"启动协议"关键词
- [x] C3: `external/dao/runtime/vta-dev/Dockerfile` 存在且第一行为 `# syntax=docker/dockerfile:1.7-labs`
- [x] C4: `external/dao/runtime/vta-dev/tasks/` namespace包存在（__init__.py, docker.py, package.py, clean.py），原tasks.py已删除
- [x] C5: `external/dao/runtime/vta-dev/build.sh` 存在且有#!/bin/bash shebang
- [x] C6: `external/dao/runtime/vta-dev/scripts/verify-wheel.sh` 存在且有#!/bin/bash shebang
- [x] C7: `external/dao/runtime/vta-dev/scripts/build-wheel.sh` 存在且有#!/bin/bash shebang
- [x] C8: `external/dao/runtime/vta-dev/pyproject.toml` 存在（scikit-build-core配置）
- [x] C9: `external/dao/runtime/vta-dev/CMakeLists.txt` 存在（LANGUAGES NONE，Nuitka产物安装规则）
- [x] C10: `external/dao/runtime/vta-dev/README.md` 存在（中文文档）
- [x] C11: `external/dao/runtime/vta-dev/docker-compose.yml` 存在（有效YAML）
- [x] C12: `external/dao/runtime/vta-dev/.gitignore` 存在且排除 dist/、logs/、workspace/、__pycache__/、*.pyc、*.pyo、.env
- [x] C13: `external/dao/runtime/vta-dev/scripts/`、`configs/`（含.gitkeep）、`tasks/` 子目录存在

## Nuitka构建系统验证（pyproject.toml + CMakeLists.txt + build-wheel.sh）
- [x] C14: pyproject.toml使用scikit-build-core作为build-backend
- [x] C15: pyproject.toml包名为xmnn，版本为1.2.1-dev
- [x] C16: pyproject.toml依赖列表包含numpy/scipy/pandas/matplotlib/Pillow/onnx/protobuf/openpyxl/tabulate/rich/tqdm/cloudpickle等
- [x] C17: CMakeLists.txt使用LANGUAGES NONE（不编译C++代码）
- [x] C18: CMakeLists.txt安装Nuitka编译产物xmnn.cpython-*.so到wheel根目录（DESTINATION "."）
- [x] C19: CMakeLists.txt安装数据目录tools_cpp/、fonts/、autolibs/到xmnn/子目录
- [x] C20: CMakeLists.txt使用patchelf设置tools_cpp/libs/**/*.so的RPATH=$ORIGIN
- [x] C21: CMakeLists.txt对tools_cpp/bin/*设置chmod +x
- [x] C22: build-wheel.sh设置CC=clang、CXX=clang++、LLVM_CONFIG指向main env（Python 3.14t）
- [x] C23: build-wheel.sh包含AST PREAMBLE注入和恢复函数（Python 3.14兼容）
- [x] C24: build-wheel.sh包含Nuitka编译命令（--module --include-package=xmnn --enable-plugin=dill-compat --nofollow-import-to=tvm,vta）
- [x] C25: build-wheel.sh使用`python -m build --wheel --no-isolation`打包，通过cmake.define传递路径参数
- [x] C26: build-wheel.sh编译后恢复npuusertools的__init__.py（AST PREAMBLE临时注入后清理）
- [x] C26.1: build-wheel.sh使用main env PATH（/opt/conda/envs/main/bin优先），确保Python 3.14t
- [x] C26.2: Nuitka从bind mount复制到/tmp/nuitka-src安装（解决RO挂载pip install问题）

## Dockerfile验证
- [x] C27: Dockerfile包含两阶段构建（两个FROM指令：builder和final）
- [x] C28: Builder阶段基础镜像为 `devcontainer-base:onnx-quantized-latest`（通过ARG可配置）
- [x] C29: Builder阶段安装了Nuitka（从本地patched源码）、patchelf、scikit-build-core、build、invoke、cloudpickle、numpy、scipy等
- [x] C30: Builder阶段设置CC/CXX/LLVM_CONFIG指向main env（/opt/conda/envs/main/bin/）
- [x] C31: Builder阶段使用 `--mount=type=bind` 挂载npuusertools源码到/source/npuusertools（rw，AST PREAMBLE需要）
- [x] C32: Builder阶段使用 `--mount=type=bind` 挂载Nuitka patched源码到/source/nuitka（ro），cp -a到/tmp安装
- [x] C33: Builder阶段使用 `--mount=type=cache` 缓存pip下载（/root/.cache/pip）
- [x] C34: Builder阶段COPY路径以external/dao/runtime/vta-dev/开头（build context为SpecWeave根目录）
- [x] C35: Builder阶段wheel输出到/opt/vta-dist/
- [x] C36: Final阶段从builder复制wheel并pip install（自动解析依赖）
- [x] C37: Final阶段配置pip aliyun mirror（PIP_INDEX_URL/PIP_TRUSTED_HOST）
- [x] C38: Final阶段COPY verify-wheel.sh到/usr/local/bin/并RUN verify-wheel.sh作为质量门禁
- [x] C39: Final阶段保留wheel副本到/opt/vta-dist/（COPY --from=builder）
- [x] C40: Final阶段ENV设置PYTHON_GIL=0和main env PATH
- [x] C41: Final阶段pip install使用os._exit(0)绕过Nuitka shutdown segfault
- [x] C42: 源码不通过COPY指令进入final镜像层（仅通过bind mount在构建时访问）

## verify-wheel.sh验证（13项检查）
- [x] C43: 脚本设置PATH=/opt/conda/envs/main/bin优先
- [x] C44: 检查1：Python版本>=3.14且为cp314t free-threading build
- [x] C45: 检查2：GIL disabled验证（sys._is_gil_enabled() is False）
- [x] C46: 检查3：import xmnn + Nuitka编译验证（nuitka_module_loader、虚拟__file__路径、.so存在、数据目录）
- [x] C47: 检查4：非TVM核心API模块import（infer/performance/bandwidth/excel_report OK，compile/accuracy SKIP per NG5）
- [x] C48: 检查5a：核心依赖import（numpy, scipy, cloudpickle）
- [x] C49: 检查5b：可选依赖import（pandas, matplotlib, onnx, protobuf, Pillow, openpyxl, tabulate, rich, tqdm, typer等；click由typer 0.27+内置，不单独检查）
- [x] C50: 检查5c：7个CLI工具--help验证（xmflow + 6个xmnn-*命令，全部PASS，无segfault）
- [x] C51: 检查6：xmnn版本检查（WARN-only，dev版本无__version__可接受）
- [x] C52: 检查7：数据目录存在（tools_cpp/, fonts/必须，autolibs/可选）
- [x] C53: 检查8：Nuitka .so存在于site-packages根目录（xmnn.cpython-*.so，5.2MB）
- [x] C54: 检查9：预编译.so库ldd检查（无not found依赖）
- [x] C55: 检查10：RPATH=$ORIGIN（patchelf设置验证，16个.so全部通过）
- [x] C56: 检查11：Nuitka编译子模块加载验证（12个子模块全部nuitka_module_loader）
- [x] C57: 检查12：wheel文件存在且大小>0（34MB）
- [x] C58: 所有import xmnn的测试均以os._exit(0)结束，绕过Nuitka 4.3rc1+Python 3.14t shutdown segfault
- [x] C59: 脚本使用check/check_warn函数封装测试，set -e安全，输出PASS/FAIL/WARN/SKIP格式
- [x] C60: 脚本输出SUMMARY统计，有FAIL时os._exit(1)，全部通过时os._exit(0)

## Nuitka源码补丁（Python 3.14 free-threading兼容）
- [x] C70: allocator.h:615 — op->ob_gc_bits → object->ob_gc_bits 修复
- [x] C71: allocator.h:200-210 — 添加Py_GIL_DISABLED分支的_Py_IMMORTAL_REFCNT定义
- [x] C72: python_internals_access.h:11 — 移除&& !defined(Py_GIL_DISABLED) guard
- [x] C73: python_internals_access.h.j2:11 — Jinja2模板同步修复
- [x] C74: CompiledFrameType.c:862-863 — _PyStackRef_FromPyObjectNew → PyStackRef_FromPyObjectNew
- [x] C75: HelpersAllocator.c:762-794 — 添加Py_GIL_DISABLED GC分支（bit-based tracking）
- [x] C76: HelpersAllocator.c:989-992 — _PyRuntime.stoptheworld → _PyInterpreterState_GET()->stoptheworld

## invoke tasks/ namespace包验证
- [x] C80: tasks/__init__.py、docker.py、package.py、clean.py均存在且ast.parse语法正确
- [x] C81: `invoke --list` 列出namespace任务：config, all（default）, docker.toolchain, docker.build, package.extract, package.verify, clean.clean
- [x] C82: docker.toolchain检查容器运行时版本（Podman>=4.0或Docker>=23.0）、BuildKit、源码路径、Dockerfile、基础镜像、磁盘空间
- [x] C83: docker.build支持--no-cache和--debug参数，使用DOCKER_BIN变量，cwd=cfg.root_dir，-f用绝对路径；Podman版本检测修复
- [x] C84: package.extract通过container create + cp提取wheel到dist/（修复/.路径复制问题，直接复制目录内容而非目录本身）
- [x] C85: package.verify运行容器内verify-wheel.sh
- [x] C86: clean.clean清理dist/和logs/，支持--images清理dangling镜像
- [x] C87: all任务（default=True）按序执行docker.toolchain → docker.build → package.verify → package.extract
- [x] C88: _get_project_root()通过`.agents/`+`external/chaos/npuusertools/`双marker查找SpecWeave根目录
- [x] C89: _get_container_bin()支持DOCKER_BIN环境变量（默认docker，可设为podman）
- [x] C90: _is_podman()检测运行时类型，版本检查和BuildKit检测适配Podman
- [x] C91: BuildConfig dataclass包含root_dir/dockerfile_path/source_path/image_name/tag/base_image/dist_dir/logs_dir
- [x] C92: Collection组装正确（ns.add_collection for docker/package/clean）
- [x] C93: 任务失败时返回非零退出码（Exit(code=1)）

## build.sh验证
- [x] C94: 脚本有#!/bin/bash shebang和set -euo pipefail
- [x] C95: 使用$DOCKER_BIN变量（不硬编码docker），支持DOCKER_BIN=podman
- [x] C96: 自动定位SpecWeave根目录（find_specweave_root双marker函数）
- [x] C97: 支持--verify-only(-V)/--no-cache(-F)/--debug(-d)/--extract(-e)/--verbose(-v)/-h/--help选项
- [x] C98: 构建context使用$SPECWEAVE_ROOT绝对路径，-f使用绝对DOCKERFILE路径
- [x] C99: 检查容器运行时可用性，Podman时给出不同的错误提示
- [x] C100: 关键路径检查（pyproject.toml, CMakeLists.txt, build-wheel.sh, verify-wheel.sh, npuusertools目录）
- [x] C101: 基础镜像检查（不存在时给出构建指引）
- [x] C102: 日志tee到logs/build-<timestamp>.log
- [x] C103: 构建后验证（verify_image函数）
- [x] C104: 提取wheel（docker create + docker cp）
- [x] C105: 错误信息清晰可操作，中文输出

## 文档验证
- [x] C106: AGENTS.md包含核心红线（不修改npuusertools子模块）
- [x] C107: AGENTS.md包含按需阅读路由表
- [x] C108: AGENTS.md包含三步快速开始
- [x] C109: README.md包含环境要求（Docker/Podman、BuildKit、磁盘空间、invoke安装）
- [x] C110: README.md包含快速开始（3条命令以内）
- [x] C111: README.md包含目录结构说明
- [x] C112: README.md包含Nuitka编译说明和常见问题排查（含Podman）
- [x] C113: 文档语言为中文（与用户输入一致）

## docker-compose.yml验证
- [x] C114: 为有效YAML格式
- [x] C115: build.context为../../..（相对于vta-dev/指向SpecWeave根目录）
- [x] C116: build.dockerfile为external/dao/runtime/vta-dev/Dockerfile
- [x] C117: 挂载./workspace到/workspace
- [x] C118: stdin_open: true, tty: true, command: /bin/bash

## CLI启动器与console_scripts验证
- [x] C119: src/xmnn_cli_launchers.py存在，提供xmflow()和6个*_cmd()薄封装函数
- [x] C120: 启动器使用os._exit(code)绕过Nuitka+py314t Py_Finalize()段错误
- [x] C121: pyproject.toml包含[project.scripts]，定义7个入口点（xmflow + xmnn-compile/infer/accuracy/performance/bandwidth/excelreport）
- [x] C122: CMakeLists.txt安装xmnn_cli_launchers.py到DESTINATION "."（site-packages根目录）
- [x] C123: Dockerfile builder阶段安装typer/rich/shellingham/tomli CLI依赖，COPY src/目录
- [x] C124: 7个CLI工具--help在容器内均可正常运行（xmflow + 6个xmnn-*命令），无segfault（exit code != 139）

## 架构一致性验证
- [x] C125: 整体架构模式与xmnn-whl-builder一致（两阶段、bind mount、verify脚本、/opt/*-dist/输出、独立pyproject.toml+CMakeLists.txt打包Nuitka产物）
- [x] C126: invoke任务namespace组织与pyinvoke namespace-organization.md参考一致
- [x] C127: 没有修改npuusertools子模块的任何文件（NG1约束）——构建过程中AST PREAMBLE注入后会恢复，xmnn/__init__.py验证干净
- [x] C128: 不包含TVM/VTA的Nuitka编译（NG5约束——仅编译xmnn包，--nofollow-import-to=tvm,vta）
- [x] C129: 容器运行时兼容docker和WSL下的podman（通过DOCKER_BIN环境变量，Podman版本检测和BuildKit检测已适配）

## 端到端构建验证（已验证）
- [x] C130: devcontainer-base:onnx-quantized-latest镜像本地可用（localhost/，3.56GB）
- [x] C131: Podman build构建成功，exit code为0
- [x] C132: podman images显示localhost/vta-dev:latest
- [x] C133: verify-wheel.sh 13项检查全部PASS（1 WARN：version未找到，dev版本正常；0 FAIL）
- [x] C134: xmnn.__loader__为nuitka_module_loader（Nuitka编译验证，Nuitka package mode下__file__为虚拟路径）
- [x] C135: wheel文件大小34MB（xmnn-1.2.1.dev0-cp314-cp314t-linux_x86_64.whl）
- [x] C136: Nuitka .so大小5.2MB（xmnn.cpython-314t-x86_64-linux-gnu.so）
- [x] C137: 容器内GIL状态为disabled（PYTHON_GIL=0, sys._is_gil_enabled()=False）
- [x] C138: 容器内ldd检查预编译.so无"not found"依赖（16个.so全部OK）
- [x] C139: RPATH=$ORIGIN设置成功（16个.so全部有$ORIGIN）
- [x] C140: 12个xmnn子模块全部通过nuitka_module_loader加载（无.py文件回退）
- [x] C141: DOCKER_BIN=podman环境下构建验证通过（WSL Podman 5.7.0）
- [x] C142: Python 3.14t (cp314t free-threading) 确认使用（用户要求"我就要使用py314t"，非Python 3.13回退）
- [x] C143: `inv --list` 在WSL中正确列出7个任务（config/all/docker.toolchain/docker.build/package.extract/package.verify/clean.clean）
- [x] C144: `inv docker.toolchain` 在DOCKER_BIN=podman下全部检查通过（Podman 5.7.0、基础镜像存在、路径正确、磁盘充足）
- [x] C145: `inv package.extract` 正确提取wheel到dist/（修复cp路径后wheel直接在dist/下，34.5MB）
- [x] C146: `inv clean.clean` 正确清理dist/目录
- [x] C147: `inv package.verify` 容器内验证通过（13 passed, 0 failed, 1 warning）
- [x] C148: npuusertools子模块git status验证：xmnn/__init__.py无变更（AST PREAMBLE已恢复）
- [x] C149: Nuitka源码6处Python 3.14t free-threading补丁全部验证通过（65个C文件编译成功，.so产出5.2MB）
- [x] C150: shutdown segfault workaround（os._exit(0)）在所有xmnn导入测试和CLI启动器中正确应用
