import asyncio
from playwright.async_api import async_playwright, Page, Locator

BASE_URL = "https://www.fwd.com.hk"

async def locate_show_more_button(page: Page) -> Locator:
    """
    Locates the 'Show more' button/div on the page.
    """
    return page.locator("div").get_by_text("Show more", exact=False)

async def expand_list(page: Page):
    """
    Repeatedly clicks the 'Show more' button until it's no longer visible or a limit is reached.
    """
    locator = await locate_show_more_button(page)
    count = await locator.count()
    
    max_clicks = 20
    click_count = 0
    
    while count > 0 and click_count < max_clicks:
        locator = await locate_show_more_button(page)
        if await locator.count() == 0:
            break

        button = locator.first
        if await button.is_visible():
            try:
                print(f"Clicking 'Show more' (Attempt {click_count + 1})...")
                await button.scroll_into_view_if_needed()
                await button.click(force=True, timeout=5000) 
                await page.wait_for_timeout(3000) # Wait for content to load
                click_count += 1
            except Exception as e:
                print(f"Failed to click button: {e}")
                break
        else:
            break
        
        locator = await locate_show_more_button(page)
        count = await locator.count()

async def extract_product_titles(page: Page):
    """
    Finds all product containers in 'product-list' and prints their titles.
    """
    print("\nExtracting product titles...")
    
    await page.wait_for_selector("#product-list")
    
    # Locate all containers with id starting with 'product-card-' inside #product-list
    containers = page.locator("#product-list div[id^='product-card-']") 
    count = await containers.count()

    for i in range(count):
        yield containers.nth(i) # generator

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(f"{BASE_URL}/en/products/", wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(1000)

            await expand_list(page)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
