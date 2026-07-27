import random
import time

from playwright.sync_api import sync_playwright, TimeoutError


def yot(HAR_name):
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

        page.goto(
            "https://soundcloud.com/",
            wait_until="load",
        )
        for i in range(60):
            # Click "Reject all" cookie button if it appears
            try:
                page.locator("#onetrust-accept-btn-handler").wait_for(
                    state="visible", timeout=10000
                )
                page.locator("#onetrust-accept-btn-handler").click()
                print("Clicked 'Reject all'")
            except TimeoutError:
                print("'Reject all' button not found")

            # Click "Directory"
            page.locator('a[href="/people/directory"]').click()

            # Wait for the Directory page to load
            page.wait_for_load_state("load")
            time.sleep(2)

            # Go back to the home page
            page.go_back(wait_until="load")
            time.sleep(2)

            page.locator('a[href="/transparency-reports"]').click()

            # Wait for the Directory page to load
            page.wait_for_load_state("load")
            time.sleep(2)

            # Go back to the home page
            page.go_back(wait_until="load")
            time.sleep(2)

        page.goto(
            "https://on.soundcloud.com/rakZPRfwxJ0xotFC24",
            wait_until="load",
        )



        # Click the modal close button if it appears
        try:
            page.locator("button.modal__closeButton").wait_for(
                state="visible", timeout=10000
            )
            page.locator("button.modal__closeButton").click()
            print("Clicked close button")
        except TimeoutError:
            print("Close button not found")

        input("Press enter to continue...")

        page.close()
        context.close()
        browser.close()


if __name__ == "__main__":
    yot("ddd")