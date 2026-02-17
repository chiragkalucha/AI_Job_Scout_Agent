# utils/login_helper.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time


class LoginHelper:
    """Help user login to job portals once"""

    @staticmethod
    def _get_driver(portal_name):
        """
        Create a stable Chrome driver with persistent profile
        """

        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # Absolute path for profile (important on Windows)
        profile_path = os.path.abspath(f"./browser_profiles/{portal_name}")
        chrome_options.add_argument(f"--user-data-dir={profile_path}")

        # Use WebDriver Manager (auto version match)
        service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=chrome_options)

        return driver

    @staticmethod
    def request_login(portal_name, login_url):
        """
        Open browser and wait for user to login
        """

        print(f"\n{'='*70}")
        print(f"⚠️  LOGIN REQUIRED: {portal_name}")
        print(f"{'='*70}")
        print(f"\nA browser window will open.")
        print(f"Please login to {portal_name} manually.")
        print(f"Once logged in, come back here and press ENTER.\n")

        driver = LoginHelper._get_driver(portal_name)
        driver.get(login_url)

        input(f"Press ENTER after you've logged in to {portal_name}...")

        print(f"✅ Session saved! Next time, you won't need to login.")

        driver.quit()

    @staticmethod
    def get_logged_in_driver(portal_name):
        """
        Get driver with saved login session
        """

        return LoginHelper._get_driver(portal_name)


# Example usage
if __name__ == "__main__":
    LoginHelper.request_login(
        portal_name="LinkedIn",
        login_url="https://www.linkedin.com/login"
    )
