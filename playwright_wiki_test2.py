import random

from playwright.sync_api import sync_playwright
import time
import argparse
import random


def wiki(HAR_name):
    with sync_playwright() as p:
        # Channel can be "chrome", "msedge", "chrome-beta", "msedge-beta" or "msedge-dev".
        browser = p.chromium.launch(channel="chrome",
                                    headless=False,
                                    args=['--disable-blink-features=AutomationControlled']
        )

        context = browser.new_context(
            user_agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
            java_script_enabled=True,
            viewport={"width": 1280, "height": 720},
            device_scale_factor= 1,
            record_har_path=HAR_name
        )
        page = context.new_page()
        cdp = context.new_cdp_session(page)
        cdp.send("Network.enable")
        cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})

        page.goto("https://www.wikipedia.org/",wait_until="networkidle")
        for i in range(1):
            page.wait_for_timeout(1000)
            page.get_by_role("link", name="English").click()
            page.wait_for_timeout(1000)
            page.go_back()
            page.wait_for_timeout(1000)
            page.get_by_role("link", name="日本語").click()
            page.wait_for_timeout(1000)
            page.go_back()
            page.wait_for_timeout(1000)
            page.get_by_role("link", name="Deutsch").click()
            page.wait_for_timeout(1000)
            page.go_back()

        for i in range(2):
            page.goto("https://en.wikipedia.org/wiki/Artificial_intelligence", wait_until="networkidle")
            link = page.get_by_role("link", name="computational systems").first
            page.wait_for_timeout(4000 + (random.gauss(0, 1000)))
            link.click()
            link = page.get_by_role("link", name="machine").first
            page.wait_for_timeout(4000 + (random.gauss(0, 1000)))
            link.click()
            link = page.get_by_role("link", name="thermodynamic system").first
            page.wait_for_timeout(4000 + (random.gauss(0, 1000)))
            link.click()
            page.wait_for_timeout(4000 + (random.gauss(0, 1000)))


        page.close()
        context.close()
        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_name', required=True, )
    args = parser.parse_args()
    wiki(args.output_name)