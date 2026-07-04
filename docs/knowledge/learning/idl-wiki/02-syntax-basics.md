---
id: "idl-wiki-syntax-basics"
title: "二、IDL 基本语法结构：类型、接口与方法的通用范式"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/idl-wiki/02-syntax-basics.toml"
source: "spec:create-idl-wiki-tutorial"
category: "learning"
tags: ["idl", "syntax", "type-system", "protobuf", "corba-idl", "thrift"]
date: "2026-07-04"
status: "stable"
author: "SpecWeave"
summary: "IDL 基本语法结构：基本数据类型、接口声明、方法描述、注解与注释机制（含 Protobuf 与 CORBA IDL 双语法对照）"
---

# 二、IDL 基本语法结构：类型、接口与方法的通用范式

IDL 虽然流派众多，但核心语法元素高度收敛：**数据类型**、**接口声明**、**方法描述**、**注解与注释**。本章以 Protobuf（`.proto`）与 CORBA IDL（`.idl`）为主对照，辅以 Thrift 补充说明，帮助读者建立跨规范的通用心智模型。同一 User 领域将贯穿全文，便于对照。

## 1. 基本数据类型

### 1.1 标量类型

不同 IDL 规范对标量类型的命名存在差异，但覆盖范围基本一致。

| 语义 | Protobuf | CORBA IDL | Thrift |
|---|---|---|---|
| 32 位整数 | `int32` | `long` | `i32` |
| 64 位整数 | `int64` | `long long` | `i64` |
| 单精度浮点 | `float` | `float` | `float` |
| 双精度浮点 | `double` | `double` | `double` |
| 布尔 | `bool` | `boolean` | `bool` |
| 字符串 | `string` | `string` | `string` |
| 字节序列 | `bytes` | `sequence<octet>` | `binary` |

### 1.2 复合类型

- **Protobuf** 使用 `message` 定义复合类型，字段需标号（用于二进制编码与向前兼容）。
- **CORBA IDL** 使用 `struct` 定义复合类型，字段无需标号。
- **Thrift** 使用 `struct` 定义复合类型，字段需标号。

### 1.3 枚举

三者均使用 `enum` 关键字声明枚举，语法接近；Protobuf 要求枚举值首项为 `0`，作为默认值。

### 1.4 容器类型

- **Protobuf**：`repeated` 表示列表；`map<key, value>` 表示映射；无原生 set。
- **CORBA IDL**：`sequence<T>` 表示列表；`sequence<T, N>` 表示有界序列；映射需借助自定义结构。
- **Thrift**：`list<T>`、`map<K,V>`、`set<T>` 三者齐备。

### 1.5 综合示例：User 类型

以同一 User 领域为例（id / userName / age / email / tags），对照三种语法。

```protobuf
// Protobuf: user.proto
syntax = "proto3";

message User {
  int32 id = 1;
  string user_name = 2;
  int32 age = 3;
  string email = 4;
  repeated string tags = 5;
  map<string, string> attributes = 6;
}

enum UserStatus {
  USER_STATUS_UNKNOWN = 0;
  USER_STATUS_ACTIVE = 1;
  USER_STATUS_INACTIVE = 2;
}
```

```idl
// CORBA IDL: user.idl
enum UserStatus {
  USER_STATUS_UNKNOWN,
  USER_STATUS_ACTIVE,
  USER_STATUS_INACTIVE
};

struct User {
  long id;
  string user_name;
  long age;
  string email;
  sequence<string> tags;
  sequence<octet> avatar_bytes;
};

typedef sequence<User> UserList;
```

```thrift
// Thrift: user.thrift
enum UserStatus {
  USER_STATUS_UNKNOWN = 0,
  USER_STATUS_ACTIVE = 1,
  USER_STATUS_INACTIVE = 2
}

struct User {
  1: i32 id,
  2: string user_name,
  3: i32 age,
  4: string email,
  5: list<string> tags,
  6: map<string, string> attributes
}
```

## 2. 接口声明语法

接口是 IDL 的核心：它声明服务端能提供哪些方法、客户端如何调用。三种规范的接口声明语法各有风格。

### 2.1 三种语法对比

```protobuf
// Protobuf: 强制使用 message 包装请求与响应
service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
}
```

```idl
// CORBA IDL: 直接使用基础类型作为参数
interface UserService {
  User getUser(in long id);
  UserList listUsers();
};
```

```thrift
// Thrift: 用字段编号标记参数
service UserService {
  User getUser(1: i32 id),
  list<User> listUsers()
}
```

