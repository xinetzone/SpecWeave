# 生图服务镜像：同时承担「长驻 API」与「一次性 CLI」两种形态
FROM docker.io/library/python:3.12-slim

WORKDIR /work

# 先装依赖，利用构建缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 业务代码
COPY generate.py .

EXPOSE 8000

# 默认长驻形态；一次性用法由 `xuan-compose run --rm --entrypoint ...` 覆盖
CMD ["uvicorn", "generate:app", "--host", "0.0.0.0", "--port", "8000"]
