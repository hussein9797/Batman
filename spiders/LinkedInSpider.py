import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from scrapy.http import Request
from linkedin_scraper.items import PostItem
import time

class LinkedInSpider(scrapy.Spider):
    name = "linkedin_spider"
    start_urls = [
        'https://www.linkedin.com/company/google/posts/',
        # Add more company profile URLs here
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize Selenium WebDriver (Headless Chrome)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=chrome_options)

    def start_requests(self):
        # First, login using Selenium
        self.login()

        # Now proceed with normal Scrapy requests using session cookies
        for url in self.start_urls:
            yield Request(url=url, cookies=self.cookies, callback=self.parse)

    def login(self):
        # Open LinkedIn login page with Selenium
        self.driver.get('https://www.linkedin.com/login')

        # Enter the username and password
        username = self.driver.find_element(By.ID, 'username')
        password = self.driver.find_element(By.ID, 'password')

        username.send_keys('xbn8g02c@minimail.gq')  # Replace with your LinkedIn email
        password.send_keys('hussain@123')  # Replace with your LinkedIn password
        password.send_keys(Keys.RETURN)

        # Wait for login to complete
        time.sleep(5)  # Adjust this depending on your network speed or add explicit waits

        # Check if login was successful
        if "feed" not in self.driver.current_url:
            self.logger.error("Login failed")
            self.driver.quit()
            return

        # Extract cookies from Selenium
        self.cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
        self.logger.info("Login successful, cookies retrieved")

    def parse(self, response):
        # Use Selenium to visit the page
        self.driver.get(response.url)
        time.sleep(5)  # Wait for the page to load (adjust based on network speed)

        # Find post containers
        posts = self.driver.find_elements(By.XPATH, '//*[@id="fie-impression-container"]/div[2]')
        print(posts)
        if not posts:
            self.logger.warning("No posts found on the page. Check your CSS selectors.")
            return

        for post in posts:
            post_item = PostItem()

            # Click "see more" if available
            try:
                see_more_button = post.find_element(By.CSS_SELECTOR, 'button.feed-shared-inline-show-more-text__see-more-less-toggle')
                see_more_button.click()
                time.sleep(1)  # Let the full content load
            except:
                pass  # No "see more" button

            # Extract the post content
            content = post.find_element(By.XPATH, '//*[@id="fie-impression-container"]/div[2]/div/div').text
            post_item['content'] = content.strip() if content else 'No content'

            # Extract post URL (if available)
           # post_item['post_url'] = post.find_element(By.CSS_SELECTOR, 'a.app-aware-link').get_attribute('href')

            # Extract post owner (company name)
            owner_name = self.driver.find_element(By.XPATH, '//h1[contains(@class, "org-top-card-summary__title")]').text

            #post_item['owner_name'] = self.driver.find_element(By.XPATH, '//*[@id="ember32"]/div[2]/div[2]/div[1]/div[1]').text.strip()
            post_item['owner_name'] = owner_name.strip() if owner_name else 'No owner name'


            # Extract post creation date (if available)
            # created_at = post.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime')
            # post_item['created_at'] = created_at if created_at else 'No date'

            # Yield the post item to the pipeline
            yield post_item

        # Handle pagination if necessary
        # next_page = self.driver.find_element(By.CSS_SELECTOR, 'a.pagination__button--next')
        # if next_page:
        #     next_page_url = next_page.get_attribute('href')
        #     self.logger.info(f"Found next page: {next_page_url}")
        #     yield scrapy.Request(next_page_url, cookies=self.cookies, callback=self.parse)
        # else:
        #     self.logger.info("No more pages to crawl")

    def closed(self, reason):
        # Close Selenium driver when done
        self.driver.quit()
