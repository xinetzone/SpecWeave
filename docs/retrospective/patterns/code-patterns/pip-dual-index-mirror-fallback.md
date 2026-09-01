---
type: Pattern
id: "pip-dual-index-mirror-fallback"
source: "docs/retrospective/reports/milestone/torch-dev-mirror-build-retrospective-20260820.md#L94-L101（洞察 I-2）"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/pip-dual-index-mirror-fallback.toml"
---
# 镜像依赖「主索引+备用源」双通道下载（extra-index mirror fallback）

## 模式概述

Docker/CI 镜像构建中，当主索引（`download.pytorch.org` / PyPI）的某依赖因网络问题（如 `files.pythonhosted.org` IPv6 不可达）下载失败时，扩展 pip 安装辅助函数支持 `--index-url` + `--extra-index-url` 双通道下载，以主索引负责版本正确的 wheel、国内镜像为备用源兜底 PyPI 侧依赖；并同步在验证层增加 CUDA/版本硬断言，防止主索引故障时静默降级。

## 核心机制：多源合并语义的"延迟风险窗口"（洞察 I-2）

`--index-url` + `--extra-index-url` 双索引的合并语义存在一个**看似无害、实则致命的延迟风险窗口**：

- **正常时无害**：主索引可达时，pip 将两个索引的候选版本合并后取最高版本，备用源只兜底主索引缺失的依赖，demo/CI 全程通过，让人误以为双索引"等价于"单源。
- **故障时即静默降级通道**：一旦主索引故障，pip 会自动 fallback 到备用源。备用源（如阿里云）往往只有 CPU 版或 beta 版 torch，且版本满足过宽约束（如 `<14,>=13.0.3`），pip 便静默取之——构建仍"成功"，运行时 CUDA 不可用才暴露。

**反常识**：风险窗口恰恰隐藏在"当初引入备用源要解决的场景"（主索引故障）里。演示时主索引可达→所有验证通过→掩盖了故障路径的静默降级。**凡是多源合并语义，必须假定"最坏匹配会命中"来设计验证层拦截，而不仅仅针对"当前正常状态"验证。**

## 触发场景

主索引（pytorch.org / PyPI）某依赖因网络问题（如 IPv6 不可达、DNS污染、源故障）下载失败，需要备用源兜底。特征信号：

- `pip download`/`pip install` 对特定 wheel 超时或 404
- 主索引 IPv6 可达性异常（`ping6`/`curl --ipv6` 无响应）而 IPv4 正常
- 某依赖（如 `cuda_bindings-cp314t`）仅存在于 PyPI 侧

## 核心步骤

1. **扩展 pip 安装辅助函数**：`pip_install_group` 支持 `--index-url` 与 `--extra-index-url` 参数解析（消除硬编码索引）
2. **Dockerfile 传入双索引**：主索引为官方版本源（如 `https://download.pytorch.org/whl/cu130`），备用源为国内镜像（如 `https://mirrors.aliyun.com/pypi/simple/`）
3. **同步生效共享 helper**：若基础层不含新参数，显式 `COPY` 覆盖共享 helper（临时补丁，全链重建后合并源头）
4. **验证层添加硬断言**：CUDA 编译版本断言（`torch.version.cuda` 非空）/ 版本锁定断言，防静默降级
5. **构建后 `pip freeze` 固化解析清单**：写入 build-info，保证可复现审计

## 反模式

- **只看主索引日志误判全局网络不可达**：主索引 IPv6 不通不代表所有源不可达，应先用备用源验证网络连通性再决策
- **只改共享文件不做 COPY 覆盖导致修改不生效**：基础层不含新参数时，改源头共享文件需在下游变体 `COPY`/重建才会生效；改造无效先排查是否因 COPY 覆盖
- **修复下载层后不补验证层断言**：`--extra-index-url` 的合并语义（pip 取最高版本）在主索引故障时成为静默降级通道——备用源往往只有 CPU 版或 beta 版 torch，装错版本构建仍"成功"，直到运行时才发现
- **不加版本锁定依赖过宽约束**：`<14,>=13.0.3` 之类过宽约束会放过 beta 版本漂移

## 正反例对比

| 维度 | ❌ 反模式 | ✅ 正模式 |
|------|---------|---------|
| 下载失败应对 | 仅轮询重试主索引（IPv6 不可达是确定性网络问题，重试无效） | 主索引+备用源双通道，备用源兜底 PyPI 依赖 |
| 备用源漂移 | 直接切换 index-url 为阿里云（无 cu130 构建，torch 静默装 CPU 2.9.1） | 主索引负责 CUDA 版本，备用源仅兜底 PyPI 侧依赖 |
| 降级拦截 | 验证层 `[SKIP]+exit(0)`（放过所有 GPU 错误，构建"成功"） | `torch.version.cuda` 硬断言，CPU 构建 FAIL |
| 依赖约束 | `>=X,<Y` 过宽约束 | 精确锁定 `torch==2.13.0+cu130`（防 beta 漂移） |
| 可复现性 | 构建后不做版本固化 | `pip freeze` 写入 build-info |

## 检查清单

- [ ] `pip_install_group` 支持 `--index-url`/`--extra-index-url` 参数解析
- [ ] 主索引保留官方版本源，备用源仅兜底 PyPI 侧依赖
- [ ] 基础层不含新参数时已显式 `COPY` 覆盖共享 helper（并标记全链重建后移除）
- [ ] 验证层已加 CUDA 编译版本硬断言（`torch.version.cuda` 非空），CPU 构建 FAIL 而非 SKIP
- [ ] 关键依赖版本已精确锁定，无过宽约束
- [ ] 构建后 `pip freeze` 固化解析清单至 build-info
- [ ] 已实测验证：真实 CUDA 版 PASS，模拟 CPU 版正确 FAIL

## 实际案例

- **torch-dev 镜像构建**（2026-08-20，validation_count=1）：`download.pytorch.org/whl/cu130` 为主索引 + `mirrors.aliyun.com/pypi/simple/` 备用源，解决 `files.pythonhosted.org` IPv6 不可达导致 `cuda_bindings-13.3.1-cp314t` 下载失败；`cuda_bindings` 经备用源成功拉取，torch 2.13.0+cu130 正常安装，5 项冒烟通过。镜像 8.22GB，Stage 3 安装 1169s。

## 成熟度

- **L1 实验性**：仅 1 次成功案例（torch-dev），待更多验证
- validation_count：1
- reuse_count：0
- 迁移验证声明：可迁移至 onnx-dev / ai-dev / 任何 pip 多索引镜像构建（需按检查清单补验证断言）

## 关联

- [Conda镜像源精确映射：custom_channels](conda-custom-channels-mirror.md)（conda 侧镜像配置，与 pip 双索引互补）
- [预训练模型多源下载与多级验证](pretrained-model-download-validation.md)（非 pip 资产的 N fallback）
- [ADR: torch-dev 双索引下载与 CUDA 硬断言](../../../knowledge/decisions/torch-dev-extra-index-cuda-assertion.md)