"""pytest tests for Todo API."""

import pytest
import requests


class TestGetTodosId:
    """Tests for GET /todos/{id} - ."""

    def test_get_todos__id__success(self, api_client, base_url):
        """ - 正常场景：请求成功返回200。"""
        id = 5
        url = f'{base_url}/todos/{id}'
        params = {
            'completed': True,
        }
        json_body = None
        
        response = api_client.get(url, params=params, json=json_body)
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert 'title' in data
        assert 'completed' in data
        assert 'userId' in data

    def test_get_todos__id__negative_id(self, api_client, base_url):
        """ - 边界值：id为负数，期望400。"""
        id = -1
        url = f'{base_url}/todos/-1'
        params = {
            'completed': False,
        }
        json_body = None
        
        response = api_client.get(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_get_todos__id__NOT_FOUND(self, api_client, base_url):
        """ - 错误场景：待办事项不存在（404）。"""
        # TODO: 构造触发404 NOT_FOUND的请求数据
        id = 5
        url = f'{base_url}/todos/{id}'
        params = {
            'completed': False,
        }
        json_body = None
        
        response = api_client.get(url, params=params, json=json_body)
        assert response.status_code == 404

    def test_get_todos__id__example(self, api_client, base_url):
        """ - 文档示例断言。"""
        # === 来自文档 ```python example 代码块 ===
        response = api_client.get(f"{base_url}/todos/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "title" in data
        assert isinstance(data["completed"], bool)


class TestPostTodos:
    """Tests for POST /todos - ."""

    def test_post_todos_success(self, api_client, base_url):
        """ - 正常场景：请求成功返回201。"""
        url = f'{base_url}/todos'
        params = None
        json_body = {
            'title': "Buy milk",
            'userId': 1,
            'completed': False,
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 201
        data = response.json()
        assert 'id' in data
        assert 'title' in data
        assert 'userId' in data
        assert 'completed' in data

    def test_post_todos_missing_title(self, api_client, base_url):
        """ - 错误场景：缺少必填参数title（body），期望400。"""
        url = f'{base_url}/todos'
        params = None
        json_body = {
            'userId': 69,
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_post_todos_missing_userId(self, api_client, base_url):
        """ - 错误场景：缺少必填参数userId（body），期望400。"""
        url = f'{base_url}/todos'
        params = None
        json_body = {
            'title': "Title 31191",
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_post_todos_empty_title(self, api_client, base_url):
        """ - 边界值：title为空字符串，期望400。"""
        url = f'{base_url}/todos'
        params = None
        json_body = {
            'title': "",
            'userId': 69,
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_post_todos_negative_userId(self, api_client, base_url):
        """ - 边界值：userId为负数，期望400。"""
        url = f'{base_url}/todos'
        params = None
        json_body = {
            'title': "Title 31191",
            'userId': -1,
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 400

