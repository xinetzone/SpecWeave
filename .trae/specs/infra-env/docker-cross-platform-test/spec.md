# Docker跨平台构建测试（macOS + Windows）- PRD

## Overview
- **Summary**: 为caffe-ffi conda包构建Docker化的跨平台测试方案，支持在Linux Docker环境中验证macOS和Windows平台的conda构建产物。采用"三层测试矩阵"策略：L1交叉编译验证、L2二进制静态验证、L3运行时验证，覆盖从源码编译到功能测试的完整链路。
- **Purpose**: 解决当前无macOS/Windows物理机时无法验证A-T2(macOS构建)、A-T5(conda安装)等L4验证项的阻塞问题，将跨平台构建验证能力左移到开发阶段。
- **Target Users**: caffe-ffi开发者、CI/CD流水线

## Goals
- G1: 在Linux Docker环境中实现macOS conda包的交叉编译与二进制静态验证（L1+L2层）
- G2: 在Linux Docker环境中通过Wine实现Windows conda包的交叉编译、安装与运行时验证（L1+L2+L3层）
- G3: 提供统一的`test-cross-build.sh`脚本，支持`--target=macos-64/macos-arm64/win-64`参数
- G4: 改造现有build.sh/meta.yaml支持conda-build cross-compilation模式
- G5: 更新L4验证计划，标记通过Docker可验证的项

## Non-Goals (Out of Scope)
- 不追求在Docker中运行完整macOS虚拟机（Docker-OSX太重，不适合CI快速反馈）
- 不实现macOS运行时验证（依赖真实macOS CI runner，如GitHub Actions macOS）
- 不修改tvm-ffi/vendor等第三方依赖的构建系统
- 不实现Windows ARM64支持（conda-forge Windows arm64生态不成熟）
- 不实现GPU/CUDA跨平台测试
- 不解决conda-build 25.x/3.x升级问题（A-T6待macOS/Windows验证完成后推进）

## Background & Context
- caffe-ffi是Python C++扩展包，使用scikit-build-core(CMake)+conda-build打包
- 当前Linux Docker环境（caffe-ffi-jupyter镜像）可完成Linux构建测试
- ACT-004已完成build.sh/meta.yaml的macOS/Windows代码路径适配（@loader_path/@rpath/.dylib等）
- A-T7已完成pyproject.toml三层分离（项目默认→平台条件→conda运行时）
- 剩余待验证项（阻塞L4升级）：A-T2(macOS构建)、A-T5(conda安装)、部分A-T7(跨平台pyproject.toml)
- conda-forge已在Linux CI上通过cross-compilation构建macOS/Windows包多年，有成熟参考

### 关键技术约束
- macOS交叉编译：使用conda-forge的osx-64/osx-arm64 toolchain（clang+MacOSX.sdk），在Linux上交叉编译Mach-O二进制
- macOS静态验证：使用cctools（llvm-otool, llvm-install-name-tool）在Linux上检查Mach-O RPATH/符号
- Windows交叉编译：使用conda-forge的win-64 toolchain（MSVC wrapper via clang-cl或MinGW），在Linux上交叉编译PE/.pyd
- Windows运行时：使用Wine运行Windows Python + conda（conda-forge有win-64包可通过Wine安装）
- conda-build cross-compile：使用`conda_build_config.yaml`指定target platform，设置`CONDA_BUILD_CROSS_COMPILATION=1`

## Functional Requirements
- **FR-1**: conda recipe支持cross-compilation模式
  - meta.yaml正确区分build/host/run依赖（build平台工具 vs host平台库）
  - build.sh在cross-compile模式下自动检测`$CONDA_BUILD_CROSS_COMPILATION`并跳过运行时测试（$PYTHON import等）
  - conda_build_config.yaml配置macOS和Windows target platforms

- **FR-2**: macOS交叉编译Docker镜像
  - 基于现有caffe-ffi-jupyter镜像扩展，安装conda-forge osx-64/osx-arm64 cross-compilation toolchain
  - 支持`conda build --platform=osx-64`和`--platform=osx-arm64`
  - 安装cctools/llvm-bintools用于Mach-O二进制静态分析（otool-L/install_name_tool/nm等价工具）
  - 提供test-cross-build.sh脚本入口

