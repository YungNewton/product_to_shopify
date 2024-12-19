import os
import time
import requests
from io import BytesIO
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
from webdriver_manager.chrome import ChromeDriverManager
import threading

class ProductScraper:
    def __init__(self, base_url, headless=True):
        self.base_url = base_url  # The URL to start scraping from
        self.headless = headless  # Whether to run Chrome in headless mode
        self.driver = self.init_driver()
    
    def init_driver(self):
        """
        Initialize the WebDriver with the desired options.
        """
        options = Options()
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

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.set_window_size(1280, 720)
        return driver
    
    def scrape_products(self):
        """
        Main method to scrape products from the website.
        """
        try:
            self.driver.get(self.base_url)
            print(f"Navigated to {self.base_url}")
            
            # Implement scraping logic here
            # For example, find all product elements on the page
            products = self.driver.find_elements(By.XPATH, '//div[contains(@class, "product-grid-item")]')
            print(f"Found {len(products)} products on the page.")
            
            for idx, product in enumerate(products, 1):
                try:
                    # Extract product details
                    product_name = product.find_element(By.XPATH, './/div[@class="product-card__title"]').text
                    product_price = product.find_element(By.XPATH, './/div[@class="product-card__price"]').text
                    product_link = product.find_element(By.XPATH, './/a').get_attribute('href')
                    
                    # Print or process the product details
                    print(f"Product {idx}:")
                    print(f"Name: {product_name}")
                    print(f"Price: {product_price}")
                    print(f"Link: {product_link}")
                    print("-" * 40)
                    
                    # Additional logic to upload to Shopify can be implemented here
                except Exception as e:
                    print(f"Error processing product {idx}: {e}")
                    
            # Pagination logic can be added here to navigate through pages
            
        except Exception as e:
            print(f"An error occurred while scraping: {e}")
    
    def close(self):
        """
        Clean up the WebDriver instance.
        """
        try:
            if self.driver:
                self.driver.quit()
                print("WebDriver closed successfully.")
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    # Define the base URL to scrape
    base_url = "https://www.flizzone.com/collections/men?filter.v.availability=1&page=1&sort_by=best-selling"
    
    # Initialize the scraper
    scraper = ProductScraper(base_url=base_url, headless=True)
    
    try:
        # Run the scraping logic
        scraper.scrape_products()
    finally:
        # Ensure cleanup
        scraper.close()
