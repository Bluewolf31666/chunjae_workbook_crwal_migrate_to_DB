from bs4 import BeautifulSoup  
from selenium.webdriver.chrome.options import Options
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import cv2
from selenium.webdriver.chrome.service import Service

chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


from selenium.webdriver.common.by import By
X_path_for_test="""#div_item_field > div > div.question_item.mt20"""

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
html = driver.page_source
driver.get("(targetUrl)")
driver.implicitly_wait(10)

element1 = driver.find_element(By.CSS_SELECTOR,X_path_for_test) 
screenshot_as_bytes = element1.screenshot_as_png

with open('elemenent.png', 'wb') as f:
    f.write(screenshot_as_bytes) 

driver.close()

image2 = Image.open('elemenent.png')
cropedImage=image2.crop((0,50,453,image2.size[1]))
cropedImage.save('croped.png','png')