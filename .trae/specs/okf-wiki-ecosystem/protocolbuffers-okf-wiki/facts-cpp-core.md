# protobuf C++ 运行时核心事实清单（R阶段）

## 范围说明

- 源码根：`d:\spaces\SpecWeave\external\libs\protocolbuffers\protobuf\src\google\protobuf`（只读采集，未修改任何源码文件）
- 采集深度：类定义、继承关系、公开方法签名（含参数与返回类型）、枚举与常量，均从头文件源码抄录
- 编号规则：F-CPP-NNN，每条标注源码相对路径（相对 `src/google/protobuf/`）
- 采集方式：Read/Grep 工具直读源码核对，零推测（无推断性措辞）

## 1. 消息基类（message_lite.h / message.h）

- F-CPP-001: `class PROTOBUF_EXPORT MessageLite` 定义 —— message_lite.h:353
- F-CPP-002: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD absl::string_view GetTypeName() const`（MessageLite 成员）—— message_lite.h:364
- F-CPP-003: `virtual void Clear() = 0`（MessageLite 纯虚成员）—— message_lite.h:388
- F-CPP-004: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD ABSL_ATTRIBUTE_REINITIALIZES bool ParseFromString(absl::string_view data)` —— message_lite.h:494
- F-CPP-005: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD ABSL_ATTRIBUTE_REINITIALIZES bool ParseFromString(const absl::Cord& data)` —— message_lite.h:496
- F-CPP-006: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD bool SerializeToString(std::string* output) const` —— message_lite.h:568
- F-CPP-007: `class PROTOBUF_EXPORT Message : public MessageLite`（Message 继承 MessageLite）—— message.h
- F-CPP-008: `void CopyFrom(const Message& from)` / `void MergeFrom(const Message& from)`（Message 成员）—— message.h
- F-CPP-009: `[[nodiscard]] const Descriptor* GetDescriptor() const { return GetMetadata().descriptor; }` / `[[nodiscard]] const Reflection* GetReflection() const { return GetMetadata().reflection; }` —— message.h
- F-CPP-010: `[[nodiscard]] std::string DebugString() const` / `[[nodiscard]] std::string ShortDebugString() const` / `[[nodiscard]] std::string Utf8DebugString() const` —— message.h
- F-CPP-011: `[[nodiscard]] Message* New() const` / `[[nodiscard]] Message* New(Arena* arena) const`（Message 成员）—— message.h
- F-CPP-012: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD size_t ByteSizeLong() const override = 0`（MessageLite 纯虚）—— message_lite.h

## 2. Reflection 反射类（message.h）

- F-CPP-013: `class PROTOBUF_EXPORT Reflection final` 定义 —— message.h:509
- F-CPP-014: `[[nodiscard]] const UnknownFieldSet& GetUnknownFields(const Message& message) const` —— message.h:518
- F-CPP-015: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD UnknownFieldSet* MutableUnknownFields(Message* message) const` —— message.h:523
- F-CPP-016: `[[nodiscard]] size_t SpaceUsedLong(const Message& message) const` —— message.h:527
- F-CPP-017: `[[nodiscard]] bool HasField(const Message& message, const FieldDescriptor* field) const` / `[[nodiscard]] int FieldSize(const Message& message, const FieldDescriptor* field) const` / `void ClearField(Message* message, const FieldDescriptor* field) const` —— message.h:541-550
- F-CPP-018: `void ListFields(const Message& message, std::vector<const FieldDescriptor*>* output) const` —— message.h:612
- F-CPP-019: `[[nodiscard]] int32_t GetInt32(const Message& message, const FieldDescriptor* field) const`（同类 getter 含 GetInt64/GetUInt32/GetUInt64/GetFloat/GetDouble/GetBool）—— message.h:627-640
- F-CPP-020: `[[nodiscard]] std::string GetString(const Message& message, const FieldDescriptor* field) const` —— message.h:641
- F-CPP-021: `[[nodiscard]] const std::string& GetStringReference(const Message& message, const FieldDescriptor* field, std::string* scratch) const` —— message.h:676
- F-CPP-022: `[[nodiscard]] absl::Cord GetCord(const Message& message, const FieldDescriptor* field) const` —— message.h:684
- F-CPP-023: `[[nodiscard]] absl::string_view GetStringView(const Message& message, const FieldDescriptor* field, ScratchSpace& scratch ABSL_ATTRIBUTE_LIFETIME_BOUND) const` —— message.h:717
- F-CPP-024: `class ScratchSpace`（Reflection 嵌套类，含 `absl::string_view CopyFromCord(const absl::Cord& cord)`）—— message.h:690
- F-CPP-025: `void SetInt32(Message* message, const FieldDescriptor* field, int32_t value) const`（同类 setter 含 SetInt64/SetUInt32/SetUInt64/SetFloat/SetDouble/SetBool）—— message.h:725-738
- F-CPP-026: `void SetString(Message* message, const FieldDescriptor* field, std::string value) const` / `void SetString(Message* message, const FieldDescriptor* field, const absl::Cord& value) const` —— message.h:739-745
- F-CPP-027: `void SetEnum(Message* message, const FieldDescriptor* field, const EnumValueDescriptor* value) const` / `void SetEnumValue(Message* message, const FieldDescriptor* field, int value) const` —— message.h:746-756
- F-CPP-028: `[[nodiscard]] const Message& GetMessage(const Message& message, const FieldDescriptor* field, MessageFactory* factory = nullptr) const` —— message.h:657
- F-CPP-029: `Message* MutableMessage(Message* message, const FieldDescriptor* field, MessageFactory* factory = nullptr) const` —— message.h:768
- F-CPP-030: `void SetAllocatedMessage(Message* message, Message* sub_message, const FieldDescriptor* field) const` —— message.h:775
- F-CPP-031: `[[nodiscard]] Message* ReleaseMessage(Message* message, const FieldDescriptor* field, MessageFactory* factory = nullptr) const` / `Message* UnsafeArenaReleaseMessage(Message* message, const FieldDescriptor* field, MessageFactory* factory = nullptr) const` —— message.h:791-800
- F-CPP-032: `[[nodiscard]] int32_t GetRepeatedInt32(const Message& message, const FieldDescriptor* field, int index) const`（同类含 GetRepeatedInt64/GetRepeatedUInt32/GetRepeatedUInt64）—— message.h:806-816
- F-CPP-033: `[[nodiscard]] bool HasOneof(const Message& message, const OneofDescriptor* oneof_descriptor) const` / `void ClearOneof(Message* message, const OneofDescriptor* oneof_descriptor) const` / `[[nodiscard]] const FieldDescriptor* GetOneofFieldDescriptor(const Message& message, const OneofDescriptor* oneof_descriptor) const` —— message.h:554-562
- F-CPP-034: `void Swap(Message* message1, Message* message2) const` / `void SwapFields(Message* message1, Message* message2, const std::vector<const FieldDescriptor*>& fields) const` / `void SwapElements(Message* message, const FieldDescriptor* field, int index1, int index2) const` —— message.h:584-592
- F-CPP-035: `void RemoveLast(Message* message, const FieldDescriptor* field) const` / `[[nodiscard]] Message* ReleaseLast(Message* message, const FieldDescriptor* field) const` —— message.h:571-575

