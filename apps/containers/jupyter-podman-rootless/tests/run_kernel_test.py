"""Start a kernel via jupyter_client and run the probe."""
from jupyter_client import KernelManager
km = KernelManager()
km.start_kernel()
kc = km.client()
kc.start_channels()
kc.wait_for_ready(timeout=10)
kc.execute(open('/tmp/kernel_probe.py').read())
import time; time.sleep(5)
# Check for any output messages
while True:
    try:
        msg = kc.get_shell_msg(timeout=2)
        c = msg.get('content', {})
        if msg['msg_type'] == 'stream':
            print(c.get('text', ''), end='')
        elif msg['msg_type'] == 'execute_result':
            print(c.get('data', {}).get('text/plain', ''))
        elif msg['msg_type'] == 'execute_error':
            print(f"ERROR: {c.get('ename')}: {c.get('evalue')}")
        else:
            break
    except Exception:
        break
print("=== file content ===")
try:
    print(open('/tmp/kern_env.txt').read())
except Exception as e:
    print(f"read error: {e}")
kc.stop_channels()
km.shutdown_kernel()
