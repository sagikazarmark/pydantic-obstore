#!/usr/bin/env python3
"""
Simple test runner script for pydantic-obstore.

This script runs the comprehensive test suite that verifies the pydantic models
match their counterpart types in the obstore library without requiring async operations.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the test suite."""
    # Get the project root directory
    project_root = Path(__file__).parent

    # Change to project directory
    import os

    os.chdir(project_root)

    print("🧪 Running pydantic-obstore test suite...")
    print("=" * 60)

    # Run pytest with verbose output
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "--color=yes"]

    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("✅ All tests passed! The pydantic models correctly match obstore types.")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"❌ Tests failed with exit code {e.returncode}")
        print("Some pydantic models may not match their obstore counterparts.")
        return e.returncode
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("⚠️  Test run interrupted by user")
        return 130


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
