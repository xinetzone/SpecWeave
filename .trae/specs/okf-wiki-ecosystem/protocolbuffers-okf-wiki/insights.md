# protobuf 束 I 阶段架构洞察与知识地图（insights.md）

> 阶段：I（Insight）阶段产出。基于 R 阶段 6 份事实清单（facts-repo-structure.md / facts-cpp-core.md / facts-compiler.md / facts-runtimes.md / facts-testing.md / facts-protobuf-ci.md，合计 542 条事实：F-REPO 67 + F-CPP 144 + F-CMP 90 + F-RT 105 + F-TST 80 + F-CI 56）提炼。
> 版本基准：protobuf 主仓 v37.0-dev（F-REPO-028、F-REPO-031）。
> 本文件是 D 阶段（文档生成）的唯一蓝图：第一部分为架构洞察，第二至五部分为两束（protobuf / protobuf-ci）+ examples + references 的完整文档清单。

---

# 第一部分：核心洞察（5 条四元组）

## 洞察 1：双运行时内核架构——"多语言"实为"多绑定"

- **陈述**：同一份 proto schema 可由 C++ 全功能内核或 upb 轻量 C 内核执行，Python/Rust/PHP/Ruby/Lua/hpb 等"非 C++"运行时并非各自独立实现 wire format，而是通过 C FFI 绑定复用这两个内核之一。
- **证据**：
  - Python C 扩展模块 `google._upb._message` 初始化时 `PyModule_AddIntConstant(m, "_IS_UPB", 1)`（F-RT-004），setup.py 的 Extension 源码 glob 直接包含 `upb/**/*.c`（F-RT-025）；
  - Rust `protobuf_lite.rs` 按编译开关选择 `use protobuf_cpp as kernel;` 或 `use protobuf_upb as kernel;`，末尾 `pub use kernel::*;`（F-RT-033），其 upb 层转导出 upb C API（F-RT-035）；
  - hpb `multibackend.h` 定义 `HPB_INTERNAL_BACKEND_UPB=1`/`HPB_INTERNAL_BACKEND_CPP=2` 并按宏将 `namespace backend` 别名到 upb 或 cpp（F-RT-059）；`rust/defs.bzl` 的 `rust_proto_library` 按 `//rust:use_upb_kernel` 条件在 upb/cpp 变体间选择（F-RT-051）；
  - PHP 扩展含 `php-upb.c/.h`（F-RT-090）、Ruby 扩展含 `ruby-upb.c/.h`（F-RT-096）、Lua 入口 `luaopen_lupb`（F-RT-100）——三个语言绑定直接内嵌 upb；
  - conformance failure list 的 `python`/`python_cpp`/`python_upb`/`rust_cc`/`rust_upb` 双实现分列（F-TST-034）。
- **反常识**：初学者以为"每个语言各自实现了一遍 protobuf 解析器"（甚至以为 Python 有纯 Python 解析器在跑）；实际上 Python 运行时已经默认是 upb C 内核（`_IS_UPB=1`），"同一语言双内核"（python_cpp/python_upb、rust_cc/rust_upb）才是常态设计。
- **行动**：知识地图不能按语言孤立组织——必须有"upb 与 Rust 运行时"（12 篇）这样的内核中心文档，Python（11 篇）与 hpb（13 篇）文档显式回链内核概念；其他语言概览（14 篇）按"语言绑定 × 内核选择"二维表格组织，而非逐语言流水账。

## 洞察 2：descriptor 体系是贯穿全生命周期的单一事实源

- **陈述**：FileDescriptorProto 既是编译器的中间表示，又是插件通信协议的载荷、代码生成的输入、运行时反射的数据源，以及跨进程传递 schema 的序列化格式（descriptor set）——protobuf 用 protobuf 描述 protobuf，完成自举。
- **证据**：
  - descriptor.proto 顶层 23 个 message（FileDescriptorProto/DescriptorProto/FieldDescriptorProto/FeatureSet/FeatureSetDefaults 等，F-CPP-066）；
  - 编译器侧：Parser 将源码解析进 FileDescriptorProto（F-CMP-021），Importer 通过 SourceTreeDescriptorDatabase（继承自 DescriptorDatabase，F-CMP-029 / F-CPP-069）将其喂入 DescriptorPool；
  - 插件协议侧：CodeGeneratorRequest 的 `repeated FileDescriptorProto proto_file = 15` 与 `source_file_descriptors = 17`（F-CMP-049）；
  - 运行时侧：C++ `DescriptorPool::BuildFile(const FileDescriptorProto&)`（F-CPP-060）与 `generated_pool()`（F-CPP-058）；Python `PyUpb_DescriptorPool` 的 `AddSerializedFile`（F-RT-013）；
  - 传输侧：protoc 的 `--descriptor_set_in`/`-o --descriptor_set_out` flag（F-CMP-014）与 `GetTransitiveDependencies`（F-CMP-017 中列出的私有方法，TransitiveDependencyOptions 见 F-CMP-011）。
- **反常识**：初学者以为反射元数据是各语言编译器内建的静态表格；实际上 C++ 反射的源头是序列化的 descriptor 数据本身，`descriptor.pb.h` 是 protobuf 自己生成的代码（F-CPP-063 的 Edition 枚举即来自该生成文件）——生成器先吃自己的狗粮。
- **行动**：把"descriptor 与反射"（03 篇）设为核心机制组的枢纽文档；编译器组（07-10 篇）与运行时组（11-14 篇）的各篇在涉及 schema 流转处显式回链 03 篇；`--descriptor_set_in/out` 归入 07 篇命令行文档而非运行时文档。

## 洞察 3：protoc 的生成器统一接口——内置生成器与外部插件同构

- **陈述**：内置语言生成器与外部插件走同一 CodeGenerator 抽象接口与同一 CodeGeneratorRequest/Response proto 协议，protoc 本体甚至存在一个不注册任何内置生成器的变体（main_no_generators.cc），语言扩展能力完全开放。
- **证据**：
  - `main.cc` 用统一的 `cli.RegisterGenerator(flag, opt_flag, &generator, help)` 注册 11 组内置生成器（`--cpp_out`/`--java_out`/`--kotlin_out`/`--python_out`/`--pyi_out`/`--php_out`/`--ruby_out`/`--rbs_out`/`--csharp_out`/`--objc_out`/`--rust_out`，F-CMP-003）；
  - `main_no_generators.cc` 注释原句 "This is a version of protoc that has no built-in code generators."，仅 `AllowPlugins("protoc-")` 后 Run（F-CMP-005）；
  - `CodeGenerator::Generate` 为纯虚接口（F-CMP-035），内置与插件共用；插件命名规则 "protoc-gen-" + flag 去掉 "_out"（F-CMP-008），`--plugin` flag 解析后写入 `plugins_` map（F-CMP-016）；
  - hpb_generator 的 `Generator : protoc::CodeGenerator`（F-RT-066）、Lua 的 `LuaGenerator : protoc::CodeGenerator`（F-RT-104）、Python 独立插件 `plugin_main.cc` 包装 `PluginMain(argc, argv, &generator)`（F-CMP-078）——三者都是"用插件身份实现内置等价能力"的实例；
  - 能力协商字段 `supported_features`/`minimum_edition`/`maximum_edition` 在 CodeGeneratorResponse 中定义（F-CMP-050），与 CodeGenerator::Feature 枚举 "must be kept in sync"（F-CMP-037）。
