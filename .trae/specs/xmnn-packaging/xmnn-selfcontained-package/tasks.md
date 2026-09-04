# xmnn-package - 自洽独立用户分发包 - Implementation Plan

## [x] Task 1: 创建xmnn-package目录结构和.gitignore
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `external/chaos/ai/` 下创建 `xmnn-package/` 目录
  - 创建子目录：`bin/`、`lib/`、`docker/`、`docs/`、`examples/`
  - 创建 `.gitignore` 排除大文件（*.whl、*.tar、*.tar.gz、*.zip、*.sha256、version.json等动态生成文件）
  - 在lib/、docker/下创建.gitkeep保持目录结构
- **Acceptance Criteria Addressed**: AC-1, AC-12
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录结构完整，bin/lib/docker/docs/examples存在
  - `programmatic` TR-1.2: .gitignore存在且包含正确的排除规则
  - `programmatic` TR-1.3: git status不显示whl/tar等大文件（即使存在）

## [x] Task 2: 编写自包含的日志函数库和公共脚本头
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 `bin/lib/common.sh`（包内公共函数，所有脚本source这个文件而非外部文件）
  - 包含：TTY颜色检测、log_info/log_warn/log_error/log_success/log_step/log_header/log_pass/log_fail
  - 计数器使用 `VAR=$((VAR+1))` 模式
  - SCRIPT_DIR计算基于脚本自身位置，PACKAGE_ROOT计算为SCRIPT_DIR的上级（包根目录）
- **Acceptance Criteria Addressed**: AC-9, NFR-6, NFR-7
- **Test Requirements**:
  - `programmatic` TR-2.1: common.sh中无source外部文件（仅内置函数）
  - `programmatic` TR-2.2: PACKAGE_ROOT正确指向包根目录（bin/的上级）
  - `programmatic` TR-2.3: 所有日志函数正常工作，非TTY环境不输出颜色

## [ ] Task 3: 编写bin/install.sh（零参数自包含安装脚本）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 安装脚本仅查找 `$PACKAGE_ROOT/lib/` 下的xmnn-*.whl
  - 移除development模式，无任何 `../` 外部路径引用
  - 功能：Python/pip前置检查 → whl自动查找 → SHA256校验 → pip install --force-reinstall --no-deps → 自动调用verify.sh
  - 支持参数：--python <path>、--skip-verify、--whl <path>（显式指定，仍需在包内或绝对路径）、--help
  - source bin/lib/common.sh获取日志函数和路径变量
- **Acceptance Criteria Addressed**: AC-2, AC-9, NFR-2, NFR-4, NFR-5
- **Test Requirements**:
  - `programmatic` TR-3.1: 脚本中grep无 `\.\./xmnn-releases` 或任何跳出包目录的 `../`
  - `programmatic` TR-3.2: 零参数执行时自动找到lib/下的whl
  - `programmatic` TR-3.3: SHA256校验逻辑正确（.sha256存在时验证，不存在时警告）
  - `programmatic` TR-3.4: --help正常输出帮助信息
  - `programmatic` TR-3.5: 重复执行幂等（不报错，force-reinstall）

## [ ] Task 4: 编写bin/verify.sh（环境验证脚本，增强版）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 基于xmnn-client/verify.sh增强，增加到10+项检查
  - 检查项：Python可执行、import tvm、import vta、import xmnn、_libs目录、libtvm.so加载、Python版本>=3.14、version.json读取、bootstrap.pth存在、基本计算测试
  - 输出PASS/FAIL/WARN统计，失败时输出针对性修复建议
  - 支持参数：--python <path>、--help
  - source bin/lib/common.sh
- **Acceptance Criteria Addressed**: AC-3, AC-9, NFR-3
- **Test Requirements**:
  - `programmatic` TR-4.1: 至少10项检查
  - `programmatic` TR-4.2: 所有FAIL项有修复建议
  - `programmatic` TR-4.3: 无外部路径引用
  - `programmatic` TR-4.4: 最终输出PASS/FAIL计数和总结

## [ ] Task 5: 编写bin/docker-setup.sh（Docker镜像管理脚本）
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 检测Docker是否可用，不可用时给出安装指引并回退到pip安装提示
  - 检测本地是否已有xmnn-runtime:latest镜像
  - 若 `$PACKAGE_ROOT/docker/xmnn-runtime.tar` 存在，提示用户是否load
  - 若不存在tar包，提示：a) 从docker/目录load（如有）b) 从registry拉取 c) 使用本地pip安装
  - 提供docker-run命令示例（挂载卷、运行容器、执行验证）
  - 支持参数：--load（强制load tar包）、--run（运行容器）、--verify（容器内验证）、--help
  - source bin/lib/common.sh
- **Acceptance Criteria Addressed**: AC-4, AC-9
- **Test Requirements**:
  - `programmatic` TR-5.1: Docker不可用时友好提示
  - `programmatic` TR-5.2: tar包存在时提供load选项
  - `programmatic` TR-5.3: 无外部路径引用
  - `human-judgement` TR-5.4: Docker使用指引清晰易懂

## [ ] Task 6: 编写bin/hello-world.sh（一键运行示例）
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 一键运行examples/hello-world.py
  - 前置检查：xmnn是否已安装（尝试import xmnn）
  - 若未安装，提示先运行install.sh
  - 支持参数：--python <path>、--help
  - source bin/lib/common.sh
- **Acceptance Criteria Addressed**: AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-6.1: 未安装时友好提示
  - `programmatic` TR-6.2: 安装后成功运行hello-world.py
  - `programmatic` TR-6.3: 无外部路径引用

