# protoc 编译器事实清单（R阶段）

> 范围：protobuf 主仓 `d:\spaces\SpecWeave\external\libs\protocolbuffers\protobuf\src\google\protobuf\compiler`（只读）及其子目录（cpp/、java/、python/、csharp/、objectivec/、php/、ruby/、rust/、kotlin/）。零推测，仅记录源码中客观存在的类定义、继承关系、方法签名、proto 字段定义与文件存在性。签名均从源码抄录核对。源码根相对路径统一省略前缀 `src/google/protobuf/compiler/`。

## 一、入口（main.cc / main_no_generators.cc）

F-CMP-001: main.cc 在 `namespace google::protobuf::compiler` 内定义 `int ProtobufMain(int argc, char* argv[])`；非 MSVC 平台的 `int main(int argc, char* argv[])` 主体为 `return google::protobuf::compiler::ProtobufMain(argc, argv);` —— main.cc L41-121、L148-150

F-CMP-002: main.cc 中 ProtobufMain 主体：`absl::InitializeLog();`、`CommandLineInterface cli;`、`cli.AllowPlugins("protoc-");`，并在 `#ifdef GOOGLE_PROTOBUF_RUNTIME_INCLUDE_BASE` 分支调用 `cli.set_opensource_runtime(true)` —— main.cc L46-52

F-CMP-003: main.cc 通过 `cli.RegisterGenerator(flag, opt_flag, &generator, help)` 注册的生成器与 flag 对（逐一抄录）：`--cpp_out`/`--cpp_opt`（`cpp::CppGenerator cpp_generator`）、`--java_out`/`--java_opt`（`java::JavaGenerator java_generator`）、`--kotlin_out`/`--kotlin_opt`（`kotlin::KotlinGenerator kt_generator`）、`--python_out`/`--python_opt`（`python::Generator py_generator`）、`--pyi_out`（单 flag 注册，`python::PyiGenerator pyi_generator`）、`--php_out`/`--php_opt`（`php::Generator php_generator`）、`--ruby_out`/`--ruby_opt`（`ruby::Generator rb_generator`）、`--rbs_out`/`--rbs_opt`（`ruby::RBSGenerator rbs_generator`）、`--csharp_out`/`--csharp_opt`（`csharp::Generator csharp_generator`）、`--objc_out`/`--objc_opt`（`objectivec::ObjectiveCGenerator objc_generator`）、`--rust_out`/`--rust_opt`（`rust::RustGenerator rust_generator`）—— main.cc L55-116

F-CMP-004: main.cc 中 `#ifdef _MSC_VER` 分支的 main() 使用 `CommandLineToArgvW(GetCommandLineW(), &argc)` 与辅助函数 `std::string ToMultiByteUtf8String(const wchar_t* input)`（内部调用 WideCharToMultiByte(CP_UTF8, ...)）将宽字符参数转为多字节后传给 ProtobufMain —— main.cc L127-151

F-CMP-005: main_no_generators.cc 定义 `int ProtocMain(int argc, char* argv[])`（注释原句："This is a version of protoc that has no built-in code generators."），主体仅有 `absl::InitializeLog(); CommandLineInterface cli; cli.AllowPlugins("protoc-"); return cli.Run(argc, argv);`，不注册任何内置生成器 —— main_no_generators.cc L19-36

## 二、command_line_interface.h / command_line_interface.cc

F-CMP-006: `class PROTOC_EXPORT CommandLineInterface`：拷贝构造与拷贝赋值均 `= delete`，公有静态成员 `static const char* const kPathSeparator;` —— command_line_interface.h L102-109

F-CMP-007: RegisterGenerator 两个重载签名：`void RegisterGenerator(const std::string& flag_name, CodeGenerator* generator, const std::string& help_text);` 与 `void RegisterGenerator(const std::string& flag_name, const std::string& option_flag_name, CodeGenerator* generator, const std::string& help_text);` —— command_line_interface.h L127-141

F-CMP-008: `void AllowPlugins(const std::string& exe_name_prefix);`（头文件注释说明插件可执行文件命名规则：exe_name_prefix + flag 名去掉 "_out"，如前缀 "protoc-" 加 `--foo_out` 对应程序 "protoc-gen-foo"）—— command_line_interface.h L179

F-CMP-009: `int Run(int argc, const char* const argv[]);` 声明于 command_line_interface.h L186，实现位于 command_line_interface.cc L1316（`int CommandLineInterface::Run(int argc, const char* const argv[])`，首先调用 `Clear()`，随后 switch ParseArguments 返回值）—— command_line_interface.cc L1316-1326

F-CMP-010: 私有枚举 `enum ParseArgumentStatus { PARSE_ARGUMENT_DONE_AND_CONTINUE, PARSE_ARGUMENT_DONE_AND_EXIT, PARSE_ARGUMENT_FAIL };`；相关私有方法签名：`ParseArgumentStatus ParseArguments(int argc, const char* const argv[]);`（实现 .cc L1982）、`bool ParseArgument(const char* arg, std::string* name, std::string* value);`（实现 .cc L2149）、`ParseArgumentStatus InterpretArgument(const std::string& name, const std::string& value);`（实现 .cc L2213）、`bool ExpandArgumentFile(const char* file, std::vector<std::string>* arguments);` —— command_line_interface.h L233-262

F-CMP-011: `struct TransitiveDependencyOptions { bool include_json_name = false; bool include_source_code_info = false; bool retain_options = false; bool skip_dependencies = false; };` —— command_line_interface.h L57-62

F-CMP-012: 私有枚举：`enum Mode { MODE_COMPILE, MODE_ENCODE, MODE_DECODE, MODE_PRINT };`（成员默认 `Mode mode_ = MODE_COMPILE;`）、`enum PrintMode { PRINT_NONE, PRINT_FREE_FIELDS };`、`enum ErrorFormat { ERROR_FORMAT_GCC, ERROR_FORMAT_MSVS };`（成员默认 `error_format_ = ERROR_FORMAT_GCC;`）—— command_line_interface.h L418-439

F-CMP-013: command_line_interface.cc 中 ParseArgument 判定"不带值"的 flag 全集（原文抄录）：`-h`、`--help`、`--disallow_services`、`--include_imports`、`--include_source_info`、`--retain_options`、`--version`、`--decode_raw`、`--notices`、`--experimental_editions`、`--print_free_field_numbers`、`--experimental_allow_proto3_optional`、`--deterministic_output`、`--unsafe_allow_out_dir_escape`、`--fatal_warnings` —— command_line_interface.cc L2193-2202

