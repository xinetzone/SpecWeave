---
name: user-api
version: "1.0.0"
description: User management REST API for authentication and profile operations.
baseUrl: https://api.example.com/v1
type: webapi
---

# User Management API

User management REST API providing authentication, profile management, and user listing capabilities. All endpoints require Bearer token authentication unless otherwise noted.

## Authentication

All endpoints except `/auth/login` and `/auth/register` require a valid Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Data Models

### User

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | yes | Unique user identifier |
| username | string | yes | Unique username (3-50 characters) |
| email | string | yes | User email address |
| full_name | string | no | User's full display name |
| role | string | yes | User role: `admin`, `user`, or `guest` |
| created_at | string | yes | Account creation timestamp (ISO 8601) |
| is_active | boolean | yes | Whether the account is active |

### AuthToken

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| access_token | string | yes | JWT access token |
| token_type | string | yes | Token type (always "bearer") |
| expires_in | integer | yes | Token expiration in seconds (default 3600) |

### CreateUserRequest

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | yes | Desired username (3-50 characters) |
| email | string | yes | User email address |
| password | string | yes | Account password (minimum 8 characters) |
| full_name | string | no | User's full display name |

### ErrorResponse

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| code | integer | yes | Error code |
| message | string | yes | Human-readable error message |
| details | object | no | Additional error context |

### PaginationMeta

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| page | integer | yes | Current page number (1-based) |
| per_page | integer | yes | Items per page |
| total | integer | yes | Total number of items |
| total_pages | integer | yes | Total number of pages |

## Endpoints

### User Login

Authenticate a user and obtain an access token. This endpoint does not require authentication.

```{endpoint} POST /auth/login
:summary: 用户登录获取access_token
:body username: string - Username or email (required)
:body password: string - Account password (required)
:response 200: AuthToken - Authentication successful, returns JWT token
:response 400: ErrorResponse - Missing required fields
:response 401: ErrorResponse - Invalid credentials
:response 429: ErrorResponse - Too many login attempts
```

#### Request Examples

Successful login request:

```json
{
  "username": "john_doe",
  "password": "mySecurePass123"
}
```

#### Response Examples

Successful authentication response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

Invalid credentials response:

```json
{
  "code": 401,
  "message": "Invalid username or password"
}
```

### User Registration

Register a new user account. This endpoint does not require authentication.

```{endpoint} POST /auth/register
:summary: 注册新用户账号
:body username: string - Desired username, 3-50 characters (required)
:body email: string - Valid email address (required)
:body password: string - Password, minimum 8 characters (required)
:body full_name: string? - User's full display name
:response 201: User - Account created successfully, returns user object
:response 400: ErrorResponse - Invalid input data or validation failed
:response 409: ErrorResponse - Username or email already exists
```

#### Request Examples

```json
{
  "username": "jane_smith",
  "email": "jane@example.com",
  "password": "SecurePass456",
  "full_name": "Jane Smith"
}
```

#### Response Examples

Successful registration:

```json
{
  "id": 42,
  "username": "jane_smith",
  "email": "jane@example.com",
  "full_name": "Jane Smith",
  "role": "user",
  "created_at": "2026-07-01T10:30:00Z",
  "is_active": true
}
```

Duplicate username error:

```json
{
  "code": 409,
  "message": "Username already exists"
}
```

### List Users

Retrieve a paginated list of users. Requires admin role.

```{endpoint} GET /users
:summary: 获取用户列表（分页）
:query page: integer? - Page number (default: 1)
:query per_page: integer? - Items per page, 1-100 (default: 20)
:query role: string? - Filter by role (admin/user/guest)
:query is_active: boolean? - Filter by active status
:response 200: User[] - List of user objects
:response 401: ErrorResponse - Missing or invalid token
:response 403: ErrorResponse - Insufficient permissions (requires admin)
```

#### Response Examples

```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Administrator",
    "role": "admin",
    "created_at": "2026-01-01T00:00:00Z",
    "is_active": true
  },
  {
    "id": 42,
    "username": "jane_smith",
    "email": "jane@example.com",
    "full_name": "Jane Smith",
    "role": "user",
    "created_at": "2026-07-01T10:30:00Z",
    "is_active": true
  }
]
```

### Get User Details

Retrieve details for a specific user by ID. Users can only access their own profile unless they have admin role.

```{endpoint} GET /users/{user_id}
:summary: 获取指定用户详情
:path user_id: integer - Unique user identifier
:response 200: User - User details object
:response 401: ErrorResponse - Missing or invalid token
:response 403: ErrorResponse - Cannot access another user's profile
:response 404: ErrorResponse - User not found
```

#### Response Examples

User found:

```json
{
  "id": 42,
  "username": "jane_smith",
  "email": "jane@example.com",
  "full_name": "Jane Smith",
  "role": "user",
  "created_at": "2026-07-01T10:30:00Z",
  "is_active": true
}
```

User not found:

```json
{
  "code": 404,
  "message": "User not found"
}
```

### Update User Profile

Update a user's profile information. Users can update their own profile; admins can update any user.

```{endpoint} PUT /users/{user_id}
:summary: 更新用户资料
:path user_id: integer - Unique user identifier
:body email: string? - Updated email address
:body full_name: string? - Updated display name
:body is_active: boolean? - Updated active status (admin only)
:response 200: User - Updated user object
:response 400: ErrorResponse - Invalid input data
:response 401: ErrorResponse - Missing or invalid token
:response 403: ErrorResponse - Insufficient permissions
:response 404: ErrorResponse - User not found
:response 409: ErrorResponse - Email already in use
```

#### Request Examples

```json
{
  "full_name": "Jane M. Smith",
  "email": "jane.smith@example.com"
}
```

## Checklist

- [x] Login endpoint returns 200 with valid credentials
- [x] Login endpoint returns 401 with invalid credentials
- [x] Register endpoint creates user with valid data
- [x] Register endpoint returns 409 for duplicate username
- [x] Users list requires authentication
- [x] Users list requires admin role
- [x] Get user returns 404 for non-existent user
- [x] All protected endpoints return 401 without token
- [ ] Password reset flow
- [ ] Email verification after registration
