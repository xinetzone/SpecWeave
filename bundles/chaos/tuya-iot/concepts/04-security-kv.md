---
type: Concept
title: 安全与 KV 存储
description: TuyaOpen 安全加密体系（SHA/MD5/HMAC/AES/X.509/mbedTLS）与 KV 键值存储（LittleFS/JSON 序列化）
tags: [tuya, tuyaopen, security, crypto, kv, littlefs, mbedtls, sha256, aes]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: tuyaopen-core-source
    resource: "/references/tuyaopen-core-source.md"
    title: TuyaOpen 核心框架源码
  - id: facts-tuyaopen-core
    resource: "/references/facts-tuyaopen-core.md"
    title: TuyaOpen 核心框架事实清单
---

# 安全与 KV 存储

TuyaOpen 在 `src/tal_security/` 提供完整的密码学服务，在 `src/tal_kv/` 提供基于 LittleFS 的键值存储。两者共同构成设备安全数据管理的基础——加密算法保护通信和数据机密性，KV 存储持久化设备凭据、配置和状态。

## 哈希算法（tal_hash）

`tal_hash.h` 提供 SHA-256/SHA-224、MD5、SHA-1 三种哈希算法及其 HMAC 实现。所有算法均提供分步操作 API 和一站式 API，并包含自测函数。

### SHA-256 / SHA-224

SHA-256 输出 32 字节摘要，通过 `is224` 参数可切换为 SHA-224（输出 28 字节）：

```c
#include "tal_hash.h"

/* 分步操作 */
tal_sha256_context_t ctx;
tal_sha256_create_init(&ctx);        /* 或 tal_sha256_starts_ret(&ctx, 0) 表 SHA-256 */
                                     /* is224=1 表示 SHA-224 */
tal_sha256_update_ret(&ctx, data1, len1);
tal_sha256_update_ret(&ctx, data2, len2);
uint8_t digest[32];
tal_sha256_finish_ret(&ctx, digest);
tal_sha256_free(&ctx);

/* 一站式 */
uint8_t digest[32];
tal_sha256_ret(data, len, digest);
```

### MD5

MD5 输出 16 字节，API 模式与 SHA-256 一致：

```c
tal_md5_context_t ctx;
tal_md5_create_init(&ctx);
tal_md5_starts_ret(&ctx);
tal_md5_update_ret(&ctx, data, len);
uint8_t digest[16];
tal_md5_finish_ret(&ctx, digest);
tal_md5_free(&ctx);

/* 一站式 */
tal_md5_ret(data, len, digest);
```

### SHA-1

SHA-1 输出 20 字节：

```c
tal_sha1_ret(data, len, digest);  /* 一站式，输出 20 字节 */
```

### HMAC

HMAC 上下文结构包含底层哈希句柄、64 字节内填充（ipad）和外填充（opad）。支持 HMAC-SHA256 和 HMAC-SHA1：

```c
/* HMAC-SHA256 分步 */
tal_hash_mac_context_t ctx;
tal_sha256_mac_create_init(&ctx, key, keylen);
tal_sha256_mac_starts(&ctx, key, keylen);
tal_sha256_mac_update(&ctx, data, len);
uint8_t mac[32];
tal_sha256_mac_finish(&ctx, mac);

/* 一站式 HMAC-SHA256 */
tal_sha256_mac(key, keylen, data, datalen, mac);

/* 一站式 HMAC-SHA1 */
tal_sha1_mac(key, keylen, data, datalen, mac);  /* 输出 20 字节 */
```

### 自测

所有哈希算法均提供 verbose 自测函数：
- `tal_sha256_self_test(verbose)`
- `tal_md5_self_test(verbose)`
- `tal_sha1_self_test(verbose)`
- `tal_sha256_mac_self_test(verbose)`
- `tal_sha1_mac_self_test(verbose)`

可在启动时调用以验证密码学实现的正确性。

## 对称加密（tal_symmetry）

`tal_symmetry.c` 基于 TKL 层提供 AES 加密解密，支持 ECB、CBC、CTR 三种模式，密钥长度支持 128 位、192 位、256 位。

```c
#include "tal_hash.h"  /* 安全相关头文件通过 tal_security.h 聚合 */

tal_aes_context_t ctx;
tal_aes_create_init(&ctx);
/* 设置密钥和模式后执行加密/解密 */
tal_aes_free(&ctx);
```