- **反常识**：初学者以为 `--cpp_out` 是写死在 protoc 里的特权通道、插件是二等公民；实际上两者在命令行层面同构（OutputDirective 对插件 generator 为 NULL，F-CMP-018），插件能拿到与内置生成器完全相同的 FileDescriptorProto 输入与 feature 协商机制。
- **行动**：编译器组按"命令行框架（07）→ 解析与导入（08）→ 生成器体系（09）→ 插件协议（10）"四段递进，且 09/10 两篇共用同一接口视角，明确说明"内置 = 进程内注册、插件 = stdin/stdout 协议化"这一唯一差异，避免写成两套体系。

## 洞察 4：Editions 特性系统——proto2/proto3 被降维为 feature 预设

- **陈述**：Edition 枚举 8 值（EDITION_UNKNOWN/LEGACY/PROTO2/PROTO3/2023/2024/2026/UNSTABLE）将"语法版本"重构为 FeatureSet 的可组合开关集合，旧语法 proto2/proto3 只是两个 legacy 预设值，编译器、生成器与运行时通过 edition 区间与 supported_features 位标志协商能力。
- **证据**：
  - Edition 枚举完整 8 值定义于 descriptor.pb.h（F-CPP-063）；FileDescriptor 的 `edition()` 注释明言 "For legacy proto2/proto3 files, special EDITION_PROTO2 and EDITION_PROTO3 values are used"（F-CPP-055）；`features()` 返回 merged FeatureSet（F-CPP-056）；
  - descriptor.proto 定义 FeatureSet(1060) 与 FeatureSetDefaults(1297)（F-CPP-066）；仓库根存在 feature_resolver.h（F-CPP-138）；
  - 编译器协商：CodeGenerator::Feature 枚举 `FEATURE_PROTO3_OPTIONAL=1, FEATURE_SUPPORTS_EDITIONS=2`（F-CMP-037）、GetMinimumEdition/GetMaximumEdition 虚方法（F-CMP-040）、`ProtocMinimumEdition()/ProtocMaximumEdition()` 返回 EDITION_PROTO2/EDITION_2026（F-CMP-043）、`EnforceEditionsSupport` 与 `SetupFeatureResolution`（F-CMP-17）、`--edition_defaults_out/--edition_defaults_minimum/--edition_defaults_maximum` flag（F-CMP-014）；
  - Parser 行为随 edition 切换：`DefaultToOptionalFields()` 对 "editions"/"proto3" 返回 true（F-CMP-027）；
  - 生成器全部声明 `GetMaximumEdition() = EDITION_2026`（cpp F-CMP-057、java F-CMP-068、python F-CMP-075、csharp F-CMP-080、objc F-CMP-084、php F-CMP-085、ruby F-CMP-086、rust F-CMP-088、kotlin F-CMP-090）；唯一例外 RBSGenerator 只声明 FEATURE_PROTO3_OPTIONAL、无 edition override（F-CMP-087）——能力协商矩阵真实生效；
  - editions/ 目录提供 compile_edition_defaults/embed_edition_defaults 规则与 2023/2024 默认值测试（F-TST-066~071）、56 个 codegen_tests proto 按 edition2023_*/edition2024_*/proto2_*/proto3_ 前缀分组（F-REPO-055 / F-TST-072）。
- **反常识**：初学者以为 proto2 与 proto3 是两套独立语法、editions 是"第三套语法"；实际上在 v37 编译器内它们只是 feature 解析系统中的两个预设（EDITION_PROTO2=998 / EDITION_PROTO3=999 被编码在同一个 Edition 枚举里），每个生成器通过 maximum_edition 声明自己"看得懂哪个未来"。
- **行动**：Editions 独立成篇（15 篇）放在高级组，作为"语法演进"主线；其证据横跨 F-CPP/F-CMP/F-TST/F-REPO 四份事实文件，D 阶段写作时必须交叉引用；RBSGenerator 这个"能力降级"实例要写进协商矩阵，防止读者误以为所有生成器能力等价。

## 洞察 5：双一等公民构建系统 × CI 分层缓存治理

- **陈述**：主仓同时维护 Bazel（MODULE.bazel + 预编译 protoc toolchain）与 CMake（17 个 option + 20 个模块）两套完整构建系统，覆盖从 lite 库到 upb、conformance 的全部产物；CI 侧由独立仓库 protobuf-ci 的 9 个 composite action 与五层缓存（bazel 远程缓存 / ccache / sccache / repository cache / bazelisk cache）支撑 10 语言 × 9 平台的构建矩阵。
- **证据**：
  - CMake 侧：17 个 option（protobuf_BUILD_TESTS/CONFORMANCE/EXAMPLES、protobuf_BUILD_LIBUPB 等，F-REPO-033）、按序 include 14 个仓库内 cmake 模块（F-REPO-034）、cmake/ 目录 20 个 .cmake + 4 个 .in 模板 + 4 个 golden 清单（F-REPO-035/036）；
  - Bazel 侧：MODULE.bazel 17 个非 dev bazel_dep + 12 个 dev 依赖（F-REPO-039/040）、prebuilt_protoc 9 平台仓库（F-REPO-041）、10 个 //toolchain 交叉编译 toolchain（F-REPO-046）、bazel/ 目录 8 个 .bzl 规则（F-REPO-050）、.bazelrc 12 条 incompatible_* 标志与多编译器配置段（F-REPO-053）；
  - CI 侧：主仓 14 个 workflow 以 `protocolbuffers/protobuf-ci/<action>@v6` 引用全部 9 个顶层 action（F-CI-052/053）；protobuf-ci 任何变更须经 release 才能反映到其他仓库（F-CI-004/056）；
  - 缓存分层：bazel 远程缓存 `--remote_cache=https://storage.googleapis.com/protobuf-bazel-cache/...`（F-CI-041）、ccache 三级 restore-keys（精确 SHA → 分支 → PR 基分支，F-CI-024）、sccache GCS 桶 `protobuf-sccache`（F-CI-038）、repository cache（单个可达 ~500 MB，F-CI-049）、bazelisk 版本缓存（F-CI-015）。
