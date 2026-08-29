---
id: "idl-wiki-syntax-interface"
title: "三、IDL 接口声明与方法描述：服务契约的通用范式"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/idl-wiki/03-syntax-interface.toml"
source: "spec:create-idl-wiki-tutorial"
category: "learning"
tags: ["idl", "syntax", "interface", "service", "rpc", "protobuf", "corba-idl", "thrift"]
date: "2026-07-04"
status: "stable"
author: "SpecWeave"
summary: "IDL 接口声明语法与方法描述规范，含参数方向、异常声明、Protobuf/CORBA/Thrift 三语法对照"
---
# 三、IDL 接口声明与方法描述：服务契约的通用范式

接口是 IDL 的核心：它声明服务端能提供哪些方法、客户端如何调用。本章聚焦"**接口声明**"与"**方法描述**"两大主题，对比三种主流规范的语法风格与设计哲学差异。

## 1. 接口声明语法

### 1.1 三种语法对比

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

### 1.2 关键差异说明

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

## 2. 方法描述

### 2.1 参数方向

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

### 2.2 异常声明

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

## 3. 小结

| 语法元素 | Protobuf | CORBA IDL | Thrift |
|---|---|---|---|
| 复合类型 | `message` | `struct` | `struct` |
| 列表 | `repeated` | `sequence<T>` | `list<T>` |
| 映射 | `map<K,V>` | 自定义结构 | `map<K,V>` |
| 接口 | `service` + `rpc` | `interface` | `service` |
| 参数方向 | 仅 in | in/out/inout | 仅 in |
| 异常 | 状态码 | `raises` | `throws` |
| 注解 | `option` | `#pragma` | `()` 注解 |

掌握上述通用元素后，学习任何具体 IDL 规范只需对照差异表即可上手。下一章将逐一介绍主流 IDL 规范的完整语法与生态。

---

**上一章**：[02 - IDL 类型系统](02-syntax-types.md)  
**返回目录**：[00 - 概念总览](00-overview.md)  
**下一章**：[04 - 主要 IDL 规范介绍](04-major-idl-specs.md)