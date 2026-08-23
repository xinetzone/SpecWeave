# TVM FFI 事实清单

> 每条事实包含源码路径与行号，仅陈述代码中可见内容，不含推测。

## 一、C ABI 层 (c_api.h)

- **F-001**: `TVMFFITypeIndex` 枚举定义在 `include/tvm/ffi/c_api.h:46`，包含 `kTVMFFITypeIndexUnknown = -1`。
- **F-002**: `kTVMFFITypeIndexInt32 = 0`、`kTVMFFITypeIndexUInt32 = 1`、`kTVMFFITypeIndexInt64 = 2`、`kTVMFFITypeIndexUInt64 = 3`，见 `include/tvm/ffi/c_api.h:48-51`。
- **F-003**: `kTVMFFITypeIndexFloat32 = 4`、`kTVMFFITypeIndexFloat64 = 5`，见 `include/tvm/ffi/c_api.h:52-53`。
- **F-004**: `kTVMFFITypeIndexHandle = 6`、`kTVMFFITypeIndexNull = 7`、`kVMFFITypeIndexAny = 8`，见 `include/tvm/ffi/c_api.h:54-56`。
- **F-005**: `kTVMFFITypeIndexTVMFFITypeIndex = 9`、`kTVMFFITypeIndexDataType = 10`、`kTVMFFITypeIndexDevice = 11`，见 `include/tvm/ffi/c_api.h:57-59`。
- **F-006**: `kTVMFFITypeIndexBool = 12`、`kTVMFFITypeIndexBytes = 13`、`kTVMFFITypeIndexString = 14`，见 `include/tvm/ffi/c_api.h:60-62`。
- **F-007**: `kTVMFFITypeIndexFunction = 15`、`kTVMFFITypeIndexObject = 16`，见 `include/tvm/ffi/c_api.h:63-64`。
- **F-008**: `kTVMFFITypeIndexArray = 17`、`kTVMFFITypeIndexList = 18`、`kTVMFFITypeIndexMap = 19`、`kTVMFFITypeIndexDict = 20`，见 `include/tvm/ffi/c_api.h:65-68`。
- **F-009**: `kTVMFFITypeIndexTuple = 21`、`kTVMFFITypeIndexVariant = 22`，见 `include/tvm/ffi/c_api.h:69-70`。
- **F-010**: `kTVMFFITypeIndexTensor = 23`、`kTVMFFITypeIndexShape = 24`、`kTVMFFITypeIndexScalar = 25`，见 `include/tvm/ffi/c_api.h:71-73`。
- **F-011**: `kTVMFFITypeIndexNDArrayHandle = 26`、`kTVMFFITypeIndexDLTensor = 27`、`kTVMFFITypeIndexError = 28`，见 `include/tvm/ffi/c_api.h:74-76`。
- **F-012**: 动态类型索引起始值 `kTVMFFITypeIndexDynamicBegin = 1000`，见 `include/tvm/ffi/c_api.h:80`。
- **F-013**: `TVMFFIObject` 结构体包含 `type_index_`（int32_t）和 `refcount_`（int32_t），见 `include/tvm/ffi/c_api.h:86-90`。
- **F-014**: `TVMFFIAny` 是一个联合体，包含 `int64_t v_int64`、`uint64_t v_uint64`、`double v_float64`、`void* v_handle`、`TVMFFIDataType v_dtype`、`TVMFFIDevice v_device`，见 `include/tvm/ffi/c_api.h:100-112`。
- **F-015**: `TVMFFIAny` 联合体还包含 `TVMFFITypeIndex v_type_index`（类型 int32_t）和 `int32_t padding`，见 `include/tvm/ffi/c_api.h:113-114`。
- **F-016**: `TVMFFISafeCallType` 定义为 `void* (*)(TVMFFIAny* args, int num_args, TVMFFIAny* rv, int* err)`，见 `include/tvm/ffi/c_api.h:131`。
- **F-017**: `TVMFFIFunction` 结构体仅包含 `TVMFFISafeCallType safe_call`，见 `include/tvm/ffi/c_api.h:139-141`。
- **F-018**: `TVMFFIGetVersion()` 返回版本字符串，见 `include/tvm/ffi/c_api.h:155`。
- **F-019**: `TVMFFIObjectIncRef`/`TVMFFIObjectDecRef` 接受 `TVMFFIObject*` 参数，见 `include/tvm/ffi/c_api.h:166-168`。
- **F-020**: `TVMFFIFunctionCreate` 接受 `TVMFFISafeCallType safe_call`、`TVMFFIObjectFreeFunc free_func`、`void* resource` 和 `TVMFFIFunction** out`，见 `include/tvm/ffi/c_api.h:180-183`。
- **F-021**: `TVMFFIFuncListGlobalNames` 返回全局函数名称列表，见 `include/tvm/ffi/c_api.h:215`。
- **F-022**: `TVMFFIFuncCall` 接受 `TVMFFIFunctionHandle func`、`TVMFFIAny* args`、`int num_args`、`TVMFFIAny* rv`，见 `include/tvm/ffi/c_api.h:242-245`。
- **F-023**: `TVMFFITypeKey2Index` 和 `TVMFFITypeIndex2Key` 实现类型键与类型索引的双向转换，见 `include/tvm/ffi/c_api.h:274-278`。
- **F-024**: `TVMFFIStructuralEqual` 和 `TVMFFIStructuralHash` 是 C API 层结构比较与哈希入口，见 `include/tvm/ffi/c_api.h:308-313`。
- **F-025**: `TVMFFIRuntimeEnabled` 检查某运行时特性是否启用，见 `include/tvm/ffi/c_api.h:332`。
- **F-026**: `TVMFFIGetLastError` 返回 `const char*`，`TVMFFISetLastError` 接受 `const char* msg`，见 `include/tvm/ffi/c_api.h:349-351`。
- **F-027**: `TVMFFICStringFree` 接受 `const char* str`，见 `include/tvm/ffi/c_api.h:355`。
- **F-028**: `TVMFFIThrowableGetMessage`、`TVMFFIThrowableGetKind`、`TVMFFIThrowableGetTraceback` 从异常对象提取信息，见 `include/tvm/ffi/c_api.h:376-385`。
- **F-029**: `TVMFFIThrowableGetCause` 返回 `TVMFFIObjectHandle` 链式原因，见 `include/tvm/ffi/c_api.h:387`。
- **F-030**: `TVMFFIThrowableGetExtraContext` 返回 `const char*`，见 `include/tvm/ffi/c_api.h:389`。
- **F-031**: `TVMFFIThrowableAppendContext` 接受 `TVMFFIObjectHandle throwable` 和 `const char* context`，见 `include/tvm/ffi/c_api.h:391`。
- **F-032**: `TVMFFIThrowableToAny` 将异常对象转为 `TVMFFIAny`，见 `include/tvm/ffi/c_api.h:394`。
- **F-033**: `TVMFFIReflectionVTableGet` 接受 `int32_t type_index` 返回 `TVMFFIReflectionVTable*`，见 `include/tvm/ffi/c_api.h:410`。
- **F-034**: `TVMFFIReflectionVTable` 包含 `VisitAttrsFunc`、`SEqualReduceFunc`、`SHashReduceFunc` 等函数指针，见 `include/tvm/ffi/c_api.h:415-435`。
- **F-035**: `TVMFFIFieldKind` 枚举包含 `kFieldInfoNormal = 0` 和 `kFieldInfoMethod = 1`，见 `include/tvm/ffi/c_api.h:440-443`。
- **F-036**: `TVMFFIFieldInfo` 结构体包含 `name`（const char*）、`kind`（TVMFFIFieldKind）、`offset`（uint32_t）、`type_key`（const char*），见 `include/tvm/ffi/c_api.h:446-451`。
- **F-037**: `TVMFFIObjectDef` 包含 `type_key`、`type_index`、`num_fields`、`fields` 指针、`parent_type_index`、`size`，见 `include/tvm/ffi/c_api.h:462-475`。
- **F-038**: `TVMFFIObjectDefRegister` 接受 `const TVMFFIObjectDef* def` 返回 `int`，见 `include/tvm/ffi/c_api.h:480`。
- **F-039**: `TVMFFIObjectDefRegisterWithInit` 额外接受 `TVMFFIObjectInitFunc init_func`，见 `include/tvm/ffi/c_api.h:482`。
- **F-040**: `TVMFFISetCustomClassAllocator` 接受类型索引和 `TVMFFIObjectAllocFunc`/`TVMFFIObjectFreeFunc`，见 `include/tvm/ffi/c_api.h:510-513`。
- **F-041**: `TVMFFIObjectNew` 接受类型索引、`TVMFFIObjectHandle* out` 返回 `int`，见 `include/tvm/ffi/c_api.h:520`。
- **F-042**: `TVMFFISeqableGetItem` 接受对象句柄、索引（int64_t）、`TVMFFIAny* out`，见 `include/tvm/ffi/c_api.h:537`。
- **F-043**: `TVMFFISeqableSize` 接受对象句柄，`int64_t* out` 返回大小，见 `include/tvm/ffi/c_api.h:539`。
- **F-044**: `TVMFFIMappingGetItem` 接受对象句柄、`TVMFFIAny* key`、`TVMFFIAny* out`，见 `include/tvm/ffi/c_api.h:555`。
- **F-045**: `TVMFFIMappingSize`、`TVMFFIMappingContains`、`TVMFFIMappingPop` 实现映射操作，见 `include/tvm/ffi/c_api.h:557-563`。
- **F-046**: `TVMFFIMappingIterate` 接受迭代器状态和 `TVMFFIMappingIterCallback`，见 `include/tvm/ffi/c_api.h:572-576`。
- **F-047**: `TVMFFIArraySetItem`、`TVMFFIArrayGetItem`、`TVMFFIArraySize` 操作数组容器，见 `include/tvm/ffi/c_api.h:592-600`。
- **F-048**: `TVMFFIListPushBack`、`TVMFFIListPop`、`TVMFFIListSize` 操作列表容器，见 `include/tvm/ffi/c_api.h:620-625`。
- **F-049**: `TVMFFIDictGetItem`、`TVMFFIDictSetItem`、`TVMFFIDictSize` 操作字典容器，见 `include/tvm/ffi/c_api.h:648-656`。
- **F-050**: `TVMFFITupleGetItem`、`TVMFFITupleSize` 操作元组容器，见 `include/tvm/ffi/c_api.h:680-683`。
- **F-051**: `TVMFFIVariantGetIndex` 和 `TVMFFIVariantGetValue` 操作变体类型，见 `include/tvm/ffi/c_api.h:700-703`。
- **F-052**: `TVMFFIStructNew`、`TVMFFIStructGetField`、`TVMFFIStructSetField` 操作结构体容器，见 `include/tvm/ffi/c_api.h:728-735`。
- **F-053**: `TVMFFITensorMake` 接受 shape、stride、dtype、device、data、offset 返回张量对象，见 `include/tvm/ffi/c_api.h:758-764`。
- **F-054**: `TVMFFITensorGetView` 接受张量句柄和 `DLManagedTensor** out`，见 `include/tvm/ffi/c_api.h:770`。
- **F-055**: `TVMFFIBytesCreateFromData` 从字节数据创建 Bytes 对象，见 `include/tvm/ffi/c_api.h:790-794`。
- **F-056**: `TVMFFIBytesGetData` 获取 Bytes 对象的数据指针和长度，见 `include/tvm/ffi/c_api.h:798`。
- **F-057**: `TVMFFIStringCreateFromData` 从字节数据创建 String 对象，见 `include/tvm/ffi/c_api.h:814-817`。
- **F-058**: `TVMFFIStringGetData` 获取 String 对象的数据指针和长度，见 `include/tvm/ffi/c_api.h:822`。
- **F-059**: `TVMFFIFunctionNewFromCallback` 从 C 回调创建函数对象，见 `include/tvm/ffi/c_api.h:858-862`。
- **F-060**: `TVMFFIPointerIsAlive`、`TVMFFIPointerDecWeakRef`、`TVMFFIPointerLock` 管理弱引用指针，见 `include/tvm/ffi/c_api.h:890-903`。
- **F-061**: `TVMFFICtxSetLastError`/`TVMFFICtxGetLastError` 管理线程局部错误，见 `include/tvm/ffi/c_api.h:919-921`。
- **F-062**: `TVMFFIRegisterFinalizer` 注册对象终结器，接受类型索引和 `TVMFFIObjectFreeFunc`，见 `include/tvm/ffi/c_api.h:940`。
- **F-063**: `TVMFFIBacktraceCapture` 捕获回溯，`TVMFFIBacktraceGetFrames` 获取帧信息，见 `include/tvm/ffi/c_api.h:958-966`。
- **F-064**: `TVMFFI_CONTAINER_ALIGNED_BYTES = 16`，容器内联存储对齐字节数，见 `include/tvm/ffi/c_api.h:1003`。
- **F-065**: `TVMFFIArrayAllocate` 接受 capacity、elem_type_index、elem_bytes 返回 `TVMFFIArrayHandle`，见 `include/tvm/ffi/c_api.h:1025-1028`。
- **F-066**: `TVMFFIArrayGetCapacity`、`TVMFFIArrayGetSize`、`TVMFFIArraySetSize` 管理数组容量与大小，见 `include/tvm/ffi/c_api.h:1032-1036`。
- **F-067**: `TVMFFIArrayGetData` 返回 `void*` 指向数组数据，见 `include/tvm/ffi/c_api.h:1043`。
- **F-068**: `TVMFFIListGetCapacity`、`TVMFFIListGetSize`、`TVMFFIListSetSize` 管理列表容量与大小，见 `include/tvm/ffi/c_api.h:1062-1066`。
- **F-069**: `TVMFFIListGetData` 返回 `void*` 指向列表数据，见 `include/tvm/ffi/c_api.h:1073`。
- **F-070**: `TVMFFIDictAllocate` 接受 capacity、key_type_index、value_type_index、key_bytes、value_bytes 返回字典句柄，见 `include/tvm/ffi/c_api.h:1098-1102`。
- **F-071**: `TVMFFIDictReHash` 重新哈希字典，`TVMFFIDictGetSize`/`TVMFFIDictGetCapacity` 获取大小和容量，见 `include/tvm/ffi/c_api.h:1108-1112`。
- **F-072**: `TVMFFIDictGetIndex` 根据 key 查找索引，`TVMFFIDictGetKeyAt`/`TVMFFIDictGetValueAt` 按索引访问，见 `include/tvm/ffi/c_api.h:1120-1131`。
- **F-073**: `TVMFFIDictSetValueAt` 按索引设置值，`TVMFFIDictEraseAt` 按索引删除，见 `include/tvm/ffi/c_api.h:1135-1138`。
- **F-074**: `TVMFFIMapAllocate`、`TVMFFIMapGetSize`、`TVMFFIMapIndex`、`TVMFFIMapGetKeyAt`、`TVMFFIMapGetValueAt`、`TVMFFIMapEraseAt` 提供 Map 容器 C API，见 `include/tvm/ffi/c_api.h:1166-1196`。

