"""
Base test class for all test cases.
"""

import os
import logging
import pytest
import allure
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile


from config.config import Config
from utils.logger import logger

logger = logging.getLogger(__name__)


class BaseTest:
    """
    Base class for all test cases.
    Provides common setup and teardown methods.
    """

    def setup_method(self, method=None):
        """
        Setup for each test method.

        Args:
            method: The test method being called
        """
        logger.info(f"Starting test: {self.__class__.__name__}")

        self.start_time = datetime.now()

        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in headless mode
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--window-size=1920,1080')
            # Use a unique user data dir for each test run
            chrome_options.add_argument(f'--user-data-dir={tempfile.mkdtemp()}')

            # Initialize WebDriver using Selenium Manager to handle driver binaries
            self.driver = webdriver.Chrome(options=chrome_options)

            # Set timeouts
            self.driver.implicitly_wait(Config.IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)

            # Maximize window
            self.driver.maximize_window()

            # Clear cookies
            self.driver.delete_all_cookies()

            # Log successful browser start
            logger.info("Browser started successfully")

        except Exception as e:
            logger.error(f"Failed to setup test: {str(e)}")
            raise

    def teardown_method(self, method=None):
        """
        Teardown for each test method.

        Args:
            method: The test method being called
        """
        logger.info(f"Completing test: {self.__class__.__name__}")

        try:
            # Take screenshot on failure
            if hasattr(self, '_outcome') and self._outcome.errors:
                self._take_screenshot(method.__name__)

            if hasattr(self, 'driver'):
                self.driver.quit()
                logger.info("Browser closed successfully")

        except Exception as e:
            logger.error(f"Error during teardown: {str(e)}")
            raise

    def _take_screenshot(self, test_name: str):
        """
        Take screenshot on test failure.

        Args:
            test_name: Name of the test
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"{test_name}_{timestamp}.png"
            screenshot_path = os.path.join(Config.SCREENSHOT_DIR, screenshot_name)

            os.makedirs(Config.SCREENSHOT_DIR, exist_ok=True)

            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")

            allure.attach.file(
                screenshot_path,
                name=screenshot_name,
                attachment_type=allure.attachment_type.PNG
            )

        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
