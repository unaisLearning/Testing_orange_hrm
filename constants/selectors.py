"""
CSS selectors for web elements.
"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class LoginPageSelectors:
    """Selectors for login page elements."""
    USERNAME: str = "input[name='username']"
    PASSWORD: str = "input[name='password']"
    LOGIN_BUTTON: str = "button[type='submit']"
    ERROR_MESSAGE: str = ".oxd-alert-content-text, .oxd-text--p"
    REQUIRED_ERROR: str = ".oxd-input-field-error-message, .oxd-text--p"
    DASHBOARD: str = ".oxd-topbar-header-breadcrumb"
    USER_DROPDOWN: str = ".oxd-userdropdown-tab"
    LOGOUT_LINK: str = "a[href*='logout']"

class DashboardPageSelectors:
    """Selectors for the dashboard page."""
    
    WELCOME_MESSAGE = {'type': 'css', 'value': '.oxd-userdropdown-name, .oxd-userdropdown-tab'}
    USER_DROPDOWN = {'type': 'css', 'value': '.oxd-userdropdown-tab'}
    LOGOUT_LINK = {'type': 'css', 'value': 'a[href="/web/index.php/auth/logout"]'}
    
    MENU_ITEMS: Dict[str, str] = {
        "type": "css",
        "value": ".oxd-main-menu-item"
    } 