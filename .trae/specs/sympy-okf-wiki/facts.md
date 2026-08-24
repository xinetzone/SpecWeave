# SymPy 核心模块事实提取

> 从 `d:\spaces\SpecWeave\external\libs\python\sympy\sympy\sympy\` 源码中提取的客观事实。
> 所有事实均陈述代码中存在的类、方法签名、继承层次和属性。

---

## 模块：core/basic.py

**F-001**：`Basic` 类定义于 [core/basic.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L164)，继承自 `Printable`（来自 `._print_helpers`），是所有 SymPy 对象的基类，`__slots__` 包含 `_mhash`、`_args`、`_assumptions`。

**F-002**：`Basic.__new__(cls, *args)` 定义于 [core/basic.py:294](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L294)，通过 `object.__new__(cls)` 创建实例，设置 `_assumptions = cls.default_assumptions`、`_mhash = None`、`_args = args`。

**F-003**：`Basic` 类使用 `__init_subclass__` 钩子（[core/basic.py:220](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L220)），在每个子类定义时调用 `_prepare_class_assumptions(cls)` 初始化默认假设。

**F-004**：`Basic.args` 属性（[core/basic.py:913](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L913)）返回 `self._args`（一个 `tuple[Basic, ...]`），文档规定外部代码应始终使用 `.args` 而非 `._args`。

**F-005**：`Basic.func` 属性（[core/basic.py:887](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L887)）返回 `self.__class__`，对所有对象满足 `x == x.func(*x.args)`。

**F-006**：`Basic.subs(self, arg1, arg2=None, **kwargs)` 方法（[core/basic.py:971](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L971)）支持三种调用形式：两个参数 `subs(old, new)`、字典 `subs({old: new})`、可迭代对象 `subs([(old, new), ...])`，支持 `simultaneous` 关键字参数。

**F-007**：`Basic.xreplace(self, rule)` 方法（[core/basic.py:1304](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L1304)）接收字典类型的 `rule` 参数，在表达式树中精确匹配完整节点进行替换，不区自由变量和约束变量。

**F-008**：`Basic.doit(self, **hints)` 方法（[core/basic.py:2005](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L2005)）递归求值默认不求值的对象（如极限、积分、求和、乘积），支持 `deep` 关键字参数（默认 `True`）。

**F-009**：`Basic.rewrite(self, *args, deep=True, **hints)` 方法（[core/basic.py:2062](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L2062)）根据定义的规则重写表达式，接受 `pattern`（类型或类型的可迭代对象）和 `rule` 作为位置参数，通过调用 `_eval_rewrite()` 或 `_eval_rewrite_as_<rulename>()` 方法执行实际重写。

**F-010**：`Basic.simplify(self, **kwargs)` 方法（[core/basic.py:2031](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L2031)）委托给 `sympy.simplify.simplify.simplify` 函数执行化简。

**F-011**：`Basic` 定义了以下公开方法：`copy()`（[L302](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L302)）、`compare(other)`（[L372](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L372)）、`fromiter(args, **assumptions)`（[L431](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L431)，类方法）、`atoms(*types)`（[L607](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L607)）、`free_symbols`（[L684](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L684)，属性）、`has(*patterns)`（[L1392](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L1392)）、`replace(query, value, map=False, simultaneous=True, exact=None)`（[L1547](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L1547)）、`find(query, group=False)`（[L1804](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L1804)）、`match(pattern, old=False)`（[L1938](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L1938)）、`matches(expr, repl_dict=None, old=False)`（[L1892](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L1892)）、`count_ops(visual=False)`（[L2000](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L2000)）、`refine(assumption=True)`（[L2036](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L2036)）、`dummy_eq(other, symbol=None)`（[L556](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L556)）、`as_dummy()`（[L743](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L743)）、`canonical_variables`（[L790](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L790)，属性）、`sort_key(order=None)`（[L454](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L454)）、`class_key()`（[L449](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L449)，类方法）。

**F-012**：`Basic` 类上声明了一组 `is_*` 类属性，初始值均为 `False` 或 `None`，包括 `is_number`、`is_Atom`、`is_Symbol`、`is_symbol`、`is_Dummy`、`is_Wild`、`is_Function`、`is_Add`、`is_Mul`、`is_Pow`、`is_Number`、`is_Float`、`is_Rational`、`is_Integer`、`is_NumberSymbol`、`is_Derivative`、`is_Relational`、`is_Equality`、`is_Boolean`、`is_Matrix` 等（[core/basic.py:229-258](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L229-L258)）。

**F-013**：`Atom` 类定义于 [core/basic.py:2311](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L2311)，继承自 `Basic`，设置 `is_Atom = True`、`__slots__ = ()`，重写了 `matches()`、`xreplace()`、`doit()`（直接返回 `self`）、`class_key()`（返回 `(2, 0, cls.__name__)`）、`sort_key()`、`_eval_simplify()`（返回 `self`），其 `_sorted_args` 属性抛出 `AttributeError`。

**F-014**：`Basic` 类包含类变量 `_constructor_postprocessor_mapping = {}`（[core/basic.py:2193](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L2193)），以及类方法 `_exec_constructor_postprocessors(cls, obj)`（[L2196](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L2196)），用于构造后处理。

**F-015**：模块级函数 `as_Basic(expr)` 定义于 [core/basic.py:40](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L40)，使用严格的 `_sympify` 将参数转换为 `Basic` 实例，失败时抛出 `TypeError`。

**F-016**：模块级列表 `ordering_of_classes` 定义于 [core/basic.py:58](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/basic.py#L58)，定义了交换律参数的规范排序优先级：单例数字→数字→单例符号→符号→Pow→Mul→Add→函数值→定义的单例函数→未定义函数→Lambda→Order→关系运算。

---

## 模块：core/expr.py

**F-017**：`Expr` 类定义于 [core/expr.py:47](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L47)，继承自 `Basic` 和 `EvalfMixin`，是所有代数表达式的基类，装饰器为 `@sympify_method_args`，`__slots__ = ()`，`is_scalar = True`。

**F-018**：`Expr` 类定义了以下公开方法：`equals(other, failing_expression=False)`（[L767](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L767)）、`diff(*symbols, **assumptions)`（[L3627](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L3627)）、`integrate(*args, **kwargs)`（[L3778](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L3778)）、`limit(x, xlim, dir='+')`（[L3501](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L3501)）、`series(x=None, x0=0, n=6, dir="+", logx=None, cdir=0)`（[L2922](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L2922)）、`expand(deep=True, modulus=None, power_base=True, power_exp=True, mul=True, log=True, multinomial=True, basic=True, **hints)`（[L3673](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L3673)）、`factor(*gens, **args)`（[L3838](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L3838)）、`collect(syms, func=None, evaluate=True, exact=False, distribute_order_term=True)`（[L3793](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L3793)）。

**F-019**：`Expr` 类通过继承 `EvalfMixin` 获得 `evalf(n=15, subs=None, maxn=100, chop=False, strict=False, quad=None, verbose=False)` 方法和 `n` 属性（`n = evalf`）。

**F-020**：`Expr` 类定义了以下分解/结构方法：`as_base_exp()`（[L2070](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L2070)，返回 `(base, exp)` 元组）、`as_coeff_add(*deps)`（[L2109](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L2109)，返回 `(coeff, rest)` 元组）、`as_coeff_Mul(rational=False)`（[L3593](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L3593)，返回 `(coeff, rest)` 元组）、`as_powers_dict()`（[L1997](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L1997)）、`as_real_imag(deep=True, **hints)`（[L1968](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L1968)，返回 `(real, imag)` 元组）、`primitive()`（[L2145](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L2145)，返回 `(Rational_coeff, rest)` 元组）、`as_content_primitive(radical=False, clear=True)`（[L2171](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L2171)）、`args_cnc(cset=False, warn=True, split_1=True)`（[L1338](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L1338)）、`conjugate()`（[L1049](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L1049)）、`transpose()`（[L1086](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L1086)）。

**F-021**：`AtomicExpr` 类定义于 [core/expr.py:4031](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L4031)，继承自 `Atom` 和 `Expr`，`__slots__ = ()`，`is_number = False`，`is_Atom = True`，其 `_eval_derivative(s)` 方法在 `self == s` 时返回 `S.One`，否则返回 `S.Zero`。

**F-022**：`UnevaluatedExpr` 类定义于 [core/expr.py:4118](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L4118)，继承自 `Expr`，`__new__(cls, arg, **kwargs)` 将参数 sympify 后传入 `Expr.__new__`，其 `doit(**hints)` 方法在 `deep=True` 时返回 `self.args[0].doit(**hints)`。

**F-023**：`ExprBuilder` 类定义于 [core/expr.py:4176](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/expr.py#L4176)，`__init__(self, op, args=None, validator=None, check=True)` 接收可调用的 `op`、参数列表 `args` 和可选的 `validator`，提供 `build()`、`validate()` 等方法用于增量构建表达式。

---

## 模块：core/symbol.py

**F-024**：`Symbol` 类定义于 [core/symbol.py:226](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/symbol.py#L226)，继承自 `AtomicExpr` 和 `Boolean`，`__slots__` 包含 `name`、`_assumptions_orig`、`_assumptions0`，`is_Symbol = True`，`is_symbol = True`，`is_comparable = False`，其 `name` 属性类型为 `str`。

**F-025**：`Dummy` 类定义于 [core/symbol.py:475](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/symbol.py#L475)，继承自 `Symbol`，`__slots__` 包含 `dummy_index`，`is_Dummy = True`，使用类变量 `_count` 和 `_base_dummy_index` 生成唯一索引，同名 `Dummy` 实例互不相等，`_hashable_content()` 返回 `Symbol._hashable_content(self) + (self.dummy_index,)`。

**F-026**：`Wild` 类定义于 [core/symbol.py:545](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/symbol.py#L545)，继承自 `Symbol`，`is_Wild = True`，`__new__` 接受 `exclude`（不匹配的实例的可迭代对象）和 `properties`（返回布尔值的函数列表）参数，用于模式匹配。

**F-027**：模块级函数 `symbols(names, *, cls=Symbol, **args)` 定义于 [core/symbol.py:689](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/symbol.py#L689)，支持通过字符串（逗号或空格分隔）一次性创建多个符号，`seq=True` 时返回元组；`var(names, **args)` 函数定义于 [L902](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/symbol.py#L902)，将符号注入调用者的命名空间。

**F-028**：`Str` 类定义于 [core/symbol.py:31](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/symbol.py#L31)，继承自 `Atom`，用于表示字符串常量。

---

## 模块：core/numbers.py

**F-029**：`Number` 类定义于 [core/numbers.py:313](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L313)，继承自 `AtomicExpr`，`is_commutative = True`，`is_number = True`，`is_Number = True`，`kind = NumberKind`，`_prec = -1`，`__new__(cls, *obj)` 根据输入类型分发到 `Integer`、`Rational`、`Float` 或单例常量。

**F-030**：数字继承层次为：`Number → Float`（[L596](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L596)）、`Number → Rational → Integer`（[L1204](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L1204)、[L1792](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L1792)）。

**F-031**：单例数字常量类（均使用 `metaclass=Singleton`）：`Zero`（[L2803](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L2803)）、`One`（[L2871](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L2871)）、`NegativeOne`（[L2922](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L2922)）、`Half`（[L2986](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L2986)）、`Infinity`（[L3018](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3018)）、`NegativeInfinity`（[L3203](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3203)）、`NaN`（[L3365](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3365)）。

**F-032**：`ComplexInfinity` 类定义于 [core/numbers.py:3481](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3481)，继承自 `AtomicExpr`（非 `Number`），使用 `metaclass=Singleton`，通过模块级变量 `zoo = S.ComplexInfinity`（[L3558](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3558)）访问。

**F-033**：`NumberSymbol` 类定义于 [core/numbers.py:3561](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3561)，继承自 `AtomicExpr`，其子类（均为单例）包括：`Exp1`（[L3618](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3618)，常量 e）、`Pi`（[L3773](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3773)，常量 π）、`GoldenRatio`（[L3841](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3841)）、`TribonacciConstant`（[L3904](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3904)）、`EulerGamma`（[L3977](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3977)）、`Catalan`（[L4036](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L4036)）。

**F-034**：`ImaginaryUnit` 类定义于 [core/numbers.py:4099](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L4099)，继承自 `AtomicExpr`，使用 `metaclass=Singleton`。

**F-035**：模块级快捷常量：`oo = S.Infinity`（[L3200](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3200)）、`nan = S.NaN`（[L3474](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3474)）、`E = S.Exp1`（[L3770](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3770)）、`pi = S.Pi`（[L3838](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L3838)）、`I = S.ImaginaryUnit`（[L4183](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L4183)）。

**F-036**：`AlgebraicNumber` 类定义于 [core/numbers.py:2263](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L2263)，继承自 `Expr`（非 `Number`），表示代数数。`RealNumber` 是 `Float` 的别名（[core/numbers.py:1201](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/numbers.py#L1201)：`RealNumber = Float`）。模块级工具函数包括 `igcd`、`ilcm`、`seterr`、`comp`、`mod_inverse`（均从 core/numbers.py 导出），以及 `integer_nthroot`、`integer_log`、`num_digits`、`trailing`（从 core/intfunc.py 导出）和 `prod`（从 core/mul.py 导出）。

---

## 模块：core/add.py

**F-037**：`Add` 类定义于 [core/add.py:93](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/add.py#L93)，继承自 `Expr` 和 `AssocOp`，`is_Add = True`，类方法 `flatten(cls, seq)`（[L212](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/add.py#L212)）对参数序列执行扁平化和合并，返回 `(seq, [], None)` 或 `(seq, coeff, None)`。

**F-038**：`Add` 定义了 `as_coeff_add(*deps)`（[L441](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/add.py#L441)）和 `as_coeff_Add(rational=False, deps=None)`（[L463](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/add.py#L463)，返回 `(Number, Expr)` 元组）方法。

---

## 模块：core/mul.py

**F-039**：`Mul` 类定义于 [core/mul.py:95](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/mul.py#L95)，继承自 `Expr` 和 `AssocOp`，`is_Mul = True`，类方法 `flatten(cls, seq)`（[L210](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/mul.py#L210)）处理参数的扁平化、合并、提取系数。

**F-040**：`Mul` 定义了 `as_coeff_mul(*deps, rational=True, **kwargs)`（[L836](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/mul.py#L836)）和 `as_coeff_Mul(rational=False)`（[L854](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/mul.py#L854)，返回 `(Number, Expr)` 元组）方法，以及 `as_ordered_factors(order=None)`（[L2099](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/mul.py#L2099)）方法。模块级还定义了 `NC_Marker` 类（[L29](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/mul.py#L29)）。

---

## 模块：core/power.py

**F-041**：`Pow` 类定义于 [core/power.py:22](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/power.py#L22)，继承自 `Expr`，`is_Pow = True`，`__new__(cls, b, e, evaluate=None)` 接受底数 `b` 和指数 `e`，定义了 `as_base_exp()`（[L797](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/power.py#L797)）方法返回 `(self.base, self.exp)`。

---

## 模块：core/operations.py

**F-042**：`AssocOp` 类定义于 [core/operations.py:29](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/operations.py#L29)，继承自 `Basic`，是 `Add` 和 `Mul` 的抽象基类，`__slots__ = ('is_commutative',)`，`__new__(cls, *args, evaluate=None, _sympify=True)`（[L63](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/operations.py#L63)）支持 `evaluate` 参数控制是否求值，要求子类定义 `identity` 属性和 `flatten` 类方法。

**F-043**：`LatticeOp` 类定义于 [core/operations.py:487](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/operations.py#L487)，继承自 `AssocOp`，表示格运算（交/并），具有结合律、交换律和幂等律（`op(a,a)=a`），要求子类定义 `zero`（吸收元）和 `identity`（单位元）属性，使用 `_argset`（frozenset）存储参数。

**F-044**：`AssocOpDispatcher` 类定义于 [core/operations.py:583](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/operations.py#L583)，用于动态分派结合操作；`ShortCircuit` 异常类定义于 [L483](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/operations.py#L483)。

---

## 模块：core/sympify.py

**F-045**：`sympify(a, locals=None, convert_xor=True, strict=False, rational=False, evaluate=None)` 函数定义于 [core/sympify.py:124](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/sympify.py#L124)，将任意 Python 对象转换为 SymPy 类型：Python `int` → `Integer`、`float` → `Float`、字符串通过解析转换，失败时抛出 `SympifyError`。

**F-046**：模块级全局字典 `converter` 定义于 [core/sympify.py:41](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/sympify.py#L41)，类型为 `dict[type[Any], Callable[[Any], Basic]]`，注册自定义类型到 SymPy 类型的转换函数；`_sympy_converter` 字典（[L44](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/sympify.py#L44)）是内部转换器，`_external_converter` 是 `converter` 的别名。

**F-047**：`SympifyError` 类定义于 [core/sympify.py:27](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/sympify.py#L27)，继承自 `ValueError`；`CantSympify` 类定义于 [L49](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/sympify.py#L49)，作为标记类表示无法被 sympify 的类型。`_sympify(a)` 函数（[L514](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/sympify.py#L514)）是严格版本的内部 sympify。

---

## 模块：core/function.py

**F-048**：`FunctionClass` 类定义于 [core/function.py:156](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L156)，继承自 `type`（元类），是所有函数类的元类，`__init__(cls, *args, **kwargs)` 处理 `nargs` 参数规范化，`nargs` 属性（[L228](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L228)）返回允许的参数数量集合（`FiniteSet` 或 `S.Naturals0`）。

**F-049**：`Application` 类定义于 [core/function.py:282](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L282)，继承自 `Basic`，使用 `metaclass=FunctionClass`，是已应用函数的基类。

**F-050**：`Function` 类定义于 [core/function.py:383](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L383)，继承自 `Application` 和 `Expr`，`is_Function = True`，通过 `Function('name')` 创建未定义函数类，其 `eval` 方法应为 `@classmethod`。

**F-051**：`AppliedUndef` 类定义于 [core/function.py:831](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L831)，继承自 `Function`，表示未定义函数的应用实例（如 `f(x)` 其中 `f = Function('f')`）。

**F-052**：`UndefinedFunction` 类定义于 [core/function.py:887](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L887)，继承自 `FunctionClass`，是 `Function('f')` 返回的未定义函数类的实际类型。

**F-053**：`WildFunction` 类定义于 [core/function.py:971](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L971)，继承自 `Function` 和 `AtomicExpr`，用于模式匹配中的函数通配符。

**F-054**：`Derivative` 类定义于 [core/function.py:1050](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L1050)，继承自 `Expr`，表示未求值的导数。

**F-055**：`Lambda` 类定义于 [core/function.py:1953](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L1953)，继承自 `Expr`，`is_Function = True`，`__new__(cls, signature, expr)` 接受变量签名（单个符号或符号元组）和表达式体，构造 lambda 函数。

**F-056**：`Subs` 类定义于 [core/function.py:2150](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L2150)，继承自 `Expr`，表示表达式中未求值的替换，`__new__` 接受 `expr`、`x`（变量或变量元组）、`x0`（求值点）。

**F-057**：模块级公开函数：`diff(f, *symbols, **kwargs)`（[L2495](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L2495)）、`expand(e, deep=True, modulus=None, power_base=True, power_exp=True, mul=True, log=True, multinomial=True, basic=True, **hints)`（[L2565](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L2565)）、`expand_mul(expr, deep=True)`（[L2915](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L2915)）、`expand_multinomial(expr, deep=True)`（[L2933](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L2933)）、`expand_log(expr, deep=True, force=False, factor=False)`（[L2951](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L2951)）、`expand_func(expr, deep=True)`（[L2996](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L2996)）、`expand_trig(expr, deep=True)`（[L3014](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L3014)）、`expand_complex(expr, deep=True)`（[L3032](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L3032)）、`expand_power_base(expr, deep=True, force=False)`（[L3056](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L3056)）、`expand_power_exp(expr, deep=True)`（[L3141](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L3141)）、`count_ops(expr, visual=False)`（[L3168](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L3168)）、`nfloat(expr, n=15, exponent=False, dkeys=False)`（[L3384](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L3384)）、`arity(cls)`（[L125](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L125)）。异常类包括 `PoleError`（[L104](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L104)）、`ArgumentIndexError`（[L108](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L108)）、`BadSignatureError`（[L114](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L114)）、`BadArgumentsError`（[L119](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/function.py#L119)）。

---

## 模块：core/evalf.py

**F-058**：`EvalfMixin` 类定义于 [core/evalf.py:1564](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/evalf.py#L1564)，`__slots__ = ()`，定义了 `evalf(self, n=15, subs=None, maxn=100, chop=False, strict=False, quad=None, verbose=False)` 方法（[L1569](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/evalf.py#L1569)）用于数值求值，以及 `n = evalf`（[L1692](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/evalf.py#L1692)）作为别名，还有 `_eval_evalf(self, prec)` 钩子方法（[L1701](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/evalf.py#L1701)）。

**F-059**：模块级函数 `N(x, n=15, **options)` 定义于 [core/evalf.py:1737](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/evalf.py#L1737)，等价于 `sympify(x, rational=True).evalf(n, **options)`。

**F-060**：模块级函数 `evalf(x, prec, options)` 定义于 [core/evalf.py:1459](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/evalf.py#L1459)，是底层数值求值引擎，接受二进制精度 `prec`；`_create_evalf_table()` 函数（[L1399](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/evalf.py#L1399)）在模块导入时注册各类表达式的 evalf 处理函数。`PrecisionExhausted` 异常类定义于 [L64](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/evalf.py#L64)，继承自 `ArithmeticError`。

---

## 模块：core/relational.py

**F-061**：`Relational` 类定义于 [core/relational.py:74](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L74)，继承自 `Boolean` 和 `EvalfMixin`，`is_Relational = True`，`__new__(cls, lhs, rhs, rop=None, **assumptions)` 通过 `rop` 参数（`'=='`、`'!='`、`'>='`、`'<='`、`'>'`、`'<'`）分派到具体子类。

**F-062**：`Relational` 的子类层次：`Equality`（[L558](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L558)，别名 `Eq`，[L758](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L758)）、`Unequality`（[L761](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L761)，别名 `Ne`，[L841](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L841)）。不等式类通过中间类 `_Inequality`（[L844](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L844)）、`_Greater`（[L904](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L904)）、`_Less`（[L922](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L922)）派生：`GreaterThan`（[L940](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L940)，别名 `Ge`，[L1178](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L1178)）、`LessThan`（[L1181](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L1181)，别名 `Le`，[L1195](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L1195)）、`StrictGreaterThan`（[L1198](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L1198)，别名 `Gt`，[L1213](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L1213)）、`StrictLessThan`（[L1216](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L1216)，别名 `Lt`，[L1230](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L1230)）。`Rel` 是 `Relational` 的别名（[L555](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/relational.py#L555)）。

---

## 模块：core/traversal.py

**F-063**：`preorder_traversal` 类定义于 [core/traversal.py:68](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/traversal.py#L68)，是一个迭代器类，对表达式树执行前序遍历，支持 `keys` 参数自定义子节点顺序，提供 `skip()` 方法跳过当前节点的子树。

**F-064**：模块级函数：`iterargs(expr)`（[L12](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/traversal.py#L12)，迭代表达式的所有参数）、`iterfreeargs(expr, _first=True)`（[L37](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/traversal.py#L37)，迭代自由参数）、`use(expr, func, level=0, args=(), kwargs={})`（[L167](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/traversal.py#L167)，在指定层级应用函数）、`walk(e, *target)`（[L199](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/traversal.py#L199)）、`bottom_up(rv, F, atoms=False, nonbasic=False)`（[L226](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/traversal.py#L226)，自底向上应用函数）、`postorder_traversal(node, keys=None)`（[L250](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/traversal.py#L250)，后序遍历生成器）。

---

## 模块：core/singleton.py

**F-065**：`SingletonRegistry` 类定义于 [core/singleton.py:42](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/singleton.py#L42)，继承自 `Registry`，全局实例 `S = SingletonRegistry()`（[L197](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/singleton.py#L197)）。`S` 既是单例对象的注册表（如 `S.Zero`、`S.One`、`S.Half`、`S.Infinity`、`S.NaN`、`S.ComplexInfinity`、`S.Exp1`、`S.Pi`、`S.ImaginaryUnit`、`S.Catalan`、`S.EulerGamma`、`S.GoldenRatio` 等），也是 `sympify` 的快捷方式（`S(1)` 等价于 `sympify(1)`）。

---

## 模块：core/__init__.py

**F-066**：[core/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/core/__init__.py) 导出的核心公开 API 包括：`sympify`、`SympifyError`、`cacheit`、`Basic`、`Atom`、`S`、`Expr`、`AtomicExpr`、`UnevaluatedExpr`、`Symbol`、`Wild`、`Dummy`、`symbols`、`var`、`Number`、`Float`、`Rational`、`Integer`、`NumberSymbol`、`RealNumber`、`igcd`、`ilcm`、`seterr`、`E`、`I`、`nan`、`oo`、`pi`、`zoo`、`AlgebraicNumber`、`Pow`、`Mul`、`prod`、`Add`、`Mod`、关系类（`Rel`/`Eq`/`Ne`/`Lt`/`Le`/`Gt`/`Ge` 及其全称类名）、`Lambda`、`WildFunction`、`Derivative`、`diff`、`FunctionClass`、`Function`、`Subs`、`expand` 及其变体、`N`、`PrecisionExhausted`、`Tuple`、`Dict`、`gcd_terms`、`factor_terms`、`evaluate`、数学常量（`Catalan`/`EulerGamma`/`GoldenRatio`/`TribonacciConstant`）、Kind 类（`UndefinedKind`/`NumberKind`/`BooleanKind`）、遍历函数（`preorder_traversal`/`bottom_up`/`use`/`postorder_traversal`）、排序工具（`default_sort_key`/`ordered`）。

---

## 模块：abc.py

**F-067**：[abc.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/abc.py) 模块通过 `symbols()` 函数预定义了拉丁小写字母 `a`-`z`、大写字母 `A`-`Z`，以及希腊字母 `alpha`、`beta`、`gamma`、`delta`、`epsilon`、`zeta`、`eta`、`theta`、`iota`、`kappa`、`lamda`（注意：使用 `lamda` 而非 Python 关键字 `lambda`）、`mu`、`nu`、`xi`、`omicron`、`pi`、`rho`、`sigma`、`tau`、`upsilon`、`phi`、`chi`、`psi`、`omega`，均可通过 `from sympy.abc import x, y` 直接导入。

**F-068**：`abc.py` 定义了三个冲突诊断字典：`_clash1`（与 SymPy 命名空间冲突的单字母变量名）、`_clash2`（多字母冲突符号名，如 `gamma`、`pi`、`zeta`）、`_clash`（两者的并集），这些字典将冲突名映射到 `sympy.parsing.sympy_parser.null`，可在 `sympify` 时作为 `locals` 参数传入以获取 Symbol 而非 SymPy 对象。

---

## 模块：顶层 __init__.py (sympy/__init__.py)

**F-069**：[sympy/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/__init__.py) 要求 Python ≥ 3.9（[L18](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/__init__.py#L18)），依赖 mpmath（[L24](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/__init__.py#L24)），从 `sympy.release` 导入 `__version__`，定义 `SYMPY_DEBUG` 环境变量控制（[L53](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/__init__.py#L53)）。

**F-070**：顶层 `__init__.py` 从 `.core` 导入所有核心符号（与 core/__init__.py 的导出基本一致），并从子模块导入大量符号：`.logic`（布尔代数）、`.assumptions`（假设系统）、`.polys`（多项式系统）、`.series`（级数）、`.functions`（数学函数）、`.ntheory`（数论）、`.concrete`（求和/乘积）、`.discrete`（离散变换）、`.simplify`（化简）、`.sets`（集合）、`.solvers`（求解器）、`.matrices`（矩阵）、`.geometry`（几何）、`.utilities`（含 `lambdify`）、`.integrals`（积分）、`.tensor`（张量）、`.parsing`（含 `parse_expr`）、`.calculus`（微积分工具）、`.algebras`（含 `Quaternion`）、`.printing`（打印/输出）、`.plotting`（绘图）、`.interactive`（交互）。

**F-071**：顶层 `__init__.py` 定义了 `test` 和 `doctest` 为延迟加载函数（[L253](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/__init__.py#L253)），在导入时调用 `evalf._create_evalf_table()`（[L265](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/__init__.py#L265)）初始化数值求值表。

---

## 核心类继承层次（汇总）

**F-072**：核心类继承链为：`Printable → Basic → Expr → Add/Mul/Pow`（其中 `Add` 和 `Mul` 还继承 `AssocOp`，`AssocOp` 继承 `Basic`）。`Expr` 还继承自 `EvalfMixin`。

**F-073**：原子类型继承链为：`Basic → Atom → AtomicExpr → Symbol/Dummy/Wild/Number/NumberSymbol/ImaginaryUnit`；其中 `Symbol` 还继承 `Boolean`，`Dummy` 和 `Wild` 继承自 `Symbol`，`Number` 下有 `Float`、`Rational→Integer`、单例常量，`NumberSymbol` 下有 `Exp1`/`Pi`/`GoldenRatio`/`EulerGamma`/`Catalan`/`TribonacciConstant` 等单例。

**F-074**：函数类继承链为：`Basic → Application(metaclass=FunctionClass) → Function → AppliedUndef/DefinedFunction`；`FunctionClass` 继承自 `type`，`WildFunction` 继承自 `Function` 和 `AtomicExpr`，`Derivative`/`Lambda`/`Subs` 直接继承自 `Expr`。

**F-075**：关系类继承链为：`Boolean → Relational(also EvalfMixin) → Equality/Unequality`；不等式类通过 `_Inequality → _Greater → GreaterThan/StrictGreaterThan` 和 `_Inequality → _Less → LessThan/StrictLessThan` 层次派生。`Relational` 同时继承 `EvalfMixin`。

---

## 模块：assumptions/

**F-076**：[assumptions/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/__init__.py) 导出的公开 API 包括：`AppliedPredicate`、`Predicate`、`AssumptionsContext`、`assuming`、`global_assumptions`（来自 `.assume`）、`Q`、`ask`（来自 `.ask`）、`refine`（来自 `.refine`）、`BinaryRelation`、`AppliedBinaryRelation`（来自 `.relation`）。

**F-077**：`ask(proposition, assumptions=True, context=global_assumptions)` 函数定义于 [assumptions/ask.py:406](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/ask.py#L406)，在给定假设下评估命题的布尔值，能确定则返回 `True`/`False`，不能确定返回 `None`。

**F-078**：`Q` 对象是 `AssumptionKeys` 类（[assumptions/ask.py:20](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/ask.py#L20)）的单例实例，通过 `@memoize_property` 装饰的属性提供谓词键，包括 `hermitian`、`antihermitian`、`real`、`extended_real`、`imaginary`、`complex`、`algebraic`、`transcendental`、`integer`、`noninteger` 等。

**F-079**：`refine(expr, assumptions=True)` 函数定义于 [assumptions/refine.py:21](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/refine.py#L21)，使用假设化简表达式，接受 `Expr` 或 `Basic` 类型的 `expr` 和布尔表达式 `assumptions`，返回同类型的化简结果。

**F-080**：`CNF` 类定义于 [assumptions/cnf.py:271](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/cnf.py#L271)，表示布尔表达式的合取范式，由子句集合组成，每个子句存储为 `Literal` 对象的 `frozenset`；`EncodedCNF` 类定义于 [L383](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/cnf.py#L383)，用于 CNF 表达式的编码表示，构造函数接受 `data` 和 `encoding` 参数。

**F-081**：`Literal` 类定义于 [assumptions/cnf.py:16](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/cnf.py#L16)，是 CNF 对象的最小元素，`__new__(cls, lit, is_Not=False)` 接受布尔表达式 `lit` 和否定标志 `is_Not`，提供 `arg` 属性、`rcall(expr)` 方法等。

**F-082**：`satask(proposition, assumptions=True, use_known_facts=True, iterations=oo)` 函数定义于 [assumptions/satask.py:18](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/assumptions/satask.py#L18)，使用 SAT 算法评估命题在假设下的布尔值，内部使用 `satisfiable`（来自 `sympy.logic.inference`）和 `CNF`/`EncodedCNF`。

---

## 模块：calculus/

**F-083**：[calculus/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/calculus/__init__.py) 导出：`euler_equations`（来自 `.euler`）；`singularities`、`is_increasing`、`is_strictly_increasing`、`is_decreasing`、`is_strictly_decreasing`、`is_monotonic`（来自 `.singularities`）；`finite_diff_weights`、`apply_finite_diff`、`differentiate_finite`（来自 `.finite_diff`）；`periodicity`、`not_empty_in`、`is_convex`、`stationary_points`、`minimum`、`maximum`（来自 `.util`）；`AccumBounds`（来自 `.accumulationbounds`）。

**F-084**：`finite_diff_weights(order, x_list, x0=S.One)` 函数定义于 [calculus/finite_diff.py:30](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/calculus/finite_diff.py#L30)，使用递归公式计算一维网格上 0 到 `order` 阶导数的有限差分权重。

**F-085**：`singularities(expression, symbol, domain=None)` 函数定义于 [calculus/singularities.py:41](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/calculus/singularities.py#L41)，返回给定函数在指定域上的奇点集合（返回类型为 `set[Symbol]`）。

**F-086**：`euler_equations(L, funcs=(), vars=())` 函数定义于 [calculus/euler.py:15](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/calculus/euler.py#L15)，对给定拉格朗日量 `L` 求解欧拉-拉格朗日方程，返回方程列表。

**F-087**：`AccumulationBounds` 类（别名 `AccumBounds`）定义于 [calculus/accumulationbounds.py:15](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/calculus/accumulationbounds.py#L15)，继承自 `Expr`，表示累积极限界。`calculus/util.py` 还定义了 `continuous_domain(f, symbol, domain)`（[L31](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/calculus/util.py#L31)）、`periodicity(f, symbol, check=False)`（[L401](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/calculus/util.py#L401)）、`is_convex(f, *syms, domain=S.Reals)`（[L680](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/calculus/util.py#L680)）、`stationary_points(f, symbol, domain=S.Reals)`（[L753](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/calculus/util.py#L753)）、`maximum(f, symbol, domain=S.Reals)`（[L805](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/calculus/util.py#L805)）、`minimum(f, symbol, domain=S.Reals)`（[L852](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/calculus/util.py#L852)）、`not_empty_in(finset_intersection, *syms)`（[L289](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/calculus/util.py#L289)）。

---

## 模块：functions/

**F-088**：[functions/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/functions/__init__.py) 包含三个子目录：`elementary/`（初等函数）、`special/`（特殊函数）、`combinatorial/`（组合函数）。初等函数子目录包含 `trigonometric.py`、`exponential.py`、`hyperbolic.py`、`complexes.py`、`integers.py`、`miscellaneous.py`、`piecewise.py`。

**F-089**：三角函数类从 `functions.elementary.trigonometric` 导出，包括 `sin`、`cos`、`tan`、`sec`、`csc`、`cot`、`sinc`、`asin`、`acos`、`atan`、`asec`、`acsc`、`acot`、`atan2`；指数/对数函数从 `functions.elementary.exponential` 导出，包括 `exp_polar`、`exp`、`log`（别名 `ln`）、`LambertW`；双曲函数从 `functions.elementary.hyperbolic` 导出，包括 `sinh`、`cosh`、`tanh`、`coth`、`sech`、`csch`、`asinh`、`acosh`、`atanh`、`acoth`、`asech`、`acsch`。

**F-090**：复数相关函数从 `functions.elementary.complexes` 导出：`re`、`im`、`sign`、`Abs`、`conjugate`、`arg`、`polar_lift`、`periodic_argument`、`unbranched_argument`、`principal_branch`、`transpose`、`adjoint`、`polarify`、`unpolarify`；整数相关函数从 `functions.elementary.integers` 导出：`floor`、`ceiling`、`frac`；杂项初等函数从 `functions.elementary.miscellaneous` 导出：`sqrt`、`root`、`Min`、`Max`、`Id`、`real_root`、`cbrt`、`Rem`。

**F-091**：`Piecewise` 类和相关函数从 `functions.elementary.piecewise` 导出，包括 `Piecewise`、`piecewise_fold`、`piecewise_exclusive`。

**F-092**：特殊函数子目录 `special/` 包含：误差函数（`erf`、`erfc`、`erfi`、`erf2`、`erfinv`、`erfcinv`、`erf2inv`、`Ei`、`expint`、`E1`、`li`、`Li`、`Si`、`Ci`、`Shi`、`Chi`、`fresnels`、`fresnelc`、`owens_t`）；Gamma 函数（`gamma`、`lowergamma`、`uppergamma`、`polygamma`、`loggamma`、`digamma`、`trigamma`、`multigamma`）；Zeta 函数（`dirichlet_eta`、`zeta`、`lerchphi`、`polylog`、`stieltjes`、`riemann_xi`）；Bessel 函数（`besselj`、`bessely`、`besseli`、`besselk`、`hankel1`、`hankel2`、`jn`、`yn`、`jn_zeros`、`hn1`、`hn2`、`airyai`、`airybi`、`airyaiprime`、`airybiprime`、`marcumq`）；超几何函数（`hyper`、`meijerg`、`appellf1`）；正交多项式（`legendre`、`assoc_legendre`、`hermite`、`hermite_prob`、`chebyshevt`、`chebyshevu`、`laguerre`、`assoc_laguerre`、`gegenbauer`、`jacobi` 等）。

**F-093**：特殊函数还包括张量函数（`Eijk`、`LeviCivita`、`KroneckerDelta`）、奇异函数（`SingularityFunction`）、Delta 函数（`DiracDelta`、`Heaviside`）、B 样条（`bspline_basis`、`bspline_basis_set`、`interpolating_spline`）、球谐函数（`Ynm`、`Ynm_c`、`Znm`）、椭圆积分（`elliptic_k`、`elliptic_f`、`elliptic_e`、`elliptic_pi`）、Beta 函数（`beta`、`betainc`、`betainc_regularized`）、Mathieu 函数（`mathieus`、`mathieuc`、`mathieusprime`、`mathieucprime`）。

**F-094**：组合函数子目录 `combinatorial/` 包含阶乘类（`factorial`、`factorial2`、`rf`/`RisingFactorial`、`ff`/`FallingFactorial`、`binomial`、`subfactorial`）和数论组合函数（`carmichael`、`fibonacci`、`lucas`、`tribonacci`、`harmonic`、`bernoulli`、`bell`、`euler`、`catalan`、`genocchi`、`andre`、`partition`、`divisor_sigma`、`mobius`、`totient`、`primepi`、`motzkin` 等）。

---

## 模块：integrals/

**F-095**：[integrals/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/integrals/__init__.py) 导出 `integrate`、`Integral`、`line_integrate`（来自 `.integrals`）；多种积分变换（来自 `.transforms`）：Mellin 变换（`mellin_transform`、`inverse_mellin_transform`、`MellinTransform`、`InverseMellinTransform`）、Laplace 变换（`laplace_transform`、`inverse_laplace_transform`、`LaplaceTransform`、`InverseLaplaceTransform`、`laplace_correspondence`、`laplace_initial_conds`）、Fourier 变换（`fourier_transform`、`inverse_fourier_transform`、`FourierTransform`、`InverseFourierTransform`）、Sine 变换、Cosine 变换、Hankel 变换各正逆对；以及 `singularityintegrate`（来自 `.singularityfunctions`）。

**F-096**：`Integral` 类定义于 [integrals/integrals.py:41](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/integrals/integrals.py#L41)，继承自 `AddWithLimits`，`__slots__ = ()`，表示未求值的积分；`integrate(function, *symbols, meijerg=None, conds='piecewise', risch=None, heurisch=None, manual=None, **kwargs)` 函数定义于 [L1412](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/integrals/integrals.py#L1412)，计算定积分或不定积分。

**F-097**：`heurisch(f, x, rewrite=False, hints=None, mappings=None, retries=3, degree_offset=0, ...)` 函数定义于 [integrals/heurisch.py:296](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/integrals/heurisch.py#L296)，实现启发式 Risch 积分算法。

**F-098**：`risch_integrate(f, x, extension=None, handle_first='log', separate_integral=False, rewrite_complex=None, conds='piecewise')` 函数定义于 [integrals/risch.py:1807](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/integrals/risch.py#L1807)，实现 Risch 算法积分。

**F-099**：Meijer G 积分函数定义于 [integrals/meijerint.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/integrals/meijerint.py)，包括 `meijerint_indefinite(f, x)`（[L1653](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/integrals/meijerint.py#L1653)，不定积分）、`meijerint_definite(f, x, a, b)`（[L1781](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/integrals/meijerint.py#L1781)，定积分）、`meijerint_inversion(f, x, t)`（[L2081](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/integrals/meijerint.py#L2081)，逆 Laplace 变换）。

**F-100**：`IntegralTransform` 基类定义于 [integrals/transforms.py:61](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/integrals/transforms.py#L61)，继承自 `Function`，是所有积分变换的基类；`IntegralTransformError` 异常类定义于 [L41](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/integrals/transforms.py#L41)，继承自 `NotImplementedError`。`manualintegrate.py` 文件存在，定义了 `IntegralInfo` NamedTuple（[L1092](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/integrals/manualintegrate.py#L1092)，包含 `integrand: Expr` 和 `symbol: Symbol` 字段）。

---

## 模块：simplify/

**F-101**：[simplify/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/simplify/__init__.py) 导出：`simplify`、`hypersimp`、`hypersimilar`、`logcombine`、`separatevars`、`posify`、`besselsimp`、`kroneckersimp`、`signsimp`、`nsimplify`（来自 `.simplify`）；`FU`、`fu`（来自 `.fu`）；`sqrtdenest`（来自 `.sqrtdenest`）；`cse`（来自 `.cse_main`）；`epath`、`EPath`（来自 `.epathtools`）；`hyperexpand`（来自 `.hyperexpand`）；`collect`、`rcollect`、`radsimp`、`collect_const`、`fraction`、`numer`、`denom`（来自 `.radsimp`）；`trigsimp`、`exptrigsimp`（来自 `.trigsimp`）；`powsimp`、`powdenest`（来自 `.powsimp`）；`combsimp`（来自 `.combsimp`）；`gammasimp`（来自 `.gammasimp`）；`ratsimp`、`ratsimpmodprime`（来自 `.ratsimp`）。

**F-102**：`simplify(expr, ratio=1.7, measure=count_ops, rational=False, inverse=False, doit=True, **kwargs)` 函数定义于 [simplify/simplify.py:443](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/simplify/simplify.py#L443)，支持 `Expr`、`Boolean`、`Set`、`Basic` 类型重载，执行通用表达式化简。

**F-103**：`trigsimp(expr, inverse=False, **opts)` 函数定义于 [simplify/trigsimp.py:464](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/simplify/trigsimp.py#L464)，使用三角恒等式化简表达式；`exptrigsimp` 为指数-三角互化简函数。

**F-104**：`powsimp(expr, deep=False, combine='all', force=False, measure=count_ops)` 函数定义于 [simplify/powsimp.py:19](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/simplify/powsimp.py#L19)，通过合并相似底数和指数来化简表达式；同模块还导出 `powdenest`。

**F-105**：`radsimp(expr, symbolic=True, max_terms=4)` 函数定义于 [simplify/radsimp.py:767](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/simplify/radsimp.py#L767)，通过移除分母中的平方根进行有理化；同模块还导出 `collect`、`rcollect`、`collect_const`、`fraction`、`numer`、`denom`。

**F-106**：`fu(rv, measure=lambda x: (L(x), x.count_ops()))` 函数定义于 [simplify/fu.py:1579](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/simplify/fu.py#L1579)，使用 Fu 等人的算法通过变换规则化简三角表达式；`FU` 对象提供 Fu 算法的具体变换规则集合。`combsimp(expr)` 函数定义于 [simplify/combsimp.py:13](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/simplify/combsimp.py#L13)，化简组合表达式。`ratsimp(expr)` 函数定义于 [simplify/ratsimp.py:12](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/simplify/ratsimp.py#L12)，将表达式通分、约分化简。`cse` 函数（来自 `cse_main.py`）执行公共子表达式消除。

---

## 模块：series/

**F-107**：[series/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/series/__init__.py) 导出：`Order`（别名 `O`）、`limit`、`Limit`（来自 `.limits`）；`gruntz`（来自 `.gruntz`）；`series`（来自 `.series`）；`approximants`、`pade_approximant`（来自 `.approximants`）；`residue`（来自 `.residues`）；`SeqPer`、`SeqFormula`、`sequence`、`SeqAdd`、`SeqMul`（来自 `.sequences`）；`fourier_series`（来自 `.fourier`）；`fps`（来自 `.formal`）；`difference_delta`、`limit_seq`（来自 `.limitseq`）；以及 `EmptySequence = S.EmptySequence`。

**F-108**：`Order` 类定义于 [series/order.py:12](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/series/order.py#L12)，继承自 `Expr`，表示函数的量级行为（大 O 记号）。

**F-109**：`limit(e, z, z0, dir="+")` 函数定义于 [series/limits.py:16](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/series/limits.py#L16)，计算表达式 `e(z)` 在点 `z0` 处的极限，`dir` 参数指定方向（`"+"` 或 `"-"`）；`Limit` 类定义于 [L130](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/series/limits.py#L130)，继承自 `Expr`，表示未求值的极限。

**F-110**：`series(expr, x=None, x0=0, n=6, dir="+")` 函数定义于 [series/series.py:5](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/series/series.py#L5)，计算表达式在 `x = x0` 处的级数展开，`n` 指定展开阶数。

---

## 模块：solvers/

**F-111**：[solvers/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/solvers/__init__.py) 导出：`solve`、`solve_linear_system`、`solve_linear_system_LU`、`solve_undetermined_coeffs`、`nsolve`、`solve_linear`、`checksol`、`det_quick`、`inv_quick`（来自 `.solvers`）；`diophantine`（来自 `.diophantine.diophantine`）；`rsolve`、`rsolve_poly`、`rsolve_ratio`、`rsolve_hyper`（来自 `.recurr`）；`checkodesol`、`classify_ode`、`dsolve`、`homogeneous_order`（来自 `.ode`）；`solve_poly_system`、`solve_triangulated`、`factor_system`（来自 `.polysys`）；`pde_separate`、`pde_separate_add`、`pde_separate_mul`、`pdsolve`、`classify_pde`、`checkpdesol`（来自 `.pde`）；`ode_order`（来自 `.deutils`）；不等式求解函数（来自 `.inequalities`）：`reduce_inequalities`、`reduce_abs_inequality`、`reduce_abs_inequalities`、`solve_poly_inequality`、`solve_rational_inequalities`、`solve_univariate_inequality`；`decompogen`（来自 `.decompogen`）；`solveset`、`linsolve`、`linear_eq_to_matrix`、`nonlinsolve`、`substitution`（来自 `.solveset`）；`lpmin`、`lpmax`、`linprog`（来自 `.simplex`）。

**F-112**：`solveset(f, symbol=None, domain=S.Complexes)` 函数定义于 [solvers/solveset.py:2338](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/solvers/solveset.py#L2338)，以集合形式求解方程或不等式；`linsolve(system, *symbols)` 定义于 [L2897](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/solvers/solveset.py#L2897)，求解 N 个线性方程 M 个变量的方程组；`nonlinsolve(system, *symbols)` 定义于 [L3910](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/solvers/solveset.py#L3910)，求解非线性方程组。

---

## 模块：matrices/

**F-113**：[matrices/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/matrices/__init__.py) 导出异常类 `ShapeError`、`NonSquareMatrixError`（来自 `.exceptions`）和 `MatrixKind`（来自 `.kind`）。`Matrix` 是 `MutableDenseMatrix` 的别名（`Matrix = MutableMatrix = MutableDenseMatrix`），`SparseMatrix` 是 `MutableSparseMatrix` 的别名，`ImmutableMatrix` 是 `ImmutableDenseMatrix` 的别名。

**F-114**：`MatrixBase` 类定义于 [matrices/matrixbase.py:127](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/matrices/matrixbase.py#L127)，继承自 `Printable`，是所有矩阵操作的基类，包含算术、变形、特殊矩阵（`zeros`、`eye`）等通用操作。`DeferredVector` 类定义于 [L5735](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/matrices/matrixbase.py#L5735)，继承自 `Symbol` 和 `NotIterable`，表示延迟求值的向量（用于 lambdify）。

**F-115**：`MutableDenseMatrix` 类定义于 [matrices/dense.py:123](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/matrices/dense.py#L123)，继承自 `DenseMatrix` 和 `MutableRepMatrix`，其 `simplify` 方法（[L128](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/matrices/dense.py#L128)）执行原地化简。`dense.py` 还导出矩阵构造函数：`eye`、`zeros`、`ones`、`diag`、`randMatrix`、`GramSchmidt`、`casoratian`、`wronskian`、`hessian`、`jordan_cell`、`rot_axis1/2/3`、`rot_ccw_axis1/2/3`、`rot_givens`、`symarray`、`matrix_multiply_elementwise`、`list2numpy`、`matrix2numpy`。

**F-116**：`MutableSparseMatrix` 类定义于 [matrices/sparse.py:462](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/matrices/sparse.py#L462)，继承自 `SparseRepMatrix` 和 `MutableRepMatrix`；`banded` 函数（来自 `.sparsetools`）创建带状矩阵。不可变矩阵类包括 `ImmutableDenseMatrix` 和 `ImmutableSparseMatrix`（来自 `.immutable`）。

**F-117**：`MatrixBase` 定义了 `eigenvals(error_when_incomplete=True, **flags)` 方法（[matrices/matrixbase.py:3671](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/matrices/matrixbase.py#L3671)，返回 `dict[Expr, int]`）和 `eigenvects(error_when_incomplete=True, iszerofunc=_iszero, **flags)` 方法（[L3676](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/matrices/matrixbase.py#L3676)，返回 `list[tuple[Expr, int, list[Self]]]`）。还定义了 `rref`、`inv(method=None, ...)`、`LUdecomposition`、`QRdecomposition`、`cholesky`、`diagonalize`、`jordan_form` 等矩阵分解方法。`_det(M, method="bareiss", iszerofunc=None)` 函数定义于 [matrices/determinant.py:596](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/matrices/determinant.py#L596)。

**F-118**：`matrices/expressions/` 子目录包含符号矩阵表达式模块，导出 `MatrixExpr`（基类，定义于 [matexpr.py:40](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/matrices/expressions/matexpr.py#L40)，继承自 `Expr`）、`MatrixSymbol`（[matexpr.py:669](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/matrices/expressions/matexpr.py#L669)，继承 `MatrixExpr`，表示符号矩阵）、`MatAdd`、`MatMul`、`MatPow`、`Inverse`、`Transpose`、`Adjoint`、`Trace`/`trace`、`Determinant`/`det`、`Identity`、`ZeroMatrix`、`OneMatrix`、`BlockMatrix`、`BlockDiagMatrix`、`MatrixSlice`、`FunctionMatrix`、`HadamardProduct`、`HadamardPower`、`KroneckerProduct`、`PermutationMatrix`、`DiagMatrix`/`DiagonalMatrix`、`DiagonalOf`、`DotProduct`、`MatrixPermute`、`MatrixSet`、`Permanent`/`per` 等。

---

## 模块：polys/

**F-119**：[polys/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/polys/__init__.py) 导出多项式核心类和函数：`Poly`、`PurePoly`、`poly_from_expr`、`parallel_poly_from_expr`（来自 `.polytools`/`.constructor`）；多项式运算：`degree`、`total_degree`、`LC`/`LM`/`LT`、`pdiv`/`prem`/`pquo`/`pexquo`、`div`/`rem`/`quo`/`exquo`、`half_gcdex`/`gcdex`、`gcd`/`gcd_list`、`lcm`/`lcm_list`、`factor`/`factor_list`、`sqf`/`sqf_list`/`sqf_part`/`sqf_norm`、`resultant`、`discriminant`、`cofactors`、`sturm`、`gff`/`gff_list`、`groebner`、`GroebnerBasis`、`cancel`、`reduced`、`intervals`、`refine_root`、`count_roots`/`real_roots`/`nroots`/`all_roots`/`ground_roots`、`roots`、`compose`、`decompose`、`terms_gcd`、`trunc`、`monic`、`content`、`primitive`、`is_zero_dimensional`、`hurwitz_conditions`/`schur_conditions`、`poly`。

**F-120**：`Poly` 类定义于 [polys/polytools.py:110](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/polys/polytools.py#L110)，继承自 `Basic`，是表示和操作多项式的通用类。`construct_domain(obj, **args)` 函数定义于 [polys/constructor.py:268](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/polys/constructor.py#L268)，为表达式列表构造最小域。多项式域类（来自 `.domains`）包括：`Domain`、`FiniteField`/`GF`/`FF`、`IntegerRing`/`ZZ`、`RationalField`/`QQ`、`RealField`/`RR`、`ComplexField`/`CC`、`PolynomialRing`、`FractionField`、`AlgebraicField`、`CyclotomicField`、`ExpressionDomain`/`EX` 等，以及 GMPY 版本（`ZZ_gmpy`、`QQ_gmpy`、`FF_gmpy`）和 Python 版本（`ZZ_python`、`QQ_python`、`FF_python`）。

**F-121**：多项式错误类（来自 `.polyerrors`）包括：`BasePolynomialError`、`ExactQuotientFailed`、`PolynomialDivisionFailed`、`HeuristicGCDFailed`、`HomomorphismFailed`、`IsomorphismFailed`、`CoercionFailed`、`NotInvertible`、`DomainError`、`PolynomialError`、`GeneratorsNeeded`、`GeneratorsError`、`ComputationFailed`、`UnivariatePolynomialError`、`MultivariatePolynomialError`、`PolificationFailed`、`OptionError`、`FlagError` 等。其他工具函数：`symmetrize`、`horner`、`interpolate`、`viete`（来自 `.polyfuncs`）；`together`（来自 `.rationaltools`）；`apart`/`apart_list`/`assemble_partfrac_list`（来自 `.partfrac`）；`itermonomials`、`Monomial`（来自 `.monomials`）；`lex`/`grlex`/`grevlex`/`ilex`/`igrlex`/`igrevlex`（项序，来自 `.orderings`）；`CRootOf`/`rootof`/`RootOf`/`ComplexRootOf`/`RootSum`（来自 `.rootoftools`）；特殊多项式（`swinnerton_dyer_poly`、`cyclotomic_poly`、`symmetric_poly`、`random_poly`、`interpolating_poly`，来自 `.specialpolys`）；正交多项式（`jacobi_poly`、`chebyshevt_poly`、`chebyshevu_poly`、`hermite_poly`、`legendre_poly`、`laguerre_poly`，来自 `.orthopolys`）；Appell 序列多项式（`bernoulli_poly`、`genocchi_poly`、`euler_poly` 等，来自 `.appellseqs`）；`minpoly`/`minimal_polynomial`/`galois_group` 等数域函数（来自 `.numberfields`）；环/域构造器 `ring`/`xring`/`vring`/`sring` 和 `field`/`xfield`/`vfield`/`sfield`（来自 `.rings`/`.fields`）；`Options` 类（来自 `.polyoptions`）。

---

## 模块：logic/

**F-122**：[logic/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/__init__.py) 导出布尔代数类：`And`、`Or`、`Not`、`Xor`、`Nand`、`Nor`、`Implies`、`Equivalent`、`ITE`、`to_cnf`、`to_dnf`、`to_nnf`、`POSform`、`SOPform`、`simplify_logic`、`bool_map`、`true`、`false`、`gateinputcount`（来自 `.boolalg`）；以及 `satisfiable`（来自 `.inference`）。

**F-123**：`Boolean` 类定义于 [logic/boolalg.py:73](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/boolalg.py#L73)，继承自 `Basic`，`kind = BooleanKind`，是所有逻辑对象的基类。`BooleanFunction` 类定义于 [L490](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/boolalg.py#L490)，继承自 `Application` 和 `Boolean`，`is_Boolean = True`，是 `And`/`Or`/`Not` 等的基类。

**F-124**：`And` 类定义于 [logic/boolalg.py:580](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/boolalg.py#L580)，继承自 `LatticeOp` 和 `BooleanFunction`，表示逻辑与；`Or` 类定义于 [L753](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/boolalg.py#L753)，继承自 `LatticeOp` 和 `BooleanFunction`，表示逻辑或；`Not` 类定义于 [L872](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/boolalg.py#L872)，继承自 `BooleanFunction`，表示逻辑非。

**F-125**：`Xor` 类定义于 [logic/boolalg.py:988](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/boolalg.py#L988)，表示异或；`Nand` 定义于 [L1126](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/boolalg.py#L1126)，表示与非；`Nor` 定义于 [L1155](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/boolalg.py#L1155)，表示或非；`Implies` 定义于 [L1220](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/boolalg.py#L1220)，表示蕴含；`Equivalent` 定义于 [L1304](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/boolalg.py#L1304)，表示等价；`ITE` 定义于 [L1383](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/boolalg.py#L1383)，表示 if-then-else。

**F-126**：`satisfiable(expr, algorithm=None, all_models=False, minimal=False, use_lra_theory=False)` 函数定义于 [logic/inference.py:34](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/logic/inference.py#L34)，检查命题逻辑语句的可满足性，成功时返回一个模型。

---

## 模块：ntheory/

**F-127**：[ntheory/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/ntheory/__init__.py) 导出素数生成（来自 `.generate`）：`nextprime`、`prevprime`、`prime`、`primepi`、`primerange`、`randprime`、`Sieve`、`sieve`、`primorial`、`cycle_length`、`composite`、`compositepi`；素性测试（来自 `.primetest`）：`isprime`、`is_gaussian_prime`、`is_mersenne_prime`；因子分解（来自 `.factor_`）：`divisors`、`proper_divisors`、`factorint`、`multiplicity`、`perfect_power`、`pollard_rho`、`pollard_pm1`、`primefactors`、`totient`、`divisor_count`、`proper_divisor_count`、`divisor_sigma`、`factorrat`、`reduced_totient`、`is_perfect`、`is_abundant`、`is_deficient`、`is_amicable`、`is_carmichael`、`abundance` 等。

**F-128**：`Sieve` 类定义于 [ntheory/generate.py:27](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/ntheory/generate.py#L27)，实现动态增长的埃拉托斯特尼筛法，全局实例 `sieve` 在模块级导出。`primepi(n)` 定义于 [L546](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/ntheory/generate.py#L546)（素数计数函数）、`nextprime(n, ith=1)` 定义于 [L732](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/ntheory/generate.py#L732)、`primerange(a, b=None)` 定义于 [L866](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/ntheory/generate.py#L866)（素数范围生成器）。

**F-129**：`isprime(n)` 函数定义于 [ntheory/primetest.py:632](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/ntheory/primetest.py#L632)，返回 `bool`，对 n < 2^64 返回确定性结果。`factorint(n, limit=None, use_trial=True, use_rho=True, use_pm1=True, use_ecm=True, verbose=False, visual=None, multiple=False)` 定义于 [ntheory/factor_.py:1221](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/ntheory/factor_.py#L1221)，返回素因子分解字典；`primefactors(n, limit=None, verbose=False)` 定义于 [L1713](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/ntheory/factor_.py#L1713)，返回排序列表；`divisors(n, generator=False, proper=False)` 定义于 [L1812](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/ntheory/factor_.py#L1812)，返回因子列表或生成器。

**F-130**：[ntheory/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/ntheory/__init__.py) 还导出：模运算（来自 `.residue_ntheory`）：`is_primitive_root`、`is_quad_residue`、`legendre_symbol`、`jacobi_symbol`、`n_order`、`sqrt_mod`、`quadratic_residues`、`primitive_root`、`nthroot_mod`、`is_nthpow_residue`、`sqrt_mod_iter`、`mobius`、`discrete_log`、`quadratic_congruence`、`polynomial_congruence`；`npartitions`（来自 `.partitions_`）；`binomial_coefficients`、`binomial_coefficients_list`、`multinomial_coefficients`（来自 `.multinomial`）；连分数（来自 `.continued_fraction`）：`continued_fraction_periodic`、`continued_fraction_iterator`、`continued_fraction_reduce`、`continued_fraction_convergents`、`continued_fraction`；`count_digits`、`digits`、`is_palindromic`（来自 `.digits`）；`egyptian_fraction`（来自 `.egyptian_fraction`）；`ecm`（来自 `.ecm`）；`qs`、`qs_factor`（来自 `.qs`）。

---

## 模块：sets/

**F-131**：[sets/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/sets/__init__.py) 导出集合类：`Set`、`Interval`、`Union`、`FiniteSet`、`ProductSet`、`Intersection`、`imageset`、`Complement`、`SymmetricDifference`、`DisjointUnion`（来自 `.sets`）；`ImageSet`、`Range`、`ComplexRegion`（来自 `.fancysets`）；`Contains`（来自 `.contains`）；`ConditionSet`（来自 `.conditionset`）；`Ordinal`、`OmegaPower`、`ord0`（来自 `.ordinals`）；`PowerSet`（来自 `.powerset`）。预定义集合单例：`Complexes = S.Complexes`、`EmptySet = S.EmptySet`、`Integers = S.Integers`、`Naturals = S.Naturals`、`Naturals0 = S.Naturals0`、`Rationals = S.Rationals`、`Reals = S.Reals`、`UniversalSet = S.UniversalSet`。

**F-132**：`Set` 基类定义于 [sets/sets.py:48](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/sets/sets.py#L48)，继承自 `Basic` 和 `EvalfMixin`。子类包括：`ProductSet`（[L854](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/sets/sets.py#L854)，笛卡尔积）、`Interval`（[L1035](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/sets/sets.py#L1035)，实数区间）、`Union`（[L1319](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/sets/sets.py#L1319)，继承 `Set` 和 `LatticeOp`，集合并）、`Intersection`（[L1509](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/sets/sets.py#L1509)，继承 `Set` 和 `LatticeOp`，集合交）、`Complement`（[L1748](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/sets/sets.py#L1748)，差集）、`EmptySet`（[L1846](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/sets/sets.py#L1846)，使用 `metaclass=Singleton`，空集）、`FiniteSet`（[L1974](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/sets/sets.py#L1974)，有限集）、`SymmetricDifference`（[L2218](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/sets/sets.py#L2218)，对称差）。

---

## 模块：stats/

**F-133**：[stats/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/stats/__init__.py) 导出概率查询函数（来自 `.rv_interface`）：`P`（概率）、`E`（期望）、`H`（熵）、`density`、`where`、`given`、`sample`、`cdf`、`median`、`characteristic_function`、`pspace`、`sample_iter`、`variance`、`std`、`skewness`、`kurtosis`、`covariance`、`dependent`、`entropy`、`independent`、`random_symbols`、`correlation`、`factorial_moment`、`moment`、`cmoment`、`sampling_density`、`moment_generating_function`、`smoment`、`quantile`、`coskewness`、`sample_stochastic_process`。

**F-134**：有限分布随机变量（来自 `.frv_types`）：`FiniteRV`、`DiscreteUniform`、`Die`、`Bernoulli`、`Coin`、`Binomial`、`BetaBinomial`、`Hypergeometric`、`Rademacher`、`IdealSoliton`、`RobustSoliton`、`FiniteDistributionHandmade`。连续分布随机变量（来自 `.crv_types`）：`ContinuousRV`、`Arcsin`、`Benini`、`Beta`、`Cauchy`、`Chi`、`ChiSquared`、`Exponential`、`Gamma`、`Gumbel`、`Laplace`、`LogNormal`、`Normal`、`Pareto`、`Rayleigh`、`StudentT`、`Triangular`、`Uniform`、`VonMises`、`Weibull`、`WignerSemicircle`、`ContinuousDistributionHandmade` 等。离散分布（来自 `.drv_types`）：`Geometric`、`Hermite`、`Logarithmic`、`NegativeBinomial`、`Poisson`、`Skellam`、`YuleSimon`、`Zeta`、`DiscreteRV`、`DiscreteDistributionHandmade`、`FlorySchulz`。

**F-135**：联合分布（来自 `.joint_rv_types`）：`JointRV`、`Dirichlet`、`Multinomial`、`MultivariateBeta`、`MultivariateNormal`、`MultivariateT`、`MultivariateLaplace`、`NormalGamma`、`NegativeMultinomial`、`marginal_distribution` 等。随机过程（来自 `.stochastic_process_types`）：`StochasticProcess`、`DiscreteTimeStochasticProcess`、`DiscreteMarkovChain`、`ContinuousMarkovChain`、`BernoulliProcess`、`PoissonProcess`、`WienerProcess`、`GammaProcess`、`TransitionMatrixOf`、`StochasticStateSpaceOf`、`GeneratorMatrixOf`。随机矩阵模型（来自 `.random_matrix_models`）：`GaussianEnsemble`、`CircularEnsemble` 及其子类型（GUE/GOE/GSE/CUE/COE/CSE）；矩阵分布：`MatrixGamma`、`Wishart`、`MatrixNormal`、`MatrixStudentT`。符号概率类：`Probability`、`Expectation`、`Variance`、`Covariance`、`Moment`、`CentralMoment`（来自 `.symbolic_probability`），以及 `ExpectationMatrix`、`VarianceMatrix`、`CrossCovarianceMatrix`（来自 `.symbolic_multivariate_probability`）。

---

## 模块：concrete/

**F-136**：[concrete/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/concrete/__init__.py) 导出 `product`、`Product`（来自 `.products`）和 `summation`、`Sum`（来自 `.summations`）。

**F-137**：`Sum` 类定义于 [concrete/summations.py:46](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/concrete/summations.py#L46)，继承自 `AddWithLimits` 和 `ExprWithIntLimits`，表示未求值的求和；`summation(f, *symbols, **kwargs)` 函数定义于 [L922](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/concrete/summations.py#L922)，计算求和。`Product` 类定义于 [concrete/products.py:20](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/concrete/products.py#L20)，继承自 `ExprWithIntLimits`，表示未求值的乘积；`product(*args, **kwargs)` 函数定义于 [L571](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/concrete/products.py#L571)，计算乘积。

**F-138**：`gosper_sum(f, k)` 函数定义于 [concrete/gosper.py:160](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/concrete/gosper.py#L160)，实现 Gosper 超几何求和算法。

---

## 模块：tensor/

**F-139**：[tensor/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/tensor/__init__.py) 导出索引对象：`IndexedBase`、`Idx`、`Indexed`（来自 `.indexed`）；`get_contraction_structure`、`get_indices`（来自 `.index_methods`）；`shape`（来自 `.functions`）；N 维数组类（来自 `.array`）：`MutableDenseNDimArray`、`ImmutableDenseNDimArray`、`MutableSparseNDimArray`、`ImmutableSparseNDimArray`、`NDimArray`、`DenseNDimArray`、`SparseNDimArray`、`Array`，以及 `tensorproduct`、`tensorcontraction`、`tensordiagonal`、`derive_by_array`、`permutedims`。

**F-140**：`Indexed` 类定义于 [tensor/indexed.py:125](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/tensor/indexed.py#L125)，继承自 `Expr`，表示带索引的数学对象；`IndexedBase` 类定义于 [L363](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/tensor/indexed.py#L363)，继承自 `Expr` 和 `NotIterable`，表示索引对象的基，通过 `__getitem__` 返回 `Indexed` 实例；`Idx` 类定义于 [L581](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/tensor/indexed.py#L581)，继承自 `Expr`，表示整数索引。

**F-141**：`NDimArray` 基类定义于 [tensor/array/ndim_array.py:89](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/tensor/array/ndim_array.py#L89)，继承自 `Printable`；`DenseNDimArray` 定义于 [tensor/array/dense_ndim_array.py:13](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/tensor/array/dense_ndim_array.py#L13)，继承自 `NDimArray`，内部使用 `_array: list[Basic]` 存储；`ImmutableDenseNDimArray`（[L131](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/tensor/array/dense_ndim_array.py#L131)）继承 `DenseNDimArray` 和 `ImmutableNDimArray`；`MutableDenseNDimArray`（[L159](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/tensor/array/dense_ndim_array.py#L159)）继承 `DenseNDimArray` 和 `MutableNDimArray`；`SparseNDimArray` 定义于 [tensor/array/sparse_ndim_array.py:12](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/tensor/array/sparse_ndim_array.py#L12)，继承自 `NDimArray`。

---

## 模块：printing/

**F-142**：[printing/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/printing/__init__.py) 导出多语言打印函数：`pretty`/`pprint`/`pretty_print`/`pager_print`（来自 `.pretty`，Unicode 美观打印）；`latex`/`print_latex`/`multiline_latex`（来自 `.latex`）；`mathml`/`print_mathml`（来自 `.mathml`）；`python`/`print_python`（来自 `.python`）；`pycode`（来自 `.pycode`）；`ccode`/`print_ccode`、`fcode`/`print_fcode`、`cxxcode`、`rust_code`（来自 `.codeprinter`）；`smtlib_code`（来自 `.smtlib`）；`glsl_code`/`print_glsl`（来自 `.glsl`）；`rcode`/`print_rcode`（来自 `.rcode`）；`jscode`/`print_jscode`（来自 `.jscode`）；`julia_code`（来自 `.julia`）；`mathematica_code`（来自 `.mathematica`）；`octave_code`（来自 `.octave`）；`maple_code`/`print_maple_code`（来自 `.maple`）；`srepr`（来自 `.repr`）；`print_tree`（来自 `.tree`）；`StrPrinter`/`sstr`/`sstrrepr`（来自 `.str`）；`TableForm`（来自 `.tableform`）；`dotprint`（来自 `.dot`）；`print_gtk`（来自 `.gtk`）；`preview`（来自 `.preview`）。

**F-143**：`Printer` 基类定义于 [printing/printer.py:235](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/printing/printer.py#L235)，是通用打印器基类，提供实现新打印器的基础设施。`StrPrinter` 类定义于 [printing/str.py:25](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/printing/str.py#L25)，继承自 `Printer`，`printmethod = "_sympystr"`，`_default_settings` 包含 `"order": None`。`LatexPrinter` 类定义于 [printing/latex.py:142](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/printing/latex.py#L142)，继承自 `Printer`，`printmethod = "_latex"`。`PythonPrinter` 类定义于 [printing/python.py:11](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/printing/python.py#L11)，继承自 `ReprPrinter` 和 `StrPrinter`，将表达式转换为 Python 代码。

---

## 模块：parsing/

**F-144**：`parse_expr(s, local_dict=None, transformations=standard_transformations, global_dict=None, evaluate=True)` 函数定义于 [parsing/sympy_parser.py:913](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/parsing/sympy_parser.py#L913)，将字符串 `s` 转换为 SymPy 表达式。`Transform` 类（AST 节点转换器）定义于 [parsing/ast_parser.py:29](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/parsing/ast_parser.py#L29)，继承自 `NodeTransformer`，`__init__(self, local_dict, global_dict)` 接收局部和全局字典。`parsing/latex/` 子目录存在，包含基于 Lark 的 LaTeX 解析器，`TransformToSymPyExpr` 类定义于 [parsing/latex/lark/transformer.py:27](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/parsing/latex/lark/transformer.py#L27)，继承自 `Transformer`。

---

## 模块：codegen/

**F-145**：[codegen/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/__init__.py) 导出跨语言 AST 节点类（来自 `.ast`）：`Assignment`、`aug_assign`、`CodeBlock`、`For`、`Attribute`、`Variable`、`Declaration`、`While`、`Scope`、`Print`、`FunctionPrototype`、`FunctionDefinition`、`FunctionCall`。子模块包括：`ast.py`（通用 AST 节点）、`cnodes.py`（C 语言节点，包含 `CommaOperator`、`Label`、`goto`、`PreDecrement` 等）、`fnodes.py`（Fortran 节点，包含 `Program`、`use`、`use_rename`、`Module` 等）、`cfunctions.py`（C99 数学函数）、`ffunctions.py`（Fortran 特有函数）。

**F-146**：`Assignment` 类定义于 [codegen/ast.py:463](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/ast.py#L463)，继承自 `AssignmentBase`，表示变量赋值；`CodeBlock` 类定义于 [L593](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/ast.py#L593)，继承自 `CodegenAST`，表示代码块；`For` 类定义于 [L810](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/ast.py#L810)，继承自 `Token`，表示 for 循环；`While` 类定义于 [L1637](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/ast.py#L1637)，表示 while 循环；`Variable` 类定义于 [L1410](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/ast.py#L1410)，继承自 `Node`，表示变量；`FunctionPrototype` 定义于 [L1751](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/ast.py#L1751)，`FunctionDefinition` 定义于 [L1800](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/ast.py#L1800)（继承自 `FunctionPrototype`），`FunctionCall` 定义于 [L1870](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/ast.py#L1870)（继承自 `Token` 和 `Expr`），`Declaration` 定义于 [L1610](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/ast.py#L1610)，`Scope` 定义于 [L1675](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/ast.py#L1675)，`Print` 定义于 [L1724](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/ast.py#L1724)，`Attribute` 定义于 [L1366](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/codegen/ast.py#L1366)。

---

## 模块：utilities/

**F-147**：`lambdify(args, expr, modules=None, printer=None, use_imps=True, dummify=False, cse=False, docstring_limit=1000)` 函数定义于 [utilities/lambdify.py:213](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/utilities/lambdify.py#L213)，将 SymPy 表达式转换为可快速数值求值的 Python 函数。

---

## 模块：vector/

**F-148**：[vector/__init__.py](file:///d:/spaces/SpecWeave/external/libs/python/sympy/sympy/sympy/vector/__init__.py) 导出向量类（来自 `.vector`）：`Vector`、`VectorAdd`、`VectorMul`、`BaseVector`、`VectorZero`、`Cross`、`Dot`、`cross`、`dot`；并矢类（来自 `.dyadic`）：`Dyadic`、`DyadicAdd`、`DyadicMul`、`BaseDyadic`、`DyadicZero`；`BaseScalar`（来自 `.scalar`）；`Del`（来自 `.deloperator`）；`CoordSys3D`（来自 `.coordsysrect`）；向量函数（来自 `.functions`）：`express`、`matrix_to_vector`、`matrix_to_dyadic`、`laplacian`、`is_conservative`、`is_solenoidal`、`scalar_potential`、`directional_derivative`、`scalar_potential_difference`；`Point`（来自 `.point`）；定向器（来自 `.orienters`）：`AxisOrienter`、`BodyOrienter`、`SpaceOrienter`、`QuaternionOrienter`；微分算子（来自 `.operators`）：`Gradient`、`Divergence`、`Curl`、`Laplacian`、`gradient`、`curl`、`divergence`；`ParametricRegion`、`parametric_region_list`、`ImplicitRegion`（来自 `.parametricregion`/`.implicitregion`）；`ParametricIntegral`、`vector_integrate`（来自 `.integrals`）；`VectorKind`（来自 `.kind`）。