- **反常识**：初学者以为开源项目只有一套构建系统、CI 缓存就是 `actions/cache` 一层；实际上这里 CMake 与 Bazel 是并重的两条一等公民路径（连 conformance 都有 `protobuf_BUILD_CONFORMANCE` option，F-TST-003），且 CI 缓存按"编译产物层（ccache/sccache）—Bazel 仓库层（repository cache）—远程共享层（GCS）"三级分工，Windows 还有专属 ccache 变量（`CCACHE_MAXSIZE=300M`，缓存体积约为其他平台 2 倍，F-CI-043）。
- **行动**：仓库总览文档（00 篇）必须双构建系统并列讲解并给出选型场景；protobuf-ci 作为独立知识束（4-5 篇 concepts + 1 个信源文件）不与主束混排；两束在"构建系统"主题上通过交叉引用衔接而非重复内容。

---

# 第二部分：protobuf 束知识地图（concepts/，17 篇）

学习路径分 5 组，编号即阅读顺序：入门组（00-02）→ 核心机制组（03-06）→ 编译器组（07-10）→ 运行时组（11-14）→ 高级组（15-16）。

## 入门组

### 00-repo-overview-and-build-systems.md
- **title**：仓库总览与双构建系统
- **覆盖事实**：F-REPO-001、F-REPO-002、F-REPO-021、F-REPO-024、F-REPO-026、F-REPO-027、F-REPO-028、F-REPO-029、F-REPO-030、F-REPO-031、F-REPO-032、F-REPO-033、F-REPO-034、F-REPO-035、F-REPO-036、F-REPO-037、F-REPO-038、F-REPO-039、F-REPO-040、F-REPO-041、F-REPO-042、F-REPO-043、F-REPO-044、F-REPO-045、F-REPO-046、F-REPO-047、F-REPO-048、F-REPO-049、F-REPO-050、F-REPO-051、F-REPO-052、F-REPO-053、F-REPO-056、F-REPO-057、F-REPO-058、F-REPO-059、F-REPO-061、F-REPO-062、F-REPO-063、F-REPO-064、F-REPO-065
- **内容范围**：一句话：32 个顶层目录与版本常量（v37.0-dev）全景图，Bazel（MODULE.bazel/预编译 protoc toolchain/10 交叉编译 toolchain）与 CMake（17 option/20 模块）两套一等公民构建系统的并列讲解，含 docs/、go/、compatibility/、ci/ 辅助目录说明。

### 01-message-model.md
- **title**：消息模型基础：Message 与 MessageLite
- **覆盖事实**：F-CPP-001、F-CPP-002、F-CPP-003、F-CPP-004、F-CPP-005、F-CPP-006、F-CPP-007、F-CPP-008、F-CPP-009、F-CPP-010、F-CPP-011、F-CPP-012、F-CPP-119、F-CPP-120、F-CPP-121、F-CPP-122、F-CPP-123、F-CPP-124、F-CPP-125、F-CPP-141、F-CPP-144、F-RT-079、F-RT-082
- **内容范围**：一句话：MessageLite（序列化/ByteSize/Clear 纯虚接口）→ Message（CopyFrom/DebugString/New(Arena)）类层次，ClassData/ReflectionSchema/MigrationSchema 生成侧类型信息，以及 C#（IMessage.cs）与 Objective-C（GPBMessage : NSObject）的对应模型。

### 02-wire-format.md
- **title**：Wire Format 二进制编码
- **覆盖事实**：F-CPP-075、F-CPP-076、F-CPP-077、F-CPP-078、F-CPP-079、F-CPP-080、F-CPP-081、F-CPP-082、F-CPP-083、F-CPP-084、F-CPP-085、F-CPP-086、F-CPP-087、F-CPP-088、F-CPP-089、F-CPP-090、F-CPP-091、F-CPP-092、F-CPP-093、F-RT-086
- **内容范围**：一句话：WireType 6 值枚举、tag 构成（kTagTypeBits=3）、varint 编码尺寸计算，WireFormatLite/WireFormat 静态工具与 CodedInputStream/CodedOutputStream、ZeroCopy 流族（Array/Cord/Copying 适配器），附 GPBWireFormat 的跨语言对照。

## 核心机制组

### 03-descriptors-and-reflection.md
- **title**：Descriptor 体系与运行时反射
- **覆盖事实**：F-CPP-013、F-CPP-014、F-CPP-015、F-CPP-016、F-CPP-017、F-CPP-018、F-CPP-019、F-CPP-020、F-CPP-021、F-CPP-022、F-CPP-023、F-CPP-024、F-CPP-025、F-CPP-026、F-CPP-027、F-CPP-028、F-CPP-029、F-CPP-030、F-CPP-031、F-CPP-032、F-CPP-033、F-CPP-034、F-CPP-035、F-CPP-042、F-CPP-043、F-CPP-044、F-CPP-045、F-CPP-046、F-CPP-047、F-CPP-048、F-CPP-049、F-CPP-050、F-CPP-051、F-CPP-052、F-CPP-053、F-CPP-054、F-CPP-057、F-CPP-058、F-CPP-059、F-CPP-060、F-CPP-061、F-CPP-062、F-CPP-066、F-CPP-069、F-CPP-070、F-CPP-071、F-CPP-072、F-CPP-073、F-CPP-074、F-RT-010、F-RT-011、F-RT-012、F-RT-013、F-RT-014、F-RT-083
- **内容范围**：一句话：8 类 Descriptor（File/Message/Field/Enum/Oneof/Service/Method/EnumValue）与 Reflection 的 getter/setter/repeated/oneof 全矩阵，DescriptorPool 的 BuildFile/generated_pool 与 DescriptorDatabase 抽象（Simple/Encoded/Merged），Python 与 Objective-C 的反射绑定对照——全文回链洞察 2 的"单一事实源"。

### 04-arena-memory-management.md
- **title**：Arena 内存管理
- **覆盖事实**：F-CPP-036、F-CPP-037、F-CPP-038、F-CPP-039、F-CPP-040、F-CPP-041、F-RT-007、F-RT-034、F-RT-036、F-RT-057、F-TST-039
- **内容范围**：一句话：C++ Arena 的 Make/Own/DoCreateMessage 与 ArenaStringPtr 可变位机制，跨语言 Arena 形态（PyUpb_Arena、Rust upb::Arena、hpb Arena 的 Fuse/IsFused）及 BM_ArenaFuseBalanced/Unbalanced 基准测试。

