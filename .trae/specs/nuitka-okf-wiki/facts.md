# Nuitka V4.1rc11 源码事实清单

> 源码根目录：`d:\spaces\SpecWeave\playground\chaos\libs\Nuitka\nuitka`
> 采集日期：2026-08-22
> G1质量门：所有事实为零推测客观描述，不含"用于"/"目的是"等推断词

---

## 一、项目基本信息

- **F-001**: [Version.py:6-8] `version_string = "Nuitka V4.1rc11\nCopyright (C) 2026 Kay Hayen."`
- **F-002**: [Version.py:11-16] `getNuitkaVersion()` 返回版本字符串（split()[1][1:]）；`getNuitkaVersionYear()` 返回版权年份2026
- **F-003**: [__init__.py:6-7] 模块docstring声明Nuitka是"an optimizing Python compiler that is compatible and integrates with CPython, but also works on its own"
- **F-004**: [__main__.py:4-9] 主程序docstring描述："translates one or more modules to a C source code using Python C/API in a '*.build' directory and then compiles that to either an executable or an extension module or package"
- **F-005**: 许可证：GNU Affero General Public License, Version 3（每个源文件头部声明）

---

## 二、编译主流程（MainControl.py + __main__.py）

- **F-006**: [__main__.py:133-293] `main()` 函数执行：环境检查→重执行判断（`reExecuteNuitka`）→`setupHooks()`→`Options.parseArgs()`→创建runner文件→`activatePlugins()`→环境变量恢复→`nuitka_main()`
- **F-007**: [MainControl.py:1145] `_main()` 函数执行完整编译流程：`setupImportingFromOptions()`→`onCompilationStartChecks()`→`_createMainModule()`→`compileTree()`→standalone/onefile打包→`onFinalResult()`→`writeCompilationReports()`
- **F-008**: [MainControl.py:229-386] `_createMainModule()` 执行：`onBeforeCodeParsing()`→`buildMainModuleTree()`→扫描额外路径→`onModuleInitialSet()`→`optimizeModules()`→`checkFreezingModuleSet()`→`onModuleCompleteSet()`
- **F-009**: [MainControl.py:486-600] `makeSourceDirectory()` 执行：Finalization准备→为每个编译模块调用`generateModuleCode()`→生成`__helpers.h/c`和`__constants.h/c`→写入C源文件
- **F-010**: [__main__.py:180-208] 重执行条件：`sys.flags.no_site == 0`、`PYTHONHASHSEED != "0"`、Python 3.11+的frozen stdlib模块与Nuitka不兼容时触发`reExecuteNuitka()`

---

## 三、AST构建与内部树（tree/ + nodes/）

### 3.1 节点元类与基类体系

- **F-011**: [nodes/NodeMetaClasses.py:51] 元类`NodeCheckMetaClass(ABCMeta)`维护类属性`kinds = {}`字典，注册所有节点kind→类的映射
- **F-012**: [nodes/NodeMetaClasses.py:54-66] `__new__`自动处理`named_children`元组，为每个子节点生成`subnode_<name>`的`__slots__`条目
- **F-013**: [nodes/NodeMetaClasses.py:107-124] `__init__`对非Base/Mixin结尾的类要求`kind`属性，注册到kinds字典，自动添加`is<KindName>()`检查方法
- **F-014**: [nodes/NodeBases.py:37] `NodeBase(NodeMetaClassBase)`的`__slots__ = ("parent", "source_ref")`；`__init__(self, source_ref)`初始化parent=None
- **F-015**: [nodes/NodeBases.py:75-99] `NodeBase.isConnected()`沿parent链检查节点是否连接到CompiledPythonModule
- **F-016**: [nodes/NodeBases.py:137-149] `NodeBase.makeClone()`通过`self.__class__(source_ref=..., **self.getCloneArgs())`克隆节点
- **F-017**: [nodes/NodeBases.py:782] `StatementBase(NodeBase)`是所有语句节点基类，提供`computeStatementSubExpressions()`默认实现
- **F-018**: [nodes/ExpressionBases.py:41] `ExpressionBase(NodeBase)`的`__slots__ = ("code_generated",)`；核心抽象方法`computeExpressionRaw(trace_collection)`返回`(node, tags, description)`
- **F-019**: [nodes/ExpressionBases.py:27] `ExpressionBase.getTypeShape()`默认返回`tshape_unknown`；`isCompileTimeConstant()`默认返回False

### 3.2 模块节点体系

