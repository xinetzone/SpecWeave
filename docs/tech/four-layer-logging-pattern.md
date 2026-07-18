# 自动化脚本四层日志增强模式

> **模式来源**：基于路径迁移脚本模板 [path-migration-template.py](../../.agents/scripts/templates/path-migration-template.py) 日志增强实战萃取
> **版本**：v1.1
> **日期**：2026-07-18
> **成熟度**：L2（已验证）

---

## 一、核心问题

编写通用自动化脚本模板时，日志往往被当作"锦上添花"的附属功能。但实战表明：

> **可调试性是通用脚本模板的核心质量属性。**
>
> 一个没有详细日志的自动化脚本模板，在面对真实世界的异常（编码问题、权限问题、git状态问题、跨平台差异）时是不可用的。日志不是装饰——它是脚本作者和使用者之间唯一的沟通渠道。

**原始脚本的问题**：
- 只有"正在扫描"、"完成"这类黑盒信息
- git 操作只返回 True/False，丢失所有诊断信息
- 编码错误直接崩溃，无降级重试
- 异常被吞掉，看不到具体原因
- DRY-RUN 只说"would do something"，没有具体信息
- 大段输出没有视觉分隔，找不到当前步骤

---

## 二、五层日志模型

### 2.1 日志级别定义

| 级别 | 值 | 使用场景 | 面向对象 | 内容要求 |
|------|-----|---------|---------|---------|
| **TRACE** | 5 | 最细粒度调试 | 脚本作者 | 每个跳过的目录、每个文件的编码尝试、文件遍历细节 |
| **DEBUG** | 10 | 排查细节 | 开发者/排查者 | 每个文件操作、git命令输出、匹配行内容、进度百分比、前后对比(-/+) |
| **INFO** | 20 | 关键进度节点 | 最终用户 | 开始/完成横幅、汇总统计、成功确认、结果摘要 |
| **WARNING** | 30 | 非阻断问题 | 用户+开发者 | 编码降级、目标已存在、旧路径残留、无内容可提交、非关键文件读取失败 |
| **ERROR** | 40 | 必须处理 | 用户+开发者 | 权限拒绝、新路径不存在、git提交失败、文件写入失败（终止流程） |

### 2.2 日志格式规范

```python
# 推荐格式：时间+级别+函数名+消息
logging.basicConfig(
    level=level,
    format="%(asctime)s [%(levelname)-7s] [%(funcName)-20s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
```

- **`%(levelname)-7s`**：级别左对齐占7位（TRACE/DEBUG/INFO/WARNING/ERROR），视觉整齐
- **`%(funcName)-20s`**：函数名左对齐占20位，快速定位日志来源
- **输出到 stdout**：避免 stderr 和 stdout 交织导致顺序错乱

### 2.3 三级日志粒度控制

实际使用中，应提供三个命令行参数控制日志粒度，避免日志过多或过少：

```python
# 推荐命令行参数设计
parser.add_argument("-v", "--verbose", action="store_true", help="DEBUG级别详细日志")
parser.add_argument("--trace", action="store_true", help="TRACE级别（最细粒度，含目录遍历细节）")
```

级别优先级：TRACE > DEBUG > INFO

| 参数组合 | 日志级别 | 典型使用场景 |
|---------|---------|------------|
| (无参数) | INFO | 日常使用、CI环境、生产运行 |
| `-v` / `--verbose` | DEBUG | 排查问题、查看每个匹配位置、git命令详情 |
| `--trace` | TRACE | 深度调试、排查"为什么某个文件没被扫描到" |

**日志降噪原则**：
- 每目录的跳过信息 → TRACE级别（默认不显示）
- 每文件的匹配发现 → INFO级别（显示"发现N处引用: filename"）
- 匹配的具体行号和内容 → DEBUG级别（-v时显示）
- 扫描进度（每100个文件）→ DEBUG级别
- 每层汇总统计 → INFO级别

---

## 三、必备日志组件

### 3.1 视觉分隔组件

大段日志必须用分隔线划分视觉层次，否则无法快速定位当前步骤：

```python
def log_section(title: str):
    """大阶段分隔（STEP 1/2/3/4/5），使用70个="""
    logger.info("=" * 70)
    logger.info(f"  {title}")
    logger.info("=" * 70)

def log_subsection(title: str):
    """子步骤分隔（如单层扫描、原子提交），使用50个-"""
    logger.info("-" * 50)
    logger.info(f"  {title}")
    logger.info("-" * 50)
```