- **FR-3**: Windows交叉编译+Wine运行时Docker镜像
  - 基于现有caffe-ffi-jupyter镜像扩展，安装conda-forge win-64 cross-compilation toolchain
  - 安装Wine用于运行Windows Python和生成的.pyd模块
  - 支持conda build产出win-64包后，通过Wine安装并执行import/功能测试
  - 提供test-cross-build.sh脚本入口

- **FR-4**: 跨平台测试脚本test-cross-build.sh
  - 参数：`--target=<osx-64|osx-arm64|win-64|all>`（必选）
  - 参数：`--skip-runtime`（仅L1+L2，跳过Wine/macOS运行时）
  - 参数：`--test-level=<1|2|3>`（测试层级，默认2）
  - L1层：conda build成功，产出正确文件（.dylib/.pyd）
  - L2层：二进制静态验证（RPATH/符号/依赖），使用平台适配工具
  - L3层：运行时验证（仅Wine/CI），Python import + Blob功能测试
  - 输出结构化测试报告（JSON或Markdown）

- **FR-5**: Docker Compose服务编排
  - 在现有docker-compose.yml中新增cross-build服务，支持TARGET_PLATFORM构建参数
  - 共享SpecWeave卷挂载（复用现有模式）

- **FR-6**: 文档与验证计划更新
  - 更新L4验证计划，标记通过Docker可验证的项
  - 记录cross-compile测试的局限和仍需真实机器验证的项

## Non-Functional Requirements
- **NFR-1 (性能)**: macOS L1+L2交叉编译测试应在10分钟内完成（不含Docker镜像构建时间）
- **NFR-2 (性能)**: Windows L1+L2+L3(Wine)测试应在20分钟内完成
- **NFR-3 (可维护性)**: Docker镜像基于现有caffe-ffi-jupyter扩展，不重复基础环境
- **NFR-4 (兼容性)**: cross-compile模式不破坏现有Linux原生构建流程（CONDA_BUILD_CROSS_COMPILATION未设置时行为不变）
- **NFR-5 (隔离性)**: 交叉编译工具链通过conda环境隔离，不污染主caffe-ffi conda环境

## Constraints
- **Technical**: 
  - Docker环境运行在Linux上（WSL2/Linux主机），需要支持binfmt_misc/QEMU（Wine不需要QEMU）
  - macOS cross-compile不能100%替代真实macOS测试（尤其是@rpath行为、系统库版本差异）
  - Wine对C++异常/OpenMP支持有限，可能存在误报/漏报
  - conda-build版本需≥3.28（现有镜像已满足）
  - Python 3.14对cross-compile支持需要验证
- **Business**: 无macOS物理机，Windows物理机可用性有限
- **Dependencies**: 
  - conda-forge cross-compilation toolchains（clangxx_osx-64, clangxx_osx-arm64, clang_win-64）
  - MacOSX.sdk（通过conda-forge的macos-sdk包提供）
  - Wine（WineHQ或conda-forge打包版本）
  - cctools/llvm-bintools（conda-forge提供）
  - 现有caffe-ffi-jupyter基础镜像

## Assumptions
- A1: conda-forge的osx-64/osx-arm64 cross-toolchain在Linux上可用且功能完整
- A2: MacOSX.sdk通过conda-forge `macos-sdk`包提供，无需从XCode手动提取
- A3: Wine能运行Windows Python 3.14 + numpy 2.x + openblas + protobuf 7.x（conda-forge win-64包）
- A4: scikit-build-core的overrides.if.platform-system在cross-compile时正确检测host平台（而非build平台）
- A5: build.sh中$PYTHON在cross-compile时指向build平台Python（Linux），可用于运行编译辅助脚本
- A6: 现有Linux构建流程在非cross-compile模式下完全不受影响

## Acceptance Criteria

