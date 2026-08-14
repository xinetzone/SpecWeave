#!/usr/bin/env python3
"""
Camera Power Controller for Automated Testing
Control smart plug power switches for camera device testing via Tuya API.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from dataclasses import dataclass
from enum import Enum

# Add Tuya API path
TUYA_SKILL_PATH = Path(__file__).parent.parent.parent / ".chaos" / "libs" / "tuya-openclaw-skills" / "tuya-smart-control" / "scripts"
sys.path.insert(0, str(TUYA_SKILL_PATH))

try:
    from tuya_api import TuyaAPI, TuyaAPIError
    TUYA_AVAILABLE = True
except ImportError:
    TUYA_AVAILABLE = False
    print(f"Warning: Tuya API not found at {TUYA_SKILL_PATH}", file=sys.stderr)


class PowerState(Enum):
    ON = "on"
    OFF = "off"
    UNKNOWN = "unknown"


@dataclass
class CameraDevice:
    device_id: str
    name: str
    switch_property: str = "switch_1"
    online: bool = False
    current_state: PowerState = PowerState.UNKNOWN


class CameraPowerController:
    """
    Controller for camera power switches via Tuya smart plugs.
    Designed for automated testing scenarios with:
    - Reliable power on/off cycling
    - State verification
    - Wait/retry mechanisms
    - Multi-device support
    - Logging and test integration
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None,
                 config_path: str | None = None):
        """
        Initialize the camera power controller.

        Args:
            api_key: Tuya API key (or set TUYA_API_KEY env var)
            base_url: Tuya API base URL (auto-detected if not provided)
            config_path: Path to JSON config file with device mappings
        """
        if not TUYA_AVAILABLE:
            raise RuntimeError(
                "Tuya API not available. Please check the tuya-openclaw-skills installation."
            )

        # Load API key
        if api_key is None:
            api_key = os.environ.get("TUYA_API_KEY")
        if not api_key:
            raise ValueError(
                "Tuya API key required. Set TUYA_API_KEY environment variable or pass api_key parameter."
            )

        self.api = TuyaAPI(api_key=api_key, base_url=base_url)
        self.devices: dict[str, CameraDevice] = {}
        self.default_wait_time: float = 2.0
        self.max_retries: int = 3
        self.retry_delay: float = 1.0

        # Load config if provided
        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str) -> None:
        """Load device configuration from JSON file."""
        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)

        for cam_config in config.get("cameras", []):
            device = CameraDevice(
                device_id=cam_config["device_id"],
                name=cam_config.get("name", cam_config["device_id"]),
                switch_property=cam_config.get("switch_property", "switch_1"),
            )
            self.devices[device.name] = device

        if "default_wait_time" in config:
            self.default_wait_time = config["default_wait_time"]
        if "max_retries" in config:
            self.max_retries = config["max_retries"]

    def save_config_template(self, config_path: str) -> None:
        """Save a configuration template file."""
        template = {
            "cameras": [
                {
                    "name": "camera-01",
                    "device_id": "your-device-id-here",
                    "switch_property": "switch_1"
                },
                {
                    "name": "camera-02",
                    "device_id": "another-device-id",
                    "switch_property": "switch"
                }
            ],
            "default_wait_time": 2.0,
            "max_retries": 3
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

    def list_all_devices(self) -> list[dict[str, Any]]:
        """List all Tuya devices available on the account."""
        result = self.api.get_all_devices()
        return result.get("devices", [])

    def discover_plugs(self) -> list[dict[str, Any]]:
        """Discover all smart plug devices (category 'cz')."""
        devices = self.list_all_devices()
        plugs = [d for d in devices if d.get("category") == "cz"]
        return plugs

    def get_device_state(self, camera_name: str) -> PowerState:
        """Get current power state of a camera device."""
        device = self._get_device(camera_name)
        try:
            detail = self.api.get_device_detail(device.device_id)
            props = detail.get("properties", {})
            is_on = props.get(device.switch_property, False)
            device.online = detail.get("online", False)
            device.current_state = PowerState.ON if is_on else PowerState.OFF
            return device.current_state
        except TuyaAPIError as e:
            device.current_state = PowerState.UNKNOWN
            raise

    def _get_device(self, camera_name: str) -> CameraDevice:
        """Get device by name, or raise error."""
        if camera_name not in self.devices:
            raise KeyError(
                f"Camera '{camera_name}' not configured. "
                f"Available: {list(self.devices.keys())}"
            )
        return self.devices[camera_name]

    def power_on(self, camera_name: str, wait: bool = True,
                 wait_time: float | None = None) -> bool:
        """
        Power on a camera device.

        Args:
            camera_name: Name of the camera in config
            wait: Whether to wait and verify state
            wait_time: Time to wait for state change (seconds)

        Returns:
            True if successful, False otherwise
        """
        device = self._get_device(camera_name)
        wait_time = wait_time or self.default_wait_time

        for attempt in range(self.max_retries):
            try:
                self.api.issue_properties(
                    device.device_id,
                    {device.switch_property: True}
                )
                if wait:
                    time.sleep(wait_time)
                    state = self.get_device_state(camera_name)
                    if state == PowerState.ON:
                        return True
                else:
                    return True
            except TuyaAPIError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
        return False

    def power_off(self, camera_name: str, wait: bool = True,
                  wait_time: float | None = None) -> bool:
        """
        Power off a camera device.

        Args:
            camera_name: Name of the camera in config
            wait: Whether to wait and verify state
            wait_time: Time to wait for state change (seconds)

        Returns:
            True if successful, False otherwise
        """
        device = self._get_device(camera_name)
        wait_time = wait_time or self.default_wait_time

        for attempt in range(self.max_retries):
            try:
                self.api.issue_properties(
                    device.device_id,
                    {device.switch_property: False}
                )
                if wait:
                    time.sleep(wait_time)
                    state = self.get_device_state(camera_name)
                    if state == PowerState.OFF:
                        return True
                else:
                    return True
            except TuyaAPIError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
        return False

    def power_cycle(self, camera_name: str, off_time: float = 5.0,
                    on_wait_time: float | None = None) -> bool:
        """
        Power cycle a camera (off → wait → on).
        Useful for testing cold boot scenarios.

        Args:
            camera_name: Name of the camera in config
            off_time: Time to wait between off and on (seconds)
            on_wait_time: Time to wait after power on for boot

        Returns:
            True if successful
        """
        self.power_off(camera_name, wait=True)
        time.sleep(off_time)
        return self.power_on(camera_name, wait=True, wait_time=on_wait_time)

    def power_on_all(self, wait: bool = True) -> dict[str, bool]:
        """Power on all configured cameras."""
        results = {}
        for name in self.devices:
            try:
                results[name] = self.power_on(name, wait=wait)
            except Exception as e:
                results[name] = False
                print(f"Error powering on {name}: {e}", file=sys.stderr)
        return results

    def power_off_all(self, wait: bool = True) -> dict[str, bool]:
        """Power off all configured cameras."""
        results = {}
        for name in self.devices:
            try:
                results[name] = self.power_off(name, wait=wait)
            except Exception as e:
                results[name] = False
                print(f"Error powering off {name}: {e}", file=sys.stderr)
        return results

    def get_all_states(self) -> dict[str, PowerState]:
        """Get power states of all configured cameras."""
        states = {}
        for name in self.devices:
            try:
                states[name] = self.get_device_state(name)
            except Exception as e:
                states[name] = PowerState.UNKNOWN
                print(f"Error getting state for {name}: {e}", file=sys.stderr)
        return states

    def wait_for_state(self, camera_name: str, expected_state: PowerState,
                       timeout: float = 30.0, poll_interval: float = 1.0) -> bool:
        """
        Wait for a camera to reach expected power state.

        Args:
            camera_name: Name of the camera
            expected_state: Desired power state
            timeout: Maximum time to wait (seconds)
            poll_interval: Time between state checks (seconds)

        Returns:
            True if state reached within timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                current = self.get_device_state(camera_name)
                if current == expected_state:
                    return True
            except Exception:
                pass
            time.sleep(poll_interval)
        return False

    def add_camera(self, name: str, device_id: str,
                   switch_property: str = "switch_1") -> None:
        """Add a camera device programmatically."""
        self.devices[name] = CameraDevice(
            device_id=device_id,
            name=name,
            switch_property=switch_property,
        )


def cli_main():
    """Command-line interface for camera power control."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Camera Power Controller for Automated Testing"
    )
    parser.add_argument("--config", "-c", help="Path to config JSON file")
    parser.add_argument("--api-key", help="Tuya API key (or set TUYA_API_KEY)")
    parser.add_argument("--list-devices", "-l", action="store_true",
                        help="List all available smart plug devices")
    parser.add_argument("--discover", action="store_true",
                        help="Discover smart plug devices")
    parser.add_argument("--init-config", metavar="PATH",
                        help="Generate a config template file")
    parser.add_argument("--on", metavar="CAMERA", help="Power on a camera")
    parser.add_argument("--off", metavar="CAMERA", help="Power off a camera")
    parser.add_argument("--cycle", metavar="CAMERA", help="Power cycle a camera")
    parser.add_argument("--status", metavar="CAMERA", nargs="?", const="__all__",
                        help="Check camera status (all if no name given)")
    parser.add_argument("--on-all", action="store_true", help="Power on all cameras")
    parser.add_argument("--off-all", action="store_true", help="Power off all cameras")
    parser.add_argument("--wait-time", type=float, default=2.0,
                        help="Wait time after power operations (seconds)")
    parser.add_argument("--no-wait", action="store_true",
                        help="Don't wait for state verification")

    args = parser.parse_args()

    # Handle init-config first (no API needed)
    if args.init_config:
        controller = CameraPowerController.__new__(CameraPowerController)
        controller.devices = {}
        controller.save_config_template(args.init_config)
        print(f"Config template saved to: {args.init_config}")
        return

    # Initialize controller
    try:
        controller = CameraPowerController(
            api_key=args.api_key,
            config_path=args.config
        )
        controller.default_wait_time = args.wait_time
    except Exception as e:
        print(f"Initialization error: {e}", file=sys.stderr)
        sys.exit(1)

    wait = not args.no_wait

    try:
        if args.list_devices:
            devices = controller.list_all_devices()
            print(json.dumps(devices, indent=2, ensure_ascii=False))

        elif args.discover:
            plugs = controller.discover_plugs()
            print(f"Found {len(plugs)} smart plug(s):")
            for plug in plugs:
                print(f"  - {plug.get('name', 'Unknown')} (ID: {plug.get('id')})")
                print(f"    Online: {plug.get('online', False)}")
                if plug.get('id'):
                    try:
                        detail = controller.api.get_device_detail(plug['id'])
                        model = controller.api.get_device_model(plug['id'])
                        props = detail.get('properties', {})
                        print(f"    Properties: {list(props.keys())}")
                    except Exception:
                        pass
                print()

        elif args.on:
            success = controller.power_on(args.on, wait=wait)
            print(f"Power on '{args.on}': {'SUCCESS' if success else 'FAILED'}")

        elif args.off:
            success = controller.power_off(args.off, wait=wait)
            print(f"Power off '{args.off}': {'SUCCESS' if success else 'FAILED'}")

        elif args.cycle:
            success = controller.power_cycle(args.cycle)
            print(f"Power cycle '{args.cycle}': {'SUCCESS' if success else 'FAILED'}")

        elif args.status is not None:
            if args.status == "__all__":
                states = controller.get_all_states()
                for name, state in states.items():
                    print(f"{name}: {state.value}")
            else:
                state = controller.get_device_state(args.status)
                print(f"{args.status}: {state.value}")

        elif args.on_all:
            results = controller.power_on_all(wait=wait)
            for name, success in results.items():
                print(f"Power on '{name}': {'SUCCESS' if success else 'FAILED'}")

        elif args.off_all:
            results = controller.power_off_all(wait=wait)
            for name, success in results.items():
                print(f"Power off '{name}': {'SUCCESS' if success else 'FAILED'}")

        else:
            parser.print_help()

    except TuyaAPIError as e:
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
