"""
WebDriver manager for handling browser instances.
"""
import os
import uuid
import tempfile
from typing import Dict, Any, Optional

from selenium import webdriver
from config.config import Config
from utils.logger import logger

class DriverManager:
    """Manages WebDriver instances for different browsers."""

    @staticmethod
    def create_driver(browser_name: Optional[str] = None) -> webdriver.Remote:
        """
        Create and configure a WebDriver instance.

        Args:
            browser_name: Name of the browser to use (defaults to Config.BROWSER)

        Returns:
            webdriver.Remote: Configured WebDriver instance
        """
        browser_name = browser_name or Config.BROWSER.lower()
        options = Config.get_browser_options().get(browser_name, {})

        try:
            if browser_name == "chrome":
                driver = DriverManager._create_chrome_driver(options)
            elif browser_name == "firefox":
                driver = DriverManager._create_firefox_driver(options)
            elif browser_name == "edge":
                driver = DriverManager._create_edge_driver(options)
            else:
                raise ValueError(f"Unsupported browser: {browser_name}")

            # Set common driver configurations
            driver.set_window_size(*options.get("window_size", (1920, 1080)))
            driver.implicitly_wait(Config.IMPLICIT_WAIT)
            driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)

            logger.info(f"Created {browser_name} WebDriver instance")
            return driver

        except Exception as e:
            logger.error(f"Failed to create {browser_name} WebDriver: {str(e)}")
            raise

    @staticmethod
    def _create_chrome_driver(options: Dict[str, Any]) -> webdriver.Chrome:
        """Create Chrome WebDriver instance using Selenium Manager and a unique user-data-dir."""
        chrome_options = webdriver.ChromeOptions()

        if options.get("headless"):
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")


        # Selenium 4+ provides Selenium Manager which resolves drivers automatically
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    @staticmethod
    def _create_firefox_driver(options: Dict[str, Any]) -> webdriver.Firefox:
        """Create Firefox WebDriver instance."""
        firefox_options = webdriver.FirefoxOptions()

        if options.get("headless"):
            firefox_options.add_argument("--headless")

        # Selenium Manager will resolve the geckodriver binary automatically
        return webdriver.Firefox(options=firefox_options)

    @staticmethod
    def _create_edge_driver(options: Dict[str, Any]) -> webdriver.Edge:
        """Create Edge WebDriver instance."""
        edge_options = webdriver.EdgeOptions()

        if options.get("headless"):
            edge_options.add_argument("--headless")

        # Selenium Manager will resolve the edgedriver binary automatically
        return webdriver.Edge(options=edge_options)
