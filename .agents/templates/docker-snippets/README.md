# Docker Snippets 代码片段模板库

> 基于 XMNN Nuitka 打包 + Docker 运行时镜像构建复盘萃取的可复用代码片段。
>
> **来源**：[retrospective-xmnn-nuitka-docker-runtime-20260722](../../docs/retrospective/reports/bug-fix/docker-build/retrospective-xmnn-nuitka-docker-runtime-20260722/README.md)
>
> **配套Checklist**：[docker-build-optimization-checklist.md](../../checklists/docker-build-optimization-checklist.md)

---

## 片段索引

| # | 模式 | 目录/文件 | 核心问题 | 关键文件 |
|---|------|----------|---------|---------|
| 1 | **基础镜像环境直用** (Build-Env-Reuse) | [01-build-env-reuse/](01-build-env-reuse/) | 已有build镜像时，runtime镜像无需新建conda环境 | Dockerfile.runtime模板、entrypoint.sh模板、.pth自初始化模板 |
| 2 | **C扩展Wheel依赖捆绑** (Wheel-Dep-Bundling) | [02-wheel-dep-bundling/](02-wheel-dep-bundling/) | conda环境下C扩展wheel的非系统共享库依赖自包含 | [bundle_wheel_deps.py](02-wheel-dep-bundling/bundle_wheel_deps.py)（完整Python工具）、CMake集成、shell快速版 |
| 3 | **多层命令脚本挂载** (Script-Mount) | [03-multi-layer-cli-script-mount/](03-multi-layer-cli-script-mount/) | PowerShell→WSL→Docker多层CLI嵌套时引号转义 | PowerShell/WSL验证模板、bash辅助函数、CI Actions模板 |
| 🧪 | **红线测试** | [test_docker_redlines.py](test_docker_redlines.py) | 五条红线pytest自动化断言 | pytest脚本，支持--image/--modules参数 |
| 🏗️ | **项目骨架** | [skeleton/](skeleton/) | 一键初始化Docker runtime项目 | Dockerfile+entrypoint+build.sh+verify.sh+.dockerignore+CONFIG.md |

---

## 使用指南

### 快速选择

```
需要构建含C扩展wheel的Docker运行时镜像？
├── 已有包含完整依赖的build镜像？
│   ├── 是 → 使用片段1（Build-Env-Reuse）：直接FROM build镜像
│   └── 否 → 需要先用片段2（Wheel-Dep-Bundling）做自包含wheel，再用python:slim基础镜像
├── 需要验证镜像功能？
│   ├── Windows+WSL环境 → 使用片段3（Script-Mount）：PowerShell脚本挂载模式
│   └── Linux/CI环境 → 使用片段3的bash辅助函数或CI模板
└── 不知道是否遗漏依赖？
    └── 运行 Checklist：[docker-build-optimization-checklist.md](../../checklists/docker-build-optimization-checklist.md)
```

### 片段使用方式

1. **复制模板**：进入对应子目录，复制需要的模板文件到项目中
2. **替换占位符**：使用目录README中的「占位符替换表」替换 `{{PLACEHOLDER}}` 变量
3. **对照Checklist**：构建前对照配套Checklist逐项确认
4. **验证**：使用片段3的脚本挂载模式进行验证

---

## 关联模式

这些代码片段是以下正式L1/L2模式的可执行实例：

| 代码片段 | 对应正式模式 | 成熟度 |
|---------|------------|--------|
| Build-Env-Reuse | [compiled-wheel-runtime-image-build.md](../../docs/retrospective/patterns/code-patterns/compiled-wheel-runtime-image-build.md) | L1 实验性 |
| Wheel-Dep-Bundling | [python-native-extension-self-contained-wheel.md](../../docs/retrospective/patterns/code-patterns/python-native-extension-self-contained-wheel.md) | L2 可复用 |
| Script-Mount | [direct-file-write-over-shell-pipe.md](../../docs/retrospective/patterns/code-patterns/direct-file-write-over-shell-pipe.md)（相关） | L1 实验性 |
| 版本验证 | [python-package-version-standard-api.md](../../docs/retrospective/patterns/code-patterns/python-package-version-standard-api.md) | L2 可复用 |
| Conda镜像源 | [conda-custom-channels-mirror.md](../../docs/retrospective/patterns/code-patterns/conda-custom-channels-mirror.md) | L2 可复用 |
