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


def setup_driver(): # chromedriver setting
    options = webdriver.ChromeOptions()
    # options.add_argument(f"--user-data-dir=./tmp")
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    return driver

######### DB에 넣을 데이터 딕셔너리 #########
def data_info(origin_size_list, munhang_list, result_img_list_path): 

    item_id_list = munhang_list # 문항 ID
    width = origin_size_list[0] # 너비
    height = origin_size_list[1] # 높이
    img_path = result_img_list_path # URL
 

    return [item_id_list, width, height, img_path]

######### 문항 id 가져오기 #########
def select_munhang_id(csv_path):
    item_id = []
    csv = pd.read_csv(csv_path, encoding='CP949')
    # print(csv['item_id'])
    item_id = csv['item_id'].tolist()
    #print(csv['item_id'].tolist())

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
            print("Sucess remove tmp folder")
        
        elif os.path.isfile(dirpath):
            os.remove(dirpath)

        else:
            print("File exists")
            
    except OSError as e:
        print("Error: %s : %s" % (dirpath, e.strerror))

######### 이미지 저장 디렉토리 자동 생성 #########

def create_tmp():
    if not os.path.exists(os.path.join('tmp')):
        os.makedirs('tmp')
    if not os.path.exists(os.path.join('origin')):
        os.makedirs('tmp/origin')
    if not os.path.exists(os.path.join('png')):
        os.makedirs('tmp/png')
    if not os.path.exists(os.path.join('svg')):
        os.makedirs('tmp/svg')


######### Crawling #########
def capture_screen(url, driver, munhang_id):

    if os.path.exists(os.path.join('tmp')): # 재실행시 tmp 있을시 삭제
        tmp_path = './tmp'
        delete_tmp(tmp_path)
    else: 
        create_tmp()

    driver.get(url)
    tmp_path = './tmp'
    origin_path = './tmp/origin/{}.png'
    png_path = './tmp/png/{}.png'
    svg_path = './tmp/svg/{}.svg'
    

    try:
        
        scroll = driver.find_element(By.CLASS_NAME,'inner.tbl_scroll_box') # 스크롤 삭제
        driver.execute_script('arguments[0].removeAttribute("style")', scroll) # 스크롤 div에서 style 삭제
        driver.set_window_size(7680, 4320)
        driver.implicitly_wait(2)
        sleep(0.1)
        element = driver.find_element(By.CLASS_NAME, "question_item.mt20") # 캡처할 요소
        sleep(0.1)
        driver.implicitly_wait(2)
        element_png = element.screenshot_as_png # 캡처

        # PNG 파일 생성
        with open(origin_path.format(munhang_id), "wb") as file:
            file.write(element_png)
        

    except NoSuchElementException as Ne:
        #print("No munhang element : ", Ne) 
        return munhang_id

    
    except Exception as e:
        print("the First Crawling Error : ", e)



    try:
        # 사이즈 재기
        
        origin_img_size = measure_size(origin_path.format(munhang_id)) # 이중 리스트 width, height
        driver.set_window_size(7680, 4320)
        scroll = driver.find_element(By.CLASS_NAME,'inner.tbl_scroll_box') # 스크롤 삭제
        driver.execute_script('arguments[0].removeAttribute("style")', scroll) # 스크롤 div에서 style 삭제
        w = origin_img_size[0] # 너비
        ratio = 453/w # 비율
        height_value = origin_img_size[1]*ratio # 비율에 따라 줄어든 높이

        driver.implicitly_wait(2)
        sleep(0.1)
        element = driver.find_element(By.CLASS_NAME, 'question_item.mt20')
        new_style = f"transform: scale({ratio}); " # 화면에 보이는 요소의 비율 줄이기 0.87
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, new_style)
        sleep(0.1)
        driver.implicitly_wait(2)
        element_png = element.screenshot_as_png # 캡처

        # PNG 파일 생성
        with open(png_path.format(munhang_id), "wb") as file: # 2차 png 저장
            file.write(element_png)

        # 이미지 크롭해서 다시 저장
        png_image = Image.open(png_path.format(munhang_id))
        croppedImage = png_image.crop((0,0,453,height_value)) # left, up, right, down
        croppedImage.save(png_path.format(munhang_id))
        png_size = measure_size(png_path.format(munhang_id))

        driver.quit()


    except Exception as e:
        print("the Second Crawling Error : ", e)
        

    # SVG 변환 save_svg에 최종 svg파일 저장
    doc = aw.Document()
    builder = aw.DocumentBuilder(doc)
    shape = builder.insert_image(png_path.format(munhang_id)) # 2차로 저장한 png파일 불러옴
    saveOptions = aw.saving.ImageSaveOptions(aw.SaveFormat.SVG)
    shape.get_shape_renderer().save(svg_path.format(munhang_id), saveOptions) # 최종 이미지 save_svg 폴더에 저장

    # S3 connection
    s3 = s3_connection() # S3 연결

    # png upload to S3
    upload_s3_png(
        s3 = s3,
        bucket = AWS_S3_BUCKET_NAME,
        path_list = png_path.format(munhang_id),
        munhang_list = munhang_id
        ) 


    # svg upload to S3
    s3_path_list = upload_s3_svg(
        s3 = s3,
        bucket = AWS_S3_BUCKET_NAME,
        path_list = svg_path.format(munhang_id),
        munhang_list = munhang_id
        )
   
    svg_url_list = get_URL(AWS_S3_BUCKET_NAME, REGION, s3_path_list) # S3에 저장된 svg 이미지 url 리스트


    # tmp 하위 디렉토리 초기화
    delete_tmp(tmp_path)

    return png_size, svg_url_list






