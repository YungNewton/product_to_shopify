import os
import time
import tempfile
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc


class ProductScraper:
    def __init__(self, base_url, headless=True):
        self.base_url = base_url  # The URL to start scraping from
        self.headless = headless  # Whether to run Chrome in headless mode
        self.driver = self.init_driver()
        self.product_links = set()  # Store unique product links
        self.products = []  # Store all scraped product details
    
    def init_driver(self):
        """
        Initialize the WebDriver with the necessary options.
        """
        options = uc.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--disable-webrtc")
        options.add_argument("--disable-media-stream")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1280,720")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        driver = uc.Chrome(options=options)
        return driver

    def escape_xpath_string(self, s):
        if "'" in s and '"' in s:
            return "concat(" + ", ".join(f"'{part}'" for part in s.split("'")) + ")"
        if "'" in s:
            return f'"{s}"'
        return f"'{s}'"

    def scrape_product_links(self):
        """
        Scrape product links from all pages of the Shopify collection.
        """
        try:
            next_page_url = self.base_url
            
            while next_page_url:
                self.driver.get(next_page_url)
                print(f"Navigated to next page")
                time.sleep(2)  # Anti-scraping delay
                
                # Wait for the product grid to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "product-grid"))
                )
                
                # Scrape product links on the current page
                product_links = self.driver.find_elements(
                    By.XPATH, '//a[contains(@class, "full-unstyled-link")]'
                )
                for link in product_links:
                    href = link.get_attribute("href")
                    if href:
                        self.product_links.add(href)
                
                # Check for the "Next page" button
                print(f"Accumulated {len(self.product_links)} unique product links so far.")
                next_page_url = None
                # try:
                #     next_button = self.driver.find_element(
                #         By.XPATH, '//a[contains(@class, "pagination__item--prev")]'
                #     )
                #     next_page_url = next_button.get_attribute("href")
                # except NoSuchElementException:
                #     print("No more pages found.")
                #     next_page_url = None
        
        except TimeoutException:
            print("Failed to load product grid in time.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def scrape_product_details(self, product_url):
        """
        Scrape details for a single product.
        """
        try:
            self.driver.get(product_url)
            time.sleep(2)  # Anti-scraping delay

            # Product name
            product_name_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'product__title')]/h1"))
            )
            product_name = product_name_element.text

            # Product description
            product_description_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '(//div[contains(@class, "accordion__content rte")]/p/span[contains(@class, "metafield-multi_line_text_field")])[1]')
                )
            )
            product_description = product_description_element.get_attribute('innerHTML').strip()

            # Current and former prices
            current_price = self.driver.find_element(
                By.XPATH, '//span[contains(@class, "price-item--sale")]'
            ).text
            former_price = self.driver.find_element(
                By.XPATH, '//s[contains(@class, "price-item--regular")]'
            ).text

            # Sizes and availability
            sizes = []
            size_elements = self.driver.find_elements(
                By.XPATH, '//fieldset[contains(@class, "js product-form__input")]//input'
            )
            for size_element in size_elements:
                size_name = size_element.get_attribute("value")
                is_available = "checked" in size_element.get_attribute("outerHTML")
                sizes.append({"size": size_name, "in_stock": is_available})
            
            # Images
            image_elements = self.driver.find_elements(
                By.XPATH, '//ul[contains(@id, "Slider-Thumbnails")]//img'
            )
            image_urls = [img.get_attribute("src") for img in image_elements]
            image_paths = self.save_images(image_urls)

            # Store product details
            self.products.append({
                "name": product_name,
                "description": product_description,
                "current_price": current_price,
                "former_price": former_price,
                "sizes": sizes,
                "images": image_paths
            })

            print(self.products)

        except Exception as e:
            print(f"An error occurred while scraping {product_url}: {e}")

    def save_images(self, image_urls):
        """
        Save images from the given URLs to a temporary directory.
        """
        temp_dir = tempfile.mkdtemp()
        image_paths = []
        for idx, image_url in enumerate(image_urls, 1):
            try:
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    image_path = os.path.join(temp_dir, f"image_{idx}.jpg")
                    with open(image_path, "wb") as file:
                        file.write(response.content)
                    image_paths.append(image_path)
            except Exception as e:
                print(f"Failed to save image {image_url}: {e}")
        return image_paths

    def close(self):
        """
        Close the WebDriver instance.
        """
        if self.driver:
            self.driver.quit()
            print("WebDriver closed.")


if __name__ == "__main__":
    base_url = "https://www.flizzone.com/collections/men?filter.v.availability=1&page=1&sort_by=best-selling"
    
    # Initialize scraper
    scraper = ProductScraper(base_url=base_url, headless=True)
    
    try:
        # Step 1: Scrape all product links
        scraper.scrape_product_links()

        # Step 2: Scrape details for each product
        for product_link in scraper.product_links:
            scraper.scrape_product_details(product_link)

    finally:
        # Cleanup
        scraper.close()