F-CMP-014: command_line_interface.cc 中 InterpretArgument 处理的带值参数（`name ==` 比较全集）：`-I` / `--proto_path`、`--direct_dependencies`、`--direct_dependencies_violation_msg`、`--option_dependencies`、`--option_dependencies_violation_msg`、`--descriptor_set_in`、`-o` / `--descriptor_set_out`、`--dependency_out`、`--include_imports`、`--include_source_info`、`--retain_options`、`-h` / `--help`、`--version`、`--disallow_services`、`--unsafe_allow_out_dir_escape`、`--encode`、`--decode`、`--decode_raw`、`--deterministic_output`、`--error_format`、`--fatal_warnings`、`--plugin`、`--print_free_field_numbers`、`--enable_codegen_trace`、`--notices`、`--experimental_editions`、`--edition_defaults_out`、`--edition_defaults_minimum`、`--edition_defaults_maximum`、`--experimental_allow_proto3_optional`（该 flag 处理体为空，注释原句 "Flag is no longer observed, but we allow it for backward compat."）—— command_line_interface.cc L2256-2600

F-CMP-015: `--error_format` 取值处理：`value == "gcc"` 置 `error_format_ = ERROR_FORMAT_GCC`，`value == "msvs"` 置 `ERROR_FORMAT_MSVS`，其他值报 "Unknown error format" 并返回 PARSE_ARGUMENT_FAIL —— command_line_interface.cc L2475-2483

F-CMP-016: `--plugin` 处理：按第一个 `=` 拆分为 plugin_name 与 path；无 `=` 时取路径 basename 作为 plugin_name；结果写入 `plugins_[plugin_name] = path;`（`absl::flat_hash_map<std::string, std::string> plugins_`）；`plugin_prefix_` 为空时报 "This compiler does not support plugins." —— command_line_interface.cc L2491-2515

F-CMP-017: CommandLineInterface 私有方法签名（部分抄录）：`CodeGeneratorRequest CreateCodeGeneratorRequest(std::vector<const FileDescriptor*> parsed_files, std::string parameter, bool copy_json_name = false, bool bootstrap = false) const;`、`bool GenerateCodeFromResponse(const CodeGeneratorResponse& response, GeneratorContext* generator_context, bool bootstrap, std::string plugin_name, std::string* error);`、`bool GenerateOutput(...)`、`bool GeneratePluginOutput(...)`、`bool GenerateBuiltInOutput(...)`、`bool EncodeOrDecode(const DescriptorPool* pool);`、`bool WriteDescriptorSet(const std::vector<const FileDescriptor*>& parsed_files);`、`bool WriteEditionDefaults(const DescriptorPool& pool);`、`bool GenerateDependencyManifestFile(...)`、`void PrintFreeFieldNumbers(const Descriptor* descriptor);`、`void GetTransitiveDependencies(const FileDescriptor* file, absl::flat_hash_set<const FileDescriptor*>* already_seen, RepeatedPtrField<FileDescriptorProto>* output, const TransitiveDependencyOptions& options = TransitiveDependencyOptions()) const;`、`void GetTransitiveOptionDependencies(...)`、`bool EnforceProto3OptionalSupport(const std::string& codegen_name, uint64_t supported_features, const std::vector<const FileDescriptor*>& parsed_files) const;`、`bool EnforceEditionsSupport(const std::string& codegen_name, uint64_t supported_features, Edition minimum_edition, Edition maximum_edition, const std::vector<const FileDescriptor*>& parsed_files) const;`、`bool SetupFeatureResolution(DescriptorPool& pool);` —— command_line_interface.h L279-371

F-CMP-018: `struct OutputDirective { std::string name; CodeGenerator* generator; std::string parameter; std::string output_location; };`（注释示例 name 为 "--foo_out"，generator 对插件为 NULL）；存储成员 `std::vector<OutputDirective> output_directives_;` —— command_line_interface.h L467-475

F-CMP-019: `struct GeneratorInfo { std::string flag_name; std::string option_flag_name; CodeGenerator* generator; std::string help_text; };`；容器成员 `absl::btree_map<std::string, GeneratorInfo> generators_by_flag_name_;`、`absl::flat_hash_map<std::string, GeneratorInfo> generators_by_option_name_;`、`absl::flat_hash_map<std::string, std::string> generator_parameters_;`、`absl::flat_hash_map<std::string, std::string> plugin_parameters_;`、`absl::flat_hash_map<std::string, std::vector<std::string>> plugin_command_prefixes_;` —— command_line_interface.h L383-415

F-CMP-020: 公有内联方法：`void SetInputsAreProtoPathRelative(bool) {}`（标注 DEPRECATED、空实现）、`void SetVersionInfo(const std::string& text) { version_info_ = text; }`、`void set_opensource_runtime(bool opensource) { opensource_runtime_ = opensource; }` —— command_line_interface.h L188-203

## 三、parser.h / parser.cc

F-CMP-021: `class PROTOBUF_EXPORT Parser final`（无基类），公有方法 `bool Parse(io::Tokenizer* input, FileDescriptorProto* file);` —— parser.h L52-61

F-CMP-022: parser.h 中不存在名为 SyntaxError 的类；在整个 compiler/ 目录 grep "SyntaxError" 仅命中两处测试名：importer_unittest.cc L641 `TEST_F(SourceTreeDescriptorDatabaseTest, ExtensionDeclarationsSyntaxError)` 与 parser_unittest.cc L2226 `TEST_F(ParseErrorTest, SimpleSyntaxError)` —— parser.h（全文核验）+ importer_unittest.cc L641 + parser_unittest.cc L2226

F-CMP-023: Parser 公有方法（抄录）：`void RecordSourceLocationsTo(SourceLocationTable* location_table)`、`void RecordErrorsTo(io::ErrorCollector* error_collector)`、`absl::string_view GetSyntaxIdentifier()`、`void SetRequireSyntaxIdentifier(bool value)`、`void SetStopAfterSyntaxIdentifier(bool value)` —— parser.h L72-104

