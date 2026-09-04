# ir-py 事实清单（R阶段）

> 纯Python ONNX IR实现源码分析事实提取。每条事实标注源码路径和行号，禁止推断。

## 项目概览

| 编号 | 事实 | 源码位置 |
|------|------|----------|
| F-001 | 项目包名为 `onnx_ir`，版本号 `__version__ = "1.1.0"`，模块导出 `serde`, `traversal`, `convenience`, `external_data`, `tape`, `schemas` 六大子模块。 | `src/onnx_ir/__init__.py` L5-L111, L199 |
| F-002 | 核心设计原则：`_core.py` 中的类不包含任何 `to_onnx`/`from_protobuf` 方法，以保持IR模块protobuf-free，序列化/反序列化关注点分离到 `serde.py`。 | `src/onnx_ir/_core.py` L6-L9 |
| F-003 | 开发者注释明确禁止在IR中导入 `pathlib`（因为慢），要求使用 `os.path` 方法。 | `src/onnx_ir/_core.py` L11 |
| F-004 | 公开导出的IR实体类包括：`Tensor`, `ExternalTensor`, `StringTensor`, `LazyTensor`, `PackedTensor`, `SymbolicDim`, `Shape`, `TensorType`, `OptionalType`, `SequenceType`, `SparseTensorType`, `TypeAndShape`, `Value`, `Attr`, `RefAttr`, `Node`, `Function`, `Graph`, `GraphView`, `Model`。 | `src/onnx_ir/__init__.py` L14-L33 |

## 类型系统枚举

| 编号 | 事实 | 源码位置 |
|------|------|----------|
| F-005 | `AttributeType` 是 `IntEnum`，定义15种属性类型：UNDEFINED=0, FLOAT=1, INT=2, STRING=3, TENSOR=4, GRAPH=5, FLOATS=6, INTS=7, STRINGS=8, TENSORS=9, GRAPHS=10, SPARSE_TENSOR=11, SPARSE_TENSORS=12, TYPE_PROTO=13, TYPE_PROTOS=14。 | `src/onnx_ir/_enums.py` L14-L31 |
| F-006 | `DataType` 是 `IntEnum`，定义27种数据类型，从UNDEFINED=0到INT2=26，涵盖标准类型（FLOAT/UINT8/INT8/.../DOUBLE/COMPLEX64/COMPLEX128）、BFLOAT16、FLOAT8系列（E4M3FN/E4M3FNUZ/E5M2/E5M2FNUZ/E8M0）、亚字节类型（UINT4/INT4/UINT2/INT2/FLOAT4E2M1）。 | `src/onnx_ir/_enums.py` L40-L71 |
| F-007 | `DataType` 提供 `from_numpy()` 类方法将numpy dtype映射到DataType，支持通过 `dtype.names` 元组字段识别ONNX自定义dtype（如 `("bfloat16",)`, `("e4m3fn",)` 等）。 | `src/onnx_ir/_enums.py` L73-L110 |
| F-008 | `DataType` 提供 `itemsize`（字节大小）、`bitwidth`（位宽）、`numpy()`（映射到numpy dtype）、`short_name()`（如f32/i64/bf16）、`is_floating_point()`/`is_integer()`/`is_signed()`/`is_string()` 等分类属性和方法。 | `src/onnx_ir/_enums.py` L123-L380 |
| F-009 | numpy原生不支持的类型集合 `_NON_NUMPY_NATIVE_TYPES` 包括 BFLOAT16, FLOAT8系列(5种), INT4, UINT4, FLOAT4E2M1, INT2, UINT2，通过 `ml_dtypes` 包提供支持。 | `src/onnx_ir/_core.py` L87-L101 |
| F-010 | `_BITWIDTH_MAP` 明确记录每种DataType的位宽：COMPLEX64=64位, COMPLEX128=128位, INT4/UINT4/FLOAT4E2M1=4位, INT2/UINT2=2位。 | `src/onnx_ir/_enums.py` L382-L408 |

## 张量体系（Tensor Protocol Hierarchy）

