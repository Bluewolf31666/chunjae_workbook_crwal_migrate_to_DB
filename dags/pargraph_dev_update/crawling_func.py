#  crawling_func.py
from config import (
    AWS_S3_BUCKET_NAME, # 실제 넣는 버킷은 AWS_S3_BUCKET_NAME
    REGION
)
from s3_conn_func import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from time import sleep
import aspose.words as aw
import os
from PIL import Image
import pandas as pd
import shutil
import random
from tempfile import mkdtemp
import base64
from datetime import datetime
def setup_driver(temp_path): # chromedriver setting
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument('--no-sandbox') ## 중요
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disk-cache-size=0")
    options.add_argument(f"--user-data-dir={temp_path}")
    options.add_argument(f"--data-path={temp_path}")
    options.add_argument(f"--disk-cache-dir={temp_path}")
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    return driver

######### DB에 넣을 데이터 딕셔너리 #########
def data_info(origin_size_list, munhang_list, result_img_list_path, platform_url): 

    item_id_list = munhang_list # 문항 ID
    width = origin_size_list[0] # 너비
    height = origin_size_list[1] # 높이
    img_path = result_img_list_path # URL
    platform_url_path = platform_url
 

    return [item_id_list, width, height, img_path, platform_url_path]

######### 문항 id 가져오기 #########
def select_munhang_id(csv_path):
    item_id = []
    csv = pd.read_csv(csv_path, encoding='CP949')
    item_id = csv['passage_id'].tolist()


    return item_id

######### 이미지 사이즈 리스트에 저장 #########
def measure_size(crop_img_list): 

    im = Image.open(crop_img_list,'r')
    width, height = im.size


    return width, height

######### 이미지 저장 디렉토리 및 하위폴더 모두 삭제 #########

def delete_tmp(dirpath):
    try:
        if os.path.isdir(dirpath):
            shutil.rmtree(dirpath)

            
    except OSError as e:
        print("Error: %s : %s" % (dirpath, e.strerror))

######### 이미지 저장 디렉토리 자동 생성 #########
def generate_random_folder_name(length=8):
    folder_name = ''.join(str(random.randint(0, 9)) for _ in range(length))
    return folder_name

def create_random_folder(directory):
    random_folder_name = generate_random_folder_name()
    folder_path = os.path.join(directory, random_folder_name)
    
    try:
        if not os.path.exists(os.path.join(folder_path)):
            os.makedirs(folder_path)
        if not os.path.exists(os.path.join('png')):
            os.makedirs('{}/png'.format(folder_path))
        if not os.path.exists(os.path.join('svg')):
            os.makedirs('{}/svg'.format(folder_path))

        return folder_path
    
    except OSError:
        print(f"Failed to create directory '{folder_path}'")
        return None

######### Crawling #########
def capture_screen(url, munhang_id):
    
    target_directory = os.getcwd()
    current_date = datetime.now().strftime('%Y-%m-%d') # 오늘 날짜
    new_folder_path = create_random_folder(target_directory)


    result_path_list = []
    error_list = []
    if not os.path.exists(os.path.join('temp')):
        os.makedirs('{}/temp'.format(new_folder_path))
    temp_path = new_folder_path+'/temp'

    driver=setup_driver(temp_path)    
    driver.get(url)
   
    png_path = new_folder_path+f'/png/{munhang_id}_{current_date}.png'
    svg_path = new_folder_path+f'/svg/{munhang_id}_{current_date}.svg'
    
    try:   
        
        driver.set_window_size(7680, 4320)
        scroll = driver.find_element(By.CLASS_NAME,'inner.tbl_scroll_box') # 스크롤 삭제
        driver.execute_script('arguments[0].removeAttribute("style")', scroll) # 스크롤 div에서 style 삭제
        exam_box_style = driver.find_element(By.CLASS_NAME,'exam_box') # 스크롤 삭제
        driver.execute_script('arguments[0].removeAttribute("style")', exam_box_style) # 스크롤 div에서 style 삭제
        #pargraog=driver.find_element(By.XPATH,"""//*[@id="preview_passage"]/div/div[2]/span/table""")
        #driver.execute_script('arguments[0].removeAttribute("style")', pargraog)
        sleep(1)
        element = driver.find_element(By.XPATH,'//*[@id="div_item_field"]/div')
        driver.execute_script('arguments[0].removeAttribute(".item_box")', element)
        sleep(1)

        element_png_raw = element.screenshot_as_png # 캡처
        element_png= base64.b64encode(element_png_raw).decode('utf-8')    
        # PNG 파일 생성
        with open(png_path, "wb") as file: # 2차 png 저장
            file.write(base64.b64decode(element_png))

        png_size = measure_size(png_path)

        driver.quit()

    
    except NoSuchElementException as Ne:
        print("No munhang element : ", Ne) 
        return munhang_id
    
    except Exception as e:
        print("the First munhang Crawling Error : ", e)
        

    # SVG 변환 save_svg에 최종 svg파일 저장
    doc = aw.Document()
    builder = aw.DocumentBuilder(doc)
    shape = builder.insert_image(png_path) # 2차로 저장한 png파일 불러옴
    saveOptions = aw.saving.ImageSaveOptions(aw.SaveFormat.SVG)
    shape.get_shape_renderer().save(svg_path, saveOptions) # 최종 이미지 save_svg 폴더에 저장

    # S3 connection
    s3 = s3_connection() # S3 연결

    # png upload to S3
    upload_s3_png(
        s3 = s3,
        bucket = AWS_S3_BUCKET_NAME,
        path_list = png_path,
        munhang_list = munhang_id
        ) 


    # svg upload to S3
    s3_path_list = upload_s3_svg(
        s3 = s3,
        bucket = AWS_S3_BUCKET_NAME,
        path_list = svg_path,
       munhang_list = munhang_id
        )
   
    svg_url_list = get_URL(AWS_S3_BUCKET_NAME, REGION, s3_path_list) # S3에 저장된 svg 이미지 url 리스트
    platform_url_list = get_platform_url(s3_path_list)

    # tmp 하위 디렉토리 초기화
    delete_tmp(new_folder_path)

    return png_size, svg_url_list, platform_url_list