F-CMP-024: Parser 私有嵌套类 `class PROTOBUF_EXPORT LocationRecorder`：构造函数 5 个重载（`LocationRecorder(Parser*)`、`LocationRecorder(const LocationRecorder&)`、`LocationRecorder(const LocationRecorder&, int path1)`、`LocationRecorder(const LocationRecorder&, int path1, int path2)`、`LocationRecorder(const LocationRecorder&, int path1, SourceCodeInfo*)`）；方法 `void AddPath(int path_component)`、`void StartAt(const io::Tokenizer::Token&)`、`void StartAt(const LocationRecorder&)`、`void EndAt(const io::Tokenizer::Token&)`、`void RecordLegacyLocation(const Message*, DescriptorPool::ErrorCollector::ErrorLocation)`、`void RecordLegacyImportLocation(const Message*, const std::string&)`、`int CurrentPathSize() const`、`void AttachComments(std::string*, std::string*, std::vector<std::string>*) const` —— parser.h L246-313

F-CMP-025: Parser 私有方法签名（语言构件解析，部分抄录）：`bool ParseSyntaxIdentifier(const FileDescriptorProto*, const LocationRecorder&)`、`bool ParseTopLevelStatement(FileDescriptorProto*, const LocationRecorder&)`、`bool ParseMessageDefinition(DescriptorProto*, const SymbolVisibility&, const LocationRecorder&, const FileDescriptorProto*)`、`bool ParseEnumDefinition(EnumDescriptorProto*, const SymbolVisibility&, const LocationRecorder&, const FileDescriptorProto*)`、`bool ParseServiceDefinition(ServiceDescriptorProto*, const LocationRecorder&, const FileDescriptorProto*)`、`bool ParsePackage(FileDescriptorProto*, const LocationRecorder&, const FileDescriptorProto*)`、`bool ParseImport(RepeatedPtrField<std::string>*, RepeatedPtrField<std::string>*, RepeatedField<int32_t>*, RepeatedField<int32_t>*, const LocationRecorder&, const FileDescriptorProto*)`、`bool ParseMessageField(FieldDescriptorProto*, RepeatedPtrField<DescriptorProto>*, const LocationRecorder&, int, const LocationRecorder&, const FileDescriptorProto*)`、`bool ParseMapType(MapField*, FieldDescriptorProto*, LocationRecorder&)`、`bool ParseOneof(OneofDescriptorProto*, DescriptorProto*, int, const LocationRecorder&, const LocationRecorder&, const FileDescriptorProto*)`、`bool ParseLabel(FieldDescriptorProto::Label*, const LocationRecorder&)`、`bool ParseType(FieldDescriptorProto::Type*, std::string*)`、`bool ParseOption(Message*, const LocationRecorder&, const FileDescriptorProto*, OptionStyle)`（`enum OptionStyle { OPTION_ASSIGNMENT, OPTION_STATEMENT };`）、`bool ParseUninterpretedBlock(std::string*)`、`bool ParseVisibility(const FileDescriptorProto*, SymbolVisibility*)` —— parser.h L321-540

F-CMP-026: Parser 私有 `struct MapField { bool is_map_field; FieldDescriptorProto::Type key_type; FieldDescriptorProto::Type value_type; std::string key_type_name; std::string value_type_name; MapField() : is_map_field(false) {} };` 与 `void GenerateMapEntry(const MapField&, FieldDescriptorProto*, RepeatedPtrField<DescriptorProto>* messages);` —— parser.h L542-556

F-CMP-027: Parser 私有内联 `bool DefaultToOptionalFields() const { if (syntax_identifier_ == "editions") return true; return syntax_identifier_ == "proto3"; }`；私有成员含 `Edition edition_ = Edition::EDITION_UNKNOWN;`、`bool limit_group_nesting_ = true;` —— parser.h L558-579

F-CMP-028: `class PROTOBUF_EXPORT SourceLocationTable`：方法 `bool Find(const Message*, DescriptorPool::ErrorCollector::ErrorLocation, int* line, int* column) const;`、`bool FindImport(const Message*, absl::string_view, int*, int*) const;`、`void Add(const Message*, DescriptorPool::ErrorCollector::ErrorLocation, int, int);`、`void AddImport(const Message*, const std::string&, int, int);`、`void Clear();`；私有 `using LocationMap = absl::flat_hash_map<std::pair<const Message*, DescriptorPool::ErrorCollector::ErrorLocation>, std::pair<int, int>>;` —— parser.h L601-635

## 四、importer.h

F-CMP-029: `class PROTOC_EXPORT SourceTreeDescriptorDatabase : public DescriptorDatabase`：构造 `SourceTreeDescriptorDatabase(SourceTree* source_tree)` 与 `SourceTreeDescriptorDatabase(SourceTree* source_tree, DescriptorDatabase* fallback_database)`；方法 `void RecordErrorsTo(MultiFileErrorCollector*)`、`DescriptorPool::ErrorCollector* GetValidationErrorCollector()`、`void AddExtensionDeclarationsFile(absl::string_view proto_file_name, absl::string_view message_name, absl::string_view declarations_file_name)`；override `bool FindFileByName(absl::string_view, FileDescriptorProto*)`、`bool FindFileContainingSymbol(absl::string_view, FileDescriptorProto*)`、`bool FindFileContainingExtension(absl::string_view, int, FileDescriptorProto*)` —— importer.h L59-110

F-CMP-030: SourceTreeDescriptorDatabase 私有嵌套类 `class PROTOC_EXPORT ValidationErrorCollector : public DescriptorPool::ErrorCollector`：override `void RecordError(absl::string_view filename, absl::string_view element_name, const Message* descriptor, ErrorLocation location, absl::string_view message)` 与 `void RecordWarning(...)` —— importer.h L122-141

F-CMP-031: `class PROTOC_EXPORT Importer`（无基类）：构造 `Importer(SourceTree* source_tree, MultiFileErrorCollector* error_collector)`；方法 `const FileDescriptor* Import(const std::string& filename);`、`const DescriptorPool* pool() const { return &pool_; }`、`void AddDirectInputFile(absl::string_view file_name, bool unused_import_is_error = false);`、`void ClearDirectInputFiles();`；私有成员 `SourceTreeDescriptorDatabase database_;` 与 `DescriptorPool pool_;` —— importer.h L159-193

F-CMP-032: `class PROTOC_EXPORT MultiFileErrorCollector`：纯虚 `virtual void RecordError(absl::string_view filename, int line, int column, absl::string_view message) = 0;`；带空默认实现的 `virtual void RecordWarning(absl::string_view filename, int line, int column, absl::string_view message) {}` —— importer.h L197-213

