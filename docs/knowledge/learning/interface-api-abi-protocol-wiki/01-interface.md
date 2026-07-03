---
id: "interface-concept"
title: "二、接口（Interface）：语言级行为抽象"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/interface-api-abi-protocol-wiki/01-interface.toml"
source: "spec:create-tech-interface-wiki-tutorial"
category: "learning"
tags: ["interface", "oop", "functional-programming", "polymorphism", "duck-typing"]
date: "2026-07-03"
status: "stable"
author: "SpecWeave"
summary: "接口（Interface）的标准定义、核心特征、多范式应用场景与代码案例"
---

# 接口（Interface）：语言级行为抽象

## 标准定义

### 软件工程通用概念

接口是两个系统、模块或组件之间交互的**边界契约**。它定义了交互的输入输出格式、调用约定和行为约束，但不涉及内部实现细节。接口是系统解耦的核心机制——调用方只需知晓"如何交互"，无需了解"内部如何工作"。

### 面向对象编程（OOP）特定含义

在面向对象编程范式中，Interface 是一种**抽象类型**，它声明了一组方法签名（方法名、参数列表、返回类型），但不提供具体实现。接口定义了"实现者必须做什么"，而将"怎么做"留给具体实现类。

## 核心特征

### 1. 抽象性
接口只声明行为契约（"做什么"），不声明具体实现（"怎么做"）。它隐藏内部细节，仅暴露必要的交互点。

### 2. 规范性
接口明确定义了调用者与实现者双方的权利义务——调用者按照约定方式调用，实现者按照约定提供服务。

### 3. 多态支持
同一接口可以有多个不同实现，运行时根据具体对象类型动态绑定相应方法，实现"一种接口，多种行为"。

### 4. 可实现性
具体类型（类、结构体等）可以实现一个或多个接口。通过实现接口，类型声明自己遵守该接口定义的契约。

### 5. 解耦性
调用方依赖抽象接口而非具体实现类，实现模块间的松耦合。更换实现类时无需修改调用方代码。

### 6. 契约性
实现接口的类型必须严格遵守接口约定（方法签名、行为语义），符合里氏替换原则（LSP）——任何使用接口的地方都可以透明替换为实现类实例。

## 不同编程范式中的应用场景

### OOP 显式接口

主流面向对象语言提供显式的接口机制：

- **Java/C#**：使用 `interface` 关键字，类通过 `implements` 显式实现接口
- **TypeScript**：`interface` 定义类型契约，支持结构化类型
- **Go**：`interface` 隐式实现（鸭子类型），无需显式声明
- **C++**：通过纯虚函数实现抽象类，模拟接口行为

### 函数式编程中的接口

函数式范式中，函数本身就是一等公民，接口体现为类型签名：

- **函数类型签名**：`(a: A, b: B) => C` 本身就是一种接口契约
- **TypeScript 类型别名**：`type Callback = (data: string) => void` 定义回调接口
- **Python Protocol**：PEP 544 引入结构子类型，支持静态鸭子类型
- **Rust Trait**：类似接口但更强大，支持默认实现、泛型约束和标记类型

### 结构化类型 vs 标称类型

| 类型系统 | 代表语言 | 匹配规则 | 特点 |
|---------|---------|---------|------|
| 标称类型（Nominal） | Java、C# | 类型名称显式声明 | 类型安全严格，需显式 `implements` |
| 结构化类型（Structural） | Go、TypeScript、Python | 结构匹配即兼容 | 灵活的鸭子类型，无需显式声明 |

Go 语言的格言很好地诠释了结构化类型："如果它走起来像鸭子，叫起来像鸭子，那它就是鸭子。"

## 代码案例

### 案例 1：支付网关接口（OOP 多态示例）

以下 TypeScript 示例展示如何通过 `PaymentGateway` 接口定义统一契约，实现支付宝和 Stripe 两种支付方式的多态调用：

