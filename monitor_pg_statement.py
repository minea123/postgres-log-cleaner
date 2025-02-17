import datetime
import logging

import psycopg2
from config import CONFIG
from elasticsearch import Elasticsearch
from telegram_message import send
import requests
from custom_logger import logger
from json import dumps

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

    # in development, no need to filter out slow query
    # since we want data for testing
    if CONFIG.isDev:
        sql = """
            select distinct s.query, s.max_exec_time, s.rows , a.datname,a.usename,a.application_name,a.client_addr,a.backend_type
            FROM   pg_stat_statements  s 
            left join pg_stat_activity a ON s.userid = a.usesysid 
            limit 10;
        """     

    send_complete = {}    
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

    # store document to be sent to API,
    # reduce API call every loop
    batch_documents = []
    
    for row in rows:
        document = dict(zip(col_names, row))
        if str(document["query"]).startswith("COPY") or str(document["query"]).startswith("copy"):
            logging.debug("COPY is for backup only")
            continue

        key_sent = hash(f"{document['query']}")
        if key_sent in send_complete:
            continue
        send_complete[key_sent] = True
        document["created_at"] = datetime.datetime.now()
        if document["max_exec_time"] > CONFIG.slow_query_duration or document["rows"] > CONFIG.slow_query_rows:
            send(f" slow query  @ {CONFIG.db_master}:  {document['query']} , duration : {document['max_exec_time']} "
                    f", total row : {document['rows']}"
                    f",  username: {document['usename']} ,client_addr : {document['client_addr']} , {document['backend_type']} "
                    )
    
        if CONFIG.elastic_enable:
            push_to_elastic(document)

        batch_documents.append(document)
    
    # send docs as batch to API
    if CONFIG.push_api_enable:
        push_to_api(batch_documents)

def push_to_elastic(document):
    es = Elasticsearch(
        hosts=CONFIG.elastic_search,
        api_key=CONFIG.elastic_api_key
    )
    es.index(index=CONFIG.elastic_index, body=document)
        
def push_to_api(documents: list[dict]):
    try:
        documents = list(map(map_dateitme, documents))
        body = dumps(documents, ensure_ascii=False, indent=4)
        print(documents[0])
        response = requests.post(CONFIG.push_api_host, json=documents, headers={
            'X-API-KEY': CONFIG.push_api_key
        })

        print(response.reason)

        if response.status_code != 200:
            send(f"""
            Unable to push statement logs to API 
            status = {response.status_code}
            reason = {response.reason}
            """)
    except Exception as error:
        send(f'Unable to request to API {CONFIG.push_api_host}, error: {str(error)}')
        logger.error(f'Unable to request to API {str(error)}')
    except Exception as error:
        logger.error(f'Unable to send alert {str(error)}')
    
def map_dateitme(doc):
    # convert python date object to iso date, to allow parse json
    doc['created_at'] = doc.get('created_at').isoformat()
    doc['max_exec_time'] = str(doc.get('max_exec_time') or '')
    doc['rows'] = str(doc.get('rows') or '')

    return doc


if __name__ == "__main__":
    get_pg_statement()
    reset_pg_statement()
