"""Check deployment dependencies without database credentials or model downloads."""

import subprocess
import sys


def main():
    checks = []
    if sys.platform.startswith("linux"):
        for library in (
            "libssl.so.3", "libcrypto.so.3", "libmariadb.so.3",
            "libGL.so.1", "libglib-2.0.so.0",
        ):
            checks.append((library, f"import ctypes; ctypes.CDLL({library!r})"))

    for module, distribution in (
        ("MySQLdb", "mysqlclient"), ("cv2", "opencv-python"),
        ("torch", "torch"), ("torchvision", "torchvision"),
        ("ultralytics", "ultralytics"), ("django", "Django"),
    ):
        checks.append((module, f"import {module}; from importlib.metadata import version; "
                       f"print(version({distribution!r}))"))

    failures = []
    for label, command in checks:
        print(f"Checking {label}...", flush=True)
        try:
            result = subprocess.run([sys.executable, "-c", command], timeout=120)
            if result.returncode:
                failures.append(label)
        except subprocess.TimeoutExpired:
            print(f"Timed out loading {label}.", flush=True)
            failures.append(label)

    if failures:
        print("Dependency checks failed: " + ", ".join(failures), file=sys.stderr)
        print("Check nixLibs in nixpacks.toml for missing shared libraries.", file=sys.stderr)
        return 1
    print("All deployment dependency checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