### 2.2 关键差异说明

| 维度 | Protobuf | CORBA IDL | Thrift |
|---|---|---|---|
| 参数包装 | 必须用 message 包装 | 直接使用基础类型 | 直接使用类型，字段需编号 |
| 返回值 | 必须返回 message | 直接返回类型 | 直接返回类型 |
| 参数方向 | 仅 in（隐式） | in / out / inout | 仅 in |
| 异常机制 | 状态码或 `google.rpc.Status` | `raises (Exception)` | `throws (1: Exception e)` |

**设计哲学差异**：
- Protobuf 坚持"消息即协议"，所有参数与返回值都是 message，便于版本演进与 schema 校验。
- CORBA IDL 更接近传统编程语言，支持指针式参数方向，适合分布式对象调用。
- Thrift 折中：直接类型参数 + 字段编号，兼顾灵活性与向前兼容。

## 3. 方法描述

### 3.1 参数方向

CORBA IDL 完整支持 `in/out/inout` 三种方向；Protobuf 与 Thrift 仅 in，通过响应 message 回传多值。

```idl
// CORBA IDL: 完整支持 in/out/inout
interface AccountService {
  void transfer(in long from, in long to, in double amount, out string receipt);
  void swap(inout long a, inout long b);
};
```

```protobuf
// Protobuf: 仅 in（通过 message 字段表达），out 信息封装在响应 message
message TransferRequest {
  int32 from = 1;
  int32 to = 2;
  double amount = 3;
}
message TransferResponse {
  string receipt = 1;
}
service AccountService {
  rpc Transfer(TransferRequest) returns (TransferResponse);
}
```

### 3.2 异常声明

以"可能抛出 UserNotFound 异常的 getUser 方法"为例，三种规范差异显著：

```protobuf
// Protobuf: 通过 RPC 状态码或 google.rpc.Status 表达
message GetUserRequest {
  int32 id = 1;
}
message GetUserResponse {
  User user = 1;
}
service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  // 异常通过 RPC 状态码传递，业务侧约定 code=5 (NOT_FOUND) 表示 UserNotFound
}
```

```idl
// CORBA IDL: 显式 raises 声明
exception UserNotFound {
  long id;
};
interface UserService {
  User getUser(in long id) raises (UserNotFound);
};
```

```thrift
// Thrift: 显式 throws 声明
exception UserNotFound {
  1: i32 id,
  2: string message
}
service UserService {
  User getUser(1: i32 id) throws (1: UserNotFound e)
}
```

## 4. 注解与注释机制

### 4.1 注释语法

三种规范都支持 `//` 单行注释和 `/* */` 多行注释；Thrift 额外支持 `#` 单行注释。

### 4.2 Protobuf options

```protobuf
// 文件级选项
option java_package = "com.example.user";
option java_multiple_files = true;

message User {
  // 字段级选项：标记废弃
  int32 legacy_id = 1 [deprecated = true];
  string email = 2;
}

// 自定义 option
import "google/protobuf/descriptor.proto";
extend google.protobuf.FieldOptions {
  string sensitive = 50000;
}
message User {
  string email = 1 [(sensitive) = "true"];
}
```

### 4.3 Thrift 注解

```thrift
struct User {
  1: i32 id (api.label = "required"),
  2: string email (sensitive = "true")
}
```

### 4.4 CORBA pragma

```idl
// 类型库前缀，用于生成 RepositoryId
#pragma prefix "omg.org"
module UserModule {
  interface UserService {
    User getUser(in long id);
  };
};
```

## 5. 小结

| 语法元素 | Protobuf | CORBA IDL | Thrift |
|---|---|---|---|
| 复合类型 | `message` | `struct` | `struct` |
| 列表 | `repeated` | `sequence<T>` | `list<T>` |
| 映射 | `map<K,V>` | 自定义结构 | `map<K,V>` |
| 接口 | `service` + `rpc` | `interface` | `service` |
| 参数方向 | 仅 in | in/out/inout | 仅 in |
| 异常 | 状态码 | `raises` | `throws` |
| 注解 | `option` | `#pragma` | `()` 注解 |

掌握上述通用元素后，学习任何具体 IDL 规范只需对照差异表即可上手。下一章将逐一介绍主流 IDL 规范（Protobuf / CORBA IDL / Thrift / FlatBuffers / Cap'n Proto / COM IDL）的完整语法与生态。

---

**上一章**：[01 - IDL 定义与作用](01-what-is-idl.md)  
**下一章**：[03 - 主要 IDL 规范介绍](03-major-idl-specs.md)
