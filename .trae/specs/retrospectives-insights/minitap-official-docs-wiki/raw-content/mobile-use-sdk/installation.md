This guide covers the common setup steps for using mobile-use SDK, whether you choose the **Platform** or **Local** approach.

## Prerequisites

Before installing the Mobile Use SDK, ensure you have the following:

Python 3.12 or higher

```shellscript
python --version
# Should be 3.12.x or higher
```

For local Android automation

For local iOS automation

- [idb (iOS Development Bridge) installation](https://fbidb.io/docs/installation/#idb-companion) - Facebook’s tool for iOS automation
- An iOS simulator

- See [Physical iOS Device Setup](https://www.minitap.ai/docs/mobile-use-sdk/physical-ios-quickstart) for detailed instructions

## Environment Setup

### 1\. Install the SDK

```shellscript
pip install minitap-mobile-use
```

We highly recommend using [UV](https://docs.astral.sh/uv/) for managing your project and packages.

### 2\. Set Up Device Access

- Android
- iOS

#### Enable Developer Options

1. Go to **Settings → About Phone**
2. Tap **Build Number** 7 times to enable Developer Options
3. In **Developer Options**, enable **USB Debugging**

#### Verify ADB Connection

```shellscript
adb devices
```

You should see your device listed.

For wireless debugging:

```shellscript
adb tcpip 5555
adb connect <device_ip>:5555
```

#### Connect your iOS device

1. Connect your iOS device to your Mac
2. Trust the computer on your iOS device when prompted
3. Install required dependencies:

```shellscript
brew install libimobiledevice
```

#### Verify connection

```shellscript
idevice_id -l
```

## Configuration

After completing the steps above, you’ll need to configure your environment based on which approach you’re using:
