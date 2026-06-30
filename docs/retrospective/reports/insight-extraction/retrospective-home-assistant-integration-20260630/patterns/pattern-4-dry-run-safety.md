+++
id = "pattern-4-dry-run-safety"
name = "dry-run 安全机制"
category = "security"
maturity = "L2"
source = "ha_api.py"
created_at = "2026-06-30"
+++

# dry-run 安全机制

## 核心理念

写操作前先预览，获得用户确认后再执行，防止误操作导致的不可逆后果。

## 问题背景

在执行破坏性操作或安全关键操作时，错误操作可能导致严重后果。例如，设备控制操作可能关闭重要设备，数据删除操作可能导致数据丢失。dry-run 安全机制通过在执行前展示操作内容，让用户确认操作的正确性，从而避免误操作。

## 实现方式

### 1. 添加 dry-run 参数

```python
parser.add_argument("--dry-run", action="store_true", help="试运行不提交")
```

### 2. 在写操作中检查 dry-run

```python
def command_set(api: HomeAssistantAPI, args: argparse.Namespace):
    if args.dry_run:
        print("Dry-run 模式 - 以下是将要发送的请求：")
        print(json.dumps({
            "entity_id": args.entity_id,
            "state": state,
            "attributes": attributes,
        }, indent=2, ensure_ascii=False))
        print("\n实际操作未执行。移除 --dry-run 参数以执行操作。")
        return

    status_code, data = api.set_entity(args.entity_id, state, attributes if attributes else None)
    print_result(status_code, data, args.verbose)
```

### 3. 强制确认流程

对于高危操作，强制用户确认：

```python
if args.dry_run:
    # 展示预览
    print("Dry-run 模式 - 以下是将要发送的请求：")
    # ...
    print("\n实际操作未执行。移除 --dry-run 参数以执行操作。")
    return

# 执行实际操作
```

## 应用场景

- 设备控制操作
- 数据删除操作
- 配置变更操作
- 服务调用操作

## 核心特点

| 特点 | 说明 |
|------|------|
| **预览功能** | 在执行前展示操作内容 |
| **用户确认** | 需要用户明确确认后才执行 |
| **安全保障** | 防止误操作导致的不可逆后果 |
| **灵活控制** | 用户可以选择是否启用 dry-run |

## 安全检查清单

| 检查项 | 说明 |
|--------|------|
| [ ] dry-run 是否已执行 | 写操作应先执行 dry-run |
| [ ] 操作内容是否清晰 | 预览内容应清晰展示操作细节 |
| [ ] 用户确认是否获得 | 获得用户明确确认后才执行 |
| [ ] 操作结果是否验证 | 执行后验证操作结果 |

## 代码示例

```python
# ha_api.py 中的 dry-run 实现

def command_set(api: HomeAssistantAPI, args: argparse.Namespace):
    state = str(args.value).lower()
    attributes = {}

    if args.brightness is not None:
        attributes["brightness"] = args.brightness
    if args.temperature is not None:
        attributes["temperature"] = args.temperature
    if args.humidity is not None:
        attributes["humidity"] = args.humidity

    if args.dry_run:
        print("Dry-run 模式 - 以下是将要发送的请求：")
        print(json.dumps({
            "entity_id": args.entity_id,
            "state": state,
            "attributes": attributes,
        }, indent=2, ensure_ascii=False))
        print("\n实际操作未执行。移除 --dry-run 参数以执行操作。")
        return

    status_code, data = api.set_entity(args.entity_id, state, attributes if attributes else None)
    print_result(status_code, data, args.verbose)

def command_service(api: HomeAssistantAPI, args: argparse.Namespace):
    parts = args.service.split(".")
    if len(parts) != 2:
        print("错误: 服务名格式应为 domain.service (如 light.turn_on)")
        sys.exit(1)

    domain, service = parts
    kwargs = {}

    if args.entity_id:
        kwargs["entity_id"] = args.entity_id
    if args.value is not None:
        kwargs["value"] = args.value

    if args.dry_run:
        print("Dry-run 模式 - 以下是将要发送的请求：")
        print(json.dumps({
            "domain": domain,
            "service": service,
            "data": kwargs,
        }, indent=2, ensure_ascii=False))
        print("\n实际操作未执行。移除 --dry-run 参数以执行操作。")
        return

    status_code, data = api.call_service(domain, service, **kwargs)
    print_result(status_code, data, args.verbose)
```

## 最佳实践

1. **默认启用 dry-run**：对于高危操作，默认启用 dry-run 模式
2. **清晰展示内容**：预览内容应清晰展示操作细节，便于用户确认
3. **提供确认机制**：提供明确的确认方式（如输入 yes/no）
4. **记录操作日志**：记录 dry-run 和实际操作的日志
5. **验证操作结果**：执行后验证操作结果，确保操作成功

## 适用范围

| 场景 | 是否适用 | 原因 |
|------|---------|------|
| 设备控制操作 | ✅ | 错误操作可能导致设备状态异常 |
| 数据删除操作 | ✅ | 错误操作可能导致数据丢失 |
| 配置变更操作 | ✅ | 错误操作可能导致系统配置异常 |
| 查询操作 | ❌ | 查询操作不修改数据，无需 dry-run |