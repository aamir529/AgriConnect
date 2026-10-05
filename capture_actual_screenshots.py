import os
import sys
import time
import subprocess

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, 'presentation', 'screenshots')
    os.makedirs(out_dir, exist_ok=True)

    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    python_exe = os.path.join(base_dir, '.venv', 'Scripts', 'python.exe')

    print("Starting local Django server on port 8003...")
    server = subprocess.Popen([python_exe, 'manage.py', 'runserver', '127.0.0.1:8003', '--noreload'], cwd=base_dir)
    time.sleep(4)

    pages = [
        ("home_screenshot.png", "http://127.0.0.1:8003/"),
        ("login_screenshot.png", "http://127.0.0.1:8003/login/"),
        ("marketplace_screenshot.png", "http://127.0.0.1:8003/marketplace/"),
        ("mandi_screenshot.png", "http://127.0.0.1:8003/mandi/"),
        ("analytics_screenshot.png", "http://127.0.0.1:8003/analytics/"),
        ("vdf_portal_screenshot.png", "http://127.0.0.1:8003/facilitator/dashboard/"),
    ]

    for filename, url in pages:
        out_file = os.path.join(out_dir, filename)
        cmd = [
            edge_path,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--screenshot={out_file}",
            "--window-size=1280,850",
            url
        ]
        print(f"Capturing {url} -> {filename}...")
        try:
            subprocess.run(cmd, timeout=30, check=True)
            print(f"Captured: {out_file} ({os.path.getsize(out_file)} bytes)")
        except Exception as e:
            print(f"Failed {filename}: {e}")

    server.terminate()
    print("All captures completed.")

if __name__ == '__main__':
    main()
