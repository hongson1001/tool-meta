"""Entry point khi chạy tool (gồm cả file .exe sau khi build PyInstaller)."""
import subprocess
import sys
import webbrowser
from pathlib import Path


def main() -> None:
    ui_path = Path(__file__).resolve().parent / "ui" / "app.py"
    webbrowser.open("http://localhost:8501")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(ui_path),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ])


if __name__ == "__main__":
    main()