### 05-containers-extensions-unknown-fields.md
- **title**：容器、扩展与未知字段
- **覆盖事实**：F-CPP-100、F-CPP-101、F-CPP-102、F-CPP-103、F-CPP-104、F-CPP-105、F-CPP-106、F-CPP-107、F-CPP-108、F-CPP-109、F-CPP-110、F-CPP-111、F-CPP-112、F-CPP-113、F-CPP-114、F-CPP-115、F-CPP-116、F-CPP-117、F-CPP-118、F-CPP-142、F-CPP-143、F-RT-016、F-RT-017、F-RT-018、F-RT-019、F-RT-046、F-RT-047、F-RT-048、F-RT-084、F-RT-085
- **内容范围**：一句话：Map/RepeatedField/RepeatedPtrField 容器语义，ExtensionSet 的 RegisterExtension/Has/Get/Set 与 LazyAnnotation，UnknownFieldSet 的 5 种 wire 类型保留机制，以及 Python（map.c/repeated.c/extension_dict.c/unknown_fields.c）、Rust（Repeated/Map view/mut 体系）、Objective-C（GPBArray/GPBDictionary 类型化容器族）三语言对照。

### 06-text-format-and-json.md
- **title**：文本格式与 JSON 序列化
- **覆盖事实**：F-CPP-094、F-CPP-095、F-CPP-096、F-CPP-097、F-CPP-098、F-CPP-099、F-RT-094、F-RT-102、F-TST-011
- **内容范围**：一句话：TextFormat 的 Printer/Parser 与 DebugString 三态，json/ 目录的 MessageToJsonString/JsonStringToMessage、ParseOptions/PrintOptions、lexer/parser/unparser/writer 内部结构，及 Ruby encode_json 与 Lua lupb_jsonencode 的跨语言入口。

## 编译器组

### 07-protoc-command-line.md
- **title**：protoc 命令行与编译管线
- **覆盖事实**：F-CMP-001、F-CMP-002、F-CMP-003、F-CMP-004、F-CMP-005、F-CMP-006、F-CMP-007、F-CMP-008、F-CMP-009、F-CMP-010、F-CMP-011、F-CMP-012、F-CMP-013、F-CMP-014、F-CMP-015、F-CMP-016、F-CMP-017、F-CMP-018、F-CMP-019、F-CMP-020
- **内容范围**：一句话：从 ProtobufMain 入口（AllowPlugins + 11 组 RegisterGenerator）到 Run/ParseArguments/InterpretArgument 的完整管线，含不带值 flag 15 个与带值参数 30+ 的全集、MODE_COMPILE/ENCODE/DECODE/PRINT 四模式、OutputDirective/GeneratorInfo 内部结构、--descriptor_set_in/out 与 --edition_defaults_* 的语义。

### 08-parser-and-importer.md
- **title**：Parser 与源码导入体系
- **覆盖事实**：F-CMP-021、F-CMP-022、F-CMP-023、F-CMP-024、F-CMP-025、F-CMP-026、F-CMP-027、F-CMP-028、F-CMP-029、F-CMP-030、F-CMP-031、F-CMP-032、F-CMP-033、F-CMP-034
- **内容范围**：一句话：Parser 的语言构件解析方法族（message/enum/service/import/oneof/map/option/visibility）与 LocationRecorder 源位置记录、SourceLocationTable，Importer/SourceTree/DiskSourceTree 的虚拟路径映射（MapPath/DiskFileToVirtualFile）与 MultiFileErrorCollector 错误收集。

### 09-code-generators.md
- **title**：代码生成器体系与各语言实现
- **覆盖事实**：F-CMP-035、F-CMP-036、F-CMP-037、F-CMP-038、F-CMP-039、F-CMP-040、F-CMP-041、F-CMP-042、F-CMP-043、F-CMP-044、F-CMP-045、F-CMP-046、F-CMP-056、F-CMP-057、F-CMP-058、F-CMP-059、F-CMP-060、F-CMP-061、F-CMP-062、F-CMP-063、F-CMP-064、F-CMP-065、F-CMP-066、F-CMP-067、F-CMP-068、F-CMP-069、F-CMP-070、F-CMP-071、F-CMP-072、F-CMP-073、F-CMP-074、F-CMP-075、F-CMP-076、F-CMP-077、F-CMP-079、F-CMP-080、F-CMP-081、F-CMP-082、F-CMP-083、F-CMP-084、F-CMP-085、F-CMP-086、F-CMP-087、F-CMP-088、F-CMP-089、F-CMP-090
- **内容范围**：一句话：CodeGenerator 接口契约（Generate 纯虚/GenerateAll 默认实现/Feature 位标志/GetMinimum/MaximumEdition/GetFeatureExtensions）与 GeneratorContext 输出抽象，随后逐一过 9 个内置生成器的目录结构与特色组件（cpp 的 FileGenerator/ParseFunctionGenerator/field_generators 工厂 14 函数、java 的 full/lite 双工厂、python/pyi、csharp、objectivec、php、ruby+rbs、rust、kotlin），并给出各生成器 edition 支持矩阵（RBSGenerator 为唯一降级实例）。

### 10-plugin-protocol.md
- **title**：插件协议（plugin.proto）
- **覆盖事实**：F-CMP-047、F-CMP-048、F-CMP-049、F-CMP-050、F-CMP-051、F-CMP-052、F-CMP-053、F-CMP-054、F-CMP-055、F-CMP-008、F-CMP-016、F-CMP-078、F-RT-065、F-RT-066、F-RT-067、F-RT-068、F-RT-069、F-RT-104
- **内容范围**：一句话：CodeGeneratorRequest/Response 的完整字段表（proto_file=15/source_file_descriptors=17/supported_features/minimum_edition 与 File 的 insertion_point/generated_code_info），PluginMain/GenerateCode 的插件进程骨架，protoc-gen-* 命名规则与 --plugin 解析，hpb_generator 与 Lua upbc 两个"以插件身份实现"的完整实例——回链洞察 3。

## 运行时组

### 11-python-runtime.md
- **title**：Python 运行时（upb C 扩展）
- **覆盖事实**：F-RT-001、F-RT-002、F-RT-003、F-RT-004、F-RT-005、F-RT-006、F-RT-007、F-RT-008、F-RT-009、F-RT-010、F-RT-011、F-RT-012、F-RT-013、F-RT-014、F-RT-015、F-RT-016、F-RT-017、F-RT-018、F-RT-019、F-RT-020、F-RT-021、F-RT-022、F-RT-023、F-RT-024、F-RT-025、F-RT-026、F-RT-027、F-RT-028、F-RT-029、F-RT-030
- **内容范围**：一句话：google._upb._message 模块从 PyInit__message 到九个 Init 子系统的初始化链、PyUpb_ModuleState 类型注册表、DescriptorPool 的 Add/Find 方法族与 fallback database、WeakMap/ObjCache 对象缓存、version_script.lds 的单符号导出、dist/setup.py 的源码 glob 与 build_targets.bzl 的三实现（python/cpp/upb）conformance 目标。

