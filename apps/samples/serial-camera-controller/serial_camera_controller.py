"""
串口控制摄像头抓图/录像 主程序
支持双协议：
  1. 文本行协议（串口助手直接可用）：CAP/REC/STOP/STAT + 换行
  2. 二进制帧协议（可靠嵌入式场景）：AA 55 CMD LEN DATA XOR 55 AA

硬件环境：CH340 (VID_1A86&PID_7523) + USB UVC Camera

使用方式：
  python serial_camera_controller.py              # 默认带GUI预览
  python serial_camera_controller.py --headless   # 无窗口后台模式
  python serial_camera_controller.py --port COM3  # 指定端口
  python serial_camera_controller.py --baud 9600  # 指定波特率

依赖：
  pip install opencv-python pyserial
"""
import cv2
import serial
import serial.tools.list_ports
import threading
import time
import argparse
import sys
from pathlib import Path
from collections import deque


# ============ 协议常量 ============
# 二进制帧协议
FRAME_HEADER = bytes([0xAA, 0x55])
FRAME_FOOTER = bytes([0x55, 0xAA])

CMD_CAPTURE = 0x01
CMD_START_REC = 0x02
CMD_STOP_REC = 0x03
CMD_QUERY_STATUS = 0x10

CMD_CAPTURE_RESP = 0x81
CMD_REC_RESP = 0x82
CMD_STATUS_RESP = 0x90
CMD_ERROR_RESP = 0xE0

# 摄像头默认参数
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480
DEFAULT_FPS = 30

# 默认保存目录：脚本所在目录下的 captures/
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SAVE_DIR = SCRIPT_DIR / "captures"


