"""Test: podman SDK connectivity from Jupyter kernel."""
import os
from podman import PodmanClient

print(f"CONTAINER_HOST = {os.environ.get('CONTAINER_HOST')}")
print(f"XDG_RUNTIME_DIR = {os.environ.get('XDG_RUNTIME_DIR')}")

try:
    client = PodmanClient.from_env(timeout=30)
    print(f"ping: {client.ping()}")
    print(f"images: {len(client.images.list())}")
    print(f"containers (all): {len(client.containers.list(all=True))}")
    print("✅ Podman SDK OK")
except Exception as e:
    print(f"❌ Podman SDK failed: {e}")