| 编号 | 事实 | 源码位置 |
|------|------|----------|
| F-011 | `TensorBase` 是所有张量类的抽象基类，继承 `abc.ABC`, `TensorProtocol`, `PrettyPrintable`，使用 `__slots__` 定义 `_doc_string`, `_metadata`, `_metadata_props`, `_name` 四个字段。 | `src/onnx_ir/_core.py` L122-L141 |
| F-012 | `TensorBase` 提供 `name`, `doc_string`, `size`（元素数，用 `math.prod(shape.numpy())` 计算）, `nbytes`（字节数，用 `math.ceil(dtype.itemsize * size)` 处理4位/2位类型）, `metadata_props`（可序列化元数据）, `meta`（临时分析用MetadataStore）, `tofile()`, `display()` 等公共属性和方法。 | `src/onnx_ir/_core.py` L154-L274 |
| F-013 | `Tensor` 类是不可变具体张量，包装原始数据（numpy/DLPack兼容对象），初始化时**零拷贝**——不做任何数据复制，仅存储引用；numpy scalar自动转为ndarray；非numpy原生dtype通过 `_maybe_view_np_array_with_ml_dtypes()` 用ml_dtypes做view。 | `src/onnx_ir/_core.py` L435-L537 |
| F-014 | `Tensor` 实现 `__array__` 和 `__dlpack__`/`__dlpack_device__` 协议方法，使其既可直接作为numpy数组使用（`np.array(tensor)`），也支持DLPack零拷贝互操作。 | `src/onnx_ir/_core.py` L539-L555 |
| F-015 | `Tensor.tobytes()` 将张量序列化为小端字节序，通过 `_create_np_array_for_byte_representation()` 处理4位/2位类型的打包（pack_4bitx2/pack_2bitx4）和字节序转换。 | `src/onnx_ir/_core.py` L590-L598, L408-L432 |
| F-016 | `ExternalTensor` 通过 `mmap.mmap` 实现内存映射外部张量数据，`_load()` 方法在首次访问时mmap整个文件，对4位/2位类型先以uint8读入再unpack；包含三层安全检查：字符串路径遍历防护、符号链接realpath检查、硬链接检测（nlink>1拒绝）。 | `src/onnx_ir/_core.py` L616-L863 |
| F-017 | `ExternalTensor` 的 `base_dir` 可变（setter），`location`/`offset`/`length`/`dtype`/`shape` 不可变；`path` 属性计算为 `os.path.join(base_dir, location)`；提供 `invalidate()` 标记数据损坏/删除，`release()` 关闭mmap并释放引用。 | `src/onnx_ir/_core.py` L711-L1019 |
| F-018 | `ExternalTensor.tofile()` 优先使用Linux `os.copy_file_range` 内核拷贝（零用户态buffer），回退到1MiB分块用户态拷贝，支持对端文件对象的 `fileno/flush/tell/seek` 检测。 | `src/onnx_ir/_core.py` L917-L992 |
| F-019 | `StringTensor` 专门处理字符串张量，`dtype` 固定为 `DataType.STRING`，不支持 `tobytes()` 和 `DLPack`，通过 `string_data()` 方法返回 `Sequence[bytes]`，`nbytes` 对所有字符串长度求和。 | `src/onnx_ir/_core.py` L1022-L1110 |
| F-020 | `LazyTensor` 延迟求值张量，接受一个返回 `TensorProtocol` 的callable（thunk），`cache` 参数控制是否缓存结果（默认False即每次访问重新求值）；实现 `__array__`/`__dlpack__`/`numpy()`/`tobytes()` 时触发 `_evaluate()`。 | `src/onnx_ir/_core.py` L1113-L1230 |
| F-021 | `PackedTensor`（v0.1.2新增）存储2位/4位类型的打包格式数据，`dtype` 必须是INT2/UINT2/INT4/UINT4/FLOAT4E2M1，`numpy_packed()` 返回打包的uint8数组，`numpy()` 返回解包后的数组。 | `src/onnx_ir/_core.py` L1233-L1383 |
| F-022 | `TensorProtoTensor`（在serde.py中定义）直接包装 `onnx.TensorProto`，`numpy()` 方法改进了 `onnx.numpy_helper.to_array`：优先使用 `raw_data` 字段配合 `np.frombuffer` 零拷贝，按不同data field（int32_data/int64_data/float_data/double_data/uint64_data/string_data）分别处理，自动处理bfloat16/float8/int4/int2等类型的view转换。 | `src/onnx_ir/serde.py` L311-L556 |

