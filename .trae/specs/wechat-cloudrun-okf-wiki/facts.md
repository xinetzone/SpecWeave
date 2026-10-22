---
type: spec-facts
theme: wechat-cloudrun-okf-wiki
source: https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/intro.html
pages_crawled: 145
captured_at: "2026-10-22"
status: complete
---

# 微信云托管官方文档 · 编号事实登记表（R 阶段）

> **信源**：微信开放文档「云服务 → 云托管」官方文档站，共 145 页（根 1 / basic 4 / quickstart 10 / guide 40 / development 51 / Billing 6 / scene 26 / practice 5 / info 2），采集日期 2026-10-22。
>
> **信源距离**：官方发布（一手）。价格为刊例价时点值；性能/成本表述均为**厂商自述**，已在条目内标注。
>
> **编号规则**：F-001 起连续编号，无跳号。本表是双份登记之一，另一份为 `projects/awesome-okf-xs/doc/bundles/jishu/iac/wxcloudrun/references/doc-source.md`。
>
> **撰写纪律**：每条仅陈述文档可逐字支撑的事实，不含因果推断词；数字、端口、命令、字段名、限制值逐字保留。

## 一、平台定位与架构模型

| F 编号 | 事实陈述 | 来源 URL |
|---|---|---|
| F-001 | 微信云托管是微信团队提供的以云原生为基础的免运维、高可用服务上云解决方案，无需服务器，1 分钟即可部署小程序/公众号服务端。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/intro.html |
| F-002 | 微信云托管使用 Docker 以及容器编排技术 Kubernetes 管理项目，K8S 的运维配置由微信云托管完全接手。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/overview.html |
| F-003 | 微信云托管的底层容器能力来自腾讯云托管，平台整合了腾讯云 TDSQL-C、腾讯云 COS 等腾讯云底层资源。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/info/faq.html |
| F-004 | 微信生态客户端（小程序、公众号）向云托管后端服务发送请求时自动经过微信接入层（内网），并附带微信校验的权威用户信息。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/overview.html |
| F-005 | 非微信生态客户端（普通 WEB 网页、APP）的请求经过微信云托管公网网关层，所有用户共用该网关层，并按域名转发到对应服务。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/overview.html |
| F-006 | 微信云托管提供默认公网域名，也可以接入自己备案好的自定义域名。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/overview.html |
| F-007 | 默认公网域名性能有限制，仅能支持接口测试使用，小程序后台无法配置使用默认公网域名。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/index.html |
| F-008 | 微信云托管与微信云开发是两套独立体系，云托管环境只能在微信云托管控制台看到，在微信开发者工具的云开发控制台和腾讯云控制台中均看不到。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/info/faq.html |
| F-009 | 云开发中的云托管能力已停止功能更新，仅支持存量业务继续运行。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/info/faq.html |
| F-010 | 必须先有微信小程序/公众号才可以开通微信云托管。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/info/faq.html |
| F-011 | 环境是微信云托管的最大单位，包含一整套资源（包括容器、数据库等），各个环境相互独立、资源隔离，不同环境的计费和资源包结算完全独立。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/noun.html |
| F-012 | 2022 年 7 月后创建的环境没有独立 VPC 的概念，微信云托管当前仅支持腾讯云上海地域 VPC。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/noun.html |
| F-013 | 微信云托管的容器最小规格为 0.25 核 0.5G。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/overview.html |
| F-014 | 突发场景下微信云托管支持 20s 内快速扩容。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/overview.html |
| F-015 | 容器规格是计费依据，无论容器实际使用率多少都按所声明的容器规格计费；弹性伸缩只产生容器实例数量的变化，单个容器的规格不会改变。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/noun.html |
| F-016 | 部署发布支持流水线、上传代码包、上传镜像 3 种发布方式。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/index.html |
| F-017 | 微信云托管按实际使用量计费，精确到 100 毫秒；文档称可用性超过 99.99%（厂商自述）。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/index.html |

## 二、资源模型、配额与运行边界

