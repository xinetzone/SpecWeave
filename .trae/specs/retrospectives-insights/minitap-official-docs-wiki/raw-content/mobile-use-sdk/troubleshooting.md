This guide helps you diagnose and resolve common issues when working with the Mobile Use SDK.

## Device Connection Issues

### No Device Found

Symptoms

- Error: `DeviceNotFoundError: No device found. Exiting.`
- Agent initialization fails

Solutions

**1\. Verify device connection**

```shellscript
adb devices
```

You should see your device listed with status “device”

```shellscript
idevice_id -l
```

**2\. Enable USB debugging (Android)**

- Settings → About Phone → Tap “Build Number” 7 times
- Settings → Developer options → USB debugging

**3\. Trust computer (iOS)**

- Unlock your device
- Tap “Trust” when prompted

**4\. Reset ADB**

```shellscript
adb kill-server
adb start-server
```

**5\. Specify device manually**

```python
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import DevicePlatform

config = (
    Builders.AgentConfig
    .for_device(platform=DevicePlatform.ANDROID, device_id="your_device_id")
    .build()
)
agent = Agent(config=config)
```

---

### USB Connection Unstable

Symptoms

- Random disconnections during automation
- `adb: error: device 'xxx' not found`

Solutions

**1\. Use a high-quality USB cable**

Poor quality cables can cause intermittent connections.

**2\. Connect directly to computer**

Avoid USB hubs which can cause instability.

**3\. Increase ADB timeout**

```shellscript
adb shell settings put global adb_timeout 0
```

**4\. Use wireless debugging**

```shellscript
# Enable TCP/IP mode
adb tcpip 5555

# Connect wirelessly
adb connect <device_ip>:5555
```

Ensure stable Wi-Fi connection for wireless debugging.

---

## Server-Related Issues

### Servers Fail to Start

Symptoms

- `ServerStartupError` during initialization
- Ports already in use
- Zombie processes from previous runs

Solutions

**1\. Force clean zombie servers**

```python
agent = Agent()

# Kill any existing mobile-use servers
agent.clean(force=True)

# Now initialize
agent.init()
```

**2\. Verify platform tools are installed**

```shellscript
adb version
```

