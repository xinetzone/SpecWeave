Reference for exception classes in the mobile-use SDK.

## Import

```python
from minitap.mobile_use.sdk.types.exceptions import (
    MobileUseError,
    AgentError,
    AgentProfileNotFoundError,
    AgentTaskRequestError,
    AgentNotInitializedError,
    AgentInvalidApiKeyError,
    DeviceError,
    DeviceNotFoundError,
    ServerError,
    ServerStartupError,
    ExecutableNotFoundError,
    PlatformServiceUninitializedError,
    PlatformServiceError,
)
```

## Exception Hierarchy

```text
MobileUseError (base)
├── AgentError
│   ├── AgentNotInitializedError
│   ├── AgentTaskRequestError
│   │   ├── AgentProfileNotFoundError
│   │   └── AgentInvalidApiKeyError
├── DeviceError
│   └── DeviceNotFoundError
├── ServerError
│   └── ServerStartupError
├── ExecutableNotFoundError
├── PlatformServiceUninitializedError
└── PlatformServiceError
```

## Base Exception

### MobileUseError

Base exception for all SDK errors.

```python
from minitap.mobile_use.sdk.types.exceptions import MobileUseError

try:
    await agent.run_task(goal="...")
except MobileUseError as e:
    print(f"SDK error: {e}")
```

Use this to catch any SDK-related error.

---

## Agent Exceptions

### AgentError

Base exception for agent-related errors.

```python
from minitap.mobile_use.sdk.types.exceptions import AgentError

try:
    await agent.run_task(goal="...")
except AgentError as e:
    print(f"Agent error: {e}")
```

---

### AgentNotInitializedError

Raised when agent methods are called before initialization.

**Common cause:** Calling `run_task()` before `init()`

```python
from minitap.mobile_use.sdk.types.exceptions import AgentNotInitializedError

agent = Agent()

try:
    # This will raise AgentNotInitializedError
    await agent.run_task(goal="Check notifications")
except AgentNotInitializedError:
    print("Agent not initialized. Call agent.init() first.")
```

**Solution:**

```python
agent = Agent()
agent.init()  # Initialize first
await agent.run_task(goal="Check notifications")
```

---

### AgentProfileNotFoundError

Raised when a specified profile is not found.

**Common cause:** Using a profile name that hasn’t been registered

```python
from minitap.mobile_use.sdk.types.exceptions import AgentProfileNotFoundError

try:
    await agent.run_task(
        goal="Some task",
        profile="non_existent_profile"
    )
except AgentProfileNotFoundError as e:
    print(f"Profile not found: {e}")
```

**Solution:**

```python
# Ensure profile is registered
profile = AgentProfile(name="my_profile", from_file="config.jsonc")
config = Builders.AgentConfig.add_profile(profile).build()
agent = Agent(config=config)
```

---

### AgentTaskRequestError

Raised for task request validation errors.

**Common causes:**

- Invalid task configuration
- Conflicting parameters

```python
from minitap.mobile_use.sdk.types.exceptions import AgentTaskRequestError

try:
    # Invalid configuration
    task = agent.new_task("").build()  # Empty goal
except AgentTaskRequestError as e:
    print(f"Invalid task request: {e}")
```

---

### AgentInvalidApiKeyError

Raised when the Minitap API key is invalid or unauthorized.

**Common causes:**

- Incorrect API key
- Expired API key
- API key not set

```python
from minitap.mobile_use.sdk.types.exceptions import AgentInvalidApiKeyError
from minitap.mobile_use.sdk.types import PlatformTaskRequest

try:
    # Using invalid API key
    result = await agent.run_task(
        request=PlatformTaskRequest(
            task="check-notifications",
            api_key="invalid_key"
        )
    )
except AgentInvalidApiKeyError:
    print("Invalid API key. Get a new one from https://platform.mobile-use.ai/api-keys")
```

**Solution:**