**启动横幅**必须输出关键配置：
```python
log_section(f"路径迁移脚本启动: {OLD_PATH} -> {NEW_PATH}")
logger.info(f"  迁移名称: {MIGRATION_NAME}")
logger.info(f"  运行模式: {'DRY-RUN（试运行）' if DRY_RUN else 'LIVE（实际执行）'}")
logger.info(f"  日志级别: {'TRACE（最细粒度）' if TRACE else 'DEBUG（详细）' if VERBOSE else 'INFO（标准）'}")
logger.info(f"  项目根目录: {PROJECT_ROOT}")
logger.info(f"  跳过目录: {sorted(SKIP_DIRS)}")
```

### 3.2 扫描类函数日志规范

扫描函数必须在三个时点输出日志：**开始时、过程中、完成时**，异常必须分类处理。

```python
def find_files(exts: Set[str], desc: str = "") -> List[Path]:
    files = []
    skipped_dirs = 0
    for path in PROJECT_ROOT.rglob("*"):
        if path.is_dir():
            if path.name in SKIP_DIRS:
                skipped_dirs += 1
                logger.log(5, f"  [TRACE] 跳过目录: {safe_relpath(path)}")  # TRACE级别
                continue
        elif path.is_file() and path.suffix in exts:
            files.append(path)
    logger.debug(f"  跳过目录数: {skipped_dirs}")
    return files

def scan_layer(name: str, exts: Set[str], patterns: List[re.Pattern]):
    log_subsection(f"扫描层: {name}")           # 开始：明确扫描范围
    start_time = time.time()
    results = {}
    files = find_files(exts, desc=name)
    total_matches = 0
    read_errors = 0

    for idx, f in enumerate(files, 1):
        rel = safe_relpath(f)
        if idx % 100 == 0 or idx == len(files):
            logger.debug(f"  进度: {idx}/{len(files)} ({idx*100//len(files)}%)")  # 过程：进度

        matches = []
        try:
            content = f.read_text(encoding="utf-8")
            for i, line in enumerate(content.splitlines(), 1):
                for pat in patterns:
                    if pat.search(line):
                        matches.append((i, line.strip()))
                        logger.debug(f"    MATCH @ {rel}:{i}: {line.strip()[:100]}")  # 匹配详情
                        break
        except UnicodeDecodeError:
            read_errors += 1
            logger.warning(f"  编码错误(尝试gbk): {rel}")  # 异常1：编码降级
            try:
                content = f.read_text(encoding="gbk", errors="replace")
                # ... gbk重试逻辑
            except Exception as e2:
                logger.error(f"  读取失败 {rel}: {e2}")  # 降级失败才是ERROR
        except PermissionError:
            read_errors += 1
            logger.warning(f"  权限不足(跳过): {rel}")  # 异常2：权限问题（跳过继续）
        except Exception as e:
            read_errors += 1
            logger.warning(f"  读取异常 {rel}: {type(e).__name__}: {e}")  # 异常3：通用

        if matches:
            results[f] = matches
            total_matches += len(matches)
            logger.info(f"  发现{len(matches)}处引用: {rel}")  # 结果：每个有匹配的文件

    elapsed = time.time() - start_time
    logger.info(f"  {name}层完成: {len(results)}文件含旧路径, "  # 完成：汇总统计
                f"{total_matches}处匹配, 读错{read_errors}, 耗时{elapsed:.2f}s")
    return results
```

**关键原则**：
- 每100个文件输出一次进度（避免日志刷屏，同时知道没卡死）
- 每个目录的跳过信息 → TRACE级别（用logger.log(5, ...)）
- 匹配项必须输出**文件:行号:内容片段**（精确定位）
- 编码错误是 WARNING（自动降级），不是 ERROR
- 权限错误是 WARNING（跳过继续），不是 ERROR
- 完成统计必须包含：文件数、匹配数、错误数、耗时

### 3.3 Git操作日志规范

git 操作最容易出问题，必须记录完整上下文：

```python
def run_git(args: List[str], check: bool = False):
    """统一git调用封装，所有git操作必须经过此函数"""
    cmd = ["git"] + args
    logger.debug(f"  GIT: {' '.join(cmd)}")  # 记录完整命令
    start = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=PROJECT_ROOT,
            encoding="utf-8", errors="replace"  # 编码容错
        )
        elapsed = time.time() - start
        if result.stdout.strip():
            logger.debug(f"  git-stdout ({elapsed:.2f}s):\n{result.stdout.strip()}")
        if result.stderr.strip():
            logger.debug(f"  git-stderr ({elapsed:.2f}s):\n{result.stderr.strip()}")
        if check and result.returncode != 0:
            logger.error(f"  git命令失败 (exit={result.returncode}): {' '.join(cmd)}")
        return result
    except FileNotFoundError:
        logger.error("  错误: 未找到git命令，请确保git已安装并在PATH中")
        raise
```