If not installed, download [Android SDK Platform Tools](https://developer.android.com/tools/adb)

```shellscript
idb --help
```

If not installed, install via: `brew install idb-companion`

**3\. Check idb\_companion status (iOS)**

```shellscript
# Check if idb_companion is running
pgrep -l idb_companion

# Start idb_companion if needed
idb_companion --udid booted
```

**4\. Check for port conflicts**

```shellscript
# Linux/Mac
lsof -i :8000
lsof -i :8001

# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :8001
```

---

## Task Execution Issues

### Agent Not Initialized

Symptoms

- Error: `AgentNotInitializedError`

Solution

Always call `agent.init()` before running tasks:

```python
agent = Agent()

# Initialize first!
if not agent.init():
    print("Initialization failed")
    exit(1)

# Now you can run tasks
await agent.run_task(goal="Your task")
```

---

### Task Times Out or Fails

Symptoms

- Task gets stuck or fails to complete
- Reaches max\_steps limit
- Unexpected results

Solutions

**1\. Simplify the task goal**

Break complex tasks into smaller steps:

```python
# ❌ Too complex
await agent.run_task(
    goal="Open settings, go to network, enable airplane mode, "
         "wait 5 seconds, then disable airplane mode"
)

# ✅ Break into steps
await agent.run_task(goal="Open settings and go to network settings")
await agent.run_task(goal="Enable airplane mode")
await asyncio.sleep(5)
await agent.run_task(goal="Disable airplane mode")
```

**2\. Increase max\_steps limit**

```python
task = (
    agent.new_task("Complex goal...")
    .with_max_steps(500)  # Default is 400
    .build()
)

await agent.run_task(request=task)
```

**3\. Enable tracing to debug**

```python
task = (
    agent.new_task("Your goal")
    .with_trace_recording(enabled=True)
    .build()
)

await agent.run_task(request=task)
# Check traces in mobile-use-traces/ directory
```

**4\. Be more specific in goals**

```python
# ❌ Vague
goal = "Check the weather"

# ✅ Specific
goal = "Open the Weather app, check the current temperature in Celsius for New York, and tell me tomorrow's forecast"
```

---

### Incorrect Task Results

Symptoms

- Task returns unexpected or incomplete data
- Structured output fields are missing or incorrect

Solutions

**1\. Use structured output with clear descriptions**

```python
from pydantic import BaseModel, Field

class WeatherInfo(BaseModel):
    current_temp: float = Field(
        ..., 
        description="Current temperature in Celsius"
    )
    condition: str = Field(
        ..., 
        description="Current weather condition (sunny, cloudy, rainy, etc.)"
    )
    tomorrow_forecast: str = Field(
        ..., 
        description="Detailed weather forecast for tomorrow"
    )

result = await agent.run_task(
    goal="Check weather for today and tomorrow",
    output=WeatherInfo
)
```

**2\. Provide more context in the goal**

```python
# ❌ Unclear
goal = "Get product info"

# ✅ Clear
goal = "Go to Amazon, search for 'wireless headphones', open the first result, and get the product name, price, and rating"
```

**3\. Use better LLM models for cortex**

```python
from minitap.mobile_use.config import LLM, LLMConfig, LLMWithFallback

profile = AgentProfile(
    name="accurate",
    llm_config=LLMConfig(
        cortex=LLMWithFallback(
            provider="openai",
            model="o4-mini",  # More powerful model
            fallback=LLM(provider="openai", model="gpt-5")
        ),
        # ... other components
    )
)
```

---

## LLM and API Issues

### API Key Authentication

Symptoms

Solutions

**1\. Verify API keys in.env file**

```shellscript
# Required based on your LLM config
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...
OPEN_ROUTER_API_KEY=sk-or-...
GOOGLE_API_KEY=...
```

**2\. Load environment variables**

The SDK automatically loads `.env` files, but you can also set manually:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Explicit load

# Or set programmatically
os.environ["OPENAI_API_KEY"] = "your_key"
```

**3\. Check API key validity**

Test your keys directly:

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[{"role": "user", "content": "test"}]
)
print("API key works!")
```

---

### Rate Limiting

Symptoms

- 429 Too Many Requests errors
- Tasks slow down over time

Solutions

**1\. Use different providers**

Distribute load across multiple LLM providers:

```python
llm_config = LLMConfig(
    planner=LLM(provider="openai", model="gpt-5-nano"),
    cortex=LLM(provider="google", model="gemini-2.5-flash"),
    executor=LLM(provider="openrouter", model="meta-llama/llama-4-scout")
)
```

**2\. Use tier limits**

Check your API tier limits and upgrade if needed.

**3\. Add delays between tasks**

```python
import asyncio

for task_goal in task_list:
    await agent.run_task(goal=task_goal)
    await asyncio.sleep(2)  # Brief delay
```

---

## System Environment Issues

### Python Version Compatibility

Symptoms

- Import errors or syntax errors
- `SyntaxError` or `ModuleNotFoundError`

Solution

Ensure you’re using Python 3.12 or higher:

```shellscript
python --version
# Should be 3.12.x or higher
```

**Create compatible environment:**

- venv

```shellscript
# UV handles Python versions automatically
curl -LsSf https://astral.sh/uv/install.sh | sh

uv venv --python 3.12
source .venv/bin/activate
uv add minitap-mobile-use
```

```shellscript
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install minitap-mobile-use
```

---

### Import Errors

Symptoms

- `ModuleNotFoundError: No module named 'minitap'`
- Import errors for SDK components

Solutions

**1\. Verify installation**

```shellscript
pip list | grep minitap
# Should show: minitap-mobile-use
```

**2\. Reinstall the SDK**

```shellscript
pip uninstall minitap-mobile-use
pip install minitap-mobile-use
```

**3\. Check virtual environment**

Ensure you’re in the correct virtual environment:

```shellscript
which python
# Should point to your venv
```

---

## Debugging Best Practices

### Enable Comprehensive Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or for mobile-use specifically
from minitap.mobile_use.utils.logger import get_logger

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)
```

### Use Trace Recording

Always enable tracing during development:

```python
from pathlib import Path
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
trace_path = Path(f"/tmp/debug_traces/{timestamp}")

task = (
    agent.new_task("Your goal")
    .with_trace_recording(enabled=True, path=trace_path)
    .with_thoughts_output_saving(path=f"{trace_path}/thoughts.txt")
    .with_llm_output_saving(path=f"{trace_path}/output.json")
    .build()
)
```

### Check Trace Contents

After a failed task, examine the traces:

```shellscript
ls /tmp/debug_traces/20241009_175416/

# View screenshots to see what the agent saw
# Read thoughts.txt to understand agent reasoning
# Check output.json for structured results
```

---

## Getting Help

## GitHub Issues

Search existing issues or create a new one

## Discord Community

Get help from the community

### Filing a Bug Report

When filing an issue, include:

---

## Quick Reference

Clean zombie servers

```python
agent.clean(force=True)
agent.init()
```

Check device connection

```shellscript
# Android
adb devices

# iOS
idevice_id -l
```

Enable debug logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Enable tracing

```python
task = agent.new_task(goal).with_trace_recording(True).build()
```

Reset ADB

```shellscript
adb kill-server
adb start-server
```

## Next Steps

## SDK Reference

Complete SDK documentation

## Examples

Working code examples