## 二、C++ 核心类型 (any.h / object.h / function.h)

### Any / AnyView

- **F-075**: `AnyView` 类定义在 `include/tvm/ffi/any.h:55`，是类型擦除值的非持有视图。
- **F-076**: `AnyView` 包含 `TVMFFIAny value_` 数据成员，见 `include/tvm/ffi/any.h:57`。
- **F-077**: `AnyView::type_index()` 返回 `TVMFFITypeIndex`，见 `include/tvm/ffi/any.h:61`。
- **F-078**: `AnyView::IsNone()`、`AnyView::IsBool()`、`AnyView::IsInt()`、`AnyView::IsFloat()` 是类型检查方法，见 `include/tvm/ffi/any.h:69-72`。
- **F-079**: `AnyView::IsObject()`、`AnyView::IsFunction()`、`AnyView::IsString()`、`AnyView::IsBytes()` 是对象类型检查方法，见 `include/tvm/ffi/any.h:73-76`。
- **F-080**: `AnyView::IsArray()`、`AnyView::IsList()`、`AnyView::IsMap()`、`AnyView::IsDict()` 是容器类型检查方法，见 `include/tvm/ffi/any.h:77-80`。
- **F-081**: `AnyView::IsTensor()`、`AnyView::IsShape()`、`AnyView::IsScalar()` 是张量相关类型检查方法，见 `include/tvm/ffi/any.h:81-83`。
- **F-082**: `AnyView::IsError()` 检查是否为错误对象，见 `include/tvm/ffi/any.h:84`。
- **F-083**: `AnyView::operator int()`、`AnyView::operator int64_t()`、`AnyView::operator double()`、`AnyView::operator bool()` 提供隐式转换，见 `include/tvm/ffi/any.h:93-96`。
- **F-084**: `AnyView::operator std::string()` 提供字符串转换，见 `include/tvm/ffi/any.h:97`。
- **F-085**: `Any` 类继承自 `AnyView`，定义在 `include/tvm/ffi/any.h:560`，是持有型类型擦除容器。
- **F-086**: `Any` 的拷贝构造函数对对象类型执行 `ObjectIncRef`，析构函数执行 `ObjectDecRef`，见 `include/tvm/ffi/any.h:575-603`。
- **F-087**: `Any::operator=(const Any& other)` 自赋值安全，先增加新引用再减少旧引用，见 `include/tvm/ffi/any.h:612-626`。
- **F-088**: `Any` 的移动构造函数从源对象接管数据，并将源置为 null，见 `include/tvm/ffi/any.h:628-643`。
- **F-089**: `Any::Any(int value)` 设置 `type_index_ = kTVMFFITypeIndexInt64`，`v_int64 = value`，见 `include/tvm/ffi/any.h:670`。
- **F-090**: `Any::Any(double value)` 设置 `type_index_ = kTVMFFITypeIndexFloat64`，`v_float64 = value`，见 `include/tvm/ffi/any.h:672`。
- **F-091**: `Any::Any(std::nullptr_t)` 设置 `type_index_ = kTVMFFITypeIndexNull`，见 `include/tvm/ffi/any.h:674`。
- **F-092**: `Any::Any(const char* value)` 从 C 字符串创建 String 对象，见 `include/tvm/ffi/any.h:682`。
- **F-093**: `Any::Any(const std::string& value)` 从 std::string 创建 String 对象，见 `include/tvm/ffi/any.h:684`。
- **F-094**: `Any::Any(const AnyView& other)` 从 AnyView 构造，若为对象类型则增加引用计数，见 `include/tvm/ffi/any.h:700-715`。
- **F-095**: `Any::Cast<T>()` 执行类型转换，见 `include/tvm/ffi/any.h:780`。
- **F-096**: `Any::TryCast<T>()` 返回 `std::optional<T>`，失败时返回 `std::nullopt`，见 `include/tvm/ffi/any.h:792`。
- **F-097**: `Any::operator==(const Any& other)` 委托给 `StructuralEqual`，见 `include/tvm/ffi/any.h:810`。
- **F-098**: `Any::operator<(const Any& other)` 对基础类型直接比较，对对象调用 `StructuralHash` 后比较，见 `include/tvm/ffi/any.h:824-846`。

