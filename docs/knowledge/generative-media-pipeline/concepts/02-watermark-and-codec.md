---
type: Reference
id: "generative-media-pipeline-concept-02"
title: "水印去除与编码兜底：让成片绕开平台标记与本机依赖缺失"
category: "generative-media-pipeline"
tags: ["水印", "inpaint", "OpenCV", "编码兜底", "ffmpeg", "H.264", "rawvideo", "依赖修复"]
date: "2026-10-20"
last_verified: "2026-10-20"
status: "stable"
author: "SpecWeave Agent（session sc-20261020-welcome-home-production-retro）"
summary: "两类工程兜底：①生成平台在画面角落烧入的可见标识，用固定矩形掩膜 + OpenCV Telea inpaint 确定性去除，输出副本并保留原片；②本机编码器缺失（OpenH264 DLL 未随附导致 VideoWriter 只能落 mp4v）或依赖库损坏（Pillow 在新 Python 版本下无法导入）时的完整处置链，含编码器逐个探测、imageio-ffmpeg 自带 libx264 的 rawvideo 管道输出、依赖强制重装与解释器选择。"
source: "../references/evidence-and-costs.md"
---

# 02 水印去除与编码兜底

## 1. 平台烧入标识：问题与判定

主流 AI 视频生成平台会在成片右下角烧入一行半透明标识（如"视频由 AI 生成"）。这对普通用途无所谓，但撞上两类硬约束就致命：

- **交付红线要求画面无可读文字**（如用于影片级概念片、需与其他成片混剪的物料）
- **下游要重新做文字层**（平台水印会和新字幕叠在一起）

**判定方法**：不要靠肉眼看首帧。批量抽帧（每段取 20%/50%/80%）后统一看角落区域——水印是逐帧烧入的，抽取三帧足够定位。

## 2. 去除方案：固定矩形 + 确定性 inpaint

水印位置由平台固定，因此去除是**确定性的几何修补**，不是内容生成。

```python
import cv2

# 平台烧入标识的包围矩形：推荐按相对比例定义，与素材分辨率解耦
# （下方数值为 1920×1080 下的一个示例，换分辨率须按比例重算）
WM_RECT = (1680, 990, 1920, 1060)   # x0, y0, x1, y1
INPAINT_RADIUS = 3

cap = cv2.VideoCapture(src)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

writer = open_writer(dst, fps, (w, h))     # 见第 4 节的编码器探测

mask = np.zeros((h, w), dtype=np.uint8)
x0, y0, x1, y1 = WM_RECT
mask[y0:y1, x0:x1] = 255

while True:
    ok, frame = cap.read()
    if not ok:
        break
    fixed = cv2.inpaint(frame, mask, INPAINT_RADIUS, cv2.INPAINT_TELEA)
    writer.write(fixed)
```

### 2.1 四个关键决策

| 决策 | 选择 | 理由 |
|---|---|---|
| **算法** | `INPAINT_TELEA` | 快速行进法，对小面积、低纹理区域足够；不引入生成模型的随机性，输出可复现 |
| **半径** | 3 | 半径过大会在水印周围产生可见涂抹感；过小则填不满字形笔画 |
| **输出策略** | **输出副本，保留原片** | 原片是溯源依据。发现问题时要能回到未处理版本重选参数 |
| **批处理形态** | 批量跑 + 抽查 | 8 段一起跑，之后抽帧确认。逐段手工确认成本高且易漏 |

### 2.2 尺寸对齐提醒

矩形坐标是**绝对像素**。素材分辨率变化时（不同模型默认 720p/1080p 不一），同一个坐标会打在错误位置。

做法：把矩形定义为**相对比例**（如右下角 12.5% × 6.5% 的区域），落地时再乘以实际宽高。定义与实际分辨率解耦，是这条做法能跨素材复用的前提。

### 2.3 验收标准

| 编号 | 标准 | 判定 |
|---|---|---|
| W1 | 处理后抽帧，标识区域无可读文字残留 | 抽帧目视 + 可选 OCR 辅助 |
| W2 | 修补区域无可见涂抹/色块断裂 | 目视；深色渐变背景上最易暴露 |
| W3 | 原片保留且可回放 | 文件存在 + 可解码 |
| W4 | 输出帧数与输入一致 | 帧数相等（不多不少） |
| W5 | 矩形定义与分辨率解耦 | 相对比例表达 |

## 3. 副作用：去水印会重编码，体积会变

必须预期到：inpaint 后的每一帧都是新编码帧，**文件体积通常显著变化**（实践中常见降到原版一半左右——原片的编码器在修补区域浪费了大量比特）。

这不是质量问题的信号，但要注意两点：

1. **体积骤降不等于画质变好**。也可能是编码器换了（第 4 节的回退链会让编码从 H.264 落到 mp4v）。核对方式：探测输出流的 codec 字段。
2. **如果最终成片要求 H.264**（多数平台与播放器的要求），去水印这一步的 mp4v 中间产物不能直接进最终成片——要用它作**帧源**，重新走一遍 H.264 编码。

## 4. 编码兜底：探测链

本机不一定有目标编码器。常见情况：`cv2.VideoWriter` 想写 `avc1`（H.264），但 OpenH264 的 DLL 没随 opencv-python 一起装，调用直接失败。

