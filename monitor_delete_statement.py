import psycopg2, logging
from config import CONFIG
import datetime
from telegram_message import send


def monitor_delete():
    sql = """
    select query, max_exec_time, rows 
        FROM   pg_stat_statements 
        WHERE query ILIKE 'DELETE%'
"""
    connection = psycopg2.connect(
        host=CONFIG.db_master,
        port=CONFIG.db_master_port,
        database=CONFIG.db_master_db,
        user=CONFIG.db_master_user,
        password=CONFIG.db_master_password
    )

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    for row in rows:
        document = dict(zip(col_names, row))
        if str(document["query"]).startswith("delete from ping_data"):
            continue
        document["created_at"] = datetime.datetime.now()
        send(f" delete query : {document['query']} , duration : {document['max_exec_time']} "
             f", total row : {document['rows']}")


if __name__ == "__main__":
    monitor_delete()
