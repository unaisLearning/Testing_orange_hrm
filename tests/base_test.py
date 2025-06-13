"""
Base test class for all test cases.
"""

import os
import platform
import logging
import pytest
import allure
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import subprocess

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

from config.config import Config
from utils.logger import logger

logger = logging.getLogger(__name__)


class BaseTest:
    """
    Base class for all test cases.
    Provides common setup and teardown methods.
    """

    def _get_chrome_driver_path(self):
        """
        Get the appropriate ChromeDriver path based on the environment.
        Returns the path to ChromeDriver executable.
        """
        # Always use webdriver-manager in GitHub Actions
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            logger.info("Running in GitHub Actions environment")
            return ChromeDriverManager().install()
        
        # For local Mac ARM64 environment
        if platform.system() == 'Darwin' and platform.machine() == 'arm64':
            logger.info("Running on Mac ARM64")
            
            # First try using the local chromedriver
            local_driver = os.path.abspath('./chromedriver')
            if os.path.exists(local_driver):
                try:
                    # Verify the chromedriver is executable
                    if not os.access(local_driver, os.X_OK):
                        logger.info("Making chromedriver executable")
                        os.chmod(local_driver, 0o755)
                    
                    # Test if chromedriver works
                    result = subprocess.run([local_driver, '--version'], 
                                         capture_output=True, 
                                         text=True)
                    if result.returncode == 0:
                        logger.info(f"Using local ChromeDriver: {local_driver}")
                        logger.info(f"ChromeDriver version: {result.stdout.strip()}")
                        return local_driver
                except Exception as e:
                    logger.warning(f"Local ChromeDriver test failed: {str(e)}")
            
            # If local driver not available or not working, try webdriver-manager with CHROMIUM
            try:
                logger.info("Attempting to use webdriver-manager with CHROMIUM")
                driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
                logger.info(f"Using webdriver-manager ChromeDriver: {driver_path}")
                return driver_path
            except Exception as e:
                logger.error(f"Failed to setup ChromeDriver: {str(e)}")
                raise
        
        # Default case for other environments
        logger.info("Using default ChromeDriver setup")
        return ChromeDriverManager().install()

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
            # Use appropriate headless mode based on environment
            if os.environ.get('GITHUB_ACTIONS') == 'true':
                chrome_options.add_argument('--headless')  # Use old headless mode for GitHub Actions
            else:
                chrome_options.add_argument('--headless=new')  # Use new headless mode for local
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--window-size=1920,1080')
            # Use a unique user data dir for each test run
            chrome_options.add_argument(f'--user-data-dir={tempfile.mkdtemp()}')

            # Get appropriate ChromeDriver path
            driver_path = self._get_chrome_driver_path()
            logger.info(f"Using ChromeDriver at: {driver_path}")
            
            # Initialize WebDriver
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

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
