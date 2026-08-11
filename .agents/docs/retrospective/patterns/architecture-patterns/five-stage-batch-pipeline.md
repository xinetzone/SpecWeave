---
id: "five-stage-batch-pipeline"
source: "../../reports/feature-development/retrospective-skill-auto-loader-20260807.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/architecture-patterns/five-stage-batch-pipeline.toml"
---
# 批量处理五步管道模式（Five-Stage Batch Pipeline）

## 模式类型
架构模式

## 成熟度
L2 已验证（3个案例：skill-auto-loader、prompt_extraction Pipeline、check_skill_quality）

## 适用场景
开发需要批量处理文件/记录/条目并生成结构化报告的CLI工具或脚本，特别是：
- 代码质量检查工具（linter、格式验证器、规范检查器）
- 文件系统扫描器（技能索引、文档索引、资源发现）
- 数据ETL管道（提取→转换→加载→验证→导出）
- 批量内容处理器（提示词萃取、文档转换、批量分析）
- CI/CD 检查脚本（链接检查、敏感信息检测、格式校验）

**适用条件**：
- 输入是一批同构或半同构的项目（文件、记录、条目）
- 每个项目需要经过多个处理阶段
- 单个项目的失败不应中断整体流程
- 需要聚合统计和生成汇总报告
- 处理成本较高，需要缓存机制加速二次运行

## 问题背景

批量处理脚本最常见的失败模式有：

1. **一损俱损**：一个文件解析失败导致整个脚本崩溃，用户拿不到任何结果
2. **阶段耦合**：发现、解析、验证、输出逻辑混杂在一个大函数中，难以测试和扩展
3. **重复计算**：每次运行都重新处理所有项目，即使99%的文件没有变更
4. **错误丢失**：出错时只打印异常堆栈，无法生成结构化的错误清单
5. **输出单一**：只有人类可读的控制台输出，没有机器可读格式供下游工具消费

## 核心设计

将批量处理系统分解为五个正交阶段，每个阶段职责单一、可独立测试：

```
┌─────────────────────────────────────────────────────────────────┐
│                        Five-Stage Pipeline                       │
├──────────┬──────────┬──────────┬──────────┬──────────────────────┤
│ Discover │  Parse   │ Validate │  Cache   │       Report         │
│  (发现)  │  (解析)  │  (验证)  │  (缓存)  │       (报告)         │
├──────────┴──────────┴──────────┴──────────┴──────────────────────┤
│  输入：根路径/配置       输出：结构化结果 + 错误清单 + 统计摘要    │
└─────────────────────────────────────────────────────────────────┘
```

### 五阶段职责定义

| 阶段 | 职责 | 输入 | 输出 | 关键特性 |
|------|------|------|------|---------|
| **Discover（发现）** | 定位所有待处理项目 | 根路径、配置选项 | 项目位置列表（Path/ID） | 递归搜索、模板排除、跳过列表 |
| **Parse（解析）** | 将原始项目转换为结构化数据 | 项目位置 | 领域模型对象 | 复用现有解析器、原始元数据保留 |
| **Validate（验证）** | 检查结构化数据的质量和合规性 | 领域模型对象 | 带状态标记的对象+问题列表 | 多模式（strict/relaxed）、错误隔离 |
| **Cache（缓存）** | 增量跳过未变更项目 | 项目位置+元数据 | 缓存命中/未命中决策 | mtime+size快速判断、--force强制刷新 |
| **Report（报告）** | 聚合结果并生成多格式输出 | 所有处理结果 | JSON（机器）+ Markdown（人类） | 按维度分组、错误清单、统计摘要 |

### 数据模型三要素

```python
# 1. 单个项目的处理结果
@dataclass
class ItemResult:
    id: str              # 项目唯一标识（路径/名称）
    status: Status       # OK / WARNING / ERROR
    issues: list[str]    # 问题描述列表
    raw_metadata: dict   # 完整原始数据（保留溯源能力）
    
# 2. 错误记录（不抛出异常，而是收集）
@dataclass
class ProcessingError:
    item_id: str
    error_type: str      # parse_error / missing_field / encoding_error
    message: str
    suggestion: str = ""

# 3. 整体结果容器
@dataclass
class BatchResult:
    items: list[ItemResult]
    errors: list[ProcessingError]
    stats: dict          # {total, ok, warning, error, conflicts}
    scan_time: str       # ISO时间戳
```

