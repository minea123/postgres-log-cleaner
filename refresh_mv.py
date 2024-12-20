import psycopg2, logging
from config import CONFIG
import os
from telegram_message import send
def read_query(directory_path="./refresh"):
    # Loop through all files in the directory
    result = {}
    for filename in os.listdir(directory_path):
        if filename.endswith(".sql"):  # Process only .txt files
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r") as file:
                content = file.read()
                queries = content.split(";")
                result[filename] = [ query for query in queries if  query and query.strip()!=""]
    print("result:", result)
    return result

def refresh_mv(sql):
    try:
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
        print(f"Done refreshing MV {sql}")
        #send(f" done run cache refresh script {sql}")
        connection.commit()
    except psycopg2.Error as e:
        # Handle database errors
        logging.error(f"Error executing query: {e}")
        print(f"Error executing query: {e}")

    finally:
        # Ensure the connection is closed
        if connection:
            connection.close()
            connection.close()


if __name__ == "__main__":
    sql_map = read_query(CONFIG.refresh_mv_path)
    for (key, values) in sql_map.items():
        for value in values:
            refresh_mv(value)
        send(f"Refreshing MV {key}")