### AC-1: meta.yaml支持cross-compilation
- **Given**: conda-build环境配置了target platform为osx-64
- **When**: 执行`conda build conda.recipe -c conda-forge --platform=osx-64`
- **Then**: 构建成功产出osx-64/_caffe_ffi*.dylib文件，build依赖（compiler/cmake/patchelf/cctools）从build平台获取，host依赖（python/numpy/openblas）从osx-64获取
- **Verification**: `programmatic`
- **Notes**: 检查CONDA_BUILD_CROSS_COMPILATION环境变量被正确传递

### AC-2: build.sh在cross-compile模式下正确处理运行时测试
- **Given**: CONDA_BUILD_CROSS_COMPILATION=1
- **When**: build.sh执行
- **Then**: 跳过$PYTHON import验证（因为host平台Python无法在build平台运行），但RPATH修复、符号检查、依赖检查（使用静态工具）仍正常执行
- **Verification**: `programmatic`
- **Notes**: L3层运行时测试交给test-cross-build.sh在Wine/CI中执行

### AC-3: macOS L1+L2交叉编译验证通过
- **Given**: Docker cross-build镜像构建完成
- **When**: `test-cross-build.sh --target=osx-64 --test-level=2`
- **Then**: 产出caffe-ffi-0.1.0-py314_7_osx-64.tar.bz2，内部_caffe_ffi*.dylib的@rpath正确，TVMFFIGetCustomAllocator符号存在，libtvm_ffi依赖引用为@rpath相对路径
- **Verification**: `programmatic`

### AC-4: Windows L1+L2交叉编译验证通过
- **Given**: Docker cross-build镜像构建完成
- **When**: `test-cross-build.sh --target=win-64 --test-level=2`
- **Then**: 产出caffe-ffi-0.1.0-py314_7_win-64.conda，内部_caffe_ffi*.pyd存在，依赖DLL列表正确
- **Verification**: `programmatic`

### AC-5: Windows L3运行时验证通过（Wine）
- **Given**: win-64 conda包构建成功
- **When**: `test-cross-build.sh --target=win-64 --test-level=3`
- **Then**: Wine环境下安装win-64包，`python -c "import caffe_ffi; b=caffe_ffi.Blob([100])"`成功执行
- **Verification**: `programmatic`
- **Notes**: Wine兼容性问题如无法解决则降级为"预期失败"并记录

### AC-6: 现有Linux构建流程不受影响
- **Given**: 无CONDA_BUILD_CROSS_COMPILATION设置
- **When**: 在现有caffe-ffi-jupyter容器中运行test-conda-build.sh
- **Then**: 所有现有测试通过，行为与修改前一致
- **Verification**: `programmatic`

### AC-7: Docker镜像构建与编排
- **Given**: docker-compose.yml已更新
- **When**: `docker compose build cross-build && docker compose run --rm cross-build --target=all --test-level=2`
- **Then**: 三个target（osx-64/osx-arm64/win-64）的L1+L2测试依次执行并输出报告
- **Verification**: `programmatic`

### AC-8: L4验证计划更新
- **Given**: 跨平台测试方案实现完成
- **When**: 审查l4-verification-plan-and-checklist.md
- **Then**: A-T2标记为"Docker L1+L2验证通过，L3待macOS CI"，A-T5标记为"win-64 Wine验证通过，osx-64/osx-arm64待CI"，新增测试覆盖矩阵
- **Verification**: `human-judgment`

## Open Questions
- [ ] Q1: macOS arm64 (osx-arm64) cross-compilation是否需要特殊配置？conda-forge是否提供完整的osx-arm64 toolchain for linux-64 build？
- [ ] Q2: Windows conda包应该用MSVC ABI（clang-cl交叉编译）还是MinGW ABI？conda-forge的win-64包用哪个？
- [ ] Q3: Wine运行Windows conda的成熟度如何？是否有已知问题影响numpy/openblas/protobuf？
- [ ] Q4: scikit-build-core的platform-system override在cross-compile时是看build还是host平台？可能需要改用CMake toolchain file传递目标平台信息。
- [ ] Q5: 是否需要支持Linux arm64 cross-compile？（用户未要求，但aarch64嵌入式/服务器场景可能需要）
- [ ] Q6: Docker镜像大小预算？macOS cross-toolchain + Wine可能使镜像超过5GB，是否需要拆分为两个镜像？
