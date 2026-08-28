# 串口通信协议文档

本文档定义了串口摄像头控制器的通信协议，包括文本行协议和二进制帧协议两种模式。

## 通信参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 波特率 | 115200 | 可通过 `--baud` 参数修改 |
| 数据位 | 8 | |
| 校验位 | None | |
| 停止位 | 1 | |
| 流控 | None | |

控制器启动后会主动发送就绪通知：`READY:SerialCameraController v1.0\r\n`

---

## 一、文本行协议

适用于串口助手调试和简单 MCU 集成。每条命令以 ASCII 文本发送，以 `\r\n`（或 `\n`）结尾。

### 命令格式

```
<COMMAND>\r\n
```

命令不区分大小写，支持别名。

### 命令列表

#### 1. 抓图（CAP）

| 项目 | 内容 |
|------|------|
| 命令 | `CAP` |
| 别名 | `CAPTURE`, `C`, `SNAP`, `PHOTO` |
| 功能 | 抓取当前摄像头画面并保存为 JPG 文件 |
| 成功应答 | `OK:capture_20260828_120000_123.jpg` |
| 失败应答 | `ERR:NO_FRAME` |

**示例会话：**
```
主机: CAP\r\n
控制器: OK:capture_20260828_120000_123.jpg\r\n
```

#### 2. 开始录像（REC）

| 项目 | 内容 |
|------|------|
| 命令 | `REC` |
| 别名 | `RECORD`, `R`, `START` |
| 功能 | 开始录制 MP4 视频 |
| 成功应答 | `OK:RECORDING:record_20260828_120000.mp4` |
| 失败应答 | `ERR:ALREADY_RECORDING` |

#### 3. 停止录像（STOP）

| 项目 | 内容 |
|------|------|
| 命令 | `STOP` |
| 别名 | `S`, `END` |
| 功能 | 停止正在录制的视频 |
| 成功应答 | `OK:STOPPED:record_20260828_120000.mp4:5.2s:156frames` |
| 失败应答 | `ERR:NOT_RECORDING` |

应答字段说明：`OK:STOPPED:<文件名>:<时长>s:<帧数>frames`

#### 4. 查询状态（STAT）

| 项目 | 内容 |
|------|------|
| 命令 | `STAT` |
| 别名 | `STATUS`, `?` |
| 功能 | 查询控制器当前状态 |
| 空闲应答 | `STATUS:IDLE:OK(5ms_ago):port=COM4` |
| 录像中应答 | `STATUS:RECORDING:OK(3ms_ago):port=COM4:rec_dur=12.3s:frames=369` |

字段说明：
- `IDLE` / `RECORDING`：录像状态
- `OK(Xms_ago)`：最后一帧距今毫秒数（-1 表示无帧）
- `port=COM4`：当前串口号
- `rec_dur=Xs`：录像持续时间（仅录像中）
- `frames=N`：已录制帧数（仅录像中）

#### 5. 心跳测试（PING）

| 项目 | 内容 |
|------|------|
| 命令 | `PING` |
| 别名 | `HELLO` |
| 功能 | 测试通信链路 |
| 应答 | `PONG:SerialCameraController v1.0` |

#### 6. 帮助（HELP）

| 项目 | 内容 |
|------|------|
| 命令 | `HELP` |
| 功能 | 返回命令列表 |
| 应答 | `HELP:CAP=抓图 REC=录像 STOP=停止 STAT=状态` |

#### 7. 未知命令

收到无法识别的命令时返回：`ERR:UNKNOWN_CMD:<原始命令>`

### 控制器启动/停止通知

| 事件 | 消息 |
|------|------|
| 控制器就绪 | `READY:SerialCameraController v1.0\r\n` |
| 控制器退出 | `BYE\r\n` |

---

## 二、二进制帧协议

适用于嵌入式生产环境，具有帧同步和校验能力，抗干扰性强。

### 帧格式