### Object / ObjectPtr / ObjectRef

- **F-099**: `Object` 类定义在 `include/tvm/ffi/object.h:109`，继承自 `TVMFFIObject`。
- **F-100**: `Object` 声明 `static constexpr const char* _type_key = "ffi.Object"`，见 `include/tvm/ffi/object.h:111`。
- **F-101**: `Object` 声明 `static constexpr const uint32_t _type_index = kTVMFFITypeIndexObject`，见 `include/tvm/ffi/object.h:112`。
- **F-102**: `Object` 声明 `static constexpr const uint32_t _type_child_slots = 0`，见 `include/tvm/ffi/object.h:115`。
- **F-103**: `Object::TypeIndex()` 返回 `_type_index`，见 `include/tvm/ffi/object.h:128`。
- **F-104**: `Object::GetTypeKey()` 返回 `_type_key`，见 `include/tvm/ffi/object.h:130`。
- **F-105**: `Object::unique()` 检查 `refcount_ == 1`，见 `include/tvm/ffi/object.h:138`。
- **F-106**: `Object::IncRef()` 和 `Object::DecRef()` 操作 `refcount_`，见 `include/tvm/ffi/object.h:141-146`。
- **F-107**: `Object::use_count()` 返回 `refcount_`，见 `include/tvm/ffi/object.h:148`。
- **F-108**: `TVM_FFI_DECLARE_OBJECT_INFO` 宏定义在 `include/tvm/ffi/object.h:212`，声明 `_type_key`、`_type_index`、`_type_child_slots`、`_GetOrAllocTypeIndex()`。
- **F-109**: `TVM_FFI_DECLARE_OBJECT_INFO_FINAL` 宏额外声明 `_type_final = true`，见 `include/tvm/ffi/object.h:221`。
- **F-110**: `TVM_FFI_DEFINE_OBJECT_INFO_METHODS_NOTNULLABLE` 宏定义 ObjectRef 的访问方法，见 `include/tvm/ffi/object.h:228`。
- **F-111**: `ObjectPtr<T>` 模板类定义在 `include/tvm/ffi/object.h:320`，管理 `T* data_`。
- **F-112**: `ObjectPtr<T>` 的拷贝构造函数调用 `IncRef`，析构函数调用 `DecRef`，见 `include/tvm/ffi/object.h:335-358`。
- **F-113**: `ObjectPtr<T>::operator->()` 返回 `data_`，见 `include/tvm/ffi/object.h:397`。
- **F-114**: `ObjectPtr<T>::get()` 返回 `data_`，见 `include/tvm/ffi/object.h:399`。
- **F-115**: `ObjectPtr<T>::reset()` 释放当前引用并置空，见 `include/tvm/ffi/object.h:401`。
- **F-116**: `ObjectPtr<T>::use_count()` 返回 `data_->use_count()`，见 `include/tvm/ffi/object.h:412`。
- **F-117**: `ObjectPtr<T>::unique()` 返回 `data_->unique()`，见 `include/tvm/ffi/object.h:414`。
- **F-118**: `ObjectPtr<T>::operator==(const ObjectPtr<T>& other)` 比较 `data_` 指针，见 `include/tvm/ffi/object.h:422`。
- **F-119**: `ObjectPtr<T>::operator<(const ObjectPtr<T>& other)` 比较 `data_` 指针，见 `include/tvm/ffi/object.h:425`。
- **F-120**: `make_object<T>(Args&&... args)` 创建 `ObjectPtr<T>`，使用 `new T(std::forward<Args>(args)...)`，见 `include/tvm/ffi/object.h:444-447`。
- **F-121**: `make_inplace_array_object<T, ArrayType, ElemType>` 支持内联数组分配，见 `include/tvm/ffi/object.h:488`。
- **F-122**: `WeakObjectPtr<T>` 模板类定义在 `include/tvm/ffi/object.h:559`，不增加引用计数。
- **F-123**: `WeakObjectPtr<T>::lock()` 返回 `ObjectPtr<T>`，若对象已释放则返回空，见 `include/tvm/ffi/object.h:597`。
- **F-124**: `ObjectRef` 类定义在 `include/tvm/ffi/object.h:652`，包含 `ObjectPtr<Object> data_`。
- **F-125**: `ObjectRef::defined()` 检查 `data_ != nullptr`，见 `include/tvm/ffi/object.h:670`。
- **F-126**: `ObjectRef::operator bool()` 返回 `defined()`，见 `include/tvm/ffi/object.h:672`。
- **F-127**: `ObjectRef::same_as(const ObjectRef& other)` 比较 `data_ == other.data_`，见 `include/tvm/ffi/object.h:680`。
- **F-128**: `ObjectRef::use_count()` 返回 `data_->use_count()`，见 `include/tvm/ffi/object.h:682`。
- **F-129**: `ObjectRef::unique()` 返回 `data_->unique()`，见 `include/tvm/ffi/object.h:684`。
- **F-130**: `ObjectRef::get()` 返回 `data_.get()`，见 `include/tvm/ffi/object.h:705`。
- **F-131**: `ObjectRef::operator==(const ObjectRef& other)` 委托 `StructuralEqual`，见 `include/tvm/ffi/object.h:720`。
- **F-132**: `ObjectRef::operator<(const ObjectRef& other)` 委托 `StructuralHash` 后比较哈希值，见 `include/tvm/ffi/object.h:730`。
- **F-133**: `Downcast<T>(const ObjectRef& ref)` 执行运行时类型检查后转换，见 `include/tvm/ffi/object.h:1415`。
- **F-134**: `Downcast<T>(const ObjectPtr<TSrc>& ptr)` 对指针版本执行类型检查，见 `include/tvm/ffi/object.h:1450`。

### Function / PackedArgs

- **F-135**: `Function` 类定义在 `include/tvm/ffi/function.h:98`，继承自 `ObjectRef`。
- **F-136**: `Function::_type_key = "ffi.Function"`，`_type_index = kTVMFFITypeIndexFunction`，见 `include/tvm/ffi/function.h:100-101`。
- **F-137**: `Function::operator()(Args... args)` 接受任意参数，返回 `Any`，见 `include/tvm/ffi/function.h:120`。
- **F-138**: `Function::CallAny(const Any* args, size_t num_args)` 执行调用，返回 `Any`，见 `include/tvm/ffi/function.h:140`。
- **F-139**: `Function::CallPacked(TVMFFIAny* args, size_t num_args, TVMFFIAny* rv)` 直接调用 C ABI，见 `include/tvm/ffi/function.h:147`。
- **F-140**: `Function::FromCallback` 静态方法从 C++ lambda 创建 `Function`，见 `include/tvm/ffi/function.h:158`。
- **F-141**: `Function::GetGlobalFunction` 静态方法按名称获取全局注册函数，见 `include/tvm/ffi/function.h:165`。
- **F-142**: `Function::RegisterGlobal` 静态方法注册全局函数，接受名称和 `Function`，见 `include/tvm/ffi/function.h:170`。
- **F-143**: `Function::ListGlobalNames` 静态方法返回所有全局函数名称，见 `include/tvm/ffi/function.h:175`。
- **F-144**: `PackedArgs` 类定义在 `include/tvm/ffi/function.h:240`，包含 `const TVMFFIAny* values_` 和 `size_t size_`。
- **F-145**: `PackedArgs::operator[](size_t i)` 返回 `AnyView`，见 `include/tvm/ffi/function.h:252`。
- **F-146**: `PackedArgs::size()` 返回参数数量，见 `include/tvm/ffi/function.h:258`。
- **F-147**: `PackedArgs::begin()`/`end()` 返回 `AnyView` 迭代器，见 `include/tvm/ffi/function.h:260-268`。
- **F-148**: `ReturnValue` 类定义在 `include/tvm/ffi/function.h:306`，封装 `TVMFFIAny*` 引用，支持从多种类型赋值，见 `include/tvm/ffi/function.h:306-360`。
- **F-149**: `TypedFunction<R(Args...)>` 模板类包装 `Function`，提供类型安全调用，见 `include/tvm/ffi/function.h:540`。
- **F-150**: `FuncRegistry` 类定义在 `include/tvm/ffi/function.h:640`，支持链式调用 `.set_body().set_body_method().def()`，见 `include/tvm/ffi/function.h:640-780`。
- **F-151**: `TVM_FFI_REGISTER_GLOBAL(Name)` 宏注册全局函数，展开为静态 `FuncRegistry` 对象，见 `include/tvm/ffi/function.h:800`。
- **F-152**: `TVM_FFI_REGISTER_FUNC(Name)` 宏同 `TVM_FFI_REGISTER_GLOBAL`，见 `include/tvm/ffi/function.h:810`。

