---
id: "content-hash-build-cache"
source: "external: 已迁移-.agents/insights/packaging/notebook-nuitka-build-retrospective-20260704.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/code-patterns/content-hash-build-cache.toml"
---
# 内容哈希构建缓存：基于源码版本的智能构建跳过

## 模式概述

对耗时长的构建步骤，用**内容哈希**（而非时间戳）判断是否需要重新构建。源码未变化时直接跳过，源码变化时强制重建，比基于时间戳的缓存更可靠。

## 问题现象

构建加速常见的时间戳缓存方案有以下问题：

1. **误跳过**：文件系统 clock skew、文件复制导致时间戳变化，不该跳的跳了
2. **误重编**：touch 一下文件但内容没变，时间戳更新导致重新构建
3. **跨平台不可靠**：不同操作系统/文件系统的时间戳精度和语义不一致
4. **团队环境不一致**：每个人的构建时间戳不同，缓存无法共享

## 解决方案

用 git HEAD 哈希 + 镜像名 + 路径生成缓存键，判断构建是否有效：

```python
import hashlib
import subprocess
from pathlib import Path

def _get_git_head(host_path: Path) -> str:
    """获取 git HEAD 哈希。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(host_path),
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""

def _get_cache_key(host_path: Path, image: str) -> str:
    """生成构建缓存键，基于源码 git HEAD 和镜像名。"""
    git_head = _get_git_head(host_path)
    key_str = f"{host_path}:{image}:{git_head}"
    return hashlib.sha256(key_str.encode()).hexdigest()[:16]

def _is_cached(host_path: Path, image: str, artifact: str,
               cache_file: Path) -> bool:
    """检查构建是否已缓存且有效。"""
    if not (host_path / artifact).exists():
        return False
    if not cache_file.exists():
        return False
    old_hash = cache_file.read_text().strip()
    new_hash = _get_cache_key(host_path, image)
    return old_hash == new_hash

def _save_cache(host_path: Path, image: str, cache_file: Path) -> None:
    """保存构建缓存。"""
    cache_hash = _get_cache_key(host_path, image)
    cache_file.write_text(cache_hash)
```

## 使用方式

```python
CACHE_FILE = Path(".build_cache.hash")
ARTIFACT = "build/liboutput.so"

def build(host_path: Path, image: str, force: bool = False):
    if not force and _is_cached(host_path, image, ARTIFACT, CACHE_FILE):
        print("[Build] 缓存命中，跳过构建")
        return

    # 执行构建...
    run_build(host_path, image)

    _save_cache(host_path, image, CACHE_FILE)
    print("[Build] 构建完成，缓存已更新")
```

## 缓存键组成

```
cache_key = SHA256(路径:镜像名:git_head)[:16]
```

| 组成部分 | 作用 |
|---------|------|
| **路径** | 区分不同项目/目录 |
| **镜像名** | 区分不同构建环境 |
| **git HEAD** | 检测源码变化 |
| **SHA256 + 截断** | 哈希缩短为 16 字符，足够唯一 |

## 内容哈希 vs 时间戳

| 维度 | 时间戳缓存 | 内容哈希缓存 |
|------|-----------|-------------|
| **可靠性** | 低（文件系统差异大） | 高（内容没变就不重编） |
| **误报率** | 高（touch/复制都触发） | 低（只认内容变化） |
| **跨平台** | 差（各 FS 语义不同） | 好（哈希算法一致） |
| **实现成本** | 低 | 中 |
| **git 依赖** | 无 | 需要 git 仓库 |

## 变体与扩展

### 变体 A：文件内容哈希（非 git 项目）

如果项目不在 git 中，可以对关键源文件算哈希：

```python
import hashlib

def _dir_hash(path: Path, pattern: str = "*.c") -> str:
    """对目录下匹配的文件内容算哈希。"""
    hasher = hashlib.sha256()
    for f in sorted(path.rglob(pattern)):
        hasher.update(f.read_bytes())
    return hasher.hexdigest()[:16]
```

### 变体 B：多级缓存（多粒度）

对不同构建层级分别缓存：

```
源码哈希 → CMake 配置缓存 → Make 编译缓存 → 打包缓存
```

每一层有独立的缓存键，细粒度跳过。

### 变体 C：远程共享缓存

将构建产物和缓存键上传到共享存储（S3/Artifactory），团队成员共享：

```
构建前：检查远程是否有匹配 cache_key 的产物
       ↓ 有 → 下载并跳过构建
       ↓ 无 → 本地构建后上传
```

## 适用场景

- 编译构建（CMake/Make/Nuitka 等耗时步骤）
- 数据处理管道（E.T.L. 的中间结果缓存）
- 模型训练（数据预处理、特征工程缓存）
- 任何"输入不变则输出不变"的幂等操作

## 注意事项

1. **产物存在性检查**：哈希匹配 + 产物文件存在，两者都满足才跳过
2. **force 参数**：提供 `--force` 选项强制重新构建
3. **非 git 回退**：git 命令失败时返回空字符串，缓存会失效（保守策略）
4. **哈希碰撞**：16 字符 hex 足够日常使用，安全敏感场景用全 64 字符
5. **配置变更**：如果构建配置影响结果，配置也应纳入缓存键

## 正反例

### 正例

```python
# ✅ 内容哈希 + 产物检查，双重保险
if not force and _is_cached(host_path, image, ARTIFACT, CACHE_FILE):
    print("缓存命中，跳过")
    return
```

### 反例

```python
# ❌ 只用时间戳，不可靠
if (build_dir / "output.so").stat().st_mtime > (src_dir / "main.c").stat().st_mtime:
    print("最新的，跳过")  # 可能因 clock skew 误判
```