**原子提交必须记录完整生命周期**：

```python
def git_commit(msg: str, files: Optional[List[Path]] = None) -> bool:
    log_subsection(f"原子提交: {msg}")

    if DRY_RUN:
        # DRY-RUN必须模拟具体操作，不能只说"would commit"
        logger.info(f"  [DRY-RUN] 将执行:")
        if files:
            logger.info(f"    git add ({len(files)}个文件)")
            for f in files[:10]:
                logger.info(f"      - {safe_relpath(f)}")
        else:
            logger.info(f"    git add -A")
        logger.info(f"    git commit -m \"{msg}\"")
        return True

    # 1. 提交前状态
    status_before = git_status()
    # 2. add 操作详情
    # 3. 暂存区 diff 预览
    cached = run_git(["diff", "--cached", "--stat"])
    # 4. commit 执行
    commit_result = run_git(["commit", "-m", msg])
    # 5. 结果处理（区分"nothing to commit"和真正失败）
    if "nothing to commit" in stderr:
        logger.warning("  无内容需要提交（可能已包含）")
        return True  # 不是错误
    # 6. 提交后确认
    git_status()
```

**关键原则**：
- stdout 和 stderr **分开记录**（不要混在一起）
- 区分 "nothing to commit"（正常，跳过）和真正的提交失败（ERROR）
- FileNotFoundError（没装git）必须单独捕获并给出明确提示
- DRY-RUN 必须输出具体文件列表，不能只说"would add files"
- 异常必须使用 `exc_info=VERBOSE` 控制是否打印栈追踪

### 3.4 文件操作日志规范

```python
def replace_in_file(fpath: Path, old: str, new: str, dry_run=None):
    rel = safe_relpath(fpath)
    try:
        content = fpath.read_text(encoding="utf-8")
        count = content.count(old)
        if count == 0:
            return False, 0
        logger.debug(f"  {rel}: 发现{count}处匹配")

        # DEBUG模式下输出前后对比（diff风格）
        if VERBOSE and count <= 5:
            for i, line in enumerate(content.splitlines(), 1):
                if old in line:
                    logger.debug(f"    L{i}(-): {line.strip()[:80]}")
                    logger.debug(f"    L{i}(+): {line.replace(old, new).strip()[:80]}")

        if not dry_run:
            fpath.write_text(content.replace(old, new), encoding="utf-8")
        return True, count
    except UnicodeDecodeError:
        logger.warning(f"  编码错误(gbk重试): {rel}")
        # ... gbk降级逻辑
    except PermissionError:
        logger.error(f"  权限不足，无法写入: {rel}")
        return False, 0
```

### 3.5 Result结果对象

每个步骤必须返回结构化结果，而不是零散的日志：

```python
@dataclass
class Result:
    step: str
    modified: List[Path] = field(default_factory=list)
    moved: List[Tuple[Path, Path]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration: float = 0.0
    success: bool = True

    def summary(self) -> str:
        """单行摘要，用于进度输出"""
        status = "OK" if self.success else "FAIL"
        return (f"[{self.step}] {status} "
                f"Modified:{len(self.modified)} Moved:{len(self.moved)} "
                f"Warn:{len(self.warnings)} Err:{len(self.errors)} "
                f"Time:{self.duration:.2f}s")

    def detail(self) -> str:
        """多行详情，用于步骤完成时输出"""
        lines = [self.summary()]
        if self.modified:
            lines.append("  修改的文件:")
            for f in self.modified[:10]:
                lines.append(f"    - {safe_relpath(f)}")
            if len(self.modified) > 10:
                lines.append(f"    ... 还有{len(self.modified)-10}个文件")
        # ... moved/warnings/errors 同理
        return "\n".join(lines)
```

**最终汇总**在main()末尾输出所有步骤的摘要：

```python
log_section("迁移完成汇总")
logger.info(f"  总耗时: {total_elapsed:.2f}s")
for r in results:
    logger.info(f"    {r.summary()}")
```

### 3.6 推荐默认排除目录

