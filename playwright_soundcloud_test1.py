import argparse
import random
import time

from playwright.sync_api import sync_playwright, TimeoutError


def play(HAR_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            java_script_enabled=True,
            viewport={"width": 1280, "height": 720},
            device_scale_factor=1,
            record_har_path=HAR_name,
        )

        page = context.new_page()
        cdp = context.new_cdp_session(page)
        cdp.send("Network.enable")
        cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})

        page.goto(
        "https://on.soundcloud.com/rakZPRfwxJ0xotFC24",
            wait_until="load",
        )
        # Click  cookie button if it appears
        try:
            page.locator("#onetrust-accept-btn-handler").wait_for(
                state="visible", timeout=1200
            )
            page.locator("#onetrust-accept-btn-handler").click()
            print("Clicked 'Reject all'")
        except TimeoutError:
            print("'Reject all' button not found")

        st_time = time.time()
        while time.time() - st_time < 20:
            print(time.time() - st_time)
            page.wait_for_timeout(abs(random.gauss(1000, 10)))
            try:
                page.locator("button.modal__closeButton").wait_for(
                    state="visible", timeout=100
                )
                page.locator("button.modal__closeButton").click()
                print("Clicked close button")
            except TimeoutError:
                print("Close button not found")

            try:
                page.locator('a.sc-button-play.playButton.sc-button.sc-button-xxlarge[title="Play"]').wait_for(
                    state="visible", timeout=100)

                page.locator('a.sc-button-play.playButton.sc-button.sc-button-xxlarge[title="Play"]').click()
                print("Clicked play button")
            except TimeoutError:
                print("play button not found")


        page.close()
        context.close()
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_name', required=True, )
    args = parser.parse_args()
    play(args.output_name)