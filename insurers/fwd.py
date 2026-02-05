import asyncio
import os
from urllib.parse import urljoin, urlparse

from playwright.async_api import Browser, Locator, Page, async_playwright

from download_file import download_file_from_url

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
                await page.wait_for_timeout(1500) # Wait for content to load
                click_count += 1
            except Exception as e:
                print(f"Failed to click button: {e}")
                break
        else:
            break
        
        locator = await locate_show_more_button(page)
        count = await locator.count()

async def get_product_containers(page: Page):
    """
    Yields each product container found in the 'product-list'.
    """
    await page.wait_for_selector("#product-list")
    
    # Locate all containers with id starting with 'product-card-' inside #product-list
    containers = page.locator("#product-list div[id^='product-card-']") 
    count = await containers.count()

    for i in range(count):
        yield containers.nth(i) # generator

async def handle_product_card(browser: Browser, card: Locator, keyword=None):
    """
    Extracts the product link from the card and processes the detail page.
    """
    if keyword is not None:
        productTags = card.locator('div[class^="ProductCard__TagLink"]')
        tags = await productTags.all_inner_texts()
        if tags is None or not any(keyword in tag for tag in tags):
            return

    links = card.locator("a")
    count = await links.count()
    
    for i in range(count):
        href = await links.nth(i).get_attribute("href")
        if not href:
            continue

        if '.pdf' in href:
            href = urljoin(BASE_URL, href)
            filename = href.split('/')[-1]
            os.makedirs('brochures', exist_ok=True)
            download_file_from_url(href, f"brochures/fwd/{filename}")
        else:
            # urljoin to join BASEURL with partial incomplete path (href)
            page_url = urljoin(BASE_URL, href)
            await process_product_page(browser, page_url)

async def process_product_page(browser: Browser, product_url: str):
    """
    Navigates to the product page and downloads the brochure if found.
    """
    context = await browser.new_context()
    page = await context.new_page()

    # it seems there is running JS script in online insurance paths
    tmp = product_url.replace(BASE_URL, "")
    if tmp.startswith('online-insurance'): 
        wait_mode = "load"
    else:
        wait_mode = "networkidle"

    parsed = urlparse(product_url)
    product_url_parsed = urljoin(product_url, parsed.path) # remove query string
    
    try:
        await page.goto(product_url_parsed, wait_until=wait_mode, timeout=30*1000)
        links = page.locator("a")
        count = await links.count()
        
        for i in range(count):
            link = links.nth(i)
            href = await link.get_attribute("href")
            text = await link.inner_text()
            
            if not href or not text or "brochure" not in text.lower():
                continue

            # Check if it looks like a PDF url (ignoring query params)
            # e.g. /path/to/file.pdf?v=123#title1 -> /path/to/file.pdf
            url_path = href.split("?")[0].split("#")[0]
            if url_path.lower().endswith(".pdf"):
                filename = url_path.split("/")[-1]
                
                output_dir = os.path.join(os.getcwd(), 'brochures/fwd')
                os.makedirs(output_dir, exist_ok=True)
                
                download_path = os.path.join(output_dir, filename)
                
                full_url = href
                if not href.startswith("https"):
                    if href.startswith("/"):
                        full_url = f"{BASE_URL}{href}"
                    else:
                        full_url = f"{BASE_URL}/{href}"

                # Run download synchronously in a thread
                await asyncio.to_thread(download_file_from_url, full_url, download_path)
                break

    except Exception as e:
        print(f"Error processing page: {e}")
    finally:
        await page.close()
        await context.close()
    
async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(f"{BASE_URL}/en/products/", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(2000)

            await expand_list(page)
            
            async for container in get_product_containers(page):
                await handle_product_card(browser, container, "medical")

        except Exception as e:
            print(f"Error in main run loop: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
