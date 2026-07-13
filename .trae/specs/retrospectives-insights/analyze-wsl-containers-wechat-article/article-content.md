---
id: wsl-containers-article-content
title: WSL Containers微信公众号文章原始内容
source: "https://mp.weixin.qq.com/s/ll92WZwrsxJ_6xSBm_1Bmw?from=industrynews&color_scheme=light#rd"
author: italks89 (UbuntuNews)
extracted_at: 2026-07-13
type: public-article
---

# 微软 WSL Containers 来了！不用装 Docker，Windows 原生跑 Linux 容器（一篇搞懂）

> **摘要** ：6 月底微软悄悄放了个大招——WSL Containers 正式开放公开预览。它内置在 WSL 里，语法和 Docker 几乎一样，不用额外安装、不用付费授权，Windows 上跑 Linux 容器从此"零门槛"。本文手把手教你装、带你认识核心命令、并说清它和 Docker Desktop 到底差在哪。
>
> ⏱ 阅读时长：约 8 分钟 ｜ 🐧 适合：WSL 用户、容器新手、被 Docker Desktop 授权费劝退的开发者

---

你有没有过这种纠结：在 Windows 上写代码，本地想跑个 Linux 容器做测试，结果先得装一个几百兆的 Docker Desktop；公司人数超过 250 人，还得为商业授权掏钱。

现在，这个痛点可能要被微软自己"端了"。

Build 2026 大会上，微软端出了一道硬菜—— **WSL Containers** 。6 月 29 日，它正式开放公开预览。一句话概括： **WSL 内置了一个原生、企业级、语法仿 Docker 的 Linux 容器运行时，你更新一下 WSL 就能用，不用装任何第三方引擎。**

今天这篇，就把它从"是什么"到"怎么用"给你讲透。

---

## 一、WSL Containers 到底是什么？

先澄清一个最大的误会： **它不是 WSL 3。**

功能公布时，社区一片"WSL 3 终于来了"的狂欢。WSL 产品经理 Craig Loewen 赶紧出来灭火：不存在所谓的 WSL 3，WSL Containers **不是 WSL 2 的继任者** ，而是基于现有 WSL 2 基础设施之上的一层 **新功能** 。

那它究竟是什么？

> **WSL Containers = 一个内置在 WSL 里的、企业就绪的 Linux 容器解决方案** ，让你在 Windows 上直接创建、运行、管理 Linux 容器， **无需额外安装 Docker 等第三方工具** 。

它跑的是标准的 **OCI 容器镜像** ——也就是你今天从 Docker Hub 拉的那些 `ubuntu` 、 `nginx` 、 `nvidia/cuda` ，换了个引擎照样能用。底层是在 Hyper-V 轻量虚拟机上跑 Linux 容器，和 WSL 2 用的是同一套内核机制。

---

## 二、两大核心组件

WSL Containers 由两部分组成：

### 1. wslc.exe —— 命令行工具（重点）

更新 WSL 后，这个二进制会自动加到 PATH 里，微软还贴心给了个别名 `container.exe` 。 **它的命令语法和 Docker 高度相似** ，所以你过去 `docker run` 、 `docker ps` 的肌肉记忆几乎可以无缝迁移。

### 2. WSL Container API —— 给程序员的"容器遥控器"

以 **NuGet 包** 形式分发，支持 **C / C++ / C#** 。Windows 上的原生应用可以 **用代码方式** 拉起、控制 Linux 容器——比如复用一段现成的 Linux 代码、在本地跑云上应用、或者限制某个 Linux 进程能访问多少宿主机资源。它还能和 MSBuild、CMake 集成，项目文件加几行配置，容器的构建部署就自动融进编译流程。

> 对大多数人来说， **wslc 命令行** 才是日常。API 那块是给 IDE、CI 工具链开发商用的，咱们了解即可。

---

## 三、3 分钟装好（手把手）

WSL Containers 走的是 **预发布通道（pre-release）** ，目前还在公开预览阶段。装法比想象中简单：

**第 1 步：以管理员身份打开 Windows 终端（PowerShell）**

右键开始菜单 → "终端(管理员)"，按 `Ctrl+Shift+1` 切到 PowerShell。

**第 2 步：确保 WSL 2 + 虚拟机平台已开启** （如果还没装）

