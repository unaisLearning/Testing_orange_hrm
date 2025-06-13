"""
Dashboard page object for OrangeHRM.
"""
from typing import List, Optional
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage
from constants.selectors import DashboardPageSelectors

class DashboardPage(BasePage):
    """Dashboard page object for OrangeHRM."""
    
    def __init__(self, driver: WebDriver):
        """
        Initialize the dashboard page.
        
        Args:
            driver: WebDriver instance
        """
        super().__init__(driver)
        self.selectors = DashboardPageSelectors
    
    def get_welcome_message(self) -> str:
        """
        Get the welcome message text.
        
        Returns:
            Welcome message text
        """
        return self.get_text(self.selectors.WELCOME_MESSAGE)
    
    def logout(self) -> None:
        """Perform logout action."""
        self.click(self.selectors.USER_DROPDOWN)
        self.click(self.selectors.LOGOUT_BUTTON)
    
    def get_menu_items(self) -> List[str]:
        """
        Get list of menu items.
        
        Returns:
            List of menu item texts
        """
        elements = self.driver.find_elements(
            By.CSS_SELECTOR,
            self.selectors.MENU_ITEMS["value"]
        )
        return [element.text for element in elements]
    
    def is_user_logged_in(self) -> bool:
        """
        Check if user is logged in.
        
        Returns:
            True if user is logged in, False otherwise
        """
        return self.is_element_present(self.selectors.WELCOME_MESSAGE) 