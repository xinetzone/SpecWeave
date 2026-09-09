---
id: "win-powershell-compress-archive-gzip-mismatch"
title: "Windows PowerShell Compress-Archive 生成无效 .tar.gz 的规避"
type: process-pattern
date: 2026-09-09
maturity: L1 实验性
maturity_note: "单案例验证（jupyter-podman-client image-cache），待第二个独立场景验证后升级 L2"
source: "../../reports/incident-reports/incident-invload-invalid-tar-20260909/retrospective-report.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/process-patterns/win-powershell-compress-archive-gzip-mismatch.toml"
related_patterns:
  - oci-shell-compatibility.md
---

# Windows PowerShell Compress-Archive 生成无效 .tar.gz 的规避

## 触发场景

在 Windows 环境下，需要将容器镜像（`podman save` 输出的 `.tar`）压缩为 `.tar.gz` 存入 `.image-cache/`，以便跨环境传递或备份。

## 核心规则

**Windows PowerShell 的 `Compress-Archive` 生成的是 ZIP 格式，不是 gzip 压缩的 tar。**

即使文件扩展名是 `.tar.gz`，`Compress-Archive` 生成的底层格式仍是 ZIP。`podman load` 解析时会报 `invalid tar header` 错误，因为 OCI-archive 和 docker-archive 格式都要求真正的 gzip tar。

## 正确做法

### 方案一：Python gzip 模块（推荐，已验证）

```python
import gzip
import shutil

with open('input.tar', 'rb') as f_in:
    with gzip.open('output.tar.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
```

匹配 `build-end` 中 `podman save | gzip > file.tar.gz` 的模式（Podman 通过管道传给 gzip）。

### 方案二：WSL2 bash（如环境可用）

```bash
tar -czf output.tar.gz input.tar
```

注意：直接运行 `tar -czf` 在 WSL2 中产生有效的 gzip tar，但 **PowerShell 中 `tar -czf` 在某些 Windows 版本的行为可能不一致**，需实际验证。

### 方案三：7-Zip（如已安装）

```powershell
7z a -tgzip output.tar.gz input.tar
```

## 反模式

| 反模式 | 症状 | 后果 |
|--------|------|------|
| 使用 `Compress-Archive` 生成 .tar.gz | `podman load` 报 `invalid tar header` | 缓存文件不可用，需要重建 |
| 用扩展名判断格式而非内容验证 | 误以为 .tar.gz 就是 gzip | 浪费调试时间 |
| 缓存命中逻辑缺少完整性校验 | 损坏文件被当作有效缓存直接使用 | 问题延迟发现 |

## 迁移验证

在以下场景复现验证修复有效性：

- [ ] `podman save localhost/myimage:latest -o image.tar && python -c "import gzip,shutil; ..."` → `podman load -i image.tar.gz` 成功
- [ ] `.image-cache/manifest.txt` 记录的 SHA256 与实际文件一致
- [ ] `inv load` 命令可正常完成镜像加载

## 预防措施

1. **`.image-cache/README.md` 明确禁令**：在 image-cache 目录下添加说明，禁止使用 `Compress-Archive`
2. **manifest.txt 加校验字段**：记录 SIZE 和 SHA256，load 前先校验
3. **tasks.py load 任务增加预检**：检查文件大小是否与 manifest 匹配
