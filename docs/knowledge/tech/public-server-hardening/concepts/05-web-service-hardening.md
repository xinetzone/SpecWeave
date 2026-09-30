# 05 Web 服务加固：HTTPS、TLS、安全头与应用层防护

> 本文面向运行 Nginx/Apache 等 Web 服务的公网服务器，覆盖传输加密、TLS 配置、安全响应头、后台与 WAF 防护，以及应用本身的基础安全项。

## 5.1 全站强制 HTTPS

使用 Certbot 签发 Let's Encrypt 免费证书并自动配置续期：

```bash
sudo apt install certbot python3-certbot-nginx   # Apache 用 python3-certbot-apache
sudo certbot --nginx -d example.com -d www.example.com
sudo certbot renew --dry-run                      # 验证自动续期
```

Certbot 会自动添加 HTTP 到 HTTPS 的跳转；手动配置时确保 80 端口返回 301 跳转，且不残留可通过 HTTP 提交数据的入口。

## 5.2 TLS 协议与套件

- 仅保留 TLS 1.2 与 TLS 1.3，禁用 SSLv3、TLS 1.0/1.1 及弱加密套件；
- 推荐使用 Mozilla SSL Configuration Generator 选择 "Intermediate"（中级）级别生成配置，兼顾安全与客户端兼容性；
- Nginx 配置形态示例（以生成器当时输出为准）：

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
```

证书部署后可用 SSL Labs Server Test 或 `ssh`/`tls` 检测工具做外部评级验证。

## 5.3 安全响应头与信息隐藏

在 Nginx 配置中添加：

```nginx
server_tokens off;                               # 不返回 Nginx 版本号
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
# Content-Security-Policy 需按站点实际加载的资源域逐项制定后再开启
```

- `Content-Security-Policy`（CSP）是防注入能力最强的响应头，但配置过严会破坏页面，建议先以 `Content-Security-Policy-Report-Only` 观察报告再转为强制；
- Apache 使用 `ServerTokens Prod`、`ServerSignature Off` 隐藏版本。

## 5.4 管理后台与 WAF

- 管理后台路径增加额外访问控制：HTTP Basic Auth、来源 IP 白名单或 VPN 接入；
- 不使用 `/admin`、`/manager` 等默认后台路径的默认命名，管理账户不使用 admin/root 等默认名称；
- 在 CDN/WAF 层开启常见攻击拦截规则（SQL 注入、跨站脚本、常见扫描器特征）；
- 对后台登录同样部署失败限速（配合 [03 篇 fail2ban](03-ssh-and-brute-force-defense.md) 的 Web 类 jail）。

## 5.5 应用层基础安全项

多数真实入侵发生在应用层，Web 服务加固之外必须检查：

1. 及时升级应用框架、CMS 及其插件/主题，删除未使用的插件与安装目录；
2. 交付后第一时间修改一切默认口令（数据库、后台、面板、缓存服务）；
3. 文件上传校验文件类型与内容，上传目录禁止执行脚本；
4. 应用连接数据库使用最小权限账号，不使用 root/管理员账号；
5. 配置项（API Key、口令）通过环境变量或受限配置文件注入，不写入可公开访问的目录；
6. 错误页面不返回堆栈跟踪、物理路径等内部信息。

## 5.6 验收标准

- 浏览器访问站点显示安全连接标识，HTTP 自动跳转 HTTPS；
- TLS 检测无低版本协议与弱套件告警；
- 响应头包含 5.3 的安全项；
- 管理后台在未授权网络中不可访问；
- 应用与插件版本、默认口令检查有记录。

> 上一篇：[04 补丁管理与源站隐藏](04-patching-and-source-hiding.md) ｜ 下一篇：[06 最小权限与隔离](06-least-privilege-and-isolation.md)
