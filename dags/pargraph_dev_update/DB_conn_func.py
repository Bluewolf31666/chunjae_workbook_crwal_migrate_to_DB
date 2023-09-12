# DB_conn_func.py

from config import MYSQL_SETTINGS, INSERT
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

def insert_data(data_list): # 데이터 INSERT
    try:
        # DB 연결
        connection = connect_to_database()
        cursor = connection.cursor(dictionary=True)
        query = INSERT
        try:
            cursor.execute(query, data_list)
            connection.commit()
            print('Data INSERT Success to Database')
        except Exception as e:
            print(f"Error occurred: {e}")
            connection.rollback()  # 롤백 수행

    except mysql.connector.Error as e:
        print(f'Data INSERT Error : {e}')
        connection.rollback()

    finally:
        disconnect_from_mysql(connection, cursor)