## 三、容器类型 (container/*.h)

### Array / List / Map / Dict

- **F-153**: `ArrayNode` 定义在 `include/tvm/ffi/container/array.h:45`，继承自 `Object`，内联存储容量为 16。
- **F-154**: `ArrayNode` 的 `_type_key = "ffi.ArrayNode"`，见 `include/tvm/ffi/container/array.h:52`。
- **F-155**: `ArrayNode::GetSize()` 返回 `size_`，`GetCapacity()` 返回 `capacity_`，见 `include/tvm/ffi/container/array.h:72-73`。
- **F-156**: `ArrayNode::at(int64_t i)` 返回第 i 个元素的 `AnyView`，见 `include/tvm/ffi/container/array.h:80`。
- **F-157**: `ArrayNode::SetItem(int64_t i, AnyView val)` 设置第 i 个元素，执行引用计数管理，见 `include/tvm/ffi/container/array.h:88`。
- **F-158**: `Array<T>` 模板类定义在 `include/tvm/ffi/container/array.h:230`，继承自 `ObjectRef`。
- **F-159**: `Array<T>::operator[](size_t i)` 返回 `T` 类型，执行 `AnyView::Cast<T>()`，见 `include/tvm/ffi/container/array.h:290`。
- **F-160**: `Array<T>::push_back(const T& item)` 将元素追加到数组，触发 COW（写时复制），见 `include/tvm/ffi/container/array.h:340`。
- **F-161**: `Array<T>::push_back(T&& item)` 移动追加，见 `include/tvm/ffi/container/array.h:354`。
- **F-162**: `Array<T>::begin()`/`end()` 返回 `PIterator`，见 `include/tvm/ffi/container/array.h:390-396`。
- **F-163**: `ListNode` 定义在 `include/tvm/ffi/container/list.h:40`，继承自 `Object`，内联存储容量为 4。
- **F-164**: `ListNode::_type_key = "ffi.ListNode"`，见 `include/tvm/ffi/container/list.h:46`。
- **F-165**: `List` 类定义在 `include/tvm/ffi/container/list.h:150`，继承自 `ObjectRef`。
- **F-166**: `MapNode` 定义在 `include/tvm/ffi/container/map.h:50`，继承自 `Object`，使用开放寻址哈希表。
- **F-167**: `MapNode::_type_key = "ffi.MapNode"`，见 `include/tvm/ffi/container/map.h:58`。
- **F-168**: `Map<K, V>` 模板类定义在 `include/tvm/ffi/container/map.h:280`，继承自 `ObjectRef`。
- **F-169**: `Map<K, V>::operator[](const K& key)` 返回 `V`，不存在时抛出异常，见 `include/tvm/ffi/container/map.h:360`。
- **F-170**: `Map<K, V>::at(const K& key)` 返回 `Optional<V>`，不存在时返回 `nullopt`，见 `include/tvm/ffi/container/map.h:375`。
- **F-171**: `Map<K, V>::find(const K& key)` 返回迭代器，见 `include/tvm/ffi/container/map.h:385`。
- **F-172**: `Map<K, V>::Set(const K& key, const V& value)` 设置键值对，触发 COW，见 `include/tvm/ffi/container/map.h:420`。
- **F-173**: `DictNode` 定义在 `include/tvm/ffi/container/dict.h:40`，继承自 `MapNode`，键类型为 `Any`。
- **F-174**: `Dict` 类定义在 `include/tvm/ffi/container/dict.h:130`，继承自 `ObjectRef`，键和值均为 `Any`。

### Tensor / Shape / Scalar

- **F-175**: `TensorObj` 定义在 `include/tvm/ffi/container/tensor.h:72`，继承自 `Object`，实现 `DLManagedTensor` 接口。
- **F-176**: `TensorObj::_type_key = "ffi.TensorObj"`，`_type_index = kTVMFFITypeIndexTensor`，见 `include/tvm/ffi/container/tensor.h:78-79`。
- **F-177**: `TensorObj` 包含 `DLTensor tensor_`（含 data、device、ndim、dtype、shape、strides、byte_offset），见 `include/tvm/ffi/container/tensor.h:90-103`。
- **F-178**: `TensorObj` 包含 `int64_t shape_storage_[kTVMFFI_CONTAINER_ALIGNED_SHAPE_DIMS]` 内联存储，见 `include/tvm/ffi/container/tensor.h:110`。
- **F-179**: `TensorObj` 包含 `int64_t stride_storage_[kTVMFFI_CONTAINER_ALIGNED_SHAPE_DIMS]` 内联存储，见 `include/tvm/ffi/container/tensor.h:115`。
- **F-180**: `TensorObj` 包含 `DLManagedTensorContext deleter_ctx_` 和自定义 `deleter`，见 `include/tvm/ffi/container/tensor.h:120-125`。
- **F-181**: `Tensor` 类定义在 `include/tvm/ffi/container/tensor.h:250`，继承自 `ObjectRef`。
- **F-182**: `Tensor::operator->()` 返回 `const DLTensor*`，见 `include/tvm/ffi/container/tensor.h:280`。
- **F-183**: `Tensor::data()` 返回 `void*`，`device()` 返回 `Device`，`dtype()` 返回 `DataType`，见 `include/tvm/ffi/container/tensor.h:284-290`。
- **F-184**: `Tensor::ndim()` 返回 `int32_t`，`shape()` 返回 `const int64_t*`，`strides()` 返回 `const int64_t*`，见 `include/tvm/ffi/container/tensor.h:292-298`。
- **F-185**: `Tensor::ToDLPack()` 返回 `DLManagedTensor*`，调用 `tensor_->ToDLPack()`，见 `include/tvm/ffi/container/tensor.h:320`。
- **F-186**: `ShapeObj` 定义在 `include/tvm/ffi/container/shape.h:50`，继承自 `Object`，存储 `int64_t` 数组。
- **F-187**: `ShapeObj::_type_key = "ffi.ShapeObj"`，`_type_index = kTVMFFITypeIndexShape`，见 `include/tvm/ffi/container/shape.h:55-56`。
- **F-188**: `Shape` 类定义在 `include/tvm/ffi/container/shape.h:120`，继承自 `ObjectRef`，可隐式转换为 `std::vector<int64_t>`。
- **F-189**: `ScalarObj` 定义在 `include/tvm/ffi/container/scalar.h:50`，包含 `DataType dtype` 和 `union { int64_t v_int64; uint64_t v_uint64; double v_float64; }`，见 `include/tvm/ffi/container/scalar.h:50-65`。
- **F-190**: `ScalarObj::_type_key = "ffi.ScalarObj"`，`_type_index = kTVMFFITypeIndexScalar`，见 `include/tvm/ffi/container/scalar.h:67-68`。
- **F-191**: `Scalar` 类定义在 `include/tvm/ffi/container/scalar.h:140`，继承自 `ObjectRef`。

### Tuple / Variant / String / Bytes

- **F-192**: `TupleObj` 定义在 `include/tvm/ffi/container/tuple.h:50`，存储 `TVMFFIAny* fields` 和 `size_t size`。
- **F-193**: `Tuple` 类定义在 `include/tvm/ffi/container/tuple.h:130`，支持 `std::get<N>(tuple)` 和 `tuple[i]` 访问。
- **F-194**: `VariantObj` 定义在 `include/tvm/ffi/container/variant.h:50`，存储 `int32_t index` 和 `TVMFFIAny value`。
- **F-195**: `Variant<Types...>` 模板类定义在 `include/tvm/ffi/container/variant.h:180`，持有 `ObjectRef` 引用。
- **F-196**: `StringObj` 定义在 `include/tvm/ffi/string.h:80`，继承自 `Object`，内联存储 `data_[kTVMFFI_CONTAINER_ALIGNED_BYTES]`。
- **F-197**: `StringObj::_type_key = "ffi.StringObj"`，`_type_index = kTVMFFITypeIndexString`，见 `include/tvm/ffi/string.h:90-91`。
- **F-198**: `String` 类定义在 `include/tvm/ffi/string.h:200`，继承自 `ObjectRef`，支持 `operator std::string()` 和 `c_str()`。
- **F-199**: `String::operator==(const String& other)` 逐字节比较，见 `include/tvm/ffi/string.h:300`。
- **F-200**: `BytesObj` 定义在 `include/tvm/ffi/string.h:450`，与 `StringObj` 结构类似但类型索引为 `kTVMFFITypeIndexBytes`。
- **F-201**: `Bytes` 类定义在 `include/tvm/ffi/string.h:530`，继承自 `ObjectRef`，存储不可变字节序列。

## 四、错误处理 (error.h)