- **F-020**: [nodes/ModuleNodes.py:50] `PythonModuleBase(NodeBase)`的`__slots__ = ("module_name", "reason")`；构造参数`(module_name, reason, source_ref)`
- **F-021**: [nodes/ModuleNodes.py:223-229] `CompiledPythonModule`多继承自多个Mixin+ClosureGiverNodeMixin+PythonModuleBase，`kind = "COMPILED_PYTHON_MODULE"`
- **F-022**: [nodes/ModuleNodes.py:236-257] `CompiledPythonModule.__slots__`包含is_top、name、trace_collection、mode、variables、active_functions、source_code、locals_scope等20+属性
- **F-023**: [nodes/ModuleNodes.py:448-455] `CompiledPythonModule.createProvidedVariable(variable_name)`创建ModuleVariable并存入self.variables字典
- **F-024**: [nodes/ModuleNodes.py:564-673] `CompiledPythonModule.computeModule()`创建TraceCollectionModule，执行body的computeStatementsSequence，调用attemptRecursion()
- **F-025**: [nodes/ModuleNodes.py:754] `CompiledPythonPackage(CompiledPythonModule)`，`kind = "COMPILED_PYTHON_PACKAGE"`
- **F-026**: [nodes/ModuleNodes.py:823] `UncompiledPythonModule(PythonModuleBase)`，`kind = "UNCOMPILED_PYTHON_MODULE"`，以字节码形式持有模块
- **F-027**: [nodes/ModuleNodes.py:899] `PythonMainModule(CompiledPythonModule)`，`kind = "PYTHON_MAIN_MODULE"`，`isMainModule()`返回True
- **F-028**: [nodes/ModuleNodes.py:1027] `PythonExtensionModule(PythonModuleBase)`，`kind = "PYTHON_EXTENSION_MODULE"`，包含used_modules、module_filename属性

### 3.3 函数与类节点

- **F-029**: [nodes/FunctionNodes.py:72-77] `ExpressionFunctionBodyBase`多继承自ClosureTakerMixin+ClosureGiverNodeMixin+ChildHavingBodyOptionalMixin+ExpressionBase
- **F-030**: [nodes/FunctionNodes.py:583-587] `ExpressionFunctionBody`，`kind = "EXPRESSION_FUNCTION_BODY"`，__slots__包含parameters、doc、unoptimized_locals等属性
- **F-031**: [nodes/FunctionNodes.py:1105] `ExpressionFunctionCreation`，`kind = "EXPRESSION_FUNCTION_CREATION"`，表示CPython函数对象创建
- **F-032**: [nodes/ClassNodes.py:25] `ExpressionClassBodyBase(ExpressionOutlineFunctionBase)`，`kind = "EXPRESSION_CLASS_BODY"`，__slots__=("doc", "locals_scope")
- **F-033**: [nodes/ClassNodes.py:223] `ExpressionBuiltinType3`，`named_children = ("type_name", "bases", "dict_arg")`；`_calculateMetaClass()`通过ctypes调用CPython私有API`_PyType_CalculateMetaclass`

### 3.4 类型形状系统

- **F-034**: [nodes/shapes/StandardShapes.py:20] `ShapeBase`使用元类`getMetaClassBase("Shape", require_slots=True)`，`helper_code = "OBJECT"`，`getCType()`返回CTypePyObjectPtr
- **F-035**: [nodes/shapes/StandardShapes.py:495] `ShapeTypeUnknown(ShapeBase)`单例`tshape_unknown`
- **F-036**: [nodes/shapes/BuiltinTypeShapes.py] 定义单例：tshape_none, tshape_bool, tshape_int, tshape_float, tshape_complex, tshape_tuple, tshape_list, tshape_set, tshape_dict, tshape_str, tshape_function
- **F-037**: [nodes/shapes/StandardShapes.py:936] `ShapeLoopCompleteAlternative(ShapeBase)`构造参数`shapes`，表示控制流汇合点的多种可能形状

### 3.5 AST构建流程