### 错误隔离模式（核心）

每个项目的处理必须用 try/except 包裹，**失败的项目记录到errors列表，不中断循环**：

```python
def process_all(items: list[Path]) -> BatchResult:
    result = BatchResult()
    for item_path in items:
        try:
            parsed = parse_item(item_path)
            validated = validate_item(parsed, mode="strict")
            result.items.append(validated)
        except Exception as e:
            # 不raise，记录错误继续
            result.errors.append(ProcessingError(
                item_id=str(item_path),
                error_type=type(e).__name__,
                message=str(e),
                suggestion=get_suggestion(e),
            ))
    result.stats = compute_stats(result)
    return result
```

### 增量缓存模式

使用文件元数据（mtime + size）快速判断是否需要重新处理，避免全量重算：

```python
def should_reprocess(file_path: Path, cached_entry: dict) -> bool:
    """mtime和size都一致时命中缓存，否则重新处理"""
    stat = file_path.stat()
    return (abs(stat.st_mtime - cached_entry["mtime"]) > 1 
            or stat.st_size != cached_entry["size"])
```

**缓存三要素**：
- **缓存位置**：工具目录下的隐藏文件（如 `.scan-cache.json`）
- **失效判断**：mtime + size 双因素比较（允许1秒mtime误差）
- **绕过机制**：`--force`/`--no-cache` 参数强制全量重扫

### 双模式验证

| 模式 | 必填检查 | 推荐检查 | 适用场景 |
|------|---------|---------|---------|
| **strict** | 核心字段完整性 | 推荐章节/格式规范 | 自有资产、CI门禁、官方标准 |
| **relaxed** | 核心字段完整性 | 不检查 | 第三方资产、快速扫描、探索性分析 |

### 双格式输出

| 格式 | 目标受众 | 用途 | 关键要求 |
|------|---------|------|---------|
| **JSON** | 机器/下游工具 | CI集成、自动化处理、数据分析 | 完整结构化数据，可json.load() |
| **Markdown** | 人类开发者 | 阅读、审查、归档 | 按维度分组、状态图标、表格对齐 |

## 代码结构模板

```
my_tool/
├── SKILL.md           # 技能门面（如作为Skill）
├── .gitignore         # 排除缓存和派生产物
├── scripts/
│   ├── __init__.py
│   ├── models.py      # 数据模型（ItemResult/ProcessingError/BatchResult）
│   ├── discovery.py   # Discover阶段
│   ├── parser.py      # Parse + Validate阶段
│   ├── cache.py       # Cache阶段
│   ├── report.py      # Report阶段
│   └── cli.py         # CLI入口（Typer），编排以上模块
├── tests/
│   ├── __init__.py
│   ├── conftest.py    # 测试配置（sys.path处理等）
│   └── test_*.py      # 各模块单元测试
└── reports/           # 输出目录（.gitignore排除）
    ├── result.json
    └── result.md
```

### CLI参数设计规范

```
--project-root / -r PATH    项目根路径（默认自动检测）
--extra-dir / -d PATH       追加处理目录（可多次指定）
--mode / -m MODE            验证模式：strict（默认）| relaxed
--no-cache                  禁用增量缓存
--force / -f                强制全量重处理（等价--no-cache）
--output / -o FILE          输出文件路径
--format / -fmt FMT         输出格式：json | markdown | both（默认both）
--verbose / -v              详细日志
--version                   版本号
```

### Exit Code 规范

| Code | 含义 |
|------|------|
| 0 | 成功（有warning但无error） |
| 1 | 存在error级别的问题 |
| 2 | 参数错误（无效选项、路径不存在等） |

## 案例对照

| 阶段 | 案例1：skill-auto-loader | 案例2：prompt_extraction | 案例3：check_skill_quality |
|------|-------------------------|-------------------------|---------------------------|
| Discover | rglob("SKILL.md") | 文件解析为record列表 | rglob("SKILL.md") |
| Parse | frontmatter解析 | 文本清洗+标准化 | frontmatter解析 |
| Validate | name必填+推荐章节检查 | 质量评分阈值 | 多维度checks（frontmatter/description/content） |
| Cache | mtime+size增量缓存 | 无（数据集每次不同） | 无（检查需实时性） |
| Report | JSON+Markdown技能索引 | CSV导出+DataFrame | JSON+控制台表格 |

## 反模式警示

