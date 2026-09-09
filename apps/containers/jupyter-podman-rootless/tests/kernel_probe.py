import os
with open('/tmp/kern_env.txt', 'w') as f:
    f.write(f"CONTAINER_HOST={os.environ.get('CONTAINER_HOST')}\n")
    f.write(f"XDG_RUNTIME_DIR={os.environ.get('XDG_RUNTIME_DIR')}\n")
    try:
        from podman import PodmanClient
        c = PodmanClient.from_env(timeout=30)
        f.write(f"ping={c.ping()} images={len(c.images.list())}\n")
        f.write("OK\n")
    except Exception as e:
        f.write(f"FAIL: {e}\n")