- **F-038**: [tree/TreeHelpers.py:74-92] `parseSourceCodeToAst(source_code, module_name, filename, line_offset)`调用`ast.parse()`解析源码
- **F-039**: [tree/TreeHelpers.py:288-296] `setBuildingDispatchers(path_args3, path_args2, path_args1)`设置三个全局调度字典，对应1/2/3参数的AST节点构建函数
- **F-040**: [tree/TreeHelpers.py:299-329] `buildNode(provider, node, source_ref)`是AST调度核心，根据节点kind查找构建函数并调用
- **F-041**: [tree/Building.py:816-993] `buildParseTree(provider, ast_tree, source_ref, is_main)`执行：pushFutureSpec→extractDocFromBody→buildStatementsNode→注入`__doc__`/`__file__`/`__compiled__`等赋值→makeModuleFrame→popFutureSpec
- **F-042**: [tree/Building.py:1303-1491] `buildModule(...)`是模块构建顶层入口：决定source_ref→读取源码→parseSourceCodeToAst→_createModule→注册根模块→createModuleTree
- **F-043**: [tree/Building.py:996-1037] `decideCompilationMode(is_top, module_name, ...)`决定模块编译模式（"compiled"或"bytecode"）：早期导入的标准库模块强制bytecode
- **F-044**: [tree/Building.py:1069-1162] `_createModule(...)`根据条件创建不同模块节点：extension→PythonExtensionModule；is_main→PythonMainModule；is_package→CompiledPythonPackage等

---

## 四、变量与闭包系统

- **F-045**: [nodes/NodeBases.py:539-586] `CodeNodeMixin(object)`，__slots__=()，构造参数(name, code_prefix)；`getCodeName()`通过父provider的code name+uid生成C标识符唯一名称
- **F-046**: [nodes/NodeBases.py:589] `ClosureGiverNodeMixin(CodeNodeMixin)`构造时初始化`self.temp_variables = {}`、`self.temp_scopes = {}`
- **F-047**: [nodes/NodeBases.py:631-656] `ClosureGiverNodeMixin.allocateTempVariable(temp_scope, name, ...)`分配临时变量，创建TempVariable实例
- **F-048**: [nodes/NodeBases.py:711] `ClosureTakerMixin(object)`，构造参数(provider)，初始化`self.taken = set()`（闭包变量集合）
- **F-049**: [Variables.py:28] `Variable`类__slots__包含variable_name、owner、version_number、traces、users、writers
- **F-050**: [Variables.py:293] `LocalVariable(Variable)`；[L331] `ParameterVariable(LocalVariable)`；[L352] `ModuleVariable(Variable)`；[L404] `TempVariable(Variable)`；[L437] `LocalsDictVariable(Variable)`

---

## 五、优化系统（optimizations/）

- **F-051**: [optimizations/Optimization.py:47-63] `optimizeCompiledPythonModule(module)`包含`while True`微遍循环：调用`module.computeModule()`，通过tag_set判断是否继续
- **F-052**: [optimizations/Optimization.py:287-367] `_makeOptimizationPass()`遍历ModuleRegistry中所有模块，对每个调用optimizeModule()
- **F-053**: [optimizations/Optimization.py:370-401] `_optimizeModules(output_filename)`执行：startGraph→第一遍makeOptimizationPass→bytecode降级→循环直到unfinished_modules为空→endGraph
- **F-054**: [optimizations/Tags.py:12-40] `allowed_tags`元组包含15个标签：new_code, new_import, new_statements, new_expression, loop_analysis, var_usage, read_only_module_variable, trusted_module_variables, new_builtin_ref, new_builtin, new_raise, new_constant, changed_variable_usage等
- **F-055**: [optimizations/ValueTraces.py:52-273] `ValueTraceBase(object)`是所有值追踪的基类，__slots__包含owner、usage_count、name_usage_count、merge_usage_count
- **F-056**: [optimizations/ValueTraces.py] ValueTrace类层次：ValueTraceStartUninitialized、ValueTraceDeleted、ValueTraceStartInit、ValueTraceUnknown、ValueTraceEscaped、ValueTraceAssign、ValueTraceMerge、ValueTraceLoopComplete/Incomplete
- **F-057**: [optimizations/FunctionInlining.py:41-94] `convertFunctionCallToOutline(provider, function_body, values, call_source_ref)`创建ExpressionOutlineBody，克隆函数体，更新变量作用域
- **F-058**: [optimizations/BytecodeDemotion.py:37-84] `demoteCompiledModuleToBytecode(module)`将编译模块降级为字节码模块，替换已导入模块引用
- **F-059**: [optimizations/TraceCollections.py:1161] `TraceCollectionFunction(CollectionStartPointMixin, TraceCollectionBase)`用于函数体的抽象执行追踪
- **F-060**: [optimizations/TraceCollections.py:1294] `TraceCollectionModule(CollectionStartPointMixin, TraceCollectionBase)`用于模块级抽象执行追踪
- **F-061**: [optimizations/OptimizeBuiltinCalls.py:1538-1572] `computeBuiltinCall(builtin_name, call_node, trace_collection)`通过_dispatch_dict查找extractor函数进行内置调用优化

