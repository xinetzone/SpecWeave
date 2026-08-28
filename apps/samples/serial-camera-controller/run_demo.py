"""
GUI 演示启动器

启动控制器后，等待3秒自动发送一次CAP抓图命令，
验证整个串口→命令解析→摄像头抓图→文件保存链路。

使用方式：
  python run_demo.py
"""
import threading
import time
from serial_camera_controller import SerialCameraController


def auto_capture_demo(controller, delay=3.0):
    """延迟后自动触发一次CAP命令（模拟串口助手发送）"""
    time.sleep(delay)
    print(f"\n[demo] 自动发送 CAP 命令（模拟串口助手，延迟{delay}s）...")
    controller._handle_text_cmd("CAP")
    print("[demo] CAP命令执行完毕，GUI窗口继续运行。\n")


def main():
    print("=" * 60)
    print("  串口摄像头控制器 - 自动CAP演示")
    print("=" * 60)
    print()

    controller = None
    try:
        controller = SerialCameraController(headless=False)
        controller.start()

        # 后台线程延迟自动触发CAP
        demo_thread = threading.Thread(
            target=auto_capture_demo, args=(controller, 3.0), daemon=True
        )
        demo_thread.start()

        # GUI主循环（阻塞直到用户按q）
        controller.run_gui_loop()

    except Exception as e:
        print(f"[!] 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if controller:
            controller.stop()
        print("\n[demo] 演示结束。")


if __name__ == "__main__":
    main()
