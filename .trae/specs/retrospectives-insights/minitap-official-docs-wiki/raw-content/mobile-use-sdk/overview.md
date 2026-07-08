The mobile-use SDK follows a layered architecture designed to provide both simplicity for common use cases and flexibility for advanced scenarios.

The core concepts apply to both **Platform** and **Local** approaches. The platform simplifies configuration by managing profiles and tasks centrally, while local development gives you full control over all components.

## Architecture Diagram

## Key Components

## Agent

The central orchestrator for mobile automation

## Tasks

Goal-based automation workflows with structured output

## Profiles

Customize agent behavior and LLM configuration

## Builders

Fluent APIs for configuring agents and tasks

## Component Overview

### Agent Layer

The `Agent` class is the primary entry point that coordinates:

- Device connections (Android/iOS)
- Server lifecycle management
- Task creation and execution
- Resource cleanup

### Task Layer

Tasks represent automation workflows defined by:

- **Natural language goals** - What you want to accomplish
- **Structured output** - Type-safe results using Pydantic
- **Tracing** - Recording execution for debugging

### LangGraph Integration

The SDK leverages [LangGraph](https://github.com/langchain-ai/langgraph) for:

- **Agent reasoning** - Transparent decision-making process
- **Step-by-step execution** - Breaking complex tasks into manageable steps
- **Dynamic adaptation** - Responding to what’s on screen

### Device Interaction

Two key components handle device control:

Device Controller

Performs physical actions on the device using native platform tools:

- **Android**: Uses ADB (Android Debug Bridge) with UIAutomator2 for reliable UI automation
- **iOS**: Uses IDB (iOS Development Bridge) for simulator and device control

Capabilities include:

- Tap, swipe, scroll gestures
- App launching and navigation
- Key press events
- Text input

## Execution Flow

## Next Steps

## Agent

Learn about the Agent class

## Tasks

Understand task creation and execution
