"""
WebDriver manager for handling browser instances.
"""
import os
import uuid
import tempfile
import platform
import subprocess
from typing import Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.core.os_manager import ChromeType

from config.config import Config
from utils.logger import logger

class DriverManager:
    """Manages WebDriver instances for different browsers."""

    @staticmethod
    def _get_chrome_driver_path() -> str:
        """
        Get the appropriate ChromeDriver path based on the environment.
        Returns the path to ChromeDriver executable.
        """
        # Check if running in GitHub Actions
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            logger.info("Running in GitHub Actions environment")
            return ChromeDriverManager().install()
        
        # Check if running on Mac ARM64
        if platform.system() == 'Darwin' and platform.machine() == 'arm64':
            logger.info("Running on Mac ARM64")
            
            # Use the local chromedriver
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
                    else:
                        logger.error(f"ChromeDriver test failed with output: {result.stderr}")
                except Exception as e:
                    logger.error(f"Local ChromeDriver test failed: {str(e)}")
            
            raise RuntimeError("Local ChromeDriver not found or not working. Please ensure chromedriver is in the project root directory.")
        
        # Default case for other environments
        logger.info("Using default ChromeDriver setup")
        return ChromeDriverManager().install()

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
        """Create Chrome WebDriver instance using webdriver-manager and a unique user-data-dir."""
        chrome_options = webdriver.ChromeOptions()

        if options.get("headless"):
            chrome_options.add_argument("--headless=new")  # Updated headless mode

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-notifications")

        # Create a unique user-data-dir to avoid parallel execution conflicts
        user_data_dir = tempfile.mkdtemp(prefix=f"user-data-dir-{uuid.uuid4()}")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

        # Get appropriate ChromeDriver path
        driver_path = DriverManager._get_chrome_driver_path()
        logger.info(f"Using ChromeDriver at: {driver_path}")
        
        # Initialize WebDriver
        service = ChromeService(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    @staticmethod
    def _create_firefox_driver(options: Dict[str, Any]) -> webdriver.Firefox:
        """Create Firefox WebDriver instance."""
        firefox_options = webdriver.FirefoxOptions()

        if options.get("headless"):
            firefox_options.add_argument("--headless")

        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=firefox_options)

    @staticmethod
    def _create_edge_driver(options: Dict[str, Any]) -> webdriver.Edge:
        """Create Edge WebDriver instance."""
        edge_options = webdriver.EdgeOptions()

        if options.get("headless"):
            edge_options.add_argument("--headless")

        service = EdgeService(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=edge_options)