class SerialCameraController:
    """串口摄像头控制器 - 共享资源 + 多线程架构

    三线程设计：
    - camera_worker: 持续读取摄像头帧到缓存
    - serial_worker: 从串口读取字节到缓冲区
    - parser_worker: 从缓冲区解析命令并执行

    这种分离确保摄像头30fps采集不会阻塞串口命令处理，
    串口I/O等待也不会导致摄像头丢帧。
    """

    def __init__(self, port=None, baudrate=115200, width=DEFAULT_WIDTH,
                 height=DEFAULT_HEIGHT, fps=DEFAULT_FPS, headless=False,
                 save_dir=None):
        self.save_dir = Path(save_dir) if save_dir else DEFAULT_SAVE_DIR
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.width = width
        self.height = height
        self.fps = fps

        # 运行状态
        self.running = False
        self.is_recording = False
        self.video_writer = None
        self.record_start_time = None
        self.frame_count = 0

        # 最新帧缓存（线程安全）
        self._frame_lock = threading.Lock()
        self._latest_frame = None
        self._latest_frame_time = 0

        # 串口数据缓冲区
        self._serial_buffer = deque(maxlen=4096)
        self._serial_lock = threading.Lock()

        # 线程
        self._camera_thread = None
        self._serial_thread = None
        self._parser_thread = None

        # 自动探测端口
        self.port = port or self._find_ch340()
        if not self.port:
            raise RuntimeError(
                "未找到CH340串口设备！请确认设备已插入，或使用--port手动指定"
            )

        # 初始化串口
        self.ser = serial.Serial(
            port=self.port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.05,
            write_timeout=1
        )
        print(f"[+] 串口已打开: {self.port} @ {baudrate}bps")

        # 初始化摄像头（多后端尝试）
        self.cap = None
        self._init_camera()

    def _find_ch340(self):
        """自动查找CH340设备（VID:1A86 PID:7523）"""
        for port in serial.tools.list_ports.comports():
            if port.vid == 0x1A86 and port.pid == 0x7523:
                return port.device
            if 'CH340' in port.description or 'USB-SERIAL' in port.description:
                return port.device
        # 回退：列出所有可用端口，取第一个非COM1的
        ports = [p.device for p in serial.tools.list_ports.comports()]
        non_com1 = [p for p in ports if p != 'COM1']
        if non_com1:
            return non_com1[0]
        return None

    def _init_camera(self):
        """初始化摄像头（多后端尝试+分辨率自动降级）

        关键设计：某些UVC摄像头的cap.set()会静默失败（不报错但设置不生效），
        因此必须在set()后实际read()一帧来验证分辨率是否真正生效。
        """
        backends = [
            (cv2.CAP_MSMF, "MediaFoundation"),
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_ANY, "Auto"),
        ]
        # 分辨率降级列表
        candidate_resolutions = [
            (self.width, self.height),
            (640, 480),
            (800, 600),
            (1024, 768),
            (1280, 720),
            (320, 240),
        ]
        # 去重
        seen = set()
        resolutions = []
        for w, h in candidate_resolutions:
            if (w, h) not in seen:
                seen.add((w, h))
                resolutions.append((w, h))

        for backend_id, name in backends:
            print(f"[*] 尝试摄像头后端: {name}...", end=" ")
            cap = cv2.VideoCapture(0, backend_id)
            if not cap.isOpened():
                print("❌ 无法打开")
                continue

            # 依次尝试各分辨率
            working_res = None
            for w, h in resolutions:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
                cap.set(cv2.CAP_PROP_FPS, self.fps)
                # 设置后验证是否生效
                try:
                    ret, frame = cap.read()
                    if ret and frame is not None and frame.size > 0:
                        actual_h, actual_w = frame.shape[:2]
                        if actual_w >= w // 2 and actual_h >= h // 2:
                            working_res = (actual_w, actual_h)
                            break
                except cv2.error:
                    continue

            if working_res:
                self.cap = cap
                actual_w, actual_h = working_res
                actual_fps = cap.get(cv2.CAP_PROP_FPS) or self.fps
                self.width = actual_w
                self.height = actual_h
                self.fps = int(actual_fps) if actual_fps > 0 else self.fps
                print(f"✅ 成功 ({actual_w}x{actual_h} @ {self.fps}fps)")
                return
            else:
                cap.release()
                print("❌ 分辨率不兼容")
        raise RuntimeError("无法打开摄像头！所有后端和分辨率组合均失败")

    def _camera_worker(self):
        """摄像头读取线程：持续更新最新帧缓存（带异常恢复）"""
        print("[*] 摄像头线程已启动")
        consecutive_errors = 0
        while self.running:
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None and frame.size > 0:
                    consecutive_errors = 0
                    with self._frame_lock:
                        self._latest_frame = frame.copy()
                        self._latest_frame_time = time.time()
                    # 录像写入
                    if self.is_recording and self.video_writer is not None:
                        try:
                            self.video_writer.write(frame)
                            self.frame_count += 1
                        except Exception as e:
                            print(f"[!] 录像写入错误: {e}")
                else:
                    time.sleep(0.005)
            except cv2.error as e:
                consecutive_errors += 1
                if consecutive_errors <= 3:
                    print(f"[!] 摄像头读取错误({consecutive_errors}): {e}")
                if consecutive_errors > 30:
                    print("[!] 摄像头连续错误过多，尝试重新初始化...")
                    try:
                        self.cap.release()
                    except:
                        pass
                    time.sleep(0.5)
                    try:
                        self._init_camera()
                        consecutive_errors = 0
                        print("[+] 摄像头重新初始化成功")
                    except Exception as reinit_err:
                        print(f"[!] 重新初始化失败: {reinit_err}")
                        time.sleep(1)
                time.sleep(0.01)
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors <= 3:
                    print(f"[!] 摄像头线程异常: {e}")
                time.sleep(0.01)
        print("[*] 摄像头线程已退出")

    def _serial_worker(self):
        """串口读取线程：仅读字节到缓冲区，不解析"""
        print("[*] 串口读取线程已启动，等待命令...")
        while self.running:
            try:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    with self._serial_lock:
                        for b in data:
                            self._serial_buffer.append(b)
                else:
                    time.sleep(0.005)
            except Exception as e:
                print(f"[!] 串口读取错误: {e}")
                time.sleep(0.1)
        print("[*] 串口读取线程已退出")

    def _parser_worker(self):
        """命令解析线程：从缓冲区解析文本协议和二进制帧

        解析优先级：二进制帧 > 文本行
        二进制帧使用帧头同步+XOR校验，防止噪声/bootloader输出误触发
        """
        print("[*] 命令解析线程已启动")

        while self.running:
            with self._serial_lock:
                available = len(self._serial_buffer)

            if available == 0:
                time.sleep(0.01)
                continue

            # 先尝试二进制帧同步（查找帧头AA 55）
            with self._serial_lock:
                buf_bytes = bytes(self._serial_buffer)

            # 二进制帧解析
            header_pos = buf_bytes.find(FRAME_HEADER)
            if header_pos >= 0 and len(buf_bytes) >= header_pos + 7:
                cmd = buf_bytes[header_pos + 2]
                data_len = buf_bytes[header_pos + 3]
                frame_end = header_pos + 4 + data_len + 1 + 2
                if frame_end <= len(buf_bytes):
                    if (buf_bytes[frame_end-2] == FRAME_FOOTER[0] and
                        buf_bytes[frame_end-1] == FRAME_FOOTER[1]):
                        data = buf_bytes[header_pos+4 : header_pos+4+data_len]
                        chk_calc = cmd ^ data_len
                        for b in data:
                            chk_calc ^= b
                        chk_recv = buf_bytes[header_pos+4+data_len]
                        if chk_calc == chk_recv:
                            with self._serial_lock:
                                for _ in range(frame_end):
                                    self._serial_buffer.popleft()
                            self._handle_binary_cmd(cmd, data)
                            continue
                        else:
                            with self._serial_lock:
                                for _ in range(header_pos + 1):
                                    self._serial_buffer.popleft()
                            continue
                    else:
                        with self._serial_lock:
                            for _ in range(header_pos + 1):
                                self._serial_buffer.popleft()
                        continue

            # 文本行协议解析
            nl_pos = -1
            for i, b in enumerate(buf_bytes):
                if b in (0x0A, 0x0D):
                    nl_pos = i
                    break

            if nl_pos > 0:
                line_bytes = buf_bytes[:nl_pos]
                with self._serial_lock:
                    for _ in range(nl_pos + 1):
                        self._serial_buffer.popleft()
                try:
                    line = line_bytes.decode('ascii', errors='ignore').strip().upper()
                    if line:
                        self._handle_text_cmd(line)
                except:
                    pass
                continue

            # 缓冲区溢出保护
            with self._serial_lock:
                if len(self._serial_buffer) > 512:
                    self._serial_buffer.clear()

            time.sleep(0.005)

        print("[*] 命令解析线程已退出")

    def _get_latest_frame(self):
        """线程安全获取最新帧"""
        with self._frame_lock:
            if self._latest_frame is not None:
                return self._latest_frame.copy(), self._latest_frame_time
            return None, 0

    def _send_text_response(self, msg):
        """发送文本应答"""
        try:
            line = (msg + '\r\n').encode('ascii')
            self.ser.write(line)
            print(f"[TX] {msg}")
        except Exception as e:
            print(f"[!] 串口发送失败: {e}")

    def _send_binary_response(self, cmd, data=b''):
        """发送二进制帧应答"""
        try:
            chk = cmd ^ len(data)
            for b in data:
                chk ^= b
            frame = FRAME_HEADER + bytes([cmd, len(data)]) + data + bytes([chk]) + FRAME_FOOTER
            self.ser.write(frame)
            print(f"[TX] BIN cmd=0x{cmd:02X} len={len(data)}")
        except Exception as e:
            print(f"[!] 串口发送失败: {e}")

    def _handle_text_cmd(self, cmd):
        """处理文本命令"""
        print(f"[RX] TXT: {cmd}")
        if cmd in ('CAP', 'CAPTURE', 'C', 'SNAP', 'PHOTO'):
            self.cmd_capture()
        elif cmd in ('REC', 'RECORD', 'R', 'START'):
            self.cmd_start_record()
        elif cmd in ('STOP', 'S', 'END'):
            self.cmd_stop_record()
        elif cmd in ('STAT', 'STATUS', '?'):
            self.cmd_query_status()
        elif cmd in ('PING', 'HELLO'):
            self._send_text_response("PONG:SerialCameraController v1.0")
        elif cmd in ('HELP', '?HELP'):
            self._send_text_response("HELP:CAP=抓图 REC=录像 STOP=停止 STAT=状态")
        else:
            self._send_text_response(f"ERR:UNKNOWN_CMD:{cmd}")

    def _handle_binary_cmd(self, cmd, data):
        """处理二进制命令"""
        print(f"[RX] BIN: cmd=0x{cmd:02X} data_len={len(data)}")
        if cmd == CMD_CAPTURE:
            filename, err = self._do_capture()
            if filename:
                resp_data = filename.encode('utf-8')
                self._send_binary_response(CMD_CAPTURE_RESP, resp_data)
            else:
                self._send_binary_response(CMD_ERROR_RESP, str(err).encode('utf-8'))
        elif cmd == CMD_START_REC:
            ok, msg = self._do_start_record()
            self._send_binary_response(CMD_REC_RESP, b'\x01' if ok else b'\x00')
        elif cmd == CMD_STOP_REC:
            ok, info = self._do_stop_record()
            self._send_binary_response(CMD_REC_RESP, b'\x00' if ok else b'\xFF')
        elif cmd == CMD_QUERY_STATUS:
            recording = 1 if self.is_recording else 0
            frame_ok = 1 if self._latest_frame is not None else 0
            stat = bytes([recording, frame_ok])
            self._send_binary_response(CMD_STATUS_RESP, stat)
        else:
            self._send_binary_response(CMD_ERROR_RESP, b'UNKNOWN_CMD')

    def _do_capture(self):
        """执行抓图：保存最新帧到文件"""
        frame, ts = self._get_latest_frame()
        if frame is None:
            return None, "NO_FRAME"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        ms = int((ts - int(ts)) * 1000) if ts > 0 else 0
        filename = f"capture_{timestamp}_{ms:03d}.jpg"
        filepath = self.save_dir / filename
        cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"[📸] 抓图保存: {filepath}")
        return filename, None

    def cmd_capture(self):
        """抓图命令（文本协议入口）"""
        filename, err = self._do_capture()
        if filename:
            self._send_text_response(f"OK:{filename}")
        else:
            self._send_text_response(f"ERR:{err}")

    def _do_start_record(self):
        """开始录像"""
        if self.is_recording:
            return False, "ALREADY_RECORDING"
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"record_{timestamp}.mp4"
        filepath = self.save_dir / filename
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        actual_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS) or self.fps
        self.video_writer = cv2.VideoWriter(
            str(filepath), fourcc, actual_fps, (actual_w, actual_h)
        )
        self.is_recording = True
        self.record_start_time = time.time()
        self.frame_count = 0
        self.current_record_file = filename
        print(f"[🎬] 开始录像: {filepath}")
        return True, filename

    def cmd_start_record(self):
        ok, msg = self._do_start_record()
        if ok:
            self._send_text_response(f"OK:RECORDING:{msg}")
        else:
            self._send_text_response(f"ERR:{msg}")

    def _do_stop_record(self):
        """停止录像"""
        if not self.is_recording:
            return False, "NOT_RECORDING"
        self.is_recording = False
        duration = time.time() - self.record_start_time if self.record_start_time else 0
        filename = getattr(self, 'current_record_file', 'unknown.mp4')
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        print(f"[⏹]  录像停止: {filename}, 时长={duration:.1f}s, 帧数={self.frame_count}")
        return True, (filename, duration, self.frame_count)

    def cmd_stop_record(self):
        ok, info = self._do_stop_record()
        if ok:
            filename, duration, frames = info
            self._send_text_response(f"OK:STOPPED:{filename}:{duration:.1f}s:{frames}frames")
        else:
            self._send_text_response(f"ERR:{info}")

    def cmd_query_status(self):
        frame, ts = self._get_latest_frame()
        frame_age = (time.time() - ts) * 1000 if ts > 0 else -1
        rec_status = "RECORDING" if self.is_recording else "IDLE"
        frame_status = f"OK({frame_age:.0f}ms_ago)" if frame is not None else "NO_FRAME"
        msg = f"STATUS:{rec_status}:{frame_status}:port={self.port}"
        if self.is_recording:
            dur = time.time() - self.record_start_time if self.record_start_time else 0
            msg += f":rec_dur={dur:.1f}s:frames={self.frame_count}"
        self._send_text_response(msg)

    def start(self):
        """启动控制器"""
        self.running = True
        self._camera_thread = threading.Thread(target=self._camera_worker, daemon=True)
        self._serial_thread = threading.Thread(target=self._serial_worker, daemon=True)
        self._parser_thread = threading.Thread(target=self._parser_worker, daemon=True)
        self._camera_thread.start()
        self._serial_thread.start()
        self._parser_thread.start()

        # 等待摄像头就绪
        print("[*] 等待摄像头就绪...")
        for _ in range(30):
            frame, _ = self._get_latest_frame()
            if frame is not None:
                break
            time.sleep(0.1)

        # 发送就绪通知
        self._send_text_response("READY:SerialCameraController v1.0")
        print()
        print("=" * 60)
        print("串口摄像头控制器已启动！")
        print(f"  串口: {self.port}")
        print(f"  保存目录: {self.save_dir}")
        print(f"  GUI预览: {'关闭(headless)' if self.headless else '开启'}")
        print()
        print("  文本命令（串口助手发送）:")
        print("    CAP      - 抓图")
        print("    REC      - 开始录像")
        print("    STOP     - 停止录像")
        print("    STAT     - 查询状态")
        print("    PING     - 心跳测试")
        print()
        print("  本地快捷键（GUI窗口中）:")
        print("    q=退出  s=抓图  r=录像  space=状态")
        print("=" * 60)
        print()

    def run_gui_loop(self):
        """GUI预览主循环（headless模式跳过）"""
        if self.headless:
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n[*] Ctrl+C 中断")
            return

        window_name = "Serial Camera Controller (q=quit s=snap r=rec/stop)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        try:
            while self.running:
                frame, ts = self._get_latest_frame()
                if frame is not None:
                    display = frame.copy()
                    h, w = display.shape[:2]
                    status_text = f"{w}x{h}"
                    if self.is_recording:
                        dur = time.time() - self.record_start_time if self.record_start_time else 0
                        cv2.circle(display, (w-30, 30), 12, (0, 0, 255), -1)
                        status_text += f" | REC {dur:.1f}s {self.frame_count}f"
                        cv2.putText(display, status_text, (w-350, 38),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    else:
                        status_text += " | IDLE"
                        cv2.putText(display, status_text, (w-250, 38),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    cv2.imshow(window_name, display)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("[*] 本地用户请求退出")
                    break
                elif key == ord('s'):
                    self.cmd_capture()
                elif key == ord('r'):
                    if self.is_recording:
                        self.cmd_stop_record()
                    else:
                        self.cmd_start_record()
                elif key == ord(' '):
                    self.cmd_query_status()

        except KeyboardInterrupt:
            print("\n[*] Ctrl+C 中断")
        finally:
            cv2.destroyAllWindows()

    def stop(self):
        """停止控制器，释放资源"""
        print("[*] 正在停止控制器...")
        self.running = False
        if self.is_recording:
            self._do_stop_record()
        time.sleep(0.2)
        if self.cap:
            self.cap.release()
        if self.ser and self.ser.is_open:
            try:
                self._send_text_response("BYE")
                time.sleep(0.05)
                self.ser.close()
            except:
                pass
        cv2.destroyAllWindows()
        print("[+] 控制器已停止，资源已释放")


def main():
    parser = argparse.ArgumentParser(description="串口控制摄像头抓图/录像")
    parser.add_argument('--port', '-p', help='串口号（默认自动探测CH340）', default=None)
    parser.add_argument('--baud', '-b', type=int, help='波特率（默认115200）', default=115200)
    parser.add_argument('--width', type=int, default=DEFAULT_WIDTH)
    parser.add_argument('--height', type=int, default=DEFAULT_HEIGHT)
    parser.add_argument('--fps', type=int, default=DEFAULT_FPS)
    parser.add_argument('--headless', action='store_true', help='无GUI后台模式')
    parser.add_argument('--save-dir', default=None, help='图片/录像保存目录（默认./captures）')
    args = parser.parse_args()

    controller = None
    try:
        controller = SerialCameraController(
            port=args.port,
            baudrate=args.baud,
            width=args.width,
            height=args.height,
            fps=args.fps,
            headless=args.headless,
            save_dir=args.save_dir
        )
        controller.start()
        controller.run_gui_loop()
    except Exception as e:
        print(f"[!] 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if controller:
            controller.stop()


if __name__ == "__main__":
    main()
