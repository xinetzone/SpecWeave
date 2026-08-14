#!/usr/bin/env python3
"""
Automated Testing Examples for Camera Power Controller

This file demonstrates how to use the camera power controller
in automated test scenarios including pytest integration.
"""

import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from camera_power import CameraPowerController, PowerState


def example_basic_usage():
    """Example 1: Basic power on/off operations"""
    print("=" * 60)
    print("Example 1: Basic Power Control")
    print("=" * 60)

    # Initialize controller (config file or env var TUYA_API_KEY)
    controller = CameraPowerController(
        config_path=str(Path(__file__).parent / "config.json")
    )

    # Power on camera
    print("\n[1] Powering on camera-01...")
    success = controller.power_on("camera-01")
    print(f"    Result: {'SUCCESS' if success else 'FAILED'}")

    # Check status
    state = controller.get_device_state("camera-01")
    print(f"    Current state: {state.value}")

    # Wait a bit
    time.sleep(3)

    # Power off camera
    print("\n[2] Powering off camera-01...")
    success = controller.power_off("camera-01")
    print(f"    Result: {'SUCCESS' if success else 'FAILED'}")

    state = controller.get_device_state("camera-01")
    print(f"    Current state: {state.value}")


def example_power_cycle_test():
    """Example 2: Cold boot / power cycle testing"""
    print("\n" + "=" * 60)
    print("Example 2: Power Cycle Test (Cold Boot)")
    print("=" * 60)

    controller = CameraPowerController(
        config_path=str(Path(__file__).parent / "config.json")
    )

    # Power cycle: off -> wait 5s -> on
    print("\n[1] Executing power cycle (5s off time)...")
    success = controller.power_cycle("camera-01", off_time=5.0)
    print(f"    Power cycle result: {'SUCCESS' if success else 'FAILED'}")

    # Wait for camera to fully boot
    print("\n[2] Waiting 15s for camera to boot...")
    time.sleep(15)

    # Verify camera is accessible (you would add your camera check here)
    state = controller.get_device_state("camera-01")
    print(f"    Power state: {state.value}")
    print("    [Note] Add your camera connectivity check here")


def example_multi_camera_test():
    """Example 3: Multi-camera batch testing"""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Camera Batch Testing")
    print("=" * 60)

    controller = CameraPowerController(
        config_path=str(Path(__file__).parent / "config.json")
    )

    # Show current states
    print("\n[1] Current states of all cameras:")
    states = controller.get_all_states()
    for name, state in states.items():
        print(f"    {name}: {state.value}")

    # Power off all cameras
    print("\n[2] Powering off all cameras...")
    results = controller.power_off_all()
    for name, success in results.items():
        print(f"    {name}: {'OFF' if success else 'FAILED'}")

    time.sleep(2)

    # Power on all cameras one by one with stagger
    print("\n[3] Powering on cameras sequentially (3s stagger)...")
    for name in controller.devices:
        print(f"    Powering on {name}...")
        controller.power_on(name)
        time.sleep(3)

    # Final states
    print("\n[4] Final states:")
    states = controller.get_all_states()
    for name, state in states.items():
        print(f"    {name}: {state.value}")


def example_reliability_test():
    """Example 4: Reliability/Stress test - multiple power cycles"""
    print("\n" + "=" * 60)
    print("Example 4: Reliability Stress Test (10 cycles)")
    print("=" * 60)

    controller = CameraPowerController(
        config_path=str(Path(__file__).parent / "config.json")
    )

    num_cycles = 10
    success_count = 0
    failures = []

    for i in range(num_cycles):
        print(f"\n[Cycle {i+1}/{num_cycles}]")

        # Off
        if not controller.power_off("camera-01", wait_time=2.0):
            failures.append(f"Cycle {i+1}: power off failed")
            continue

        time.sleep(3)

        # On
        if not controller.power_on("camera-01", wait_time=2.0):
            failures.append(f"Cycle {i+1}: power on failed")
            continue

        success_count += 1
        print(f"    Success")
        time.sleep(3)

    print(f"\nResults: {success_count}/{num_cycles} successful cycles")
    if failures:
        print("Failures:")
        for f in failures:
            print(f"  - {f}")


def example_wait_for_boot():
    """Example 5: Wait for camera to boot with timeout"""
    print("\n" + "=" * 60)
    print("Example 5: Wait for Camera Boot with Timeout")
    print("=" * 60)

    controller = CameraPowerController(
        config_path=str(Path(__file__).parent / "config.json")
    )

    # Power cycle
    print("\n[1] Power cycling camera...")
    controller.power_off("camera-01")
    time.sleep(3)
    controller.power_on("camera-01", wait=False)

    # Wait for power state to be ON (with timeout)
    print("\n[2] Waiting for power state to be ON (timeout: 30s)...")
    power_ok = controller.wait_for_state(
        "camera-01",
        expected_state=PowerState.ON,
        timeout=30.0,
        poll_interval=1.0
    )
    print(f"    Power state confirmed: {power_ok}")

    # Here you would add your own wait logic for camera to be fully ready
    # e.g., ping camera IP, check RTSP stream, etc.
    print("\n[3] Waiting 20s for camera to finish booting...")
    boot_start = time.time()
    time.sleep(20)  # Replace with actual camera ready check
    boot_time = time.time() - boot_start
    print(f"    Waited {boot_time:.1f}s for boot")
    print("    [Note] Replace sleep with actual camera readiness check")


# ============================================================================
# Pytest Integration Examples
# ============================================================================

def pytest_example_setup_teardown():
    """
    Example: Use as pytest fixture for test setup/teardown.

    In conftest.py:
    ```python
    import pytest
    from pathlib import Path
    from camera_power import CameraPowerController

    @pytest.fixture(scope="session")
    def camera():
        config_path = Path(__file__).parent / "config.json"
        controller = CameraPowerController(config_path=str(config_path))

        # Setup: Power on camera before tests
        controller.power_on("camera-01")
        time.sleep(20)  # Wait for boot

        yield controller

        # Teardown: Power off after tests
        controller.power_off("camera-01")
    ```
    """
    pass


def pytest_example_test_function():
    """
    Example: Test function using camera power control.

    ```python
    def test_camera_cold_boot(camera):
        # Test camera behavior after cold boot
        camera.power_off("camera-01")
        time.sleep(5)
        camera.power_on("camera-01")
        camera.wait_for_state("camera-01", PowerState.ON, timeout=30)
        time.sleep(15)  # Wait for boot

        # Your test assertions here
        # assert camera_stream_is_accessible()
        # assert video_quality_is_good()
    ```
    """
    pass


if __name__ == "__main__":
    print("Camera Power Controller - Automated Test Examples")
    print("Note: Configure your config.json with real device IDs first!")
    print()

    # Uncomment examples to run
    # example_basic_usage()
    # example_power_cycle_test()
    # example_multi_camera_test()
    # example_reliability_test()
    # example_wait_for_boot()

    print("\nEdit this file to uncomment and run examples.")
    print("\nQuick start commands:")
    print("  # Discover your smart plugs:")
    print(f"  python {Path(__file__).name} --discover")
    print("\n  # Generate config template:")
    print(f"  python {Path(__file__).parent / 'camera_power.py'} --init-config config.json")
