from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
import time
from dotenv import load_dotenv
import os
import pickle  # For saving and loading cookies

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
USERNAME = os.getenv("PORTAL_EMAIL")
PASSWORD = os.getenv("PORTAL_PASSWORD")

# MongoDB Setup
client = MongoClient(mongo_uri, tls=True, tlsAllowInvalidCertificates=True)
db = client['job_scraper']  
collection = db['processeng_jobs']  
COOKIE_FILE = "cookies.pkl"


def save_cookies(driver, filename):
    """Save cookies to a file."""
    with open(filename, "wb") as file:
        pickle.dump(driver.get_cookies(), file)
    print(f"[DEBUG] Cookies saved to {filename}")


def load_and_force_cookies(driver, filename, url):
    """Load cookies from a file and inject them into the browser session."""
    try:
        with open(filename, "rb") as file:
            cookies = pickle.load(file)
        driver.get(url)  # Open the base URL before injecting cookies
        time.sleep(5)  # Ensure the page loads before injecting cookies
        for cookie in cookies:
            driver.add_cookie(cookie)
        print(f"[DEBUG] Cookies loaded and forced from {filename}")
        driver.refresh()  # Refresh the page after injecting cookies
        time.sleep(5)
        return True
    except FileNotFoundError:
        print(f"[DEBUG] Cookie file {filename} not found.")
        return False


def login_to_portal(driver, login_credentials):
    """
    Logs into the job portal using the provided credentials.

    Args:
        driver: Selenium WebDriver instance.
        login_credentials: A dictionary containing 'username' and 'password'.

    Returns:
        bool: True if login is successful, False otherwise.
    """
    try:
        print("[DEBUG] Checking if login fields are present...")

        # Wait for the username field using CSS selector
        email_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input#username"))
        )
        print("[DEBUG] Email input field located.")

        # Ensure the element is interactable
        driver.execute_script("arguments[0].focus();", email_input)
        email_input.clear()
        email_input.send_keys(login_credentials['username'])
        print("[DEBUG] Entered email address.")

        # Wait for the password field using CSS selector
        password_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input#password"))
        )
        print("[DEBUG] Password input field located.")

        driver.execute_script("arguments[0].focus();", password_input)
        password_input.clear()
        password_input.send_keys(login_credentials['password'])
        print("[DEBUG] Entered password.")

        # Click the "Sign In" button using CSS selector
        sign_in_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick*='validateFields']"))
        )
        sign_in_button.click()
        print("[DEBUG] Clicked 'Sign In' button.")

        # Allow time for the login process
        time.sleep(30)

        # Verify if login succeeded by checking for login elements
        try:
            driver.find_element(By.CSS_SELECTOR, "input#username")
            print("[DEBUG] Login failed. Username field still present.")
            return False
        except Exception:
            print("[DEBUG] Login successful. Username field no longer present.")
            return True

    except Exception as e:
        print(f"[DEBUG] Login process encountered an error: {e}")
        return False




def apply_to_job(driver, job, collection, login_credentials):
    """
    Automates the process of applying to a job.

    Args:
        driver: The Selenium WebDriver instance.
        job: A dictionary containing job details, including the link.
        collection: MongoDB collection object to update job status.
        login_credentials: A dictionary containing 'username' and 'password'.
    """
    try:
        # Step 1: Navigate to the job description page
        print(f"[DEBUG] Opening job link: {job['Link']}")
        driver.get(job["Link"])
        time.sleep(10)
        print("[DEBUG] Cookies after navigating to job page:", driver.get_cookies())

        # Step 2: Click the "Apply Now" button
        try:
            print("[DEBUG] Searching for 'Apply Now' button...")
            apply_now_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-primary.btn-large.btn-lg.apply.dialogApplyBtn"))
            )
            apply_now_button.click()
            print("[DEBUG] 'Apply Now' button clicked")
            time.sleep(5)
            print("[DEBUG] Cookies after clicking 'Apply Now':", driver.get_cookies())
        except Exception as e:
            print(f"[DEBUG] Failed to click 'Apply Now' button: {e}")
            return False

        # Step 3: Handle login if redirected or login page detected
        try:
            print("[DEBUG] Checking for login elements...")
            email_input = driver.find_element(By.ID, "username")  # Check if username field exists
            print("[DEBUG] Login page detected. Proceeding to log in...")
    
        # Perform the login
            if not login_to_portal(driver, login_credentials):
                print("[DEBUG] Login failed. Could not apply for the job.")
            return False
        except Exception:
            print("[DEBUG] Login page not detected. Proceeding to the next step...")
        # No login elements found, proceed to step 4


        # Step 4: Locate the "Apply" button
        try:
            print("[DEBUG] Searching for 'Apply' button on the application page...")
            apply_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "301:_submitBtn"))
            )
            apply_button.click()
            print("[DEBUG] Successfully clicked 'Apply' button.")
            time.sleep(10)
            print("[DEBUG] Cookies after applying for the job:", driver.get_cookies())

            # Step 5: Update job status in MongoDB
            print("[DEBUG] Updating job status in MongoDB...")
            collection.update_one(
                {"Job ID": job["Job ID"]},
                {"$set": {"Applied": True}},
                upsert=False
            )
            print(f"[DEBUG] Job status updated to 'Applied' for: {job['Title']}")
            return True

        except Exception as e:
            print(f"[DEBUG] Failed to complete 'Apply' process: {e}")
            print("[DEBUG] Current URL:", driver.current_url)
            print("[DEBUG] Page Source Snippet:", driver.page_source[:500])
            return False

    except Exception as e:
        print(f"[DEBUG] Error in applying for job '{job['Title']}': {e}")
        return False


def main():
    print("[DEBUG] Fetching jobs with False status...")
    pending_jobs = collection.find({"Applied": False}).limit(5)
    login_credentials = {"username": USERNAME, "password": PASSWORD}

    print("[DEBUG] Setting up Selenium WebDriver...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    try:
        for job in pending_jobs:
            print(f"[DEBUG] Processing job: {job['Title']}")
            success = apply_to_job(driver, job, collection, login_credentials)
            if not success:
                print(f"[DEBUG] Failed to apply for job: {job['Title']}")
    finally:
        driver.quit()
        print("[DEBUG] Job application process completed.")


if __name__ == "__main__":
    main()
