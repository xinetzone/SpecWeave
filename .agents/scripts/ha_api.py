#!/usr/bin/env python3
"""Home Assistant API 自动化脚本。

支持通过 REST API 与 Home Assistant 交互，实现设备控制、状态查询、服务调用等核心功能。

本脚本为可选模块，采用优雅降级机制：
- HA 连接不可用时返回友好提示，不抛出致命错误
- 支持配置化参数（.env 文件或环境变量）
- 所有写操作支持 dry-run 预览
- **零第三方依赖**：仅使用 Python 标准库（urllib.request/json/argparse 等），跨平台即用

使用方法：
    python ha_api.py <command> [options]

命令：
    info        检查 HA 连接状态和版本信息
    list        获取所有实体列表
    get         查询指定实体状态
    set         设置实体状态
    service     调用 HA 服务

示例：
    python ha_api.py info
    python ha_api.py list
    python ha_api.py get light.living_room
    python ha_api.py set light.living_room --value true
    python ha_api.py service light.turn_on --entity-id light.living_room
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


@dataclass
class HAConfig:
    """Home Assistant 配置类。"""

    ha_url: str = ""
    ha_token: str = ""
    timeout: int = 10

    def is_configured(self) -> bool:
        """检查配置是否完整。"""
        return bool(self.ha_url and self.ha_token)


@dataclass
class EntityState:
    """实体状态数据类。"""

    entity_id: str
    state: str
    friendly_name: Optional[str] = None
    entity_category: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> EntityState:
        """从 API 响应创建实体状态。"""
        return cls(
            entity_id=data.get("entity_id", ""),
            state=data.get("state", ""),
            friendly_name=data.get("attributes", {}).get("friendly_name"),
            entity_category=data.get("attributes", {}).get("entity_category"),
            attributes=data.get("attributes", {}),
        )


@dataclass
class HARequest:
    """HA 请求数据类。"""

    method: str
    endpoint: str
    data: Optional[Dict[str, Any]] = None


@dataclass
class HAResponse:
    """HA 响应数据类。"""

    status_code: int
    data: Optional[Dict[str, Any]]
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """检查响应是否成功。"""
        return 200 <= self.status_code < 300

    @property
    def is_network_error(self) -> bool:
        """检查是否为网络错误。"""
        return self.status_code == -1


class HomeAssistantAPI:
    """Home Assistant REST API 客户端（零第三方依赖，仅使用标准库）。"""

    def __init__(self, ha_url: str, ha_token: str, timeout: int = 10):
        self.ha_url = ha_url.rstrip("/")
        self.ha_token = ha_token
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> Tuple[int, Optional[Dict[str, Any]]]:
        """发送 HTTP 请求（使用标准库 urllib.request）。"""
        url = f"{self.ha_url}/api{endpoint}"
        data_bytes = None

        json_data = kwargs.pop("json", None)
        if json_data is not None:
            data_bytes = json.dumps(json_data).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=data_bytes,
            headers=self.headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                status_code = response.getcode()
                response_body = response.read().decode("utf-8")
                try:
                    data = json.loads(response_body) if response_body else None
                except (json.JSONDecodeError, ValueError):
                    data = None
                return status_code, data
        except urllib.error.HTTPError as e:
            try:
                error_body = e.read().decode("utf-8")
                data = json.loads(error_body) if error_body else None
            except (json.JSONDecodeError, ValueError):
                data = {"error": str(e)}
            return e.code, data
        except (urllib.error.URLError, OSError, ValueError) as e:
            return -1, {"error": str(e)}

    def get_info(self) -> Tuple[int, Optional[Dict[str, Any]]]:
        """获取 HA 状态和版本信息。"""
        return self._request("GET", "/")

    def get_entities(self) -> Tuple[int, Optional[Dict[str, Any]]]:
        """获取所有实体列表。"""
        return self._request("GET", "/states")

    def get_entity(self, entity_id: str) -> Tuple[int, Optional[Dict[str, Any]]]:
        """获取指定实体状态。"""
        return self._request("GET", f"/states/{entity_id}")

    def set_entity(self, entity_id: str, state: str, attributes: Optional[Dict[str, Any]] = None) -> Tuple[int, Optional[Dict[str, Any]]]:
        """设置实体状态。"""
        data = {"state": state}
        if attributes:
            data["attributes"] = attributes
        return self._request("POST", f"/states/{entity_id}", json=data)

    def call_service(self, domain: str, service: str, **kwargs) -> Tuple[int, Optional[Dict[str, Any]]]:
        """调用 HA 服务。"""
        return self._request("POST", f"/services/{domain}/{service}", json=kwargs)


def load_config() -> HAConfig:
    """加载配置参数。

    优先级：环境变量 > .env 文件 > 默认值
    """
    config = HAConfig(
        ha_url=os.getenv("HA_URL", ""),
        ha_token=os.getenv("HA_TOKEN", ""),
    )

    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with env_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key == "HA_URL" and not config.ha_url:
                        config.ha_url = value.strip('"').strip("'")
                    elif key == "HA_TOKEN" and not config.ha_token:
                        config.ha_token = value.strip('"').strip("'")

    return config


def print_result(status_code: int, data: Optional[Dict[str, Any]], verbose: bool = False):
    """打印结果。"""
    if status_code == -1:
        print(f"错误: {data.get('error', '未知错误')}")
        sys.exit(1)

    if status_code >= 200 and status_code < 300:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        error_msg = data.get("message", "请求失败") if data else f"HTTP {status_code}"
        print(f"错误 (HTTP {status_code}): {error_msg}")
        sys.exit(1)


def command_info(api: HomeAssistantAPI, args: argparse.Namespace):
    """处理 info 命令。"""
    status_code, data = api.get_info()
    print_result(status_code, data, args.verbose)


def command_list(api: HomeAssistantAPI, args: argparse.Namespace):
    """处理 list 命令。"""
    status_code, data = api.get_entities()
    if status_code == 200 and data:
        entities = [
            EntityState.from_api_response(entity)
            for entity in data
        ]
        output = [
            {
                "entity_id": e.entity_id,
                "state": e.state,
                "friendly_name": e.friendly_name,
                "entity_category": e.entity_category,
            }
            for e in entities
        ]
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print_result(status_code, data, args.verbose)


def command_get(api: HomeAssistantAPI, args: argparse.Namespace):
    """处理 get 命令。"""
    status_code, data = api.get_entity(args.entity_id)
    print_result(status_code, data, args.verbose)


def command_set(api: HomeAssistantAPI, args: argparse.Namespace):
    """处理 set 命令。"""
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
        request = HARequest(
            method="POST",
            endpoint=f"/states/{args.entity_id}",
            data={"state": state, "attributes": attributes} if attributes else {"state": state},
        )
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
    """处理 service 命令。"""
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
    if args.brightness is not None:
        kwargs["brightness"] = args.brightness
    if args.temperature is not None:
        kwargs["temperature"] = args.temperature

    if args.dry_run:
        print("Dry-run 模式 - 以下是将要发送的请求：")
        request = HARequest(
            method="POST",
            endpoint=f"/services/{domain}/{service}",
            data=kwargs,
        )
        print(json.dumps({
            "domain": domain,
            "service": service,
            "data": kwargs,
        }, indent=2, ensure_ascii=False))
        print("\n实际操作未执行。移除 --dry-run 参数以执行操作。")
        return

    status_code, data = api.call_service(domain, service, **kwargs)
    print_result(status_code, data, args.verbose)


def main():
    """主函数。"""
    parser = argparse.ArgumentParser(
        description="Home Assistant API 自动化脚本",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--ha-url", help="Home Assistant URL (覆盖配置)")
    parser.add_argument("--ha-token", help="API Token (覆盖配置)")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    subparsers.add_parser("info", help="检查 HA 连接状态和版本信息")
    subparsers.add_parser("list", help="获取所有实体列表")

    get_parser = subparsers.add_parser("get", help="查询指定实体状态")
    get_parser.add_argument("entity_id", help="实体ID")

    set_parser = subparsers.add_parser("set", help="设置实体状态")
    set_parser.add_argument("entity_id", help="实体ID")
    set_parser.add_argument("--value", "-val", required=True, help="状态值")
    set_parser.add_argument("--brightness", type=int, help="亮度 (0-255)")
    set_parser.add_argument("--temperature", type=float, help="温度")
    set_parser.add_argument("--humidity", type=int, help="湿度")
    set_parser.add_argument("--dry-run", action="store_true", help="试运行不提交")

    service_parser = subparsers.add_parser("service", help="调用 HA 服务")
    service_parser.add_argument("service", help="服务名 (如 light.turn_on)")
    service_parser.add_argument("--entity-id", "-e", help="目标实体ID")
    service_parser.add_argument("--value", "-val", help="参数值")
    service_parser.add_argument("--brightness", type=int, help="亮度 (0-255)")
    service_parser.add_argument("--temperature", type=float, help="温度")
    service_parser.add_argument("--dry-run", action="store_true", help="试运行不提交")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    config = load_config()
    ha_url = args.ha_url or config.ha_url
    ha_token = args.ha_token or config.ha_token

    if not ha_url:
        print("错误: HA_URL 未配置。请设置环境变量或在 .env 文件中配置。")
        print("优雅降级：跳过 HA 操作，核心系统不受影响。")
        sys.exit(0)

    if not ha_token:
        print("错误: HA_TOKEN 未配置。请设置环境变量或在 .env 文件中配置。")
        print("优雅降级：跳过 HA 操作，核心系统不受影响。")
        sys.exit(0)

    api = HomeAssistantAPI(ha_url, ha_token)

    if args.command == "info":
        command_info(api, args)
    elif args.command == "list":
        command_list(api, args)
    elif args.command == "get":
        command_get(api, args)
    elif args.command == "set":
        command_set(api, args)
    elif args.command == "service":
        command_service(api, args)


if __name__ == "__main__":
    main()