### 12-upb-and-rust-runtime.md
- **title**：upb 内核与 Rust 双 kernel 运行时
- **覆盖事实**：F-RT-031、F-RT-032、F-RT-033、F-RT-034、F-RT-035、F-RT-036、F-RT-037、F-RT-038、F-RT-039、F-RT-040、F-RT-041、F-RT-042、F-RT-043、F-RT-044、F-RT-045、F-RT-046、F-RT-047、F-RT-048、F-RT-049、F-RT-050、F-RT-051、F-RT-052、F-RT-053、F-RT-054、F-REPO-013、F-REPO-014、F-REPO-015、F-REPO-019、F-REPO-020
- **内容范围**：一句话：upb C 内核的 17 子目录结构与 upb_generator，Rust 的 protobuf_lite.rs kernel 编译开关、upb/sys 转导出层（"intended to be burned down"）、upb_kernel 与 cpp_kernel 的 InnerMap/InnerRepeated 平行实现、Proxied/MutProxied/Repeated/Map/Message trait 体系、defs.bzl 的 use_upb_kernel 条件选择与 8 个 release crates——洞察 1 的主证据文档。

### 13-hpb.md
- **title**：hpb：C++ 多后端 API 层与 hpb_generator
- **覆盖事实**：F-RT-055、F-RT-056、F-RT-057、F-RT-058、F-RT-059、F-RT-060、F-RT-061、F-RT-062、F-RT-063、F-RT-064、F-RT-065、F-RT-066、F-RT-067、F-RT-068、F-RT-069、F-RT-070、F-REPO-017、F-REPO-018
- **内容范围**：一句话：hpb 的 CreateMessage/Parse/Serialize 模板 API、multibackend.h 的 HPB_INTERNAL_BACKEND 编译期后端选择（upb=1/cpp=2）、backend/cpp 与 backend/upb 的双实现、Ptr/RepeatedField 的 Proxy conditional_t 技巧、StatusOr/SourceLocation 错误体系，及 hpb_generator 作为 protoc 插件（Generator : protoc::CodeGenerator）的生成流程与 GeneratedCodeInfo 注解。

### 14-other-language-runtimes.md
- **title**：其他语言运行时概览：Java/C#/ObjC/PHP/Ruby/Lua
- **覆盖事实**：F-RT-071、F-RT-072、F-RT-073、F-RT-074、F-RT-075、F-RT-076、F-RT-077、F-RT-078、F-RT-079、F-RT-080、F-RT-081、F-RT-082、F-RT-083、F-RT-084、F-RT-085、F-RT-086、F-RT-087、F-RT-088、F-RT-089、F-RT-090、F-RT-091、F-RT-092、F-RT-093、F-RT-094、F-RT-095、F-RT-096、F-RT-097、F-RT-098、F-RT-099、F-RT-100、F-RT-101、F-RT-102、F-RT-103、F-RT-104、F-RT-105、F-REPO-006、F-REPO-007、F-REPO-008、F-REPO-009、F-REPO-010、F-REPO-011、F-REPO-012、F-REPO-016
- **内容范围**：一句话：以"语言绑定 × 内核选择"二维视角综述六语言：Java（core/lite/kotlin 双运行时 + maven 布局）、C#（Google.Protobuf 源码清单与 WireFormat.cs）、Objective-C（GPB 前缀全家桶与类型化容器）、PHP（upb 扩展 + 纯 PHP Descriptors）、Ruby（C 扩展与 FFI 双实现）、Lua（lupb 绑定与 lua_proto_library 规则）。

## 高级组

### 15-editions-feature-system.md
- **title**：Editions 特性系统
- **覆盖事实**：F-CPP-055、F-CPP-056、F-CPP-063、F-CPP-064、F-CPP-065、F-CPP-066、F-CPP-067、F-CPP-068、F-CPP-138、F-CPP-139、F-CMP-014、F-CMP-017、F-CMP-027、F-CMP-037、F-CMP-040、F-CMP-041、F-CMP-042、F-CMP-043、F-CMP-057、F-CMP-068、F-CMP-075、F-CMP-080、F-CMP-084、F-CMP-085、F-CMP-086、F-CMP-087、F-CMP-088、F-CMP-090、F-TST-066、F-TST-067、F-TST-068、F-TST-069、F-TST-070、F-TST-071、F-TST-072、F-TST-073、F-REPO-054、F-REPO-055、F-REPO-049
- **内容范围**：一句话：Edition 8 值枚举与 FeatureSet/FeatureSetDefaults 的数据模型、feature_resolver 解析链、编译器与 9 个生成器的 edition 协商矩阵（GetMinimumEdition=PROTO2 / GetMaximumEdition=2026 与 RBSGenerator 例外）、editions/ 目录的 compile_edition_defaults/embed_edition_defaults 规则与 56 个 codegen_tests 的前缀分组——洞察 4 的展开。

### 16-wkt-conformance-benchmarks.md
- **title**：公共契约层：Well-Known Types、Conformance 与 Benchmarks
- **覆盖事实**：F-CPP-126、F-CPP-127、F-CPP-128、F-CPP-129、F-CPP-130、F-CPP-131、F-CPP-132、F-CPP-133、F-CPP-134、F-CPP-135、F-CPP-136、F-CPP-137、F-REPO-004、F-REPO-048、F-TST-001、F-TST-002、F-TST-003、F-TST-004、F-TST-005、F-TST-006、F-TST-007、F-TST-008、F-TST-009、F-TST-010、F-TST-011、F-TST-012、F-TST-013、F-TST-014、F-TST-015、F-TST-016、F-TST-017、F-TST-018、F-TST-019、F-TST-020、F-TST-021、F-TST-022、F-TST-023、F-TST-024、F-TST-025、F-TST-026、F-TST-027、F-TST-028、F-TST-029、F-TST-030、F-TST-031、F-TST-032、F-TST-033、F-TST-034、F-TST-035、F-TST-036、F-TST-037、F-TST-038、F-TST-039、F-TST-040、F-TST-041、F-TST-042、F-TST-043、F-TST-044、F-TST-045、F-TST-046、F-TST-047、F-TST-048、F-TST-049、F-TST-076、F-TST-079、F-TST-080
- **内容范围**：一句话：WKT 全家族（Any/Duration/Timestamp/Struct/Wrapper/Type/Api/FieldMask/Empty/CppFeatures）与顶层 40 个 BUILD alias，conformance 的 ConformanceTestRunner/Testee/TestManager 三层框架、failure list 三级 trie 与 19 语言清单、Bazel/CMake 双构建入口，benchmarks 的 BM_* 函数族与 descriptor_sv.proto STRING_PIECE 变体。

