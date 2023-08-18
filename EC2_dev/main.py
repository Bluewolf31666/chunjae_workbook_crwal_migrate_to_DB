# main.py
from crawling_func import (
    setup_driver,
    data_info,
    capture_screen,
    select_munhang_id,
)
from config import URL
from tqdm import trange
from DB_conn_func import insert_data

def main(): 
    
    # 테스트용 
    # munhang_list = [147864, 147434,147376,146368,145664,145571,144916,144904,144605,144576,144468]
    # munhang_id = [164404] # 테스트용 가장 긴 문항
    no_element_list = []
    item_id_list = select_munhang_id('../select_munhang_id/item_id.csv')
    item_id_list.sort()
    N = int(len(item_id_list)/3) # 병렬처리 갯수
    div_munhang_list = [item_id_list[div * N:(div + 1) * N] for div in range((len(item_id_list) + N - 1) // N )]
    #num = div_munhang_list[1][:].index(165442) # index()는 문항 id
    munhang_id = div_munhang_list[0][:10] # 0 ~ 2

    # print(len(div_munhang_list[0][:]))
    # print(len(div_munhang_list[1][:]))
    # print(len(div_munhang_list[2][:]))
    
    for item_id in trange(len(munhang_id)):
        while True:
            try:
                #print(munhang_id[item_id])
                driver = setup_driver()
                url = URL.format(munhang_id[item_id])
                size_and_url = capture_screen(url, driver, munhang_id[item_id])
                

                if size_and_url == munhang_id[item_id]:
                    no_element_list.append(size_and_url)
                    pass

                else:
                    data_list = data_info(size_and_url[0], munhang_id[item_id], size_and_url[1]) #  width, height, item_id, img_url
                    

                    # INSERT Data
                    insert_data(data_list)
                
            except Exception as e: 
                print("Error : ", e)

            else:
                break
    
    with open('./munhang.txt','w+',encoding='UTF-8') as f:
        for li in range(len(no_element_list)):
            f.write(str(no_element_list[li])+'\n')

        
if __name__ == '__main__': 
    
    main()    
    
    
