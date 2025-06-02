"""
Test cases for login functionality.
"""
import pytest
import allure
import json
from pathlib import Path
from datetime import datetime
import os
import glob

from tests.base_test import BaseTest
from pages.login_page import LoginPage
from utils.logger import logger
from config.config import Config

@allure.epic('OrangeHRM')
@allure.feature('Authentication')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
# OrangeHRM Login Test Suite

This test suite verifies the login functionality of OrangeHRM application.

## Test Coverage:
- Valid login scenarios
- Invalid login scenarios
- Error message validations
- Logout functionality

## Prerequisites:
- Valid OrangeHRM credentials
- Access to OrangeHRM demo site
""")
class TestLogin(BaseTest):
    """Test cases for login functionality."""
    
    def setup_method(self, method):
        """
        Setup for each test method.
        
        Args:
            method: The test method being called
        """
        # Call parent setup_method first
        super().setup_method(method)
        
        # Initialize login page
        self.login_page = LoginPage(self.driver)
        self.login_page.navigate()
        
        # Load test data
        test_data_path = Path(__file__).parent.parent / 'test_data' / 'login_test_data.json'
        with open(test_data_path) as f:
            self.test_data = json.load(f)
            
        # Add environment info to Allure
        allure.dynamic.parameter('Browser', Config.BROWSER)
        allure.dynamic.parameter('Environment', Config.CURRENT_ENV)
        allure.dynamic.parameter('Base URL', Config.BASE_URL)
        
        # Attach current log file to Allure report
        log_files = glob.glob('logs/test_run_*.log')
        if log_files:
            latest_log = max(log_files, key=os.path.getctime)
            with open(latest_log, 'r') as f:
                allure.attach(
                    f.read(),
                    name="test_log",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    def teardown_method(self, method):
        """Teardown for each test method."""
        # Attach final log file to Allure report
        log_files = glob.glob('logs/test_run_*.log')
        if log_files:
            latest_log = max(log_files, key=os.path.getctime)
            with open(latest_log, 'r') as f:
                allure.attach(
                    f.read(),
                    name="test_log_final",
                    attachment_type=allure.attachment_type.TEXT
                )
        
        # Call parent teardown_method
        super().teardown_method(method)
    
    @allure.story('Valid Login')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    # Valid Login Test
    
    ## Test Objective:
    Verify that a user can successfully login with valid credentials.
    
    ## Test Steps:
    1. Navigate to login page
    2. Enter valid username
    3. Enter valid password
    4. Click login button
    5. Verify successful login
    
    ## Expected Result:
    User should be logged in successfully and redirected to dashboard.
    """)
    def test_valid_login(self):
        """Test valid login with correct credentials."""
        with allure.step("Navigate to login page"):
            self.login_page.navigate()
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="login_page",
                attachment_type=allure.attachment_type.PNG
            )
        
        with allure.step("Enter valid credentials"):
            self.login_page.login(
                self.test_data['valid_credentials']['username'],
                self.test_data['valid_credentials']['password']
            )
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="credentials_entered",
                attachment_type=allure.attachment_type.PNG
            )
        
        with allure.step("Verify successful login"):
            assert self.login_page.is_login_successful(), "Login was not successful"
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="login_successful",
                attachment_type=allure.attachment_type.PNG
            )
    
    @allure.story('Invalid Login')
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("""
    # Invalid Login Test
    
    ## Test Objective:
    Verify that appropriate error messages are displayed for invalid login attempts.
    
    ## Test Scenarios:
    - Invalid username
    - Invalid password
    - Blank fields
    - Case sensitivity
    - Special characters
    - Long input
    
    ## Expected Result:
    Appropriate error message should be displayed for each invalid attempt.
    """)
    @pytest.mark.parametrize("credentials,expected_error", [
        ("invalid_username", "Invalid credentials"),
        ("invalid_password", "Invalid credentials"),
        ("blank_fields", "Required"),
        ("case_sensitive", "Invalid credentials"),
        ("special_chars", "Invalid credentials"),
        ("long_input", "Invalid credentials")
    ])
    def test_invalid_login(self, credentials, expected_error):
        """Test invalid login scenarios."""
        test_creds = self.test_data['invalid_credentials'][credentials]
        
        with allure.step(f"Login with {credentials}"):
            self.login_page.login(test_creds['username'], test_creds['password'])
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name=f"invalid_login_{credentials}",
                attachment_type=allure.attachment_type.PNG
            )
        
        with allure.step("Verify error message"):
            error_message = self.login_page.get_error_message()
            assert error_message == expected_error, \
                f"Expected error message '{expected_error}' but got '{error_message}'"
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name=f"error_message_{credentials}",
                attachment_type=allure.attachment_type.PNG
            )
    
    @allure.story('Login Button')
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("""
    # Login Button Test
    
    ## Test Objective:
    Verify that clicking login button without entering data shows required field error.
    
    ## Test Steps:
    1. Navigate to login page
    2. Click login button without entering data
    3. Verify required field error message
    
    ## Expected Result:
    Required field error message should be displayed.
    """)
    def test_login_button_without_data(self):
        """Test clicking login button without entering any data."""
        with allure.step("Click login button without data"):
            self.login_page.click_login_button()
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="login_button_clicked",
                attachment_type=allure.attachment_type.PNG
            )
        
        with allure.step("Verify error message"):
            error_message = self.login_page.get_error_message()
            assert error_message == "Required", \
                f"Expected error message 'Required' but got '{error_message}'"
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="required_error_message",
                attachment_type=allure.attachment_type.PNG
            )
    
    @allure.story('Error Message Persistence')
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("""
    # Error Message Persistence Test
    
    ## Test Objective:
    Verify that error message persists after failed login attempt.
    
    ## Test Steps:
    1. Attempt login with invalid credentials
    2. Verify error message
    3. Verify error message persists
    
    ## Expected Result:
    Error message should remain visible after failed login.
    """)
    def test_error_message_persistence(self):
        """Test that error message persists after failed login attempt."""
        with allure.step("Attempt login with invalid credentials"):
            self.login_page.login("invalid", "invalid")
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="invalid_login_attempt",
                attachment_type=allure.attachment_type.PNG
            )
        
        with allure.step("Verify error message"):
            error_message = self.login_page.get_error_message()
            assert error_message == "Invalid credentials", \
                f"Expected error message 'Invalid credentials' but got '{error_message}'"
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="error_message",
                attachment_type=allure.attachment_type.PNG
            )
        
        with allure.step("Verify error message persists"):
            assert self.login_page.get_error_message() == "Invalid credentials", \
                "Error message did not persist"
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="persistent_error_message",
                attachment_type=allure.attachment_type.PNG
            )
    
    @allure.story('Logout')
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("""
    # Logout Test
    
    ## Test Objective:
    Verify that user can successfully logout from the application.
    
    ## Test Steps:
    1. Login with valid credentials
    2. Verify successful login
    3. Perform logout
    4. Verify successful logout
    
    ## Expected Result:
    User should be able to logout successfully.
    """)
    def test_logout(self):
        """Test logout functionality."""
        with allure.step("Login with valid credentials"):
            self.login_page.login(
                self.test_data['valid_credentials']['username'],
                self.test_data['valid_credentials']['password']
            )
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="login_for_logout",
                attachment_type=allure.attachment_type.PNG
            )
        
        with allure.step("Verify successful login"):
            assert self.login_page.is_login_successful(), "Login was not successful"
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="login_successful_for_logout",
                attachment_type=allure.attachment_type.PNG
            )
        
        with allure.step("Perform logout"):
            self.login_page.logout()
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="logout_clicked",
                attachment_type=allure.attachment_type.PNG
            )
        
        with allure.step("Verify successful logout"):
            assert not self.login_page.is_login_successful(), "Logout was not successful"
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="logout_successful",
                attachment_type=allure.attachment_type.PNG
            ) 