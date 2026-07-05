---
id: "idl-wiki-syntax-types"
title: "二、IDL 类型系统：基本数据类型与注解机制"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/idl-wiki/02-syntax-types.toml"
source: "spec:create-idl-wiki-tutorial"
category: "learning"
tags: ["idl", "syntax", "type-system", "protobuf", "corba-idl", "thrift", "annotations"]
date: "2026-07-04"
status: "stable"
author: "SpecWeave"
summary: "IDL 基本数据类型体系（标量/复合/枚举/容器）与注解注释机制，含 Protobuf/CORBA/Thrift 三语法对照"
---

# 二、IDL 类型系统：基本数据类型与注解机制

IDL 的类型系统是契约定义的基础。本章聚焦"**数据类型**"与"**注解/注释机制**"两大核心主题，以 Protobuf（`.proto`）与 CORBA IDL（`.idl`）为主对照，辅以 Thrift 补充说明，帮助读者建立跨规范的通用类型心智模型。

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

## 2. 注解与注释机制

### 2.1 注释语法

三种规范都支持 `//` 单行注释和 `/* */` 多行注释；Thrift 额外支持 `#` 单行注释。

### 2.2 Protobuf options

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

### 2.3 Thrift 注解

```thrift
struct User {
  1: i32 id (api.label = "required"),
  2: string email (sensitive = "true")
}
```

### 2.4 CORBA pragma

```idl
// 类型库前缀，用于生成 RepositoryId
#pragma prefix "omg.org"
module UserModule {
  interface UserService {
    User getUser(in long id);
  };
};
```

---

**上一章**：[01 - IDL 定义与作用](01-what-is-idl.md)  
**返回目录**：[00 - 概念总览](00-overview.md)  
**下一章**：[03 - IDL 接口声明与方法描述](03-syntax-interface.md)