---

## 六、C代码生成（code_generation/）

- **F-062**: [code_generation/Emission.py:15-21] `SourceCodeCollector(list)`的`__call__(self, code)`方法append代码，别名`emit = __call__`
- **F-063**: [code_generation/Emission.py:24-46] 上下文管理器`withSubCollector(emit, context)`创建子emit收集器，处理局部变量声明作用域
- **F-064**: [code_generation/CodeHelpers.py:21] 模块级字典`expression_dispatch_dict = {}`；`statement_dispatch_dict = {}`
- **F-065**: [code_generation/CodeHelpers.py:37-58] `generateExpressionCode(to_name, expression, emit, context)`通过`expression_dispatch_dict[expression.kind]`分发代码生成
- **F-066**: [code_generation/CodeHelpers.py:169-185] `generateStatementCode(statement, emit, context)`通过`statement_dispatch_dict[statement.kind]`分发
- **F-067**: [code_generation/Contexts.py:334-525] `PythonContextBase`是代码生成上下文基类，包含allocateTempName、addHelperCode、pushCleanupScope等抽象方法
- **F-068**: [code_generation/Contexts.py:768] `PythonModuleContext(TempMixin, ..., PythonContextBase)`模块级代码生成上下文
- **F-069**: [code_generation/Contexts.py:957] `PythonFunctionContext(TempMixin, ..., PythonChildContextBase)`函数级代码生成上下文基类
- **F-070**: [code_generation/Contexts.py] 函数上下文子类：PythonFunctionDirectContext、PythonGeneratorObjectContext、PythonCoroutineObjectContext、PythonAsyncgenObjectContext、PythonFunctionCreatedContext、PythonFunctionOutlineContext
- **F-071**: [code_generation/CodeGeneration.py:383-528] `generateFunctionBodyCode(function_body, context)`通过_generated_functions字典缓存，根据函数体类型选择不同context
- **F-072**: [code_generation/CodeGeneration.py:531-593] `_generateModuleCode(module, data_filename)`创建PythonModuleContext，遍历used/crossUsed函数生成代码，调用getModuleCode返回模块C代码
- **F-073**: [code_generation/CodeGeneration.py:623-628] `generateHelpersCode()`调用getCallsCode()和getConstantsDefinitionCode()返回辅助代码元组
- **F-074**: [code_generation/VariableDeclarations.py:26-131] `VariableDeclaration`类封装C变量声明，__slots__包含c_type、code_name、init_value、heap_name
- **F-075**: [code_generation/VariableDeclarations.py:134-200] `VariableStorage`类管理堆/主/闭包/局部/顶层变量声明栈，提供withLocalStorage()上下文管理器

---

## 七、C编译后端（build/）

- **F-076**: [build/SconsInterface.py:501-607] `runScons(scons_options, env_values, scons_filename)`设置环境变量→构建scons命令→subprocess.call()执行→处理错误码27→检查缓存
- **F-077**: [build/SconsInterface.py:670-870] `getCommonSconsOptions()`返回OrderedDict，包含nuitka_src、python_version、debug_modes、lto_mode、target_arch、module_mode、standalone_mode、onefile_mode等键
- **F-078**: [build/SconsCompilerSettings.py:1047-1259] `createNuitkaSconsEnvironment()`初始化scons→解析参数→createEnvironmentAndCheckCompiler→检测编译器版本→enableCcache/enableClcache
- **F-079**: [build/SconsCompilerSettings.py:1262-1650] `setupCCompiler(env, ...)`配置C编译器标志：LTO、C11标准、优化级别(-O3等)、平台目标设置、栈大小(8MB/4MB)
- **F-080**: [build/SconsCompilerSettings.py:642-729] `_decideBlobResourceMode(env)`支持6种资源模式：c23_embed、linker、incbin、coff_obj、win_resource、mac_section、code
- **F-081**: [build/SconsUtils.py:213-484] `createEnvironment(...)`创建SCons Environment对象，支持MinGW/zig/MSVC模式，monkey-patch MSVC检测
- **F-082**: [build/SconsCaching.py:151-237] `enableCcache(...)`在非zig模式下设置ccache环境变量，查找或下载ccache（macOS从nuitka.net下载）
- **F-083**: [build/DataComposerInterface.py:33-43] `runDataComposer(source_dir)`执行DataComposer子进程生成常量blob文件`<source_dir>/blobs/__constant.bin`
- **F-084**: [build/static_src/MainProgram.c] C主程序入口，`#include "nuitka/prelude.h"`，定义`NUITKA_MAIN_MODULE_NAME "__main__"`宏
- **F-085**: [build/static_src/] 包含100+个C文件：HelpersCalling.c、HelpersDictionaries.c、HelpersLists.c、HelpersTuples.c、HelpersStrings.c、HelpersBytes.c、HelpersClasses.c、HelpersExceptions.c、HelpersFiles.c、HelpersImport.c、CompiledMethodType.c、CompiledGeneratorType.c等
- **F-086**: [build/SconsInterface.py:143-160] `provideStaticSourceFilesBackend(source_dir)`复制CompiledFunctionType.c和MainProgram.c到目标目录static_src/子目录