## 形状与符号维度

| 编号 | 事实 | 源码位置 |
|------|------|----------|
| F-023 | `SymbolicDim` 是不可变符号维度，内部存储 `_value`（str/None）和懒初始化的 `_expr_cache`（sympy.Expr），支持算术运算（`+`, `-`, `*`, `//`, `/`, `%`, `neg`, `ceil`, `floor`, `trunc`），`evaluate(bindings)` 用具体值替换符号变量，`free_symbols()` 返回自由符号集合。 | `src/onnx_ir/_core.py` L1386-L1663 |
| F-024 | `Shape` 支持冻结（`freeze()`）后不可修改，提供 `rank()`, `numpy()`（要求全静态维度）, `is_static(dim?)`, `is_dynamic(dim?)`, `is_unknown_dim(dim)`, `has_unknown_dim()`, `evaluate(bindings)`, `simplify()`, `free_symbols()`, `get_denotation()`/`set_denotation()` 等方法；维度合并规则：int优先于SymbolicDim，有名字的SymbolicDim优先于None，同名字保留当前值。 | `src/onnx_ir/_core.py` L1708-L2023 |

## 核心实体：Value/Node/Graph/Model/Function

| 编号 | 事实 | 源码位置 |
|------|------|----------|
| F-025 | `Value` 统一表示图/函数/节点的输入输出，泛化了ONNX的 `ValueInfoProto`。每个Value有0或1个producer Node；当无producer时必须是图输入或Initializer。使用 `dict[Usage, None]`（有序字典）存储uses集合以支持同一值在同一节点被多次引用。 | `src/onnx_ir/_core.py` L2982-L3090 |
| F-026 | `Value` 通过 `_is_graph_input`/`_is_graph_output`/`_is_initializer` 三个布尔标记标识其在图中的角色，这些标记只能由Graph类（`_GraphIO`/`GraphInitializers`）设置；`is_graph_input()`/`is_graph_output()`/`is_initializer()` 方法公开查询。 | `src/onnx_ir/_core.py` L3084-L3090, L3337-L3347 |
| F-027 | `Value.name` setter包含重命名逻辑：如果是initializer，先检查新名称不冲突，再同步更新 `const_value.name`、弹出graph.initializers旧条目并插入新条目；禁止将initializer名称设为None。 | `src/onnx_ir/_core.py` L3200-L3235 |
| F-028 | `Value.replace_all_uses_with(replacement, replace_graph_outputs=False)` 替换所有使用点，遍历 `uses()` 调用每个consumer的 `replace_input_with()`；当值是图输出且 `replace_graph_outputs=False` 时抛出ValueError。 | `src/onnx_ir/_core.py` L3349-L3402 |
| F-029 | `Value` 继承 `WithArithmeticMethods` mixin，通过类级别的 `_magic_handler`（ClassVar）实现算术运算符（`+`, `-`, `*`, `/`, 负号及反向版本），框架作者可通过 `set_value_magic_handler()` 注入自定义handler实现算子录制。 | `src/onnx_ir/_core.py` L2879-L2980 |
| F-030 | `Node` 初始化时：domain为 `"ai.onnx"` 时归一化为 `""`；inputs存储为不可变tuple；outputs在初始化时创建（默认1个输出），每个输出的 `_producer` 设为self、`_index` 设为对应序号；attributes包装为 `_graph_containers.Attributes`；初始化后自动将自身注册为所有input values的usage。 | `src/onnx_ir/_core.py` L2063-L2179 |
| F-031 | `Node.inputs` 不可直接赋值（setter抛出AttributeError），必须通过 `resize_inputs(new_size)` + `replace_input_with(index, value)` 修改；`Node.outputs` 同样不可直接赋值，通过 `resize_outputs(new_size)` 修改（缩小时被移除的输出不能有uses）。 | `src/onnx_ir/_core.py` L2324-L2492 |
| F-032 | `Node` 提供 `predecessors()`（去重的前驱节点，按dict有序去重）、`successors()`（去重的后继节点）、`prepend(nodes)`/`append(nodes)`（委托给graph的insert_before/insert_after）、`op_identifier()` 返回 `(domain, op_type, overload)` 三元组。 | `src/onnx_ir/_core.py` L2366-L2437, L2541-L2546 |
| F-033 | `Node` 支持多设备配置：`device_configurations` 存储 `NodeDeviceConfiguration` 元组，`shard(value, configuration, axis, num_shards, ...)` 方法记录张量分片信息，`sharding_of(value)` 按对象身份匹配返回分片规格，`set_pipeline_stage(configuration, stage)` 设置流水线阶段。 | `src/onnx_ir/_core.py` L2548-L2768 |
| F-034 | `Graph` 继承 `Sequence[Node]`，节点存储在 `_linked_list.DoublyLinkedSet[Node]` 中（双向链表有序集合），支持安全迭代中变异；inputs/outputs包装为 `_graph_containers.GraphInputs/GraphOutputs`（MutableSequence），initializers包装为 `_graph_containers.GraphInitializers`（dict-like）；`_name_authority` 管理自动命名。 | `src/onnx_ir/_core.py` L3512-L3582 |
| F-035 | `Graph` 构造时：先注册inputs和initializers的名称到NameAuthority，再通过 `self.extend(nodes)` 添加节点（每个节点会被设置graph引用、自动命名、输出值自动命名）；提供 `append/extend/remove/insert_after/insert_before` 变异方法、`sort()` 拓扑排序（Kahn算法+堆实现稳定排序）、`clone()` 深拷贝、`subgraphs()`/`all_nodes()` 递归遍历。 | `src/onnx_ir/_core.py` L3551-L3582, L3810-L4013 |
| F-036 | `Graph.sort()` 使用稳定拓扑排序算法（参考MedallionTopologicalSort）：将子图中的所有节点视为包含子图属性节点的前驱；用优先队列（heapq）按负原始索引排序以获得稳定顺序；排序后对每个子图分别reversed后extend回graph。 | `src/onnx_ir/_core.py` L3913-L4013 |
| F-037 | `Graph.remove(nodes, safe=False)` 的safe模式执行三项检查：(1)被移除节点的输出不被其他保留节点使用；(2)被移除节点的输出不是图输出；(3)断开所有input引用（replace_input_with(i, None)）；出错时保证图不被修改（先全部检查再执行）。 | `src/onnx_ir/_core.py` L3839-L3877 |
| F-038 | `GraphView` 是只读视图，inputs/outputs存储为tuple，nodes存储为tuple，initializers为dict，不拥有节点但反映底层变异；可序列化为ONNX、可用于创建Model（创建时拓扑固定、不复制）。 | `src/onnx_ir/_core.py` L4105-L4240 |
| F-039 | `Model` 包含 `graph`（Graph）、`ir_version`、`producer_name`、`producer_version`、`domain`、`model_version`、`doc_string`、`_functions`（以 `(domain,name,overload)` 为key的dict）、`device_configurations` 元组；`opset_imports` 委托给 `graph.opset_imports`；`graphs()` 方法yield主图和所有子图。 | `src/onnx_ir/_core.py` L4243-L4375 |
| F-040 | `Function` 内部包装一个 `Graph` 对象（`_graph`），通过委托模式暴露 `inputs`/`outputs`/`__getitem__`/`__len__`/`__iter__`/`append`/`extend`/`remove`/`insert_after`/`insert_before`/`sort`/`subgraphs`/`all_nodes`/`clone` 等方法；额外有 `attributes`（函数参数定义，支持RefAttr）和 `identifier()` 返回 `(domain, name, overload)`。 | `src/onnx_ir/_core.py` L4553-L4865 |
| F-041 | `Attr` 统一表示普通属性和引用属性（`ref_attr_name` 非None时为RefAttr），构造时对INT/FLOAT强制转为Python int/float（而非numpy类型），对INTS/FLOATS/STRINGS/TENSORS/GRAPHS/TYPE_PROTOS强制转为tuple；提供 `as_float/as_int/as_string/as_tensor/as_graph/as_floats/as_ints/as_strings/as_tensors/as_graphs` 类型安全getter，类型不匹配时抛TypeError。 | `src/onnx_ir/_core.py` L4868-L5090 |
| F-042 | `TypeAndShape` 是dataclass，包含 `type: TypeProtocol | None` 和 `shape: Shape | None` 两个字段，用于构造TypeProto属性值。 | `src/onnx_ir/_core.py` L5258-L5266 |
| F-043 | 类型系统类层次：`_TensorTypeBase`（TensorType, SparseTensorType）和 `_RecursiveTypeBase`（SequenceType, OptionalType）都继承 `TypeProtocol`，递归类型持有 `elem_type`，通过递归 `__eq__` 比较元素类型。 | `src/onnx_ir/_core.py` L2784-L2876 |

