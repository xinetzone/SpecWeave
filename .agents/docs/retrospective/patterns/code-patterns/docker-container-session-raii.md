---
id: "docker-container-session-raii"
source: "external: 已迁移-.agents/insights/packaging/notebook-nuitka-build-retrospective-20260704.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/docker-container-session-raii.toml"
---
# Docker 容器会话 RAII 模式：上下文管理器封装容器生命周期

## 模式概述

需要在 Docker 容器内执行多步操作时，使用上下文管理器（context manager）封装容器的创建、使用和清理，确保异常情况下资源也能正确释放。

## 问题现象

直接使用 `subprocess` 调用 `docker run` / `docker exec` 时，常见问题：

1. **资源泄漏**：脚本异常退出时，容器未被 `docker rm` 清理
2. **多步操作繁琐**：每步操作都要手动拼接 `docker exec` 命令
3. **失败难以调试**：`docker run --rm` 一步执行失败时，容器已销毁无法排查
4. **残留容器冲突**：同名容器残留导致下次启动失败

## 解决方案

使用上下文管理器模式封装 Docker 容器生命周期：

```python
import subprocess
from pathlib import Path

class DockerRunError(RuntimeError):
    """Docker 容器执行失败。"""

class DockerContainerSession:
    """通过 docker CLI 管理一个短生命周期构建容器。"""

    def __init__(
        self,
        *,
        host_path: Path,
        image: str,
        name: str,
        target: str,
        working_dir: str,
        network_mode: str = "host",
    ) -> None:
        self.host_path = host_path
        self.image = image
        self.name = name
        self.target = target
        self.working_dir = working_dir
        self.network_mode = network_mode
        self.started = False

    def __enter__(self) -> "DockerContainerSession":
        self._remove_container(self.name)  # 清理残留

        command = [
            "docker", "run",
            "-d", "--rm",
            "--name", self.name,
            "-v", f"{self.host_path}:{self.target}",
            "-w", self.working_dir,
        ]
        if self.network_mode:
            command.extend(["--network", self.network_mode])
        command.extend([self.image, "tail", "-f", "/dev/null"])

        result = subprocess.run(command, capture_output=True, check=False)
        if result.returncode != 0:
            raise DockerRunError(f"docker run 失败:\n{result.stderr.decode()}")

        self.started = True
        return self

    def exec(self, command: str) -> None:
        """在容器内执行 bash 命令。"""
        result = subprocess.run(
            ["docker", "exec", "-w", self.working_dir,
             self.name, "bash", "-lc", command],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise DockerRunError(result.stdout + result.stderr)

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        """显式关闭容器。"""
        if not self.started:
            return
        self._remove_container(self.name)
        self.started = False

    @staticmethod
    def _remove_container(name: str) -> None:
        subprocess.run(
            ["docker", "rm", "-f", name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
```

## 使用方式

```python
with DockerContainerSession(
    host_path=Path("/path/to/source"),
    image="build-env:latest",
    name="build-container",
    target="/work",
    working_dir="/work",
) as container:
    container.exec("cmake -B build -S .")      # 步骤 1
    container.exec("cmake --build build")       # 步骤 2
    container.exec("ctest --test-dir build")    # 步骤 3
# 退出 with 块时容器自动清理，即使中间抛出异常
```

## 模式优势

| 优势 | 说明 |
|------|------|
| **RAII 保证** | 进入 with 块创建，退出自动销毁，异常也不泄漏 |
| **多步共享** | 多步操作共享同一个容器文件系统，无需额外 volume |
| **失败定位清晰** | 每步独立 exec，知道哪一步失败 |
| **调试友好** | 临时去掉 `--rm` 或 `close()`，失败时容器保留可进入排查 |
| **残留清理** | 启动前先 `docker rm -f` 清理同名残留 |

## 变体与扩展

### 变体 A：单步模式（简单场景）

如果只需要执行一条命令，可以用函数式封装：

```python
def docker_run(image: str, command: str, volumes: list[tuple[str, str]] = None):
    """一次性执行，不需要上下文管理器。"""
    args = ["docker", "run", "--rm"]
    for src, dst in (volumes or []):
        args.extend(["-v", f"{src}:{dst}"])
    args.extend([image, "bash", "-lc", command])
    return subprocess.run(args, check=True)
```

### 变体 B：流式输出（长时构建）

构建任务需要实时查看日志时，用 `Popen` + `stdout.buffer` 流式输出：

```python
def _stream_command(command: list[str]) -> tuple[int, str]:
    """执行命令并将 bytes 直写 stdout.buffer，避免编码层干扰。"""
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    chunks: list[bytes] = []
    for chunk in iter(process.stdout.readline, b""):
        chunks.append(chunk)
        if hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
        else:
            sys.stdout.write(chunk.decode("utf-8", errors="replace"))
            sys.stdout.flush()
    exit_code = process.wait()
    return exit_code, b"".join(chunks).decode("utf-8", errors="replace")
```

## 适用场景

- 编译构建流水线（CMake/Make/Nuitka 等多步构建）
- 容器化开发环境（临时启动容器执行开发任务）
- CI/CD 任务（需要可控容器生命周期的自动化任务）
- 多步数据处理管道（每步依赖上一步结果文件）

## 注意事项

1. **容器名唯一**：并行任务需使用不同容器名，避免冲突
2. **bind mount 性能**：Windows → WSL2 的 bind mount I/O 较慢，大文件写入建议放容器本地存储
3. **--rm 与调试**：调试时临时去掉 `--rm`，成功后恢复
4. **网络模式**：`--network host` 在 Linux 上性能好，macOS/Windows 可能需要调整
5. **信号处理**：长时运行考虑捕获 SIGINT 优雅停止容器

## 正反例

### 正例

```python
# ✅ 上下文管理器，异常安全
with DockerContainerSession(...) as c:
    c.exec("step1")
    c.exec("step2")
    c.exec("step3")
```

### 反例

```python
# ❌ 手动管理，异常时资源泄漏
subprocess.run(["docker", "run", "-d", "--name", "c1", ...])
subprocess.run(["docker", "exec", "c1", "step1"])
subprocess.run(["docker", "exec", "c1", "step2"])  # 这里失败的话...
subprocess.run(["docker", "exec", "c1", "step3"])
subprocess.run(["docker", "rm", "-f", "c1"])        # ...这里不会执行！
```
