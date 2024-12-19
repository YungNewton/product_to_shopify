import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class ProductScraper:
    def __init__(self, base_url, headless=True):
        self.base_url = base_url  # The URL to start scraping from
        self.headless = headless  # Whether to run Chrome in headless mode
        self.driver = self.init_driver()
        self.product_links = set()  # Store unique product links
    
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
        options.add_argument("--disable-web-security")  # Disable CORS restrictions
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass detection
        options.add_argument("--disable-gpu")
        driver = uc.Chrome(options=options)
        return driver

    def scrape_product_links(self):
        """
        Scrape product links from all pages of the Shopify collection.
        """
        try:
            next_page_url = self.base_url  # Start with the base URL
            
            while next_page_url:
                self.driver.get(next_page_url)
                print(f"Navigated to {next_page_url}")
                
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
                
                print(f"Accumulated {len(self.product_links)} unique product links so far.")
                
                # Check for the "Next page" button and get its URL
                try:
                    next_button = self.driver.find_element(
                        By.XPATH, '//a[contains(@class, "pagination__item--prev")]'
                    )
                    next_page_url = next_button.get_attribute("href")
                except Exception:
                    print("No more pages found.")
                    next_page_url = None  # Exit the loop if there's no "Next" button
        
        except TimeoutException:
            print("Failed to load product grid in time.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def close(self):
        """
        Close the WebDriver instance.
        """
        if self.driver:
            self.driver.quit()
            print("WebDriver closed.")

if __name__ == "__main__":
    # Shopify collection URL
    base_url = "https://www.flizzone.com/collections/men?filter.v.availability=1&page=1&sort_by=best-selling"
    
    # Initialize scraper
    scraper = ProductScraper(base_url=base_url, headless=True)
    
    try:
        # Scrape product links
        scraper.scrape_product_links()

    finally:
        # Cleanup
        scraper.close()