## 双向链表与名称管理

| 编号 | 事实 | 源码位置 |
|------|------|----------|
| F-044 | `_LinkBox` 是双向链表节点容器，`prev`/`next` 指向相邻box，`value` 存储实际对象（None表示已擦除/根节点），`owning_list` 指向所属DoublyLinkedSet；`erase()` 方法将自身从链表中摘除并置value为None，但不破坏prev/next指针以便迭代器安全继续。 | `src/onnx_ir/_linked_list.py` L13-L65 |
| F-045 | `DoublyLinkedSet` 使用循环双向链表（root哨兵节点value=None），维护 `_length` 和 `_value_ids_to_boxes: dict[int, _LinkBox]`（按id查找O(1)）；`append/remove` O(1)，`insert_after/insert_before` O(1)（先通过id查box），索引访问O(n)但首尾O(1)；插入重复值时先remove旧的再插入；迭代时遇到erased box跳过。 | `src/onnx_ir/_linked_list.py` L68-L283 |
| F-046 | `DoublyLinkedSet` 迭代器安全保证：迭代中在当前节点后插入的新元素会被遍历到，在当前节点前插入的不会；当前节点被移动到其他位置时，迭代从原位置的next继续。 | `src/onnx_ir/_linked_list.py` L78-L84, L106-L123 |
| F-047 | `NameAuthority` 为匿名value生成 `val_{counter}` 格式名称，为匿名node生成 `node_{op_type}_{counter}` 格式名称；维护 `_value_names` 和 `_node_names` 两个集合防止重复；如果value/node已有名称则不改名；**注意**：名称一旦被跟踪，即使节点/值被移除也不会释放（可能导致计数器无限增长）。 | `src/onnx_ir/_name_authority.py` L10-L72 |

