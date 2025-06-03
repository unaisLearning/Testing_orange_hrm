"""
Login page object for OrangeHRM.
"""
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from constants.selectors import LoginPageSelectors
from config.config import Config
from utils.logger import logger

class LoginPage(BasePage):
    """Login page object for OrangeHRM."""
    
    def __init__(self, driver: WebDriver):
        """
        Initialize the login page.
        
        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.url = Config.BASE_URL
        self.selectors = LoginPageSelectors
    
    def navigate(self) -> None:
        """Navigate to the login page."""
        try:
            logger.info(f"Navigating to {self.url}")
            self.driver.get(self.url)
            
            # Wait for login form to be present
            WebDriverWait(self.driver, Config.IMPLICIT_WAIT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, LoginPageSelectors.USERNAME))
            )
            logger.info("Login page loaded successfully")
            
            # Check if already logged in
            if "/dashboard/index" in self.driver.current_url:
                logger.info("User already logged in, attempting to logout")
                self.logout()
                
        except TimeoutException:
            logger.error("Timeout waiting for login page to load")
            raise
        except Exception as e:
            logger.error(f"Failed to navigate to login page: {str(e)}")
            raise
    
    def login(self, username: str, password: str) -> None:
        """
        Login with given credentials.
        
        Args:
            username: Username to login with
            password: Password to login with
        """
        try:
            # Input username
            self.input_text(LoginPageSelectors.USERNAME, username)
            logger.info(f"Entered username: {username}")
            
            # Input password
            self.input_text(LoginPageSelectors.PASSWORD, password)
            logger.info("Entered password")
            
            # Click login button
            self.click_login_button()
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise
    
    def click_login_button(self) -> None:
        """Click the login button."""
        try:
            self.click(LoginPageSelectors.LOGIN_BUTTON)
            logger.info("Clicked login button")
        except Exception as e:
            logger.error(f"Failed to click login button: {str(e)}")
            raise
    
    def get_error_message(self) -> str:
        """
        Get the error message if present.
        
        Returns:
            str: Error message text or empty string if no error
        """
        try:
            # Wait for either error message type to be present
            WebDriverWait(self.driver, Config.IMPLICIT_WAIT).until(
                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, LoginPageSelectors.ERROR_MESSAGE)) > 0 or
                             len(driver.find_elements(By.CSS_SELECTOR, LoginPageSelectors.REQUIRED_ERROR)) > 0
            )
            
            # Check for general error message
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, LoginPageSelectors.ERROR_MESSAGE)
            if error_elements:
                return error_elements[0].text.strip()
            
            # Check for required field error
            required_elements = self.driver.find_elements(By.CSS_SELECTOR, LoginPageSelectors.REQUIRED_ERROR)
            if required_elements:
                return required_elements[0].text.strip()
            
            return ""
            
        except TimeoutException:
            logger.debug("No error message found within timeout period")
            return ""
        except Exception as e:
            logger.error(f"Failed to get error message: {str(e)}")
            return ""
    
    def is_login_successful(self) -> bool:
        """
        Check if login was successful.
        
        Returns:
            bool: True if login was successful, False otherwise
        """
        try:
            # Wait for URL to change to dashboard
            WebDriverWait(self.driver, Config.IMPLICIT_WAIT).until(
                lambda driver: "/dashboard/index" in driver.current_url
            )
            
            # Check for dashboard element
            dashboard = self.find_element(LoginPageSelectors.DASHBOARD)
            return bool(dashboard)
            
        except (TimeoutException, NoSuchElementException):
            return False
        except Exception as e:
            logger.error(f"Failed to check login status: {str(e)}")
            return False
    
    def logout(self) -> None:
        """Logout from the application."""
        try:
            # Click user dropdown
            self.click(LoginPageSelectors.USER_DROPDOWN)
            logger.info("Clicked user dropdown")
            
            # Click logout link
            self.click(LoginPageSelectors.LOGOUT_LINK)
            logger.info("Clicked logout link")
            
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            raise 