F-CMP-033: `class PROTOC_EXPORT SourceTree`：纯虚 `virtual io::ZeroCopyInputStream* Open(absl::string_view filename) = 0;`；虚 `virtual std::string GetLastErrorMessage();` —— importer.h L219-238

F-CMP-034: `class PROTOC_EXPORT DiskSourceTree : public SourceTree`（importer.h 中不存在名为 DiskFileSource 的类或嵌套类）：方法 `void MapPath(absl::string_view virtual_path, absl::string_view disk_path);`、`DiskFileToVirtualFileResult DiskFileToVirtualFile(absl::string_view disk_file, std::string* virtual_file, std::string* shadowing_disk_file);`（枚举 `enum DiskFileToVirtualFileResult { SUCCESS, SHADOWED, CANNOT_OPEN, NO_MAPPING };`）、`bool VirtualFileToDiskFile(absl::string_view virtual_file, std::string* disk_file);`、override `Open` 与 `GetLastErrorMessage`；私有 `struct Mapping { std::string virtual_path; std::string disk_path; };` 与 `std::vector<Mapping> mappings_;` —— importer.h L243-330

## 五、code_generator.h / code_generator_lite.h

F-CMP-035: `class PROTOC_EXPORT CodeGenerator`：纯虚 `virtual bool Generate(const FileDescriptor* file, const std::string& parameter, GeneratorContext* generator_context, std::string* error) const = 0;` —— code_generator.h L53-74

F-CMP-036: `virtual bool GenerateAll(const std::vector<const FileDescriptor*>& files, const std::string& parameter, GeneratorContext* generator_context, std::string* error) const;`（非纯虚，有默认实现）—— code_generator.h L87-90

F-CMP-037: `enum Feature { FEATURE_PROTO3_OPTIONAL = 1, FEATURE_SUPPORTS_EDITIONS = 2 };`（注释原句 "This must be kept in sync with plugin.proto."）；`virtual uint64_t GetSupportedFeatures() const { return 0; }` —— code_generator.h L95-103

F-CMP-038: `virtual bool HasGenerateAll() const { return true; }`，注释原句："This is no longer used, but this class is part of the opensource protobuf library, so it has to remain to keep vtables the same for the current version of the library." —— code_generator.h L105-109

F-CMP-039: `virtual std::vector<const FieldDescriptor*> GetFeatureExtensions() const { return {}; }` —— code_generator.h L115-117

F-CMP-040: `virtual Edition GetMinimumEdition() const { return Edition::EDITION_UNKNOWN; }` 与 `virtual Edition GetMaximumEdition() const { return Edition::EDITION_UNKNOWN; }` —— code_generator.h L121-125

F-CMP-041: `absl::StatusOr<FeatureSetDefaults> BuildFeatureSetDefaults() const;`（公有，非虚）—— code_generator.h L133

F-CMP-042: protected 静态模板方法：`template <typename DescriptorT> static const FeatureSet& GetResolvedSourceFeatures(const DescriptorT& desc)`（内部调用 `::google::protobuf::internal::InternalFeatureHelper::GetFeatures(desc)`）；`static auto GetResolvedSourceFeatureExtension(...)`；`static typename TypeTraitsT::ConstType GetUnresolvedSourceFeatures(...)`；`static Edition GetEdition(const FileDescriptor& file)` —— code_generator.h L140-176

F-CMP-043: constexpr 版本函数：`constexpr auto ProtocMinimumEdition() { return Edition::EDITION_PROTO2; }`、`constexpr auto ProtocMaximumEdition() { return Edition::EDITION_2026; }`、`constexpr auto MaximumKnownEdition() { return Edition::EDITION_2026; }` —— code_generator.h L180-187

F-CMP-044: `class PROTOC_EXPORT GeneratorContext`：纯虚 `virtual io::ZeroCopyOutputStream* Open(const std::string& filename) = 0;`；虚方法 `OpenForAppend(const std::string&)`、`OpenForInsert(const std::string& filename, const std::string& insertion_point)`、`OpenForInsertWithGeneratedCodeInfo(const std::string&, const std::string&, const google::protobuf::GeneratedCodeInfo&)`、`ListParsedFiles(std::vector<const FileDescriptor*>*)`、`GetCompilerVersion(Version*) const`；文件尾部 `typedef GeneratorContext OutputDirectory;` —— code_generator.h L193-245

F-CMP-045: 文件级导出函数 `PROTOC_EXPORT bool CanSkipEditionCheck(absl::string_view filename);` —— code_generator.h L248

F-CMP-046: code_generator_lite.h 不定义任何类；导出内容：`PROTOC_EXPORT void ParseGeneratorParameter(absl::string_view, std::vector<std::pair<std::string, std::string>>*);`、`PROTOC_EXPORT std::string StripProto(absl::string_view filename);`、`PROTOC_EXPORT bool IsKnownFeatureProto(absl::string_view filename);`、命名空间 generator_internal 内模板函数 `GetResolvedFeatureExtension(...)`、namespace internal 内 `PROTOC_EXPORT bool IsOss();` —— code_generator_lite.h L34-64

## 六、plugin.proto / plugin.pb.h

F-CMP-047: plugin.proto 头部：`syntax = "proto2";`、`package google.protobuf.compiler;`、`option java_package = "com.google.protobuf.compiler";`、`option java_outer_classname = "PluginProtos";`、`import "google/protobuf/descriptor.proto";`、`option csharp_namespace = "Google.Protobuf.Compiler";`、`option go_package = "google.golang.org/protobuf/types/pluginpb";` —— plugin.proto L21-30

F-CMP-048: message Version 完整字段：`optional int32 major = 1;`、`optional int32 minor = 2;`、`optional int32 patch = 3;`、`optional string suffix = 4;` —— plugin.proto L33-40

F-CMP-049: message CodeGeneratorRequest 完整字段：`repeated string file_to_generate = 1;`、`optional string parameter = 2;`、`repeated FileDescriptorProto proto_file = 15;`、`repeated FileDescriptorProto source_file_descriptors = 17;`、`optional Version compiler_version = 3;` —— plugin.proto L43-80

F-CMP-050: message CodeGeneratorResponse 完整字段：`optional string error = 1;`、`optional uint64 supported_features = 2;`、`optional int32 minimum_edition = 3;`、`optional int32 maximum_edition = 4;`、`repeated File file = 15;`；嵌套 `enum Feature { FEATURE_NONE = 0; FEATURE_PROTO3_OPTIONAL = 1; FEATURE_SUPPORTS_EDITIONS = 2; }` —— plugin.proto L83-115、L179