## 序列化/反序列化（serde）

| 编号 | 事实 | 源码位置 |
|------|------|----------|
| F-048 | `from_proto()` 是重载的多态入口，根据proto类型（ModelProto/GraphProto/NodeProto/TensorProto/AttributeProto/ValueInfoProto/TypeProto/FunctionProto/TensorShapeProto/Dimension/OperatorSetIdProto序列/StringStringEntryProto序列）分发到对应的deserialize函数。 | `src/onnx_ir/serde.py` L126-L190 |
| F-049 | `to_proto()` 是多态序列化入口，通过Protocol类型判断分发：ModelProtocol→serialize_model, GraphProtocol→serialize_graph, NodeProtocol→serialize_node, TensorProtocol→serialize_tensor, ValueProtocol→serialize_value, AttributeProtocol（非ref）→serialize_attribute, ReferenceAttributeProtocol→serialize_reference_attribute, TypeProtocol→serialize_type_into, FunctionProtocol→serialize_function, GraphViewProtocol→serialize_graph。 | `src/onnx_ir/serde.py` L258-L308 |
| F-050 | 图反序列化 `_deserialize_graph()` 使用作用域栈 `scoped_values: list[dict[str, Value]]` 处理嵌套子图的值引用：两阶段处理——先声明所有node output名称（处理前向引用和子图跨作用域引用），再反序列化节点体。 | `src/onnx_ir/serde.py` L763-L886 |
| F-051 | 反序列化张量时，`EXTERNAL` data_location的TensorProto转为 `ExternalTensor`，STRING类型转为 `StringTensor`，其余转为 `TensorProtoTensor`（零拷贝包装proto）。 | `src/onnx_ir/serde.py` L1150-L1179 |
| F-052 | `deserialize_tensor()` 接受 `base_path` 参数用于ExternalTensor的base_dir设置；在 `_io.load()` 中加载模型后会调用 `external_data.set_base_dir(model.graph, os.path.dirname(path))` 设置外部数据基础目录。 | `src/onnx_ir/serde.py` L1150-L1167; `src/onnx_ir/_io.py` L19-L38 |
| F-053 | `from_onnx_text()` 通过 `onnx.parser.parse_model()` 解析文本格式，可选接受initializers参数将张量附加到对应Value；`to_onnx_text()` 通过 `onnx.printer.to_text()` 序列化，支持 `exclude_initializers` 选项。 | `src/onnx_ir/serde.py` L193-L255 |