---

## 八、模块导入系统（importing/）

- **F-087**: [importing/Importing.py:1078-1135] `locateModule(module_name, parent_package, level, logger)`是模块定位核心公共API，返回(module_name, module_filename, module_kind, finding)四元组
- **F-088**: [importing/Importing.py:436-560] `findModule(module_name, parent_package, level, logger)`执行实际搜索：相对导入处理→fake模块检查→preloaded包路径→文件系统搜索
- **F-089**: [importing/Importing.py:289-332] `getModuleNameAndKindFromFilename(module_filename)`根据后缀返回(module_name, module_kind)：.py→"py"，.pyc→"pyc"，扩展模块后缀→"extension"
- **F-090**: [importing/ImportCache.py:19-20] 全局字典`imported_modules = {}`（键为(module_filename, full_name)）和`imported_by_name = {}`（键为full_name）
- **F-091**: [importing/ImportCache.py:23-37] `addImportedModule(imported_module)`添加到两个缓存字典，首次添加时调用onModuleDiscovered插件钩子
- **F-092**: [importing/Recursion.py:83-131] `recurseTo(module_name, module_filename, module_kind, ...)`先查缓存，未命中则调用onModuleRecursion钩子→buildModule→缓存
- **F-093**: [importing/Recursion.py:159-226] `decideRecursion(using_module_name, ...)`判断是否递归到某模块，考虑用户选项、PGO决策、插件钩子、标准库策略
- **F-094**: [importing/StandardLibrary.py:33-115] `getStandardLibraryPaths()`通过os.__file__位置推断标准库路径集合，处理virtualenv、Homebrew符号链接等
- **F-095**: [importing/PreloadedPackages.py:37-45] `detectPreLoadedPackagePaths()`遍历sys.modules中有__path__但无__file__的模块（.pth创建的命名空间包）

---

## 九、打包分发系统（freezer/）

- **F-096**: [freezer/IncludedEntryPoints.py:69-128] `IncludedEntryPoint`类__slots__包含kind、source_path、dest_path、module_name、executable、reason、tags
- **F-097**: [freezer/IncludedEntryPoints.py:207-267] 工厂函数：makeExtensionModuleEntryPoint(kind="extension")、makeDllEntryPoint(kind="dll")、makeExeEntryPoint(kind="exe")、makeMainExecutableEntryPoint(kind="executable")
- **F-098**: [freezer/IncludedDataFiles.py:129-198] `IncludedDataFile`类，kind为"data_file"或"data_blob"
- **F-099**: [freezer/Standalone.py:777] `detectUsedDLLs(standalone_entry_points, source_dir)`递归检测所有入口点的DLL依赖
- **F-100**: [freezer/Onefile.py:75-87] `packDistFolderToOnefile(dist_dir)`调用packDistFolderToOnefileBootstrap()执行打包
- **F-101**: [freezer/Onefile.py:90-141] `_runOnefileScons(...)`调用runScons()执行Onefile.scons构建引导二进制
- **F-102**: [freezer/Onefile.py:182-252] `runOnefileCompressor(...)`在当前进程或外部Python中调用attachOnefilePayload()将分发目录压缩附加到引导二进制
- **F-103**: [freezer/ImportDetection.py:29-197] `_detectImports(command)`通过子进程执行`python -s -S -v -c`并解析stderr输出检测模块导入（格式：`import <module> # <origin> <filename>`）
- **F-104**: [freezer/DllDependenciesCommon.py:25-44] `_msvc_redist_dll_names`集合包含12个MSVC可再发行DLL名称（concrt140.dll, msvcp140.dll, vcruntime140.dll等）