```python
# Set valid API key in .env
MINITAP_API_KEY=your_valid_key_here
MINITAP_BASE_URL=https://platform.mobile-use.ai/api/v1  # Optional, this is the default
```

---

## Device Exceptions

### DeviceError

Base exception for device-related errors.

```python
from minitap.mobile_use.sdk.types.exceptions import DeviceError

try:
    agent.init()
except DeviceError as e:
    print(f"Device error: {e}")
```

---

### DeviceNotFoundError

Raised when no device is found or device becomes disconnected.

**Common causes:**

- No device connected
- USB debugging not enabled
- Device unplugged during operation

```python
from minitap.mobile_use.sdk.types.exceptions import DeviceNotFoundError

try:
    agent.init()
except DeviceNotFoundError:
    print("No device found. Please connect a device and enable USB debugging.")
```

**Solutions:**

1. **Check device connection:**

```shellscript
# Android
adb devices

# iOS
idevice_id -l
```

2. **Enable USB debugging** (Android)
3. **Specify device explicitly:**

```python
config = (
    Builders.AgentConfig
    .for_device(platform=DevicePlatform.ANDROID, device_id="your_device_id")
    .build()
)
```

---

## Server Exceptions

### ServerError

Base exception for server-related errors.

```python
from minitap.mobile_use.sdk.types.exceptions import ServerError

try:
    agent.init()
except ServerError as e:
    print(f"Server error: {e}")
```

---

### ServerStartupError

Raised when server startup fails.

**Common causes:**

- Port already in use
- Missing dependencies (ADB for Android, idb for iOS)
- Permission issues

```python
from minitap.mobile_use.sdk.types.exceptions import ServerStartupError

try:
    agent.init()
except ServerStartupError as e:
    print(f"Failed to start servers: {e}")
```

**Solutions:**

1. **Kill zombie servers:**

```python
agent.clean(force=True)  # Clean up existing servers
agent.init()
```

2. **Verify platform tools are installed:**

```shellscript
# Android
adb version

# iOS
idb --help
```

---

## Executable Exceptions

### ExecutableNotFoundError

Raised when required system executables are not found in PATH.

**Common causes:**

- `adb` not installed (for Android)
- `idb` not installed (for iOS)
- `xcrun` not installed (for iOS on macOS)

```python
from minitap.mobile_use.sdk.types.exceptions import ExecutableNotFoundError

try:
    agent.init()
except ExecutableNotFoundError as e:
    print(f"Missing executable: {e}")
```

**Solutions:**

1. **Install ADB** (for Android):

```shellscript
# Visit: https://developer.android.com/tools/adb
# Or use package manager
brew install android-platform-tools  # macOS
sudo apt install adb                 # Linux
```

2. **Install idb** (for iOS):

```shellscript
brew install idb-companion
```

3. **Install Xcode Command Line Tools** (for iOS):

```shellscript
xcode-select --install
```

---

## Platform Exceptions

### PlatformServiceUninitializedError

Raised when attempting to use platform features without proper initialization.

**Common causes:**

- `MINITAP_API_KEY` not set in environment
- No API key provided in PlatformTaskRequest
- Platform service not configured

```python
from minitap.mobile_use.sdk.types.exceptions import PlatformServiceUninitializedError
from minitap.mobile_use.sdk.types import PlatformTaskRequest

try:
    # Missing API key
    result = await agent.run_task(
        request=PlatformTaskRequest(task="check-notifications")
    )
except PlatformServiceUninitializedError:
    print("Platform service not initialized. Set MINITAP_API_KEY in .env")
```

**Solution:**

```shellscript
# Add to .env file
MINITAP_API_KEY=your_api_key_here
MINITAP_BASE_URL=https://platform.mobile-use.ai/api/v1  # Optional, this is the default
```

Or provide API key directly:

```python
result = await agent.run_task(
    request=PlatformTaskRequest(
        task="check-notifications",
        api_key="your_api_key_here"
    )
)
```

---

### PlatformServiceError

Base exception for platform service-related errors.