| F 编号 | 事实陈述 | 来源 URL |
|---|---|---|
| F-018 | 服务名称只能包含数字、小写字母和 `-`，只能以小写字母开头，最多 20 个字符，且不支持修改。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/index.html |
| F-019 | 每个环境支持最多创建 15 个服务。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/index.html |
| F-020 | 单个环境下总实例数量最大支持 28 个实例个数，不可特殊申请。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/env/index.html |
| F-021 | 单个环境下所有服务的 QPS（每秒并发请求数）最大为 500，超出可通过提交工单特殊申请。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/env/index.html |
| F-022 | 目前一个「小程序/公众号」账号最多支持创建 3 个微信云托管环境，仅第 1 个环境带有 3 个月免费额度。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/env/index.html |
| F-023 | 一个服务同一时间点只能存在 1 张发布单，如需发布其他版本需先取消发布或者结单。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/noun.html |
| F-024 | 一个服务下最多 2 个版本有流量（服务灰度过程中），超过 2 个的其他版本可以存在但没有流量接入。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/noun.html |
| F-025 | 监听端口必须为 1~61000 之间的整数且不能为 9100；微信云托管默认为 80 端口，如果没有找到则部署失败。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/noun.html |
| F-026 | 端口号由业务项目自行设定，系统无法自动获取，必须通过新建版本时在控制台填写来告知云托管。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/noun.html |
| F-027 | 一个服务只能设置一个端口，端口在「服务设置」中定义、部署时决定，该端口不暴露给调用方，公网域名收到请求后由云托管统一网关转发到对应端口。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/faq.html |
| F-028 | 扩缩容条件目前支持 CPU 使用率、内存使用率两种，默认值为 60%；每次扩缩容后冷却 15 秒再检测条件。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/noun.html |
| F-029 | 容器规格的内存与 CPU 搭配规则为 0.25 核配 0.5GB、0.5 核配 1GB、1 核配 2GB、2 核配 4GB、4 核配 8GB、8 核配 16GB、16 核配 32GB。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/pipeline.html |
| F-030 | 规格设置过低可能导致部署成功但频繁出现 500 错误；Java 服务相对较重，建议使用 1 核 2G 及以上规格。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/pipeline.html |
| F-031 | 定时扩缩容支持每日/每周/每月/不重复 4 种定时类型，支持添加 3 个自定义时间段；定时扩容实例副本数不能设置小于最小实例副本数且不可设置为 0。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/pipeline.html |
| F-032 | 日志采集路径可设置目录或文件，支持标准输出（stdout）以及 `*` 通配路径，多个路径用 `,`（半角逗号）分割；日志采集路径不能与 Dockerfile 中 volume 配置的路径相同。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/pipeline.html |
| F-033 | 日志检索支持全文检索、键值检索、模糊关键字检索，语法包含 key:value、A and B、A or B、not B、`>`、`>=`、`<`、`<=`、TO、`[]`、`{}`、exists，运算符优先级由高到低为 `:` > `"` > and > not > or。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/journal.html |
| F-034 | 构建阶段无报错日志、空白，大概率是构建超时（> 10 分钟）；微信云托管不支持 Docker Compose。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/faq.html |
| F-035 | 云托管服务创建完成后，后台会分配给该服务一个公网域名和一个镜像仓库，每个服务一个镜像仓库，互相隔离；镜像仓库支持存储 100 个镜像，存储镜像不产生费用。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/image.html |
| F-036 | 镜像仓库账号默认为「root」不可更改；密码 8-64 个字符，包含大小写英文字母、数字和符号 `~!@#$%^&*_-+=`\|(){}[]:;<>,.?/` 中的任意三种。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/image.html |
| F-037 | WebShell 仅供调试，对容器内容的写操作不能持久，容器会自动恢复到镜像所固化的状态；最小实例为 0 且无流量时 WebShell 入口不可点击。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/webshell.html |
| F-038 | 容器默认时区为 UTC，如需使用上海时间需在 Dockerfile 中启用时区设置命令；使用无 Dockerfile 模式部署暂不支持修改时区。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/faq.html |
| F-039 | 容器系统时间默认为 UTC 协调世界时间，与本地所属时区 CST（上海时间）相差 8 个小时。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/timezone/index.html |
| F-040 | 时区修正需在 Dockerfile 中按基础镜像系统类型选择命令：Alpine 用 `ENV TZ Asia/Shanghai` 加 `apk add tzdata && cp /usr/share/zoneinfo/${TZ} /etc/localtime`，Debian/Ubuntu/CentOS 用 `ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone`。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/timezone/index.html |
| F-041 | 服务监控视图共有 8 个监控指标，版本监控视图共有 10 个监控指标；CPU 用量单位为（核 x 小时），内存用量单位为（GiB x 小时）。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/monitor/index.html |
| F-042 | 每个环境最多可配置 50 条告警策略，每个告警策略中最多可添加 10 个告警条件；统计周期仅支持 5 分钟统计一次，告警频率支持每小时告警一次和每 12 个小时告警一次。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/alarm/index.html |
| F-043 | 资源到期通知在资源到期前 7 天开始推送；账号欠费通知的对象为小程序管理员。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/alarm/index.html |
| F-044 | 微信云托管环境在 30 天内未产生任何请求调用即被冻结（统计时长自 2024 年 4 月 1 日开始），冻结后云服务资源无法使用、线上业务停服；冻结时间超过 180 天系统自动销毁并删除环境，且不支持恢复。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/env/index.html |
| F-045 | 账号欠费时所有环境都将被冻结，欠费超过 7 天所有环境都将被删除且无法恢复；环境删除后环境内所有资源将被释放，不可恢复；有免费额度的环境删除后再次创建的环境不会再有免费额度。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/env/index.html |
| F-046 | 云托管管理员最多支持设置 3 个、环境管理员最多 5 个、开发者最多 30 个；最后一个云托管管理员不支持删除。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/authset/index.html |
| F-047 | 已支持的开发账号类型为微信小程序、微信小游戏、微信公众号、微信小商店、微信开放平台第三方服务商；未认证的公众号不支持开通微信云托管。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/account/index.html |
| F-048 | 每个微信生态账号一对一绑定一个腾讯云账号，不支持多个账号绑定同一个腾讯云账号；更换绑定的腾讯云账号必须销毁当前所有环境且无法恢复。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/account/index.html |
| F-049 | 资源复用当前仅支持小程序、小游戏、公众号、小商店的账号间复用，不支持第三方平台、开放平台 WEB 网站等其他账号类型；被复用方不需要开通微信云托管。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/reuse/index.html |
| F-050 | 私有网络设置按服务进行设置，需将服务设置到腾讯云资源所在的 VPC，子网可以不同，同一 VPC 内子网间默认是互通的；访问腾讯云资源时使用资源在 VPC 内的内网 IP。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/practice/redis.html |
| F-051 | 购买腾讯云 Redis 服务必须选择「上海」地域，因为微信云托管服务目前部署在「上海」地域，VPC 私有网络设置暂不支持跨地域。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/practice/redis.html |
| F-052 | 资源互联只支持授权 1 个 VPC，资源互联带宽峰值最大为 5 Gbps；云托管资源地域暂只支持上海，暂不支持跨地域资源互联。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/env/envsetting.html |

## 三、发布单、灰度与回滚

| F 编号 | 事实陈述 | 来源 URL |
|---|---|---|
| F-053 | 部署发布采用发布单形式，流程包含新建版本、测试、灰度上线 3 个子流程。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/online.html |
| F-054 | 首次发布选择代码的方式有绑定 Github 仓库、绑定 Gitlab 仓库、绑定 Gitee 仓库、手动上传代码包、拉取镜像 5 种。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/online.html |
| F-055 | 手动上传代码包支持代码文件夹、代码 zip 压缩包两种方式，大小不能超过 2 MiB。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/online.html |
| F-056 | 测试方式有 OpenID 白名单和 URL 参数两种；选择 URL 参数测试方式时至少配置 1 个 key 和 value 条件，value 支持 Glob 表达式。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/online.html |
| F-057 | 灰度上线时按 10% 粒度加减流量比例，只支持最多 2 个版本有流量，支持将灰度流量比例回调。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/online.html |
| F-058 | 流量路由规则为用户首次进入时按照流量比例随机进入某一个有流量的版本，非首次进入时该用户将一直进入到首次进入的版本中。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/online.html |
| F-059 | 进入灰度上线步骤后测试阶段的测试配置失效且不可再回到上一步骤；一旦更新测试配置，当前流程不可返回上一步再重新选择版本。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/online.html |
| F-060 | 版本分线上、线下两种状态；线下版本会无视配置信息，在下线半小时内缩容到 0，并一直保持直到再次被推到线上。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/online.html |
| F-061 | 新版本发布成功后旧版本还会缓存 2 分钟时间，这段时间内控制台会看到新旧版本同时都有实例，且部分请求还会走到旧版本。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/online.html |
| F-062 | 回退操作只能向前回退，即高版本回退到低版本，不可反向回退；回退时先把目标版本的实例数保持到版本创建时的最小副本数，再接入现网。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/online.html |
| F-063 | 版本创建时「服务设置 - 基础信息」里的规格、副本数、扩缩容条件、环境变量信息会锁定在版本中，不可以再次更改；除线上版本不可删除外，其余版本均可删除。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/online.html |
| F-064 | 流水线目前支持 GitHub、GitLab、码云 Gitee 三种代码源；端口目前仅支持配置一个端口；推送触发只能全量发布现网；业务自己搭建的私人仓库因涉及需要填写账密暂不支持。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/pipeline.html |
| F-065 | 实例副本数最小值设为 0 时，服务在 30min 内无流量后台会将实例副本数缩容为 0；服务部署发布时都会先产生 1 个容器实例，部署成功后等待半小时再缩容至 0。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/pipeline.html |
| F-066 | 版本切换空窗期流量切换出现空白一般持续 1 分钟自动恢复，推荐灰度发布做法为先 50%，然后隔 3-5 分钟结束灰度。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/faq.html |
| F-067 | 服务间以内网域名方式内网调用，每个服务开启内网访问后分配一个内网域名，开启内网方式时将自动触发一次部署发布；服务间内网调用的端口为服务部署发布时填写的端口，其他端口不可使用。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/internal.html |
| F-068 | CLI 部署命令为 `wxcloud run:deploy [OPTIONS] [PATH]`，支持 `--releaseType=FULL\|GRAY`、`--containerPort`、`--dockerfile`、`--targetDir`、`--libraryImage`、`--envParams`、`--override`、`--noConfirm`、`--detach` 等参数，发布版本后直接 100% 接入现网。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/cli/index.html |
| F-069 | CLI 通过 `npm install -g @wxcloud/cli` 安装，登录命令为 `wxcloud login`，参数为 `-a, --appId=appId` 和 `-k, --privateKey=privateKey`；CLI 密钥需在「微信云托管控制台-设置-CLI 密钥」生成，生成时需要账号管理员扫码。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/cli/index.html |

## 四、调用链路与身份透传

| F 编号 | 事实陈述 | 来源 URL |
|---|---|---|
| F-070 | 云托管服务调用分为「微信体系内调用」和「公网调用」两种形态；目前仅支持 HTTP 协议，不支持 tcp/udp/mqtt 等其他协议。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/index.html |
| F-071 | `callContainer` 方法仅限被该微信云托管环境授权的小程序/公众号使用，仅凭环境 id 和服务名无法调用对应服务。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/index.html |
| F-072 | 需在「小程序管理后台」-「设置」-「功能设置」-「基础库最低版本设置」中把值设定为 2.23.0 及以上，否则无法正常使用 `callContainer` 方法。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/index.html |
| F-073 | 小程序调用示例为 `wx.cloud.callContainer({ config: { env: '填入云环境ID' }, path: '/xxx', method: 'POST', header: { 'X-WX-SERVICE': 'xxx' } })`，`X-WX-SERVICE` 填服务名称。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/mini.html |
| F-074 | 使用前需在小程序 app.js 中执行 `wx.cloud.init()`，全局执行一次即可；init 过程是异步的，需要等待 init 完成才可以发起调用。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/mini.html |
| F-075 | `callContainer` 请求参数中 `config.env`、`path`、`header` 必填；header 中不能设置 Referer，content-type 默认为 application/json；timeout 单位毫秒，最大值不能超过 15 秒，否则无效。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/mini.html |
| F-076 | `method` 合法值为 OPTIONS、GET、HEAD、POST、PUT、DELETE、TRACE、CONNECT；`dataType` 合法值为 json（默认）与 other；`responseType` 合法值为 text（默认）与 arraybuffer。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/mini.html |
| F-077 | 容器内收到的请求 header 包含 `X-WX-OPENID`、`X-WX-APPID`、`X-WX-UNIONID`、`X-WX-FROM-OPENID`、`X-WX-FROM-APPID`、`X-WX-FROM-UNIONID`、`X-WX-ENV`、`X-WX-SOURCE`、`X-Original-Forwarded-For`。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/weixin/index.html |
| F-078 | header 大小写不敏感，部分框架会将原始 header 转为小写、无划线驼峰或下划线形式，业务开发前需先打印测试 header 信息；判断调用来源是否为微信生态端可判断 `X-WX-SOURCE` 头部是否存在。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/weixin/index.html |
| F-079 | 小程序发起 callContainer 调用时，服务请求 header 中会自动带有 openid、unionid、IP 地址、可信来源等用户信息，无需再通过 `wx.login` 登录置换。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/mini.html |
| F-080 | 公众号处于未登录模式时，`callContainer` 方法中不包含微信用户信息。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/index.html |
| F-081 | 小程序中使用 web-view 时，web-view 部分只能走公网调用，不支持 call container 内网调用。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/index.html |
| F-082 | 公网调用不包含任何微信用户信息，开发者需要自己搭建用户登录鉴权等用户体系；不支持通过公网 IP 访问服务。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/index.html |
| F-083 | 公众号 H5 登录鉴权流程目前只有已微信认证的服务号可完成；需引入 `jweixin-1.6.0.js`、`cloud.js`（1.3.0）、`mplogin.min.js`（1.3.1）三个 JS 文件。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/h5.html |
| F-084 | `mplogin` 的 `scope` 必填，取值 `snsapi_userinfo`、`snsapi_base`；`region` 可选 `ap-guangzhou`、`ap-beijing`，不填默认为 `ap-shanghai`；`traceUser` 默认 true，非上海地域请设置成 false。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/h5.html |
| F-085 | `mplogin` 返回 `ret` 取值为 -1 参数错误、0 成功、1 当前页面或 redirect 页面非 https 协议、2 系统判定有风险阻止登录、3 未引入微信 WEBSDK 或环境未授权此账号。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/h5.html |
| F-086 | 跨端方案提供 `@wxcloud/cloud-sdk`，安装命令 `npm install @wxcloud/cloud-sdk --save`；downloadFile、uploadFile 暂不支持适配；公众号登录相关的 API 在微信客户端之外调用无法正常完成相应逻辑。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/crossplaform.html |
| F-087 | 若业务不需要用户身份信息，可在 header 中添加 `X-WX-EXCLUDE-CREDENTIALS: unionid, cloudbase-access-token, openid`；附带信息会占用大概 10ms-50ms 时间。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/practice/call.html |
| F-088 | 通用限制为请求大小限制 100KiB（文本 100KiB，二进制 20MiB），返回包大小限制 1000KiB；排查指引错误码 -606001 表示请求包大小超过 100KB，-606002 表示响应包大小超过 1MB。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/index.html |
| F-089 | 容器内环境变量包括 `CBR_ENV_ID`（当前环境 ID）、`MYSQL_USERNAME`、`MYSQL_PASSWORD`、`MYSQL_ADDRESS`（后三者仅在模板部署自动开通数据库时产生）。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/weixin/index.html |
| F-090 | 一套代码对应多个环境时，项目内部可通过环境变量 `CBR_ENV_ID` 感知当前项目在哪个环境运行，并维护 env 到配置的映射表。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/practice/mult.html |
| F-091 | 开发/测试环境建议绑定代码仓库的 dev 或 test 分支并可开启推送触发，预发/生产环境绑定 master/main 分支且一般不建议开启推送触发，建议采用手动触发流水线 + 灰度发布。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/practice/mult.html |
| F-092 | 资源复用场景下需构造 `new wx.cloud.Cloud({ resourceAppid: 'WXAAA', resourceEnv: 'prod_001' })` 并 `await c1.init()`，`resourceAppid` 填环境所属的账号 appid。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/call/mini.html |
| F-093 | 其他平台小程序（支付宝/快手/字节）后端和网站一同被视为「其他客户端」，只可通过公网链路访问，无法享受微信链路及生态优势。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/quickstart/plan/index.html |
| F-094 | callContainer 的微信链路效果相当于 WAF 和 DDoS 高防叠加，在云托管服务中这些都是标准配置，无需支付任何费用（厂商自述）。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/practice/call.html |

## 五、微信生态集成（开放接口、支付、推送、存储）

| F 编号 | 事实陈述 | 来源 URL |
|---|---|---|
| F-095 | 「开放接口服务」以旁加载形式部署到服务中，中转 api.weixin.qq.com 的请求并自动处理 token 和鉴权问题；请求包体最大限制 32 MiB，请求回包最大限制 32 MiB，云调用最大超时时间为 30s。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/open.html |
| F-096 | 容器内云调用会增加 Header `x-openapi-seqid`，会修改 `x-forwarded-for` 标记请求来源；`connection`、`proxy-connection`、`keep-alive`、`proxy-authenticate`、`proxy-authorization`、`te*`、`trailer`、`transfer-encoding`、`upgrade`、`expect` 不会被传递。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/open.html |
| F-097 | 开放接口服务依赖 shell，镜像内无 sh/bash 时无法正常部署容器（如 scratch 作为基础镜像时）；开放接口服务不允许外网直接访问，请求解析到 169.254.0.x。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/open.html |
| F-098 | 开启「开放接口服务」前已存在的服务版本需要在开启后重新构建版本才会生效；实例扩缩容遵循版本创建时的开关状态。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/open.html |
| F-099 | 资源复用场景下开放接口调用需在地址后加 `from_appid` 参数；不携带该参数时归属为云托管环境所属的「小程序/公众号」。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/open.html |
| F-100 | 旧版云调用中 access_token 推送的时间间隔为 10 分钟，令牌的有效期为 30 分钟，挂载路径为 `/.tencentcloudbase/wx/cloudbase_access_token`；2022 年 7 月后创建的环境均不再支持旧版云调用。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/token.html |
| F-101 | cloudbase_access_token 需要在云托管平台配置接口白名单，access_token 不需要；配置以环境为维度区分，不同环境有不同的 token 和不同的配置。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/token.html |
| F-102 | 云托管封装微信支付后，商户号填入 `sub_mch_id` 字段，小程序/公众号 AppID 填入 `sub_appid` 字段，免填写 `mch_id`、`AppID`、`sign`、`sign_type`，接口入参和返回值都为 JSON 而不是 XML。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/pay.html |
| F-103 | 收到支付结果回调的云托管服务必须返回一个 `{ "errcode": 0 }` 的对象，否则在接下来两天内会持续收到回调，直到返回成功为止。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/pay.html |
| F-104 | 通过开放接口服务调用支付接口使用 `POST http://api.weixin.qq.com/_/pay/接口名称`，统一下单 `/_/pay/unifiedOrder` 与申请退款 `/_/pay/refund` 需要 OpenID，查询订单 `/_/pay/queryorder`、关闭订单 `/_/pay/closeorder`、下载对账单 `/_/pay/downloadbill` 不需要。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/pay.html |
| F-105 | 云托管微信支付只支持小程序使用，关系是「商户号—小程序」；jsapi 和 API 退款权限需要前往微信支付商户平台「我的授权产品」中确认授权。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/pay.html |
| F-106 | 统一下单必填字段为 `sub_mch_id`、`body`（String(128)）、`out_trade_no`（String(32)）、`total_fee`（Int，单位分）、`spbill_create_ip`（String(64)）、`trade_type`（小程序取值 JSAPI）；`prepay_id` 有效期为 2 小时。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/pay/order/unified.html |
| F-107 | 关闭订单时订单生成后不能马上调用关单接口，最短调用时间间隔为 5 分钟。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/pay/order/close.html |
| F-108 | 微信在次日 9 点启动生成前一天的对账单，建议商户 10 点后再获取；对账单接口只能下载三个月以内的账单；对账单中涉及金额的字段单位为「元」。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/pay/order/bill.html |
| F-109 | 申请退款的限制为交易时间超过一年的订单无法提交退款、每个支付订单的部分退款次数不能超过 50 次、请求频率限制 150qps 且错误或无效请求频率限制 6qps、申请退款总金额不能超过订单金额。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/pay/order/refund.html |
| F-110 | 查询退款时一个订单部分退款超过 10 笔后默认返回前 10 笔和 `total_refund_count`，可传 `offset` 继续查询，offset 超过 total_refund_count 时返回报错 PARAM_ERROR。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/pay/order/queryrefund.html |
| F-111 | 分账接口共 8 个：`/_/pay/profitsharingaddreceiver`、`/_/pay/profitsharingremovereceiver`、`/_/pay/profitsharing`、`/_/pay/multiprofitsharing`、`/_/pay/profitsharingfinish`、`/_/pay/profitsharingquery`、`/_/pay/profitsharingreturn`、`/_/pay/profitsharingreturnquery`。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/pay/account/index.html |
| F-112 | 请求单次分账限频为单个服务商 300QPS、单个交易收款商户 30QPS，超限报错 FREQUENCY_LIMITED；`receivers` 不超过 50 个 JSON 对象；同一笔订单最多能发起 20 次多次分账请求。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/pay/account/onesharing.html |
| F-113 | 支付结果回调只有用户支付成功时才会有，未支付或支付失败需使用接口主动查询；容器服务必须返回 `{ errcode, errmsg }` 对象，`errcode` 为 0 表示正常，异常时支付回调会持续重试最多两天。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/pay/callback/index.html |
| F-114 | 微信支付通知重试频率为 15s/15s/30s/3m/10m/20m/30m/30m/30m/60m/3h/3h/3h/6h/6h，总计 24h4m；同样的通知可能多次发送，商户系统必须能正确处理重复通知；`sign_type` 目前支持 HMAC-SHA256 和 MD5，默认为 MD5。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/pay/callback/index.html |
| F-115 | 消息推送在「微信云托管控制台-设置-全局设置-消息推送」中配置，需填写环境 ID、服务名称、path，只需配置 1 个服务即可接收所有类型消息。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/push.html |
| F-116 | 配置消息推送时微信后台会发起检测请求，请求体 action 为 `CheckContainerPath`，开发者回复 success 或回复空即可完成测试；路径返回的 Status 需要为 200，否则路径配置检查失败。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/weixin/push.html |
| F-117 | 公众号 H5 场景的云托管不支持未登录模式操作对象存储；公众号 H5 被动回复只支持公众号，小程序需要使用主动回复接口 `http://api.weixin.qq.com/cgi-bin/message/custom/send`，并需将 `/cgi-bin/message/custom/send` 加入配置白名单。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/storage/h5/upload.html |
| F-118 | 对象存储 API 操作共 4 个接口：上传文件、下载文件、删除文件、获取临时链接地址；`cloudID` 由 `cloud://`、微信云托管环境 ID、存储桶 ID、文件路径 四部分构成。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/storage/index.html |
| F-119 | 对象存储本身没有文件夹和目录的概念，控制台展示的文件夹是以 `/` 结尾的空对象；COS API 仅支持删除单个文件，删除整个目录需先用 GET Bucket (List Objects) 获取指定前缀下的所有文件，再使用 DELETE Object 逐个删除。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/storage/index.html |
| F-120 | 微信小程序端对象存储需基础库版本 2.13.2 及以上；上传至同一路径是覆盖写，路径格式为根路径直接填文件名、文件夹例子 `test/文件名`，不要 `/` 开头。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/storage/miniapp/upload.html |
| F-121 | 获取临时链接 `wx.cloud.getTempFileURL({ fileList: [{ fileID, maxAge }] })` 一次最多取 50 个；公有读的文件获取的链接不会过期，私有文件获取的链接默认 24 小时有效期（`maxAge` 默认 86400，单位秒）。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/storage/miniapp/gettempurl.html |
| F-122 | 服务端对象存储接口为 `getUploadTcbFileLink`（`POST https://api.weixin.qq.com/tcb/uploadfile`）、`getDownloadTcbFileLink`（`POST https://api.weixin.qq.com/tcb/batchdownloadfile`）、`deleteTcbCloudFile`（`POST https://api.weixin.qq.com/tcb/batchdeletefile`）；三者均应在服务器端调用、不可在前端直接调用、均不支持云调用，所属权限集 id 为 49。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/storage/service/delete.html |
| F-123 | COS-SDK 使用三步：使用开放接口服务获取临时密钥 `http://api.weixin.qq.com/_/cos/getauth`、用临时密钥初始化 COS-SDK、用 COS-SDK 做增删改查操作；访问存储桶需指定 Bucket 与 Region（默认 `ap-shanghai`）。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/storage/service/cos-sdk.html |
| F-124 | 服务端上传文件需增加文件元数据：通过 `POST http://api.weixin.qq.com/_/cos/metaid/encode` 获取 `x_cos_meta_field_strs`，上传时在 Headers 中增加 `x-cos-meta-fileid`；文件无元数据时小程序端无法访问。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/storage/service/cos-sdk.html |
| F-125 | 微信云托管对象存储底层 COS 存储桶默认私有读写且没有暴露控制台界面，控制台文件路径以 `tcb.qcloud.la` 结尾。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/storage/service/cos-sdk.html |
| F-126 | WebSocket 服务目前只支持 wss 方式连接；云托管底层会有健康检查尝试连接，正常 WebSocket 连接请求带 `Connection: Upgrade`、`Upgrade: websocket` 两个 header，可据此过滤。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/websocket/index.html |
| F-127 | 小程序 WebSocket 需基础库版本最低 2.21.1；H5 WebSocket 需要 WEB-SDK 版本最低 3.4.0；在 iOS 高性能+ 模式下 connectContainer 暂时无法携带微信身份，服务端读取不到 `x-wx-openid`。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/development/websocket/miniprogram.html |

