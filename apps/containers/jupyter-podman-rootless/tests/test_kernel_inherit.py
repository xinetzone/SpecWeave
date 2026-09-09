"""Minimal env test - write to file so we can read it."""
import os, json, sys
with open('/tmp/kernel_env_test.txt', 'w') as f:
    f.write(f"CONTAINER_HOST={os.environ.get('CONTAINER_HOST')}\n")
    f.write(f"XDG_RUNTIME_DIR={os.environ.get('XDG_RUNTIME_DIR')}\n")
try:
    from podman import PodmanClient
    client = PodmanClient.from_env(timeout=30)
    f.write(f"ping={client.ping()}\n")
    f.write(f"images={len(client.images.list())}\n")
    f.write("OK\n")
except Exception as e:
    f.write(f"FAIL: {e}\n")
