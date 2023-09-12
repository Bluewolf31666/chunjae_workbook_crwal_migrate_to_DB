# main.py
from crawling_func import (
    data_info,
    capture_screen,
    select_munhang_id,
    delete_numfolder
)
from DB_conn_func import insert_data
from config import question_URL, answer_URL, explain_URL
from tqdm import trange
import time
import ray

ray.init(ignore_reinit_error=True) # ignore_reinit_error=True : 재실행시 오류 무시

@ray.remote
def main(item_id): 

    error_id_list = []

    try:  
        question_url = question_URL.format(item_id) # 문항 URL
        answer_url = answer_URL.format(item_id) # 정답 URL
        explain_url = explain_URL.format(item_id) # 설명 URL
        url_list = [question_url, answer_url, explain_url]

        # 크롤링 question => answer => explain
        result_data = capture_screen(url_list,  item_id)
        img_size = result_data[0] # png 사이즈
        img_url = result_data[1] # s3 svg 경로

        data_list = data_info(item_id, img_size, img_url) 
        #print(data_list)

        # INSERT Data
        insert_data(data_list)
        
        # NoSuchElementException, WebDriverException, Exception 예외처리된 item_id 리스트 
        error_id_list.extend(result_data[2])
        
    except Exception as e:
        error_id_list.append(item_id)
        print("Main Error : ", e)
        pass

    return error_id_list


if __name__ == '__main__':

    result_error_id_list = [] # 크롤링이 안되는 id를 담는 리스트 
    
    item_id_list = select_munhang_id('/opt/airflow/dags/select_munhang_id_update/item_id.csv')
    munhang_id = item_id_list[:]
    munhang_id.sort() # 정렬

    n = 16 # 한번에 처리할 문항 수 = 12개씩 병렬처리

    # munhang_id 리스트를 [[n개], [n개], ...] 형태로 나눠진 2차원리스트로 변경
    munhang_id_two_dimensional_array = [munhang_id[i * n:(i + 1) * n] for i in range((len(munhang_id) + n - 1) // n )] 
    
    start = time.time() # ray 시작 시간

    delete_numfolder() # 중단시 생기는 폴더 삭제
    
    for index in trange(len(munhang_id_two_dimensional_array)): # 2차원 리스트를 병렬처리
    
        futures = [main.remote(munhang_id_two_dimensional_array[index][j]) for j in range(len(munhang_id_two_dimensional_array[index]))]
        result_error_id_list.append(ray.get(futures))

    # 예외 처리된 item_id리스트 txt로 작성
    with open('./Error_munhang.txt','w+',encoding='UTF-8') as f:
            for li in range(len(result_error_id_list)):
                f.write(str(result_error_id_list[li])+'\n')

    ray.shutdown()
            
    print("실행 시간: ", time.time() - start)
   
