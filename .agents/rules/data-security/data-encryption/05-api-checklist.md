---
id: "ds-encryption-api-checklist"
title: "第三方API通信加密与实施检查清单"
source: "data-encryption.md#05-api-checklist"
x-toml-ref: "../../../../.meta/toml/.agents/rules/data-security/data-encryption/05-api-checklist.toml"
---
# 第三方API通信加密与实施检查清单

## 第三方API通信加密要求（AI场景专项）

### API密钥传输
- **Header传递**：API密钥必须通过`Authorization`请求头传递，格式为`Authorization: Bearer sk-xxxxxx`或`Authorization: ApiKey <key>`
- **禁止位置**：严禁在URL查询参数、请求体（非加密）、Cookie中传递API密钥（防止被日志、代理、Referer头泄露）
- **密钥轮换**：AI API密钥每90天轮换一次，支持双密钥并行过渡期
- **密钥隔离**：不同环境（开发/测试/生产）使用不同API密钥，生产密钥禁止在测试环境使用

### 请求体加密
- **默认要求**：L4级敏感请求（如包含完整用户PII、核心业务prompt、商业机密）需在TLS基础上增加应用层加密
- **加密方案**：使用API供应商提供的公钥（RSA-4096/SM2）加密随机生成的会话密钥，会话密钥（AES-256-GCM）加密实际请求体
- **格式示例**：
  ```json
  {
    "encrypted_key": "base64(RSA-OAEP-Encrypt(aes_key, vendor_public_key))",
    "iv": "base64(12字节随机IV)",
    "tag": "base64(16字节GCM认证标签)",
    "ciphertext": "base64(AES-256-GCM加密的请求体)",
    "key_fingerprint": "公钥指纹，用于密钥轮换匹配"
  }
  ```

### 响应体验证
- **强制签名验证**：所有包含敏感数据的响应必须携带签名，客户端必须验证签名后才处理响应
- **签名流程**：
  1. 从响应头获取`t=<timestamp>,v1=<signature>`
  2. 验证时间戳在±5分钟窗口内
  3. 拼接`timestamp + "." + response_body`为签名字符串
  4. 使用HMAC-SHA256（或SM3-HMAC）与webhook密钥计算期望签名
  5. 恒定时间比较签名（防止时序攻击），不匹配则拒绝响应
- **防篡改**：签名验证失败必须触发安全告警，记录完整请求响应上下文用于排查

### 流式响应加密
- **SSE/WebSocket加密**：流式输出（Server-Sent Events、WebSocket）必须运行在TLS1.3之上
- **增量签名**：SSE事件可采用增量签名方案，每个事件独立签名，或最终结束事件携带全流签名
- **流式密钥更新**：长连接场景建议每小时协商新的会话密钥，限制单密钥加密数据量
- **断连续传**：断点续传时必须验证已接收数据的完整性签名，防止中间人注入恶意内容

### API供应商加密能力评估清单
接入第三方AI API前，必须对照以下清单评估供应商加密能力：

| 评估项 | 必须满足 | 验证方式 |
|---|---|---|
| 传输加密 | ✅ 强制TLS1.2+，禁用弱版本弱套件 | SSL Labs测试、配置审计 |
| 密钥管理 | ✅ API密钥支持轮换、支持细粒度权限 | 查看控制台、测试轮换流程 |
| 数据留存 | ❓ 明确prompt/response数据留存策略，支持零留存选项 | 合同条款、隐私政策审核 |
| 静态加密 | ✅ 客户数据静态加密（AES-256+，KMS管理密钥） | 安全白皮书、SOC2报告 |
| 签名机制 | ✅ webhook回调支持HMAC-SHA256签名验证 | 文档核查、功能测试 |
| 合规认证 | ✅ 具备SOC2 Type II、ISO27001认证，国内供应商需等保三级 | 证书核查 |
| 国密支持 | 🟡 政务/国企场景需支持SM2/SM3/SM4国密算法 | 技术文档、功能测试 |
| 数据驻留 | 🟡 支持数据境内存储（敏感数据场景） | 合同约定、架构核查 |
| 审计日志 | ✅ 提供API访问审计日志供客户查询 | 控制台/API核查 |
| 漏洞响应 | ✅ 承诺漏洞响应SLA，支持安全问题上报渠道 | SLA文档核查 |

✅=必须满足，❓=需评估确认，🟡=按需满足


## 加密实施检查清单

