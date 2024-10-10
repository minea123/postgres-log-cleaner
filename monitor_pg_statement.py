import datetime
import logging

import psycopg2
from config import CONFIG
from elasticsearch import Elasticsearch
from telegram_message import send


def reset_pg_statement():
    connection = psycopg2.connect(
        host=CONFIG.db_master,
        port=CONFIG.db_master_port,
        database=CONFIG.db_master_db,
        user=CONFIG.db_master_user,
        password=CONFIG.db_master_password
    )
    sql = """ SELECT pg_stat_statements_reset(); """
    cursor = connection.cursor()
    cursor.execute(sql)


def get_pg_statement():
    sql = """
    
    select distinct s.query, s.max_exec_time, s.rows , a.datname,a.usename,a.application_name,a.client_addr,a.backend_type
        FROM   pg_stat_statements  s 
		inner join pg_stat_activity a ON s.userid = a.usesysid
        WHERE s.rows > 100
        and s.max_exec_time > 100
        limit 1000;
"""
    es = Elasticsearch(
        hosts=CONFIG.elastic_search,
        api_key=CONFIG.elastic_api_key
    )
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
        if str(document["query"]).startswith("COPY") or str(document["query"]).startswith("copy"):
            logging.debug("COPY is for backup only")
            continue

        document["created_at"] = datetime.datetime.now()
        if document["max_exec_time"] > CONFIG.slow_query_duration or document["rows"] > CONFIG.slow_query_rows:
            send(f" slow query : {document['query']} , duration : {document['max_exec_time']} "
                 f", total row : {document['rows']}"
                 f",  username: {document['usename']} ,client_addr : {document['client_addr']} , {document['backend_type']} "
                 )

        es.index(index=CONFIG.elastic_index, body=document)


if __name__ == "__main__":
    get_pg_statement()
    reset_pg_statement()