## 3. Arena 内存分配（arena.h / arenastring.h）

- F-CPP-036: `class PROTOBUF_EXPORT Arena final` 定义 —— arena.h
- F-CPP-037: `[[nodiscard]] PROTOBUF_NDEBUG_INLINE Ptr<T> Make(Args&&... args)`（Arena 模板成员）—— arena.h:379
- F-CPP-038: `PROTOBUF_ALWAYS_INLINE void Own(T* PROTOBUF_NULLABLE object)` / `PROTOBUF_ALWAYS_INLINE void OwnDestructor(T* PROTOBUF_NULLABLE object)` —— arena.h:478,496
- F-CPP-039: `PROTOBUF_NDEBUG_INLINE T* PROTOBUF_NONNULL DoCreateMessage(Args&&... args)`（Arena 内部模板，Create/DoCreateMessage 调用链位于 arena.h:717,734,769）—— arena.h:769
- F-CPP-040: `class ArenaStringPtr`（含 `std::string* Mutable(Arena* arena)` / `std::string* Mutable(const LazyString& default_value, Arena* arena)` / `const std::string& Get() const`）—— arenastring.h:325-338
- F-CPP-041: `inline bool IsMutable() const { return as_int() & kMutableBit; }`（ArenaStringPtr 成员）—— arenastring.h:138

## 4. 描述符类（descriptor.h）