```
┌──────┬──────┬─────┬─────┬──────────┬─────┬──────┬──────┐
│ 0xAA │ 0x55 │ CMD │ LEN │ DATA...  │ XOR │ 0x55 │ 0xAA │
└──────┴──────┴─────┴─────┴──────────┴─────┴──────┴──────┘
  帧头   帧头   命令  长度   数据域     校验  帧尾   帧尾
```

| 字段 | 长度 | 说明 |
|------|------|------|
| 帧头 | 2 字节 | 固定 `0xAA 0x55` |
| CMD | 1 字节 | 命令码 |
| LEN | 1 字节 | DATA 域长度（0-255） |
| DATA | 0-255 字节 | 命令参数（可为空） |
| XOR | 1 字节 | 校验和 = CMD ^ LEN ^ (DATA 各字节) |
| 帧尾 | 2 字节 | 固定 `0x55 0xAA` |

**最小帧长度**：7 字节（LEN=0，无 DATA）

### 命令码定义

#### 主机 → 控制器（请求）

| CMD | 名称 | DATA | 说明 |
|-----|------|------|------|
| 0x01 | CAPTURE | 无 | 抓图 |
| 0x02 | START_REC | 无 | 开始录像 |
| 0x03 | STOP_REC | 无 | 停止录像 |
| 0x10 | QUERY_STATUS | 无 | 查询状态 |

#### 控制器 → 主机（应答）

| CMD | 名称 | DATA | 说明 |
|-----|------|------|------|
| 0x81 | CAPTURE_RESP | 文件名（UTF-8） | 抓图结果 |
| 0x82 | REC_RESP | 1 字节状态 | 录像控制结果 |
| 0x90 | STATUS_RESP | 2 字节状态 | 状态查询结果 |
| 0xE0 | ERROR_RESP | 错误信息（UTF-8） | 错误应答 |

### 命令详情

#### 0x01 抓图

**请求帧：**
```
AA 55 01 00 <XOR> 55 AA
```
XOR = 0x01 ^ 0x00 = 0x01

**成功应答（0x81）：**
```
AA 55 81 <LEN> <文件名UTF-8> <XOR> 55 AA
```

**失败应答（0xE0）：**
```
AA 55 E0 <LEN> <错误信息UTF-8> <XOR> 55 AA
```

#### 0x02 开始录像

**请求帧：**
```
AA 55 02 00 <XOR> 55 AA
```

**应答（0x82）：**

DATA 为 1 字节：
- `0x01`：成功开始录像
- `0x00`：失败（已在录像中）

```
AA 55 82 01 01 <XOR> 55 AA    ← 成功
AA 55 82 01 00 <XOR> 55 AA    ← 失败
```

成功帧的 XOR = 0x82 ^ 0x01 ^ 0x01 = 0x82

#### 0x03 停止录像

**请求帧：**
```
AA 55 03 00 <XOR> 55 AA
```

**应答（0x82）：**

DATA 为 1 字节：
- `0x00`：成功停止录像
- `0xFF`：失败（未在录像）

#### 0x10 查询状态

**请求帧：**
```
AA 55 10 00 <XOR> 55 AA
```
XOR = 0x10 ^ 0x00 = 0x10

**应答（0x90）：**

DATA 为 2 字节：

| 字节 | 含义 | 值 |
|------|------|-----|
| DATA[0] | 录像状态 | 0=空闲, 1=录像中 |
| DATA[1] | 帧状态 | 0=无帧, 1=帧正常 |

```
AA 55 90 02 00 01 <XOR> 55 AA    ← 空闲，帧正常
AA 55 90 02 01 01 <XOR> 55 AA    ← 录像中，帧正常
```

空闲帧的 XOR = 0x90 ^ 0x02 ^ 0x00 ^ 0x01 = 0x93

### 校验和计算

XOR 校验从 CMD 字段开始，覆盖 CMD、LEN 和全部 DATA 字节：

