#!/usr/bin/env python3
"""
Test runner script for portfolio-insight project.

This script runs all tests in the project and provides a unified interface
for testing both locally and in CI environments.
"""

import sys
import subprocess
import os


def run_command(command, description):
    """Run a command and handle its output."""
    print(f"\n=== {description} ===")
    try:
        # Get the directory where this script is located (project root)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=script_dir,
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Run all tests."""
    print("🧪 Portfolio Insight Test Runner")
    print("=" * 50)

    tests_passed = 0
    tests_failed = 0

    # List of test commands
    test_commands = [
        ("python tests/test_allocation.py", "Allocation Tests"),
        ("python tests/test_allocation_service.py", "Allocation Service Tests"),
    ]

    # Run each test
    for command, description in test_commands:
        if run_command(command, description):
            tests_passed += 1
            print(f"✅ {description} PASSED")
        else:
            tests_failed += 1
            print(f"❌ {description} FAILED")

    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results Summary:")
    print(f"   ✅ Passed: {tests_passed}")
    print(f"   ❌ Failed: {tests_failed}")
    print(f"   📋 Total:  {tests_passed + tests_failed}")

    if tests_failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n💥 {tests_failed} test(s) failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