- F-CPP-042: `class PROTOBUF_EXPORT Descriptor : private internal::SymbolBase` —— descriptor.h
- F-CPP-043: `[[nodiscard]] absl::string_view name() const` / `[[nodiscard]] absl::string_view full_name() const` / `[[nodiscard]] const FileDescriptor* file() const`（Descriptor 成员）—— descriptor.h
- F-CPP-044: `[[nodiscard]] int field_count() const` / `[[nodiscard]] const FieldDescriptor* field(int index) const` / `[[nodiscard]] const FieldDescriptor* FindFieldByName(absl::string_view name) const` / `[[nodiscard]] const FieldDescriptor* FindFieldByNumber(int number) const` —— descriptor.h
- F-CPP-045: `class PROTOBUF_EXPORT FieldDescriptor : private internal::SymbolBase, public internal::FieldDescriptorLite`（FieldDescriptor 双重继承）—— descriptor.h
- F-CPP-046: FieldDescriptor::Type 枚举完整值：`TYPE_DOUBLE=1, TYPE_FLOAT=2, TYPE_INT64=3, TYPE_UINT64=4, TYPE_INT32=5, TYPE_FIXED64=6, TYPE_FIXED32=7, TYPE_BOOL=8, TYPE_STRING=9, TYPE_GROUP=10, TYPE_MESSAGE=11, TYPE_BYTES=12, TYPE_UINT32=13, TYPE_ENUM=14, TYPE_SFIXED32=15, TYPE_SFIXED64=16, TYPE_SINT32=17, TYPE_SINT64=18, MAX_TYPE=18` —— descriptor.h
- F-CPP-047: FieldDescriptor::Label 枚举完整值：`LABEL_OPTIONAL=1, LABEL_REQUIRED=2, LABEL_REPEATED=3, MAX_LABEL=3` —— descriptor.h
- F-CPP-048: `[[nodiscard]] Type type() const` / `[[nodiscard]] Label label() const` / `[[nodiscard]] bool is_required() const` / `[[nodiscard]] bool is_repeated() const` / `[[nodiscard]] const Descriptor* message_type() const` / `[[nodiscard]] const EnumDescriptor* enum_type() const` —— descriptor.h
- F-CPP-049: `class PROTOBUF_EXPORT OneofDescriptor : private internal::SymbolBase` —— descriptor.h:1390
- F-CPP-050: `class PROTOBUF_EXPORT EnumDescriptor : private internal::SymbolBase` —— descriptor.h:1500
- F-CPP-051: `class PROTOBUF_EXPORT EnumValueDescriptor : private internal::SymbolBaseN<0>` —— descriptor.h:1731
- F-CPP-052: `class PROTOBUF_EXPORT ServiceDescriptor : private internal::SymbolBase` —— descriptor.h:1843
- F-CPP-053: `class PROTOBUF_EXPORT MethodDescriptor : private internal::SymbolBase` —— descriptor.h:1954
- F-CPP-054: `class PROTOBUF_EXPORT FileDescriptor : private internal::SymbolBase` —— descriptor.h:2065
- F-CPP-055: `Edition edition() const`（FileDescriptor 私有成员，注释含 "For legacy proto2/proto3 files, special EDITION_PROTO2 and EDITION_PROTO3 values are used"）—— descriptor.h:2238
- F-CPP-056: `const FeatureSet& features() const { return *merged_features_; }`（FileDescriptor 私有成员）—— descriptor.h:2244
- F-CPP-057: `class PROTOBUF_EXPORT DescriptorPool` —— descriptor.h:2353
- F-CPP-058: `generated_pool()`（DescriptorPool 静态方法，descriptor.h:2395）—— descriptor.h
- F-CPP-059: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD const FileDescriptor* FindFileByName(absl::string_view filename) const` 与 `FindFileContainingSymbol(absl::string_view symbol_name) const` —— descriptor.h:2400-2408
- F-CPP-060: `const FileDescriptor* BuildFile(const FileDescriptorProto& proto)` —— descriptor.h:2525
- F-CPP-061: `bool TryFindFileInFallbackDatabase(...)` / `bool TryFindSymbolInFallbackDatabase(...)` / `bool TryFindExtensionInFallbackDatabase(...)`（DescriptorPool 私有方法）—— descriptor.h:2812-2816
- F-CPP-062: `internal_generated_pool()`（DescriptorPool 内部静态，descriptor.h:2683）—— descriptor.h

## 5. descriptor.pb.h 生成类与 Edition 枚举

- F-CPP-063: `enum Edition : int` 完整值（descriptor.pb.h:999-1007）：`EDITION_UNKNOWN=0, EDITION_LEGACY=900, EDITION_PROTO2=998, EDITION_PROTO3=999, EDITION_2023=1000, EDITION_2024=1001, EDITION_2026=1002, EDITION_UNSTABLE=9999` —— descriptor.pb.h
- F-CPP-064: `PROTOBUF_EXPORT extern const uint32_t Edition_internal_data_[]`（descriptor.pb.h:52）—— descriptor.pb.h
- F-CPP-065: 枚举前向声明（descriptor.pb.h:51-59）：`enum Edition : int` / `enum ExtensionRangeOptions_VerificationState : int` / `enum FeatureSet_EnforceNamingStyle : int` / `enum FeatureSet_EnumType : int` / `enum FeatureSet_FieldPresence : int` —— descriptor.pb.h
- F-CPP-066: descriptor.proto 顶层 message 定义（行号）：`FileDescriptorSet(33) FileDescriptorProto(85) DescriptorProto(132) ExtensionRangeOptions(169) FieldDescriptorProto(227) OneofDescriptorProto(334) EnumDescriptorProto(340) EnumValueDescriptorProto(372) ServiceDescriptorProto(380) MethodDescriptorProto(391) FileOptions(439) MessageOptions(593) FieldOptions(682) OneofOptions(859) EnumOptions(877) EnumValueOptions(916) ServiceOptions(952) MethodOptions(982) UninterpretedOption(1029) FeatureSet(1060) FeatureSetDefaults(1297) SourceCodeInfo(1330) GeneratedCodeInfo(1507)` —— descriptor.proto
- F-CPP-067: `enum Edition`（descriptor.proto:45）与 `enum SymbolVisibility`（descriptor.proto:1547）定义 —— descriptor.proto
- F-CPP-068: `enum ExtensionRangeOptions_VerificationState`、`enum FeatureSet_EnforceNamingStyle`、`enum FeatureSet_EnumType`、`enum FeatureSet_FieldPresence` 枚举数据表前向声明（descriptor.pb.h:53-59）—— descriptor.pb.h

## 6. 描述符数据库（descriptor_database.h）

- F-CPP-069: `class PROTOBUF_EXPORT DescriptorDatabase`（抽象基类）—— descriptor_database.h:53
- F-CPP-070: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD virtual bool FindFileByName(absl::string_view filename, FileDescriptorProto* PROTOBUF_NONNULL output) = 0` —— descriptor_database.h:67-69
- F-CPP-071: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD virtual bool FindFileContainingSymbol(absl::string_view symbol_name, FileDescriptorProto* PROTOBUF_NONNULL output) = 0` —— descriptor_database.h:74-76
- F-CPP-072: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD virtual bool FindFileContainingExtension(absl::string_view containing_type, int field_number, FileDescriptorProto* PROTOBUF_NONNULL output) = 0` —— descriptor_database.h:82-84
- F-CPP-073: `class PROTOBUF_EXPORT SimpleDescriptorDatabase : public DescriptorDatabase`（含 `bool Add(const FileDescriptorProto& file)` / `bool AddAndOwn(const FileDescriptorProto* PROTOBUF_NONNULL file)` / `bool AddUnowned(const FileDescriptorProto* PROTOBUF_NONNULL file)`）—— descriptor_database.h:159-177
- F-CPP-074: 前向声明（descriptor_database.h:39-43）：`class DescriptorDatabase; class SimpleDescriptorDatabase; class EncodedDescriptorDatabase; class DescriptorPoolDatabase; class MergedDescriptorDatabase;` —— descriptor_database.h