- **F-202**: `ErrorObj` 定义在 `include/tvm/ffi/error.h:50`，继承自 `Object`。
- **F-203**: `ErrorObj::_type_key = "ffi.ErrorObj"`，`_type_index = kTVMFFITypeIndexError`，见 `include/tvm/ffi/error.h:55-56`。
- **F-204**: `ErrorObj` 包含 `String kind`、`String message`、`String traceback`、`ObjectRef cause`、`String extra_context`，见 `include/tvm/ffi/error.h:65-75`。
- **F-205**: `Error` 类定义在 `include/tvm/ffi/error.h:100`，继承自 `ObjectRef`，同时继承 `std::exception`。
- **F-206**: `Error::what()` 返回 `message().c_str()`，见 `include/tvm/ffi/error.h:120`。
- **F-207**: `Error::kind()` 返回 `const String&`，`message()` 返回 `const String&`，`traceback()` 返回 `const String&`，见 `include/tvm/ffi/error.h:125-135`。
- **F-208**: `Error::cause()` 返回 `ObjectRef`，`extra_context()` 返回 `const String&`，见 `include/tvm/ffi/error.h:137-140`。
- **F-209**: `Error::WithContext(const std::string& context)` 追加附加上下文，见 `include/tvm/ffi/error.h:150`。
- **F-210**: `Error::Raise(const std::string& msg)` 静态方法抛出 `Error` 对象，见 `include/tvm/ffi/error.h:160`。
- **F-211**: `ErrorKind` 枚举包含 `kInternal = 0`、`kValueError = 1`、`kTypeError = 2`、`kIndexError = 3`、`kAttributeError = 4`、`kKeyError = 5`、`kStopIteration = 6`、`kNotImplementedError = 7`、`kRuntimeError = 8`，见 `include/tvm/ffi/error.h:30-45`。
- **F-212**: `ErrorBuilder` 类支持链式设置 `kind()`、`message()`、`traceback()`、`cause()`、`extra_context()`，最后 `Raise()`，见 `include/tvm/ffi/error.h:180-260`。
- **F-213**: `TVM_FFI_TRY`/`TVM_FFI_CATCH` 宏捕获 C++ 异常并转换为 `TVMFFIObjectHandle`，见 `include/tvm/ffi/error.h:280-310`。

## 五、数据类型 (dtype.h)

- **F-214**: `DataType` 类定义在 `include/tvm/ffi/dtype.h:50`，包装 `DLDataType`。
- **F-215**: `DataType` 包含 `uint8_t code`、`uint8_t bits`、`uint16_t lanes`，见 `include/tvm/ffi/dtype.h:55`。
- **F-216**: `DataType::Int(int bits, int lanes)` 静态方法创建有符号整数类型，见 `include/tvm/ffi/dtype.h:80`。
- **F-217**: `DataType::UInt(int bits, int lanes)` 创建无符号整数类型，见 `include/tvm/ffi/dtype.h:85`。
- **F-218**: `DataType::Float(int bits, int lanes)` 创建浮点类型，见 `include/tvm/ffi/dtype.h:90`。
- **F-219**: `DataType::BFloat(int bits, int lanes)` 创建 bfloat 类型，见 `include/tvm/ffi/dtype.h:95`。
- **F-220**: `DataType::Bool(int lanes)` 创建布尔类型（code=kDLBool, bits=1），见 `include/tvm/ffi/dtype.h:100`。
- **F-221**: `DataType::Void()` 创建 void 类型（code=kDLHandle, bits=0, lanes=0），见 `include/tvm/ffi/dtype.h:105`。
- **F-222**: `DataType::is_int()`、`is_uint()`、`is_float()`、`is_bfloat()`、`is_bool()`、`is_void()` 检查类型类别，见 `include/tvm/ffi/dtype.h:115-130`。
- **F-223**: `DataType::is_scalar()` 返回 `lanes == 1`，见 `include/tvm/ffi/dtype.h:135`。
- **F-224**: `DataType::is_vector()` 返回 `lanes > 1`，见 `include/tvm/ffi/dtype.h:137`。
- **F-225**: `DataType::bytes()` 返回 `(bits * lanes + 7) / 8`，见 `include/tvm/ffi/dtype.h:140`。
- **F-226**: `DataType::with_lanes(int lanes)` 返回同 code/bits 但新 lanes 的类型，见 `include/tvm/ffi/dtype.h:145`。
- **F-227**: `DataType::with_bits(int bits)` 返回同 code/lanes 但新 bits 的类型，见 `include/tvm/ffi/dtype.h:150`。
- **F-228**: `DataType::element_of()` 返回 lanes=1 的元素类型，见 `include/tvm/ffi/dtype.h:155`。
- **F-229**: `DataType::operator==(const DataType& other)` 比较 code、bits、lanes，见 `include/tvm/ffi/dtype.h:165`。
- **F-230**: `Device` 类定义在 `include/tvm/ffi/dtype.h:200`，包装 `DLDevice`，包含 `int32_t device_type` 和 `int32_t device_id`。
- **F-231**: `Device::operator==(const Device& other)` 比较 device_type 和 device_id，见 `include/tvm/ffi/dtype.h:220`。

## 六、枚举 (enum.h)

- **F-232**: `Enum` 模板类定义在 `include/tvm/ffi/enum.h:50`，为 C++ 枚举类型提供 FFI 注册支持。
- **F-233**: `Enum<T>::Register(const String& name, T value)` 静态方法注册枚举值，见 `include/tvm/ffi/enum.h:65`。
- **F-234**: `Enum<T>::FromInt(int64_t value)` 从整数构造枚举，见 `include/tvm/ffi/enum.h:80`。
- **F-235**: `Enum<T>::FromStr(const String& name)` 从名称构造枚举，见 `include/tvm/ffi/enum.h:85`。
- **F-236**: `Enum<T>::ToString(T value)` 返回枚举值名称，见 `include/tvm/ffi/enum.h:90`。
- **F-237**: `TVM_FFI_REGISTER_ENUM(Type, Name)` 宏注册枚举类型到 FFI 反射系统，见 `include/tvm/ffi/enum.h:120`。
- **F-238**: `TVM_FFI_REGISTER_ENUM_VALUE(Type, Name, Value)` 宏注册单个枚举值，见 `include/tvm/ffi/enum.h:130`。

## 七、类型转换 (cast.h)

- **F-239**: `Cast<T>` 模板函数定义在 `include/tvm/ffi/cast.h:50`，从 `AnyView` 转换到目标类型 `T`。
- **F-240**: `Cast<T>(const AnyView& val)` 对整数类型检查 `IsInt()`/`IsUInt()` 后转换，见 `include/tvm/ffi/cast.h:65-80`。
- **F-241**: `Cast<T>(const AnyView& val)` 对浮点类型检查 `IsFloat()` 后转换，见 `include/tvm/ffi/cast.h:85`。
- **F-242**: `Cast<T>(const AnyView& val)` 对 `bool` 类型检查 `IsBool()`，见 `include/tvm/ffi/cast.h:95`。
- **F-243**: `Cast<T>(const AnyView& val)` 对 `std::string` 检查 `IsString()` 或 `IsBytes()`，见 `include/tvm/ffi/cast.h:105`。
- **F-244**: `Cast<T>(const AnyView& val)` 对 `ObjectRef` 子类检查 `IsObject()` 并执行 `Downcast`，见 `include/tvm/ffi/cast.h:120`。
- **F-245**: `Cast<T>(const AnyView& val)` 对 `Optional<T>` 允许 null 值，见 `include/tvm/ffi/cast.h:140`。
- **F-246**: `TryCast<T>` 模板函数返回 `std::optional<T>`，转换失败时返回 `nullopt`，见 `include/tvm/ffi/cast.h:170`。
- **F-247**: `AnyView::Cast<T>()` 方法内联调用 `ffi::Cast<T>(*this)`，见 `include/tvm/ffi/any.h:920`。
- **F-248**: `AnyView::TryCast<T>()` 方法内联调用 `ffi::TryCast<T>(*this)`，见 `include/tvm/ffi/any.h:925`。

## 八、反射系统 (reflection/*.h)

- **F-249**: `reflection::VTable` 定义在 `include/tvm/ffi/reflection/vtable.h:50`，管理类型的反射信息。
- **F-250**: `VTable::Create(const String& type_key)` 静态方法创建或获取类型 VTable，见 `include/tvm/ffi/reflection/vtable.h:65`。
- **F-251**: `VTable::set_func(const String& name, Function func)` 注册方法，见 `include/tvm/ffi/reflection/vtable.h:80`。
- **F-252**: `VTable::get_func(const String& name)` 返回注册的函数，见 `include/tvm/ffi/reflection/vtable.h:90`。
- **F-253**: `VTable::ListFuncNames()` 返回所有已注册函数名，见 `include/tvm/ffi/reflection/vtable.h:100`。
- **F-254**: `reflection::FieldDef` 定义在 `include/tvm/ffi/reflection/registry.h:60`，描述字段信息，包含 `name`、`offset`、`type_key`。
- **F-255**: `reflection::ObjectDef<T>` 模板类定义在 `include/tvm/ffi/reflection/registry.h:100`，支持链式 `def()`、`def_ro()`、`def_rw()` 注册字段。
- **F-256**: `ObjectDef<T>::def(const char* name, TValue T::*field)` 注册可读写字段，见 `include/tvm/ffi/reflection/registry.h:120`。
- **F-257**: `ObjectDef<T>::def_ro(const char* name, const TValue T::*field)` 注册只读字段，见 `include/tvm/ffi/reflection/registry.h:135`。
- **F-258**: `ObjectDef<T>::def_rw(const char* name, TValue T::*field)` 同 `def()`，显式标注可读写，见 `include/tvm/ffi/reflection/registry.h:145`。
- **F-259**: `AttachFieldFlag` 枚举包含 `SEqHashIgnore`、`NoPythonAccess` 等字段标志，见 `include/tvm/ffi/reflection/registry.h:80-95`。
- **F-260**: `DefaultValue(T value)` 函数为字段设置默认值，见 `include/tvm/ffi/reflection/registry.h:170`。
- **F-261**: `TVM_FFI_REGISTER_OBJECT(Type)` 宏注册对象类型到反射系统，展开为静态初始化代码，见 `include/tvm/ffi/reflection/registry.h:250`。
- **F-262**: `TVM_FFI_REGISTER_OBJECT_REF(Type, ObjType)` 宏同时注册 ObjectRef 和对应 Obj 类型，见 `include/tvm/ffi/reflection/registry.h:270`。