**做法：逐个探测，第一个能打开的就是它，并记录实际用的是哪个。**

```python
def open_writer(path, fps, size):
    for fourcc_name in ("avc1", "mp4v", "XVID"):
        ext = ".mp4" if fourcc_name in ("avc1", "mp4v") else ".avi"
        trial = path + ext
        writer = cv2.VideoWriter(
            trial, cv2.VideoWriter_fourcc(*fourcc_name), fps, size
        )
        if writer.isOpened():
            return writer, trial, fourcc_name
        writer.release()
    raise RuntimeError("no usable encoder")
```

**要点**：
- 探测顺序即偏好顺序：优先 H.264（`avc1`），退 `mp4v`（通用但体积大、画质差），再退 `XVID`（.avi）。
- **必须把实际使用的编码器记进日志**。否则后面看到"体积大了 3 倍"会以为是去水印的问题。
- `VideoWriter` 打开失败的典型表现是**不抛异常、只返回 `isOpened() == False`**。不检查这个返回值，脚本会静默产出 0 字节文件。

## 5. 终极兜底：借 ffmpeg 自带的 libx264

当 OpenCV 写不出目标格式时，绕开 OpenCV 的编码器：让 OpenCV 只做**像素搬运**，用 ffmpeg 做编码。

```python
# ffmpeg 由 imageio-ffmpeg 提供，无需系统安装
import imageio_ffmpeg
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

cmd = [
    ffmpeg, "-y",
    "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
    "-i", "-",                      # 从 stdin 读原始帧
    "-an",                          # 无音轨
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-pix_fmt", "yuv420p",          # 兼容性关键
    "-movflags", "+faststart",      # 网页/流式播放需要
    out_path,
]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
```

**四个必备参数**：

| 参数 | 为什么 |
|---|---|
| `-pix_fmt bgr24` | 与 OpenCV 的像素顺序一致，否则颜色全反 |
| `-pix_fmt yuv420p`（输出侧） | H.264 的 4:2:0 色彩抽样，**不写会导致播放器不认** |
| `-movflags +faststart` | 把 moov atom 挪到文件头，网页播放必须 |
| `-r <fps>` | 输入侧帧率，与输出侧一致 |

**管道模式要点**：所有帧写完必须 `proc.stdin.close()` 再 `proc.wait()`，否则 ffmpeg 收不到 EOF，产出的文件不完整。子进程退出码非 0 时要抛错，不要静默通过。

这条兜底还有一个附带好处：**颜色空间、码率、faststart 都变成显式可控的参数**，而不是交给某个库的默认值。

## 6. 依赖损坏的处置

生成管线常踩的一个坑：某个图像库在新版 Python 下无法导入。

典型症状：

```
ImportError: cannot import name '_imaging' from 'PIL'
```

这类错误**不是**"没装 pillow"，而是**装的那版与当前 Python 版本不兼容**（二进制轮子没跟上）。

**处置链**：

1. 先看当前 Python 版本，确认它是否超出了该库支持范围。
2. 强制重装，绕过缓存里的坏轮子：
   ```bash
   python -m pip install --force-reinstall --no-cache-dir pillow
   ```
   `--no-cache-dir` 是关键——否则 pip 会从缓存里取出同一个坏轮子装回去，你会以为重装没生效。
3. 装完立刻做一次最小验证：`from PIL import Image, ImageDraw, ImageFont; Image.new("RGB",(4,4))`。

### 6.1 解释器选择：多 Python 环境下的 cv2 缺失

一个高频状况：本机有多个 Python，而装 `opencv-python` 的那个不是当前默认的解释器。

```
ModuleNotFoundError: No module named 'cv2'
```

**不要**因此就去给默认解释器装包——那会污染一个本该干净的环境。**正确做法是找到已经装好的那个解释器，用它跑管线**：

```bash
# 逐个探测哪个解释器有 cv2
for py in python3 python /path/to/venv/Scripts/python.exe; do
  "$py" -c "import cv2; print('$py', cv2.__version__)" 2>/dev/null
done
```

**Windows 布局提醒**：venv 的解释器在 `Scripts/` 而不是 `bin/`。写死了 `bin/python` 的脚本在 Windows 上必然失败。

**教训**：把「生产环境依赖清单」写下来（Python 版本、opencv 版本、Pillow 版本、ffmpeg 来源、各自的位置），否则下一次换机器或换会话就要重新踩一遍探测。

## 7. 检验标准

| 编号 | 标准 | 判定 |
|---|---|---|
| E1 | 输出流的 codec 字段等于目标格式 | 探测输出文件 |
| E2 | 实际使用的编码器已记入日志 | 日志中存在该字段 |
| E3 | `VideoWriter.isOpened()` 被检查 | 代码中存在该判断 |
| E4 | 帧数与输入一致 | 帧数相等 |
| E5 | ffmpeg 子进程退出码被检查 | 代码中存在 `proc.wait()` + 返回码判断 |
| E6 | 管道写完后 stdin 关闭 | 存在 `stdin.close()` |
| E7 | 依赖清单已归档，含解释器路径 | 存在清单文件 |

---

- [🏠 返回知识包首页](../index.md)
- [← 上一篇：首帧保真](01-anchor-frame-fidelity.md)
- [下一篇：文字渲染与限流降级 →](03-text-rendering-and-fallback.md)