## 7. Wire Format（wire_format_lite.h / wire_format.h）

- F-CPP-075: `class PROTOBUF_EXPORT WireFormatLite` —— wire_format_lite.h
- F-CPP-076: WireFormatLite::WireType 枚举完整值：`WIRETYPE_VARINT=0, WIRETYPE_FIXED64=1, WIRETYPE_LENGTH_DELIMITED=2, WIRETYPE_START_GROUP=3, WIRETYPE_END_GROUP=4, WIRETYPE_FIXED32=5` —— wire_format_lite.h
- F-CPP-077: `static constexpr int kTagTypeBits = 3` / `static constexpr uint32_t kTagTypeMask = (1 << kTagTypeBits) - 1` —— wire_format_lite.h
- F-CPP-078: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD constexpr static uint32_t MakeTag(int field_number, WireType type)` —— wire_format_lite.h
- F-CPP-079: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD static WireType GetTagWireType(uint32_t tag)` / `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD static int GetTagFieldNumber(uint32_t tag)` —— wire_format_lite.h
- F-CPP-080: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD static size_t VarintSize32(uint32_t value)` / `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD static size_t VarintSize64(uint64_t value)` —— wire_format_lite.h
- F-CPP-081: `class PROTOBUF_EXPORT WireFormat`（`WireFormat() = delete;`，仅静态方法）—— wire_format.h:63
- F-CPP-082: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD static inline WireFormatLite::WireType WireTypeForField(const FieldDescriptor* field)` / `static inline WireFormatLite::WireType WireTypeForFieldType(FieldDescriptor::Type type)` —— wire_format.h:68-73
- F-CPP-083: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD static inline size_t TagSize(int field_number, FieldDescriptor::Type type)` —— wire_format.h:77
- F-CPP-084: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD static bool ParseAndMergePartial(io::CodedInputStream* input, Message* message)` / `static const char* _InternalParse(Message* msg, const char* ptr, internal::ParseContext* ctx)` —— wire_format.h:96-102
- F-CPP-085: `static void SerializeWithCachedSizes(const Message& message, int size, io::CodedOutputStream* output)` / `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD static uint8_t* _InternalSerialize(const Message& message, uint8_t* target, io::EpsCopyOutputStream* stream)` —— wire_format.h:111-122
- F-CPP-086: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD static size_t ByteSize(const Message& message)` —— wire_format.h:129
- F-CPP-087: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD static bool SkipField(io::CodedInputStream* input, uint32_t tag, UnknownFieldSet* unknown_fields)` / `static bool SkipMessage(io::CodedInputStream* input, UnknownFieldSet* unknown_fields)` —— wire_format.h:138-145
- F-CPP-088: `static void SerializeUnknownFields(const UnknownFieldSet& unknown_fields, io::CodedOutputStream* output)` / `static uint8_t* SerializeUnknownFieldsToArray(const UnknownFieldSet& unknown_fields, uint8_t* target)` / `static uint8_t* InternalSerializeUnknownFieldsToArray(const UnknownFieldSet& unknown_fields, uint8_t* target, io::EpsCopyOutputStream* stream)` —— wire_format.h:148-170