## 六、计费与成本核算

| F 编号 | 事实陈述 | 来源 URL |
|---|---|---|
| F-128 | 微信云托管以环境为维度，只提供「按量计费」计费方式，按量计费方式下还可通过购买资源包进一步降低成本。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/index.html |
| F-129 | 同一个账号下所有微信云托管环境共享账户余额、独立计费；资源包以环境为维度，一个资源包只能给一个环境使用，不可给多个环境使用。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/index.html |
| F-130 | 低消说明为在按量计费环境内，如果当日有资源使用且产生的计费金额不足 0.01 元，将补齐按照 0.01 元收取。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/index.html |
| F-131 | 云环境均为按量付费模式，系统每日进行资源消耗和结算，并在次日（特殊情况下可能延迟几天，但不会超过当月最后一天）进行扣费。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-132 | 首个环境赠送一定免费额度，该免费额度有效期为 3 个月；免费额度使用 80% 时会推送消息通知；免费体验仅限首个环境，额外多建的环境会立刻计费。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-133 | 刊例价为容器 CPU 使用量 0.055 元/（核 *小时），免费额度 720（核 *小时）；容器内存使用量 0.032 元/（GB *小时），免费额度 1440（GB *小时）。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-134 | 刊例价为容器构建时长 0.05 元/分钟，免费额度 600 分钟；容器公网流量 0.8 元/GB，免费额度 5GB。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-135 | 刊例价为 MySQL 数据库算力 0.342 元/（个 *小时），免费额度 720（个 *小时）；MySQL 数据库存储 0.00485 元/（GB *小时），免费额度 720（GB *小时）。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-136 | 刊例价为对象存储容量 0.0043 元/（GB *天），免费额度 5GB；下载操作次数 0.01 元/万次，免费额度 6000 万次；上传操作次数 0.01 元/万次，免费额度 3000 万次；CDN 回源流量 0.15 元/GB，免费额度 3GB；CDN 流量 0.18 元/GB，免费额度 3GB。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-137 | 刊例价为静态资源存储容量 0.0043 元/（GB*天），免费额度为「无」；静态资源存储流量 0.21 元/GB，免费额度为「无」。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-138 | CPU（核×小时）与内存（GiB×小时）的产生用量条件均为「环境中任意服务下任意版本，实例数量不为 0」；1（核×小时）= 60（核×分钟）= 3600（核×秒）。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-139 | 流量（GB）的产生用量条件为「环境中任意服务通过公网域名访问，或任意服务访问过公网」；只通过 callcontainer 访问服务不产生用量。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-140 | 构建（分钟）的产生用量条件为「发布服务时采用了『本地代码/代码库拉取』方式」；使用「镜像拉取」方式无构建用量。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-141 | MySQL 数据库算力的产生用量条件为「对数据库进行了任意读写/运算操作，或通过任意管理界面登录访问过数据库」；1 CCU 等价于 1 核 2GB 的数据库的计算能力。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-142 | MySQL 数据库存储（GB *小时）在「开通了 MySQL 未注销」时持续产生用量；无论是否存有业务数据，数据库系统表都至少消耗 28M 存储空间。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-143 | 对象存储下载操作次数与上传操作次数无论请求成功或失败均计算次数，不足一万次按一万次计算；对象存储默认开启了 CDN 加速，只要调用即会产生 CDN 流量。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-144 | 增值服务（出口固定 IP）以包年包月付费模式计费、先付后用、每个环境独立计费，价格为 49 元/（月*环境）；不可用作域名备案；到期未续费该固定 IP 将被回收不可用。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/price.html |
| F-145 | 按量计费结算时的抵扣顺序为「先抵扣免费资源，再进行资源包的用量抵扣，抵扣完成后再计算按量计费费用」；当有多个资源包时可叠加使用，一个资源包中某个指标用量耗尽后其他指标仍可继续抵扣。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/package.html |
| F-146 | 资源包均为一次性购买，不可续费，可反复购买；为环境级别购买，不支持转移到其他环境；到期后不可再用于抵扣按量计费的用量。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/package.html |
| F-147 | 服务资源包内容为容器（服务）CPU 使用量 360（核 *小时）、内存使用量 720（GB *小时）、构建时长 60 分钟、公网流量 10GB，有效时长 3 个月，原价 53.84 元，售价 36 元。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/env/envsetting.html |
| F-148 | 实例消耗的资源量为规格乘以运行时间（精确到秒）：0.25 核 0.5GB 实例运行 4 小时消耗 CPU 1（核*小时）、内存 2（GB *小时）；1 核 2GB 实例运行 1 小时与两个 0.5 核 1GB 实例运行 1 小时消耗的资源量完全相同。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/faq.html |
| F-149 | 每个版本的实例数上限为 50 个，超过上限不会再继续扩容。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/faq.html |
| F-150 | 开启数据库的自动暂停后，连续 10 分钟内没有任何读写和运算操作数据库即进入暂停状态；暂停状态不会产生数据库算力资源用量，但还会有数据库存储用量。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/faq.html |
| F-151 | 服务下版本的实例最小副本数为 0 且当前服务连续半小时没有任何访问时会触发缩容到 0，不产生任何容器相关用量和费用；只创建服务没有创建版本不会产生费用。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/faq.html |
| F-152 | 开通数据库之后就会创建出 3 个系统数据库用于创建系统表，预计占用数据库 28M 内存，每天都会产生微量的数据库存储费用；如无需使用数据库请及时销毁。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/faq.html |
| F-153 | 欠费 12 小时内正常使用且继续扣费；欠费大于 12 小时小于 7 天所有环境停服，数据库存储、对象存储容量、静态资源存储容量继续扣费，数据保留；欠费大于 7 天资源销毁无法找回，账号下所有环境被删除。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/overdue.html |
| F-154 | 计费示例——工具类小程序每日 8:00～24:00 维持 1 个 0.25 核 0.5GB 实例，每月 CPU 120（核*小时）、内存 240（GB *小时），每月费用总计 14.28 元。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/example.html |
| F-155 | 计费示例——活动类小程序每月费用总计 28.3545 元；社区论坛类小程序每日费用总计 4.7264 元、每月费用总计 141.792 元。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/example.html |
| F-156 | 计费示例中的费用预估均基于刊例价，不考虑折扣、特惠活动、资源包、优惠券等，文档称可理解为理论上的最高价。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/Billing/example.html |

