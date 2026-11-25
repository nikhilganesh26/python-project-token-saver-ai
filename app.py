import subprocess
import sys
import time
import webbrowser
from pathlib import Path

PORT = 8501
HERE = Path(__file__).parent

def main():
    windows = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    cmd = [sys.executable, "-m", "streamlit", "run", str(HERE / "frontend.py"),
           "--server.port", str(PORT), "--server.headless", "true"]
    server = subprocess.Popen(cmd, cwd=HERE)

    try:
        time.sleep(4)  # give the server a moment to start
        for _ in range(windows):
            webbrowser.open_new_tab(f"http://localhost:{PORT}")
            time.sleep(0.5)
        print(f"TokenSaver AI running at http://localhost:{PORT}")
        print("Open more tabs at that address for more users. Press Ctrl+C here to stop.")
        server.wait()
    except KeyboardInterrupt:
        pass
    finally:
        server.terminate()

if __name__ == "__main__":
    main()