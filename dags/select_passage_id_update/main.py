from DB_select_func import select_data
import pandas as pd
def main():
    item_id_list = select_data() # 리스트로 저장
    item_df = pd.DataFrame(item_id_list, columns = ['passage_id']) # 데이터프레임으로 변환
    item_df.to_csv('/opt/airflow/dags/select_passage_id_update/passage_id.csv') # csv로 저장

if __name__ == '__main__': # 핸들러 함수로 변경시 주석처리
    
    main()