## 七、安全边界与攻击面

| F 编号 | 事实陈述 | 来源 URL |
|---|---|---|
| F-157 | 必须禁止服务公网访问，才可获得 DDoS 防护能力；使用公网访问方式遭到攻击或损失不在微信云托管责任范围之内。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/intro.html |
| F-158 | 微信云托管对公网域名不具备安全防护能力（包括默认公网域名和自定义域名），默认公网域名仅支持接口测试使用。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/debug/know.html |
| F-159 | 应对 DDoS/刷单/爬虫的安全配置需同时满足三条：在小程序或公众号 H5 中采用 callcontainer 方式调用后端接口、在「服务设置」中关闭「公网访问」开关、在小程序后台「基础库最低版本设置」中设定为 2.23.0 及以上；文档写明这三条缺一不可。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/noun/ddos.html |
| F-160 | 微信云托管费用当前为按天结算，遭受攻击导致用量异常要到第二天早晨结算时才会产生高额费用并可能触发欠费通知，文档称后续将优化为按小时结算。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/noun/ddos.html |
| F-161 | 刷单和爬虫难以通过系统监控指标发现，云托管从平台层面也无法确认用户是否遭遇恶意刷单或爬虫；使用 callcontainer 方式时只有真实的微信小程序/公众号用户才能发起请求。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/noun/ddos.html |
| F-162 | 公网访问减小损失的告警配置建议为在「告警设置」中选择指标「调用次数」+「平均实例个数」，参考服务正常运行时的值扩大 2～5 倍设置告警，并在腾讯云侧设置余额告警能力。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/noun/ddos.html |
| F-163 | 微信云托管暂不支持的场景包括：仅支持 HTTP 协议通过域名调用服务、不支持 tcp/udp/mqtt 等协议、不支持通过公网 IP 访问服务、不支持部署 Docker Compose、不支持接入 WAF、不支持一个服务开启多个监听端口、不支持用来部署数据库/Redis 等有状态服务。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/basic/scene.html |
| F-164 | 微信云托管服务是计算型的，扩缩过程中数据无法持久化保存；微信云托管服务挂载硬盘目前还不支持，多实例共享暂时只能使用数据库、存储等媒介沟通；Redis 暂未支持，可以在腾讯云或其他云厂商购买。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/change/check.html |
| F-165 | 微信云托管一开始有内网域名，但因安全性方面有隐患已主动下掉，后续会通过服务升级方式回归该功能；在此期间同一环境下服务间访问可通过容器 IP 或版本虚拟 IP 实现。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/deploy/innet.html |
| F-166 | 版本虚拟 IP 通过「所有服务容器中环境变量」注入，形如 `SERVER_001_SERVICE_HOST`、`SERVER_001_SERVICE_PORT`、`SERVER_001_PORT_80_TCP_PROTO`；该 IP 映射同一个版本下的所有容器实例，多个会轮询。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/deploy/innet.html |
| F-167 | 服务间访问使用容器 IP 不可靠：容器存活时 IP 不变，但自动弹性扩缩容或版本更替会导致容器被回收，无法在其他服务中写固定 IP 地址。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/deploy/innet.html |
| F-168 | 不开启公网访问时服务只能被同一环境下的其他服务调用，或同一 VPC 网络（内网互联）下的其他资源调用，公网其他资源将无法访问；该限制只针对外向内访问，不限制服务内向外发送网络请求。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/guide/service/index.html |
| F-169 | 在微信云托管上使用第三方代码包时，平台不对第三方代码包承担任何责任，使用者需自行承担风险并确保符合适用法律法规和相关许可协议规定。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/info/tsdk.html |