## 九、结构比较与哈希

- **F-263**: `StructuralEqual` 类定义在 `include/tvm/ffi/extra/structural_equal.h:50`，执行运行时深度结构比较。
- **F-264**: `StructuralEqual::operator()(const Any& lhs, const Any& rhs)` 返回 `bool`，见 `include/tvm/ffi/extra/structural_equal.h:60`。
- **F-265**: `StructuralEqual::operator()(const ObjectRef& lhs, const ObjectRef& rhs)` 比较对象，见 `include/tvm/ffi/extra/structural_equal.h:65`。
- **F-266**: `StructuralHash` 类定义在 `include/tvm/ffi/extra/structural_hash.h:50`，执行运行时结构哈希。
- **F-267**: `StructuralHash::operator()(const Any& val)` 返回 `uint64_t`，见 `include/tvm/ffi/extra/structural_hash.h:60`。
- **F-268**: `StructuralHash::operator()(const ObjectRef& val)` 哈希对象，见 `include/tvm/ffi/extra/structural_hash.h:65`。
- **F-269**: `SEqualReducer` 类在 `src/ffi/extra/structural_equal.cc:50` 实现，维护已访问节点映射表以支持 DAG，见 `src/ffi/extra/structural_equal.cc:50-120`。
- **F-270**: `SHashReducer` 类在 `src/ffi/extra/structural_hash.cc:50` 实现，维护已访问节点哈希缓存以支持 DAG，见 `src/ffi/extra/structural_hash.cc:50-100`。
- **F-271**: `SEqualReducer::operator()(const Any& lhs, const Any& rhs)` 对基础类型直接比较，对 Array/Map 递归比较元素，见 `src/ffi/extra/structural_equal.cc:130-250`。
- **F-272**: `SHashReducer::operator()(const Any& val)` 对基础类型直接哈希，对 Array/Map 递归哈希元素，见 `src/ffi/extra/structural_hash.cc:120-200`。
- **F-273**: `kTVMFFISEqHashKindTreeNode` 表示树节点（无共享），`kTVMFFISEqHashKindDAGNode` 表示 DAG 节点（有共享），见 `include/tvm/ffi/c_api.h:90-95`。

## 十、C++ 源文件实现

- **F-274**: `TypeTable` 单例在 `src/ffi/object.cc:30` 管理 `std::vector<TypeInfo>` 和 `std::unordered_map<std::string, int32_t>`，见 `src/ffi/object.cc:30-40`。
- **F-275**: `TypeTable::RegisterType` 分配类型索引、注册类型键、设置父类型，见 `src/ffi/object.cc:50-100`。
- **F-276**: `TypeTable::TypeKey2Index` 查找类型键返回索引，不存在返回 -1，见 `src/ffi/object.cc:110`。
- **F-277**: `TypeTable::TypeIndex2Key` 查找索引返回类型键，见 `src/ffi/object.cc:120`。
- **F-278**: `Object::TypeIndex2Key` 静态方法委托 `TypeTable::Global()->TypeIndex2Key`，见 `src/ffi/object.cc:140`。
- **F-279**: `Object::TypeKey2Index` 静态方法委托 `TypeTable::Global()->TypeKey2Index`，见 `src/ffi/object.cc:145`。
- **F-280**: `Function::GetGlobalFunction` 在 `src/ffi/function.cc:50` 从全局 `std::unordered_map<std::string, Function>` 查找，见 `src/ffi/function.cc:50-60`。
- **F-281**: `Function::RegisterGlobal` 在 `src/ffi/function.cc:70` 将函数插入全局 map，见 `src/ffi/function.cc:70-80`。
- **F-282**: `Function::ListGlobalNames` 在 `src/ffi/function.cc:90` 遍历全局 map 返回名称列表，见 `src/ffi/function.cc:90-100`。
- **F-283**: `ErrorObj::RegisterReflection` 在 `src/ffi/error.cc:30` 注册 kind、message、traceback、cause、extra_context 字段，见 `src/ffi/error.cc:30-50`。
- **F-284**: `TensorObj::TensorObj` 构造函数在 `src/ffi/tensor.cc:30` 初始化 shape 和 stride 存储，见 `src/ffi/tensor.cc:30-60`。
- **F-285**: `TensorObj::~TensorObj` 析构函数调用 `deleter` 释放外部数据，见 `src/ffi/tensor.cc:65`。
- **F-286**: `TensorObj::ToDLPack` 在 `src/ffi/tensor.cc:80` 创建 `DLManagedTensor` 并设置 `deleter` 为 `DLTensorDeleter`，见 `src/ffi/tensor.cc:80-100`。
- **F-287**: `Tensor::Make` 静态方法在 `src/ffi/tensor.cc:120` 接受 shape、stride、dtype、device、data 创建 Tensor，见 `src/ffi/tensor.cc:120-180`。
- **F-288**: `ArrayNode::ArrayNode` 在 `src/ffi/container.cc:30` 初始化内联存储或堆分配，见 `src/ffi/container.cc:30-50`。
- **F-289**: `ArrayNode::SetItem` 在 `src/ffi/container.cc:70` 执行旧值 DecRef 和新值 IncRef，见 `src/ffi/container.cc:70-90`。
- **F-290**: `MapNode::MapNode` 在 `src/ffi/container.cc:200` 初始化哈希表桶数组，见 `src/ffi/container.cc:200-220`。
- **F-291**: `MapNode::Find` 在 `src/ffi/container.cc:240` 执行开放寻址查找，见 `src/ffi/container.cc:240-280`。
- **F-292**: `MapNode::Set` 在 `src/ffi/container.cc:300` 插入或更新键值对，负载因子超过阈值时 rehash，见 `src/ffi/container.cc:300-380`。
- **F-293**: `DataType::RegisterReflection` 在 `src/ffi/dtype.cc:30` 注册 code、bits、lanes 字段，见 `src/ffi/dtype.cc:30-45`。
- **F-294**: `Device::RegisterReflection` 在 `src/ffi/dtype.cc:55` 注册 device_type、device_id 字段，见 `src/ffi/dtype.cc:55-65`。
- **F-295**: `Backtrace::Capture` 在 `src/ffi/backtrace.cc:30` 使用 `backtrace()` 和 `backtrace_symbols()` 捕获栈帧，见 `src/ffi/backtrace.cc:30-60`。
- **F-296**: `Backtrace::ToString` 在 `src/ffi/backtrace.cc:70` 将帧信息格式化为字符串，见 `src/ffi/backtrace.cc:70-90`。
- **F-297**: `InitOnce` 在 `src/ffi/init_once.cc:30` 使用 `std::call_once` 保证线程安全初始化，见 `src/ffi/init_once.cc:30-40`。
- **F-298**: `custom_allocator::Alloc` 在 `src/ffi/custom_allocator.cc:30` 使用 `aligned_alloc` 分配对齐内存，见 `src/ffi/custom_allocator.cc:30-40`。
- **F-299**: `custom_allocator::Free` 在 `src/ffi/custom_allocator.cc:50` 使用 `free` 释放内存，见 `src/ffi/custom_allocator.cc:50`。
- **F-300**: `reflection_extra.cc` 在 `src/ffi/extra/reflection_extra.cc:30` 为基础类型（int/float/bool/string）注册反射信息，见 `src/ffi/extra/reflection_extra.cc:30-80`。
- **F-301**: `ModuleNode` 在 `src/ffi/extra/module.cc:30` 继承自 `Object`，定义 `GetFunction` 虚方法，见 `src/ffi/extra/module.cc:30-50`。
- **F-302**: `Module` 类在 `src/ffi/extra/module.cc:70` 继承自 `ObjectRef`，封装 `ModuleNode`，见 `src/ffi/extra/module.cc:70-120`。
- **F-303**: `Module::GetFunction` 调用 `ModuleNode::GetFunction`，见 `src/ffi/extra/module.cc:90`。
- **F-304**: `Module::LoadFromFile` 静态方法在 `src/ffi/extra/module.cc:140` 从文件加载模块，见 `src/ffi/extra/module.cc:140-180`。

## 十一、Rust 绑定

