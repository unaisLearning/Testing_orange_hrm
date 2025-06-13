"""
WebDriver manager for handling browser instances.
"""
import os
import uuid
import tempfile
import platform
import subprocess
import shutil
from typing import Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.options import Options

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
        # Always use webdriver-manager in GitHub Actions
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            logger.info("Running in GitHub Actions environment")
            try:
                # Install ChromeDriver using webdriver-manager
                driver_path = ChromeDriverManager().install()
                # Verify it's the correct executable
                if not os.path.basename(driver_path) == 'chromedriver':
                    # Find the actual chromedriver executable in the directory
                    driver_dir = os.path.dirname(driver_path)
                    for file in os.listdir(driver_dir):
                        if file == 'chromedriver':
                            driver_path = os.path.join(driver_dir, file)
                            break
                # Make sure it's executable
                os.chmod(driver_path, 0o755)
                logger.info(f"Using ChromeDriver at: {driver_path}")
                return driver_path
            except Exception as e:
                logger.error(f"Failed to setup ChromeDriver in GitHub Actions: {str(e)}")
                raise
        
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

    @staticmethod
    def _get_unique_user_data_dir() -> str:
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
        """
        Create and configure a Chrome WebDriver instance.

        Args:
            options: Optional Chrome options to use

        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        try:
            chrome_options = webdriver.ChromeOptions()
            
            # Add common Chrome options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-notifications")
            
            # Create a unique user data directory for this instance
            user_data_dir = DriverManager._get_unique_user_data_dir()
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            
            # Add headless mode in GitHub Actions
            if os.environ.get('GITHUB_ACTIONS') == 'true':
                chrome_options.add_argument('--headless')
            
            # Get appropriate ChromeDriver path
            driver_path = DriverManager._get_chrome_driver_path()
            service = ChromeService(driver_path)
            
            # Create the driver with explicit cleanup
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Register cleanup
            def cleanup():
                try:
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error during driver cleanup: {str(e)}")
                finally:
                    try:
                        shutil.rmtree(user_data_dir, ignore_errors=True)
                    except Exception as e:
                        logger.warning(f"Error cleaning up user data directory: {str(e)}")
            
            import atexit
            atexit.register(cleanup)
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {str(e)}")
            # Clean up user data directory on failure
            try:
                if 'user_data_dir' in locals():
                    shutil.rmtree(user_data_dir, ignore_errors=True)
            except Exception as cleanup_error:
                logger.warning(f"Error cleaning up user data directory after failure: {str(cleanup_error)}")
            raise

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