## 8. IO 流（io/coded_stream.h / io/zero_copy_stream.h / io/zero_copy_stream_impl_lite.h）

- F-CPP-089: `class PROTOBUF_EXPORT CodedInputStream`（含 `bool ReadVarint32(uint32_t* value)` / `bool ReadVarint64(uint64_t* value)` / `bool ReadLittleEndian32(uint32_t* value)` / `bool ReadLittleEndian64(uint64_t* value)` / `Limit PushLimit(int byte_limit)` / `void PopLimit(Limit limit)`）—— io/coded_stream.h
- F-CPP-090: `class PROTOBUF_EXPORT CodedOutputStream`（含 `void WriteVarint32(uint32_t value)` / `void WriteVarint64(uint64_t value)` / `void WriteLittleEndian32(uint32_t value)` / `void WriteLittleEndian64(uint64_t value)` / `static size_t VarintSize32(uint32_t value)` / `static size_t VarintSize64(uint64_t value)`）—— io/coded_stream.h
- F-CPP-091: `class PROTOBUF_EXPORT ZeroCopyInputStream`（纯虚接口：`virtual bool Next(const void** data, int* size) = 0` / `virtual void BackUp(int count) = 0` / `virtual bool Skip(int count) = 0` / `virtual int64_t ByteCount() const = 0`）—— io/zero_copy_stream.h
- F-CPP-092: `class PROTOBUF_EXPORT ZeroCopyOutputStream`（纯虚接口：`virtual bool Next(void** data, int* size) = 0` / `virtual void BackUp(int count) = 0` / `virtual int64_t ByteCount() const = 0`）—— io/zero_copy_stream.h
- F-CPP-093: io/zero_copy_stream_impl_lite.h 类清单（行号）：`ArrayInputStream(46) : public ZeroCopyInputStream`、`ArrayOutputStream(83) : public ZeroCopyOutputStream`、`StringOutputStream(118) : public ZeroCopyOutputStream`、`CopyingInputStream(165)`、`CopyingInputStreamAdaptor(192) : public ZeroCopyInputStream`、`CopyingOutputStream(263)`、`CopyingOutputStreamAdaptor(280) : public ZeroCopyOutputStream`、`LimitingInputStream(350) : public ZeroCopyInputStream`、`CordInputStream(380) : public ZeroCopyInputStream`、`CordOutputStream(428) : public ZeroCopyOutputStream` —— io/zero_copy_stream_impl_lite.h

## 9. 文本格式与 JSON（text_format.h / util/json_util.h / json/）

- F-CPP-094: `class PROTOBUF_EXPORT TextFormat`（含 `static bool Print(const Message& message, io::ZeroCopyOutputStream* output)` / `static bool PrintToString(const Message& message, std::string* output)` / `static bool Parse(io::ZeroCopyInputStream* input, Message* output)` / `static bool ParseFromString(absl::string_view input, Message* output)`）—— text_format.h
- F-CPP-095: `class PROTOBUF_EXPORT Printer`（TextFormat 嵌套，含 `void SetUseShortRepeatedPrimitives(bool use_short)` / `bool PrintToString(const Message& message, std::string* output) const`）与 `class PROTOBUF_EXPORT Parser`（TextFormat 嵌套，含 `void AllowPartialMessage(bool allow)` / `bool ParseFromCodedStream(io::CodedInputStream* input, Message* output)`）—— text_format.h
- F-CPP-096: `struct ParseOptions { bool ignore_unknown_fields = false; bool case_insensitive_enum_parsing = false; }` 与 `struct PrintOptions { bool add_whitespace = false; bool always_print_fields_with_no_presence = false; bool always_print_enums_as_ints = false; bool preserve_proto_field_names = false; }` —— json/json.h
- F-CPP-097: `PROTOBUF_EXPORT absl::Status MessageToJsonString(const Message& message, std::string* output, const PrintOptions& options)` / `PROTOBUF_EXPORT absl::Status JsonStringToMessage(absl::string_view input, Message* message, const ParseOptions& options)` —— json/json.h
- F-CPP-098: json/ 目录文件清单：`json.cc`、`json.h`、`internal/{descriptor_traits.h, lexer.cc, lexer.h, lexer_test.cc, message_path.cc, message_path.h, parser.cc, parser.h, parser_traits.h, unparser.cc, unparser.h, unparser_traits.h, untyped_message.cc, untyped_message.h, writer.cc, writer.h, zero_copy_buffered_stream.cc, zero_copy_buffered_stream.h, zero_copy_buffered_stream_test.cc}`、`json_test.cc` —— json/（目录枚举）
- F-CPP-099: util/json_util.h 存在（与 json/json.h 并列）—— util/json_util.h