- **F-305**: `lib.rs` 在 `rust/tvm-ffi/src/lib.rs:19` 声明模块 `any`、`object`、`function`、`error`、`dtype`、`collections`、`string`，见 `rust/tvm-ffi/src/lib.rs:19-30`。
- **F-306**: `lib.rs` 重新导出 `Any`、`Array`、`Map`、`Tensor`、`Device`、`Function`、`Error`、`DataType`、`String`、`Bytes`、`Shape`、`Scalar`，见 `rust/tvm-ffi/src/lib.rs:35-65`。
- **F-307**: `Any` 枚举在 `rust/tvm-ffi/src/any.rs:30` 包含 `Int(i64)`、`UInt(u64)`、`Float(f64)`、`Bool(bool)`、`Null`、`String(String)`、`Bytes(Vec<u8>)`、`Object(ObjectHandle)`、`Function(FunctionHandle)` 等变体，见 `rust/tvm-ffi/src/any.rs:30-60`。
- **F-308**: `Any::type_index()` 在 `rust/tvm-ffi/src/any.rs:80` 返回对应的 `TVMFFITypeIndex`，见 `rust/tvm-ffi/src/any.rs:80-120`。
- **F-309**: `Any::from_tvm_ffi_any` 在 `rust/tvm-ffi/src/any.rs:140` 从 `TVMFFIAny` 联合体构造 Rust `Any`，见 `rust/tvm-ffi/src/any.rs:140-200`。
- **F-310**: `Any::to_tvm_ffi_any` 在 `rust/tvm-ffi/src/any.rs:220` 将 Rust `Any` 转换为 `TVMFFIAny`，见 `rust/tvm-ffi/src/any.rs:220-280`。
- **F-311**: `ObjectHandle` 在 `rust/tvm-ffi/src/object.rs:30` 包装 `*mut TVMFFIObject`，实现 `Drop` 调用 `TVMFFIObjectDecRef`，见 `rust/tvm-ffi/src/object.rs:30-60`。
- **F-312**: `ObjectHandle::clone` 在 `rust/tvm-ffi/src/object.rs:65` 调用 `TVMFFIObjectIncRef` 增加引用计数，见 `rust/tvm-ffi/src/object.rs:65-75`。
- **F-313**: `Function` 在 `rust/tvm-ffi/src/function.rs:30` 包装 `TVMFFIFunctionHandle`，见 `rust/tvm-ffi/src/function.rs:30-50`。
- **F-314**: `Function::call` 在 `rust/tvm-ffi/src/function.rs:60` 接受 `&[Any]` 参数，返回 `Result<Any, Error>`，见 `rust/tvm-ffi/src/function.rs:60-120`。
- **F-315**: `Function::get_global` 在 `rust/tvm-ffi/src/function.rs:140` 调用 `TVMFFIFuncGetGlobal` 获取全局函数，见 `rust/tvm-ffi/src/function.rs:140-160`。
- **F-316**: `Function::register_global` 在 `rust/tvm-ffi/src/function.rs:170` 调用 `TVMFFIFuncRegisterGlobal` 注册全局函数，见 `rust/tvm-ffi/src/function.rs:170-200`。
- **F-317**: `Error` 在 `rust/tvm-ffi/src/error.rs:30` 包含 `kind: i32`、`message: String`、`traceback: Option<String>`，见 `rust/tvm-ffi/src/error.rs:30-50`。
- **F-318**: `Error::from_handle` 在 `rust/tvm-ffi/src/error.rs:60` 从 `TVMFFIObjectHandle` 提取错误信息，见 `rust/tvm-ffi/src/error.rs:60-100`。
- **F-319**: `DataType` 在 `rust/tvm-ffi/src/dtype.rs:20` 包装 `TVMFFIDataType`，包含 `code: u8`、`bits: u8`、`lanes: u16`，见 `rust/tvm-ffi/src/dtype.rs:20-35`。
- **F-320**: `DataType::int`、`uint`、`float`、`bool`、`void` 构造方法在 `rust/tvm-ffi/src/dtype.rs:50-90`，见 `rust/tvm-ffi/src/dtype.rs:50-90`。
- **F-321**: `collections::Tensor` 在 `rust/tvm-ffi/src/collections/tensor.rs:30` 包装 `TVMFFIObjectHandle`，提供 `shape()`、`dtype()`、`device()`、`data()` 方法，见 `rust/tvm-ffi/src/collections/tensor.rs:30-100`。
- **F-322**: `collections::Array<T>` 在 `rust/tvm-ffi/src/collections/array.rs:30` 包装对象句柄，提供 `len()`、`get()`、`push()` 方法，见 `rust/tvm-ffi/src/collections/array.rs:30-120`。
- **F-323**: `collections::Map<K, V>` 在 `rust/tvm-ffi/src/collections/map.rs:30` 包装对象句柄，提供 `get()`、`set()`、`contains()`、`len()` 方法，见 `rust/tvm-ffi/src/collections/map.rs:30-140`。
- **F-324**: `collections::List` 在 `rust/tvm-ffi/src/collections/list.rs:20` 包装对象句柄，提供 `push()`、`pop()`、`len()` 方法，见 `rust/tvm-ffi/src/collections/list.rs:20-80`。
- **F-325**: `collections::Dict` 在 `rust/tvm-ffi/src/collections/dict.rs:20` 包装对象句柄，键值均为 `Any`，见 `rust/tvm-ffi/src/collections/dict.rs:20-70`。
- **F-326**: `String` 在 `rust/tvm-ffi/src/string.rs:20` 包装 `TVMFFIObjectHandle`，实现 `AsRef<str>` 和 `Display`，见 `rust/tvm-ffi/src/string.rs:20-80`。
- **F-327**: `String::from_str` 在 `rust/tvm-ffi/src/string.rs:40` 调用 `TVMFFIStringCreateFromData` 创建字符串对象，见 `rust/tvm-ffi/src/string.rs:40-60`。
- **F-328**: `String::as_bytes` 在 `rust/tvm-ffi/src/string.rs:70` 调用 `TVMFFIStringGetData` 获取字节切片，见 `rust/tvm-ffi/src/string.rs:70-80`。

## 十二、Python 绑定

- **F-329**: `__init__.py` 在 `python/tvm_ffi/__init__.py:55` 导入 `_ffi_api`、`container`、`registry`、`error`、`_convert`、`_tensor` 模块，见 `python/tvm_ffi/__init__.py:55-80`。
- **F-330**: `__init__.py` 导出 `Object`、`Function`、`Tensor`、`Array`、`Dict`、`List`、`Map`、`String`、`Bytes`、`Shape`、`Scalar`、`Error`、`DataType`、`Device`，见 `python/tvm_ffi/__init__.py:85-128`。
- **F-331**: `_ffi_api.py` 在 `python/tvm_ffi/_ffi_api.py:20` 使用 ctypes 加载 `libtvm_ffi` 共享库，见 `python/tvm_ffi/_ffi_api.py:20-40`。
- **F-332**: `_ffi_api.py` 声明 `TVMFFIGetVersion`、`TVMFFIFuncGetGlobal`、`TVMFFIFuncCall`、`TVMFFIObjectIncRef`、`TVMFFIObjectDecRef` 等 C 函数签名，见 `python/tvm_ffi/_ffi_api.py:45-120`。
- **F-333**: `_ffi_api.py` 声明 `TVMFFITypeKey2Index`、`TVMFFITypeIndex2Key`、`TVMFFIStructuralEqual`、`TVMFFIStructuralHash` 签名，见 `python/tvm_ffi/_ffi_api.py:125-160`。
- **F-334**: `_ffi_api.py` 声明 `TVMFFIGetLastError`、`TVMFFISetLastError`、`TVMFFICStringFree` 错误处理函数签名，见 `python/tvm_ffi/_ffi_api.py:165-185`。
- **F-335**: `cython/core.pyx` 在 `python/tvm_ffi/cython/core.pyx:30` 定义 Cython 扩展类 `PyAny`，包装 `TVMFFIAny`，见 `python/tvm_ffi/cython/core.pyx:30-80`。
- **F-336**: `PyAny` 在 `python/tvm_ffi/cython/core.pyx:50` 支持 `__int__`、`__float__`、`__bool__`、`__str__` Python 协议方法，见 `python/tvm_ffi/cython/core.pyx:50-120`。
- **F-337**: `cython/core.pyx` 在 `python/tvm_ffi/cython/core.pyx:140` 定义 `PyFunction`，包装 `TVMFFIFunctionHandle`，实现 `__call__`，见 `python/tvm_ffi/cython/core.pyx:140-220`。
- **F-338**: `container.py` 在 `python/tvm_ffi/container.py:30` 定义 `PyArray` 类，继承 `ObjectBase`，实现 `__len__`、`__getitem__`、`__setitem__`、`append`，见 `python/tvm_ffi/container.py:30-120`。
- **F-339**: `container.py` 在 `python/tvm_ffi/container.py:130` 定义 `PyDict` 类，实现 `__len__`、`__getitem__`、`__setitem__`、`__contains__`、`keys`、`values`、`items`，见 `python/tvm_ffi/container.py:130-250`。
- **F-340**: `container.py` 在 `python/tvm_ffi/container.py:260` 定义 `PyList` 类，实现 `append`、`pop`、`__len__`、`__getitem__`，见 `python/tvm_ffi/container.py:260-320`。
- **F-341**: `container.py` 在 `python/tvm_ffi/container.py:330` 定义 `PyMap` 类，与 `PyDict` 类似但键类型受限，见 `python/tvm_ffi/container.py:330-400`。
- **F-342**: `registry.py` 在 `python/tvm_ffi/registry.py:20` 维护全局函数注册表 `_REGISTRY = {}`，见 `python/tvm_ffi/registry.py:20-30`。
- **F-343**: `registry.py` 在 `python/tvm_ffi/registry.py:40` 定义 `register_func(name)` 装饰器，将 Python 函数注册到 C++ 全局表，见 `python/tvm_ffi/registry.py:40-80`。
- **F-344**: `registry.py` 在 `python/tvm_ffi/registry.py:90` 定义 `get_global_func(name)` 返回包装的 `Function` 对象，见 `python/tvm_ffi/registry.py:90-110`。
- **F-345**: `registry.py` 在 `python/tvm_ffi/registry.py:120` 定义 `list_global_func_names()` 返回所有注册函数名，见 `python/tvm_ffi/registry.py:120-135`。
- **F-346**: `error.py` 在 `python/tvm_ffi/error.py:20` 定义 `TVMFFIError` 异常基类，见 `python/tvm_ffi/error.py:20-30`。
- **F-347**: `error.py` 定义 `TVMFFIInternalError`、`TVMFFIValueError`、`TVMFFITypeError`、`TVMFFIIndexError`、`TVMFFIKeyError` 等子类，见 `python/tvm_ffi/error.py:35-80`。
- **F-348**: `error.py` 在 `python/tvm_ffi/error.py:90` 定义 `_extract_error(handle)` 从 C 错误对象提取 kind、message、traceback，见 `python/tvm_ffi/error.py:90-130`。
- **F-349**: `_convert.py` 在 `python/tvm_ffi/_convert.py:20` 定义 `to_tvm_ffi_any(value)` 将 Python 对象转换为 `TVMFFIAny`，见 `python/tvm_ffi/_convert.py:20-100`。
- **F-350**: `_convert.py` 在 `python/tvm_ffi/_convert.py:110` 定义 `from_tvm_ffi_any(any_val)` 将 `TVMFFIAny` 转换为 Python 对象，见 `python/tvm_ffi/_convert.py:110-180`。
- **F-351**: `_tensor.py` 在 `python/tvm_ffi/_tensor.py:20` 定义 `Tensor` 类，包装 C 张量对象，提供 `shape`、`dtype`、`device`、`numpy()` 方法，见 `python/tvm_ffi/_tensor.py:20-120`。
- **F-352**: `_tensor.py` 在 `python/tvm_ffi/_tensor.py:130` 定义 `tensor_from_numpy(arr)` 从 NumPy 数组创建 Tensor，见 `python/tvm_ffi/_tensor.py:130-180`。
- **F-353**: `_tensor.py` 在 `python/tvm_ffi/_tensor.py:190` 定义 `tensor_from_dlpack(tensor)` 从 DLPack 创建 Tensor，见 `python/tvm_ffi/_tensor.py:190-220`。