F-CMP-051: message CodeGeneratorResponse.File 完整字段：`optional string name = 1;`、`optional string insertion_point = 2;`、`optional string content = 15;`、`optional GeneratedCodeInfo generated_code_info = 16;` —— plugin.proto L118-178

F-CMP-052: plugin.pb.h 生成的四个消息类（均 `final : public ::google::protobuf::Message`）：`Version`（L127）、`CodeGeneratorResponse_File`（L382）、`CodeGeneratorResponse`（L651）、`CodeGeneratorRequest`（L950）；字段号常量与 plugin.proto 一致：CodeGeneratorRequest 的 `kFileToGenerateFieldNumber = 1`、`kProtoFileFieldNumber = 15`、`kParameterFieldNumber = 2`、`kCompilerVersionFieldNumber = 3`、`kSourceFileDescriptorsFieldNumber = 17`（L1102-1106）；CodeGeneratorResponse 的 `kFileFieldNumber = 15`、`kErrorFieldNumber = 1`、`kSupportedFeaturesFieldNumber = 2`、`kMinimumEditionFieldNumber = 3`、`kMaximumEditionFieldNumber = 4`（L820-824）；CodeGeneratorResponse_File 的 `kNameFieldNumber = 1`、`kInsertionPointFieldNumber = 2`、`kContentFieldNumber = 15`、`kGeneratedCodeInfoFieldNumber = 16`（L529-532）；Version 的 `kSuffixFieldNumber = 4`、`kMajorFieldNumber = 1`、`kMinorFieldNumber = 2`、`kPatchFieldNumber = 3`（L274-277）—— plugin.pb.h

F-CMP-053: plugin.pb.h 访问器（抄录示例）：CodeGeneratorResponse 的 `[[nodiscard]] ::uint64_t supported_features() const;`（L865）、`[[nodiscard]] ::int32_t minimum_edition() const;`（L876）；CodeGeneratorResponse_File 的 `[[nodiscard]] bool has_insertion_point() const;`、`[[nodiscard]] const ::std::string& insertion_point() const;`、`::std::string* PROTOBUF_NONNULL mutable_insertion_point();`（L551-556）、`[[nodiscard]] const ::google::protobuf::GeneratedCodeInfo& generated_code_info() const;`（L585）—— plugin.pb.h L551-594、L863-886

## 七、plugin.h / plugin.cc

F-CMP-054: plugin.h 导出两个函数签名：`PROTOC_EXPORT int PluginMain(int argc, char* argv[], const CodeGenerator* generator);` 与 `bool GenerateCode(const CodeGeneratorRequest& request, const CodeGenerator& generator, CodeGeneratorResponse* response, std::string* error_msg);` —— plugin.h L56-65

F-CMP-055: plugin.cc 实现位置：`bool GenerateCode(const CodeGeneratorRequest& request, ...)` 位于 L99，`int PluginMain(int argc, char* argv[], const CodeGenerator* generator)` 位于 L161 —— plugin.cc L99、L161

## 八、cpp/ 目录

F-CMP-056: cpp_generator.h 全文仅 `#include "google/protobuf/compiler/cpp/generator.h"`（无任何类定义）；C++ 生成器主类为 `class PROTOC_EXPORT CppGenerator final : public CodeGenerator`，定义于 cpp/generator.h L43 —— cpp/cpp_generator.h L8-13、cpp/generator.h L43

F-CMP-057: CppGenerator 成员（抄录）：`enum class Runtime { kGoogle3, kOpensource, kOpensourceGoogle3 };`、`void set_opensource_runtime(bool)`、`void set_runtime_include_base(std::string base)`、`bool Generate(...) const override;`、`bool GenerateAll(...) const override;`、`uint64_t GetSupportedFeatures() const override { return FEATURE_PROTO3_OPTIONAL | FEATURE_SUPPORTS_EDITIONS; }`、`Edition GetMinimumEdition() const override { return Edition::EDITION_PROTO2; }`、`Edition GetMaximumEdition() const override { return Edition::EDITION_2026; }`、`std::vector<const FieldDescriptor*> GetFeatureExtensions() const override { return {GetExtensionReflection(pb::cpp)}; }`、私有 `bool GenerateImpl(const FileDescriptor*, const std::string&, GeneratorContext*, std::string*, const Options&) const;` 与 `absl::Status ValidateFeatures(const FileDescriptor*) const;` —— cpp/generator.h L50-104

F-CMP-058: `class PROTOC_EXPORT FileGenerator`（cpp/file.h）：构造 `FileGenerator(const FileDescriptor* file, const Options& options);`；公有方法 `void GenerateProtoHeader(io::Printer* p, absl::string_view info_path);`、`void GeneratePBHeader(io::Printer* p, absl::string_view info_path);`、`void GenerateSource(io::Printer* p);`、`int NumMessages() const`、`int NumExtensions() const`、`void GenerateSourceForMessage(int idx, io::Printer* p);`、`void GenerateSourceForExtension(int idx, io::Printer* p);`、`void GenerateGlobalSource(io::Printer* p);` —— cpp/file.h L42-73

F-CMP-059: cpp/ 目录类定义清单（class 声明位置）：EnumGenerator（enum.h L25）、ExtensionGenerator（extension.h L45）、FieldGeneratorBase（field.h L48）、FieldGenerator（field.h L229）、FieldGeneratorTable（field.h L511）、FileGenerator（file.h L42）、MessageSCCAnalyzer（helpers.h L718）、Formatter（helpers.h L950）、NamespaceOpener（helpers.h L1087）、FieldLayout（field_layout.h L21）、MessageGenerator（message.h L40）、IfdefGuardPrinter（ifndef_guard.h L43）、FieldGroup 与 MessageLayoutHelper（message_layout_helper.h L30/L81）、NamespacePrinter（namespace_printer.h L40）、ParseFunctionGenerator（parse_function_generator.h L37）、ServiceGenerator（service.h L27）—— cpp/ 各头文件

F-CMP-060: cpp/field_generators/ 目录文件清单（共 8 个）：cord_field.cc、enum_field.cc、map_field.cc、message_field.cc、primitive_field.cc、string_field.cc、string_view_field.cc、generators.h（该目录仅 generators.h 一个头文件）—— cpp/field_generators/（目录清单）