文件扫描脚本必须默认排除以下目录，否则会扫描备份/缓存/构建产物/外部依赖，导致：
- 扫描速度慢数倍（从17秒变64秒的实测数据）
- 匹配到不应修改的历史备份文件
- 匹配到node_modules等第三方依赖

```python
SKIP_DIRS = {
    # 版本控制
    ".git", ".gitcode",
    # Python缓存
    "__pycache__", ".pytest_cache", ".mypy_cache", ".tox", "*.egg-info",
    # 虚拟环境
    ".venv", "venv",
    # Node.js
    "node_modules",
    # 构建产物
    "_build", "build", "dist",
    # IDE配置
    ".idea", ".vscode",
    # 外部依赖和备份
    "vendor", "external", ".temp",
}
```

**实测性能对比**（以SpecWeave项目为例）：
- 未排除备份/外部目录：扫描10277文件，耗时64秒，匹配到.temp/backup中的历史文件
- 排除后：扫描10277文件（实际有效文件），耗时17秒，无历史文件干扰
- **性能提升：73%**

**启动时必须显示当前跳过目录列表**，让用户知道哪些目录被排除了。

---

## 四、DRY-RUN 一致性原则

DRY-RUN 模式最容易被敷衍——只打印 "would do something" 而不模拟具体操作。正确的 DRY-RUN 必须：

1. **走完全相同的代码路径**（包括所有扫描、检查、统计）
2. **只在真正写入/commit的最后一步跳过**
3. **输出足够具体**（文件列表、替换次数、移动映射）
4. **可以用来验证操作影响范围**（用户看完DRY-RUN输出后，应该能准确知道LIVE模式会做什么）

```python
# ✅ 正确的DRY-RUN
if DRY_RUN:
    logger.info(f"  [DRY-RUN] 将移动: {old_toml} -> {new_toml}")
    logger.info(f"  [DRY-RUN] 将更新{count}处引用")
else:
    shutil.move(str(old_toml), str(new_toml))
    fpath.write_text(new_content, encoding="utf-8")

# ❌ 错误的DRY-RUN
if not DRY_RUN:
    shutil.move(...)
    # 没有任何输出说明将要做什么
```

---

## 五、命令行参数规范

通用脚本模板必须支持以下参数：

```python
parser.add_argument("--dry-run", action="store_true", help="试运行模式，不实际修改文件或提交")
parser.add_argument("-v", "--verbose", action="store_true", help="DEBUG级别详细日志")
parser.add_argument("--trace", action="store_true", help="TRACE级别（最细粒度，含目录遍历细节）")
parser.add_argument("--scan-only", action="store_true", help="只执行扫描，不执行迁移步骤")
parser.add_argument("--no-commit", action="store_true", help="执行修改但不进行git提交")
```

| 参数 | 用途 |
|------|------|
| `--scan-only` | 第一步用！先看影响范围，再决定是否执行 |
| `--dry-run` | 预览完整流程，确认每个步骤正确 |
| `--dry-run -v` | 预览+详细输出，看到每个文件的修改 |
| `--dry-run --trace` | 预览+最细粒度日志，排查为什么文件没被扫描到 |
| (无参数) | 实际执行，INFO级别日志 |
| `-v` | 实际执行+DEBUG详细日志，排查问题用 |
| `--trace` | 实际执行+TRACE最细粒度日志，深度调试用 |
| `--no-commit` | 修改文件但手动提交（分步调试用） |

**推荐使用顺序**：`--scan-only` → `--dry-run -v` → `--dry-run` → LIVE

---

## 六、反模式（禁止）

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| 只返回 True/False 的 git_commit() | 丢失所有诊断信息，"nothing to commit"和"合并冲突"表现一样 | 返回bool+输出完整stdout/stderr+分类处理异常 |
| 只说"扫描完成"不说统计数据 | 用户不知道是扫描了10个文件还是10000个，找不到问题 | 输出目录数/文件数/匹配数/错误数/耗时 |
| 编码错误直接崩溃 | Windows环境大量GBK文件，UTF-8读取失败就会中断 | 自动降级GBK重试，记录WARNING |
| catch Exception 但不 print | 异常被吞掉，完全不知道发生了什么 | 至少记录异常类型+消息，VERBOSE时打印栈 |
| DRY-RUN 只打一行"would run" | 无法用DRY-RUN验证正确性 | 输出具体文件列表和操作数量 |
| 大段日志无分隔线 | 几千行日志里找不到当前在执行哪一步 | 使用====和----分隔大/小阶段 |
| stderr和stdout交织 | subprocess用capture_output但不分开打印，顺序混乱 | stdout/stderr分开记录，或统一输出到stdout |
| 进度完全没有输出 | 处理1000个文件时长时间无输出，用户以为卡死了 | 每100个文件输出一次进度百分比 |
| 跳过目录的日志用DEBUG级别 | 大项目中跳过成百上千个目录，DEBUG模式下日志刷屏，关键信息被淹没 | 将每个目录的跳过日志降级到TRACE，只在汇总时输出跳过目录总数 |