| 反模式 | 后果 | 正确做法 |
|--------|------|---------|
| **一损俱损**：不用try/except隔离单个项目 | 一个坏文件导致整个批处理崩溃，用户拿不到结果 | 逐项目try/except，失败记录到errors列表 |
| **大泥球**：所有逻辑写在一个main()函数中 | 无法单元测试、难以扩展、代码不可读 | 按五阶段拆分模块，每个模块单一职责 |
| **git add .**：提交缓存和报告文件 | 缓存文件污染版本控制、派生产物造成diff噪音 | 创建.gitignore排除缓存和reports/ |
| **全量重算**：每次都重新处理所有项目 | 30个文件1秒→3000个文件100秒，二次运行无加速 | 基于mtime+size的增量缓存 |
| **仅控制台输出**：只有print没有结构化输出 | 下游工具无法消费结果、无法自动化集成 | 同时输出JSON（机器）和Markdown（人类） |
| **异常吞噬**：except Exception: pass 不记录 | 静默失败，用户不知道有多少项目出错 | 记录到errors列表，最终汇总报告 |
| **裸raise**：自定义异常不携带修复建议 | 用户看到错误不知道怎么修 | ProcessingError携带suggestion字段 |
| **relative import冲突**：脚本与项目lib同名模块冲突 | ImportError、加载错误模块 | 使用importlib预加载到sys.modules |
| **git add .** 提交时用通配符add | 临时文件、调试代码混入提交 | 原子提交：显式指定每个文件，禁止git add . |

## 效果数据

skill-auto-loader 采用本模式后：
| 指标 | 数值 |
|------|------|
| 首次扫描 | 31个技能全量解析，<2秒 |
| 二次扫描（缓存命中） | 31/31命中，<0.5秒 |
| 错误隔离 | 0个崩溃（即使构造坏文件也能正常产出报告） |
| 测试覆盖率 | 20个测试覆盖6大模块 |
| 代码复用 | parser复用lib/frontmatter.py，零新增第三方依赖 |

## 检查清单

### 架构层面
- [ ] 处理流程是否按五阶段拆分（发现/解析/验证/缓存/报告）？
- [ ] 每个阶段是否封装在独立模块中，可独立单元测试？
- [ ] 是否有清晰的数据模型（ItemResult/ProcessingError/BatchResult）？

### 错误处理
- [ ] 单个项目处理是否用try/except隔离？
- [ ] 异常是否携带错误类型、消息和修复建议？
- [ ] 最终报告是否包含完整的错误清单？

### 性能
- [ ] 是否有增量缓存机制加速二次运行？
- [ ] 缓存文件是否在.gitignore中？
- [ ] 是否有--force/--no-cache参数绕过缓存？

### 输出
- [ ] 是否同时提供机器可读（JSON）和人类可读（Markdown）输出？
- [ ] Markdown报告是否按有意义的维度分组？
- [ ] 是否有统计摘要（总数/成功/警告/失败）？

### CLI
- [ ] 是否有--help输出完整帮助？
- [ ] Exit code是否符合规范（0成功/1有错误/2参数错误）？
- [ ] Windows平台是否处理了中文编码问题？

### 提交
- [ ] 提交时是否显式git add每个文件，禁止git add .？
- [ ] 提交信息是否遵循Conventional Commits规范？

## 与现有模式的关系

- `periodic-check-caching.md`：本模式中Cache阶段的具体实现策略参考该模式
- `cli-as-api-design.md`：CLI参数设计应遵循CLI即API的设计原则
- `script-json-output-contract.md`：JSON输出格式应遵循结构化输出契约
- `three-layer-test-validation.md`：测试策略参考三层验证方法
- `preflight-checks-script.md`：Discover阶段可参考预检脚本的发现逻辑
- `exception-precision-guards.md`：错误处理阶段参考精确异常守卫模式

## 迁移验证记录

本模式从以下三个独立案例中萃取，已在不同场景验证可复用性：

1. **skill-auto-loader**（技能扫描）：文件系统批量扫描场景，验证五阶段拆分有效性
2. **prompt_extraction Pipeline**（NLP批处理）：数据记录批量处理场景，验证错误隔离和阶段解耦
3. **check_skill_quality**（代码质量检查）：代码检查工具场景，验证多维度验证和报告生成

## Changelog

- **v1.0.0** (2026-08-07): 初始版本，基于skill-auto-loader、prompt_extraction、check_skill_quality三案例萃取
