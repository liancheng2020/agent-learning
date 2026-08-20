import os
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    output = ROOT / "demo-video"
    output.mkdir(exist_ok=True)
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8115"], cwd=ROOT)
    try:
        time.sleep(2)
        with sync_playwright() as playwright:
            executable_path = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
            browser = playwright.chromium.launch(headless=True, executable_path=executable_path)
            context = browser.new_context(viewport={"width": 1440, "height": 900}, record_video_dir=output, record_video_size={"width": 1440, "height": 900})
            page = context.new_page()
            page.goto("http://127.0.0.1:8115")
            page.wait_for_timeout(8_000)
            page.locator("#diff").click()
            page.wait_for_timeout(8_000)
            page.locator("#run").click()
            page.wait_for_selector("#connection:text-is('Complete')")
            page.wait_for_timeout(25_000)
            page.locator("#findings").scroll_into_view_if_needed()
            page.wait_for_timeout(20_000)
            page.locator("#plan").scroll_into_view_if_needed()
            page.wait_for_timeout(20_000)
            page.locator("#sources").scroll_into_view_if_needed()
            page.wait_for_timeout(20_000)
            page.locator("header").scroll_into_view_if_needed()
            page.wait_for_timeout(15_000)
            context.close()
            browser.close()
        print(f"演示视频已输出到 {output}")
    finally:
        server.terminate()
        server.wait(timeout=5)


if __name__ == "__main__":
    main()
