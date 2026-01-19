# INSTALL REQUIREMENTS
!apt-get update -qq
!apt install -y chromium-chromedriver -qq
!pip install selenium faker webdriver-manager -q

# DOWNLOAD FROM PASTEBIN
!wget -q "https://pastebin.com/raw/1VgSHYvp" -O razorpay.py

# RUN THE SCRIPT
!python razorpay.py