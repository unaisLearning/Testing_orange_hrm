"""
PyTest fixtures for the test framework.
"""
import os
import logging
from datetime import datetime

import allure
import pytest

from config.config import Config
from utils.logger import logger


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def write_allure_environment() -> None:
    """Write environment.properties for Allure reporting."""
    env = Config.get_allure_environment_properties()
    os.makedirs(Config.ALLURE_RESULTS_DIR, exist_ok=True)
    with open(os.path.join(Config.ALLURE_RESULTS_DIR, "environment.properties"), "w") as f:
        for k, v in env.items():
            f.write(f"{k}={v}\n")


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """PyTest hook to run before the session starts."""
    write_allure_environment()


def _get_page_object_from_request(item):
    """Return the first page object from test function arguments."""
    for arg in item.funcargs.values():
        if hasattr(arg, 'driver') and hasattr(arg, 'take_screenshot'):
            return arg
    return None


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach screenshot to Allure report on test failure."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'call' and rep.failed:
        page = _get_page_object_from_request(item)
        if page:
            screenshot_path = page.take_screenshot(item.name)
            try:
                with open(screenshot_path, 'rb') as f:
                    allure.attach(
                        f.read(),
                        name=item.name,
                        attachment_type=allure.attachment_type.PNG
                    )
            except Exception as e:
                logging.error(f"Failed to attach screenshot to Allure: {e}")

