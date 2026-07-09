---
id: "analyze-omniroute-ai-gateway-08"
title: "安全特性与数据隐私"
theme: "retrospectives-insights"
source: "article-content.md"
chapter: 8
created: "2026-07-09"
---

# 安全特性与数据隐私

## 本地运行架构

OmniRoute采用本地运行架构，所有服务都在用户本地机器上运行，不走云端中转。

## 数据主权

用户的数据、API key、请求记录全部存储在自己的机器上，完全由用户掌控。

## 加密机制

采用AES-256-GCM加密存储敏感数据，提供企业级的安全保障。

## 隐私承诺

OmniRoute承诺不收集任何遥测数据，用户的使用行为不会被追踪或上传。

## Dashboard本地访问

Dashboard仅通过localhost:20128本地访问，不对外暴露端口，减少攻击面。

## 与云端网关的核心差异

本地网关与云端网关的核心差异在于数据泄露风险：本地运行架构下，数据不会经过第三方服务器，从根本上消除了云端网关可能存在的数据泄露风险。