## 10. 容器（map.h / repeated_field.h / repeated_ptr_field.h）

- F-CPP-100: `class PROTOBUF_FUTURE_ADD_WARN_UNUSED Map final : private internal::KeyMapBase<internal::KeyForBase<Key>>` —— map.h
- F-CPP-101: Map 成员：`T& operator[](const key_arg<K>& key) ABSL_ATTRIBUTE_LIFETIME_BOUND` / `iterator begin()` / `iterator end()` / `size_type size() const` / `bool empty() const` / `std::pair<iterator, bool> insert(const value_type& value)` / `iterator find(const key_arg<K>& key)` / `size_type erase(const key_arg<K>& key)` / `void clear()` —— map.h
- F-CPP-102: `class ABSL_ATTRIBUTE_WARN_UNUSED RepeatedField final : private internal::RepeatedFieldBase` —— repeated_field.h
- F-CPP-103: RepeatedField 成员：`int size() const` / `bool empty() const` / `const_reference Get(int index) const` / `pointer Mutable(int index)` / `void Add(Element value)` / `void Add(const Element* begin, const Element* end)` / `void RemoveLast()` / `void Clear()` / `void Reserve(int new_size)` / `void Truncate(int new_size)` —— repeated_field.h
- F-CPP-104: `class RepeatedPtrField`（repeated_ptr_field.h，模板容器）—— repeated_ptr_field.h

## 11. 未知字段与扩展（unknown_field_set.h / extension_set.h）

- F-CPP-105: `class PROTOBUF_EXPORT UnknownField`（含 `enum Type { TYPE_VARINT, TYPE_FIXED32, TYPE_FIXED64, TYPE_LENGTH_DELIMITED, TYPE_GROUP }`）—— unknown_field_set.h
- F-CPP-106: UnknownField 成员：`Type type() const` / `uint64_t varint() const` / `uint32_t fixed32() const` / `uint64_t fixed64() const` / `absl::string_view length_delimited() const` / `const UnknownFieldSet& group() const` —— unknown_field_set.h
- F-CPP-107: `class PROTOBUF_EXPORT UnknownFieldSet`（含 `void Clear()` / `bool empty() const` / `int field_count() const` / `const UnknownField& field(int index) const` / `void AddVarint(int number, uint64_t value)` / `void AddFixed32(int number, uint32_t value)` / `void AddFixed64(int number, uint64_t value)` / `void AddLengthDelimited(int number, absl::string_view value)` / `UnknownField* AddGroup(int number)`）—— unknown_field_set.h
- F-CPP-108: `class PROTOBUF_EXPORT ExtensionSet`（extension_set.h:247，含 `constexpr ExtensionSet() = default` / `ExtensionSet(const ExtensionSet& rhs) = delete`）—— extension_set.h:247-253
- F-CPP-109: `static void RegisterExtension(const ClassData* extendee, int number, FieldType type, bool is_repeated, bool is_packed, bool is_utf8 = false)` / `static void RegisterEnumExtension(const ClassData* extendee, int number, FieldType type, bool is_repeated, bool is_packed, const uint32_t* validation_data)` / `static void RegisterMessageExtension(const ClassData* extendee, int number, FieldType type, bool is_repeated, bool is_packed, const ClassData* inner_data, LazyEagerVerifyFnType verify_func, LazyAnnotation is_lazy)` —— extension_set.h:260-272
- F-CPP-110: `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD bool Has(int number) const` / `int ExtensionSize(int number) const` / `int NumExtensions() const` / `FieldType ExtensionType(int number) const` / `void ClearExtension(int number)` —— extension_set.h:330-336
- F-CPP-111: `template <typename T> PROTOBUF_FUTURE_ADD_EARLY_NODISCARD const T& Get(int number, const internal::type_identity_t<T>& default_value) const` / `template <typename T, typename U> void Set(Arena* arena, int number, FieldType type, U&& value, const FieldDescriptor* descriptor)` —— extension_set.h:340-362
- F-CPP-112: `[[nodiscard]] const MessageLite& GetMessageByClassData(Arena* arena, int number, const ClassData* class_data) const` / `PROTOBUF_FUTURE_ADD_EARLY_NODISCARD const MessageLite& GetMessage(Arena* arena, int number, const Descriptor* message_type, MessageFactory* factory) const` —— extension_set.h:364-368
- F-CPP-113: `void AppendToList(const Descriptor* extendee, const DescriptorPool* pool, std::vector<const FieldDescriptor*>* output) const` / `bool IsEmpty() const` —— extension_set.h:292-298
- F-CPP-114: `struct ExtensionInfo`（含字段 `const MessageLite* message` / `int number` / `FieldType type` / `bool is_repeated` / `bool is_packed : 1` / `bool is_utf8 : 1` / `LazyAnnotation is_lazy` / `const FieldDescriptor* descriptor` / `LazyEagerVerifyFnType lazy_eager_verify_func`，含嵌套 `struct EnumValidityCheck` 与 `struct MessageInfo`）—— extension_set.h:124-186
- F-CPP-115: `class PROTOBUF_EXPORT GeneratedExtensionFinder`（含 `bool Find(int number, ExtensionInfo* output)`，构造 `explicit GeneratedExtensionFinder(const MessageLite* extendee)`）—— extension_set.h:196-207
- F-CPP-116: `class PROTOBUF_EXPORT DescriptorPoolExtensionFinder`（构造 `DescriptorPoolExtensionFinder(const DescriptorPool* pool, MessageFactory* factory, const Descriptor* extendee)`，含 `bool Find(int number, ExtensionInfo* output)`）—— extension_set.h:212-226
- F-CPP-117: `enum class LazyAnnotation : int8_t { kUndefined = 0, kLazy = 1, kEager = 2 }` —— extension_set.h:115-119
- F-CPP-118: `typedef uint8_t FieldType`（extension_set.h:109，internal 命名空间内）—— extension_set.h

