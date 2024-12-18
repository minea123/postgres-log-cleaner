import psycopg2, logging
from config import CONFIG
import os
def read_query(directory_path="./refresh"):
    # Loop through all files in the directory
    sql_list = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".sql"):  # Process only .txt files
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r") as file:
                content = file.read()
                sql_list.append(content)
    return sql_list

def refresh_mv(sql):
    connection = psycopg2.connect(
        host=CONFIG.db_master,
        port=CONFIG.db_master_port,
        database=CONFIG.db_master_db,
        user=CONFIG.db_master_user,
        password=CONFIG.db_master_password
    )
    cursor = connection.cursor()
    cursor.execute(sql)
    logging.info(f"Done refreshing MV {sql}")
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    sql_list = read_query(CONFIG.refresh_mv_path)
    for sql in sql_list:
        refresh_mv(sql)
