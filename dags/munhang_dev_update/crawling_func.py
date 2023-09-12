#  crawling_func.py
from config import (
    AWS_S3_BUCKET_NAME, # 실제 넣는 버킷은 AWS_S3_BUCKET_NAME
    REGION,
    s3_bucket_munhang,
    s3_bucket_answer,
    s3_bucket_explain
)
from s3_conn_func import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from time import sleep
import aspose.words as aw
import os
from PIL import Image
import pandas as pd
import shutil
import random
import numpy as np
import base64
from datetime import datetime

######### Chrome option Setting #########
def setup_driver(temp_path): # temp_path : 캐시 파일을 담을 폴더 경로 
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox') ## 중요
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
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
def data_info(munhang_list, origin_size_list, result_path): 

    item_id_list = munhang_list # 문항 ID
    width = origin_size_list[0] # 너비
    height = origin_size_list[1] # 높이

    question_svg_url = result_path[0][0]
    question_cdn_url = result_path[0][1]
    answer_svg_url = result_path[0][2]
    answer_cdn_url = result_path[0][3]
    explain_svg_url = result_path[0][4]
    explain_cdn_url = result_path[0][5]

    question_svg_url = str(question_svg_url)
    question_cdn_url = str(question_cdn_url)
    answer_svg_url = str(answer_svg_url)
    answer_cdn_url = str(answer_cdn_url)
    explain_svg_url = str(explain_svg_url)
    explain_cdn_url = str(explain_cdn_url)

    return [item_id_list, width, height, question_svg_url, question_cdn_url, answer_svg_url, answer_cdn_url, explain_svg_url, explain_cdn_url]

######### 문항 id 가져오기 #########
def select_munhang_id(csv_path):
    item_id = []
    csv = pd.read_csv(csv_path, encoding='CP949')
    item_id = csv['item_id'].tolist()


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
        print("OSError: %s : %s" % (dirpath, e.strerror))

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
        if not os.path.exists(os.path.join('question_png')):
            os.makedirs('{}/question_png'.format(folder_path))
        if not os.path.exists(os.path.join('question_svg')):
            os.makedirs('{}/question_svg'.format(folder_path))
        if not os.path.exists(os.path.join('answer_png')):
            os.makedirs('{}/answer_png'.format(folder_path))
        if not os.path.exists(os.path.join('answer_svg')):
            os.makedirs('{}/answer_svg'.format(folder_path))
        if not os.path.exists(os.path.join('explain_png')):
            os.makedirs('{}/explain_png'.format(folder_path))
        if not os.path.exists(os.path.join('explain_svg')):
            os.makedirs('{}/explain_svg'.format(folder_path))

        return folder_path
    
    except OSError:
        print(f"Failed to create directory '{folder_path}'")
        return None


def delete_numfolder():

    # 현재 디렉토리 내의 모든 항목(파일 및 디렉토리)을 가져옴
    items = os.listdir()
    # 삭제할 디렉토리 리스트
    directories_to_delete = [item for item in items if os.path.isdir(item) and item.isdigit()]

    # 디렉토리 삭제
    for directory in directories_to_delete:
        shutil.rmtree(os.path.join(os.getcwd(), directory))  # rmtree 함수를 사용하여 디렉토리와 그 내용을 모두 삭제합니다.
        print(f"디렉토리 {directory} 삭제됨")


    # 삭제된 디렉토리가 없는 경우
    if not directories_to_delete:
        print("삭제할 디렉토리가 없습니다.")


######### Crawling #########
def capture_screen(url_list, munhang_id):
    target_directory = os.getcwd()
    current_date = datetime.now().strftime('%Y-%m-%d') # 오늘 날짜
    new_folder_path = create_random_folder(target_directory)

    url_info = [
        {
            'url': url_list[0],
            'png_path': f'{new_folder_path}/question_png/{munhang_id}_{current_date}.png',
            'svg_path': f'{new_folder_path}/question_svg/{munhang_id}_{current_date}.svg',
            's3_bucket': s3_bucket_munhang,
        },
        {
            'url': url_list[1],
            'png_path': f'{new_folder_path}/answer_png/{munhang_id}_{current_date}.png',
            'svg_path': f'{new_folder_path}/answer_svg/{munhang_id}_{current_date}.svg',
            's3_bucket': s3_bucket_answer,
        },
        {
            'url': url_list[2],
            'png_path': f'{new_folder_path}/explain_png/{munhang_id}_{current_date}.png',
            'svg_path': f'{new_folder_path}/explain_svg/{munhang_id}_{current_date}.svg',
            's3_bucket': s3_bucket_explain,
        },
    ]

    result_path_list = []
    error_list = []

    for info in url_info:
        try:
            temp_path = create_random_folder(new_folder_path)
            driver = setup_driver(temp_path)
            driver.get(info['url'])
            driver.set_window_size(7680, 4320)

            element = driver.find_element(By.XPATH, '//*[@id="div_item_field"]/div')
            sleep(1)

            screenshot = element.screenshot_as_png

            element_png = base64.b64encode(screenshot).decode('utf-8')

            with open(info['png_path'], "wb") as file:
                file.write(base64.b64decode(element_png))

            munhang_png_size = measure_size(info['png_path'])
            driver.quit() # 크롬 프로세스 종료

        except (NoSuchElementException, WebDriverException, Exception) as e:
            print(f"Error for URL {info['url']}: {e}")
            error_list.append(info['url'])

            # screenshot_as_png height가 0일때 WebDriverException으로 걸림
            info['png_path'] = None
            munhang_png_size = None
            continue

        finally:
            delete_tmp(temp_path)

        png_to_svg(info['png_path'], info['svg_path'], munhang_id)
        path_list = s3_img_upload(info['png_path'], info['svg_path'], munhang_id, info['s3_bucket'])
        print(path_list)
        result_path_list.append(path_list)

    delete_tmp(new_folder_path)

    sum_list = sum(result_path_list, [])
    sum_list = np.array(sum_list)
    finsh_data = [[sum_list[i * 6 + j] for j in range(6)] for i in range(int(len(sum_list) / 6))]

    return munhang_png_size, finsh_data, error_list


def png_to_svg(png_path, svg_path, munhang_id):
    # SVG 변환 save_svg에 최종 svg파일 저장
    doc = aw.Document()
    builder = aw.DocumentBuilder(doc)
    shape = builder.insert_image(png_path.format(munhang_id)) # 2차로 저장한 png파일 불러옴
    saveOptions = aw.saving.ImageSaveOptions(aw.SaveFormat.SVG)
    shape.get_shape_renderer().save(svg_path.format(munhang_id), saveOptions) # 최종 이미지 save_svg 폴더에 저장


def s3_img_upload(png_path, svg_path, munhang_id, object):
    # S3 connection
    s3 = s3_connection() # S3 연결

    # png upload to S3
    upload_s3_png(
        s3 = s3,
        bucket = AWS_S3_BUCKET_NAME,
        path_list = png_path.format(munhang_id),
        munhang_list = munhang_id,
        bucket_object = object
        ) 

    # svg upload to S3
    s3_path_list = upload_s3_svg(
        s3 = s3,
        bucket = AWS_S3_BUCKET_NAME,
        path_list = svg_path.format(munhang_id),
        munhang_list = munhang_id,
        bucket_object = object
        )
    
    svg_url_list = get_URL(AWS_S3_BUCKET_NAME, REGION, s3_path_list) # S3에 저장된 svg 이미지 url 리스트
    platform_url_list = get_platform_url(s3_path_list)


    return [svg_url_list,platform_url_list]
