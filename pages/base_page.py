"""
Base page object model.
"""
from typing import Optional, List
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from utils.logger import logger
from config.config import Config

class BasePage:
    """Base class for all page objects."""
    
    def __init__(self, driver: WebDriver):
        """
        Initialize base page.
        
        Args:
            driver: WebDriver instance
        """
        self.driver = driver
    
    def find_element(self, selector: str, timeout: Optional[int] = None) -> WebElement:
        """
        Find an element using the provided selector.
        
        Args:
            selector: CSS selector string
            timeout: Optional timeout in seconds
        
        Returns:
            WebElement: Found element
        
        Raises:
            TimeoutException: If element is not found within timeout
        """
        try:
            wait = WebDriverWait(self.driver, timeout or Config.EXPLICIT_WAIT)
            
            logger.debug(f"Waiting for element: {selector}")
            element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
            logger.debug(f"Found element: {selector}")
            
            return element
            
        except TimeoutException as e:
            logger.error(f"Element not found: {selector}")
            logger.debug(f"Current URL: {self.driver.current_url}")
            logger.debug(f"Page source: {self.driver.page_source[:500]}...")
            raise
        except Exception as e:
            logger.error(f"Error finding element {selector}: {str(e)}")
            raise
    
    def find_elements(self, selector: str, timeout: Optional[int] = None) -> List[WebElement]:
        """
        Find multiple elements using the provided selector.
        
        Args:
            selector: CSS selector string
            timeout: Optional timeout in seconds
        
        Returns:
            List[WebElement]: List of found elements
        """
        try:
            wait = WebDriverWait(self.driver, timeout or Config.EXPLICIT_WAIT)
            
            logger.debug(f"Waiting for elements: {selector}")
            elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
            logger.debug(f"Found {len(elements)} elements: {selector}")
            
            return elements
            
        except TimeoutException as e:
            logger.error(f"Elements not found: {selector}")
            return []
        except Exception as e:
            logger.error(f"Error finding elements {selector}: {str(e)}")
            return []
    
    def wait_for_element_to_be_clickable(self, selector: str, timeout: Optional[int] = None) -> WebElement:
        """
        Wait for an element to be clickable.
        
        Args:
            selector: CSS selector string
            timeout: Optional timeout in seconds
        
        Returns:
            WebElement: Clickable element
        """
        try:
            wait = WebDriverWait(self.driver, timeout or Config.EXPLICIT_WAIT)
            
            logger.debug(f"Waiting for element to be clickable: {selector}")
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            logger.debug(f"Element is clickable: {selector}")
            
            return element
            
        except TimeoutException as e:
            logger.error(f"Element not clickable: {selector}")
            raise
        except Exception as e:
            logger.error(f"Error waiting for element to be clickable {selector}: {str(e)}")
            raise
    
    def is_element_present(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Check if an element is present.
        
        Args:
            selector: CSS selector string
            timeout: Optional timeout in seconds
        
        Returns:
            bool: True if element is present, False otherwise
        """
        try:
            self.find_element(selector, timeout)
            return True
        except (TimeoutException, NoSuchElementException):
            return False
        except Exception as e:
            logger.error(f"Error checking element presence {selector}: {str(e)}")
            return False
    
    def get_text(self, selector: str) -> str:
        """
        Get text from an element.
        
        Args:
            selector: CSS selector string
        
        Returns:
            str: Element text
        """
        try:
            element = self.find_element(selector)
            text = element.text
            logger.debug(f"Got text from element {selector}: {text}")
            return text
        except Exception as e:
            logger.error(f"Error getting text from element {selector}: {str(e)}")
            return ""
    
    def input_text(self, selector: str, text: str) -> None:
        """
        Input text into an element.
        
        Args:
            selector: CSS selector string
            text: Text to input
        """
        try:
            element = self.find_element(selector)
            element.clear()
            element.send_keys(text)
            logger.debug(f"Input text into element {selector}: {text}")
        except Exception as e:
            logger.error(f"Error inputting text into element {selector}: {str(e)}")
            raise
    
    def click(self, selector: str) -> None:
        """
        Click an element.
        
        Args:
            selector: CSS selector string
        """
        try:
            element = self.wait_for_element_to_be_clickable(selector)
            element.click()
            logger.debug(f"Clicked element: {selector}")
        except Exception as e:
            logger.error(f"Error clicking element {selector}: {str(e)}")
            raise
    
    def take_screenshot(self, name: Optional[str] = None) -> str:
        """
        Take screenshot of current page.
        
        Args:
            name: Optional custom name for the screenshot
            
        Returns:
            Path to the saved screenshot
        """
        if not os.path.exists(Config.SCREENSHOT_DIR):
            os.makedirs(Config.SCREENSHOT_DIR)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name or 'screenshot'}_{timestamp}.png"
        filepath = os.path.join(Config.SCREENSHOT_DIR, filename)
        
        self.driver.save_screenshot(filepath)
        logger.info(f"Screenshot saved: {filepath}")
        return filepath 