F-CMP-061: cpp/field_generators/generators.h 工厂函数全集（返回类型均为 `std::unique_ptr<FieldGeneratorBase>`；函数名 "Singuar" 为源码原文拼写，缺少字母 l）：`MakeSinguarPrimitiveGenerator`、`MakeRepeatedPrimitiveGenerator`、`MakeSinguarEnumGenerator`、`MakeRepeatedEnumGenerator`、`MakeSinguarStringGenerator`、`MakeRepeatedStringGenerator`、`MakeSingularStringViewGenerator`、`MakeRepeatedStringViewGenerator`、`MakeSinguarMessageGenerator`、`MakeRepeatedMessageGenerator`、`MakeOneofMessageGenerator`、`MakeMapGenerator`、`MakeSingularCordGenerator`、`MakeOneofCordGenerator`（参数均为 `const FieldDescriptor* desc, const Options& options`）—— cpp/field_generators/generators.h L33-73

F-CMP-062: cpp/helpers.h 关键函数（抄录）：`PROTOC_EXPORT std::string ClassName(const Descriptor* descriptor);`、`PROTOC_EXPORT std::string ClassName(const EnumDescriptor* enum_descriptor);`、`std::string QualifiedClassName(const Descriptor* d, const Options& options);`（共 4 个重载）、`PROTOC_EXPORT std::string FieldName(const FieldDescriptor* field);`（L228）、`std::string FieldConstantName(const FieldDescriptor* field);`（L247）、`std::string DefaultValue(const Options& options, const FieldDescriptor* field);`（L274）、`std::string Namespace(const FileDescriptor* d);`（4 个重载 L104-113）、`PROTOC_EXPORT bool ValidateCcNamespace(const FileDescriptor* file, std::string* error);`（L109）、`std::string ExtensionName(const FieldDescriptor* d);`（L156）、`std::string QualifiedExtensionName(const FieldDescriptor* d, const Options& options);`（L158）、`PROTOC_EXPORT std::string StripProto(absl::string_view filename);`（L1183）—— cpp/helpers.h L104-277、L1183

F-CMP-063: `class ParseFunctionGenerator`（parse_function_generator.h L36）：静态常量 `static constexpr float kUnknownPresenceProbability = 0.5f;`；`using GetHasBitIndex = absl::FunctionRef<absl::optional<int>(const FieldDescriptor* field) const>;`；两个构造重载；静态方法 `static std::vector<internal::TailCallTableInfo::FieldOptions> BuildFieldOptions(...)`、`static internal::TailCallTableInfo BuildTcTableInfoFromDescriptor(...)`；公有 `void GenerateAliasParseTableType(io::Printer* printer);`、`void GenerateParseTableHelperDefinition(io::Printer* printer);` —— cpp/parse_function_generator.h L36-79

F-CMP-064: cpp/tracker.h 无类定义；导出两个重载函数：`std::vector<google::protobuf::io::Printer::Sub> MakeTrackerCalls(const google::protobuf::Descriptor* message, const Options& opts);` 与 `std::vector<google::protobuf::io::Printer::Sub> MakeTrackerCalls(const google::protobuf::FieldDescriptor* field, const Options& opts);` —— cpp/tracker.h L23-28

F-CMP-065: `struct Options`（cpp/options.h L42）成员清单（抄录）：`const AccessInfoMap* access_info_map = nullptr;`、`const SplitMap* split_map = nullptr;`、`cpp::MessageSCCAnalyzer* scc_analyzer = nullptr;`、`std::string dllexport_decl;`、`std::string runtime_include_base;`、`std::string annotation_pragma_name;`、`std::string annotation_guard_name;`、`FieldListenerOptions field_listener_options;`、`EnforceOptimizeMode enforce_mode = EnforceOptimizeMode::kNoEnforcement;`、`int num_cc_files = 0;`、`bool proto_h = false;`、`bool transitive_pb_h = true;`、`bool annotate_headers = false;`、`bool lite_implicit_weak_fields = false;`、`bool descriptor_implicit_weak_messages = false;`、`bool bootstrap = false;`、`bool opensource_runtime = false;`、`bool annotate_accessor = false;`、`bool force_split = false;`、`bool force_eagerly_verified_lazy`、`bool force_inline_string`、`bool strip_nonfunctional_codegen = false;`、`bool experimental_use_micro_string` —— cpp/options.h L42-68

F-CMP-066: cpp/options.h 另定义：`struct FieldListenerOptions { bool inject_field_listener_events = false; absl::flat_hash_set<std::string> forbidden_field_listener_events; };` 与枚举 `enum EnforceOptimizeMode { kNoEnforcement, kSpeed, kCodeSize, kLiteRuntime };` —— cpp/options.h L30-39

## 九、java/ 目录

F-CMP-067: java_generator.h 全文仅 `#include "google/protobuf/compiler/java/generator.h"`（无类定义）；Java 生成器主类为 `class PROTOC_EXPORT JavaGenerator : public CodeGenerator`，定义于 java/generator.h L38 —— java/java_generator.h L8-12、java/generator.h L38

F-CMP-068: JavaGenerator 成员：`bool Generate(const FileDescriptor* file, const std::string& parameter, GeneratorContext* context, std::string* error) const override;`、`uint64_t GetSupportedFeatures() const override;`（generator.cc L39-42 实现：`return CodeGenerator::Feature::FEATURE_PROTO3_OPTIONAL | CodeGenerator::Feature::FEATURE_SUPPORTS_EDITIONS;`）、`Edition GetMinimumEdition() const override { return Edition::EDITION_PROTO2; }`、`Edition GetMaximumEdition() const override { return Edition::EDITION_2026; }`、`std::vector<const FieldDescriptor*> GetFeatureExtensions() const override { return {GetExtensionReflection(pb::java)}; }` —— java/generator.h L46-61、java/generator.cc L39-42

F-CMP-069: java/full/ 子目录 .h 文件（14 个）：enum.h、enum_field.h、extension.h、field_generator.h、generator_factory.h、make_field_gens.h、map_field.h、message.h、message_builder.h、message_field.h、oneof_generator.h、primitive_field.h、service.h、string_field.h；java/lite/ 子目录 .h 文件（12 个）：enum.h、enum_field.h、extension.h、field_generator.h、generator_factory.h、make_field_gens.h、map_field.h、message.h、message_builder.h、message_field.h、primitive_field.h、string_field.h —— java/full/、java/lite/（目录清单）

