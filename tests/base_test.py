"""
Base test class for all test cases.
"""

import os
import platform
import logging
import pytest
import allure
import shutil
import tempfile
import uuid
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

    def _get_unique_user_data_dir(self) -> str:
        """
        Create a unique user data directory for Chrome.
        Uses worker ID from pytest-xdist if available.
        Ensures complete isolation between test instances.
        """
        # Get worker ID from pytest-xdist if available
        worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'gw0')
        # Create a unique directory name using worker ID, process ID, and UUID
        process_id = os.getpid()
        unique_dir = f"chrome-user-data-{worker_id}-{process_id}-{uuid.uuid4()}"
        
        # Create the directory in the system temp directory
        user_data_dir = os.path.join(tempfile.gettempdir(), unique_dir)
        
        # Clean up any existing directory with the same prefix
        for existing_dir in os.listdir(tempfile.gettempdir()):
            if existing_dir.startswith(f"chrome-user-data-{worker_id}"):
                try:
                    full_path = os.path.join(tempfile.gettempdir(), existing_dir)
                    if os.path.isdir(full_path):
                        shutil.rmtree(full_path, ignore_errors=True)
                except Exception as e:
                    logger.warning(f"Failed to clean up directory {existing_dir}: {str(e)}")
        
        # Create fresh directory
        os.makedirs(user_data_dir, exist_ok=True)
        logger.info(f"Created unique user data directory: {user_data_dir}")
        return user_data_dir

    def _get_chrome_driver_path(self):
        """
        Get the appropriate ChromeDriver path based on the environment.
        Returns the path to ChromeDriver executable.
        """
        # Always use webdriver-manager in GitHub Actions
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            logger.info("Running in GitHub Actions environment")
            try:
                driver_path = ChromeDriverManager().install()
                if not os.path.basename(driver_path) == 'chromedriver':
                    driver_dir = os.path.dirname(driver_path)
                    for file in os.listdir(driver_dir):
                        if file == 'chromedriver':
                            driver_path = os.path.join(driver_dir, file)
                            break
                os.chmod(driver_path, 0o755)
                logger.info(f"Using ChromeDriver at: {driver_path}")
                return driver_path
            except Exception as e:
                logger.error(f"Failed to setup ChromeDriver in GitHub Actions: {str(e)}")
                raise
        # For local Mac ARM64 environment
        if platform.system() == 'Darwin' and platform.machine() == 'arm64':
            logger.info("Running on Mac ARM64")
            local_driver = os.path.abspath('./chromedriver')
            if os.path.exists(local_driver):
                try:
                    if not os.access(local_driver, os.X_OK):
                        logger.info("Making chromedriver executable")
                        os.chmod(local_driver, 0o755)
                    result = subprocess.run([local_driver, '--version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        logger.info(f"Using local ChromeDriver: {local_driver}")
                        logger.info(f"ChromeDriver version: {result.stdout.strip()}")
                        return local_driver
                except Exception as e:
                    logger.warning(f"Local ChromeDriver test failed: {str(e)}")
            # Fallback: Use webdriver-manager for Chrome (not Chromium)
            try:
                logger.info("Attempting to use webdriver-manager for Chrome")
                driver_path = ChromeDriverManager().install()
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
        self.user_data_dir = None

        try:
            # Configure Chrome options
            chrome_options = Options()
            
            # Add common Chrome options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Create a unique user data directory for this instance
            self.user_data_dir = self._get_unique_user_data_dir()
            chrome_options.add_argument(f'--user-data-dir={self.user_data_dir}')
            
            # Add headless mode in GitHub Actions
            if os.environ.get('GITHUB_ACTIONS') == 'true':
                chrome_options.add_argument('--headless')
            
            # Get appropriate ChromeDriver path
            driver_path = self._get_chrome_driver_path()
            service = Service(driver_path)
            
            # Initialize WebDriver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(Config.IMPLICIT_WAIT)
            self.wait = WebDriverWait(self.driver, Config.EXPLICIT_WAIT)
            
            # Navigate to the application
            self.driver.get(Config.BASE_URL)
            
        except Exception as e:
            logger.error(f"Error in setup_method: {str(e)}")
            # Clean up user data directory on failure
            if self.user_data_dir and os.path.exists(self.user_data_dir):
                try:
                    shutil.rmtree(self.user_data_dir, ignore_errors=True)
                except Exception as cleanup_error:
                    logger.warning(f"Error cleaning up user data directory after failure: {str(cleanup_error)}")
            raise

    def teardown_method(self, method=None):
        """
        Teardown for each test method.

        Args:
            method: The test method being called
        """
        logger.info(f"Ending test: {self.__class__.__name__}")
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        logger.info(f"Test duration: {duration:.2f} seconds")

        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
        except Exception as e:
            logger.error(f"Error quitting driver: {str(e)}")
        finally:
            # Clean up user data directory
            if hasattr(self, 'user_data_dir') and self.user_data_dir and os.path.exists(self.user_data_dir):
                try:
                    shutil.rmtree(self.user_data_dir, ignore_errors=True)
                except Exception as e:
                    logger.warning(f"Error cleaning up user data directory: {str(e)}")

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
