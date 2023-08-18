from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import pymysql
import setting
import math

path=os.getcwd()
Url_list=[147434,147376,146368,145664,145571,144916,144904,144605,144576,144468]
for i in Url_list:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    X_path_for_test=setting.workbook_selector
    html = driver.page_source
    driver.get(setting.workbook_address.format(i))
    driver.implicitly_wait(10)

    element1 = driver.find_element(By.CSS_SELECTOR,X_path_for_test) 
    screenshot_as_bytes = element1.screenshot_as_png

    with open(f'test_raw_{i}.png', 'wb') as f:
        f.write(screenshot_as_bytes) 

    driver.close()

    image2 = Image.open(f'test_raw_{i}.png')
    image_lenght= math.ceil(image2.size[1]*(453/515))
    cropedImage=image2.resize((453,image_lenght),Image.Resampling.LANCZOS)
    cropedImage.save(f'croped_{i}.png','png')
    image2.close()
    cropedImage.close()
    os.remove(f'test_raw_{i}.png')
    file_name=f'croped_{i}.png'
    if path == "/":
        full_path="/"+file_name
    else:
        full_path=path+"/"+file_name

    conn = pymysql.connect(host=setting.host_address, user=setting.id, password=setting.pw, db=setting.db, charset='utf8')
    cur = conn.cursor()
    sql="""INSERT INTO monhangdb.tb_item_capture
    (capture_id,item_id, width, height, img_url, create_date, `usage`)
    VALUES(NULL,%s, %s, %s, %s, current_timestamp(), NULL);
    """
    vals = (i,453,image_lenght,full_path)
    cur.execute(sql, vals)
    cur.close()
    conn.commit()
    conn.close()