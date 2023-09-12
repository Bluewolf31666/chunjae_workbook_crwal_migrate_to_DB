from config import MYSQL_SETTINGS, SELECT
import mysql.connector


def connect_to_database(): # DB 연결확인
    try:
        connection = mysql.connector.connect(**MYSQL_SETTINGS)
        if connection.is_connected():
            print('Database server Connection Success')
        return connection

    except mysql.connector.Error as e:
        print(f'Database server connection error : {e}')
        return None

def disconnect_from_mysql(connection, cursor): # 연결 종료
    if connection.is_connected():
        cursor.close()
        connection.close()
        print('Close Database connection')


def select_data(): # 데이터 SELECT
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(SELECT)
    id_list = cursor.fetchall()
    item_id_list=[]
    #print(len(id_list))
    for x in range(len(id_list)):
    
        data_dict = id_list[x]
        item_id = data_dict['passage_id']
      
        item_id_list.append(item_id)
       
    print(len(item_id_list))

    return item_id_list