## 八、迁移路径与常见陷阱

| F 编号 | 事实陈述 | 来源 URL |
|---|---|---|
| F-170 | 云函数迁移到云托管后 wx-server-sdk 基本失效；云函数通过 `cloud.getWXContext()` 获取 openid 等信息，在云托管中直接从请求的 req.headers 中读取；wx.cloud.CloudID 在云托管中不做自动解析，需自行通过 API 完成信息置换。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/change/cloudbase.html |
| F-171 | 云开发的云数据库属于 mongo 协议的 flexdb 数据库，云托管没有与其对应的数据库类型；解决方向为保留云开发数据库形态并使用 cloudbase-node-sdk 操作、迁移到云托管 mysql 数据库、或在腾讯云购买 mongo 数据库。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/change/cloudbase.html |
| F-172 | 「CMS 管理系统」是云开发环境定制的项目，完全迁移难度巨大，文档建议放弃迁移，改用其他数据库基础在云托管支持范围中的内容管理系统。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/change/cloudbase.html |
| F-173 | 云函数的执行是一次执行对应一次请求，所以在云开发业务中无需考虑数据库连接数问题，放在云托管中就需要考虑这一点。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/change/cloudbase.html |
| F-174 | Django migration 同步分两步：`python manage.py makemigrations` 生成 migrations 文件对比新旧 Model 找出差异，`python manage.py migrate` 根据 migrations 执行 SQL 并依据 django_migrations 表只执行没有执行过的步骤。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/noun/migration.html |
| F-175 | 在 Dockerfile 的 RUN 命令中执行 migration 时，构建环境不在数据库 VPC 内网中，只能使用外网地址；文档不建议这种用法，migration 操作非常多时会增加构建耗时。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/noun/migration.html |
| F-176 | 在 Dockerfile 的 CMD 或 ENTRYPOINT 中集成 migration 时，多个实例同时创建出来需要注意竞争处理；通过任意服务的实例 webshell 进入执行 migration 时，webshell 进入的实例都处于同一数据库 VPC 内网环境。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/noun/migration.html |
| F-177 | 异步任务场景下最小实例为 0 时触发一个时长 2 小时的异步任务，若期间没有任何访问请求，半小时就直接缩容到 0，需保证实例不会回收、在半小时内触发更新的实例直到异步任务执行完毕。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/noun/async.html |
| F-178 | 真实异步任务例子为每天凌晨开始的数据迁移任务时长约 3 小时，使用云函数定时触发器在凌晨前先把迁移服务拉起来（冷启动 1 分钟），过程中每 15 分钟发起请求防止容器缩容，5 点半结束请求；服务规格需设置内存/CPU 条件大于 95% 以降低突刺导致扩容的概率。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/noun/async.html |
| F-179 | 云托管服务常识中的一条描述为「代码中请不要在请求处理程序范围之外启动后台线程或例程，并确保在传送响应之前完成所有异步操作」；用户无法控制实例服务的重启、新增、销毁，这些权限都由云托管集群自己控制。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/noun/async.html |
| F-180 | 迁移检查清单包含：微信云托管目前不支持同一个服务多个端口，项目若暴露多个端口需拆分成多个子服务；迁移时须确认项目中数据库连接地址是线上可访问的外网地址或内网地址而不是 localhost:3306；项目暴露的端口要和控制台配置的端口保持一致。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/change/check.html |
| F-181 | 微信云托管服务实例暂未支持挂载硬盘，需要在容器化改造时将数据库、存储等迁移到对象存储和云数据库中。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/quickstart/plan/index.html |
| F-182 | 微信云托管的 k8s 底层使用的是 docker，需要在提供的镜像启动时运行一个守护进程（docker daemon），而 podman 不需要，因此 podman 上能运行的程序迁移到云托管可能启动不起来。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/build/template.html |
| F-183 | Docker 构建缓存规则为对 ADD 和 COPY 指令会检查镜像中文件内容并为每个文件计算校验标识，校验标识通常不考虑文件的最后修改时间和最后访问时间；缓存无效后所有后续命令都会重新构建。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/build/speed.html |
| F-184 | 先 COPY ./package*.json 再执行 npm install 最后 COPY . . 的写法，在不变更 package*.json 时打包时间基本都在 1 秒左右。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/build/speed.html |
| F-185 | 微信云托管线上构建的 Docker 镜像源已经是腾讯加速源，所以不需要自己设置 registry-mirrors；Dockerfile 内可自行指定 alpine（mirrors.tencent.com）、NPM（mirrors.tencent.com/npm/）、Python（mirrors.cloud.tencent.com/pypi/simple）加速源。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/build/speed.html |
| F-186 | 构建方案文档收录 6 类模板：Nginx+HTML 分发模板、Nginx+Node 分发模板、PHP 中 SG11 扩展安装模板、jetty 应用模板、Nginx+java-openjdk 分发模板、Nginx+Node 简易 WebSocket。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/scene/build/index.html |
| F-187 | 服务内定时触发的 Dockerfile 改造目标为 3 个：安装 cron（需要触发业务 url 则安装 curl）、创建 crontab 执行命令（task.txt）、将项目启动命令和 cron 启动命令合并成脚本并把容器启动命令改成执行脚本；示例使用 `RUN crontab task.txt` 与 `ENTRYPOINT ["sh", "start.sh"]`。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/practice/trigger.html |
| F-188 | 官方模板仓库位于 https://github.com/WeixinCloud/ 命名空间，包含 springboot、express、django、thinkphp-nginx、thinkphp-apache、laravel、flask、koa、dotnet、golang 等框架与语言模板。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/quickstart/template/official.html |
| F-189 | 手动新建服务并部署时必须在「服务设置」中补全环境变量 `MYSQL_ADDRESS`、`MYSQL_PASSWORD`、`MYSQL_USERNAME`，否则会引发无法连接数据库并导致部署失败；控制台部署模板成功后这三个环境变量会消失，二次部署前需先补全。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/quickstart/template/index.html |
| F-190 | 微信云托管提供「无门槛部署」和「自定义部署」两种快速入门方式；无门槛部署整个步骤会在 3-5 分钟完成。 | https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/quickstart/index.html |