## 12. ClassData 与反射模式（class_data.h / generated_message_reflection.h）

- F-CPP-119: `struct PROTOBUF_EXPORT ClassData`（含 `bool (*is_initialized)(const MessageLite&)` / `void (*merge_to_from)(MessageLite& to, const MessageLite& from_msg)` / `internal::MessageCreator message_creator` / `uint32_t cached_size_offset` / `bool is_lite` / `bool is_dynamic = false`）—— class_data.h:156
- F-CPP-120: ClassData 中 PROTOBUF_CUSTOM_VTABLE 条件编译块：`void (*destroy_message)(MessageLite& msg)` / `void (*clear)(MessageLite& msg)` / `size_t (*byte_size_long)(const MessageLite&)` / `uint8_t* (*serialize)(const MessageLite& msg, uint8_t* ptr, io::EpsCopyOutputStream* stream)` —— class_data.h:160-166
- F-CPP-121: `struct PROTOBUF_EXPORT ReflectionData`（含 `const Reflection* reflection` / `const Descriptor* descriptor` / `const internal::DescriptorTable* descriptor_table` / `const DescriptorMethods* descriptor_methods` / `void (*get_metadata_tracker)()`）—— class_data.h:120-145
- F-CPP-122: `class MessageCreator`（含 `using Func = void* (*)(const void*, void*, Arena*)` / `enum Tag : int8_t { kFunc = -1, kZeroInit = 0, kMemcpy = 1 }` / `static constexpr MessageCreator ZeroInit(uint32_t allocation_size, uint8_t alignment)` / `static constexpr MessageCreator CopyInit(uint32_t allocation_size, uint8_t alignment)` / `Tag tag() const` / `uint32_t allocation_size() const` / `uint8_t alignment() const`）—— class_data.h:49-113
- F-CPP-123: `class ReflectionSchema`（含构造 `ReflectionSchema(const Message* default_instance, const uint32_t* offsets, const uint32_t* has_bit_indices, int has_bits_offset, int extensions_offset, int oneof_case_offset, int object_size, int split_offset, int sizeof_split)` / `static ReflectionSchema MigrationToReflectionSchema(...)` / `uint32_t GetFieldOffset(const FieldDescriptor* field) const` / `uint32_t GetOneofCaseOffset(const OneofDescriptor* oneof_descriptor) const` / `bool HasHasbits() const` / `bool HasExtensionSet() const` / `const void* GetFieldDefault(const FieldDescriptor* field) const`）—— generated_message_reflection.h:127-213
- F-CPP-124: `struct MigrationSchema { int32_t offsets_index; int object_size; }` —— generated_message_reflection.h:79-82
- F-CPP-125: 偏移标记常量：`inline constexpr uint32_t kSplitFieldOffsetTag = 0x80000000u` / `kLazyOffsetTag = 0x40000000u` / `kInlinedOffsetTag = 0x40000000u` / `kMicroStringOffsetTag = 0x20000000u` / `kAllOffsetTags` —— generated_message_reflection.h:64-71

## 13. Well-Known Types（proto 文件与 any.h）

