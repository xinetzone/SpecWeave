"""pytest tests for 用户管理 API."""

import pytest
import requests


class TestGetUsers:
    """Tests for GET /users - 获取用户列表."""

    def test_get_users_success(self, api_client, base_url):
        """获取用户列表 - 正常场景：请求成功返回200。"""
        url = f'{base_url}/users'
        params = {
            'page': 1,
            'page_size': 20,
            'keyword': "test39364",
            'status': "active",
            'sort_by': "created_at",
            'sort_order': "desc",
        }
        json_body = None
        
        response = api_client.get(url, params=params, json=json_body)
        assert response.status_code == 200
        data = response.json()
        assert 'total' in data
        assert 'page' in data
        assert 'page_size' in data
        assert 'items' in data

    def test_get_users_err_401(self, api_client, base_url):
        """获取用户列表 - 错误场景：未授权（401）。"""
        # TODO: 构造触发401 的请求数据
        url = f'{base_url}/users'
        params = {
            'page': 1,
            'page_size': 20,
            'keyword': "test39364",
            'status': "active",
            'sort_by': "created_at",
            'sort_order': "desc",
        }
        json_body = None
        
        response = api_client.get(url, params=params, json=json_body)
        assert response.status_code == 401

    def test_get_users_err_403(self, api_client, base_url):
        """获取用户列表 - 错误场景：权限不足（403）。"""
        # TODO: 构造触发403 的请求数据
        url = f'{base_url}/users'
        params = {
            'page': 1,
            'page_size': 20,
            'keyword': "test39364",
            'status': "active",
            'sort_by': "created_at",
            'sort_order': "desc",
        }
        json_body = None
        
        response = api_client.get(url, params=params, json=json_body)
        assert response.status_code == 403


