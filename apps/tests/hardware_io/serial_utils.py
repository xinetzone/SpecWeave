"""串口设备发现与健壮打开.

封装了串口枚举、VID/PID 匹配、CH340 自动探测等模式。核心 API:

- :func:`list_ports`: 列出系统中所有串口及其详细信息
- :func:`find_port_by_vid_pid`: 按 USB VID/PID 查找设备端口
- :func:`find_ch340_port`: 自动查找 CH340/CH341 串口
- :func:`open_serial`: 带默认参数的健壮串口打开

这些函数与具体业务逻辑无关，可用于任何 pyserial 项目。

示例::

    from hardware_io.serial_utils import find_ch340_port, open_serial

    port = find_ch340_port()
    if port:
        ser = open_serial(port, baudrate=115200)
        ser.write(b"PING\\r\\n")
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import serial
import serial.tools.list_ports


@dataclass(frozen=True)
class PortInfo:
    """串口设备信息."""

    device: str
    description: str
    hwid: str
    vid: Optional[int]
    pid: Optional[int]
    manufacturer: Optional[str]
    serial_number: Optional[str]


def list_ports() -> List[PortInfo]:
    """列出系统中所有可用串口.

    Returns:
        :class:`PortInfo` 列表。
    """
    result = []
    for p in serial.tools.list_ports.comports():
        result.append(
            PortInfo(
                device=p.device,
                description=p.description or "",
                hwid=p.hwid or "",
                vid=p.vid,
                pid=p.pid,
                manufacturer=p.manufacturer,
                serial_number=p.serial_number,
            )
        )
    return result


def find_port_by_vid_pid(
    vid: int,
    pid: Optional[int] = None,
) -> Optional[str]:
    """按 USB VID/PID 查找串口设备.

    Args:
        vid: USB 厂商标识 ID（如 CH340 的 0x1A86）。
        pid: USB 产品标识 ID（如 CH340 的 0x7523）。为 ``None`` 时仅匹配 VID。

    Returns:
        设备端口名（如 ``"COM4"``），未找到返回 ``None``。
    """
    for p in serial.tools.list_ports.comports():
        if p.vid == vid:
            if pid is None or p.pid == pid:
                return p.device
    return None


def find_port_by_description(keywords: List[str]) -> Optional[str]:
    """按描述符关键词查找串口设备（不区分大小写）.

    Args:
        keywords: 关键词列表，描述符中包含任一关键词即匹配。

    Returns:
        设备端口名，未找到返回 ``None``。
    """
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "").upper()
        for kw in keywords:
            if kw.upper() in desc:
                return p.device
    return None


def find_ch340_port() -> Optional[str]:
    """自动查找 CH340/CH341 USB 转串口设备.

    查找顺序：
    1. 精确匹配 VID=0x1A86, PID=0x7523（CH340/CH341）
    2. 描述符包含 "CH340" 或 "USB-SERIAL"
    3. 回退：若存在 COM4 则返回 COM4

    Returns:
        设备端口名，未找到返回 ``None``。
    """
    # 1. 精确 VID/PID 匹配
    port = find_port_by_vid_pid(0x1A86, 0x7523)
    if port:
        return port

    # 2. 描述符匹配
    port = find_port_by_description(["CH340", "CH341", "USB-SERIAL", "USB2.0-SERIAL"])
    if port:
        return port

    # 3. 回退：检查 COM4 是否存在
    available = [p.device for p in serial.tools.list_ports.comports()]
    if "COM4" in available:
        return "COM4"

    return None


def open_serial(
    port: str,
    baudrate: int = 115200,
    bytesize: int = serial.EIGHTBITS,
    parity: str = serial.PARITY_NONE,
    stopbits: float = serial.STOPBITS_ONE,
    timeout: float = 0.05,
    write_timeout: float = 1.0,
    rtscts: bool = False,
    dsrdtr: bool = False,
) -> serial.Serial:
    """打开串口（带常用默认参数）.

    Args:
        port: 端口名（如 ``"COM4"``）。
        baudrate: 波特率。
        bytesize: 数据位。
        parity: 校验位。
        stopbits: 停止位。
        timeout: 读超时（秒）。默认 0.05 适合非阻塞轮询。
        write_timeout: 写超时（秒）。
        rtscts: RTS/CTS 硬件流控。
        dsrdtr: DSR/DTR 硬件流控。

    Returns:
        已打开的 :class:`serial.Serial` 实例。

    Raises:
        serial.SerialException: 端口无法打开（被占用、不存在等）。
    """
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=bytesize,
        parity=parity,
        stopbits=stopbits,
        timeout=timeout,
        write_timeout=write_timeout,
        rtscts=rtscts,
        dsrdtr=dsrdtr,
    )
    return ser


def get_modem_signals(ser: serial.Serial) -> dict:
    """读取串口 MODEM 信号状态.

    Args:
        ser: 已打开的串口实例。

    Returns:
        包含 CTS/DSR/RI/CD 信号状态的字典。读取失败的信号值为 ``None``。
    """
    signals = {"cts": None, "dsr": None, "ri": None, "cd": None}
    try:
        signals["cts"] = ser.getCTS()
    except Exception:
        pass
    try:
        signals["dsr"] = ser.getDSR()
    except Exception:
        pass
    try:
        signals["ri"] = ser.getRI()
    except Exception:
        pass
    try:
        signals["cd"] = ser.getCD()
    except Exception:
        pass
    return signals