```
Enable-WindowsOptionalFeature -Online -FeatureName "Microsoft-Windows-Subsystem-Linux","VirtualMachinePlatform"
```

装完按 `Y` 重启。

**第 3 步：升级到预发布版本**

```
wsl --update --pre-release
```

**第 4 步：重启 WSL 让更新生效**

```
wsl --shutdown
```

**第 5 步：验证安装**

```
wslc version
```

看到版本号 **2.9.3.0** 左右，就说明 wslc 已就位。再跑个内置镜像确认环境正常：

```
wslc run --rm hello-world
```

看到 "Hello" 字样，恭喜，容器环境通了。

> 💡 **系统要求** ：Windows 11（或 Win10 22H2+）；64 位且支持 SLAT 的处理器；内存至少 4GB（建议 8–16GB）；BIOS/UEFI 里 **开启虚拟化** 。注意它 **不要求 Copilot+ PC** ，但依赖现代虚拟化支持。

---

## 四、常用命令速查（对照 Docker）

这是最实用的一节。左边是你熟悉的 Docker，右边是 wslc 的对应写法：

| 用途 | Docker 命令 | WSL Containers 命令 |
| --- | --- | --- |
| 运行容器 | `docker run --rm -it ubuntu bash` | `wslc run --rm -it ubuntu:latest bash` |
| 跑个 Web 服务 | `docker run -d -p 8080:80 nginx` | `wslc run -it --rm -d -p 8080:80 --name web nginx` |
| 列出容器 | `docker ps` | `wslc container ps` |
| 列出镜像 | `docker images` | `wslc image ls` |
| 停止容器 | `docker stop web` | `wslc container stop web` |
| 构建镜像 | `docker build -t myapp .` | `wslc build -t myapp:latest .` |
| 调用 GPU | `docker run --gpus all ...` | `wslc run --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi` |

几个能直接抄的去味例子：