```
XOR = CMD
XOR ^= LEN
for each byte in DATA:
    XOR ^= byte
```

**Python 实现：**
```python
def calc_xor(cmd, data):
    chk = cmd ^ len(data)
    for b in data:
        chk ^= b
    return chk
```

**C/Arduino 实现：**
```c
byte calc_xor(byte cmd, byte* data, byte len) {
    byte chk = cmd ^ len;
    for (byte i = 0; i < len; i++) {
        chk ^= data[i];
    }
    return chk;
}
```

### 帧同步与错误恢复

解析器按以下规则处理接收缓冲区：

1. **查找帧头**：在缓冲区中搜索 `AA 55`
2. **等待完整帧**：根据 LEN 计算帧总长度，等待数据到齐
3. **验证帧尾**：检查末尾 2 字节是否为 `55 AA`
4. **验证校验**：计算 XOR 并与接收的校验字节比较
5. **处理帧**：校验通过则执行业务逻辑，从缓冲区移除该帧
6. **重同步**：校验失败或帧尾不匹配时，丢弃帧头第一字节（0xAA），从下一字节重新搜索帧头
7. **溢出保护**：缓冲区超过 512 字节无有效帧时清空整个缓冲区

### 二进制帧构建示例

#### Python

```python
import serial

FRAME_HEADER = bytes([0xAA, 0x55])
FRAME_FOOTER = bytes([0x55, 0xAA])

def build_frame(cmd, data=b''):
    chk = cmd ^ len(data)
    for b in data:
        chk ^= b
    return FRAME_HEADER + bytes([cmd, len(data)]) + data + bytes([chk]) + FRAME_FOOTER

ser = serial.Serial('COM4', 115200)

# 发送抓图命令
ser.write(build_frame(0x01))

# 读取应答（实际使用中应循环读取并解析）
response = ser.read(64)
print(response.hex())
```

#### Arduino

```cpp
void sendFrame(byte cmd, byte* data, byte len) {
  Serial.write(0xAA);
  Serial.write(0x55);
  Serial.write(cmd);
  Serial.write(len);
  byte chk = cmd ^ len;
  for (byte i = 0; i < len; i++) {
    Serial.write(data[i]);
    chk ^= data[i];
  }
  Serial.write(chk);
  Serial.write(0x55);
  Serial.write(0xAA);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  sendFrame(0x01, nullptr, 0);  // 抓图
}
```

---

## 三、协议选择建议

| 场景 | 推荐协议 | 原因 |
|------|----------|------|
| 串口助手手动调试 | 文本 | 直接输入可读命令，无需编码 |
| Arduino/STM32 快速原型 | 文本 | `Serial.println("CAP")` 即可 |
| 工业环境/长距离通信 | 二进制 | 帧同步+校验防止噪声误触发 |
| MCU 启动有 bootloader 输出 | 二进制 | 文本可能被启动信息中的随机字符误触发 |
| 需要传输参数/扩展命令 | 二进制 | DATA 域支持结构化参数 |
| 多设备总线 | 二进制 | 帧头同步和校验更可靠 |

## 四、协议扩展指南

添加新命令的步骤：

1. 在代码中定义新的 CMD 常量（请求码使用 0x04-0x0F，应答码使用 0x83-0x8F）
2. 在 `_handle_binary_cmd()` 中添加处理分支
3. 在 `_handle_text_cmd()` 中添加文本命令别名（如需要）
4. 更新 HELP 应答文本
5. 更新本文档的命令列表

### 保留命令码范围

| 范围 | 用途 |
|------|------|
| 0x01-0x0F | 主机→控制器请求命令 |
| 0x10-0x1F | 主机→控制器查询命令 |
| 0x80-0x8F | 控制器→主机操作应答 |
| 0x90-0x9F | 控制器→主机状态应答 |
| 0xE0-0xEF | 控制器→主机错误应答 |
| 0xF0-0xFF | 保留 |