---

## 十、插件系统（plugins/）

- **F-105**: [plugins/Plugins.py:82] 模块级变量`active_plugins = OrderedDict()`，键为插件名，值为插件实例
- **F-106**: [plugins/Plugins.py:83-89] 7个按回调能力分类的插件列表：with_implicit_imports、with_decide_compilation、with_decide_annotations、with_decide_doc_strings、with_decide_assertions、with_function_body_parsing、with_class_body_parsing
- **F-107**: [plugins/Plugins.py:456] `Plugins(object)`类提供约40个@staticmethod/@classmethod作为插件系统对外API
- **F-108**: [plugins/PluginBase.py:455] `NuitkaPluginBase(getMetaClassBase("Plugin", require_slots=False))`，类属性plugin_name=None
- **F-109**: [plugins/PluginBase.py:491-1600] `NuitkaPluginBase`定义约60个可被子类覆盖的虚方法，包括onModuleSourceCode、getImplicitImports、onModuleEncounter、decideCompilation、getExtraDlls、considerDataFiles等
- **F-110**: [plugins/PluginBase.py:503] `isAlwaysEnabled()`默认返回False，返回True的插件自动激活且对用户不可见
- **F-111**: [plugins/YamlPluginBase.py:17] `NuitkaYamlPluginBase(NuitkaPluginBase)`，覆写onCompilationStartChecks()加载YAML配置
- **F-112**: [plugins/Hooks.py:11] 模块级变量Plugins=None，所有函数转发到Plugins对象的同名方法（约45个转发函数）
- **F-113**: [plugins/standard/] standard/目录下有34个标准插件文件，包含AntiBloatPlugin、DataFilesPlugin、NumpyPlugin、TorchPlugin、TkinterPlugin、PySidePyQtPlugin、GeventPlugin、TrioPlugin、ImplicitImports等

---

## 十一、命令行选项系统（options/）

- **F-114**: [options/Options.py:108] 模块级变量options=None, positional_args=None
- **F-115**: [options/Options.py:1323-1715] 定义80+个is*()/shall*()/get*()公共访问器函数：isVerbose()、shallExecuteImmediately()、shallMakeModule()、isStandaloneMode()、isOnefileMode()、isShowProgress()等
- **F-116**: [options/OptionParsing.py:92] 创建全局optparse解析器；[L2652] `parseOptions(logger)`作为命令行解析入口

---

## 十二、模块注册表（ModuleRegistry.py）

- **F-117**: [ModuleRegistry.py:23-36] 三个模块级集合：root_modules=OrderedSet()、active_modules=OrderedSet()、done_modules=set()
- **F-118**: [ModuleRegistry.py:135] `startTraversal()`将active_modules初始化为root_modules副本并重置done_modules
- **F-119**: [ModuleRegistry.py:170] `nextModule()`从active_modules弹出下一个待处理模块并加入done_modules
- **F-120**: [ModuleRegistry.py:188-236] 查询函数：getDoneModules()、hasDoneModule()、getModuleByName()、getModuleFromCodeName()

---

## 十三、终结处理（finalizations/）

- **F-121**: [finalizations/Finalization.py:17] `prepareCodeGeneration(module)`创建FinalizeMarkups访问者并调用Operations.visitTree()遍历AST
- **F-122**: [finalizations/FinalizeMarkups.py:25] `FinalizeMarkups(VisitorNoopMixin)`在_onEnterNode中标记return语句的generator return处理需求、函数创建/调用标记、跨模块函数引用标记等

---

## 十四、参数规范（specs/）

- **F-123**: [specs/ParameterSpecs.py:37] `ParameterSpec(object)`__slots__包含name、owner、normal_args、normal_variables、list_star_arg、dict_star_arg、kw_only_args、pos_only_args、default_count、type_shape
- **F-124**: [specs/BuiltinParameterSpecs.py:16] `BuiltinParameterSpec(ParameterSpec)`新增__slots__=("builtin",)，方法simulateCall()使用self.builtin(*args, **kwargs)模拟编译期调用
- **F-125**: [specs/HardImportSpecs.py:25-150] 定义约30个模块级BuiltinParameterSpec实例，覆盖pkg_resources、importlib.metadata、os.path等硬导入函数规范
