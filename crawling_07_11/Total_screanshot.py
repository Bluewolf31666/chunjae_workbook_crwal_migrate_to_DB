from bs4 import BeautifulSoup 
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.chrome.service import Service as ChromeService
from PIL import Image
import cv2

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
 
driver.get("http://naver.com")
time.sleep(2)
height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight,document.body.offsetHeight, document.documentElement.offsetHeight,document.body.clientHeight, document.documentElement.clientHeight)")
print(height)
#close browser
driver.close()

#Open another headless browser with height extracted above
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(f"--window-size=1920,{height}")
chrome_options.add_argument("--hide-scrollbars")
driver = webdriver.Chrome(options=chrome_options)
url="http://naver.com"
driver.get(url)
#pause 3 second to let page loads
time.sleep(3)
#save screenshot
driver.save_screenshot('screen_shot.png')
driver.close()