```typescript
interface PaymentGateway {
  charge(amount: number, currency: string): Promise<PaymentResult>;
  refund(transactionId: string, amount: number): Promise<RefundResult>;
  getStatus(transactionId: string): Promise<TransactionStatus>;
}

interface PaymentResult {
  success: boolean;
  transactionId: string;
  timestamp: Date;
}

interface RefundResult {
  success: boolean;
  refundId: string;
}

type TransactionStatus = "pending" | "completed" | "failed" | "refunded";

class AlipayGateway implements PaymentGateway {
  constructor(private appId: string, private privateKey: string) {}

  async charge(amount: number, currency: string): Promise<PaymentResult> {
    console.log(`[Alipay] 发起支付: ${amount} ${currency}`);
    return {
      success: true,
      transactionId: `ali_${Date.now()}`,
      timestamp: new Date(),
    };
  }

  async refund(transactionId: string, amount: number): Promise<RefundResult> {
    console.log(`[Alipay] 退款: ${transactionId}, 金额: ${amount}`);
    return { success: true, refundId: `ali_refund_${Date.now()}` };
  }

  async getStatus(transactionId: string): Promise<TransactionStatus> {
    return "completed";
  }
}

class StripeGateway implements PaymentGateway {
  constructor(private apiKey: string) {}

  async charge(amount: number, currency: string): Promise<PaymentResult> {
    console.log(`[Stripe] Charging: ${amount} ${currency}`);
    return {
      success: true,
      transactionId: `ch_${Date.now()}`,
      timestamp: new Date(),
    };
  }

  async refund(transactionId: string, amount: number): Promise<RefundResult> {
    console.log(`[Stripe] Refunding: ${transactionId}, amount: ${amount}`);
    return { success: true, refundId: `re_${Date.now()}` };
  }

  async getStatus(transactionId: string): Promise<TransactionStatus> {
    return "completed";
  }
}

class PaymentService {
  constructor(private gateway: PaymentGateway) {}

  async processOrder(amount: number, currency: string): Promise<string> {
    const result = await this.gateway.charge(amount, currency);
    if (!result.success) {
      throw new Error("支付失败");
    }
    return result.transactionId;
  }
}

const alipay = new AlipayGateway("app123", "secret_key");
const stripe = new StripeGateway("sk_test_xxx");

const service1 = new PaymentService(alipay);
const service2 = new PaymentService(stripe);
```

**要点说明**：
- `PaymentService` 依赖抽象接口 `PaymentGateway`，不感知具体支付渠道
- 新增支付方式（如微信支付）只需实现该接口，无需修改 `PaymentService`
- 运行时可动态切换网关实现多态行为

### 案例 2：函数式回调接口（策略模式）

以下示例展示高阶函数如何作为接口契约，实现灵活的策略模式：

```typescript
type FilterStrategy<T> = (item: T) => boolean;
type TransformStrategy<T, U> = (item: T) => U;
type ErrorHandler = (error: Error, context: string) => void;

interface DataProcessor<T, U> {
  filter: FilterStrategy<T>;
  transform: TransformStrategy<T, U>;
  onError: ErrorHandler;
}

function processData<T, U>(data: T[], processor: DataProcessor<T, U>): U[] {
  const results: U[] = [];

  for (const item of data) {
    try {
      if (processor.filter(item)) {
        results.push(processor.transform(item));
      }
    } catch (err) {
      processor.onError(err as Error, String(item));
    }
  }

  return results;
}

const numberProcessor: DataProcessor<number, string> = {
  filter: (n) => n > 0 && n % 2 === 0,
  transform: (n) => `EVEN:${n * 2}`,
  onError: (err, ctx) => console.error(`处理 ${ctx} 出错:`, err.message),
};

const numbers = [1, -2, 4, 3, 6, 8, -1, 10];
const processed = processData(numbers, numberProcessor);
console.log(processed);
```

**要点说明**：
- `FilterStrategy`、`TransformStrategy`、`ErrorHandler` 都是函数类型签名构成的接口
- 相比 OOP 接口，函数式接口更轻量，适用于策略、回调、中间件等场景
- 调用方通过传入不同函数实现即可替换行为，无需创建新类

---

**上一章**：[00 - 概念总览](00-overview.md)  
**下一章**：[02 - API：源码与服务级契约](02-api.md)
