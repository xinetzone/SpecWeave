---
name: graphql-blog-api
version: "1.0.0"
description: Blog platform GraphQL API providing posts, comments, and user management.
endpoint: https://api.example.com/graphql
schemaPath: inline
type: graphql
title: "Blog GraphQL API"
x-toml-ref: "../../.meta/toml/examples/mdi/graphql-blog.toml"
authors:
  - SpecWeave Team
license: MIT
tags:
  - graphql
  - blog
  - api
---
# Blog GraphQL API

GraphQL API for a blog platform supporting posts, comments, user authentication, and real-time updates via subscriptions.

## Overview

This API follows standard GraphQL conventions:
- Single endpoint: `/graphql`
- Query operations for reading data
- Mutation operations for writing data
- Subscription operations for real-time updates
- JWT-based authentication via Authorization header

## Authentication

All mutations and protected queries require a valid JWT token:

```
Authorization: Bearer <jwt_token>
```

Public queries (getPost, listPosts) do not require authentication.

## Schema Types

### User

```graphql
type User {
  id: ID!
  username: String!
  email: String!
  displayName: String
  avatarUrl: String
  createdAt: String!
  posts: [Post!]!
}
```

### Post

```graphql
type Post {
  id: ID!
  title: String!
  content: String!
  excerpt: String
  author: User!
  published: Boolean!
  tags: [String!]!
  comments: [Comment!]!
  createdAt: String!
  updatedAt: String
}
```

### Comment

```graphql
type Comment {
  id: ID!
  content: String!
  author: User!
  post: Post!
  createdAt: String!
}
```

### AuthPayload

```graphql
type AuthPayload {
  token: String!
  user: User!
}
```

### PostInput

```graphql
input PostInput {
  title: String!
  content: String!
  excerpt: String
  tags: [String!]
  published: Boolean
}

input CommentInput {
  content: String!
}
```

## Queries

### Get Single Post

Retrieve a single post by ID with author and comments.

```{query} getPost
:arg id: ID! - Post unique identifier
:returns Post - Requested post object
:error NOT_FOUND: Post does not exist
```

#### Query Example

```graphql
query GetPost($id: ID!) {
  getPost(id: $id) {
    id
    title
    content
    author {
      username
      displayName
    }
    comments {
      id
      content
      author {
        username
      }
    }
    createdAt
  }
}
```

#### Response Example

```json
{
  "data": {
    "getPost": {
      "id": "post_123",
      "title": "Introduction to GraphQL",
      "content": "GraphQL is a query language for APIs...",
      "author": {
        "username": "john_doe",
        "displayName": "John Doe"
      },
      "comments": [
        {
          "id": "comment_456",
          "content": "Great article!",
          "author": {
            "username": "jane_smith"
          }
        }
      ],
      "createdAt": "2026-07-01T10:00:00Z"
    }
  }
}
```

### List Posts

Retrieve a paginated list of posts with optional filtering.

```{query} listPosts
:arg page: Int - Page number (default: 1)
:arg limit: Int - Items per page (default: 10, max: 50)
:arg tag: String - Filter by tag
:arg authorId: ID - Filter by author ID
:returns [Post!]! - Paginated list of posts
```

#### Query Example

```graphql
query ListPosts($page: Int, $limit: Int, $tag: String) {
  listPosts(page: $page, limit: $limit, tag: $tag) {
    id
    title
    excerpt
    author {
      username
    }
    tags
    published
    createdAt
  }
}
```

### Me (Current User)

Get the currently authenticated user's profile.

```{query} me
:returns User - Current user profile
:error UNAUTHORIZED: Not authenticated
```

## Mutations

### Login

Authenticate a user and obtain JWT token.

```{mutation} login
:arg username: String! - Username or email
:arg password: String! - Password
:returns AuthPayload! - JWT token and user info
:error INVALID_CREDENTIALS: Username or password incorrect
:error TOO_MANY_REQUESTS: Rate limited
```

#### Mutation Example

```graphql
mutation Login($username: String!, $password: String!) {
  login(username: $username, password: $password) {
    token
    user {
      id
      username
      email
      displayName
    }
  }
}
```

#### Response Example

```json
{
  "data": {
    "login": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": {
        "id": "user_789",
        "username": "john_doe",
        "email": "john@example.com",
        "displayName": "John Doe"
      }
    }
  }
}
```

### Create Post

Create a new blog post (authentication required).

```{mutation} createPost
:arg input: PostInput! - Post data
:returns Post! - Created post
:error UNAUTHORIZED: Not authenticated
:error VALIDATION_ERROR: Invalid input data
```

#### Mutation Example

```graphql
mutation CreatePost($input: PostInput!) {
  createPost(input: $input) {
    id
    title
    content
    author {
      username
    }
    published
    createdAt
  }
}
```

#### Variables Example

```json
{
  "input": {
    "title": "Getting Started with MDI",
    "content": "MDI (Markdown Interface) is a new way to define APIs...",
    "excerpt": "Introduction to MDI concepts",
    "tags": ["api", "markdown", "mdi"],
    "published": true
  }
}
```

### Add Comment

Add a comment to a post (authentication required).

```{mutation} addComment
:arg postId: ID! - Post to comment on
:arg input: CommentInput! - Comment data
:returns Comment! - Created comment
:error UNAUTHORIZED: Not authenticated
:error NOT_FOUND: Post does not exist
```

## Subscriptions

### New Comment Subscription

Receive real-time notifications when new comments are added to a post.

```{subscription} onNewComment
:arg postId: ID! - Post to subscribe to
:returns Comment! - Newly added comment
```

#### Subscription Example

```graphql
subscription OnNewComment($postId: ID!) {
  onNewComment(postId: $postId) {
    id
    content
    author {
      username
      displayName
    }
    createdAt
  }
}
```

## Error Handling

Errors follow the standard GraphQL error format with extensions.code for machine-readable error types:

| Error Code | Meaning |
|------------|---------|
| UNAUTHORIZED | Missing or invalid JWT token |
| FORBIDDEN | Insufficient permissions |
| NOT_FOUND | Requested resource does not exist |
| VALIDATION_ERROR | Input validation failed |
| RATE_LIMITED | Too many requests |

## Checklist

- [x] Login mutation returns valid JWT token with correct credentials
- [x] Login mutation returns INVALID_CREDENTIALS error with wrong password
- [x] GetPost returns post data for valid ID
- [x] GetPost returns NOT_FOUND for non-existent post ID
- [x] ListPosts returns array of posts with default pagination
- [x] CreatePost requires authentication
- [x] CreatePost returns VALIDATION_ERROR for empty title
- [x] Me query returns UNAUTHORIZED without token
- [ ] Subscription real-time functionality
- [ ] Rate limiting verification
- [ ] Complex nested query performance testing
