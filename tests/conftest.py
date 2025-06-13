"""
PyTest fixtures for the test framework.
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import logging
import os
import allure
from selenium.webdriver.remote.webdriver import WebDriver
from datetime import datetime

from utils.driver_manager import DriverManager
from utils.logger import logger
from config.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def write_allure_environment():
    env = Config.get_allure_environment_properties()
    os.makedirs(Config.ALLURE_RESULTS_DIR, exist_ok=True)
    with open(os.path.join(Config.ALLURE_RESULTS_DIR, "environment.properties"), "w") as f:
        for k, v in env.items():
            f.write(f"{k}={v}\n")

# Pytest hook to write environment.properties before session starts
@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    write_allure_environment()

@pytest.fixture(scope="session")
def browser() -> WebDriver:
    """
    Create and configure a WebDriver instance.
    
    Returns:
        WebDriver: Configured WebDriver instance
    """
    driver = None
    try:
        driver = DriverManager.create_driver()
        logger.info("Browser started")
        yield driver
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")

@pytest.fixture(autouse=True)
def clear_cookies(browser: WebDriver) -> None:
    """Clear cookies before each test."""
    browser.delete_all_cookies()
    logger.debug("Cleared browser cookies")

@pytest.fixture(scope="function")
def login_page(browser):
    """
    Fixture to create login page object.
    
    Args:
        browser: WebDriver instance from browser fixture
        
    Returns:
        LoginPage instance
    """
    from pages.login_page import LoginPage
    return LoginPage(browser)

@pytest.fixture(scope="function")
def dashboard_page(browser):
    """
    Fixture to create dashboard page object.
    
    Args:
        browser: WebDriver instance from browser fixture
        
    Returns:
        DashboardPage instance
    """
    from pages.dashboard_page import DashboardPage
    return DashboardPage(browser)

@pytest.fixture(scope="function")
def logged_in_user(login_page, dashboard_page):
    """
    Fixture to perform login before test.
    
    Args:
        login_page: LoginPage instance
        dashboard_page: DashboardPage instance
        
    Returns:
        DashboardPage instance after successful login
    """
    login_page.navigate()
    login_page.login()
    assert dashboard_page.is_user_logged_in(), "Login failed"
    return dashboard_page

def _get_page_object_from_request(item):
    # Try to get a page object from the test function's arguments
    for arg in item.funcargs.values():
        if hasattr(arg, 'driver') and hasattr(arg, 'take_screenshot'):
            return arg
    return None

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'call' and rep.failed:
        page = _get_page_object_from_request(item)
        if page:
            screenshot_path = page.take_screenshot(item.name)
            # Attach to Allure if available
            try:
                with open(screenshot_path, 'rb') as f:
                    allure.attach(f.read(), name=item.name, attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                logging.error(f"Failed to attach screenshot to Allure: {e}") 