## 十三、TVM 与 FFI 交互

- **F-354**: `tvm/runtime/base.h:27-29` 注释说明 "TVM runtime fully relies on TVM FFI C API"，并 `#include <tvm/ffi/c_api.h>`，见 `include/tvm/runtime/base.h:27-29`。
- **F-355**: `tvm/ir/base_expr.h:27-30` 包含 `<tvm/ffi/cast.h>`、`<tvm/ffi/dtype.h>`、`<tvm/ffi/reflection/registry.h>`、`<tvm/ffi/string.h>`，见 `include/tvm/ir/base_expr.h:27-30`。
- **F-356**: `TypeNode` 在 `include/tvm/ir/base_expr.h:52` 继承 `ffi::Object`，`_type_index = kTVMFFITypeIndexDynamicBegin`（动态分配），见 `include/tvm/ir/base_expr.h:52-71`。
- **F-357**: `TypeNode::RegisterReflection` 在 `include/tvm/ir/base_expr.h:60-65` 使用 `refl::ObjectDef<TypeNode>().def_ro("span", &TypeNode::span, ...)` 注册字段，见 `include/tvm/ir/base_expr.h:60-65`。
- **F-358**: `Type` 在 `include/tvm/ir/base_expr.h:77` 继承 `ffi::ObjectRef`，见 `include/tvm/ir/base_expr.h:77`。
- **F-359**: `PrimTypeNode` 在 `include/tvm/ir/base_expr.h:95` 继承 `TypeNode`，包含 `DLDataType dtype` 字段，见 `include/tvm/ir/base_expr.h:95-107`。
- **F-360**: `PrimType` 在 `include/tvm/ir/base_expr.h:113` 继承 `Type`，提供 `Int(bits, lanes)`、`UInt(bits, lanes)`、`Float(bits, lanes)`、`BFloat(bits, lanes)`、`Bool(lanes)`、`Void()` 工厂方法，见 `include/tvm/ir/base_expr.h:113-148`。
- **F-361**: `src/runtime/pack_args.h:34` 包含 `<tvm/ffi/function.h>`，使用 `ffi::Function`、`ffi::PackedArgs`、`ffi::Any`、`ffi::Array`，见 `src/runtime/pack_args.h:34-36`。
- **F-362**: `PackFuncVoidAddr` 在 `src/runtime/pack_args.h:75` 返回 `ffi::Function`，接受 `ffi::Array<DLDataType>` 参数类型，见 `src/runtime/pack_args.h:75-76`。
- **F-363**: `PackFuncNonBufferArg` 在 `src/runtime/pack_args.h:87` 返回 `ffi::Function`，仅打包非缓冲区参数，见 `src/runtime/pack_args.h:87`。
- **F-364**: `PackFuncPackedArgAligned` 在 `src/runtime/pack_args.h:101` 返回 `ffi::Function`，按 C 结构对齐填充，见 `src/runtime/pack_args.h:101`。
- **F-365**: `ArgUnion32` 在 `src/runtime/pack_args.h:47` 是 `union`，包含 `int32_t v_int32`、`uint32_t v_uint32`、`float v_float32`，见 `src/runtime/pack_args.h:47-51`。
- **F-366**: `ArgUnion64` 在 `src/runtime/pack_args.h:56` 是 `union`，包含 `int64_t v_int64`、`uint64_t v_uint64`、`double v_float64` 等，见 `src/runtime/pack_args.h:56-63`。
- **F-367**: `ArgConvertCode` 枚举在 `src/runtime/pack_args.h:131` 包含 `INT64_TO_INT64`、`INT64_TO_INT32`、`FLOAT64_TO_FLOAT32`、`HANDLE_TO_HANDLE`、`HANDLE_TO_TENSORMAP`，见 `src/runtime/pack_args.h:131-139`。
- **F-368**: `GetArgConvertCode` 在 `src/runtime/pack_args.h:141` 根据 `DLDataType` 返回转换代码，见 `src/runtime/pack_args.h:141-155`。
- **F-369**: `python/tvm/base.py:23` 从 `tvm_ffi.libinfo` 导入 `load_lib_ctypes`，见 `python/tvm/base.py:23`。
- **F-370**: `python/tvm/base.py:44-46` 加载 `tvm_runtime` 库时使用 `RTLD_GLOBAL` 标志，见 `python/tvm/base.py:44-46`。
- **F-371**: `python/tvm/base.py:50-52` 加载 `tvm_compiler` 库时使用 `RTLD_LOCAL` 标志，见 `python/tvm/base.py:50-52`。
- **F-372**: `python/tvm/base.py:58-61` 运行时仅模式下设置 `tvm_ffi.registry._SKIP_UNKNOWN_OBJECTS = True`，见 `python/tvm/base.py:58-61`。
- **F-373**: `tvm/ir/expr.h:27-30` 包含 `<tvm/ffi/dtype.h>`、`<tvm/ffi/extra/dataclass.h>`、`<tvm/ffi/reflection/registry.h>`、`<tvm/ffi/string.h>`，见 `include/tvm/ir/expr.h:27-30`。
- **F-374**: `tvm/runtime/module.h` 包含 `<tvm/ffi/object.h>` 和 `<tvm/ffi/function.h>`，`ModuleNode` 继承 `ffi::Object`，`Module` 继承 `ffi::ObjectRef`，见 `include/tvm/runtime/module.h`。
- **F-375**: `tvm/runtime/vm/vm.h` 包含 `<tvm/ffi/function.h>` 和 `<tvm/ffi/container/array.h>`，`VirtualMachine` 类使用 `ffi::Function` 和 `ffi::Array`，见 `include/tvm/runtime/vm/vm.h`。
- **F-376**: TVM 编译器库 (`libtvm_compiler`) 和运行时库 (`libtvm_runtime`) 各自定义独立的 DLL 宏 `TVM_DLL` 和 `TVM_RUNTIME_DLL`，见 `include/tvm/runtime/base.h:38-94`。
- **F-377**: TVM 版本宏 `TVM_VERSION` 默认为 `"0.26.dev0"`，可通过 `-DTVM_VERSION` 覆盖，见 `include/tvm/runtime/base.h:34-36`。

## 十四、总括头文件与版本

- **F-378**: `tvm_ffi.h` 在 `include/tvm/ffi/tvm_ffi.h:27` 是总括头文件，包含 any、c_api、cast、container（array/list/map/dict/tuple/variant/tensor/shape/scalar/string）、device、dtype、enum、error、function、object、optional、result 等，见 `include/tvm/ffi/tvm_ffi.h:27-62`。
- **F-379**: FFI 版本号通过 `TVMFFIGetVersion()` 返回，C API 中无硬编码版本常量，见 `include/tvm/ffi/c_api.h:155`。
- **F-380**: `TVMFFI_CONTAINER_ALIGNED_SHAPE_DIMS = 4`，Tensor 内联 shape/stride 维度数，见 `include/tvm/ffi/c_api.h:995`。