---

## 七、可复用代码速查

### 7.1 最小可复用模板骨架

```python
#!/usr/bin/env python3
import argparse, logging, sys, time
from pathlib import Path

TRACE = 5
logging.addLevelName(TRACE, "TRACE")

def setup_logging(verbose=False, trace=False):
    if trace:
        level = TRACE
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)-7s] [%(funcName)-20s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
logger = logging.getLogger(__name__)

SKIP_DIRS = {
    ".git", ".gitcode",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".tox", "*.egg-info",
    ".venv", "venv",
    "node_modules",
    "_build", "build", "dist",
    ".idea", ".vscode",
    "vendor", "external", ".temp",
}

def log_section(t):
    logger.info("="*70); logger.info(f"  {t}"); logger.info("="*70)
def log_subsection(t):
    logger.info("-"*50); logger.info(f"  {t}"); logger.info("-"*50)
def safe_relpath(p):
    try: return str(p.relative_to(Path.cwd()))
    except ValueError: return str(p)

def find_files(exts):
    files = []
    skipped = 0
    for path in Path.cwd().rglob("*"):
        if path.is_dir():
            if path.name in SKIP_DIRS:
                skipped += 1
                logger.log(TRACE, f"  跳过目录: {safe_relpath(path)}")
                continue
        elif path.is_file() and path.suffix in exts:
            files.append(path)
    logger.debug(f"  跳过目录: {skipped}个")
    return files

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--trace", action="store_true")
    args = parser.parse_args()
    setup_logging(args.verbose, args.trace)
    log_section("脚本启动")
    logger.info(f"  跳过目录: {sorted(SKIP_DIRS)}")
    # ... 业务逻辑 ...
    logger.info("完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 7.2 完整参考实现

完整日志增强的实际示例参见：
- [path-migration-template.py](../../.agents/scripts/templates/path-migration-template.py) - 路径迁移脚本模板（本模式的完整实现）

---

## 八、检查清单

编写或审查自动化脚本时，用此清单验证日志质量：

- [ ] **格式**：日志格式包含时间、级别、函数名
- [ ] **横幅**：启动时输出关键配置（路径、模式、参数）
- [ ] **分隔**：大阶段用`=====`、子步骤用`-----`
- [ ] **默认排除**：SKIP_DIRS包含.git/__pycache__/node_modules/vendor/.venv/.temp/external/_build/build/dist等常见无关目录
- [ ] **日志粒度**：提供--verbose/-v(DEBUG)和--trace(TRACE)两级调试参数，避免日志刷屏
- [ ] **启动信息**：启动时显示当前跳过目录列表
- [ ] **扫描**：开始(范围)→过程(进度)→完成(统计：文件/匹配/错误/耗时)
- [ ] **匹配**：每个匹配项输出`文件:行号:内容片段`
- [ ] **编码**：UTF-8失败自动降级GBK，记录WARNING
- [ ] **git**：stdout/stderr分开记录，区分"nothing to commit"和真正失败
- [ ] **异常**：分类捕获（FileNotFoundError/PermissionError/UnicodeDecodeError/通用Exception）
- [ ] **DRY-RUN**：输出具体操作（文件列表、数量），不是泛泛的"would run"
- [ ] **结果**：每个步骤返回结构化Result对象，包含modified/moved/errors/warnings/duration
- [ ] **汇总**：结束时输出所有步骤的摘要表
- [ ] **进度**：大批量操作每N个文件输出一次进度百分比
- [ ] **对比**：DEBUG模式下输出替换前后内容（-/+风格）

---

## 九、总结

**一句话原则**：

> 通用脚本模板的日志不是附属功能，而是产品本身。
>
> 当用户在陌生环境运行你的模板遇到问题时，日志就是你和用户之间唯一的沟通渠道。
>
> 黑盒脚本在真实世界里是不可用的——可调试性是模板的第一质量属性。

**记住**：用户看到的第一条报错信息，决定了他们能否在5分钟内自己解决问题，还是需要花1小时找脚本作者求助。好的日志能把"求助邮件"变成"哦原来如此，我自己解决了"。
