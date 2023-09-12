# main.py

from crawling_func import (
    setup_driver,
    data_info,
    capture_screen,
    select_munhang_id,
)
from DB_conn_func import insert_data
from config import URL
from tqdm import trange
import time
import ray

ray.init(ignore_reinit_error=True) # ignore_reinit_error=True : 재실행시 오류 무시
error_id_list = []
@ray.remote
def main(munhang_id):
    try:
        #driver = setup_driver()
        url = URL.format(munhang_id)
        size_and_url = capture_screen(url, munhang_id)        
        data_list = data_info(size_and_url[0], munhang_id, size_and_url[1], size_and_url[2]) #  width, height, item_id, img_url
        print(data_list)
        # INSERT Data
        insert_data(data_list)
                                    
    except Exception as e: 
        error_id_list.append(munhang_id)
        print("Error : ", e)
        pass



if __name__ == '__main__':

    item_id_list = select_munhang_id('/opt/airflow/dags/select_passage_id_update/passage_id.csv')
    munhang_id = item_id_list
    #munhang_id = [24511]
    #munhang_id=munhang_id[:3] 
    munhang_id.sort()
    n = 5  # 한번에 처리할 문항 수 = 10개씩 병렬처리
    result = [munhang_id[i * n:(i + 1) * n] for i in range((len(munhang_id) + n - 1) // n )] 
    
    start = time.time()
    for index in trange(len(result)):
    
        futures = [main.remote(result[index][j]) for j in range(len(result[index]))]
        ray.get(futures)
    with open('./Error_munhang_id.txt','w+', encoding='UTF-8') as f:
        for li in range(len(error_id_list)):
            f.write(str(error_id_list[li]+'\n'))
                    
    ray.shutdown()
            
    print("실행 시간: ", time.time() - start)
   
