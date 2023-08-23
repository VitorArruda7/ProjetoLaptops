import asyncio
import json
from playwright.async_api import async_playwright

class NotebookScraper:
    def __init__(self):
        self.notebooks = []

    async def scrape_notebooks(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            await page.goto("https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops")

            await page.wait_for_load_state('networkidle')
            await page.wait_for_selector(".thumbnail")

            products = await page.query_selector_all(".thumbnail")
            for product in products:
                title_element = await product.query_selector("a.title")
                description_element = await product.query_selector("p.description")
                price_element = await product.query_selector("h4.price")

                description = await description_element.inner_text() if description_element else "N/A"
                price = await price_element.inner_text() if price_element else "N/A"

                product_link = await title_element.get_attribute("href")
                product_data = await self.get_product_data(browser, product_link)
                title = product_data["title"]
                review_count = product_data["review_count"]
                star_count = product_data["star_count"]
                hdd_options = product_data["hdd_options"]

                notebook = {
                    "Title": title,
                    "Description": description,
                    "Price": price,
                    "Reviews": review_count,
                    "Stars": star_count,
                    "HD Options": hdd_options
                }
                self.notebooks.append(notebook)

            await browser.close()

    async def get_product_data(self, browser, product_link):
        page = await browser.new_page()
        base_url = "https://webscraper.io"
        product_url = f"{base_url}{product_link}"
        await page.goto(product_url)

        await page.wait_for_load_state('networkidle')

        title_element = await page.query_selector(".caption h4:nth-child(2)")
        title = await title_element.inner_text() if title_element else "N/A"

        review_count_element = await page.query_selector(".ratings")
        review_count = await review_count_element.inner_text() if review_count_element else "N/A"

        star_count_elements = await page.query_selector_all(".ratings .ws-icon.ws-icon-star")
        star_count = len(star_count_elements)

        hdd_options_elements = await page.query_selector_all(".swatches button.swatch")
        hdd_options = []
        for option_element in hdd_options_elements:
            hdd_option = await option_element.inner_text()

            await option_element.click()
            await page.wait_for_selector(".caption .pull-right.price")

            price_element = await page.query_selector(".caption .pull-right.price")
            price = await price_element.inner_text() if price_element else "N/A"

            hdd_options.append({
                "HD": hdd_option,
                "Price": price
            })
        await page.close()

        product_data = {
            "title": title,
            "review_count": review_count,
            "star_count": star_count,
            "hdd_options": hdd_options
        }

        return product_data

class run_format:
    def run(self):
        notebook_scraper = NotebookScraper()
        asyncio.run(notebook_scraper.scrape_notebooks())

        notebooks_data = notebook_scraper.notebooks

        for notebook in notebooks_data:
            notebook["Price"] = float(notebook["Price"].replace("$", "").replace(",", ""))
            notebook["Reviews"] = float(notebook["Reviews"].replace(" reviews", ""))
            for option in notebook["HD Options"]:
                option["Price"] = float(option["Price"].replace("$", "").replace(",", ""))

        with open("notebooks_data.json", "w") as json_file:
            json.dump(notebooks_data, json_file, indent=4)

        print(json.dumps(notebooks_data, indent=4))

if __name__ == "__main__":
    run_format().run()