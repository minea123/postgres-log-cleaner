import datetime

import psycopg2
import logging
from config import CONFIG
from telegram_message import send
from elasticsearch import Elasticsearch
es = Elasticsearch(
    hosts=CONFIG.elastic_search,
    api_key=CONFIG.elastic_api_key
)


def get_replication_status():
    connection = psycopg2.connect(
        host=CONFIG.db_master,
        port=CONFIG.db_master_port,
        database=CONFIG.db_master_db,
        user=CONFIG.db_master_user,
        password=CONFIG.db_master_password
    )
    cursor = connection.cursor()
    connected_slaves = {}
    try:
        sql = """ SELECT 
            client_addr, 
            state, 
            sync_state,
            sent_lsn,
            write_lsn,
            flush_lsn,
            replay_lsn,
			replay_lag,
			write_lag,
			flush_lag
         
            FROM pg_stat_replication;"""
        # Execute the query
        cursor.execute(sql)

        # Fetch and print results
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        for row in rows:
            document = dict(zip(col_names, row))
            client_ip, state, sync_state, sent_lsn, write_lsn, flush_lsn, replay_lsn, replay_lag, write_lag, flush_lag = row
            document["created_at"] = datetime.datetime.now()
            es.index(index=CONFIG.index_replica, body=document)
            if replay_lag.seconds > 0 or write_lag.seconds > 0 or flush_lag.seconds > 0:
                send(
                    f"postgres db slave nodes [{client_ip}]  state: {state} ,sync : {sync_state} , sent_lsn:{sent_lsn},write_lsn:{write_lsn}, flush_lsn:{flush_lsn} has delay or lag replay_lag\t:{replay_lag} , \t write_lag: {write_lag} \t flush_lag : {flush_lag}")
            connected_slaves[client_ip] = True
        cursor.close()
        connection.close()

    except Exception as e:
        logging.error(f"error connecting to postgresql {e}")
    config_slaves = CONFIG.db_slaves.split(",")
    for slave_ip in config_slaves:
        if slave_ip not in connected_slaves:
            send(f"postgres db slave nodes {slave_ip} not connected to master : {CONFIG.db_master} as replica, please "
                 f"check!")


if __name__ == "__main__":
    get_replication_status()