## [ ] Task 7: 编写examples/hello-world.py
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 基于xmnn-client/examples/hello-world.py，确保完全独立可运行
  - 输出：XMNN版本、TVM版本、简单张量计算验证
  - 不依赖包外任何文件
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-7.1: 安装xmnn后可独立运行
  - `programmatic` TR-7.2: 输出包含版本信息和计算结果

## [ ] Task 8: 编写docs/自包含文档（5个文档）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建以下文档，所有文档**不引用包外任何路径**：
    - `README.md`：3步快速开始（解压→bash bin/install.sh→bash bin/hello-world.sh），支持Linux/WSL2说明，文档索引
    - `INSTALL.md`：详细安装指南（前提条件、Python环境、pip安装、离线安装、验证）
    - `DOCKER.md`：Docker使用指南（镜像加载、容器运行、挂载卷、验证、pip升级）
    - `WSL2.md`：Windows WSL2完整指引（安装WSL2、进入目录、路径转换、常见问题）
    - `TROUBLESHOOTING.md`：故障排查（常见问题、错误信息对照、解决方案）
  - 文档中所有路径均为相对于包根目录的相对路径
- **Acceptance Criteria Addressed**: AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-8.1: grep所有文档无 `\.\./xmnn` 或 `SpecWeave` 等外部路径/仓库引用
  - `human-judgement` TR-8.2: README.md快速开始3步清晰
  - `human-judgement` TR-8.3: WSL2.md对Windows用户友好
  - `human-judgement` TR-8.4: TROUBLESHOOTING.md覆盖verify.sh可能输出的所有错误

## [ ] Task 9: 编写根目录README.md（包入口文档）
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - 包根目录的README.md是用户看到的第一个文件
  - 内容：XMNN简介、支持平台、3步快速开始（代码块可直接复制执行）、文档索引、版本信息展示
  - 不引用包外任何文档
- **Acceptance Criteria Addressed**: AC-5, AC-11
- **Test Requirements**:
  - `programmatic` TR-9.1: 无外部链接/路径引用
  - `human-judgement` TR-9.2: 3步快速开始可在复制到任意目录后直接执行
  - `human-judgement` TR-9.3: 文档语言为中文

## [ ] Task 10: 编写package.sh一键打包脚本（开发者使用）
- **Priority**: high
- **Depends On**: Task 1-9
- **Description**: 
  - 在xmnn-package/根目录创建package.sh（开发者在开发仓库中运行）
  - 功能：
    1. 参数解析：--version <vX.Y.Z>（必填）、--with-docker（可选，是否导出镜像tar）、--output <dir>（可选输出目录）、--help
    2. 创建目标目录：`<output>/xmnn-package-<version>/`
    3. 复制模板文件：bin/、docs/、examples/、README.md、.gitignore
    4. 从 `../xmnn-releases/latest/` 复制whl和sha256到lib/
    5. 复制version.json到包根目录（或基于latest/version.json生成）
    6. 若指定--with-docker，执行 `docker save xmnn-runtime:latest -o docker/xmnn-runtime.tar`
    7. 生成/更新version.json中的package_type="self-contained"
    8. 输出打包结果摘要
  - SCRIPT_DIR为脚本所在目录（即xmnn-package/模板目录）
- **Acceptance Criteria Addressed**: AC-6, AC-10
- **Test Requirements**:
  - `programmatic` TR-10.1: --version参数必填，无时报错
  - `programmatic` TR-10.2: 打包后目标目录包含所有必要文件
  - `programmatic` TR-10.3: lib/下有whl和sha256文件
  - `programmatic` TR-10.4: --with-docker时docker/下有tar包
  - `programmatic` TR-10.5: version.json包含所有必填字段
  - `programmatic` TR-10.6: 打包后的目录grep无外部路径引用

## [ ] Task 11: 创建version.json模板和占位文件
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 创建 `version.json.template` 模板文件（在xmnn-package/根目录，不纳入生成包）
  - 包含字段：version、build_date、python_version、xmnn_version、whl_filename、whl_sha256、package_type="self-contained"
  - 在lib/和docker/下放.gitkeep
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-11.1: 模板包含所有必填字段
  - `programmatic` TR-11.2: .gitkeep存在以保持空目录

## [ ] Task 12: 更新父级AGENTS.md路由表
- **Priority**: low
- **Depends On**: Task 1
- **Description**: 
  - 更新 `external/chaos/ai/AGENTS.md`，在镜像矩阵中添加xmnn-package/的说明
  - 明确xmnn-client（开发仓库内工具）和xmnn-package（独立交付物）的定位区别
  - 在上下文路由表中添加xmnn-package/条目
  - 注意：不修改xmnn-client/内容
- **Acceptance Criteria Addressed**: AC-1（上下文清晰）
- **Test Requirements**:
  - `human-judgement` TR-12.1: AGENTS.md中xmnn-package定位清晰
  - `human-judgement` TR-12.2: xmnn-client与xmnn-package区别明确

## [ ] Task 13: 端到端验证（打包→复制到临时目录→安装→验证→运行）
- **Priority**: high
- **Depends On**: Task 1-11
- **Description**: 
  - 执行完整的端到端测试：
    1. 运行package.sh生成自洽包
    2. 将生成的包复制到/tmp/（或其他独立路径）
    3. 在独立路径中执行bash bin/install.sh
    4. 执行bash bin/verify.sh，确认全部PASS
    5. 执行bash bin/hello-world.py，确认输出正确
    6. grep所有脚本和文档，确认无外部路径引用
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-13.1: 打包成功无错误
  - `programmatic` TR-13.2: 复制到独立路径后install.sh成功
  - `programmatic` TR-13.3: verify.sh全部PASS
  - `programmatic` TR-13.4: hello-world成功运行
  - `programmatic` TR-13.5: grep无外部路径引用（允许package.sh引用../xmnn-releases，因为它是开发脚本不是分发内容）