F-CMP-070: java/ 顶层不存在 kotlin/ 子目录；Kotlin 生成器位于 compiler/kotlin/（见 F-CMP-090）—— java/（目录清单）

F-CMP-071: java/full/generator_factory.h 声明 `std::unique_ptr<GeneratorFactory> MakeImmutableGeneratorFactory(Context* context);`；java/lite/generator_factory.h 声明 `std::unique_ptr<GeneratorFactory> MakeImmutableLiteGeneratorFactory(Context* context);` —— java/full/generator_factory.h L11-12、java/lite/generator_factory.h L11-12

F-CMP-072: `class SharedCodeGenerator`（java/shared_code_generator.h L44）：构造 `SharedCodeGenerator(const FileDescriptor* file, const Options& options);`；方法 `void Generate(GeneratorContext* generator_context, std::vector<std::string>* file_list, std::vector<std::string>* annotation_file_list);`、`void GenerateDescriptors(io::Printer* printer);`；私有成员 `std::unique_ptr<ClassNameResolver> name_resolver_;` —— java/shared_code_generator.h L44-61

F-CMP-073: `class PROTOC_EXPORT ClassNameResolver`（java/name_resolver.h L38）：方法 `std::string GetFileClassName(const FileDescriptor* file, bool immutable);`（2 重载）、`std::string GetFileImmutableClassName(const FileDescriptor* file);`、`static std::string GetFileDefaultImmutableClassName(...);`、`std::string GetDescriptorClassName(const FileDescriptor* file);`、`std::string GetClassName(const Descriptor*/const EnumDescriptor*/const ServiceDescriptor*/const FileDescriptor*, bool immutable);`（各 2 重载）、模板 `GetImmutableClassName(const DescriptorType*)`、`std::string GetExtensionIdentifierName(const FieldDescriptor*, ...);` —— java/name_resolver.h L38-91

F-CMP-074: java/ 顶层 .h 文件清单（17 个）：shared_code_generator.h、options.h、names_internal.h、names.h、name_resolver.h、message_serialization.h、java_generator.h、java_features.pb.h、internal_helpers.h、helpers.h、generator_factory.h、generator_common.h、generator.h、file.h、field_common.h、doc_comment.h、context.h（其中 context.h 定义 `class Context`，L42）—— java/（目录清单）

## 十、python/ 目录

F-CMP-075: `class PROTOC_EXPORT Generator : public CodeGenerator`（python/generator.h L56）：`bool Generate(const FileDescriptor* file, const std::string& parameter, GeneratorContext* generator_context, std::string* error) const override;`；`uint64_t GetSupportedFeatures() const override { return Feature::FEATURE_PROTO3_OPTIONAL | Feature::FEATURE_SUPPORTS_EDITIONS; }`；`Edition GetMinimumEdition() const override { return Edition::EDITION_PROTO2; }`；`Edition GetMaximumEdition() const override { return Edition::EDITION_2026; }`；`std::vector<const FieldDescriptor*> GetFeatureExtensions() const override { return {}; }`；`void set_opensource_runtime(bool opensource)`；私有 `GeneratorOptions ParseParameter(absl::string_view parameter, std::string* error) const;` —— python/generator.h L56-89

F-CMP-076: `struct GeneratorOptions { bool generate_pyi = false; bool annotate_pyi = false; bool bootstrap = false; bool strip_nonfunctional_codegen = false; };` —— python/generator.h L49-54

F-CMP-077: `class PROTOC_EXPORT PyiGenerator : public google::protobuf::compiler::CodeGenerator`（python/pyi_generator.h L41）：`uint64_t GetSupportedFeatures() const override`（返回 `Feature::FEATURE_PROTO3_OPTIONAL | Feature::FEATURE_SUPPORTS_EDITIONS`）、`bool Generate(...) const override;`、`Edition GetMinimumEdition() const override { return Edition::EDITION_PROTO2; }`、`Edition GetMaximumEdition() const override { return Edition::EDITION_2026; }`、`std::vector<const FieldDescriptor*> GetFeatureExtensions() const override { return {}; }` —— python/pyi_generator.h L41-62

F-CMP-078: python/plugin_main.cc 全文主体：`int main(int argc, char *argv[]) { ::google::protobuf::compiler::python::Generator generator; ... return ::google::protobuf::compiler::PluginMain(argc, argv, &generator); }`（`#ifdef GOOGLE_PROTOBUF_RUNTIME_INCLUDE_BASE` 分支调用 `generator.set_opensource_runtime(true)` 与 `generator.set_runtime_include_base(...)`）—— python/plugin_main.cc L4-11

F-CMP-079: python/ 目录 .h 文件清单（5 个）：python_generator.h、pyi_generator.h、names.h、helpers.h、generator.h —— python/（目录清单）

## 十一、csharp/ 目录

F-CMP-080: `class PROTOC_EXPORT Generator : public CodeGenerator`（csharp/csharp_generator.h L29）：`bool Generate(const FileDescriptor* file, const std::string& parameter, GeneratorContext* generator_context, std::string* error) const override;`、`uint64_t GetSupportedFeatures() const override;`（声明，实现于 .cc）、`Edition GetMinimumEdition() const override { return Edition::EDITION_PROTO2; }`、`Edition GetMaximumEdition() const override { return Edition::EDITION_2026; }`、`std::vector<const FieldDescriptor*> GetFeatureExtensions() const override { return {GetExtensionReflection(pb::csharp)}; }` —— csharp/csharp_generator.h L29-47

F-CMP-081: csharp_helpers.h 函数（抄录）：`std::string GetFieldName(const FieldDescriptor* descriptor);`（L54）、`std::string GetFieldConstantName(const FieldDescriptor* field);`（L56）、`std::string GetPropertyName(const FieldDescriptor* descriptor);`（L58）、`std::string GetOneofCaseName(const FieldDescriptor* descriptor);`（L60）、`std::string StringToBase64(absl::string_view input);`（L70）、`std::string FileDescriptorToBase64(const FileDescriptor* descriptor);`（L72）、`std::string GetFullExtensionName(const FieldDescriptor* descriptor);`（L78）—— csharp/csharp_helpers.h L54-78