AES 上下文创建直接调用 `tkl_aes_create_init()`，由平台硬件加速或软件实现。

## X.509 证书（tal_x509）

`tal_x509.h` 提供 X.509 证书解析功能：

| 函数 | 功能 |
|------|------|
| `tuya_x509_is_ca_pem_format(buf, len)` | 检查缓冲区是否包含 PEM 格式 CA 证书，返回 `BOOL_T` |
| `tuya_x509_pem2der(pem, pemlen, der, derlen)` | PEM 编码证书转换为 DER 格式 |
| `tuya_x509_get_serial(der, derlen, serial, serlen)` | 提取证书序列号（输出缓冲区 32 字节） |
| `tuya_x509_get_fingerprint(der, derlen, type, fp, fplen)` | 计算证书指纹（输出 64 字节，支持 SHA1/SHA256） |
| `tuya_x509_self_test(verbose)` | X.509 模块自测 |

指纹类型枚举 `X509_fingerprint` 支持 SHA1(0) 和 SHA256(1)。这些函数在 TLS 连接证书验证过程中被使用。

## mbedTLS 封装（libtls）

`libtls` 组件基于 mbedTLS 3.1.0 提供更高层的密码学封装：

### 认证加密

`cipher_wrapper.h` 定义了认证加密/解密接口：

```c
typedef struct {
    uint8_t *key;       size_t key_len;
    uint8_t *nonce;     size_t nonce_len;
    uint8_t *ad;        size_t ad_len;     /* 附加认证数据 */
    uint8_t *data;      size_t data_len;
    mbedtls_cipher_type_t cipher_type;
} cipher_params_t;

/* 认证加密：输出密文和 tag */
int mbedtls_cipher_auth_encrypt_wrapper(cipher_params_t *params,
                                        uint8_t *output, size_t *olen,
                                        uint_t *tag, size_t *tag_len);

/* 认证解密：验证 tag 后解密 */
int mbedtls_cipher_auth_decrypt_wrapper(cipher_params_t *params,
                                        uint8_t *output, size_t *olen,
                                        uint_t *tag, size_t tag_len);
```

### 消息摘要与 HMAC

```c
/* 通用消息摘要，通过 mbedtls_md_type_t 指定算法 */
int mbedtls_message_digest(mbedtls_md_type_t md_type,
                           const uint8_t *input, size_t ilen,
                           uint8_t *output);

/* 通用 HMAC */
int mbedtls_message_digest_hmac(mbedtls_md_type_t md_type,
                                const uint8_t *key, size_t keylen,
                                const uint8_t *input, size_t ilen,
                                uint8_t *output);
```

mbedTLS 还为 TLS 连接提供底层支持，移植层在 `port/` 目录下提供线程适配（`threading_alt.h`）和 TLS 配置（`tuya_tls_config.h`）。

## KV 存储（tal_kv）

KV 存储模块基于 LittleFS 实现，提供类型安全的键值持久化。KV 数据在 Flash 上以 JSON 格式序列化，支持 8 种数据类型。

### 数据类型

`kv_tp_t`（uint8_t）支持的类型及序列化开销：

| 类型 | 值 | 序列化格式 | 开销 |
|------|-----|-----------|------|
| CHAR | 0 | JSON 数字 | - |
| BYTE | 1 | JSON 数字 | - |
| SHORT | 2 | JSON 数字 | - |
| USHORT | 3 | JSON 数字 | - |
| INT | 4 | JSON 数字 | 11+6 字节 |
| BOOL | 5 | JSON true/false | 6+6 字节 |
| STRING | 6 | JSON 字符串 | len+6 字节 |
| RAW | 7 | Base64 编码 | 约 33% 膨胀 |

### 核心 API

```c
#include "tal_kv.h"

/* 初始化（返回 0 成功，负值失败） */
int tal_kv_init(void);

/* 设置键值 */
int tal_kv_set(const char *key, const uint8_t *value, size_t length);

/* 获取键值（value 内部分配，需 tal_kv_free 释放） */
int tal_kv_get(const char *key, uint8_t **value, size_t *length);

/* 释放 tal_kv_get 返回的内存 */
int tal_kv_free(uint8_t *value);

/* 删除键 */
int tal_kv_del(const char *key);
```