**主仓顶层目录覆盖核对**（18 个必须目录 → 归属概念篇）：src→01-06/07-10；python→11；rust→12；upb、upb_generator→12；hpb、hpb_generator→13；java、csharp、objectivec、php、ruby、lua→14；editions→15；conformance、benchmarks→16；examples→第三部分 examples/ 清单；docs→00（F-REPO-056~059）；bazel→00（F-REPO-050/053）；cmake→00（F-REPO-034~036）；go→00（F-REPO-021）。✓ 全覆盖。

---

# 第三部分：examples/ 文档清单（5 篇）

基于 examples/addressbook 教程（F-TST-050~065、F-REPO-060），按"schema → 单语言 → 多语言 → 构建"递进。

### 01-addressbook-proto.md
- **title**：addressbook.proto：入门 schema 解析
- **覆盖事实**：F-TST-050、F-TST-051、F-REPO-060
- **内容范围**：一句话：proto3 语法下 Person/AddressBook 消息、PhoneNumber/PhoneType 嵌套、Timestamp WKT 引用与 5 语言文件级 option（java_package/csharp_namespace/go_package）的逐字段讲解。

### 02-cpp-tutorial.md
- **title**：C++ 教程：add_person 与 list_people
- **覆盖事实**：F-TST-054、F-TST-055、F-TST-061、F-TST-062、F-TST-064
- **内容范围**：一句话：tutorial::Person 的 setter/mutable/add API、ParseFromIstream/SerializeToOstream 文件 IO、GOOGLE_PROTOBUF_VERIFY_VERSION 与 ShutdownProtobufLibrary 生命周期、TimeUtil::SecondsToTimestamp 的 WKT 用法及 pkg-config/CMake 双构建方式。

### 03-python-tutorial.md
- **title**：Python 教程：add_person 与 list_people
- **覆盖事实**：F-TST-052、F-TST-053、F-TST-062、F-TST-064
- **内容范围**：一句话：addressbook_pb2 动态模块加载、people.add()/phones.add() 容器追加、ParseFromString/SerializeToString、枚举常量 Person.MOBILE/HOME/WORK 比较与 pip install protobuf 运行路径。

### 04-java-ruby-dart-tutorials.md
- **title**：Java、Ruby 与 Dart 教程
- **覆盖事实**：F-TST-056、F-TST-057、F-TST-058、F-TST-059、F-TST-060、F-TST-062、F-TST-063
- **内容范围**：一句话：Java 的 newBuilder/mergeFrom/writeTo builder 模式与 Timestamps.now()，Ruby 的 Tutorial::Person.new/encode/decode 与符号枚举（含 add_person.rb 源码原文 `newlD()` 拼写事实），Dart 的 fromBuffer/writeToBuffer 与 ..number 级联语法。

### 05-examples-build-systems.md
- **title**：examples 构建体系与多语言互操作
- **覆盖事实**：F-TST-061、F-TST-062、F-TST-063、F-TST-064、F-TST-065、F-REPO-060
- **内容范围**：一句话：CMake（find_package + protobuf_generate + foreach 循环生成 add_person_cpp/list_people_cpp）、Makefile（protoc_middleman 多语言 --*_out 与 go_opt=paths=source_relative）、Bazel（bazel build :all）、pubspec/go 子目录四套构建入口，及"add_person_java 写入、list_people_python 读取"的跨语言互操作演示（F-TST-063 README 原句）。

---

# 第四部分：protobuf-ci 束文档清单（5 篇 concepts + 1 篇 references）

独立知识束，主题：protocolbuffers/protobuf-ci 仓库（9 个 composite action + 7 个 internal action）。编号即阅读顺序。

### 01-repo-positioning-and-structure.md
- **title**：仓库定位与结构：可复用 CI 动作集合
- **覆盖事实**：F-CI-001、F-CI-002、F-CI-003、F-CI-004、F-CI-005、F-CI-006、F-CI-007、F-CI-052、F-CI-053、F-CI-054、F-CI-055、F-CI-056
- **内容范围**：一句话：9 顶层 action + 7 internal action 的目录全景、"多仓库复用须 release"的版本纪律（@v6 固定 tag 引用）、主仓 14 个 workflow 的引用计数矩阵（test_cpp.yml 28 处居首）与 Apache-2.0/CLA 治理。

### 02-bazel-build-actions.md
- **title**：bazel 与 bazel-docker 构建动作及远程缓存
- **覆盖事实**：F-CI-011、F-CI-012、F-CI-013、F-CI-014、F-CI-015、F-CI-016、F-CI-017、F-CI-018、F-CI-019、F-CI-020、F-CI-040、F-CI-041、F-CI-049、F-CI-050
- **内容范围**：一句话：宿主机 bazel 与容器内 bazel-docker 两条执行路径的步骤对比（gcloud-auth → setup-runner → bazel-setup）、bazelisk 跨 OS 缓存路径、BAZEL_FLAGS 拼装与 repository_cache 挂载、GCS 远程缓存 `protobuf-bazel-cache` 与 pull_request_target 禁写策略、repository-cache save/restore 配对（~500 MB 上限）。

### 03-ccache-sccache-actions.md
- **title**：ccache 与 sccache 编译缓存动作
- **覆盖事实**：F-CI-021、F-CI-022、F-CI-023、F-CI-024、F-CI-025、F-CI-036、F-CI-037、F-CI-038、F-CI-039、F-CI-042、F-CI-043、F-CI-047
- **内容范围**：一句话：ccache 的环境变量全家桶（BASEDIR/DIR/COMPRESS/SLOPPINESS/DIRECT 与 modules 追加项）、三级 restore-keys 回退链、Windows 专属安装器（msvc-dev-cmd + zip 下载 + COMPILERTYPE=msvc + 300M 上限），sccache 的 GCS 桶配置（SCCACHE_GCS_BUCKET=protobuf-sccache、RW 模式引用 mozilla/sccache#1886）与 docker-run 的 sccache 参数透传。

### 04-docker-checkout-bash-actions.md
- **title**：docker、checkout、bash 基础动作与 internal 基建
- **覆盖事实**：F-CI-008、F-CI-009、F-CI-010、F-CI-026、F-CI-027、F-CI-033、F-CI-034、F-CI-035、F-CI-044、F-CI-045、F-CI-046、F-CI-048、F-CI-051
- **内容范围**：一句话：非 Bazel 的 docker/bash 执行封装（staleness 检查 + DOCKER_RUN_FLAGS 拼接）、checkout 的 submodule 三连命令与 nick-fields/retry 重试、internal/docker-run 的 fork PR 安全拦截（release 镜像禁用）、gcloud-auth 凭据链与 setup-runner 的 Windows d2u 行尾修复。