F-CMP-082: `class FieldGeneratorBase : public SourceGeneratorBase`（csharp/csharp_field_base.h L28）：构造 `FieldGeneratorBase(const FieldDescriptor* descriptor, const Options* options);`；纯虚方法 `GenerateCloningCode(io::Printer*)`、`GenerateMembers(io::Printer*)`、`GenerateMergingCode(io::Printer*)`、`GenerateParsingCode(io::Printer*)`、`GenerateSerializationCode(io::Printer*)`、`GenerateSerializedSizeCode(io::Printer*)`；虚方法（带默认实现）`GenerateFreezingCode`、`GenerateCodecCode`、`GenerateExtensionCode`、`GenerateParsingCode(io::Printer*, bool use_parse_context)`、`GenerateSerializationCode(io::Printer*, bool use_write_context)` —— csharp/csharp_field_base.h L28-48

F-CMP-083: csharp/ 目录 .h 文件清单（19 个）：names.h、csharp_wrapper_field.h、csharp_source_generator_base.h、csharp_repeated_primitive_field.h、csharp_repeated_message_field.h、csharp_repeated_enum_field.h、csharp_reflection_class.h、csharp_primitive_field.h、csharp_options.h、csharp_message_field.h、csharp_message.h、csharp_map_field.h、csharp_helpers.h、csharp_generator.h、csharp_field_base.h、csharp_enum_field.h、csharp_enum.h、csharp_doc_comment.h、c_sharp_features.pb.h —— csharp/（目录清单）

## 十二、objectivec/ / php/ / ruby/ / rust/ / kotlin/

F-CMP-084: `class PROTOC_EXPORT ObjectiveCGenerator final : public CodeGenerator`（objectivec/generator.h L33）：`bool Generate(...) const override;`、`bool GenerateAll(...) const override;`、`uint64_t GetSupportedFeatures() const override { return (FEATURE_PROTO3_OPTIONAL | FEATURE_SUPPORTS_EDITIONS); }`、`Edition GetMinimumEdition() const override { return Edition::EDITION_PROTO2; }`、`Edition GetMaximumEdition() const override { return Edition::EDITION_2026; }` —— objectivec/generator.h L33-53

F-CMP-085: php/php_generator.h：`class PROTOC_EXPORT Generator : public CodeGenerator`，公有 `bool Generate(...) const override;`、`bool GenerateAll(...) const override;`、`uint64_t GetSupportedFeatures() const override { return Feature::FEATURE_PROTO3_OPTIONAL | Feature::FEATURE_SUPPORTS_EDITIONS; }`、`Edition GetMinimumEdition() const override { return Edition::EDITION_PROTO2; }`、`Edition GetMaximumEdition() const override { return Edition::EDITION_2026; }`、`GetFeatureExtensions` 返回 `{}`；私有 `bool Generate(const FileDescriptor* file, const Options& options, GeneratorContext* generator_context, std::string* error) const;` 重载；文件级 `inline bool IsWrapperType(const FieldDescriptor* descriptor)`；php/ 目录仅 php_generator.h 与 names.h 两个头文件 —— php/php_generator.h L26-59

F-CMP-086: ruby/ruby_generator.h：`class PROTOC_EXPORT Generator : public CodeGenerator`（L35），`bool Generate(...) const override;`、`uint64_t GetSupportedFeatures() const override { return Feature::FEATURE_PROTO3_OPTIONAL | Feature::FEATURE_SUPPORTS_EDITIONS; }`、`Edition GetMinimumEdition() const override { return Edition::EDITION_PROTO2; }`、`Edition GetMaximumEdition() const override { return Edition::EDITION_2026; }`；文件级自由函数 `std::string GetRequireName(absl::string_view proto_file);`、`std::string PackageToModule(absl::string_view name);`、`std::string RubifyConstant(absl::string_view name);`、`bool IsValidRubyPackage(absl::string_view pkg, std::string* error);`、`int GeneratePackageModules(const FileDescriptor* file, io::Printer* printer);`、`void EndPackageModules(int levels, io::Printer* printer);` —— ruby/ruby_generator.h L24-45

F-CMP-087: ruby/rbs_generator.h：`class PROTOC_EXPORT RBSGenerator : public CodeGenerator`（L24），`bool Generate(...) const override;`、`uint64_t GetSupportedFeatures() const override { return FEATURE_PROTO3_OPTIONAL; }`（不含 FEATURE_SUPPORTS_EDITIONS，也无 GetMinimumEdition/GetMaximumEdition override）；ruby/ 目录仅 ruby_generator.h 与 rbs_generator.h 两个头文件 —— ruby/rbs_generator.h L24-31

F-CMP-088: rust/generator.h：`class PROTOC_EXPORT RustGenerator final : public google::protobuf::compiler::CodeGenerator`（L24），`bool Generate(const FileDescriptor* file, const std::string& parameter, GeneratorContext* generator_context, std::string* error) const override;`、`uint64_t GetSupportedFeatures() const override { return FEATURE_PROTO3_OPTIONAL | FEATURE_SUPPORTS_EDITIONS; }`、`Edition GetMinimumEdition() const override { return Edition::EDITION_PROTO2; }`、`Edition GetMaximumEdition() const override { return Edition::EDITION_2026; }` —— rust/generator.h L24-41

F-CMP-089: rust/ 目录其他类：`class RustGeneratorContext`（context.h L61）、`class Context`（context.h L89）、`class AccessorGenerator`（accessors/generator.h L26）及其 final 派生类 SingularScalar（L80）、SingularString（L89）、SingularCord（L98）、SingularMessage（L107）、RepeatedField（L116）、UnsupportedField（L125）、Map（L132）、`class MultiCasePrefixStripper final`（naming.h L135）、`class RelativePath final`（relative_path.h L25）—— rust/ 各头文件

F-CMP-090: kotlin/generator.h：`class PROTOC_EXPORT KotlinGenerator : public CodeGenerator`（L33），`bool Generate(...) const override;`、`uint64_t GetSupportedFeatures() const override;`（声明，实现于 .cc）、`Edition GetMinimumEdition() const override { return Edition::EDITION_PROTO2; }`、`Edition GetMaximumEdition() const override { return Edition::EDITION_2026; }`、`std::vector<const FieldDescriptor*> GetFeatureExtensions() const override { return {GetExtensionReflection(pb::java)}; }`；kotlin/ 目录文件：generator.h、generator.cc、file.h、message.h、field.h —— kotlin/generator.h L33-54、kotlin/（目录清单）
