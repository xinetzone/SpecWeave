# camera_utils — 摄像头发现与健壮初始化

封装了多后端尝试、分辨率自动降级、设置后实际验证等模式。解决 OpenCV 在不同 Windows 后端上摄像头打开失败、`cap.set()` 静默失败等常见问题。

## 何时使用

- 需要在不同 Windows 机器上可靠打开 USB UVC 摄像头
- 摄像头在特定后端（MediaFoundation/DirectShow）下不兼容
- `cap.set()` 设置的分辨率与实际读取分辨率不一致
- 需要快速探测系统是否有可用摄像头

## 前置条件

```bash
pip install opencv-python numpy
```

## API 参考

### `open_camera_robust(...)`

多后端+多分辨率尝试打开摄像头，返回经过实际读帧验证的 `VideoCapture`。

```python
from hardware_io.camera_utils import open_camera_robust

info = open_camera_robust(
    preferred_width=1280,
    preferred_height=720,
    fps=30,
    device_index=0,
    verbose=True,
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `preferred_width` | `int` | `640` | 首选画面宽度 |
| `preferred_height` | `int` | `480` | 首选画面高度 |
| `fps` | `int` | `30` | 目标帧率 |
| `device_index` | `int` | `0` | 摄像头设备索引 |
| `backends` | `list[tuple[int,str]] \| None` | `None` | 后端列表，为 `None` 时使用默认顺序（MSMF→DSHOW→ANY） |
| `resolutions` | `list[tuple[int,int]] \| None` | `None` | 分辨率候选列表，为 `None` 时自动生成（首选+默认降级列表） |
| `min_frame_ratio` | `float` | `0.5` | 实际分辨率至少达到请求分辨率的此比例才算成功 |
| `verbose` | `bool` | `False` | 是否打印尝试过程 |

**返回**：[`CameraInfo`](#camerainfo) 数据类，包含已打开的 `VideoCapture` 和实际参数。

**异常**：
- `RuntimeError`：所有后端和分辨率组合均失败，异常信息包含每个后端的失败原因。

#### 尝试顺序

1. 依次尝试每个后端（MSMF → DSHOW → ANY）
2. 对每个后端，依次尝试各候选分辨率
3. 设置分辨率后实际 `read()` 一帧，验证真实分辨率
4. 实际分辨率 ≥ 请求分辨率 × `min_frame_ratio` 即视为成功

#### 默认分辨率降级列表

```python
DEFAULT_RESOLUTION_FALLBACK = [
    (1280, 720),
    (1920, 1080),
    (1024, 768),
    (800, 600),
    (640, 480),
    (320, 240),
]
```

首选分辨率自动排在此列表最前面（去重）。

### `CameraInfo`

`open_camera_robust()` 的返回值类型：

| 字段 | 类型 | 说明 |
|------|------|------|
| `cap` | `cv2.VideoCapture` | 已打开的摄像头实例（使用完毕需调用 `cap.release()`） |
| `width` | `int` | 实际画面宽度 |
| `height` | `int` | 实际画面高度 |
| `fps` | `float` | 实际帧率 |
| `backend_name` | `str` | 成功使用的后端名称 |

### `probe_camera(device_index=0)`

快速探测摄像头是否可读，不设置分辨率。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `device_index` | `int` | `0` | 摄像头设备索引 |

**返回**：`(width, height) | None`——成功返回实际分辨率元组，失败返回 `None`。

```python
from hardware_io.camera_utils import probe_camera

result = probe_camera()
if result:
    print(f"摄像头可用: {result[0]}x{result[1]}")
else:
    print("未检测到可用摄像头")
```

### `list_backends()`

列出当前平台各后端是否可用（通过尝试打开摄像头检测）。

**返回**：[`CameraBackend`](#camerabackend) 列表。

```python
from hardware_io.camera_utils import list_backends

for b in list_backends():
    status = "✓" if b.available else "✗"
    print(f"  {status} {b.name}")
```

### `CameraBackend`

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `int` | OpenCV 后端常量（如 `cv2.CAP_MSMF`） |
| `name` | `str` | 后端名称 |
| `available` | `bool` | 该后端能否打开摄像头 |

### `save_frame(frame, filepath, jpeg_quality=95)`

保存帧为图片文件。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `frame` | `np.ndarray` | — | OpenCV BGR 格式帧 |
| `filepath` | `str` | — | 输出路径，扩展名决定编码（`.jpg`/`.png`） |
| `jpeg_quality` | `int` | `95` | JPEG 质量（1-100），仅对 `.jpg` 有效 |

**返回**：`bool`，是否保存成功。

```python
from hardware_io.camera_utils import save_frame

ret, frame = info.cap.read()
if ret:
    save_frame(frame, "snapshot.jpg", jpeg_quality=90)
```

## 使用示例

### 示例 1：最简打开摄像头

```python
from hardware_io.camera_utils import open_camera_robust
import cv2

info = open_camera_robust(verbose=True)
print(f"摄像头: {info.width}x{info.height} @ {info.fps:.0f}fps [{info.backend_name}]")

while True:
    ret, frame = info.cap.read()
    if not ret:
        break
    cv2.imshow("camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

info.cap.release()
cv2.destroyAllWindows()
```

### 示例 2：指定首选分辨率

```python
info = open_camera_robust(preferred_width=1920, preferred_height=1080, fps=25)
# 如果 1080p 不可用，会自动降级到 720p、480p 等
```

### 示例 3：自定义后端和分辨率顺序

```python
import cv2
from hardware_io.camera_utils import open_camera_robust

# 只尝试 DirectShow，分辨率从高到低
info = open_camera_robust(
    backends=[(cv2.CAP_DSHOW, "DirectShow")],
    resolutions=[(1920, 1080), (1280, 720), (640, 480)],
)
```

### 示例 4：无硬件环境的优雅降级

```python
from hardware_io.camera_utils import probe_camera

cam = probe_camera()
if cam is None:
    print("无摄像头，使用测试图片模式")
    # ... 加载测试图片或跳过摄像头相关逻辑
else:
    print(f"摄像头就绪: {cam[0]}x{cam[1]}")
    # ... 正常摄像头流程
```

### 示例 5：采集线程配合 FrameBuffer

```python
import threading, cv2
from hardware_io.camera_utils import open_camera_robust
from hardware_io.frame_buffer import FrameBuffer

buf = FrameBuffer()
running = True

def capture_loop():
    info = open_camera_robust(640, 480, verbose=True)
    while running:
        ret, frame = info.cap.read()
        if ret:
            buf.set_copy(frame)
    info.cap.release()

threading.Thread(target=capture_loop, daemon=True).start()

# 主线程按需取帧
while running:
    frame, _ = buf.get_copy()
    if frame is not None:
        cv2.imshow("preview", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
```

## 常见陷阱

1. **`cap.set()` 会静默失败**：OpenCV 的 `set()` 返回 `bool`，但部分摄像头即使返回 `True`，实际分辨率也可能不变。本模块通过 `read()` 后检查 `frame.shape` 验证真实分辨率。
2. **后端优先级因设备而异**：MediaFoundation 在多数现代摄像头表现更好，但部分老旧 UVC 摄像头只在 DirectShow 下支持特定分辨率。多后端尝试可覆盖绝大多数情况。
3. **使用完毕必须 `cap.release()`**：否则摄像头设备被占用，其他进程无法打开。
4. **`min_frame_ratio` 的作用**：部分摄像头会返回接近但不完全等于请求值的分辨率（如请求 1280×720 实际返回 1280×720 或 960×540），默认 0.5 的阈值允许这种偏差。
