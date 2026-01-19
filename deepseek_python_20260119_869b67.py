#!/usr/bin/env python3
"""
Razorpay Bot - Google Colab Version
Complete automation for testing
"""

print("🚀 Setting up Google Colab environment...")

# Install required packages
!apt-get update
!apt install -y chromium-chromedriver
!pip install selenium faker webdriver-manager

print("✅ Packages installed successfully!")

import sys
import os
import re
import time
import random
import zipfile
from google.colab import files
from IPython.display import Image, display, HTML

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from faker import Faker

print("✅ All imports successful!")

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

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
    
    # Configure for Colab
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
    
    # Use webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)
    
    return driver

def check_razorpay_card_sync(card_data):
    start_time = time.time()
    driver = None
    
    print(f"\n{'='*60}")
    print(f"🌐 STARTING REAL CHECK FOR: {card_data}")
    print(f"{'='*60}\n")
    
    # Store all screenshots
    screenshots = []
    
    try:
        parts = card_data.split('|')
        if len(parts) < 4:
            return {'status': 'error', 'message': 'Invalid card format', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshots': []}
        
        cc, mes, ano, cvv = parts[0], parts[1], parts[2], parts[3]
        if len(ano) == 2:
            ano = f"20{ano}"
        if len(mes) == 1:
            mes = f"0{mes}"
        
        fake_address = generate_fake_address()
        
        print("🔄 Setting up Chrome browser...")
        driver = setup_driver()
        wait = WebDriverWait(driver, 20)
        
        # Create screenshots directory
        os.makedirs('/content/screenshots', exist_ok=True)
        
        # ============================================
        # STEP 1: Product Page -> Click "Buy Now"
        # ============================================
        print("\n[STEP 1] Product page -> Buy Now")
        try:
            driver.get("https://etradus.in/product/computer-software/npav-antivirus-total-security/")
            print(f"✓ Page loaded: {driver.current_url}")
            print(f"✓ Page title: {driver.title}")
            time.sleep(3)
            
            # Take screenshot
            ss1 = f'/content/screenshots/1_product_page_{int(time.time())}.png'
            driver.save_screenshot(ss1)
            screenshots.append(ss1)
            
            buy_now = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='add-to-cart'], .single_add_to_cart_button")))
            buy_now.click()
            print("✓ Buy Now clicked")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Step 1 failed: {str(e)[:100]}")
            return {'status': 'error', 'message': f'Product page failed: {str(e)[:100]}', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshots': screenshots}
        
        # ============================================
        # STEP 2: Cart Page -> Click "Proceed to Checkout"
        # ============================================
        print("\n[STEP 2] Cart -> Proceed to Checkout")
        try:
            driver.get("https://etradus.in/cart/")
            print(f"✓ Cart page: {driver.current_url}")
            time.sleep(3)
            
            # Take screenshot
            ss2 = f'/content/screenshots/2_cart_page_{int(time.time())}.png'
            driver.save_screenshot(ss2)
            screenshots.append(ss2)
            
            checkout_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.checkout-button, .checkout-button")))
            checkout_btn.click()
            print("✓ Checkout clicked")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Step 2 failed: {str(e)[:100]}")
            return {'status': 'error', 'message': f'Cart page failed: {str(e)[:100]}', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshots': screenshots}
        
        # ============================================
        # STEP 3: Checkout Page -> Fill details -> Place Order
        # ============================================
        print("\n[STEP 3] Checkout -> Fill & Place Order")
        try:
            print(f"✓ Checkout page: {driver.current_url}")
            wait.until(EC.presence_of_element_located((By.ID, "billing_first_name")))
            print("✓ Billing form loaded")
            
            driver.find_element(By.ID, "billing_first_name").send_keys(fake_address['first_name'])
            driver.find_element(By.ID, "billing_last_name").send_keys(fake_address['last_name'])
            driver.find_element(By.ID, "billing_email").send_keys(fake_address['email'])
            driver.find_element(By.ID, "billing_phone").send_keys(fake_address['phone'])
            driver.find_element(By.ID, "billing_address_1").send_keys(fake_address['address'])
            driver.find_element(By.ID, "billing_city").send_keys(fake_address['city'])
            
            # Select state
            try:
                state_select = Select(driver.find_element(By.ID, "billing_state"))
                state_select.select_by_value("MH")
            except:
                driver.find_element(By.ID, "billing_state").send_keys("Maharashtra")
            
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
            
            # Take screenshot of filled form
            ss3 = f'/content/screenshots/3_filled_form_{int(time.time())}.png'
            driver.save_screenshot(ss3)
            screenshots.append(ss3)
            
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
            
            time.sleep(5)
            
            # Take screenshot after clicking
            ss4 = f'/content/screenshots/4_place_order_{int(time.time())}.png'
            driver.save_screenshot(ss4)
            screenshots.append(ss4)
            
            print(f"✓ Current URL after order: {driver.current_url}")
            
        except Exception as e:
            print(f"❌ Step 3 failed: {str(e)[:100]}")
            return {'status': 'error', 'message': f'Checkout failed: {str(e)[:100]}', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshots': screenshots}
        
        # ============================================
        # STEP 4: Wait for Razorpay iframe
        # ============================================
        print("\n[STEP 4] Waiting for Razorpay...")
        time.sleep(10)
        print(f"✓ Current URL: {driver.current_url}")
        
        # Take screenshot
        ss5 = f'/content/screenshots/5_payment_redirect_{int(time.time())}.png'
        driver.save_screenshot(ss5)
        screenshots.append(ss5)
        
        # Check if still on checkout page
        if 'checkout' in driver.current_url and 'order-pay' not in driver.current_url:
            print("❌ Still on checkout page - Place Order failed!")
            return {'status': 'error', 'message': 'Place Order button failed', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshots': screenshots}
        
        # ============================================
        # STEP 5: Switch to Razorpay iframe
        # ============================================
        print("\n[STEP 5] Looking for Razorpay iframe...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"✓ Found {len(iframes)} iframes")
        
        razorpay_found = False
        razorpay_iframe_index = -1
        
        for i, iframe in enumerate(iframes):
            try:
                driver.switch_to.frame(iframe)
                page_source = driver.page_source.lower()
                driver.switch_to.default_content()
                
                if "razorpay" in page_source:
                    print(f"✓ Razorpay iframe found (index {i})")
                    razorpay_found = True
                    razorpay_iframe_index = i
                    break
            except:
                driver.switch_to.default_content()
        
        if not razorpay_found:
            print("❌ Razorpay iframe not found!")
            # Check if we're on success page
            if 'order-received' in driver.current_url:
                print("✅ Order completed successfully!")
                return {'status': 'approved', 'message': 'Payment successful', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshots': screenshots}
            else:
                return {'status': 'error', 'message': 'Razorpay iframe not found', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshots': screenshots}
        
        # Switch to Razorpay iframe
        driver.switch_to.frame(iframes[razorpay_iframe_index])
        time.sleep(3)
        
        # Take screenshot inside iframe
        ss6 = f'/content/screenshots/6_razorpay_iframe_{int(time.time())}.png'
        driver.save_screenshot(ss6)
        screenshots.append(ss6)
        
        # ============================================
        # STEP 6: Click "Cards" option
        # ============================================
        print("\n[STEP 6] Clicking Cards option...")
        cards_clicked = False
        
        # Try finding "Cards" text
        all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Cards') or contains(text(), 'Card')]")
        for elem in all_elements:
            try:
                elem_text = elem.text.strip()
                if ('Cards' in elem_text or 'Card' in elem_text) and elem.is_displayed():
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
                    if div.is_displayed() and ('Cards' in div.text or 'Card' in div.text):
                        driver.execute_script("arguments[0].click();", div)
                        print("✓ Cards clicked (alternative)")
                        cards_clicked = True
                        time.sleep(2)
                        break
            except:
                pass
        
        if not cards_clicked:
            print("⚠ Could not click Cards option, trying to find card fields directly...")
        
        # ============================================
        # STEP 7: Fill card details
        # ============================================
        print("\n[STEP 7] Filling card details...")
        time.sleep(2)
        
        # Card number
        card_filled = False
        for attempt in range(10):
            try:
                card_fields = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='Card'], input[placeholder*='card'], input[type='tel'], input[type='text']")
                for field in card_fields:
                    if field.is_displayed():
                        field.send_keys(cc)
                        print("✓ Card number filled")
                        card_filled = True
                        break
                if card_filled:
                    break
            except:
                pass
            time.sleep(1)
        
        if not card_filled:
            print("❌ Card field not found!")
            driver.switch_to.default_content()
            return {'status': 'error', 'message': 'Card field not found', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshots': screenshots}
        
        time.sleep(1)
        
        # Expiry
        expiry_filled = False
        try:
            expiry_fields = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='MM'], input[placeholder*='YY'], input[placeholder*='Expiry']")
            for field in expiry_fields:
                if field.is_displayed():
                    field.send_keys(f"{mes}{ano[-2:]}")
                    print("✓ Expiry filled")
                    expiry_filled = True
                    break
        except:
            print("⚠ Expiry field not found")
        
        time.sleep(1)
        
        # CVV
        cvv_filled = False
        try:
            cvv_fields = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='CVV'], input[placeholder*='CVC']")
            for field in cvv_fields:
                if field.is_displayed():
                    field.send_keys(cvv)
                    print("✓ CVV filled")
                    cvv_filled = True
                    break
        except:
            print("⚠ CVV field not found")
        
        time.sleep(2)
        
        # Take screenshot after filling card
        ss7 = f'/content/screenshots/7_card_filled_{int(time.time())}.png'
        driver.save_screenshot(ss7)
        screenshots.append(ss7)
        
        # ============================================
        # STEP 8: Click Continue/Pay button
        # ============================================
        print("\n[STEP 8] Looking for Continue/Pay button...")
        continue_clicked = False
        
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            try:
                if btn.is_displayed():
                    btn_text = btn.text.lower()
                    if 'continue' in btn_text or 'pay' in btn_text or 'submit' in btn_text:
                        driver.execute_script("arguments[0].click();", btn)
                        print(f"✓ Button clicked: {btn.text}")
                        continue_clicked = True
                        break
            except:
                pass
        
        if not continue_clicked:
            print("⚠ Continue/Pay button not found, trying form submit...")
            try:
                forms = driver.find_elements(By.TAG_NAME, "form")
                for form in forms:
                    if form.is_displayed():
                        form.submit()
                        print("✓ Form submitted")
                        continue_clicked = True
                        break
            except:
                pass
        
        time.sleep(5)
        
        # ============================================
        # STEP 9: Check for result
        # ============================================
        print("\n[STEP 9] Checking for result...")
        
        # Check if new window opened (3DS authentication)
        driver.switch_to.default_content()
        current_windows = driver.window_handles
        print(f"✓ Windows count: {len(current_windows)}")
        
        # Check if new window opened (3DS card)
        if len(current_windows) > 1:
            print("🔐 3DS Authentication window detected!")
            print(f"✓ Switching to new window...")
            
            # Switch to new window
            driver.switch_to.window(current_windows[-1])
            time.sleep(3)
            
            print(f"✓ New window URL: {driver.current_url}")
            
            # Take screenshot of 3DS page
            ss8 = f'/content/screenshots/8_3ds_page_{int(time.time())}.png'
            driver.save_screenshot(ss8)
            screenshots.append(ss8)
            
            return {'status': '3ds', 'message': '3DS Authentication Required', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshots': screenshots}
        
        # Check current URL for success
        current_url = driver.current_url
        if 'order-received' in current_url or 'thank-you' in current_url:
            print("✅ Order completed successfully!")
            
            ss9 = f'/content/screenshots/9_success_page_{int(time.time())}.png'
            driver.save_screenshot(ss9)
            screenshots.append(ss9)
            
            return {'status': 'approved', 'message': 'Payment successful', 'time': f'{round(time.time() - start_time, 2)}s', 'screenshots': screenshots}
        
        # Check page source for result
        page_source = driver.page_source.lower()
        
        result_status = 'declined'
        result_message = 'Payment failed or pending'
        
        # Check for various responses
        if 'success' in page_source or 'approved' in page_source or 'thank you' in page_source:
            result_status = 'approved'
            result_message = 'Payment successful'
        elif 'declined' in page_source or 'failed' in page_source or 'error' in page_source:
            result_status = 'declined'
            result_message = 'Card declined'
        elif 'insufficient' in page_source:
            result_status = 'declined'
            result_message = 'Insufficient funds'
        elif 'invalid' in page_source or 'incorrect' in page_source:
            result_status = 'declined'
            result_message = 'Invalid card details'
        elif 'pending' in page_source or 'processing' in page_source:
            result_status = 'pending'
            result_message = 'Payment processing'
        
        # Take final screenshot
        ss10 = f'/content/screenshots/10_final_result_{int(time.time())}.png'
        driver.save_screenshot(ss10)
        screenshots.append(ss10)
        
        elapsed_time = round(time.time() - start_time, 2)
        
        return {'status': result_status, 'message': result_message, 'time': f'{elapsed_time}s', 'screenshots': screenshots}
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        error_ss = f'/content/screenshots/error_{int(time.time())}.png'
        try:
            if driver:
                driver.save_screenshot(error_ss)
                screenshots.append(error_ss)
        except:
            pass
        
        elapsed_time = round(time.time() - start_time, 2)
        
        return {'status': 'error', 'message': f'Critical error: {str(e)[:150]}', 'time': f'{elapsed_time}s', 'screenshots': screenshots}
    
    finally:
        if driver:
            try:
                driver.quit()
                print("✅ Browser closed")
            except:
                pass

def download_screenshots(screenshots):
    """Download all screenshots as zip"""
    if not screenshots:
        print("❌ No screenshots to download")
        return
    
    # Filter only existing screenshots
    existing_screenshots = [ss for ss in screenshots if os.path.exists(ss)]
    
    if not existing_screenshots:
        print("❌ No screenshot files found")
        return
    
    # Create zip file
    zip_path = '/content/screenshots.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for screenshot in existing_screenshots:
            zipf.write(screenshot, os.path.basename(screenshot))
    
    # Download zip
    files.download(zip_path)
    print(f"✅ Downloading {len(existing_screenshots)} screenshots...")

def display_screenshot(screenshot_path):
    """Display screenshot in Colab"""
    if os.path.exists(screenshot_path):
        display(Image(filename=screenshot_path))
    else:
        print(f"❌ Screenshot not found: {screenshot_path}")

def main():
    """Main function for Google Colab"""
    print("=" * 70)
    print("🚀 RAZORPAY FULL AUTOMATION - GOOGLE COLAB")
    print("=" * 70)
    print("✅ Full automation including card entry in Razorpay")
    print("✅ Takes screenshots at every step")
    print("✅ Shows real approval/decline results")
    print("=" * 70)
    
    while True:
        print("\n" + "━" * 70)
        print("📝 Enter card (format: 4532015112830366|12|2025|123)")
        print("Commands: 'test' = test card, 'demo' = see demo, 'exit' = quit")
        print("━" * 70)
        
        user_input = input("\n🎯 Enter command or card: ").strip()
        
        if user_input.lower() == 'exit':
            print("\n👋 Exiting... Goodbye!")
            break
        
        elif user_input.lower() == 'test':
            print("\n📋 Available test cards:")
            print("1. 4532015112830366|12|2025|123  (Visa - Test)")
            print("2. 5123456789012346|06|2026|456  (MasterCard - Test)")
            print("3. 378282246310005|12|2027|1234  (Amex - Test)")
            print("4. 4012888888881881|08|2026|123  (Visa - Test 2)")
            
            choice = input("\nSelect card (1-4): ").strip()
            if choice == '1':
                user_input = "4532015112830366|12|2025|123"
            elif choice == '2':
                user_input = "5123456789012346|06|2026|456"
            elif choice == '3':
                user_input = "378282246310005|12|2027|1234"
            elif choice == '4':
                user_input = "4012888888881881|08|2026|123"
            else:
                print("❌ Invalid choice")
                continue
            
            print(f"✅ Using: {user_input}")
        
        elif user_input.lower() == 'demo':
            print("\n🎬 Running DEMO with test card...")
            user_input = "4532015112830366|12|2025|123"
            print(f"✅ Using demo card: {user_input}")
        
        # Extract card
        card = extract_card(user_input)
        
        if not card:
            print("❌ Invalid format! Use: 4532015112830366|12|2025|123")
            continue
        
        print(f"\n{'='*70}")
        print(f"🔍 PROCESSING: {card}")
        print(f"{'='*70}")
        
        print("\n⚠️  IMPORTANT:")
        print("• Full automation - will enter card in Razorpay")
        print("• May trigger 3DS authentication")
        print("• Takes 30-60 seconds")
        print("• Screenshots taken at each step")
        
        confirm = input("\n✅ Type 'GO' to continue: ").strip().upper()
        if confirm != 'GO':
            print("❌ Cancelled by user")
            continue
        
        # Start the check
        print("\n" + "🔄" * 35)
        print("STARTING FULL AUTOMATION...")
        print("🔄" * 35)
        
        result = check_razorpay_card_sync(card)
        
        # Display results
        print(f"\n{'='*70}")
        print("🎯 RESULTS")
        print(f"{'='*70}")
        
        status = result.get('status', 'error')
        message = result.get('message', 'Unknown')
        elapsed_time = result.get('time', '0s')
        screenshots = result.get('screenshots', [])
        
        # Color coded status
        if status == 'approved':
            status_display = f"🟢 APPROVED"
        elif status == 'declined':
            status_display = f"🔴 DECLINED"
        elif status == '3ds':
            status_display = f"🟡 3DS AUTH REQUIRED"
        elif status == 'pending':
            status_display = f"🟡 PENDING"
        elif status == 'error':
            status_display = f"🔴 ERROR"
        else:
            status_display = f"⚪ {status.upper()}"
        
        print(f"\n📊 SUMMARY:")
        print(f"┌{'─'*68}┐")
        print(f"│ {'Card:':<15} {card:<51} │")
        print(f"│ {'Status:':<15} {status_display:<51} │")
        print(f"│ {'Message:':<15} {message:<51} │")
        print(f"│ {'Time:':<15} {elapsed_time:<51} │")
        print(f"│ {'Screenshots:':<15} {len(screenshots)} files{' '*36} │")
        print(f"└{'─'*68}┘")
        
        # Show screenshot preview
        if screenshots and len(screenshots) > 0:
            print(f"\n📸 Screenshots available:")
            for i, ss in enumerate(screenshots[:3], 1):  # Show first 3
                if os.path.exists(ss):
                    print(f"  {i}. {os.path.basename(ss)}")
            
            # Download option
            download = input("\n⬇️  Download all screenshots as ZIP? (yes/no): ").strip().lower()
            if download == 'yes':
                download_screenshots(screenshots)
            
            # Display first screenshot
            display_first = input("\n👀 Display first screenshot here? (yes/no): ").strip().lower()
            if display_first == 'yes' and len(screenshots) > 0:
                display_screenshot(screenshots[0])
        
        print(f"\n{'='*70}")
        print("✅ Process completed!")
        print(f"{'='*70}")

# Run the main function
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")