# utils/silent_browser.py - Completely silent browser

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

def get_silent_driver():
    """
    Get a completely silent Chrome driver
    No windows, no popups, no interruptions
    """
    
    chrome_options = Options()
    
    # CRITICAL: Headless mode (no visible window)
    chrome_options.add_argument('--headless=new')  # New headless mode
    
    # Additional silent options
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--log-level=3')  # Suppress logs
    chrome_options.add_argument('--silent')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-breakpad')
    chrome_options.add_argument('--disable-component-extensions-with-background-pages')
    chrome_options.add_argument('--disable-features=TranslateUI')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--window-position=-2400,-2400')  # Off-screen
    
    # User agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Suppress all notifications
    prefs = {
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_settings.popups': 0,
        'profile.managed_default_content_settings.images': 2  # Disable images for speed
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    # Suppress ChromeDriver logs
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Service with suppressed logs
    service = Service(log_path='NUL' if os.name == 'nt' else '/dev/null')
    
    driver = webdriver.Chrome(options=chrome_options, service=service)
    
    return driver