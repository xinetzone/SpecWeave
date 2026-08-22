# onnx/ 核心项目 - R阶段事实采集

> 源码路径：`d:\spaces\SpecWeave\external\libs\models\onnx\onnx\`

## Protobuf IR 模型结构

### F-001: AttributeProto 包含14种属性类型枚举值（UNDEFINED=0, FLOAT=1, INT=2, STRING=3, TENSOR=4, GRAPH=5, SPARSE_TENSOR=11, TYPE_PROTO=13, FLOATS=6, INTS=7, STRINGS=8, TENSORS=9, GRAPHS=10, SPARSE_TENSORS=12, TYPE_PROTOS=14）
**信源**：`onnx/onnx.proto` L144-L161

### F-002: AttributeProto 包含 ref_attr_name 字段（字段号21），用于引用父函数作用域中的属性，仅在子图（函数）中有效
**信源**：`onnx/onnx.proto` L166-L170

### F-003: AttributeProto 的 type 字段（字段号20）是类型鉴别器，IR_VERSION >= 2（IR_VERSION_2017_10_30）起必须设置并与实际值字段匹配
**信源**：`onnx/onnx.proto` L175-L181

### F-004: ValueInfoProto 包含 name（字段1）、type（字段2）、doc_string（字段3）、metadata_props（字段4）四个字段
**信源**：`onnx/onnx.proto` L205-L215

### F-005: NodeProto 包含 input（重复字符串，字段1）、output（重复字符串，字段2）、name（字段3）、op_type（字段4）、domain（字段7）、overload（字段8）、attribute（重复AttributeProto，字段5）、doc_string（字段6）、metadata_props（字段9）、device_configurations（字段10）
**信源**：`onnx/onnx.proto` L224-L250

### F-006: ModelProto 的 ir_version 字段（字段1）必须存在，opset_import 字段（字段8）为重复 OperatorSetIdProto
**信源**：`onnx/onnx.proto` L449-L462

### F-007: ModelProto 在 IR_VERSION >= 8（IR_VERSION_2021_7_30）起支持 functions 字段（字段25），存储模型局部函数列表，(domain, name, overload) 三元组必须唯一
**信源**：`onnx/onnx.proto` L505-L521；`onnx/onnx.proto` L99-L104

### F-008: GraphProto 包含 node（重复NodeProto，字段1）、name（字段2）、initializer（重复TensorProto，字段5）、sparse_initializer（重复SparseTensorProto，字段15）、doc_string（字段10）、input（重复ValueInfoProto，字段11）、output（重复ValueInfoProto，字段12）、value_info（重复ValueInfoProto，字段13）、quantization_annotation（字段14）、metadata_props（字段16）
**信源**：`onnx/onnx.proto` L564-L602

### F-009: TensorProto.DataType 枚举定义了26种数据类型，从 UNDEFINED=0 到 INT2=26，包括FLOAT=1, UINT8=2, INT8=3, FLOAT16=10, DOUBLE=11, BFLOAT16=16, FLOAT8E4M3FN=17, UINT4=21, INT4=22, FLOAT4E2M1=23, FLOAT8E8M0=24, UINT2=25, INT2=26
**信源**：`onnx/onnx.proto` L608-L663

### F-010: TensorProto 的数据存储字段包括 float_data（字段4）、int32_data（字段5）、string_data（字段6）、int64_data（字段7）、raw_data（字段9）、double_data（字段10）、uint64_data（字段11）
**信源**：`onnx/onnx.proto` L686-L785

### F-011: TensorProto 包含 external_data 字段（字段13），以 StringStringEntryProto 键值对描述外部数据位置，识别键包括 "location"（必需）、"offset"（可选）、"length"（可选）、"checksum"（可选）
**信源**：`onnx/onnx.proto` L751-L760

### F-012: TensorProto 的 data_location 字段（字段14）是 DataLocation 枚举（DEFAULT=0, EXTERNAL=1），默认为 DEFAULT（数据存储在protobuf消息内部）
**信源**：`onnx/onnx.proto` L762-L771

### F-013: TensorShapeProto.Dimension 使用 oneof value 表示维度，dim_value（int64）或 dim_param（字符串符号变量），并有可选 denotation 字段
**信源**：`onnx/onnx.proto` L819-L833

### F-014: TypeProto 使用 oneof value 表示类型变体：tensor_type（字段1）、sequence_type（字段4）、map_type（字段5）、optional_type（字段9）、sparse_tensor_type（字段8）、opaque_type（字段7）
**信源**：`onnx/onnx.proto` L838-L916

### F-015: TypeProto.Tensor 包含 elem_type（int32，字段1）和 shape（TensorShapeProto，字段2）；TypeProto.SparseTensor 结构相同；TypeProto.Sequence 和 TypeProto.Optional 包含 elem_type（TypeProto）；TypeProto.Map 包含 key_type（int32）和 value_type（TypeProto）
**信源**：`onnx/onnx.proto` L840-L890

### F-016: FunctionProto 包含 name（字段1）、input（重复string，字段4）、output（重复string，字段5）、attribute（重复string，字段6）、attribute_proto（重复AttributeProto，字段11）、node（重复NodeProto，字段7）、opset_import（重复OperatorSetIdProto，字段9）、domain（字段10）、overload（字段13）、value_info（字段12）、metadata_props（字段14）
**信源**：`onnx/onnx.proto` L946-L1011

### F-017: FunctionProto 的 since_version（字段2）和 status（字段3）已在 IR_VERSION 8 中废弃，使用 reserved 关键字保留字段号
**信源**：`onnx/onnx.proto` L951-L959

### F-018: OperatorSetIdProto 包含 domain（字段1，空字符串或缺失表示ONNX标准域）和 version（字段2，必须存在）
**信源**：`onnx/onnx.proto` L928-L938

### F-019: SparseTensorProto 包含 values（TensorProto，字段1，形状[NNZ]）、indices（TensorProto，字段2，形状[NNZ,rank]或[NNZ]）、dims（重复int64，字段3）
**信源**：`onnx/onnx.proto` L792-L814

### F-020: IR_VERSION 枚举当前值为 0x0000000E（14），从 IR_VERSION_2017_10_10=1 到 IR_VERSION=14 共经历14个版本
**信源**：`onnx/onnx.proto` L50-L130；`onnx/onnx.proto` L129

## Python Helper API

### F-021: make_node 函数接受 op_type、inputs、outputs、name、doc_string、domain、overload 参数，kwargs 中的属性通过 make_attribute 转换后添加到 NodeProto，值为 None 的属性被跳过
**信源**：`onnx/helper.py` L136-L182

### F-022: make_graph 函数接受 nodes、name、inputs、outputs、initializer、doc_string、value_info、sparse_initializer 参数，返回 GraphProto；initializer/value_info/sparse_initializer 默认为空列表
**信源**：`onnx/helper.py` L203-L243

### F-023: make_model 函数创建 ModelProto，自动设置 ir_version 为当前 onnx.IR_VERSION，若未指定 opset_imports 则默认导入当前 ai.onnx opset 版本（通过 defs.onnx_opset_version()）
**信源**：`onnx/helper.py` L297-L329

### F-024: make_model_gen_version 函数在未指定 ir_version 时，根据 opset_imports 通过 find_min_ir_version_for 计算最小所需 IR 版本
**信源**：`onnx/helper.py` L334-L340

### F-025: make_tensor 函数在 raw=False 时根据 data_type 选择对应 proto 存储字段；在 raw=True 时使用 raw_data 字段；STRING 类型不支持 raw=True；4-bit 类型（UINT4/INT4/FLOAT4E2M1）按2个元素打包到1字节，2-bit 类型按4个元素打包到1字节
**信源**：`onnx/helper.py` L365-L485

### F-026: make_attribute 函数根据 Python 值类型自动推断 AttributeProto 类型：整数→INT，浮点数→FLOAT，字符串/字节→STRING，TensorProto→TENSOR，SparseTensorProto→SPARSE_TENSOR，GraphProto→GRAPH，TypeProto→TYPE_PROTO；可迭代对象映射到对应的复数类型（INTS/FLOATS/STRINGS/TENSORS等）
**信源**：`onnx/helper.py` L608-L699

### F-027: make_attribute_ref 函数创建引用属性（ref_attr_name 非空），该属性不携带值，在实例化时从父函数的同名属性获取值，仅在函数子图中有效
**信源**：`onnx/helper.py` L702-L733

### F-028: make_tensor_value_info 函数创建 ValueInfoProto，接受 name、elem_type、shape、doc_string、shape_denotation 参数；shape 中 int 值设为 dim_value，str 值设为 dim_param，None 值不设维度值；显式传入空 shape 时会产生空 dim 列表（与未设 shape 不同）
**信源**：`onnx/helper.py` L787-L847

### F-029: make_function 函数接受 domain、fname、inputs、outputs、nodes、opset_imports、attributes（字符串列表）、attribute_protos（AttributeProto列表）、doc_string、overload、value_info 参数
**信源**：`onnx/helper.py` L261-L294

### F-030: tensor_dtype_to_field 函数（带 lru_cache）将 TensorProto 数据类型映射到存储字段名：FLOAT→float_data，INT32→int32_data，INT64→int64_data，DOUBLE→double_data，UINT32/UINT64→uint64_data，STRING→string_data
**信源**：`onnx/helper.py` L1309-L1330

### F-031: VERSION_TABLE 维护了从 ONNX 1.0 到 1.23.0 的版本映射表，每行记录 Release-version、IR version、ai.onnx version、ai.onnx.ml version、ai.onnx.training version
**信源**：`onnx/helper.py` L45-L81

### F-032: _mapping.TENSOR_TYPE_MAP 字典将 TensorProto 数据类型映射到 (np_dtype, storage_dtype, name) 三元组；UINT8/INT8/BOOL/FLOAT16/BFLOAT16/FLOAT8/UINT4/INT4/FLOAT4E2M1/UINT2/INT2 的存储类型均为 INT32；UINT32 的存储类型为 UINT64
**信源**：`onnx/_mapping.py` L24-L119

## Checker 检查器机制

### F-033: check_model 函数验证 ModelProto：ir_version 必须设置且不能超过当前 IR_VERSION；metadata_props 中不能有重复 key；IR >= 3 必须指定 opset_import；IR < 3 不能有 opset_import（此时默认 opset 域版本为1）
**信源**：`onnx/checker.cc` L1265-L1296

### F-034: Python checker.py 中所有检查函数（check_value_info、check_tensor、check_attribute、check_node、check_graph、check_sparse_tensor）均将 proto 序列化为字符串后委托给 C++ 实现（onnx.onnx_cpp2py_export.checker 模块，别名 C）
**信源**：`onnx/checker.py` L54-L117

### F-035: MAXIMUM_PROTOBUF 常量值为 2147483647（2 GiB - 1 字节），超过此大小的 protobuf 序列化会触发 ValueError 提示使用外部数据
**信源**：`onnx/checker.py` L35；`onnx/serialization.py` L105-L109

### F-036: DEFAULT_CONTEXT 初始化时 ir_version 设为当前 IR_VERSION，opset_imports 设为 {"": onnx.defs.onnx_opset_version()}
**信源**：`onnx/checker.py` L39-L42

### F-037: check_model 的 full_check=True 时，会在基本检查后对模型副本执行形状推断（ShapeInferenceOptions{check_type=true, error_mode=1, data_prop=false}），且不修改原始模型
**信源**：`onnx/checker.cc` L1326-L1329；`onnx/checker.cc` L1341-L1347

### F-038: IR_VERSION >= 8 时 check_model 会调用 check_model_local_functions 检查模型局部函数，并调用 check_function_call_cycles 检测函数调用循环
**信源**：`onnx/checker.cc` L1301-L1304

## 序列化/反序列化

### F-039: _Registry 类维护 _serializers 字典（格式名→ProtoSerializer）和 _extension_to_format 字典（文件扩展名→格式名），支持 register()、get()、get_format_from_file_extension() 方法
**信源**：`onnx/serialization.py` L51-L91

### F-040: ONNX 内置注册4种序列化器：_ProtobufSerializer（格式"protobuf"，扩展名.onnx/.pb）、_TextProtoSerializer（格式"textproto"，扩展名.txtpb/.textproto/.prototxt/.pbtxt）、_JsonSerializer（格式"json"，扩展名.json/.onnxjson）、_TextualSerializer（格式"onnxtxt"，扩展名.onnxtxt/.onnxtext）
**信源**：`onnx/serialization.py` L94-L212

### F-041: _ProtobufSerializer 序列化时若 proto 字节超过 2GiB 限制会抛出 ValueError，提示使用 save_as_external_data
**信源**：`onnx/serialization.py` L100-L110

### F-042: _TextualSerializer 反序列化时会发出实验性警告，并根据 proto 类型分别调用 onnx.parser.parse_model/parse_graph/parse_function/parse_node
**信源**：`onnx/serialization.py` L183-L204

### F-043: load_model 函数支持 file-like 对象、字符串路径或 PathLike 对象；format 未指定时从文件扩展名推断，无法推断时默认为 "protobuf"；load_external_data=True 时自动从模型所在目录加载外部数据
**信源**：`onnx/__init__.py` L210-L239

### F-044: save_model 函数支持 save_as_external_data 参数，可将张量数据序列化到外部文件；all_tensors_to_one_file=True 时所有张量保存到单个外部文件；size_threshold=1024 为默认阈值，数据 >= 阈值时才转为外部数据
**信源**：`onnx/__init__.py` L299-L349

### F-045: __init__.py 中定义了向后兼容别名：load=load_model，load_from_string=load_model_from_string，save=save_model
**信源**：`onnx/__init__.py` L372-L375

## OpSchema 算子注册机制

### F-046: OpSchema 类提供链式调用 API 注册算子，包括 SinceVersion()、NumInputs()、NumOutputs()、SetDoc()、SetDomain()、Attr()、Input()、Output()、TypeConstraint()、AllowConsumed() 等方法
**信源**：`onnx/defs/schema.h` L352-L582

### F-047: FormalParameterOption 枚举定义三种形参选项：Single=0（单个必选）、Optional=1（单个可选）、Variadic=2（可变参数，最小元数由 min_arity 指定）
**信源**：`onnx/defs/schema.h` L151-L162

### F-048: OpSchema 支持通过宏 ONNX_OPERATOR_SET_SCHEMA(name, ver, impl) 注册特定版本算子，对应域包括 Onnx（ONNX_DOMAIN=""）、OnnxML（AI_ONNX_ML_DOMAIN="ai.onnx.ml"）、OnnxTraining（AI_ONNX_TRAINING_DOMAIN="ai.onnx.training"）、OnnxPreview（AI_ONNX_PREVIEW_DOMAIN="ai.onnx.preview"）
**信源**：`onnx/defs/schema.h` L1278-L1302；`onnx/common/constants.h` L13-L19

### F-049: OpSchemaRegistry 是单例注册表（ISchemaRegistry 实现），OpSchemaRegisterOnce 在构造时自动将 OpSchema 注册到 OpSchemaRegistry，未显式设置 SinceVersion 时默认设为1
**信源**：`onnx/defs/schema.h` L911-L1046

### F-050: TypeConstraintParam 和 TypeConstraintMap 用于类型约束：类型约束字符串（如"T"）映射到允许的 DataTypeSet 和描述字符串；Input()/Output() 方法通过类型字符串引用类型约束
**信源**：`onnx/defs/schema.h` L487-L582；`onnx/defs/schema.h` L122-L126

### F-051: OpSchema 支持 FunctionBody() 和 ContextDependentFunctionBodyBuilder 机制，可为算子注册函数体构建器，实现上下文化的函数体展开
**信源**：`onnx/defs/schema.h` L91-L95；`onnx/defs/schema.h` L764-L818

## C++ IR 类层次

### F-052: C++ IR 使用三个核心结构体：Graph（计算图）、Node（计算节点）、Value（值/边），Graph 拥有所有 Node 和 Value 的所有权（通过 unique_ptr），所有内部引用为原始指针
**信源**：`onnx/common/ir.h` L43-L55；`onnx/common/ir.h` L952-L953

### F-053: Node 继承自 Attributes<Node>（CRTP模式），使用双向循环链表（next_in_graph 数组）维护图中的拓扑序，output_ 节点作为哨兵节点
**信源**：`onnx/common/ir.h` L438-L468

### F-054: Value 结构体包含 node_（生产节点指针）、offset_（在节点输出中的索引）、unique_（唯一ID）、elem_type_、sizes_（vector<Dimension>）、type_（unique_ptr<TypeProto>）等字段；提供 replaceAllUsesWith() 方法替换所有使用点
**信源**：`onnx/common/ir.h` L307-L436

### F-055: Dimension 结构体使用 is_unknown、is_int 标志和 dim（int64_t）、param（string）字段表示维度，支持未知维度、整数值维度和符号参数维度
**信源**：`onnx/common/ir.h` L70-L79

### F-056: AttributeKind 枚举定义12种属性种类：f, fs, i, is, s, ss, t, ts, g, gs, tp, tps（对应单值/列表的float/int/string/tensor/graph/type_proto）
**信源**：`onnx/common/ir.h` L81-L96

### F-057: Graph 类中 initializer_node_ 是独立的 Param 节点，用于持有不在图输入中的初始化器值（IR >= 4 支持）；addInitializerAndCreateValue() 方法同时添加 Tensor 和对应的 Value
**信源**：`onnx/common/ir.h` L962-L965；`onnx/common/ir.h` L1078-L1097

### F-058: Graph 维护 used_names_ 哈希表（名字→引用计数）实现 O(1) 的名字唯一性检查，subgraph_bearing_nodes_ 集合跟踪包含子图属性的节点，避免遍历所有节点
**信源**：`onnx/common/ir.h` L983-L1005

### F-059: Use 结构体表示值的使用点，包含 user（Node* 消费者节点）和 offset（在消费者输入中的索引）
**信源**：`onnx/common/ir.h` L291-L295

## Shape Inference 形状推断

### F-060: InferenceContext 抽象类提供 getAttribute()、getNumInputs()、getInputType()、getInputData()、getNumOutputs()、getOutputType()、getGraphAttributeInferencer() 等虚函数接口
**信源**：`onnx/defs/shape_inference.h` L92-L130

### F-061: InferenceFunction 类型为 std::function<void(InferenceContext&)>，DataPropagationFunction 类型为 std::function<void(DataPropagationContext&)>；dummyInferenceFunction 为空实现作为默认推断函数
**信源**：`onnx/defs/shape_inference.h` L154-L162

### F-062: ShapeInferenceOptions 包含三个选项：check_type（检查输入输出类型相等）、error_mode（0=不抛节点级错误，1=抛节点级错误）、enable_data_propagation（启用数据传播以进行形状计算）
**信源**：`onnx/defs/shape_inference.h` L26-L38

### F-063: kMaxMaterializedRank 常量值为1024，限制形状推断中物化的最大秩，防止无界 protobuf 物化
**信源**：`onnx/defs/shape_inference.h` L24

### F-064: Python 端 infer_shapes() 函数接受 check_type、strict_mode、data_prop 参数，将 ModelProto 序列化后委托给 C++ 实现（onnx.onnx_cpp2py_export.shape_inference.infer_shapes），推断结果添加到 graph.value_info 字段
**信源**：`onnx/shape_inference.py` L32-L70

## Compose 图组合

### F-065: merge_models 函数要求两个模型具有相同的 ir_version 和兼容的 opset_import（同一域的版本必须相同）；合并时合并 metadata_props（同名key值必须相同），functions 不能有重名
**信源**：`onnx/compose.py` L353-L441

### F-066: merge_graphs 函数在连接两个图前调用 check_overlapping_names 检查名字冲突（edge/value_info/initializer/sparse_initializer），存在冲突时抛出 ValueError 并建议使用 add_prefix
**信源**：`onnx/compose.py` L22-L88；`onnx/compose.py` L200-L210

### F-067: add_prefix_graph 函数可选择性地为图中 nodes、edges、inputs、outputs、initializers、value_infos 添加前缀；空名字不添加前缀；rename_edges 时跳过图输出名（由 rename_outputs 单独处理）；递归处理子图属性（g 和 graphs）
**信源**：`onnx/compose.py` L445-L565

### F-068: add_prefix 函数在 add_prefix_graph 基础上还支持 rename_functions 参数，对模型局部函数名也添加前缀
**信源**：`onnx/compose.py` L568-L620

## Parser/Printer 文本格式

### F-069: Python parser 模块提供 parse_model、parse_graph、parse_function、parse_node 四个函数，均委托给 C++ 解析器（onnx.onnx_cpp2py_export.parser），返回三元组 (success, msg, proto_str)，失败时抛出 ParseError
**信源**：`onnx/parser.py` L14-L73

### F-070: Python printer.to_text() 函数根据 proto 类型分别调用 C++ 的 model_to_text、function_to_text、graph_to_text、node_to_text
**信源**：`onnx/printer.py` L10-L21

## 版本转换

### F-071: version_converter.convert_version() 函数接受 ModelProto 和 target_version，序列化后委托给 C++ 实现（onnx.onnx_cpp2py_export.version_converter.convert_version）
**信源**：`onnx/version_converter.py` L17-L39

### F-072: find_min_ir_version_for() 函数根据 OperatorSetIdProto 列表查找所需的最小 IR 版本，通过 OP_SET_ID_VERSION_MAP 映射表查表，取各域所需 IR 版本的最大值
**信源**：`onnx/helper.py` L108-L133

## 外部数据处理

### F-073: external_data_helper 使用三层安全防御：第一层属性白名单（_ALLOWED_EXTERNAL_DATA_KEYS = {location, offset, length, checksum, basepath}）忽略未知键；第二层 ExternalDataInfo.__init__ 验证 offset 和 length 为非负整数；第三层 load_external_data_for_tensor 验证文件大小
**信源**：`onnx/external_data_helper.py` L35-L57；`onnx/external_data_helper.py` L60-L100

### F-074: C++ checker 中 verify_path_containment 函数对外部数据路径进行规范化（weakly_canonical），验证路径不超出模型目录范围（防止路径遍历攻击）；resolve_external_data_location 要求 location 为相对路径且不包含 ".." 路径组件
**信源**：`onnx/checker.cc` L1364-L1409

### F-075: numpy_helper.to_array() 支持从外部数据加载张量（uses_external_data 检测 + load_external_data_for_tensor）；raw_data 按小端序存储，大端系统上自动 byteswap；支持4-bit/2-bit 类型的解包
**信源**：`onnx/numpy_helper.py` L187-L298

## 内联处理

### F-076: inliner.inline_local_functions() 函数将模型中所有对模型局部函数的调用递归内联，convert_version 参数控制是否进行版本转换
**信源**：`onnx/inliner.py` L11-L27

### F-077: inliner.inline_selected_functions() 支持选择性内联，通过 function_ids 指定要内联（或排除）的函数，exclude 参数控制是内联列表内还是列表外的函数，inline_schema_functions 参数控制是否内联 schema 定义的函数
**信源**：`onnx/inliner.py` L30-L60

## 常量和域

### F-078: C++ 常量定义了 ONNX 域：ONNX_DOMAIN=""（空字符串），AI_ONNX_DOMAIN="ai.onnx"（两者在 proto 表示中等价，NormalizeDomain 将 "ai.onnx" 转为 ""）；ML域 "ai.onnx.ml"；训练域 "ai.onnx.training"；预览域 "ai.onnx.preview"
**信源**：`onnx/common/constants.h` L13-L27

### F-079: ONNX_DOMAIN（""）和 AI_ONNX_DOMAIN（"ai.onnx"）通过 NormalizeDomain() 函数统一为空字符串，IsOnnxDomain() 检查域是否为两者之一
**信源**：`onnx/common/constants.h` L21-L27

### F-080: OperatorStatus 枚举定义 EXPERIMENTAL=0 和 STABLE=1 两个值，对应 Python 中 EXPERIMENTAL 和 STABLE 常量
**信源**：`onnx/onnx.proto` L941-L944；`onnx/__init__.py` L21-L22

### F-081: ModelProto 覆写了 __repr__ 方法，显示 ir_version、opset_import（显示为{domain:version}字典）、domain、producer_name、producer_version、graph、functions 数量；GraphProto 的 __repr__ 显示 name、inputs/outputs/initializers/nodes/value_info 数量
**信源**：`onnx/__init__.py` L378-L470

### F-082: CheckerContext 包含 ir_version_、opset_imports_、is_main_graph_、schema_registry_（默认 OpSchemaRegistry::Instance()）、model_dir_、skip_opset_compatibility_check_、check_custom_domain_ 等字段
**信源**：`onnx/checker.h` L40-L103

### F-083: LexicalScopeContext 支持词法作用域链，通过 parent_context_ 指针构成链，this_or_ancestor_graph_has() 方法递归查找当前图和祖先图中的名字
**信源**：`onnx/checker.h` L105-L145
