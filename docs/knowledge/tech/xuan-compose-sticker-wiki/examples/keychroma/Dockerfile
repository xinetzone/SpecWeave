# 色幕去底一次性任务镜像（无服务、无常驻进程）
FROM docker.io/library/python:3.12-slim

WORKDIR /work

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY remove_chroma_key.py .

# 由 `xuan-compose run --rm keychroma -- <参数>` 传入输入输出
ENTRYPOINT ["python", "remove_chroma_key.py"]