**Common causes:**

- Network connectivity issues
- Platform API errors
- Invalid task configuration on platform

```python
from minitap.mobile_use.sdk.types.exceptions import PlatformServiceError

try:
    result = await agent.run_task(
        request=PlatformTaskRequest(task="my-task")
    )
except PlatformServiceError as e:
    print(f"Platform service error: {e}")
```

**Solutions:**

1. Check network connectivity
2. Verify task exists on platform
3. Check platform status at [platform.mobile-use.ai](https://platform.mobile-use.ai/)

---

## Exception Handling Best Practices

### 1\. Always Clean Up

```python
agent = Agent()

try:
    agent.init()
    await agent.run_task(goal="...")
except MobileUseError as e:
    print(f"Error: {e}")
finally:
    agent.clean()  # Always clean up
```

### 2\. Handle Specific Exceptions

```python
from minitap.mobile_use.sdk.types.exceptions import (
    AgentNotInitializedError,
    DeviceNotFoundError,
    ServerStartupError,
    ExecutableNotFoundError,
    PlatformServiceUninitializedError,
    AgentInvalidApiKeyError,
)

try:
    agent.init()
    await agent.run_task(goal="...")
    
except ExecutableNotFoundError as e:
    print(f"Missing required executable: {e}")
    
except DeviceNotFoundError:
    print("Please connect a device")
    
except ServerStartupError:
    print("Server startup failed. Try agent.clean(force=True)")
    
except AgentNotInitializedError:
    print("Call agent.init() first")
    
except PlatformServiceUninitializedError:
    print("Platform service not initialized. Set MINITAP_API_KEY")
    
except AgentInvalidApiKeyError:
    print("Invalid API key. Visit https://platform.mobile-use.ai/api-keys")
    
except Exception as e:
    print(f"Unexpected error: {e}")
    raise
```

### 3\. Check Initialization

```python
agent = Agent()

if not agent.init():
    print("Initialization failed")
    exit(1)

# Safe to proceed
await agent.run_task(goal="...")
```

### 4\. Retry Logic

```python
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        agent.init()
        break
    except ServerStartupError:
        if attempt < max_retries - 1:
            print(f"Retry {attempt + 1}/{max_retries}")
            agent.clean(force=True)
            time.sleep(2)
        else:
            raise
```

## Complete Example

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types.exceptions import (
    AgentNotInitializedError,
    DeviceNotFoundError,
    ServerStartupError,
    ExecutableNotFoundError,
    PlatformServiceUninitializedError,
    AgentInvalidApiKeyError,
    MobileUseError,
)

async def main():
    profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
    config = Builders.AgentConfig.with_default_profile(profile).build()
    agent = Agent(config=config)
    
    try:
        # Initialize with error handling
        if not agent.init():
            print("Failed to initialize agent")
            return
        
        # Run task
        result = await agent.run_task(
            goal="Check notifications",
            name="notification_check"
        )
        
        print(f"Result: {result}")
        
    except ExecutableNotFoundError as e:
        print(f"Error: Missing required executable: {e}")
        print("Install required tools (adb for Android, idb for iOS)")
        
    except DeviceNotFoundError:
        print("Error: No device found. Please connect a device.")
        
    except ServerStartupError:
        print("Error: Failed to start servers. Try cleaning up first.")
        print("Run: agent.clean(force=True)")
        
    except AgentNotInitializedError:
        print("Error: Agent not initialized properly.")
        
    except PlatformServiceUninitializedError:
        print("Error: Platform service not initialized.")
        print("Set MINITAP_API_KEY in your .env file")
        
    except AgentInvalidApiKeyError:
        print("Error: Invalid Minitap API key.")
        print("Get a valid key from https://platform.mobile-use.ai/api-keys")
        
    except MobileUseError as e:
        print(f"SDK error: {e}")
        
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        raise
        
    finally:
        agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

## Troubleshooting

Common issues and solutions

## Agent SDK

Agent class reference
