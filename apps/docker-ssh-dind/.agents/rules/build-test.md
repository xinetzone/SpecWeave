---
id: "dind-build-test-rules"
title: "构建与测试规范"
---
# 构建与测试规范（docker-ssh-dind）

## 构建命令

```bash
# 标准构建
docker build -t dind-ssh -f Containerfile .

# 构建时不使用缓存（调试用）
docker build --no-cache -t dind-ssh -f Containerfile .

# 构建参数（如需）
docker build -t dind-ssh -f Containerfile \
  --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) .
```

## 运行命令

```bash
# 基本运行（随机root密码，查看日志获取）
docker run -d --privileged -p 2222:22 \
  -v dind-data:/var/lib/docker --name dind-test dind-ssh

# 指定root密码
docker run -d --privileged -p 2222:22 \
  -v dind-data:/var/lib/docker \
  -e ROOT_PASSWORD=mypassword --name dind-test dind-ssh

# 注入SSH公钥
docker run -d --privileged -p 2222:22 \
  -v dind-data:/var/lib/docker \
  -e SSH_PUBLIC_KEY="$(cat ~/.ssh/id_rsa.pub)" --name dind-test dind-ssh

# 调试模式
docker run -d --privileged -p 2222:22 \
  -v dind-data:/var/lib/docker \
  -e ROOT_PASSWORD=pass -e DEBUG=1 --name dind-test dind-ssh
```

**注意**：DinD必须使用`--privileged`标志运行。

## 验证流程

构建后必须通过以下验证：

### 1. 构建验证
```bash
# 构建日志中无ERROR
docker build -t dind-ssh -f Containerfile . 2>&1 | grep -i error
# 期望：无输出
```

### 2. 容器启动验证
```bash
# 启动容器
docker run -d --privileged -p 2222:22 \
  -e ROOT_PASSWORD=test123 --name dind-test dind-ssh

# 等待启动完成（查看日志）
docker logs dind-test
# 期望：看到 "Container ready!" 和 "[OK] Docker daemon is ready!"
```

### 3. SSH连接验证
```bash
# 使用sshpass或手动输入密码
sshpass -p test123 ssh -o StrictHostKeyChecking=no -p 2222 root@localhost echo "SSH OK"
# 期望：SSH OK
```

### 4. Docker功能验证
```bash
# 在容器内运行docker命令
docker exec dind-test docker version
docker exec dind-test docker run --rm hello-world
# 期望：成功拉取并运行hello-world
```

### 5. ai用户验证
```bash
# ai用户存在且在docker组
docker exec dind-test id ai
# 期望：uid=1000(ai) gid=...(docker) groups=...(docker),...(sudo)

# ai用户免密sudo
docker exec dind-test su - ai -c "sudo -n whoami"
# 期望：root

# ai用户可运行docker
docker exec dind-test su - ai -c "docker ps"
# 期望：正常输出容器列表
```

### 6. 中文环境验证
```bash
docker exec dind-test locale | grep LANG
# 期望：LANG=zh_CN.UTF-8

docker exec dind-test date
# 期望：显示中国时区时间（CST）
```

### 7. 清理
```bash
docker stop dind-test && docker rm dind-test
docker volume rm dind-data  # 可选：清理数据卷
```

## 常见问题排查

| 问题 | 排查命令 | 常见原因 |
|------|---------|---------|
| Docker启动失败 | `docker logs <name>` 查看dockerd.log | 未使用--privileged、cgroup未挂载 |
| SSH连接被拒 | `docker exec <name> netstat -tlnp | grep 22` | sshd未启动、端口未映射 |
| ai用户无法运行docker | `docker exec <name> ls -la /var/run/docker.sock` | docker.sock权限不是666 |
| 中文乱码 | `docker exec <name> locale` | locale未正确生成 |
| 容器启动后立即退出 | `docker logs <name>` | entrypoint.sh语法错误或Docker启动失败 |