### 05-composer-cross-compile-actions.md
- **title**：composer-setup 与 cross-compile-protoc 专项动作
- **覆盖事实**：F-CI-028、F-CI-029、F-CI-030、F-CI-031、F-CI-032
- **内容范围**：一句话：PHP composer 依赖缓存（pull_request_target 只读缓存 + COMPOSER_HOME）与 chmod 777 权限修复；cross-compile-protoc 复用 bazel-docker 构建 `//:protoc_static --config={architecture}` 并输出 $PROTOC 环境变量。

**9 个顶层 action 覆盖核对**：bash→04；bazel→02；bazel-docker→02；ccache→03；checkout→04；composer-setup→05；cross-compile-protoc→05；docker→04；sccache→03。internal 7 个：bazel-setup→02；ccache-setup-windows→03；docker-run→04；gcloud-auth→04；repository-cache-restore/save→02；setup-runner→04。✓ 全覆盖。

---

# 第五部分：两束 references/ 信源登记文件清单

## protobuf 束 references/（5 个信源文件，按 R 阶段事实文件主题划分）

### references/repo-structure.md
- **登记范围**：仓库根目录结构、版本常量与双构建系统（F-REPO-001~067 的信源）。
- **源码路径清单**（相对 protobuf 主仓根）：
  - 仓库根（32 目录 + 顶层文件清单：BUILD.bazel、CMakeLists.txt、MODULE.bazel、WORKSPACE、WORKSPACE.bzlmod、protobuf_version.bzl、protobuf_deps.bzl、protobuf_release.bzl、protobuf.bzl、version.json、.bazelrc、bazel9.bazelrc 等）
  - protobuf_version.bzl、version.json、CMakeLists.txt、MODULE.bazel、WORKSPACE、WORKSPACE.bzlmod、.bazelrc、顶层 BUILD.bazel
  - cmake/（20 个 .cmake + 4 个 .in + 4 个 golden 清单）
  - bazel/（8 个 .bzl 与 common/flags/private/tests/toolchains 子目录）、build_defs/（9 文件）、toolchain/（4 文件）
  - editions/（defaults.bzl、BUILD、codegen_tests/、golden/、input/）
  - docs/（7 个 .md 与 csharp/、design/、upb/ 子目录）
  - editors/、ci/、compatibility/（smoke/、v3.25.0/）、pkg/、third_party/、patches/、go/

### references/cpp-core.md
- **登记范围**：C++ 运行时核心（F-CPP-001~144 的信源）。
- **源码路径清单**（相对 src/google/protobuf/）：
  - message_lite.h、message.h、arena.h、arenastring.h
  - descriptor.h、descriptor.pb.h、descriptor.proto、descriptor_database.h、descriptor_lite.h
  - wire_format_lite.h、wire_format.h
  - io/coded_stream.h、io/zero_copy_stream.h、io/zero_copy_stream_impl_lite.h
  - text_format.h、json/（json.cc/json.h 与 internal/ 子目录）、util/json_util.h
  - map.h、repeated_field.h、repeated_ptr_field.h、unknown_field_set.h、extension_set.h
  - class_data.h、generated_message_reflection.h、feature_resolver.h、port_def.inc
  - WKT 文件：any.proto、any.h、duration.proto、timestamp.proto、struct.proto、wrappers.proto、type.proto、api.proto、source_context.proto、field_mask.proto、empty.proto、cpp_features.proto、any_test.proto

### references/compiler.md
- **登记范围**：protoc 编译器（F-CMP-001~090 的信源）。
- **源码路径清单**（相对 src/google/protobuf/compiler/）：
  - main.cc、main_no_generators.cc
  - command_line_interface.h、command_line_interface.cc
  - parser.h、parser.cc、importer.h
  - code_generator.h、code_generator_lite.h、plugin.h、plugin.cc、plugin.proto、plugin.pb.h
  - cpp/（generator.h、cpp_generator.h、file.h、helpers.h、options.h、parse_function_generator.h、field.h、enum.h、extension.h、message.h、service.h、ifndef_guard.h、namespace_printer.h、message_layout_helper.h、tracker.h 与 field_generators/ 子目录）
  - java/（generator.h、java_generator.h、generator.cc、shared_code_generator.h、name_resolver.h、context.h 与 full/、lite/ 子目录）
  - python/（generator.h、python_generator.h、pyi_generator.h、plugin_main.cc、names.h、helpers.h）
  - csharp/（csharp_generator.h、csharp_helpers.h、csharp_field_base.h 等 19 个 .h）
  - objectivec/generator.h、php/php_generator.h、ruby/ruby_generator.h、ruby/rbs_generator.h、rust/generator.h、rust/context.h、kotlin/generator.h

### references/runtimes.md
- **登记范围**：多语言运行时（F-RT-001~105 的信源）。
- **源码路径清单**（相对 protobuf 主仓根）：
  - python/（protobuf.c、protobuf.h、descriptor.c/.h、descriptor_pool.c/.h、descriptor_containers.c/.h、message.c/.h、map.c/.h、repeated.c/.h、unknown_fields.c/.h、convert.c/.h、buffer_convert.c/.h、extension_dict.c/.h、python_api.h、version_script.lds、internal.bzl、build_targets.bzl、dist/setup.py、requirements.txt、google/protobuf/__init__.py、google/__init__.py、dist/ 子目录）
  - rust/（protobuf.rs、protobuf_lite.rs、proxied.rs、singular.rs、repeated.rs、map.rs、enum.rs、extension.rs、codegen_traits.rs、string.rs、primitive.rs、shared.rs、prelude.rs、internal.rs、cord.rs、defs.bzl、dist.bzl、rules.bzl、upb/lib.rs、upb/arena.rs、upb/message.rs、upb/wire.rs、upb/sys/lib.rs、upb/sys/upb_api.c、upb_kernel/、cpp_kernel/、release_crates/、test/）
  - hpb/（hpb.h、arena.h、multibackend.h、ptr.h、repeated_field.h、extension.h/.cc、status.h/.cc、options.h、requires.h、backend/cpp/、backend/upb/、internal/、bazel/hpb_proto_library.bzl）
  - hpb_generator/（generator.h/.cc、protoc-gen-hpb.cc、context.h、gen_accessors.h/.cc、gen_enums.h/.cc、gen_extensions.h/.cc、gen_messages.h/.cc、gen_repeated_fields.h/.cc、gen_utils.h/.cc、keywords.h/.cc、names.h/.cc、tests/）
  - java/（BUILD.bazel、lite.md 与 core/lite/kotlin/kotlin-lite/util/protoc 子目录布局）
  - csharp/（src/Google.Protobuf/ 文件清单与 Reflection/、WellKnownTypes/ 子目录、keys/、protos/）
  - objectivec/（GPBMessage.h、GPBDescriptor.h、GPBArray.h、GPBDictionary.h、GPBWireFormat.h、GPBRootObject.h、GPBCodedInputStream.h、GPBCodedOutputStream.h、GPBExtensionRegistry.h、GPBUnknownFields.h 与 GPB*.pbobjc.h 生成文件、DevTools/）
  - php/（composer.json、ext/google/protobuf/（php-upb.c/.h、arena.c、array.c、map.c、message.c、def.c、convert.c、names.c、config.m4、config.w32、wkt.inc）、src/Google/Protobuf/、tests/）
  - ruby/（lib/google/protobuf.rb、lib/google/（protobuf_ffi.rb、protobuf_native.rb、ffi/ 子目录）、ext/google/protobuf_c/（ruby-upb.c/.h、defs.c、message.c、map.c、repeated_field.c、convert.c、glue.c）、tests/、defs.bzl）
  - lua/（upb.c、upb.h、upbc.cc、upb.lua、def.c、msg.c、main.c、test_upb.lua、test.proto、lua_proto_library.bzl）

