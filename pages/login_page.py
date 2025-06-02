"""
Login page object for OrangeHRM.
"""
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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
                EC.presence_of_element_located(LoginPageSelectors.USERNAME)
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
            # Check for general error message
            error_element = self.find_element(LoginPageSelectors.ERROR_MESSAGE)
            if error_element:
                return error_element.text
            
            # Check for required field error
            required_error = self.find_element(LoginPageSelectors.REQUIRED_ERROR)
            if required_error:
                return required_error.text
            
            return ""
            
        except NoSuchElementException:
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
            # Check for error messages first
            if self.get_error_message():
                return False
            
            # Check for dashboard element
            dashboard = self.find_element(LoginPageSelectors.DASHBOARD)
            return bool(dashboard)
            
        except NoSuchElementException:
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