## IO与Tape

| 编号 | 事实 | 源码位置 |
|------|------|----------|
| F-054 | `_io.load()` 使用 `onnx.load(path, load_external_data=False)` 加载proto（不让ONNX加载外部数据），反序列化为IR Model后设置external data base_dir为模型文件所在目录。 | `src/onnx_ir/_io.py` L19-L38 |
| F-055 | `_io.save()` 支持external_data模式：当指定external_data路径时，调用 `external_data.unload_from_model()` 将initializer转为外部数据（支持size_threshold_bytes阈值、max_shard_size_bytes分片、max_workers并行写入、max_in_flight_bytes内存上限、alignment对齐），序列化后在finally块中恢复原始initializer值以保证model不变。 | `src/onnx_ir/_io.py` L41-L203 |
| F-056 | `Tape` 是图构建录制器，收集 `op()` 创建的节点和 `initializer()` 创建的初始化值到内部list；`op()` 返回单输出Value，`op_multi_out()` 返回多输出序列；`used_opsets` 记录所有用到的 `(domain, version)` 集合；`graph_like` 参数可绑定到Graph/Function使节点自动添加。 | `src/onnx_ir/_tape.py` L20-L205 |
| F-057 | `Builder` 继承 `Tape`，通过 `__getattr__` 魔术方法实现 `builder.Add(...)`, `builder.MatMul(...)` 风格的算子调用API，支持 `_domain`/`_version`/`_outputs` kwargs控制，`_outputs` 为int时创建对应数量输出、为Sequence时设置输出名称。 | `src/onnx_ir/_tape.py` L208-L242 |
| F-058 | `tape.py` 公开模块仅导出 `Tape` 类（Builder是内部扩展），并通过 `Tape.__module__ = __name__` 重设模块路径。 | `src/onnx_ir/tape.py` L9-L15 |

## 元数据存储

| 编号 | 事实 | 源码位置 |
|------|------|----------|
| F-059 | `MetadataStore` 继承 `collections.UserDict`，在普通dict基础上增加 `_invalid_keys: set[str]` 集合，提供 `invalidate(key)` 标记键失效和 `is_valid(key)` 查询有效性；`__setitem__` 写入时自动从invalid_keys中移除该键；`__bool__` 在data非空或有invalid_keys时返回True。 | `src/onnx_ir/_metadata.py` L12-L48 |
| F-060 | 所有IR核心实体（TensorBase/Value/Node/Graph/GraphView/Model/Function/Attr）都有两个元数据接口：`meta`（MetadataStore，用于中间分析，不序列化）和 `metadata_props`（dict[str,str]，序列化到ONNX proto）。 | `src/onnx_ir/_core.py` L184-L203, L2508-L2527, L3016-L3335, L4017-L4037, L4191-L4207, L4311-L4331, L4685-L4700, L4946-L4954 |

## 废弃API与便捷构造器

| 编号 | 事实 | 源码位置 |
|------|------|----------|
| F-061 | `Input()` 函数自v0.1.9起标记为deprecated，等价于 `Value(name=name, shape=shape, type=type, doc_string=doc_string)`，建议使用 `ir.val(...)` 替代。 | `src/onnx_ir/_core.py` L3460-L3473 |
| F-062 | 便捷属性构造器（`AttrFloat32`, `AttrInt64`, `AttrString`, `AttrTensor`, `AttrGraph`, `AttrFloat32s`, `AttrInt64s`, `AttrStrings`, `AttrTensors`, `AttrGraphs`, `AttrSparseTensor`, `AttrSparseTensors`, `AttrTypeProto`, `AttrTypeProtos`）和 `RefAttr()` 都是工厂函数，统一创建 `Attr` 实例。 | `src/onnx_ir/_core.py` L5096-L5290 |
| F-063 | 顶层便捷构造器 `tensor()`, `node()`, `val()` 从 `_convenience._constructors` 导入，提供比直接调用核心类更友好的API。 | `src/onnx_ir/__init__.py` L112 |