- F-CPP-126: `message Any`（any.proto:72）与 any.h 中 `class Any` 的 `bool PackFrom(const ::google::protobuf::Message& message)` / `bool UnpackTo(::google::protobuf::Message* message) const` / `template <typename T> bool Is() const` —— any.proto:72 / any.h
- F-CPP-127: `message Duration`（duration.proto:102），字段 `int64 seconds = 1` / `int32 nanos = 2` —— duration.proto:102-114
- F-CPP-128: `message Timestamp`（timestamp.proto:133），字段 `int64 seconds = 1` / `int32 nanos = 2` —— timestamp.proto:133-144
- F-CPP-129: struct.proto 消息：`message Struct(56)` / `message Value(67)` / `message ListValue(108)` / `enum NullValue(102)` —— struct.proto
- F-CPP-130: wrappers.proto 消息：`DoubleValue(66) FloatValue(77) Int64Value(88) UInt64Value(99) Int32Value(110) UInt32Value(121) BoolValue(132) StringValue(143) BytesValue(154)`（Int64Value 含 `int64 value = 1`，Int32Value 含 `int32 value = 1`）—— wrappers.proto
- F-CPP-131: type.proto 消息与枚举：`message Type(52)` / `message Field(75)`（含 `int32 number = 3`、`int32 oneof_index = 7`）/ `message Enum(160)` / `message EnumValue(181)`（含 `int32 number = 2`）/ `message Option(196)` / `enum Syntax(210)` —— type.proto
- F-CPP-132: api.proto 消息：`message Api(59)` / `message Method(112)` / `message Mixin(222)` —— api.proto
- F-CPP-133: `message SourceContext`（source_context.proto:44）—— source_context.proto
- F-CPP-134: `message FieldMask`（field_mask.proto:240）—— field_mask.proto
- F-CPP-135: `message Empty {}`（empty.proto:51）—— empty.proto
- F-CPP-136: `message CppFeatures`（cpp_features.proto:18）与 `namespace pb { class CppFeatures; }`（extension_set.h:83-85）—— cpp_features.proto:18 / extension_set.h:83
- F-CPP-137: `message TestAny`（any_test.proto:16）—— any_test.proto

## 14. 其他运行时核心文件

- F-CPP-138: `feature_resolver.h` 存在于 src/google/protobuf/ 根目录 —— feature_resolver.h
- F-CPP-139: `editions/` 目录不存在于 src/google/protobuf/ 层级（目录枚举返回不存在；editions 相关内容位于 feature_resolver.h 与 descriptor.proto 的 FeatureSet/FeatureSetDefaults）—— 目录枚举
- F-CPP-140: port_def.inc 防重入宏：`#ifdef PROTOBUF_PORT_ #error "port_def.inc included multiple times" #endif #define PROTOBUF_PORT_`（port_def.inc:29-32）—— port_def.inc:29-32
- F-CPP-141: `descriptor_lite.h` 存在（含 internal::FieldDescriptorLite 基类）—— descriptor_lite.h
- F-CPP-142: `generated_message_reflection.h` 内 internal 命名空间声明 `class ExtensionSet;  // extension_set.h` —— generated_message_reflection.h:59
- F-CPP-143: extension_set.h 前向声明：`class Arena; class Descriptor; class FieldDescriptor; class DescriptorPool; class MessageLite; class Message; class MessageFactory; class Reflection; class UnknownFieldSet; class FeatureSet;`（extension_set.h:62-71）—— extension_set.h:62-71
- F-CPP-144: `class_data.h` 头部注释原文："Defines ClassData, the structure that contains type information about messages. Used to implement reflection, parsing, dynamic casting, and other runtime features."（class_data.h:8-10）—— class_data.h:8-10

---

## 事实统计

- **事实总条数：144 条**（F-CPP-001 ~ F-CPP-144）
- **采集深度**：类/方法签名级（含枚举完整值、模板参数、默认参数值）

## 覆盖模块清单

| # | 模块 | 关键文件 | 事实区间 |
|---|---|---|---|
| 1 | 消息基类 | message_lite.h, message.h | F-CPP-001~012 |
| 2 | Reflection 反射类 | message.h | F-CPP-013~035 |
| 3 | Arena 内存分配 | arena.h, arenastring.h | F-CPP-036~041 |
| 4 | 描述符类 | descriptor.h | F-CPP-042~062 |
| 5 | descriptor 生成类与 Edition 枚举 | descriptor.pb.h, descriptor.proto | F-CPP-063~068 |
| 6 | 描述符数据库 | descriptor_database.h | F-CPP-069~074 |
| 7 | Wire Format | wire_format_lite.h, wire_format.h | F-CPP-075~088 |
| 8 | IO 流 | io/coded_stream.h, io/zero_copy_stream.h, io/zero_copy_stream_impl_lite.h | F-CPP-089~093 |
| 9 | 文本格式与 JSON | text_format.h, json/json.h, util/json_util.h, json/ | F-CPP-094~099 |
| 10 | 容器 | map.h, repeated_field.h, repeated_ptr_field.h | F-CPP-100~104 |
| 11 | 未知字段与扩展 | unknown_field_set.h, extension_set.h | F-CPP-105~118 |
| 12 | ClassData 与反射模式 | class_data.h, generated_message_reflection.h | F-CPP-119~125 |
| 13 | Well-Known Types | any.h, duration.proto, timestamp.proto, struct.proto, wrappers.proto, type.proto, api.proto, source_context.proto, field_mask.proto, empty.proto, cpp_features.proto | F-CPP-126~137 |
| 14 | 其他运行时核心文件 | feature_resolver.h, port_def.inc, descriptor_lite.h | F-CPP-138~144 |

- 源码根全程只读，未修改任何源码文件