```
# 在临时 Ubuntu 容器里跑句命令
wslc run --rm -it ubuntu:latest bash -c "echo Hello from WSL container!"

# 起个 Nginx 并映射端口，浏览器开 localhost:8080 就能访问
wslc run -it --rm -d -p 8080:80 --name web nginx

# 看正在跑的容器（自动生成的名字像 mossy_sawtooth 这种）
wslc container ps

# AI/ML 场景：把宿主机 GPU 透传给容器
wslc run --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

看完你会发现： **几乎就是把 `docker` 换成 `wslc` ，参数一模一样。** 迁移成本极低。

---

## 五、它和 Docker Desktop 到底差在哪？

这是大家最关心的问题。一张表看清：

| 对比项 | WSL Containers | Docker Desktop |
| --- | --- | --- |
| **安装** | 内置 WSL 更新，自动获得 | 需额外下载安装 |
| **价格** | 免费（内置 Windows） | 商业版 24/人（250 人以上企业需付费） |
| **企业管控** | GPO/ADMX 模板 + 镜像允许列表 + Intune（即将上线）+ Defender | 需 Docker Business 才较完善 |
| **隔离模型** | 每个调用 API 的应用有 **独立轻量 VM** （Hyper-V） | 所有容器跑在 **单个共享 VM** 里 |
| **功能完整度** | 预览阶段较基础 | 非常完整（Compose / GUI / Scout） |
| **GPU 支持** | 支持（CDI 方式） | 支持（NVIDIA） |
| **Docker Compose** | 首发暂不支持 | 支持 |
| **GUI** | 纯 CLI，无界面 | 有图形界面 |

微软的态度很明确： **"我们不是在取代 Docker Desktop。"** Loewen 说，Docker 提供了优秀的 GUI、Compose 和 Scout 安全扫描；WSL Containers 是给"想要极简 CLI 工作流"或"CI/CD 场景不愿装整套 Docker 引擎"的开发者准备的。而且它会支持 **Docker 兼容的 socket 转发** ，所以 VS Code 的 Docker 插件照样能用。

简单说： **重度依赖 Compose 编排、喜欢图形界面的团队，Docker Desktop 还得留着；只想本地 `run` 一下容器、或者被授权费劝退的，可以换 wslc 了。**

---

## 六、性能实测：比 Docker Desktop 快多少？

微软放出的基准测试（同硬件：i9-14900K / 64GB / 990 Pro）很有意思：

| 指标 | WSL Containers | Docker Desktop (WSL2) |
| --- | --- | --- |
| 冷启动 nginx | **180 ms** | 2.1 s |
| 热启动 | **50 ms** | 800 ms |
| Node 构建（1000 模块） | **12.3 s** | 15.8 s |
| 跨 OS 文件读（1GB） | 8.2 s | 8.5 s |

启动快，是因为 wslc 直接复用 WSL 2 已有的内核，不用再另外起一个 Docker 虚拟机。不过 **跨系统文件读写** 这块两者几乎打平——毕竟底层都是同一套 9P 文件系统，微软也承认这是已知短板。

---

## 七、对 Ubuntu 用户意味着什么？

重点来了，和咱们读者关系最大：

**`ubuntu:latest` 一行就能拉起。** 无论是做开发测试、跑 CI、还是本地搭服务，Ubuntu 都是容器世界里最常见的 base image 之一。以前要装 Docker Desktop，现在一个 `wslc run -it ubuntu:latest bash` 就进去了。

再往大了看——这其实是咱们 7/11 那篇《苹果发 Container，微软推 WSL Containers，为什么说 Linux 赢了》的 **最佳注脚** ：连微软和苹果都在自家系统里原生拥抱 Linux 容器，Ubuntu 作为容器第一梯队的基础镜像，含金量是真在涨。

> 📌 还没看过那篇观点文的，建议搭配食用：\[《苹果 Container + 微软 WSL Containers，Linux 已经赢了？》\]

---

## 八、现在能不能上？预览阶段的 3 个限制

理智提醒，别一股脑全换：

1. 1\. **没有 Docker Compose** ：多容器编排（ `compose.yml` ）目前不支持，依赖它的工作流暂时换不了。
2. 2\. **纯 CLI，没有图形界面** ：喜欢点界面的朋友得再等等。
3. 3\. **文档还比较稀疏** ：处于公开预览，偶发 bug 难免；官方文档也在持续补齐中。

另外它 **要求 Windows 11** （Hyper-V 依赖），Win10 用户得先升系统。

---

## 总结

WSL Containers 是微软"把 Linux 吃进 Windows"战略的又一步：WSL 1 让 Linux 二进制能跑、WSL 2 给完整内核、Build 2026 又补齐了原生容器层。 **对普通开发者最实在的好处就一句：本地跑 Linux 容器，不用装 Docker、不用交授权费、命令还几乎一样。**

想现在就试？ `wsl --update --pre-release` 跑起来，然后 `wslc run --rm hello-world` ，你的第一个 WSL 容器就起来了。

---

💡 **UbuntuNews** ｜ 资讯 · 工具 · 教程 · 社区
🐧 关注我们，获取更多 Ubuntu / Linux 技术干货
💬 加入 QQ 群 / 频道，与全国爱好者交流成长
❤️ 觉得有用？点个"在看"分享给更多人！

---

📚 **延伸阅读**

WSL 根本没有"开机"！一文看懂它和普通 Ubuntu 启动的 7 大本质区别

- [WSL 根本没有"开机"！一文看懂它和普通 Ubuntu 启动的 7 大本质区别](https://mp.weixin.qq.com/s?__biz=MjM5NjY1NjYyMQ==&mid=2650154210&idx=1&sn=e978ddc73de75f9339bae5afa0c60f93&scene=21#wechat_redirect)
- [Ubuntu官方Workshop：一条YAML，开发环境秒级复现](https://mp.weixin.qq.com/s?__biz=MjM5NjY1NjYyMQ==&mid=2650154203&idx=1&sn=517ab9c4bc9c4c473ad2bc365c6ba523&scene=21#wechat_redirect)
- [微软把 Linux 命令"搬"进了 Windows！原生支持 ls/cp/grep，无需 WSL](https://mp.weixin.qq.com/s?__biz=MjM5NjY1NjYyMQ==&mid=2650154198&idx=1&sn=2453003de89686796403b6236e97f705&scene=21#wechat_redirect)
- [告别命令行管理 WSL！WSL Dashboard v0.9.1 一键搞定：磁盘瘦身、端口转发、USB 直通](https://mp.weixin.qq.com/s?__biz=MjM5NjY1NjYyMQ==&mid=2650154192&idx=1&sn=abdd5ee3f23405433b5adde9c71a12f3&scene=21#wechat_redirect)