class TestGetUsersUserId:
    """Tests for GET /users/{user_id} - 获取用户详情."""

    def test_get_users__user_id__success(self, api_client, base_url):
        """获取用户详情 - 正常场景：请求成功返回200。"""
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = None
        json_body = None
        
        response = api_client.get(url, params=params, json=json_body)
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert 'name' in data
        assert 'email' in data
        assert 'avatar' in data
        assert 'status' in data
        assert 'role' in data
        assert 'bio' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_get_users__user_id__empty_user_id(self, api_client, base_url):
        """获取用户详情 - 边界值：user_id为空字符串，期望400。"""
        user_id = ""
        url = f'{base_url}/users/'
        params = None
        json_body = None
        
        response = api_client.get(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_get_users__user_id__USER_NOT_FOUND(self, api_client, base_url):
        """获取用户详情 - 错误场景：用户不存在（404）。"""
        # TODO: 构造触发404 USER_NOT_FOUND的请求数据
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = None
        json_body = None
        
        response = api_client.get(url, params=params, json=json_body)
        assert response.status_code == 404

    def test_get_users__user_id__err_401(self, api_client, base_url):
        """获取用户详情 - 错误场景：未授权（401）。"""
        # TODO: 构造触发401 的请求数据
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = None
        json_body = None
        
        response = api_client.get(url, params=params, json=json_body)
        assert response.status_code == 401

    def test_get_users__user_id__err_403(self, api_client, base_url):
        """获取用户详情 - 错误场景：权限不足（403）。"""
        # TODO: 构造触发403 的请求数据
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = None
        json_body = None
        
        response = api_client.get(url, params=params, json=json_body)
        assert response.status_code == 403


class TestPostUsers:
    """Tests for POST /users - 创建新用户."""

    def test_post_users_success(self, api_client, base_url):
        """创建新用户 - 正常场景：请求成功返回201。"""
        url = f'{base_url}/users'
        params = None
        json_body = {
            'name': "李四",
            'email': "lisi@example.com",
            'password': "SecurePass123",
            'role': "user",
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 201

    def test_post_users_missing_name(self, api_client, base_url):
        """创建新用户 - 错误场景：缺少必填参数name（body），期望400。"""
        url = f'{base_url}/users'
        params = None
        json_body = {
            'email': "user_74652@example.com",
            'password': "TestPass34075!@",
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_post_users_missing_email(self, api_client, base_url):
        """创建新用户 - 错误场景：缺少必填参数email（body），期望400。"""
        url = f'{base_url}/users'
        params = None
        json_body = {
            'name': "Test Name 43420",
            'password': "TestPass34075!@",
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_post_users_missing_password(self, api_client, base_url):
        """创建新用户 - 错误场景：缺少必填参数password（body），期望400。"""
        url = f'{base_url}/users'
        params = None
        json_body = {
            'name': "Test Name 43420",
            'email': "user_74652@example.com",
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_post_users_empty_name(self, api_client, base_url):
        """创建新用户 - 边界值：name为空字符串，期望400。"""
        url = f'{base_url}/users'
        params = None
        json_body = {
            'name': "",
            'email': "user_74652@example.com",
            'password': "TestPass34075!@",
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_post_users_empty_email(self, api_client, base_url):
        """创建新用户 - 边界值：email为空字符串，期望400。"""
        url = f'{base_url}/users'
        params = None
        json_body = {
            'name': "Test Name 43420",
            'email': "",
            'password': "TestPass34075!@",
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_post_users_empty_password(self, api_client, base_url):
        """创建新用户 - 边界值：password为空字符串，期望400。"""
        url = f'{base_url}/users'
        params = None
        json_body = {
            'name': "Test Name 43420",
            'email': "user_74652@example.com",
            'password': "",
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_post_users_EMAIL_ALREADY_EXISTS(self, api_client, base_url):
        """创建新用户 - 错误场景：邮箱已被注册（409）。"""
        # TODO: 构造触发409 EMAIL_ALREADY_EXISTS的请求数据
        url = f'{base_url}/users'
        params = None
        json_body = {
            'name': "Test Name 43420",
            'email': "user_74652@example.com",
            'password': "TestPass34075!@",
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 409

    def test_post_users_err_401(self, api_client, base_url):
        """创建新用户 - 错误场景：未授权（401）。"""
        # TODO: 构造触发401 的请求数据
        url = f'{base_url}/users'
        params = None
        json_body = {
            'name': "Test Name 43420",
            'email': "user_74652@example.com",
            'password': "TestPass34075!@",
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 401

    def test_post_users_err_403(self, api_client, base_url):
        """创建新用户 - 错误场景：权限不足（仅管理员可创建用户）（403）。"""
        # TODO: 构造触发403 的请求数据
        url = f'{base_url}/users'
        params = None
        json_body = {
            'name': "Test Name 43420",
            'email': "user_74652@example.com",
            'password': "TestPass34075!@",
        }
        
        response = api_client.post(url, params=params, json=json_body)
        assert response.status_code == 403


class TestPutUsersUserId:
    """Tests for PUT /users/{user_id} - 更新用户信息."""

    def test_put_users__user_id__success(self, api_client, base_url):
        """更新用户信息 - 正常场景：请求成功返回200。"""
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = None
        json_body = {
            'name': "李四（已认证）",
            'bio': "更新后的个人简介",
        }
        
        response = api_client.put(url, params=params, json=json_body)
        assert response.status_code == 200

    def test_put_users__user_id__empty_user_id(self, api_client, base_url):
        """更新用户信息 - 边界值：user_id为空字符串，期望400。"""
        user_id = ""
        url = f'{base_url}/users/'
        params = None
        json_body = {
        }
        
        response = api_client.put(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_put_users__user_id__USER_NOT_FOUND(self, api_client, base_url):
        """更新用户信息 - 错误场景：用户不存在（404）。"""
        # TODO: 构造触发404 USER_NOT_FOUND的请求数据
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = None
        json_body = {
        }
        
        response = api_client.put(url, params=params, json=json_body)
        assert response.status_code == 404

    def test_put_users__user_id__EMAIL_ALREADY_EXISTS(self, api_client, base_url):
        """更新用户信息 - 错误场景：邮箱已被其他用户使用（409）。"""
        # TODO: 构造触发409 EMAIL_ALREADY_EXISTS的请求数据
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = None
        json_body = {
        }
        
        response = api_client.put(url, params=params, json=json_body)
        assert response.status_code == 409

    def test_put_users__user_id__err_401(self, api_client, base_url):
        """更新用户信息 - 错误场景：未授权（401）。"""
        # TODO: 构造触发401 的请求数据
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = None
        json_body = {
        }
        
        response = api_client.put(url, params=params, json=json_body)
        assert response.status_code == 401

    def test_put_users__user_id__err_403(self, api_client, base_url):
        """更新用户信息 - 错误场景：权限不足（403）。"""
        # TODO: 构造触发403 的请求数据
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = None
        json_body = {
        }
        
        response = api_client.put(url, params=params, json=json_body)
        assert response.status_code == 403


class TestDeleteUsersUserId:
    """Tests for DELETE /users/{user_id} - 删除用户."""

    def test_delete_users__user_id__success(self, api_client, base_url):
        """删除用户 - 正常场景：请求成功返回204。"""
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = {
            'force': False,
        }
        json_body = None
        
        response = api_client.delete(url, params=params, json=json_body)
        assert response.status_code == 204

    def test_delete_users__user_id__empty_user_id(self, api_client, base_url):
        """删除用户 - 边界值：user_id为空字符串，期望400。"""
        user_id = ""
        url = f'{base_url}/users/'
        params = {
            'force': False,
        }
        json_body = None
        
        response = api_client.delete(url, params=params, json=json_body)
        assert response.status_code == 400

    def test_delete_users__user_id__USER_NOT_FOUND(self, api_client, base_url):
        """删除用户 - 错误场景：用户不存在（404）。"""
        # TODO: 构造触发404 USER_NOT_FOUND的请求数据
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = {
            'force': False,
        }
        json_body = None
        
        response = api_client.delete(url, params=params, json=json_body)
        assert response.status_code == 404

    def test_delete_users__user_id__USER_HAS_DEPENDENCIES(self, api_client, base_url):
        """删除用户 - 错误场景：用户有关联数据无法删除（需先处理关联资源）（409）。"""
        # TODO: 构造触发409 USER_HAS_DEPENDENCIES的请求数据
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = {
            'force': False,
        }
        json_body = None
        
        response = api_client.delete(url, params=params, json=json_body)
        assert response.status_code == 409

    def test_delete_users__user_id__err_401(self, api_client, base_url):
        """删除用户 - 错误场景：未授权（401）。"""
        # TODO: 构造触发401 的请求数据
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = {
            'force': False,
        }
        json_body = None
        
        response = api_client.delete(url, params=params, json=json_body)
        assert response.status_code == 401

    def test_delete_users__user_id__err_403(self, api_client, base_url):
        """删除用户 - 错误场景：权限不足（403）。"""
        # TODO: 构造触发403 的请求数据
        user_id = "usr_61012"
        url = f'{base_url}/users/{user_id}'
        params = {
            'force': False,
        }
        json_body = None
        
        response = api_client.delete(url, params=params, json=json_body)
        assert response.status_code == 403

