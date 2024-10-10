import psycopg2, logging
from config import CONFIG
import datetime
from telegram_message import send


def monitor_delete():
    sql = """
    select s.query, s.max_exec_time, s.rows , a.datname,a.usename,a.application_name,a.client_addr,a.backend_type
        FROM   pg_stat_statements  s 
		inner join pg_stat_activity a ON s.userid = a.usesysid
	WHERE s.query ILIKE 'DELETE%' OR s.query ILIKE 'TRUNCATE%'
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
        send(f" delete query : {document['query']} , database : {document['datname']} "
             f",  username: {document['usename']} ,client_addr : {document['client_addr']} , {document['backend_type']} ")


if __name__ == "__main__":
    monitor_delete()
