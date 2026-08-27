---
id: "jupyter-three-tier-backend"
title: "三层后端编排架构"
source: "README.md#三层后端编排架构"
---
# 三层后端编排架构

为了最大化兼容性和用户体验，所有invoke命令采用三层后端自动降级架构，根据宿主机环境自动选择最优后端。

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    invoke 任务层                         │
│  build / run / stop / shell / exec / model.push/...     │
└─────────────────────┬───────────────────────────────────┘
                      │ 自动检测可用后端
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Tier 1: podman-compose 后端（优先）                     │
│  通过声明式 YAML 管理服务生命周期                         │
│  支持 compose.yaml 多文件覆盖、profiles、环境变量         │
└─────────────────────┬───────────────────────────────────┘
                      │ 降级（podman-compose 未安装）
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Tier 2: podman-py SDK 后端                              │
│  通过 Podman Unix socket 直接调用 API                    │
│  比 CLI 更高效，支持流式输出、事件监听                    │
└─────────────────────┬───────────────────────────────────┘
                      │ 降级（podman-py 未安装）
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Tier 3: CLI fallback（保底）                            │
│  通过 subprocess 调用 podman/docker 命令                 │
│  零依赖，任何有 podman/docker 的环境都能工作              │
└─────────────────────────────────────────────────────────┘
```

后端选择对用户完全透明——同一 `invoke` 命令根据宿主机环境自动选择最优后端。

## Tier 1: podman-compose 后端（优先）

**触发条件**：`podman-compose` Python包已安装

**实现文件**：`tasks/compose_backend.py`

**优势**：
- 声明式YAML配置，与`podman-compose up/down`命令行为一致
- 自动支持多文件覆盖（`-f compose.yaml -f compose.dev.yaml`）
- 自动支持profiles（`--profile registry`启动model-registry）
- 环境变量从.env文件自动加载
- 与直接使用podman-compose命令体验一致

**使用场景**：
- 用户已安装podman-compose（推荐安装方式：`pip install -e ".[compose]"`）
- 复杂编排场景（多服务、profiles、多文件覆盖）
- 需要使用compose.dev.yaml透传配置

**工作原理**：
```python
# 通过subprocess调用podman-compose命令
subprocess.run(["podman-compose", "-f", "compose.yaml", "up", "-d", "--build"])
```

## Tier 2: podman-py SDK 后端

**触发条件**：`podman` Python包（podman-py SDK）已安装，且podman-compose未安装

**实现文件**：通过client.py封装podman SDK调用

**优势**：
- 直接通过Unix socket调用Podman API，比CLI更高效
- 支持流式日志输出（实时查看容器日志）
- 支持事件监听（容器状态变化）
- 编程式控制，更灵活

**使用场景**：
- 用户安装了完整版本：`pip install -e ".[full]"`
- 需要高级API功能（事件监听、流式输出）
- 单容器简单场景

**工作原理**：
```python
import podman
client = podman.PodmanClient(base_url="unix:///run/podman/podman.sock")
container = client.containers.run(image, name=name, ports=ports, detach=True)
```

## Tier 3: CLI fallback（保底）

**触发条件**：podman-compose和podman-py都未安装，但系统PATH中有podman或docker命令

**实现**：通过subprocess直接调用podman/docker CLI命令

**优势**：
- **零额外Python依赖**，只要安装了podman/docker就能工作
- 最通用的方式，兼容所有Podman/Docker版本
- 适合快速体验、CI环境等不想安装额外依赖的场景

**使用场景**：
- 基础安装：`pip install -e .`
- 快速体验，不想安装podman-compose/podman-py
- CI/CD环境最小依赖

**工作原理**：
```python
import subprocess
subprocess.run(["podman", "build", "-t", tag, "."])
subprocess.run(["podman", "run", "-d", "--name", name, "-p", "2222:22", tag])
```

## 后端自动检测逻辑

client.py中的检测逻辑：

```python
def get_client():
    # Tier 1: 检查podman-compose是否可用
    if is_podman_compose_available():
        return ComposeBackend()
    
    # Tier 2: 检查podman-py SDK是否可用
    if is_podman_py_available():
        return PodmanPyBackend()
    
    # Tier 3: 检查CLI是否可用
    runtime = detect_runtime()  # "podman" or "docker"
    if runtime:
        return CLIBackend(runtime)
    
    # 都不可用，抛出友好错误
    raise RuntimeError(
        "Neither podman-compose, podman-py, nor podman/docker found. "
        "Please install Podman or Docker, or run: pip install -e '.[compose]'"
    )
```

## 后端透明性保证

所有后端实现统一的接口，确保同一命令行为一致：

```python
class ContainerBackend(ABC):
    @abstractmethod
    def build(self, tag: str, build_args: dict, no_cache: bool = False): ...
    
    @abstractmethod
    def run(self, name: str, tag: str, ports: dict, volumes: list, 
            environment: dict, detach: bool = True): ...
    
    @abstractmethod
    def stop(self, name: str): ...
    
    @abstractmethod
    def status(self, name: str) -> dict: ...
    
    @abstractmethod
    def exec(self, name: str, command: str, user: str = "devuser"): ...
    
    @abstractmethod
    def logs(self, name: str, follow: bool = False, tail: int = 100): ...
    
    @abstractmethod
    def shell(self, name: str, user: str = "devuser"): ...
    
    @abstractmethod
    def clean(self, name: str, tag: str = None, volume: bool = False, image: bool = False): ...
```

## WSL2 路径自动转换

所有后端都通过`utils.to_posix_path()`自动处理WSL2路径转换：
- Windows路径（`D:\project`）自动转换为WSL2路径（`/mnt/d/project`）
- 自动检测是否在WSL2环境
- 非WSL2环境直接返回原路径

```python
def to_posix_path(path: str) -> str:
    """Convert Windows path to WSL2 POSIX path if in WSL2 environment."""
    if not is_wsl2():
        return path
    # D:\project → /mnt/d/project
    ...
```

## ML命令的三层后端

`invoke model.*`命令同样遵循三层后端架构：
1. 优先通过podman-compose exec进入容器调用omlmd/olot
2. 其次通过podman-py SDK exec
3. CLI fallback通过podman exec
4. 如果容器未运行，尝试在宿主机直接调用omlmd/olot

Invoke任务开发规范详见 [.agents/rules/invoke-tasks.md](../.agents/rules/invoke-tasks.md)。
