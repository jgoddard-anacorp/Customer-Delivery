from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import time
import argparse

def main():
    parser = argparse.ArgumentParser(description="Welloptix report generator")    
    parser.add_argument("--username", required=True, type=str, help="Login username") 
    parser.add_argument("--password", required=True, type=str, help="Password")
    parser.add_argument("--customer_tag", required=True, type=str, help="Realm tag for url ie https://welloptix.net/<Realm Tag>/ANYWAYS/Reports")
    parser.add_argument("--output_directory", required=True, type=str, help="Directory to output to")
    parser.add_argument("--report_type", required=False, type=str, default="Tag Configurable Report", help="Report type")
    parser.add_argument("--period_preset", required=False, type=str, default="Previous calendar day", help="Reporting period")
    parser.add_argument("--tag_type", required=False, type=str, default="RealmTag", help="Type of tags to show")   
    parser.add_argument("--tag_area", required=False, type=str, default="All Areas", help="Tag areas")
    parser.add_argument("--output_type", required=False, type=str, default="CSV File", help="Output file type, default CSV")
    args = parser.parse_args()
    
    # Set up the Chrome WebDriver
    print("Setting up web driver...")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-crash-reporter")
    options.add_experimental_option("prefs", {
        "download.default_directory": args.output_directory, 
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    
    })
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Open the webpage
    driver.get(f"https://welloptix.net/{args.customer_tag}/ANYWHERE/Reports")  # Change this URL to the actual login page
    
    # Wait for the page to load completely
    driver.implicitly_wait(10)  # Waits up to 10 seconds for the elements to become available
    
    # Enter username
    print("Logging in...")
    username = driver.find_element(By.ID, "username")  # Replace 'username' with the actual ID if different
    username.clear()
    username.send_keys(args.username)  # Replace with the actual username
    
    # Enter password
    password = driver.find_element(By.ID, "password")  # Replace 'password' with the actual ID if different
    password.clear()
    password.send_keys(args.password)  # Replace with the actual password
    
    # Find the login button and click it
    login_button = driver.find_element(By.ID, "login")  # Replace 'login' with the actual ID if different
    login_button.click()
    
    t = time.time()
    print("Loading reports page...")
    
    # Wait for the save report button
    save_report_button = WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, '//button[.//canvas[@width="32" and @height="32"]]')))

    l = time.time() - t
    print(f"Loaded reports in {l} seconds")
    
    # Configure select boxes
    print("Configuring...")
    report_type = driver.find_element(By.XPATH, "//select[.//option[text()='Tag Configurable Report']]")
    select = Select(report_type)
    select.select_by_visible_text(args.report_type)
    
    presets = driver.find_element(By.XPATH, "//select[.//option[text()='Previous calendar month']]")
    select = Select(presets)
    select.select_by_visible_text(args.period_preset)
    
    types = driver.find_element(By.XPATH, "//select[.//option[text()='RealmTag']]")
    select = Select(types)
    select.select_by_visible_text(args.tag_type)
    
    areas = driver.find_element(By.XPATH, "//select[.//option[text()='All Areas']]")
    select = Select(areas)
    select.select_by_visible_text(args.tag_area)
    
    output_type = driver.find_element(By.XPATH, "//select[.//option[text()='CSV File']]")
    select = Select(output_type)
    select.select_by_visible_text(args.output_type)
    
    # Select all tags (because we are forced to)
    add_all_button = driver.find_element(By.XPATH, "//button[.//canvas[@width='12' and @height='10']]")
    remove_all_button = driver.find_element(By.XPATH, "(//button[.//canvas[@width='12' and @height='10']])[2]")
    
    if remove_all_button.is_enabled():
        remove_all_button.click()
        print("Removing stale tags...")
        button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[.//canvas[@width='12' and @height='10']]")))
        button.click()
        print("Adding all tags...")
    elif add_all_button.is_enabled():
        add_all_button.click()
        print("Adding all tags...")
    
    # Wait until unclickable (server registered click)
    button = WebDriverWait(driver, 20).until_not(EC.element_to_be_clickable((By.XPATH, "//button[.//canvas[@width='12' and @height='10']]")))
    driver.save_screenshot('final_config.png')
    
    print("Saving report...")
    save_report_button.click()
    
    # This requires the popup box to close on its own when downloading is finished
    button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//button[.//td[normalize-space(text())='Close']]")))
    button = WebDriverWait(driver, 90).until_not(EC.visibility_of_element_located((By.XPATH, "//button[.//td[normalize-space(text())='Close']]")))

    print("Cleaning up...")
    driver.quit()

if __name__ == "__main__":
    main()