本清单供developer实现加密功能时自查、reviewer代码审查时使用，所有L3/L4相关项为**强制检查项**，不满足不得合入代码。

| 序号 | 检查项 | 适用级别 | 责任人 | 是否通过 |
|---|---|---|---|---|
| 1 | 所有对外HTTP接口强制HTTPS，无HTTP明文入口 | L1+ | developer/reviewer | ☐ |
| 2 | TLS最低版本为1.2，优先1.3，SSLv3/TLS1.0/TLS1.1已禁用 | L1+ | developer/reviewer | ☐ |
| 3 | 密码套件仅使用批准的安全套件，RC4/3DES/MD5/SHA1已禁用 | L1+ | developer/reviewer | ☐ |
| 4 | L4/L3外部通信使用mTLS双向认证，客户端校验服务器证书链 | L3+ | developer/reviewer | ☐ |
| 5 | 服务器证书有效期不超过1年，存在自动化轮换机制 | L2+ | developer | ☐ |
| 6 | 私钥文件权限为0400，加密存储，未硬编码在代码中 | L2+ | developer/reviewer | ☐ |
| 7 | API密钥仅通过Authorization Header传递，未出现在URL/日志/Cookie中 | L2+ | developer/reviewer | ☐ |
| 8 | 第三方回调/webhook已实现HMAC-SHA256签名验证，使用恒定时间比较 | L3+ | developer/reviewer | ☐ |
| 9 | 接口防重放机制已实现（nonce+timestamp窗口验证） | L3+ | developer | ☐ |
| 10 | 服务器系统盘/数据盘已启用LUKS/BitLocker磁盘加密（AES-256-XTS） | L2+ | 运维 | ☐ |
| 11 | L3及以上数据库已启用透明数据加密（TDE），数据库连接强制SSL | L3+ | DBA/developer | ☐ |
| 12 | 所有数据备份已加密，备份密钥与生产密钥分离存储 | L2+ | DBA/运维 | ☐ |
| 13 | 对象存储启用SSE-KMS加密，存储桶策略拒绝非HTTPS访问 | L2+ | 运维/developer | ☐ |
| 14 | 敏感字段（API密钥、身份证、银行卡、核心PII）已实现字段级加密 | L3+ | developer/reviewer | ☐ |
| 15 | 字段级加密使用AES-256-GCM/SM4-GCM认证加密，未使用ECB模式 | L3+ | developer/reviewer | ☐ |
| 16 | IV/Nonce使用CSPRNG生成，同一密钥下未重复使用IV | L3+ | developer | ☐ |
| 17 | GCM认证标签完整存储，解密时严格验证，失败拒绝处理 | L3+ | developer | ☐ |
| 18 | 密钥未硬编码、未明文配置，通过KMS/环境变量（加密）安全获取 | L2+ | developer/reviewer | ☐ |
| 19 | 密钥使用后内存立即安全清零，密钥内存页锁定防止swap | L3+ | developer | ☐ |
| 20 | 密钥按周期轮换，存在双密钥过渡期，已验证轮换流程 | L3+ | 运维/developer | ☐ |
| 21 | 密钥销毁有完整记录，退役密钥有归档保存用于历史数据解密 | L3+ | 运维 | ☐ |
| 22 | 密钥操作全流程审计日志已开启，日志包含操作人/时间/操作类型 | L3+ | developer/运维 | ☐ |
| 23 | 代码已通过gitleaks/git-secrets扫描，无密钥意外提交风险 | L2+ | developer/CI | ☐ |
| 24 | 国密合规场景已验证SM2/SM3/SM4算法可用性，加密链路符合国密要求 | L3+（合规场景） | developer | ☐ |
| 25 | 加密功能已通过单元测试，覆盖正常加密/解密/篡改验证/边界条件 | L2+ | developer/tester | ☐ |


---

## 相关模式

- [数据分类分级标准](../data-classification.md)
- [数据加密与密钥管理规范](../data-encryption.md)
- [数据安全监控体系](../security-monitoring.md)
- [第三方API供应商安全准入制度](../vendor-admission.md)
- [第三方API供应商持续审计制度](../vendor-audit.md)
- [数据出境安全评估机制](../cross-border-assessment.md)
- [数据安全治理角色职责矩阵](../role-responsibilities.md)

← 上一章: [密钥全生命周期管理](04-key-lifecycle.md) | **[返回索引](../data-encryption.md)**
