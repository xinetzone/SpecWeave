"""Home Assistant API 自动化脚本测试用例。

这些测试用例验证 ha_api.py 的核心功能，包括：
- 参数解析
- 配置加载
- 错误处理
- 优雅降级机制
- dataclass 数据结构

由于需要实际的 Home Assistant 实例进行完整测试，
这些测试主要验证脚本的基本功能和错误处理逻辑。
"""

import argparse
import os
import sys
from unittest import mock, TestCase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ha_api import (
    HAConfig,
    EntityState,
    HARequest,
    HAResponse,
    HomeAssistantAPI,
    load_config,
    command_set,
    command_service,
)


class TestDataclasses(TestCase):
    """测试 dataclass 数据结构。"""

    def test_ha_config_is_configured(self):
        """测试 HAConfig.is_configured() 方法。"""
        config = HAConfig(ha_url="http://test:8123", ha_token="token")
        self.assertTrue(config.is_configured())

        config_empty = HAConfig()
        self.assertFalse(config_empty.is_configured())

    def test_entity_state_from_api_response(self):
        """测试 EntityState.from_api_response() 工厂方法。"""
        data = {
            "entity_id": "light.test",
            "state": "on",
            "attributes": {
                "friendly_name": "Test Light",
                "entity_category": "config",
            },
        }
        entity = EntityState.from_api_response(data)

        self.assertEqual(entity.entity_id, "light.test")
        self.assertEqual(entity.state, "on")
        self.assertEqual(entity.friendly_name, "Test Light")
        self.assertEqual(entity.entity_category, "config")
        self.assertEqual(entity.attributes, data["attributes"])

    def test_ha_response_properties(self):
        """测试 HAResponse 属性方法。"""
        success_response = HAResponse(status_code=200, data={"result": "ok"})
        self.assertTrue(success_response.is_success)
        self.assertFalse(success_response.is_network_error)

        error_response = HAResponse(status_code=500, data={"error": "failed"})
        self.assertFalse(error_response.is_success)
        self.assertFalse(error_response.is_network_error)

        network_error = HAResponse(status_code=-1, data={"error": "timeout"}, error="timeout")
        self.assertFalse(network_error.is_success)
        self.assertTrue(network_error.is_network_error)

    def test_ha_request(self):
        """测试 HARequest 数据类。"""
        request = HARequest(method="POST", endpoint="/states/light.test", data={"state": "on"})
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.endpoint, "/states/light.test")
        self.assertEqual(request.data, {"state": "on"})


class TestLoadConfig(TestCase):
    """测试配置加载功能。"""

    def test_load_config_from_env(self):
        """测试从环境变量加载配置。"""
        with mock.patch.dict(os.environ, {"HA_URL": "http://test:8123", "HA_TOKEN": "test-token"}):
            config = load_config()
            self.assertEqual(config.ha_url, "http://test:8123")
            self.assertEqual(config.ha_token, "test-token")

    def test_load_config_empty(self):
        """测试配置为空的情况。"""
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("ha_api.Path.exists", return_value=False):
                config = load_config()
                self.assertFalse(config.is_configured())


class TestHomeAssistantAPI(TestCase):
    """测试 HomeAssistantAPI 类。"""

    def setUp(self):
        self.api = HomeAssistantAPI("http://test:8123", "test-token")

    def test_init(self):
        """测试初始化。"""
        self.assertEqual(self.api.ha_url, "http://test:8123")
        self.assertEqual(self.api.ha_token, "test-token")
        self.assertIn("Authorization", self.api.headers)
        self.assertIn("Content-Type", self.api.headers)

    def test_request_timeout(self):
        """测试请求超时处理。"""
        with mock.patch("ha_api.requests") as mock_requests:
            mock_requests.exceptions.RequestException = Exception
            mock_requests.request.side_effect = mock_requests.exceptions.RequestException("timeout")
            status_code, data = self.api._request("GET", "/")
            self.assertEqual(status_code, -1)
            self.assertIn("error", data)


class TestCommands(TestCase):
    """测试命令处理函数。"""

    def test_command_set_dry_run(self):
        """测试 set 命令的 dry-run 模式。"""
        api = HomeAssistantAPI("http://test:8123", "test-token")
        args = argparse.Namespace(
            entity_id="light.test",
            value="true",
            brightness=None,
            temperature=None,
            humidity=None,
            dry_run=True,
            verbose=False,
        )

        with mock.patch("ha_api.print_result") as mock_print:
            command_set(api, args)
            mock_print.assert_not_called()

    def test_command_service_dry_run(self):
        """测试 service 命令的 dry-run 模式。"""
        api = HomeAssistantAPI("http://test:8123", "test-token")
        args = argparse.Namespace(
            service="light.turn_on",
            entity_id="light.test",
            value=None,
            brightness=None,
            temperature=None,
            dry_run=True,
            verbose=False,
        )

        with mock.patch("ha_api.print_result") as mock_print:
            command_service(api, args)
            mock_print.assert_not_called()


if __name__ == "__main__":
    import unittest
    unittest.main()
