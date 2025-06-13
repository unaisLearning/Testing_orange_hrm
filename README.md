# OrangeHRM UI Test Automation Framework

A robust, scalable UI test automation framework for OrangeHRM using Python, Selenium, and PyTest.

## 🚀 Features

- Page Object Model (POM) design pattern
- Modular and maintainable architecture
- Parallel test execution support
- Allure reporting integration
- Type hints and comprehensive logging
- Screenshot capture on test failures
- Dynamic wait handling
- CI/CD ready

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Chrome/Firefox browser

## 🛠 Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd orangehrm-automation
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Running Tests

### Run all tests:

```bash
pytest
```

### Run tests in parallel:

```bash
pytest -n auto
```

### Run tests with Allure reporting:

```bash
pytest --alluredir=./allure-results
allure serve ./allure-results
```

### Run specific test file:

```bash
pytest tests/test_login.py
```

## 📁 Project Structure

```
├── tests/              # Test cases
├── pages/             # Page Object classes
├── utils/             # Utility functions
├── configs/           # Configuration files
├── constants/         # Static data and constants
├── fixtures/          # PyTest fixtures
├── requirements.txt   # Project dependencies
└── README.md         # Project documentation
```

## 🔧 Configuration

- Update `configs/config.py` for environment-specific settings
- Modify `constants/selectors.py` for web element locators
- Adjust timeouts in `constants/timeouts.py`

## 📊 Reports

- HTML reports: `pytest --html=report.html`
- Allure reports: `allure serve ./allure-results`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
