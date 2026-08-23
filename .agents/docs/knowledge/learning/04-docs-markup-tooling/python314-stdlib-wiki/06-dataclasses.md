---
id: "python314-stdlib-wiki-06"
title: "Python 3.14 标准库 dataclasses 全面详解"
source: "https://docs.python.org/3.14/"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/python314-stdlib-wiki/06-dataclasses.toml"
---

# Python 3.14 标准库 dataclasses 全面详解

> 一句话摘要：`dataclasses` 模块用一个 `@dataclass` 装饰器和一组配套函数，根据你在类里写的类型标注自动生成 `__init__`、`__repr__`、`__eq__` 等样板方法，让你只声明字段就能得到一个功能完整的数据类。

## 1. 模块定位与用途

`dataclasses` 是 Python 标准库内置模块（源码位于 `Lib/dataclasses.py`），最初的设想见 [**PEP 557**](https://peps.python.org/pep-0557/)，于 Python 3.7 引入。

它的核心目标只有一个：**消灭样板代码（boilerplate）**。在只使用普通类的时代，每写一个"只用来装数据"的类，都要手写一遍构造函数、可读的字符串表示、相等性比较等方法。例如：

```python
class InventoryItem:
    def __init__(self, name, unit_price, quantity_on_hand=0):
        self.name = name
        self.unit_price = unit_price
        self.quantity_on_hand = quantity_on_hand
    def __repr__(self):
        return (f"InventoryItem(name={self.name!r}, unit_price={self.unit_price!r}, "
                f"quantity_on_hand={self.quantity_on_hand!r})")
    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.name, self.unit_price, self.quantity_on_hand) == \
               (other.name, other.unit_price, other.quantity_on_hand)
```

用 `dataclasses` 之后，同样的类只需要声明字段即可：

```python
from dataclasses import dataclass

@dataclass
class InventoryItem:
    """用于记录库存中一件商品的类。"""
    name: str
    unit_price: float
    quantity_on_hand: int = 0
```

装饰器会自动补上 `__init__`、`__repr__`、`__eq__` 等方法，其效果等价于：

```python
def __init__(self, name: str, unit_price: float, quantity_on_hand: int = 0):
    self.name = name
    self.unit_price = unit_price
    self.quantity_on_hand = quantity_on_hand
```

需要特别强调的是：这些方法是被**自动添加**到类里的，并不是你手写的那一份。字段的成员变量通过 [**PEP 526**](https://peps.python.org/pep-0526/) 类型标注（`name: str` 这种写法）来定义。

## 2. 核心术语表

| 术语 | 一句话平实解释 |
|---|---|
| 数据类（dataclass） | 用 `@dataclass` 装饰的普通类，会自动获得若干常用方法 |
| 字段（field） | 类里带类型标注的变量，代表每个实例各自拥有的一个数据槽位 |
| 装饰器（decorator） | 以 `@` 开头写在类或函数上方的一种语法，能在不改动原有代码的情况下给它附加额外功能 |
| 特殊方法 / 双下划线方法（dunder method） | 名字以双下划线开头和结尾的方法，如 `__init__`、`__repr__`，由 Python 在特定时机自动调用 |
| 默认值（default） | 参数没有被显式传入时采用的预设值 |
| 默认工厂（default_factory） | 一个不带参数的函数，每次需要默认值时被调用一次，从而生成一个全新的默认值 |
| 哨兵值（sentinel） | 一个特殊的占位对象，专门用来表示"这个参数没有被调用方提供" |
| 不可哈希（unhashable） | 对象无法交给内置 `hash()` 处理，因此不能作为字典的键或放进集合，通常意味着该对象是可变的 |
| 仅关键字参数（keyword-only） | 调用时只能写成 `name=value`、不能按位置顺序传入的参数 |
| 类变量（ClassVar） | 属于类本身而非某个实例的变量，所有实例共享同一个值 |
| 仅初始化变量（InitVar） | 只在对象初始化阶段参与、不会作为实例属性保留下来的临时参数 |
| slots | 一种让实例不再自带 `__dict__` 字典、从而节省内存并略微提升访问速度的机制 |

## 3. `@dataclass` 装饰器详解

装饰器完整签名如下：

```python
@dataclasses.dataclass(*, init=True, repr=True, eq=True, order=False,
                        unsafe_hash=False, frozen=False, match_args=True,
                        kw_only=False, slots=False, weakref_slot=False)
```

（签名中的 `*` 表示其后的所有参数都只能以关键字形式传入。）`@dataclass` 会检查类并找出其中的字段——字段被定义为**带有类型标注的类变量**。除后文说明的两处例外（`ClassVar` 与 `InitVar`），装饰器**不会**去校验标注里写的具体类型是什么。

字段在所有生成方法中的顺序，就是它们在类定义中出现的顺序。装饰器返回传入的那个类本身，并不会创建新类（`slots=True` 时除外，详见下文）。

若将 `@dataclass` 当作不带任何参数的简单装饰器使用，其行为等同于全部采用默认值——下面三种写法完全等价：

```python
@dataclass
class C: ...

@dataclass()
class C: ...

@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False,
           frozen=False, match_args=True, kw_only=False, slots=False,
           weakref_slot=False)
class C: ...
```

各参数语义如下：

- **`init`**：若为真（默认），生成 `__init__()` 方法。若类里已经定义了 `__init__()`，此参数会被忽略。
- **`repr`**：若为真（默认），生成 `__repr__()` 方法。生成的字符串形如 `InventoryItem(name='widget', unit_price=3.0, quantity_on_hand=10)`，包含类名和各字段的名称及 `repr`，按定义顺序排列；被标记为从 `repr` 中排除的字段不会出现。若类里已定义 `__repr__()`，此参数被忽略。
- **`eq`**：若为真（默认），生成 `__eq__()` 方法。该方法按字段顺序逐一比较类；参与比较的两个实例必须是同一类型。若类里已定义 `__eq__()`，此参数被忽略。
  > 3.13 版本变更：生成的 `__eq__` 现在逐字段比较（如 `self.a == other.a and self.b == other.b`），而不再像旧版本那样把字段打包成元组再比较。这一改动让比较更快，但在"属性按同一性相等、按值不相等"的场景（如 `float('nan')`）中可能改变比较结果。3.12 及更早版本的做法是构造字段元组再比较（如 `(self.a, self.b) == (other.a, other.b)`）。
- **`order`**：若为真（默认 `False`），生成 `__lt__()`、`__le__()`、`__gt__()`、`__ge__()` 方法。它们把类当作"由字段依次组成的元组"来比较，两个实例必须是同一类型。若 `order=True` 而 `eq=False`，会引发 `ValueError`。若类里已定义了上述任意一个比较方法，会引发 `TypeError`。
- **`unsafe_hash`**：若为真，强制 `dataclasses` 生成 `__hash__()` 方法，即便可能不安全。默认 `False`。`__hash__()` 供内置 `hash()` 使用，并在对象被加入字典、集合等哈希容器时被调用。拥有 `__hash__()` 意味着实例应当是不可变的。可变性是一个复杂属性，取决于程序员的意图、`__eq__()` 是否存在与行为，以及 `@dataclass` 的 `eq`、`frozen` 标志。
  - 默认情况下，`@dataclass` 只在**安全**时才隐式添加 `__hash__()`，也绝不添加或改动已有的显式 `__hash__()`。将类属性设为 `__hash__ = None` 对 Python 有特殊含义（表示不可哈希）。
  - 隐式生成 `__hash__()` 的规则：若 `eq` 与 `frozen` 均为真，则默认生成 `__hash__()`；若 `eq` 为真而 `frozen` 为假，则 `__hash__()` 被设为 `None`（标记为不可哈希，因为它可变）；若 `eq` 为假，则 `__hash__()` 保持不动，意味着沿用超类的 `__hash__()`（若超类是 `object`，则退化为基于 id 的哈希）。
  - 注意：不能在类里既定义显式 `__hash__()` 又设置 `unsafe_hash=True`，否则引发 `TypeError`。
  - `unsafe_hash=True` 应谨慎使用，只有在你确定"类在逻辑上不可变、只是仍可能被修改"这类特殊场景才需要。
- **`frozen`**：若为真（默认 `False`），对字段赋值将抛异常，以此模拟只读的冻结实例（详见后文"只读实例"）。若类里定义了 `__setattr__()` 或 `__delattr__()` 且 `frozen=True`，会引发 `TypeError`。
- **`match_args`**：若为真（默认 `True`），将根据传给生成的 `__init__()` 的**非仅关键字**参数列表创建 `__match_args__` 元组（即使未生成 `__init__()` 也一样，见上文）。若为假，或类里已定义 `__match_args__`，则不生成。3.10 新增。该元组用于模式匹配（`match`/`case`）时按位置拆包字段。
- **`kw_only`**：若为真（默认 `False`），所有字段都被标记为仅关键字字段。其唯一影响是：由仅关键字字段生成的 `__init__()` 形参在调用时**必须**以关键字形式指定。仅关键字字段不会被纳入 `__match_args__`。3.10 新增。
- **`slots`**：若为真（默认 `False`），将生成 `__slots__` 属性并**返回一个新类**而非原类。若类里已定义 `__slots__`，引发 `TypeError`。3.10 新增。
  > 警告：使用 `slots=True` 时向基类的 `__init_subclass__()` 传参会引发 `TypeError`，应改用不带参数的 `__init_subclass__` 或带默认值的方式绕过，详见 [gh-91126](https://github.com/python/cpython/issues/91126)。
  > 3.11 变更：若某字段名已包含在基类的 `__slots__` 中，它不会出现在新生成的 `__slots__` 里以避免覆写。因此不要用 `__slots__` 来读取数据类的字段名，应改用 `fields()`。
- **`weakref_slot`**：若为真（默认 `False`），增加一个名为 `"__weakref__"` 的槽位，这是让实例可被弱引用所必需的。只指定 `weakref_slot=True` 而不同时指定 `slots=True` 会报错。3.11 新增。

### 字段默认值的普通语法

可以就用普通 Python 语法给字段指定默认值：

```python
@dataclass
class C:
    a: int       # 'a' 没有默认值
    b: int = 0   # 给 'b' 赋默认值
```

生成的 `__init__` 为：

```python
def __init__(self, a: int, b: int = 0): ...
```

若一个**没有默认值**的字段出现在一个**有默认值**的字段之后（无论发生在单个类里，还是类继承累积的结果），都会引发 `TypeError`。

## 4. `field()` 函数详解

对常见、简单的用例，不需要额外功能。但有些数据类特性需要"逐字段"的额外信息，此时可以用 `field()` 函数替换字段默认值所在的位置。完整签名：

```python
dataclasses.field(*, default=MISSING, default_factory=MISSING, init=True,
                  repr=True, hash=None, compare=True, metadata=None,
                  kw_only=MISSING, doc=None)
```

常见示例：

```python
@dataclass
class C:
    mylist: list[int] = field(default_factory=list)

c = C()
c.mylist += [1, 2, 3]
```

各参数语义如下：

- **`default`**：若提供，作为该字段的默认值。需要它的原因是 `field()` 调用本身就占用了原本写默认值的位置。
- **`default_factory`**：若提供，必须是一个**零参数可调用对象**，在字段需要默认值时被调用。典型用途是给可变类型字段生成全新的默认值（见后文"可变默认值"）。同时指定 `default` 和 `default_factory` 会报错。
- **`init`**：若为真（默认），该字段作为形参出现在生成的 `__init__()` 中。
- **`repr`**：若为真（默认），该字段出现在生成的 `__repr__()` 返回的字符串里。
- **`hash`**：可为布尔值或 `None`。为真则纳入生成的 `__hash__()`；为假则排除；为 `None`（默认）则采用 `compare` 的值——这通常是期望行为，因为"用于比较的字段就应当参与哈希"。不建议设成 `None` 以外的值。一个设 `hash=False` 但 `compare=True` 的合理场景是：某字段计算哈希代价很高，但相等性判断又离不开它，且还有其他字段可决定哈希值。即便某字段被排除在哈希之外，它仍会被用于比较。
- **`compare`**：若为真（默认），该字段纳入生成的相等与比较方法（`__eq__()`、`__gt__()` 等）。
- **`metadata`**：可为映射或 `None`（`None` 等价于空字典）。该值会被包装进 `MappingProxyType()` 变为只读，并暴露在 `Field` 对象上。数据类本身**完全不用**它，它只是提供给第三方的扩展机制，多个第三方可各自用自己的键作为命名空间。
- **`kw_only`**：若为真，该字段标记为仅关键字。3.10 新增。仅关键字字段不会进入 `__match_args__`。
- **`doc`**：该字段的可选文档字符串。3.14 新增。

一个关于类属性的细节：若字段默认值通过 `field()` 指定，该字段对应的类属性会被替换为指定的 `default` 值；若未提供 `default`，该类属性会被删除。目的是让 `@dataclass` 运行后，类属性里保存的都是字段默认值，如同你直接写了默认值一样。例如执行：

```python
@dataclass
class C:
    x: int
    y: int = field(repr=False)
    z: int = field(repr=False, default=10)
    t: int = 20
```

之后 `C.z` 为 `10`、`C.t` 为 `20`，而 `C.x` 和 `C.y` 不会被设置。

### `Field` 类

`class dataclasses.Field` 描述每个已定义的字段。这些对象由内部创建，通过模块级函数 `fields()` 返回。**用户绝不应直接实例化 `Field`**。其已文档化的属性有：

- `name`：字段名。
- `type`：字段类型。
- `default`、`default_factory`、`init`、`repr`、`hash`、`compare`、`metadata`、`kw_only`：含义与 `field()` 中同名参数一致（3.14 起还含 `doc`）。

其余属性均为私有，不应检查或依赖。

## 5. 特殊标识符与单例：`MISSING`、`KW_ONLY`

- **`dataclasses.MISSING`**：一个哨兵值，表示"缺少 `default` 或 `default_factory`"。之所以需要它，是因为 `None` 对某些参数是合法的用户取值（含义不同）。任何代码都不应直接使用 `MISSING` 值。
- **`dataclasses.KW_ONLY`**：一个用作类型标注的哨兵值。凡出现在类型为 `KW_ONLY` 的伪字段**之后**的字段，都会被标记为仅关键字字段（3.10 新增）。该伪字段本身被完全忽略，包括它的名字；按惯例其名字用 `_`。例如：

```python
@dataclass
class Point:
    x: float
    _: KW_ONLY
    y: float
    z: float

p = Point(0, y=1.5, z=2.0)   # y、z 被标记为仅关键字
```

在单个数据类里指定多于一个类型为 `KW_ONLY` 的字段会报错。

## 6. 伪字段与内建类型：`InitVar`、`ClassVar`

这是 `@dataclass` 为数不多会真正检查字段类型注解的地方。

### `ClassVar`（类变量）

`typing.ClassVar` 标注的字段会被判定为**类变量**，从而被排除在字段之外、被数据类机制忽略。它们不会被 `fields()` 返回。所有实例共享同一个类变量值。

### `InitVar[T]`（仅初始化变量）

`dataclasses.InitVar[T]` 标注的字段是"仅初始化"变量，属于**伪字段**：既不会被 `fields()` 返回，也不会以实例属性形式留存，唯一的用途是作为形参加入生成的 `__init__()`（以及可选的 `__post_init__()`）。典型场景是：字段需要一个对外的初始输入，但最终要转换/派生为别的内部属性。例如从数据库取值初始化：

```python
@dataclass
class C:
    i: int
    j: int | None = None
    database: InitVar[DatabaseType | None] = None

    def __post_init__(self, database):
        if self.j is None and database is not None:
            self.j = database.lookup('j')

c = C(10, database=my_database)
```

此处 `fields()` 只返回 `i` 和 `j` 的 `Field`，不返回 `database`。

## 7. 模块级函数

### `dataclasses.fields(class_or_instance)`

返回一个 `Field` 对象元组，描述该数据类的全部字段。接受数据类本身或其实例。传入的不是数据类时引发 `TypeError`。**不返回** `ClassVar` 或 `InitVar` 之类的伪字段。

### `dataclasses.asdict(obj, *, dict_factory=dict)`

把数据类 `obj` 转换为字典（用工厂函数 `dict_factory` 创建）。每个数据类被转为以 `name: value` 键值对存储其字段的字典；数据类、字典、列表、元组会被递归处理；其他对象通过 `copy.deepcopy()` 拷贝。嵌套示例：

```python
@dataclass
class Point:
    x: int
    y: int

@dataclass
class C:
    mylist: list[Point]

p = Point(10, 20)
assert asdict(p) == {'x': 10, 'y': 20}
c = C([Point(0, 0), Point(10, 4)])
assert asdict(c) == {'mylist': [{'x': 0, 'y': 0}, {'x': 10, 'y': 4}]}
```

制作浅拷贝的变通写法：`{field.name: getattr(obj, field.name) for field in fields(obj)}`。`obj` 不是数据类实例时引发 `TypeError`。

### `dataclasses.astuple(obj, *, tuple_factory=tuple)`

把数据类 `obj` 转换为元组（用 `tuple_factory` 创建）。递归规则同 `asdict()`。接续上例：`astuple(p) == (10, 20)`、`astuple(c) == ([(0, 0), (10, 4)],)`。浅拷贝变通写法：`tuple(getattr(obj, field.name) for field in dataclasses.fields(obj))`。

### `dataclasses.make_dataclass(cls_name, fields, *, bases=(), namespace=None, ..., module=None, decorator=dataclass)`

动态新建数据类。`fields` 是元素形如 `name`、`(name, type)` 或 `(name, type, Field)` 的可迭代对象；仅给 `name` 时类型用 `typing.Any`。其余 `init`、`repr`、`eq`、`order`、`unsafe_hash`、`frozen`、`match_args`、`kw_only`、`slots`、`weakref_slot` 与 `@dataclass` 含义相同。`module` 设 `__module__` 属性（默认为调用方模块名）。`decorator` 参数（3.14 新增）是实际用于创建数据类的可调用对象，默认就是 `@dataclass`。例如：

```python
C = make_dataclass('C',
                   [('x', int),
                    'y',
                    ('z', int, field(default=5))],
                   namespace={'add_one': lambda self: self.x + 1})
```

### `dataclasses.replace(obj, /, **changes)`

创建一个与 `obj` 同类型的新对象，用 `changes` 中的值替换字段。`obj` 不是数据类、或 `changes` 中的键不是该数据类的字段名，都会引发 `TypeError`。新对象通过调用数据类的 `__init__()` 创建，因此若有 `__post_init__()` 也会被调用。若无默认值的仅初始化变量存在，调用 `replace()` 时必须给出它们的值。若 `changes` 含任何 `init=False` 的字段，引发 `ValueError`。要留意 `init=False` 字段在 `replace()` 中的行为：它们不会被从源对象拷贝，而是在 `__post_init__()`（若有）里初始化；建议尽量少用 `init=False` 字段。数据类实例也受泛型函数 `copy.replace()` 支持。

### `dataclasses.is_dataclass(obj)`

参数是数据类（含其子类，但不含泛型别名）或其实例时返回 `True`，否则返回 `False`。若要判断"是否数据类的实例（而非数据类本身）"，可加一层 `not isinstance(obj, type)`：

```python
def is_dataclass_instance(obj):
    return is_dataclass(obj) and not isinstance(obj, type)
```

### `exception dataclasses.FrozenInstanceError`

当对以 `frozen=True` 定义的数据类调用隐式定义的 `__setattr__()` 或 `__delattr__()` 时被引发。它是 `AttributeError` 的子类。

## 8. `__post_init__()` 钩子与初始化后处理

在类上定义了 `__post_init__()` 后，它会被生成的 `__init__()` 调用，通常是 `self.__post_init__()`。若定义了任何 `InitVar` 字段，它们会按类中定义的顺序**作为参数**传给 `__post_init__()`。若没有生成 `__init__()`，`__post_init__()` 不会被自动调用。

常见用途是初始化"依赖其他字段"的派生字段：

```python
@dataclass
class C:
    a: float
    b: float
    c: float = field(init=False)

    def __post_init__(self):
        self.c = self.a + self.b
```

`@dataclass` 生成的 `__init__()` **不会**调用基类的 `__init__()`。若基类有必须调用的 `__init__()`，通常的做法是在 `__post_init__()` 里调用：

```python
class Rectangle:
    def __init__(self, height, width):
        self.height = height
        self.width = width

@dataclass
class Square(Rectangle):
    side: float

    def __post_init__(self):
        super().__init__(self.side, self.side)
```

不过一般而言，若基类本身也是数据类，派生数据类会自动初始化基类所有字段，通常无需手动调用基类 `__init__()`。

## 9. 继承、字段顺序与内部元数据属性

当 `@dataclass` 创建数据类时，会以**逆 MRO**（从 `object` 开始）遍历所有基类，把每个数据类基类的字段加入一个**有序**字段映射，最后再加入自身字段。生成的所有方法都使用这份合并后的有序映射。由于字段按插入顺序排列，派生类会覆盖基类同名字段。示例：

```python
@dataclass
class Base:
    x: Any = 15.0
    y: int = 0

@dataclass
class C(Base):
    z: int = 10
    x: int = 15
```

最终字段顺序是 `x, y, z`，且 `x` 的最终类型是 `int`（以 `C` 中的声明为准），生成的 `__init__` 为 `def __init__(self, x: int = 15, y: int = 0, z: int = 10):`。

### 仅关键字参数的重新排序

`__init__()` 所需参数计算完成后，所有仅关键字参数会被移到所有普通参数之后——这是 Python 对仅关键字参数实现方式的硬性要求。相对顺序保持不变。例如：

```python
@dataclass
class Base:
    x: Any = 15.0
    _: KW_ONLY
    y: int = 0
    w: int = 1

@dataclass
class D(Base):
    z: int = 10
    t: int = field(kw_only=True, default=0)
```

`D` 生成的 `__init__` 为 `def __init__(self, x: Any = 15.0, z: int = 10, *, y: int = 0, w: int = 1, t: int = 0):`——普通字段参数在前，仅关键字参数在后。

### 三个内部元数据属性

数据类在类创建时还会挂载若干以 `__dataclass_` 前缀开头的内部属性，它们属于实现细节，官方文档并未承诺其稳定性，仅作了解即可：

- **`__dataclass_fields__`**：一个 `dict`，把每个字段名映射到对应的 `Field` 对象（`fields()` 函数内部就基于它工作）。
- **`__dataclass_params__`**：一个内部参数对象，记录传给 `@dataclass` 的 `init`、`repr`、`eq`、`order`、`unsafe_hash`、`frozen`、`match_args`、`kw_only`、`slots`、`weakref_slot` 的实际值。
- **`__dataclass_owner__`**：需要说明的是，在 Python 3.14 中，`Field` 对象上已**不再**存在这一属性（较早版本的若干实现中曾作为内部属性记录"字段最初定义于哪个类"）。由于它从未成为官方公开 API，请勿在代码中依赖；如需判断字段归属，可借助基类的 `__dataclass_fields__` 或读取 `Field` 的 `name`、`type` 等信息自行推断。

## 10. 只读实例（frozen）、可哈希、slots 与 weakref

- **frozen**：Python 无法创建真正不可变的对象，但传 `frozen=True` 可以模拟不可变。此时数据类会添加 `__setattr__()` 和 `__delattr__()` 方法，调用时抛出 `FrozenInstanceError`。使用 `frozen=True` 有极小的性能损耗：`__init__()` 不能再用简单赋值初始化字段，而必须改用 `object.__setattr__()`。
- **可哈希**：结合第 3 节的 `unsafe_hash` 规则——`frozen=True` 且 `eq=True` 时自动获得 `__hash__()`，实例可安全放入字典/集合；`eq=True` 而 `frozen=False` 时 `__hash__` 被置为 `None`（不可哈希）。
- **slots**：`slots=True` 生成 `__slots__` 并返回新类，实例不再有 `__dict__`，节省内存。注意不要用 `__slots__` 读取字段名（继承时可能不完整），应使用 `fields()`。基类 `__slots__` 可以是任意可迭代对象，但不能是迭代器。
- **weakref**：`weakref_slot=True` 增加一个名为 `"__weakref__"` 的槽位，使实例可被弱引用；它必须与 `slots=True` 同时使用。

## 11. 综合代码示例

### 示例一：基础用法 + 模块级函数

```python
from dataclasses import dataclass, asdict, astuple, replace, fields

@dataclass
class InventoryItem:
    name: str
    unit_price: float
    quantity_on_hand: int = 0

    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand

item = InventoryItem("widget", 3.0, 10)
print(item)                          # InventoryItem(name='widget', unit_price=3.0, quantity_on_hand=10)
print(asdict(item))                  # {'name': 'widget', 'unit_price': 3.0, 'quantity_on_hand': 10}
print(astuple(item))                 # ('widget', 3.0, 10)
print(replace(item, quantity_on_hand=25).total_cost())  # 75.0
print([f.name for f in fields(item)])  # ['name', 'unit_price', 'quantity_on_hand']
```

### 示例二：排序、默认工厂与 repr 排除

```python
from dataclasses import dataclass, field

@dataclass(order=True)
class Employee:
    name: str
    salary: float
    tags: list = field(default_factory=list, repr=False)

e1 = Employee("alice", 5000.0)
e2 = Employee("bob", 6000.0)
print(e1 < e2)          # True（按字段顺序比较）
print(e1)               # Employee(name='alice', salary=5000.0)（tags 被排除）
e1.tags.append("dev")   # 各实例拥有独立的 list
print(e2.tags)          # []
```

### 示例三：frozen + slots + InitVar + ClassVar + `__post_init__`

```python
from dataclasses import dataclass, field, InitVar
from typing import ClassVar

@dataclass(frozen=True, slots=True)
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)
    scale: InitVar[float] = 1.0
    kind: ClassVar[str] = "rectangle"

    def __post_init__(self, scale):
        object.__setattr__(self, "area", self.width * self.height * scale)

r = Rectangle(3.0, 4.0, scale=2.0)
print((r.width, r.height, r.area))  # (3.0, 4.0, 24.0)
print(Rectangle.kind)               # rectangle
print(hasattr(r, "__dict__"))       # False（slots 生效）
```

## 12. 版本可用性说明

以官方文档为准，关键里程碑如下：

| 版本 | 变更 |
|---|---|
| 3.7 | 首次引入 `dataclasses` 模块（`@dataclass`、`field()`、`Field`、`InitVar`、`fields()`、`asdict()`、`astuple()`、`make_dataclass()`、`replace()`、`is_dataclass()`、`MISSING`、`FrozenInstanceError` 等原始 API） |
| 3.10 | 新增 `match_args`、`kw_only`、`slots` 参数与 `KW_ONLY` 哨兵、`field()` 的 `kw_only` 参数 |
| 3.11 | 新增 `weakref_slot` 参数；`slots` 不再重复包含基类已有的字段名；可变默认值检测改为"不允许不可哈希对象"（不再针对 `list`/`dict`/`set`） |
| 3.13 | 生成的 `__eq__` 改为逐字段比较（更快，但 `float('nan')` 等边界行为可能变化） |
| 3.14 | `field()` 新增 `doc` 参数；`make_dataclass()` 新增 `decorator` 参数 |

## 13. 注意事项与反模式

- **可变默认值陷阱**：不要写 `x: list = []` 这种默认值。普通 Python 会把默认值存在类属性里，导致所有实例共享同一个可变对象。`@dataclass` 检测到不可哈希（通常即"可变"）的默认值时，会直接抛出 `ValueError`（3.11 起）来拦截这类常见错误。正确做法是用 `field(default_factory=list)`，每次生成全新实例。
- **frozen 下修改会抛异常**：对 `frozen=True` 的实例赋值或 `del` 字段会抛 `FrozenInstanceError`；若有需要，可在 `__post_init__` 内用 `object.__setattr__()` 完成一次性初始化。
- **继承与字段顺序**：字段顺序由逆 MRO 合并决定，子类能覆盖父类同名字段。注意"无默认值字段不能排在"有默认值字段"之后"的规则同样适用于继承累积的结果。
- **entity 性能**：`order=True` 会额外生成四个比较方法；`frozen=True` 有微小性能损耗（用 `object.__setattr__` 初始化）；`slots=True` 可省内存但会返回新类，且与向基类 `__init_subclass__()` 传参冲突。
- **不要用 `__slots__` 或 `__dataclass_fields__` 读字段**：字段名请一律用 `fields()`；`__dataclass_fields__`、`__dataclass_params__` 等是内部属性，勿依赖。
- **`init=False` 字段慎用**：它们不参与 `__init__` 参数，`replace()` 对其行为特殊（不拷贝、在 `__post_init__` 里初始化），建议改用备选构造器或自定义 `replace()`。
- **哈希一致性**：若对象可哈希（`frozen=True`），务必保证其参与哈希的字段不发生变化；不要轻率使用 `unsafe_hash=True`。

## 14. 章节导航

- [上一章：annotationlib](05-annotationlib.md) →
- [下一章：traceback](07-traceback.md) →