# frame_buffer — 线程安全的"最新值"缓存

适用于实时数据流（视频帧、传感器读数、状态快照等）的生产者-消费者场景。生产者持续更新最新值，消费者按需读取。与队列不同，本缓存**只保留最新值**，当消费者处理速度跟不上时自动丢弃旧值。

> **核心设计决策**：对实时预览而言，延迟比丢帧更不可接受。宁可丢弃旧帧，也不让消费者处理过期数据。

## 何时使用

- 摄像头采集线程与 GUI/处理线程之间传递最新帧
- 传感器数据轮询线程与业务逻辑线程之间共享最新读数
- 任何"只关心当前最新状态，不关心历史"的多线程场景

## 何时不使用

- 需要处理每一帧数据（不允许丢帧）——使用 `queue.Queue`
- 需要回溯历史数据——使用时间序列数据库或环形缓冲区
- 多生产者需要严格顺序——使用消息队列

## API 参考

### `FrameBuffer[T]`

泛型线程安全缓存。`T` 为缓存值类型。

#### 构造

```python
from hardware_io.frame_buffer import FrameBuffer

buf = FrameBuffer()  # T 可自动推断
buf_int = FrameBuffer[int]()  # 显式类型
```

#### `set(value, timestamp=None)`

更新缓存值。

| 参数 | 类型 | 说明 |
|------|------|------|
| `value` | `T` | 要缓存的值 |
| `timestamp` | `float \| None` | 可选时间戳（`time.time()` 格式），为 `None` 时自动取当前时间 |

```python
buf.set({"temp": 23.5})
buf.set(frame, timestamp=time.time())
```

> **注意**：`set()` 存储的是值的引用。对于 numpy 数组等可变对象，生产者在 `set()` 后修改原对象会影响缓存中的值。如需隔离，使用 `set_copy()`。

#### `set_copy(value, timestamp=None)`

更新缓存值并存储副本（如果值支持 `copy()` 方法）。对于 numpy 数组调用 `.copy()`，其他类型直接存储引用。

```python
import numpy as np

frame = np.zeros((480, 640, 3), dtype=np.uint8)
buf.set_copy(frame)  # 缓存的是副本，后续修改 frame 不影响缓存
```

#### `get() -> tuple[T | None, float]`

获取最新值及其时间戳。

**返回**：`(value, timestamp)` 元组。从未 set 过时 value 为 `None`，timestamp 为 `0.0`。

```python
data, ts = buf.get()
if data is not None:
    print(f"数据时间: {ts}, 年龄: {time.time() - ts:.3f}s")
```

> **注意**：返回的是引用（非副本），调用方如需长期持有应自行复制，或使用 `get_copy()`。

#### `get_copy() -> tuple[T | None, float]`

获取最新值的副本及其时间戳。值支持 `copy()` 时返回副本，否则返回引用。

```python
frame, ts = buf.get_copy()
if frame is not None:
    process_frame(frame)  # 处理副本，不影响缓存
```

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `age_ms` | `float` | 最新值的年龄（毫秒），无值时返回 `-1.0` |
| `is_fresh` | `bool` | 是否已有值缓存 |
| `frame_count` | `int` | 累计 `set()` 次数，可用于帧率统计 |

```python
if buf.is_fresh and buf.age_ms < 100:
    print("数据新鲜（<100ms）")

# 计算最近一秒的帧率
buf.set(frame)
# ... 一秒后 ...
fps = buf.frame_count - previous_count
```

#### `clear()`

清空缓存，重置 value 为 `None`、timestamp 为 `0.0`（`frame_count` 不重置）。

## 使用示例

### 示例 1：摄像头采集线程与处理线程

```python
import threading, time, cv2
from hardware_io.frame_buffer import FrameBuffer

frame_buf = FrameBuffer()
running = True

def capture_thread():
    cap = cv2.VideoCapture(0)
    while running:
        ret, frame = cap.read()
        if ret:
            frame_buf.set_copy(frame)  # 存副本，避免 OpenCV 复用缓冲区
    cap.release()

def process_thread():
    while running:
        frame, ts = frame_buf.get_copy()
        if frame is not None:
            # 处理帧（可能慢于采集速度，自动丢帧）
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow("processed", gray)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        time.sleep(0.001)

t1 = threading.Thread(target=capture_thread, daemon=True)
t2 = threading.Thread(target=process_thread, daemon=True)
t1.start()
t2.join()
running = False
cv2.destroyAllWindows()
```

### 示例 2：传感器数据缓存

```python
import threading, time, random
from hardware_io.frame_buffer import FrameBuffer

sensor_buf = FrameBuffer()

def read_sensor():
    while True:
        value = random.uniform(20.0, 25.0)
        sensor_buf.set(value)
        time.sleep(0.01)  # 100Hz 采样

threading.Thread(target=read_sensor, daemon=True).start()

# 主线程按需读取（可能 10Hz，远慢于采样率）
while True:
    value, ts = sensor_buf.get()
    if value is not None:
        print(f"温度: {value:.2f}°C ({sensor_buf.age_ms:.0f}ms ago)")
    time.sleep(0.1)
```

### 示例 3：帧率统计

```python
buf = FrameBuffer()
last_count = 0
last_time = time.time()

while True:
    # ... 某处持续 buf.set(frame) ...

    now = time.time()
    elapsed = now - last_time
    if elapsed >= 1.0:
        current_count = buf.frame_count
        fps = (current_count - last_count) / elapsed
        print(f"FPS: {fps:.1f}")
        last_count = current_count
        last_time = now
```

### 示例 4：配合二进制帧解析器使用

```python
import serial
from hardware_io.frame_buffer import FrameBuffer
from hardware_io.frame_protocol import StreamingFrameParser

ser = serial.Serial("COM4", 115200, timeout=0.05)
parser = StreamingFrameParser()
cmd_buf = FrameBuffer()  # 缓存最新收到的命令帧

while True:
    chunk = ser.read(256)
    if chunk:
        parser.feed(chunk)
        while True:
            frame = parser.get_frame()
            if frame is None:
                break
            cmd_buf.set(frame)  # 只保留最新命令

    # 主循环按需取最新命令
    cmd, _ = cmd_buf.get()
    if cmd is not None:
        handle_command(cmd.cmd, cmd.data)
```

## 线程安全保证

- 所有读写操作通过 `threading.Lock` 保护
- `get()` 返回值引用时，在锁内获取引用——对于不可变类型（`int`、`bytes`、`tuple`）安全；对于可变类型（`numpy.ndarray`、`list`、`dict`），调用方应使用 `get_copy()` 或自行加锁
- `frame_count` 在锁内递增，多线程写入计数准确

## 常见陷阱

1. **numpy 数组必须用 `set_copy()`**：OpenCV 的 `cap.read()` 可能复用内部缓冲区，直接 `set(frame)` 后下一帧读取会覆盖缓存内容。
2. **消费者不应持有引用后休眠**：`get()` 返回的引用可能被生产者的下一次 `set()` 替换（对于不可变类型是安全的，但可变类型有风险）。
3. **`frame_count` 不会在 `clear()` 后重置**：它是单调递增的累计计数器，适合计算帧率差值。
4. **无阻塞 API**：`get()` 在无值时立即返回 `(None, 0.0)`，不会阻塞等待。需要阻塞等待语义时，调用方自行轮询或使用 `threading.Event`。