### references/testing.md
- **登记范围**：测试与规范体系（F-TST-001~080 的信源）。
- **源码路径清单**（相对 protobuf 主仓根）：
  - conformance/（README.md、conformance.proto、conformance_test_runner.cc、conformance_test.cc/.h、conformance_test_main.cc、test_runner.h、testee.h/.cc、test_manager.h/.cc、naming.h、failure_list_trie_node.cc/.h、binary_json_conformance_suite.cc/.h、text_format_conformance_suite.cc/.h、binary_wireformat.cc/.h、fork_pipe_runner.cc/.h、defs.bzl、BUILD、bazel_conformance_test_runner.sh、conformance_cpp.cc、conformance_objc.m、conformance_php.php、conformance_python.py、conformance_rust.rs、ConformanceJava.java、ConformanceJavaLite.java、update_failure_list.py、failure_list_*.txt 全 19 个、text_format_failure_list_*.txt 全 8 个、ruby/、test_protos/）
  - benchmarks/（BUILD、build_defs.bzl、benchmark.cc、compare.py、descriptor.proto、descriptor_sv.proto、empty.proto、gen_protobuf_binary_cc.py、gen_synthetic_protos.py、gen_upb_binary_c.py）
  - examples/（addressbook.proto、add_person.cc/.py/.rb/.dart、list_people.cc/.py/.rb/.dart、AddPerson.java、ListPeople.java、CMakeLists.txt、Makefile、BUILD.bazel、MODULE.bazel、README.md、pubspec.yaml）
  - editions/（defaults.bzl、defaults_test.cc、edition_defaults_test_utils.cc/.h、generated_files_test.cc、generated_reflection_test.cc、internal_defaults_escape.cc、BUILD、4 个 .h.template、codegen_tests/）
  - ci/（README.md、clang_wrapper、clang_wrapper++、python_compatibility.sh、push_auto_update.sh）
  - cmake/tests.cmake、editors/（proto.vim、protobuf-mode.el、README.txt）

## protobuf-ci 束 references/（1 个信源文件）

### references/protobuf-ci-actions.md
- **登记范围**：protobuf-ci 仓库全部 9 个顶层 action、7 个 internal action 与顶层文档（F-CI-001~056 的信源）。
- **源码路径清单**（相对 protobuf-ci 仓库根）：
  - README.md、CONTRIBUTING.md、LICENSE
  - bash/action.yml
  - bazel/action.yml
  - bazel-docker/action.yml
  - ccache/action.yml
  - checkout/action.yml
  - composer-setup/action.yml
  - cross-compile-protoc/action.yml
  - docker/action.yml
  - sccache/action.yml
  - internal/bazel-setup/action.yml
  - internal/ccache-setup-windows/action.yml
  - internal/docker-run/action.yml
  - internal/gcloud-auth/action.yml
  - internal/repository-cache-restore/action.yml
  - internal/repository-cache-save/action.yml
  - internal/setup-runner/action.yml
  - 信源补充（主仓侧交叉验证，对应 F-CI-052~056）：protobuf 主仓 .github/workflows/ 目录下 24 个 yaml 中引用 protobuf-ci 的 14 个文件（staleness_check.yml、test_bazel.yml、test_cpp.yml、test_csharp.yml、test_hpb.yml、test_java.yml、test_objectivec.yml、test_php_ext.yml、test_php.yml、test_python.yml、test_ruby.yml、test_rust.yml、test_upb.yml、test_yaml.yml）

---

## 统计汇总（供 D 阶段排产）

| 维度 | 数量 | 明细 |
|---|---|---|
| 核心洞察 | 5 条 | 双内核架构 / descriptor 单一事实源 / 生成器统一接口 / Editions 特性系统 / 双构建系统 × CI 分层缓存 |
| protobuf 束 concepts/ | 17 篇 | 入门 3（00-02）+ 核心机制 4（03-06）+ 编译器 4（07-10）+ 运行时 4（11-14）+ 高级 2（15-16） |
| protobuf 束 examples/ | 5 篇 | 01-addressbook-proto / 02-cpp / 03-python / 04-java-ruby-dart / 05-build-systems |
| protobuf-ci 束 concepts/ | 5 篇 | 01 定位结构 / 02 bazel 动作 / 03 ccache-sccache / 04 docker-checkout-bash / 05 composer-cross-compile |
| protobuf 束 references/ | 5 个信源文件 | repo-structure.md / cpp-core.md / compiler.md / runtimes.md / testing.md |
| protobuf-ci 束 references/ | 1 个信源文件 | protobuf-ci-actions.md（登记 17 个 action 路径 + 主仓 14 个 workflow 交叉验证） |

**质量门自检**：① 5 条洞察四元组（陈述/证据/反常识/行动）齐备，每条证据均跨 2 份以上事实文件；② 知识地图 17 篇的事实编号均已对照 6 份 facts 文件逐一核验（F-REPO ≤067、F-CPP ≤144、F-CMP ≤090、F-RT ≤105、F-TST ≤080、F-CI ≤056 区间内真实存在）；③ 主仓 18 个必覆盖顶层目录 + protobuf-ci 9 个顶层 action + 7 个 internal action 均已映射到具体文档。