### 批量序列化

```c
/* 批量设置多个键值对 */
int tal_kv_serialize_set(kv_db_t *kvs, int count);

/* 批量获取多个键值对，返回找到的条目数 */
int tal_kv_serialize_get(const char **keys, kv_db_t *kvs, int max_count);
```

`kv_db_t` 结构包含键名 `key`、类型 `tp`、值指针 `val` 和长度 `len`。

### KV 加密

KV 密钥长度 `TAL_LV_KEY_LEN` 为 16 字节。配置结构 `tal_kv_cfg_t` 包含 seed 和 key 两个 17 字节字段（含字符串结束符）：

```c
typedef struct {
    char seed[17];
    char key[17];
} tal_kv_cfg_t;
```

这使得 KV 数据可以加密存储在 Flash 上，保护设备凭据（如 UUID/AuthKey）等敏感信息。

### CLI 命令

`tal_kv_cmd()` 提供 CLI 命令入口，可在串口终端中直接操作 KV：

```bash
tuya> kv_dump          /* 转储所有 KV（需 CONFIG_CLI_CMD_KV=y） */
```

### LittleFS 访问

`tal_lfs_get()` 获取底层 LittleFS 文件系统句柄 `lfs_t *`，可直接进行文件系统操作，用于 KV 不适合的大文件存储场景。

### 实现细节

- 静态维护 `lfs_t lfs` 文件系统实例
- 使用 `lfs_flash_addr` 记录 Flash 起始地址
- `lfs_mutex` 保证线程安全
- 块设备读接口 `user_provided_block_device_read()` 内部调用 `tkl_flash_read()`，失败返回 `LFS_ERR_IO`
- 写接口 `user_provided_block_device_prog()` 调用 `tkl_flash_write()`
- JSON 序列化/反序列化通过外部引用的 `kv_serialize()` 和 `kv_deserialize()` 实现
- 移植层在 `port/` 目录下，包含 FlashDB 适配、FAL 配置和 LittleFS 配置

## 设备凭据存储

KV 存储最关键的用途之一是持久化设备连接涂鸦云所需的三个凭据：

| 凭据 | 宏定义 | KV 键名 | 长度 |
|------|--------|---------|------|
| Product ID | `TUYA_PRODUCT_ID` | - | 创建产品时获取 |
| UUID | `TUYA_OPENSDK_UUID` | `UUID_TUYAOPEN` | 约 20 字符 |
| AuthKey | `TUYA_OPENSDK_AUTHKEY` | `AUTHKEY_TUYAOPEN` | 约 32 字符 |

凭据解析优先级（首次成功优先）：
1. KV 存储（通过 CLI `auth <uuid> <authkey>` 命令写入）
2. OTP/模组 Flash（`tuya_iot_license_read()` 从硬件读取）
3. 源代码宏（`tuya_config.h` 中）

AP 配网二维码可选宏 `TUYA_NETCFG_PINCODE`，用于 PBKDF2 派生 TLS-PSK，启用二维码安全配对。

## 安全开发实践

基于上述能力，TuyaOpen 应用应遵循以下安全实践：

1. **敏感信息不硬编码**：UUID/AuthKey 等通过 KV 或 OTP 存储，代码中使用占位符（如 `"your_uuid_here"`）
2. **日志不泄露密钥**：`tal_log_print_escape()` 可安全打印含 `%` 的外部输入；避免在日志中输出完整密钥
3. **通信加密**：使用 libtls/mbedTLS 的 TLS 连接，根据设备能力选择合适的安全等级（0-3）
4. **KV 加密**：配置 tal_kv_cfg_t 的 seed/key 对静态凭据加密
5. **证书验证**：TLS 连接中使用 X.509 证书验证，通过指纹校验防止中间人攻击
6. **代码检查**：使用 code-check 技能检测硬编码凭据，所有 `.c/.h` 文件通过格式检查

## 相关概念

- [TAL 抽象层架构](/concepts/01-tal-architecture.md)
- [系统服务](/concepts/02-system-services.md)
- [网络栈](/concepts/03-network-stack.md)
- [第三方库集成](/concepts/05-third-party-libs.md)
- [IoT 开发完整工作流](/concepts/14-iot-workflow.md)