## 九、文档勘误登记（源文档内部口径不一致）

| 勘误号 | 冲突点 | A 侧口径 | B 侧口径 | 采信结论 |
|---|---|---|---|---|
| E-001 | 实例副本数上限 | `basic/noun.html`：最大 5 | `guide/service/pipeline.html` 与 `Billing/faq.html`：最大 50，大于 50 可提工单 | 以 guide + Billing（更具体且被计费文档复述）为准，noun 页为旧值 |
| E-002 | 缩容到 0 的判定时长 | `basic/noun.html` 与 `guide/service/pipeline.html`：30min | `basic/scene.html`：1 小时 | 以 30min 为准（两处文档一致且与计费文档 F-151 一致） |
| E-003 | 版本下线后缩容时长 | `guide/service/online.html` 正文：下线半小时内缩容到 0 | 同页举例：缓存 2 分钟后缩容为 0 | 以「2 分钟缓存期 + 半小时缩容」并列描述，二者分别对应缓存与缩容两个阶段 |
| E-004 | callContainer 超时上限 | `development/call/index.html`：请求最大超时 60 秒 | `development/call/mini.html` 与 `faq.html`：timeout 最大值不能超过 15 秒 | 以 15 秒为准（参数级约束更具体） |
| E-005 | 请求体大小限制 | `development/call/index.html`：100KiB（文本）/ 20MiB（二进制） | `development/call/h5.txt` 与 `faq.html`：100K / 100KB | 以 100KiB 文本 + 20MiB 二进制为准 |
| E-006 | 出口固定 IP 是否提供 | `Billing/price.html`：增值服务 49 元/（月*环境） | `scene/deploy/otherres.html`：目前还未提供付费的固定 IP 服务 | otherres 页自述「只适用于 2022 年 7 月之前创建的环境」，为过时文档；以 price 页为准 |
| E-007 | 服务间内网访问状态 | `scene/deploy/innet.html`：已主动下掉，后续通过服务升级回归 | `scene/change/check.html`：暂时下线，有进展会修改 | 两者一致（状态=下线中），仅措辞不同 |
| E-008 | 部分退款次数上限 | `development/pay/order/refund.html`：不超过 50 次 | `development/pay/order/queryrefund.html`：超过 20 次请使用退款单号查询 | 二者为不同约束（发起上限 50 次 vs 查询接口建议阈值 20 次），非直接冲突，按各自页面表述呈现 |
| E-009 | 资源包场景三剩余量 | `Billing/package.html`：CPU 12 核*小时由 B 抵扣后剩余 702 核*小时 | 同例：720 − 12 = 708 | 源文档算术不一致，正文按源文档原值引用并在正文标注「源文档算术存疑」 |

## 十、统计

- 事实条目总数：**190 条**（F-001 ~ F-190，连续无跳号）
- 覆盖文档域：basic(4) / quickstart(10) / guide(40) / development(51) / Billing(6) / scene(26) / practice(5) / info(2)
- 勘误条目：**9 条**（E-001 ~ E-009）
- 厂商自述标记条目：F-017、F-094（及 basic/intro 中的性能与成本表述，采信为厂商宣称）
