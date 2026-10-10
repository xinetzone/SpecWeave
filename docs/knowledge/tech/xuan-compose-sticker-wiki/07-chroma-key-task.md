---
type: Reference
id: "xuan-compose-sticker-07-chroma-key-task"
title: "色幕去底：把一次性任务做成退出码可判定的容器"
tags: ["xuan-compose", "一次性任务", "chroma-key", "pillow", "rgba", "贴纸"]
date: "2026-10-09"
last_verified: "2026-10-09"
status: "stable"
category: "tech"
author: "SpecWeave Agent"
source: "derived: examples/keychroma/remove_chroma_key.py；skills: travel-memory-card-duo 及其 references/style-guide.md；src/xuan_compose/commands/runexec.py"
summary: "用 Pillow/numpy 实现均匀色幕抠除（边框取色、RMS 色差双阈值、软蒙版、溢色抑制 despill、边缘腐蚀），打包成无守护进程的 keychroma 镜像，通过 xuan-compose run --rm 触发并以退出码与四角 alpha 校验透明底 PNG 的正确性。"
---

> 📚 **教程导航**：[总览](00-overview.md) | [流水线与架构](01-pipeline-architecture.md) | [安装与文件发现](02-install-discovery.md) | [compose.yaml 逐段精讲](03-compose-walkthrough.md) | [卷与密钥](04-volumes-secrets.md) | [生命周期与一次性任务](05-lifecycle-tasks.md) | [生图服务实战](06-generator-worker.md) | [色幕去底任务](07-chroma-key-task.md) | [库 API 与预演](08-library-api.md) | [避坑与 FAQ](09-pitfalls-faq.md) | [模式与验收清单](10-pattern-checklist.md)

# 色幕去底：一次性任务的容器化

## 为什么去底要独立成一个确定性任务

透明底贴纸有两类完全不同的正确性要求：

- **视觉正确性**（六枚贴纸与记忆卡同版）——由 [06 章](06-generator-worker.md)的色幕稿保证；
- **通道正确性**（真 RGBA、四角全透明、贴纸本体不透明、无幕布色镶边）——由本任务用**确定性算法 + 可重复校验**保证。

把它从"模型一次画成"中拆出来，好处是：纯本地、零 API 费用、同一张色幕稿永远得到同一张 PNG、失败有明确非零退出码。

## 算法五步（[remove_chroma_key.py](examples/keychroma/remove_chroma_key.py)）

1. **取色幕色**：`--auto-key border`（默认）取四边 2px 边框像素的中位数（抗 JPEG/压缩噪点）；`corners` 只取四角；`none` + `--key #RRGGBB` 显式指定（默认取环境变量 `CHROMA_KEY`）。
2. **算色差**：每像素 RGB 与幕色的 **RMS 距离**（0–255），对幕布轻微不均比单次欧氏距离更稳。
3. **双阈值出 alpha**：
   - 距离 ≤ `--transparent-threshold`（默认 12）→ alpha=0；
   - 距离 ≥ `--opaque-threshold`（默认 60）→ alpha=255；
   - 之间：`--soft-matte` 时线性渐变（软边，模切纸边更自然），否则硬边；
   - 与原图自带 alpha 取交集。
4. **`--despill` 抑溢色**：只对半透明边缘带，把幕布主通道压到非幕布通道最大值 + 偏置（绿幕压绿、品红幕压红蓝），消除绿/品红镶边。
5. **`--edge-contract N`**：对 alpha 做 N 次 3×3 最小滤波（形态学腐蚀），吃掉一两个像素的残余光晕。

## 触发：run --rm 与退出码透传

`keychroma` 镜像没有守护进程，`ENTRYPOINT` 固定为去底脚本；compose 把 `./out` 挂到 `/work/out`：

```bash
xuan-compose run --rm keychroma -- \
  /work/out/stickers-chroma.png /work/out/stickers.png \
  --soft-matte --despill --edge-contract 1
```

- `run` 会先按需构建镜像、确保 Pod 存在，再 `podman run -i --rm`（见 [05 章](05-lifecycle-tasks.md)）；
- 脚本校验失败返回 **2**，经 `sys.exit(p)` 原样成为 `xuan-compose run` 的退出码，因此可以：

```bash
xuan-compose run --rm keychroma -- /work/out/stickers-chroma.png /work/out/stickers.png \
  --soft-matte --despill --edge-contract 1 \
&& echo "透明底校验通过" || echo "去底未通过，调阈值或重新生成色幕稿"
```

## 验收标准（脚本自检 + 人工目检）

脚本自检（不通过即退出码 2）：

- 输出为 **PNG / RGBA**（含 Alpha 通道）；
- **四角 alpha 全为 0**；
- 打印全透明/全不透明像素占比与四角 alpha 值。

人工目检（脚本无法判断图案语义）：

- 恰好**六枚**贴纸，全部完整、互不接触、未被裁切；
- 形状、配色、暖白模切边与记忆卡上的六枚一致；
- 贴纸本体无不透明破洞、边缘无绿/品红镶边、无残留幕布色块；
- 画面中无纸张底板、阴影、文字、标签（这些都不该出现在透明 PNG 里）。

在看图软件里以棋盘格/深色底预览，透明区域应显示背景——但**棋盘格只是预览，不是文件内容**，以脚本的 Alpha 校验为准。

## 调参与换幕色

| 现象 | 处理 |
|------|------|
| 四角未全透明 / 贴纸外有薄雾 | 加大 `--transparent-threshold`（如 12→20），或加 `--edge-contract 1` |
| 贴纸边缘被啃掉、细枝丫缺失 | 缩小阈值差（opaque 调到 45–50），去掉一次 edge-contract |
| 绿幕场景边缘发绿 | 加 `--despill`，必要时 `--despill-bias` 调小 |
| 图案本身含大片绿色（植被） | 改用品红幕：`.env` 设 `CHROMA_KEY=#ff00ff` 后**重新生成贴纸稿**再去底 |

> 关键前提在生图那一步：贴纸稿背景必须**绝对均匀**（无渐变、纹理、投影）。若模型给了带光影的背景，不要靠调阈值硬救，回到 [06 章](06-generator-worker.md)强化贴纸稿提示词重新生成。
